# CEO AI Executive Assistant — Architecture

**Status:** PROPOSED — awaiting approval. No application code written yet.
**Date:** 2026-09-19
**Principal:** Sarah Shaw, Director of Sales & Strategy, Stravion Investments (Titans Real Estate LLC), Dubai
**Default timezone:** `Asia/Dubai` (UTC+4) — configurable, never hard-coded
**Default operating window:** 10:00–22:00 `Asia/Dubai` — configurable

---

## 0. Environment inspection results (Phase 0 — COMPLETE)

### Host

| Item | Finding |
|---|---|
| Repo | `github.com/sarrahshaw-jpg/shaw` — **completely empty**, zero commits |
| Branch | `claude/ceo-ai-assistant-architecture-ke8ih7` (unborn) |
| OS | Ubuntu 24.04.4 LTS, 4 vCPU, 15 GiB RAM, 30 GiB free |
| Node | v22.22.2 / npm 10.9.7 |
| Python | 3.11.15 (uv 0.8.17, poetry 2.3.3) |
| PostgreSQL | 16.13 client present |
| Redis | 7.0.15 client present |
| Docker | 29.3.1 |
| Egress | All HTTPS via policy-enforcing agent proxy; CA bundle at `/root/.ccr/ca-bundle.crt` |

### Live integration surface (verified by calling each one)

| System | State | Evidence |
|---|---|---|
| **Hostinger Mail** | ✅ CONNECTED | `GET /api/v1/me` → one mailbox: `sarah@stravion.ae`, resourceId `AC17d75d6399ce66bff0357b5c5ef8`, order `OR3548026f9aca6ccaca6ef5c9c781` |
| **Google Calendar** | ✅ CONNECTED | Calendar `aamirsawar123@gmail.com`, timeZone already `Asia/Dubai`; + UAE holidays calendar |
| **Google Drive** | ✅ CONNECTED | search / read / create / share available |
| **Zapier** | ✅ CONNECTED | but only **LinkedIn** enabled (4 actions) |
| **Apify / Vibe Prospecting / Indeed** | ✅ CONNECTED | research & contact enrichment |
| **Microsoft 365** | ❌ `connect_incomplete` | Outlook / Teams / SharePoint unavailable |
| **Notion** | ❌ `connect_incomplete` | |
| **ScrapeGraphAI** | ❌ `needs_reconnect` | |
| **Zoom** | ❌ NOT CONNECTED | exists in Zapier catalog (`read 10 / write 6 / search 5`), no account linked |
| **Zoho CRM** | ❌ NOT CONNECTED | exists in Zapier catalog, **Premium tier**, no account linked |
| **Slack / Teams / WhatsApp** | ❌ NOT CONNECTED | |
| **Gmail** | ❌ NOT PRESENT | — see finding #1 below |

### Three findings that change the design

#### FINDING 1 — Email is Hostinger, not Gmail/Outlook
The spec assumes Gmail or Outlook. The actual mailbox is **Hostinger Mail** (`sarah@stravion.ae`), an IMAP-backed REST API. Consequences:

- ✅ **It has webhooks** (`POST /api/v1/mailboxes/{id}/webhooks`, with `test` and `regenerate-secret`). This is a genuine push event source for `NEW_EMAIL`. Better than polling, and better than what the Calendar connector offers.
- ⚠️ **It has no thread model.** Endpoints are folder + UID based (`listMessages`, `getMessage`, `getMessageText`, `getMessageSource`, `searchMessages`). "Summarize this thread" must be built by us: fetch RFC822 source, parse `Message-ID` / `In-Reply-To` / `References`, and reconstruct threads in our own database. This is real work and belongs in Phase 7.
- ⚠️ **No draft-create endpoint is exposed.** There is `sendEmail` but no `createDraft`. The existing house workflow *depends* on drafts living in `INBOX.Drafts`. Needs resolution — see "What I need from you", item 6.
- ⚠️ Rate limit observed: **300 requests/window** (`X-Ratelimit-Limit: 300`). The tool layer needs a token-bucket limiter.

#### FINDING 2 — These MCP connectors cannot power the always-on backend
This is the single most important architectural constraint, and it is easy to get wrong.

The Google Calendar, Google Drive, Hostinger Mail and Zapier connectors listed above are **bound to this Claude session**. They are OAuth grants held by the claude.ai client, brokered per-conversation. A headless server process running at 03:00 has no session, and therefore **cannot call any of them**.

Requirement 1 of the spec — *"The system must NOT depend on the CEO manually starting Claude for every event"* — therefore cannot be satisfied by the connectors alone.

The system must hold **its own service credentials**:

| Layer | Credential it needs |
|---|---|
| Backend (always-on) | Hostinger API token, Google OAuth **refresh token** (offline access), Zoom S2S OAuth, Zoho self-client OAuth |
| Claude session (interactive) | the existing MCP connectors — kept, for the conversational path |

Both paths call the **same internal tool registry**, so behaviour, risk gating and audit logging are identical whichever way a request arrives. The connectors become a convenience front-end, not the foundation.

#### FINDING 3 — The operating policy already exists in prose
The `stravion-outreach` skill encodes hard business rules: no em/en dashes, every letter ends at "Warm regards," with nothing after, CC `ar@alirao.com` on every campaign email and reply, **price is never written**, shareholding never mentioned, one contact per firm forever, location detail limits, and — critically — *"the session does not send, it builds drafts and the user hits send."*

That last rule is already the spec's approval model, stated informally. These rules should not stay in a prompt. They become a versioned, testable **policy pack** enforced in code at the tool boundary (`src/policy/stravion.ts`), so a model that forgets an instruction still cannot send a price in writing. Prompt = guidance; policy engine = guarantee.

---

## A. Architecture diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│  INTERFACES                                                                │
│                                                                            │
│   Claude mobile / desktop          Web dashboard          Push / Email     │
│   (MCP connectors, interactive)    (approvals, audit)     (notifications)  │
└───────────┬──────────────────────────────┬─────────────────────┬───────────┘
            │                              │                     │
            │  MCP (session-scoped)        │  HTTPS + JWT        │  outbound
            ▼                              ▼                     ▲
┌────────────────────────────────────────────────────────────────┴───────────┐
│  ea-mcp-server            │  ea-api (Fastify)                              │
│  our own MCP server       │  /webhooks/*  /approvals/*  /audit/*  /health   │
│  exposes EA tools to      │  HMAC verify, replay guard, RBAC                │
│  Claude clients           │                                                 │
└───────────────┬───────────┴───────────────────┬────────────────────────────┘
                │                               │
                │        ┌──────────────────────▼──────────────────────┐
                │        │  LAYER C — ORCHESTRATION (always-on)        │
                │        │                                             │
                │        │   Redis + BullMQ                            │
                │        │   ├─ events      (idempotent, dedupe key)   │
                │        │   ├─ actions     (exp. backoff, DLQ)        │
                │        │   └─ scheduler   (briefing, due, polls)     │
                │        │                                             │
                │        │   ea-worker  ── event → workflow → outcome  │
                │        └──────────────────────┬──────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  LAYER A — REASONING                                                       │
│  Claude (Agent SDK, claude-opus-5 / claude-sonnet-5 by task class)          │
│  intent → plan → tool selection → risk check → draft → outcome             │
└────────────────────────────────┬───────────────────────────────────────────┘
                                 │  every call passes through:
                    ┌────────────▼────────────┐
                    │  TOOL REGISTRY + GUARD  │
                    │  schema · risk · policy │
                    │  approval · audit · RL  │
                    └────────────┬────────────┘
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  LAYER B — INTEGRATIONS (adapter per system, one interface)                │
│                                                                            │
│  ✅ Hostinger Mail   REST + webhook    sarah@stravion.ae                    │
│  ✅ Google Calendar  API + watch ch.   Asia/Dubai                           │
│  ✅ Google Drive     API                                                    │
│  ⬜ Zoom             S2S OAuth + webhook   ← needs credentials              │
│  ⬜ Zoho CRM         self-client OAuth     ← needs credentials              │
│  ⬜ Google Meet      Meet REST + Drive                                      │
│  ⬜ Slack / WhatsApp / LinkedIn            ← later phases                   │
└────────────────────────────────┬───────────────────────────────────────────┘
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  LAYER D — STATE (PostgreSQL 16 + pgvector)                                │
│  preferences · vip_contacts · firm_register · threads · meetings           │
│  commitments · tasks · approvals · events · audit_log · memory · outbox    │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## B. Technology stack

### Language: **TypeScript** (Node 22)

Recommended over Python. Reasoning:

1. **This is an I/O-orchestration system, not a data-science system.** Almost every operation is an await on someone's HTTP API. Node's event loop is the right shape; there is no CPU-bound or numerical work anywhere in the spec.
2. **MCP is TypeScript-first.** The spec makes MCP the preferred integration abstraction (§18). The reference SDK, and the majority of servers, are TS. We are also *writing* an MCP server (`ea-mcp-server`) so Claude clients can reach our tools — that is materially easier in TS.
3. **One schema, four uses.** The tool registry (§18) demands input schema, output schema, risk level, approval flag. Zod gives us a single declaration that yields the runtime validator, the static type, the JSON Schema for Claude's tool definition, and the API contract. In Python this is Pydantic plus glue, and the MCP story is weaker.
4. **One language end to end** — backend, MCP server, and the approvals web UI. A CEO-facing approval screen is not optional here (§15), and a TS backend means no second toolchain.
5. **Anthropic Agent SDK** has first-class TS support.

Python would win if this were transcript ML, embeddings research, or heavy dataframe work. Transcript *analysis* here is done by Claude, not by us, so that advantage does not apply. **If you prefer Python, say so now** — this is the one decision that is expensive to reverse.

### Components

| Concern | Choice | Why |
|---|---|---|
| Runtime | Node 22 LTS + TypeScript 5.x (strict) | above |
| HTTP | Fastify | fast, schema-first, first-class raw-body access for HMAC webhook verification |
| Queue | BullMQ on Redis 7 | delayed jobs, exponential backoff, DLQ, job IDs = free idempotency (§19, §20) |
| Database | PostgreSQL 16 + pgvector | relational state + audit; vector search for "what did we discuss with ABC" |
| Migrations/ORM | Drizzle | SQL-first, typed, no magic |
| Validation | Zod | one source of truth per §18 |
| Reasoning | Claude Agent SDK — `claude-opus-5` for judgement, `claude-sonnet-5` for classification/extraction | cost/latency split |
| Scheduling | BullMQ repeatable jobs, all cron expressed in UTC, rendered in `Asia/Dubai` via Luxon | DST-safe (Dubai has no DST, but the code must not assume that) |
| Secrets | env vars in dev; cloud secret manager in prod. `.env.example` only, never `.env` | §17 |
| Logging | Pino → structured JSON, with a redaction allowlist | §16, §17 |
| Tests | Vitest + Testcontainers (real Postgres/Redis) + `nock` for HTTP fixtures | §21 |
| Deploy | Docker Compose → single VM (Phase 19); dual process: `api` + `worker` | |

---

## C. Integration map

Legend — **MCP**: usable via existing connector (interactive only). **API**: backend must hold its own credentials. **Both**: implement once behind an adapter, reachable either way.

| Capability | Route | Event source | Status | Blocker |
|---|---|---|---|---|
| Read / search email | Hostinger REST — **Both** | webhook ✅ | Ready | — |
| Thread reconstruction | our code over `getMessageSource` | — | Design done | none |
| Draft email | Hostinger — **API** | — | ⚠️ | no `createDraft` endpoint exposed; see need #6 |
| Send email | Hostinger `POST /send` — **API** | — | Ready | gated HIGH risk |
| Calendar read / write | Google Calendar — **Both** | ⚠️ poll or watch channel | Ready | connector has no push; backend needs OAuth refresh token |
| Drive / documents | Google Drive — **Both** | — | Ready | — |
| **Zoom** meetings + transcripts | Zoom REST — **API** | webhook `meeting.ended`, `recording.completed`, `recording.transcript_completed` ✅ | ⛔ Blocked | Server-to-Server OAuth app credentials |
| **Zoho CRM** | Zoho REST — **API** | Notifications API webhook ✅ | ⛔ Blocked | self-client OAuth credentials + data centre region |
| Google Meet transcripts | Meet REST + Drive — **API** | Calendar watch → `conferenceData` | Partial | Workspace tier dependent; Meet transcripts need Business Standard+ |
| Slack / Teams | — | — | Deferred | M365 connector incomplete |
| WhatsApp Business | Meta WABA — **API** | webhook | Deferred | business verification, template approval |
| LinkedIn | Zapier (4 actions) | — | ⚠️ Limited | LinkedIn's API permits little; automated outreach breaches ToS. Treat as publish-only. |

**Recommendation on Zoom and Zoho: use the direct APIs, not Zapier.** Zapier can call *out* to those systems, but the spec's event engine (§19) needs those systems to call *in* to us — `MEETING_ENDED`, `TRANSCRIPT_AVAILABLE`, `CRM_UPDATED`. Direct webhooks give us signed, replayable, idempotent delivery. Zapier in the middle adds a hop, a cost tier (Zoho CRM is Premium), and no webhook ingress to our backend. Zapier stays useful as a fallback for long-tail apps.

---

## D. Security & permission model

### Risk tiers (§15), enforced in the registry — not in the prompt

| Tier | Rule | Examples |
|---|---|---|
| **LOW** | auto-execute, audit only | read calendar, search mail, summarize thread, prepare briefing, search CRM |
| **MEDIUM** | execute if a configured rule allows; else escalate | create internal meeting, create task, update CRM note, move message to folder |
| **HIGH** | explicit approval, always | send external email, cancel/reschedule an important meeting, write to a CRM deal, external messaging |
| **PROHIBITED** | never autonomous, no override flag exists in code | move money, approve payment, sign contract, delete critical records, legal commitment, impersonate the CEO on a high-risk decision |

Every tool declares (§18): `name`, `description`, `inputSchema`, `outputSchema`, `risk`, `requiresApproval`, `reversible`, `auditLevel`, `rateLimit`, `allowlistGroup`. Destructive tools (`deleteAllMessages`, `deleteMessages`, `deleteFolder`, `trash_file`) are **excluded from the default allowlist** and require an explicit opt-in group.

### Stravion policy pack — enforced, not suggested

Mechanical checks run at the tool boundary on every outbound message body. A violation blocks the call and logs it:

- reject any `—` or `–` in body text
- reject anything typed after `Warm regards,`
- require `ar@alirao.com` in CC on campaign mail and replies
- reject price, yield, leaseback and entry-ratio figures in writing
- reject any mention of the principal's hotel shareholding
- reject a recipient whose firm/domain is already in `firm_register` (one contact per firm, forever)
- reject pre-NDA disclosure of key counts, RevPAR, occupancy, Musataha year
- enforce location granularity: "Palm Jumeirah" only, "Dubai Media City" only, school has no location
- sender must be `sarah@stravion.ae`

### Platform security (§17)

OAuth everywhere available · refresh tokens encrypted at rest (AES-256-GCM, KMS-held key) · separate dev/prod credentials and separate Zoom/Zoho apps · webhook HMAC verification on raw body + timestamp window + replay cache · least-privilege scopes · RBAC (`ceo`, `admin`, `service`) · append-only audit log · secret scanning in CI · `.env` in `.gitignore` from the first commit.

### Legal / consent

Zoom recording and transcription are processed **only** where the meeting was recorded with participant consent under the host's own Zoom settings. The system never initiates covert recording and never enables recording on a meeting by itself. Counterparties here are institutional investors in the UAE and abroad; DIFC/GDPR posture should be confirmed before Phase 8 goes live.

---

## E. Development phases

Phases 0–1 are the current deliverable. Nothing past Phase 1 starts without approval.

| # | Phase | Output | Gate |
|---|---|---|---|
| 0 | ✅ Environment inspection | this document, §0 | done |
| 1 | ⏳ Architecture | this document | **← YOU ARE HERE — approval needed** |
| 2 | Repo structure | skeleton, CI, lint, typecheck | |
| 3 | Config system | Zod-validated config, tz + hours, `.env.example` | tz test passes |
| 4 | Auth & security | token vault, OAuth flows, HMAC middleware, RBAC | secret scan clean |
| 5 | Tool registry | schema + risk + guard + audit, no real integrations | registry unit tests |
| 6 | Calendar | read, availability, create, conflict detection | conflict tests pass |
| 7 | Email | fetch, thread reconstruction, classify, draft | thread tests pass |
| 8 | Zoom | meetings, webhooks, transcripts | **blocked on credentials** |
| 9 | Zoho CRM | contacts, accounts, deals, notes | **blocked on credentials** |
| 10 | Meeting intelligence | decisions, action items, owners, deadlines | extraction eval set |
| 11 | Memory | preferences, VIPs, firm register, semantic recall | no silent writes |
| 12 | Event engine | queues, idempotency, backoff, DLQ, replay | duplicate-suppression test |
| 13 | Morning briefing | 10:00 Asia/Dubai | |
| 14 | Approval system | approval objects, expiry, UI, notify | full audit trail |
| 15 | Notifications | CRITICAL/HIGH/NORMAL/LOW + quiet hours | |
| 16 | Claude/mobile interface | `ea-mcp-server` | |
| 17 | Security review | threat model, pen pass, scope audit | |
| 18 | Integration testing | sandbox accounts only | `tests.json` green |
| 19 | Deployment | Docker, migrations, backups, runbook | |
| 20 | Monitoring | health, alerts, DLQ watch, cost tracking | |

### Proposed repository structure

```
shaw/
├── README.md  ARCHITECTURE.md  SETUP.md  SECURITY.md  INTEGRATIONS.md
├── PERMISSIONS.md  AUTOMATIONS.md  TROUBLESHOOTING.md  DEPLOYMENT.md
├── TESTING.md  CHANGELOG.md
├── progress.md  todo.md  tests.json
├── .env.example                      # never .env
├── .gitignore  .github/workflows/ci.yml
├── docker-compose.yml  Dockerfile
├── package.json  tsconfig.json  drizzle.config.ts  vitest.config.ts
│
├── src/
│   ├── config/         # Zod-validated env, timezone, operating hours
│   ├── db/             # schema.ts, migrations/, repositories/
│   ├── auth/           # token vault, oauth/, rbac.ts, crypto.ts
│   ├── registry/       # tool.ts, guard.ts, risk.ts, allowlist.ts
│   ├── policy/         # engine.ts, stravion.ts, rules/
│   ├── integrations/
│   │   ├── hostinger/  # client, webhooks, threading, rate-limit
│   │   ├── google/     # calendar/, drive/, meet/, oauth
│   │   ├── zoom/       # client, webhooks, transcripts
│   │   ├── zoho/       # crm/, oauth, notifications
│   │   └── base/       # Adapter interface, retry, circuit breaker
│   ├── agent/          # claude client, prompts/, intent, model routing
│   ├── events/         # types, queues, dedupe, dlq, handlers/
│   ├── workflows/      # morning-briefing, meeting-prep, meeting-followup,
│   │                   # email-triage, commitment-tracker
│   ├── approvals/      # store, notify, expiry
│   ├── memory/         # preferences, vip, firm-register, semantic
│   ├── notifications/  # priority classifier, channels/, quiet-hours
│   ├── audit/          # logger, query
│   ├── api/            # server, routes/, middleware/
│   ├── mcp/            # ea-mcp-server
│   └── worker/         # worker entrypoint, scheduler
│
├── tests/  unit/  integration/  fixtures/  e2e/
└── scripts/  seed  register-webhooks  oauth-bootstrap
```

---

## F. What I need from you

**Decisions (blocking Phase 2):**

1. **TypeScript — confirm or override.** My recommendation is above.
2. **Hosting.** Where does the always-on backend live? Options: a VPS you control (Hostinger already bills you), AWS/GCP, or Fly.io. It needs a **stable public HTTPS URL** for webhooks, which this dev container does not have. Without it, Zoom/Zoho/Hostinger push events cannot reach us and Layer C degrades to polling.
3. **Whose assistant is this?** Three identities appeared: `titanarshian@gmail.com` (this account), `aamirsawar123@gmail.com` (the connected calendar), `sarah@stravion.ae` (the mailbox). The calendar and the mailbox belong to different people. Tell me which one is the CEO/principal, and whether the assistant manages one person or both.
4. **Zoom — is it actually in use?** The spec devotes a section to it, but no Zoom account is connected. If meetings are on Zoom, I need a **Server-to-Server OAuth app**: Account ID, Client ID, Client Secret, and a Webhook Secret Token, with scopes `meeting:read`, `recording:read`, `user:read`. If meetings are really on Google Meet or Teams, say so and I will drop the Zoom phase.
5. **Zoho — which products, and is there data in them today?** I need a self-client OAuth Client ID + Secret, the **data centre region** (`.com` / `.eu` / `.sa` / `.in` — this changes every endpoint), and confirmation of which modules matter (Contacts, Accounts, Deals, Activities). Also: is Zoho CRM already populated, or would we be starting it from scratch? If it is empty, I would rather build the firm register in Postgres first and sync to Zoho later.
6. **Email drafts.** The Hostinger API exposes `send` but no draft-create endpoint, while the current workflow depends on drafts in `INBOX.Drafts`. Three options: (a) get IMAP credentials for the mailbox and APPEND drafts directly — cleanest, preserves your current habit; (b) hold drafts in our database and expose them in an approval UI, sending on approval; (c) both. I recommend **(c)**, starting with (b). Which do you want?
7. **Approval channel.** When the assistant needs a yes/no at 21:40, how should it reach you — WhatsApp, email to a second address, push via a small web app, or Claude chat only?

**Credentials (do not paste them in chat — I will give you a `.env.example` and a secure path):**

- Hostinger API token for backend use (separate from this session's connector)
- Google OAuth client + **offline refresh token** for calendar/drive
- Zoom S2S OAuth app (if Zoom is in scope)
- Zoho self-client OAuth (if Zoho is in scope)

**Things I will not do without you telling me to:**

- LinkedIn automation beyond what the official API permits. The 4 Zapier LinkedIn actions are publish-oriented; automated connection requests and scraping breach LinkedIn's ToS and risk the account. I will not build that quietly.
- Browser automation as a substitute for a missing API. If a capability has no supported API, I will tell you before writing a fragile workaround (§24).
- Any covert recording or transcription.

---

## Open risks

| Risk | Impact | Mitigation |
|---|---|---|
| No public HTTPS endpoint yet | Layer C cannot receive push events | decide hosting (need #2); poll as interim |
| Session-scoped connectors ≠ backend auth | "always-on" silently fails | backend holds own credentials (Finding 2) |
| Hostinger 300 req/window | triage stalls on a busy inbox | token bucket + incremental sync + cache |
| No thread model in mail API | weak summarization | reconstruct from RFC822 headers, store in Postgres |
| LLM non-determinism on policy rules | a price reaches a counterparty in writing | mechanical policy engine at tool boundary, plus tests |
| Zoom/Zoho unverified | two phases may be dead weight | confirm in needs #4 and #5 before building |
