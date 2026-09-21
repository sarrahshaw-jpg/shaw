# CEO AI Executive Assistant — Architecture v4

**Status:** PROPOSED, Phases 0–1 complete, **awaiting written approval**. No application code exists.
**Principal:** Ali Rao (`ar@alirao.com`), CEO, Stravion Investments (Titans Real Estate LLC), Dubai. **Delegate:** Sarah Shaw (`sarah@stravion.ae`). All principal facts are configuration.
**Defaults (config, not constants):** tz `Asia/Dubai` · hours 10:00–22:00 · booking 10:00–18:00 · briefing 10:00 · wrap 21:30 · approval expiry 72h · meeting 30 min · buffer 15 min.
**History:** v1 custom backend (`docs/ARCHITECTURE-v1-backend.md`) → v2 Claude‑native (built in `claude/`) → v3 two‑track (`docs/ARCHITECTURE-v3-two-track.md`) → **v4** (this): same recommendation as v3, restated in the shape the condensed prompt asks for, with the option judgement, per‑integration auth, hosting and credential fields made explicit.

---

## 0. Phase 0 — environment inspection (re‑verified 2026‑09‑21)

| Item | Finding |
|---|---|
| Repo | `sarrahshaw-jpg/shaw`, branch `claude/busy-mccarthy-gu06jb`, 4 commits, Track 1 package + docs, no code |
| Host | Ubuntu 24.04, 4 vCPU, 15 GiB; Node 22.22 / npm 10.9; Python 3.11.15 / uv 0.8; Docker 29.3; Postgres 16 + Redis 7 clients; egress via policy proxy; **no public inbound URL** |
| Google Calendar | connected, calendar `aamirsawar123@gmail.com`, tz `Asia/Dubai` |
| Google Drive | connected; **no `EA — Ali Rao` folder exists**; Track 1 never installed |
| Hostinger Mail | connected; one mailbox `sarah@stravion.ae`; 300 req/window; webhook endpoints present; no thread model; no draft‑create |
| Zapier | connected; LinkedIn only (4 actions) |
| Apify · Vibe Prospecting · Indeed | connected; research only |
| Zoom · Zoho CRM · Gmail · Microsoft 365 · Slack | **not connected in this session**; official claude.ai connectors exist for all five (directory, verified 19 Sep) |
| Claude Code Routines | **3 live Routines** in this account (LinkedIn prep ×2, DMC reply watch) run daily in fresh cloud sessions with Drive/Hostinger/Calendar/Zapier connectors and push notifications; run history visible; one run failed 18 Sep. Minimum interval hourly. |
| `ar@alirao.com` mail host | **unknown**; MX lookup blocked by egress policy |

Identities: `titanarshian@gmail.com` operates this workspace; `aamirsawar123@gmail.com` is the connected calendar (not confirmed as Ali's); `sarah@stravion.ae` is the connected mailbox. Nothing is wired to Ali's own accounts yet.

---

## A. Architecture diagram

```
 Ali (phone / desktop / voice)          Sarah (delegate)            Admin
        │ natural language                    │                        │ edits config + rules
        ▼                                     ▼                        ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER A  REASONING   Claude Project "Executive Assistant"                        │
│   PROJECT_INSTRUCTIONS.md + skills: operating-model · email · calendar ·          │
│   meeting-prep · meeting-followup · zoho-crm · morning-briefing · memory ·        │
│   commitments        intent → skill → tool plan → risk tier → act | card | refuse │
└───────────────┬──────────────────────────────────────────────┬───────────────────┘
                │ LOW-risk reads: official connectors directly  │ MEDIUM/HIGH writes
                │                                               ▼
                │                    ┌──────────────────────────────────────────────┐
                │                    │  APPROVAL CHOKEPOINT  (ea-core MCP tool)      │
                │                    │  registry: schema · tier · approval · audit   │
                │                    │  policy pack: price/dash/firm/CC/disclosure   │
                │                    │  HIGH → approval object (72h) → CEO "approve" │
                │                    │  PROHIBITED → refused, no flag                │
                │                    │  every call → audit_log (append-only)         │
                │                    └──────────────────┬───────────────────────────┘
                ▼                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER B  TOOLS   official connectors, per-user OAuth          │ official APIs,    │
│   Google Calendar · Google Drive · Gmail | Hostinger | M365    │ service creds     │
│   Zoho CRM · Zoom for Claude · Slack (later) · Zapier→LinkedIn │ (Track 2 adapters)│
└──────────────────────────────────────────────────────────────────────────────────┘
        ▲ tool calls                                            ▲ webhooks in
        │                                                       │
┌───────┴──────────────────────────────┐   ┌────────────────────┴──────────────────┐
│ LAYER C  ALWAYS-ON  (Track 1)        │   │ LAYER C+  (Track 2, hosted)           │
│  Routines / scheduled tasks, fresh   │   │  ingress: HMAC + ts window + replay   │
│  session each run, connectors on:    │   │  queue (BullMQ): dedupe key, backoff, │
│   10:00 briefing · hourly sweep      │   │  DLQ, replay; admin alert on repeat   │
│   11:00–21:00 · 21:30 wrap           │◀──│  handler: fire_trigger(Routine) with  │
│  never executes HIGH; queues cards   │   │  context, or Agent SDK workflow       │
└───────────────┬──────────────────────┘   └────────────────────┬──────────────────┘
                ▼                                               ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER D  STATE                                                                   │
│  Track 1: Drive folder "EA — Ali Rao": 00-config · 01-preferences · 02-vips ·     │
│   03-firm-register · 04-commitments · 05-approvals · 06-rules · 07-processed ·     │
│   audit/ · drafts/ · meetings/ · briefings/                                        │
│  Track 2: Postgres (same records, append-only audit_log, approvals, events,       │
│   memory_changes) — Drive kept as the human-readable mirror                       │
└──────────────────────────────────────────────────────────────────────────────────┘

 Event flow:  provider webhook ─▶ ingress (verify, dedupe) ─▶ queue ─▶ handler ─▶ Claude
              ─▶ registry gate ─▶ [LOW: do] [MEDIUM: rule?] [HIGH: card, WAITING FOR
              APPROVAL] [PROHIBITED: refuse] ─▶ outcome status ─▶ audit ─▶ notify by tier
```

---

## B. Technology stack

### Language decision: **TypeScript** (Node 22) for everything that is code
Evaluated on the five axes you named:

| Axis | TypeScript | Python | Weight |
|---|---|---|---|
| MCP ecosystem + Agent SDK | reference MCP SDK is TS‑first; Agent SDK has first‑class TS; we *ship* an MCP server | FastMCP is good; Agent SDK also supports Python | TS ahead |
| Single‑declaration tool schemas | Zod → validator + static type + JSON Schema for Claude + API contract, one object | Pydantic v2 does the same; JSON Schema export is fine | tie |
| Workload profile | pure I/O orchestration over HTTP; event loop is the natural shape; no numeric work (Claude does the analysis) | async works, but ecosystem pulls toward sync/data tooling we do not need | TS ahead |
| Webhook / queue / DB / deploy | Fastify raw‑body HMAC, BullMQ (delayed jobs, backoff, DLQ, job‑id idempotency), Drizzle, one Docker image | FastAPI, Celery/arq, SQLAlchemy; Celery is heavier than needed | TS ahead |
| One language across backend + MCP server + approval UI | yes | UI would be a second toolchain | TS ahead |

Python would win if we did transcript ML, embeddings research or dataframe work ourselves. The spec routes all analysis through Claude, so that advantage never applies. **Recommendation: TypeScript.** Override cost: high once Phase 5 starts, near zero now.

### Components (Track 2 `ea-core`) and why each exists
| Component | Choice | Exists because |
|---|---|---|
| Runtime | Node 22 LTS, TypeScript 5 strict | above |
| Tool registry + guard | Zod schemas, one `defineTool()` per tool | spec §18: single source of truth, risk tier, approval, allowlist |
| Policy engine | pure functions over outbound bodies | §5 of the condensed prompt: violations block in code, not prompt |
| MCP server | `@modelcontextprotocol/sdk`, HTTP transport | the Claude Project reaches the registry as one connector; CEO sees nothing |
| HTTP | Fastify | raw body for HMAC; schema‑first routes |
| Queue | BullMQ on Redis 7 | §19/§20: dedupe by job id, exponential backoff, DLQ, replay |
| Database | Postgres 16, Drizzle migrations | §16/§10: durable audit, approvals, memory; append‑only trigger on `audit_log` |
| Reasoning | Claude Agent SDK; `claude-opus-5` judgement, `claude-sonnet-5` classification/extraction | cost/latency split; model ids per current docs |
| Time | Luxon; all cron in UTC, rendered in configured tz | §3: no hard‑coded tz; Dubai has no DST but code must not assume |
| Secrets | env in dev, host secret store in prod, `.env.example` committed | §17 |
| Logging | Pino JSON with redaction | §16, §17 |
| Tests | Vitest, Testcontainers (real Postgres/Redis), recorded HTTP fixtures | §21 |
| Deploy | Docker Compose: `api`, `worker`, `postgres`, `redis`, `caddy` (TLS) | §19 hosting |

Track 1 has no code: Claude Project, skills, Routines/scheduled tasks, Drive markdown.

---

## C. The shape: three options judged, one recommended

| Criterion | Option 1 custom backend (v1) | Option 2 Claude‑native (v2, built) | **Option 3 hybrid (recommended)** |
|---|---|---|---|
| No dependency on CEO starting Claude | yes, webhooks | yes, hourly Routines (proven in this account) | yes; hourly day 1, webhook‑driven once ea-core is up |
| Code‑enforced HIGH blocking | yes | **no**: model + human approval only | yes for every send‑class action routed through ea-core |
| Audit durability | append‑only DB | Drive markdown, editable by folder editors | DB append‑only + Drive mirror |
| Latency | seconds | ≤ 60 min | ≤ 60 min until ea-core; seconds after |
| Cost | 4–6 weeks build; VM + API spend from day 1 | near zero; days to install | Track 1 in days; ea-core 3–4 weeks (no dashboard, no notifier: Claude's app does both) |
| Hosting you must provide | VM + public HTTPS + secrets from day 1 | none | none for Track 1; one small VM for Track 2 |

**Recommendation: Option 3, staged.** Install Track 1 now, run the 22 evals on real accounts, then build `ea-core` with the evidence of where hourly latency and model‑only policy actually bit.

### Requirements the recommended option cannot meet, and accepted trade‑offs
| Spec requirement | Track 1 alone | After Track 2 |
|---|---|---|
| §19 event‑driven, sub‑hour reaction (meeting ended → follow‑up) | **not met**: ≤ 60 min, polling by Routine | met via Zoom/Zoho/Hostinger/Google webhooks |
| §15/§5 HIGH blocking and policy enforced in code | **not met**: enforced by model plus a human approval step; a slip is caught at the card, not before it | met at the registry |
| §16 tamper‑resistant audit | **partial**: Drive file, append by convention | met: DB append‑only |
| §21 automated tests | **not met**: behavioural evals run by hand | met: unit + integration suites; evals stay for the model layer |
| §20 admin alert on persistent failure | **partial**: Routine run history shows failures; nobody is paged | met: DLQ watcher |
| §17 webhook validation | n/a (no webhooks) | met |
| §7 MEETING_STARTED event | **not met on either track without Zoom webhooks**; only `meeting.ended` and transcript events are useful anyway | met |
| Sub‑hour is impossible on Track 1 | accepted: the assistant is a chief of staff, not a pager; the 10:00 briefing, hourly sweeps and live chat cover the CEO's actual asks | |

Named limitation per condensed prompt §3: on Track 1 **every** event class is handled through the Claude product surface (Routines). Latency cost ≤ 60 min; reliability cost = a failed run is visible but not paged.

### What runs continuously vs through Claude directly
| Continuously (Layer C) | Through Claude directly (Layer A, on demand) |
|---|---|
| 10:00 briefing; hourly sweep 11:00–21:00 (NEW_EMAIL, VIP_MESSAGE, CALENDAR_CHANGED, MEETING_ENDED/TRANSCRIPT_AVAILABLE, CRM_UPDATED); 21:30 wrap (TASK_DUE, commitments) | every §4 request: schedule, inbox, drafts, prep, "what did we agree", CRM brief, updates behind a card |
| Track 2 adds: webhook ingress, queue, DLQ watcher, approval expiry, early briefing on overnight CRITICAL | approvals themselves: only a person in a live session can approve |

---

## D. Integration map

Classification: **MCP** = official claude.ai connector · **API+code** = official API behind ea-core adapter · **custom‑only** · **not feasible officially**.

| Capability | Track 1 route | Track 2 route | Auth (who connects) | Event source | Status / blocker |
|---|---|---|---|---|---|
| Calendar | **MCP** Google Calendar | API+code, Calendar API | connector OAuth by Ali; T2: Google OAuth client, offline refresh token, scope `calendar` | Calendar push channel (`events.watch`) | connected (whose calendar is `aamirsawar123@gmail.com`?) |
| Drive / docs / state | **MCP** Google Drive | API+code | same client; scope `drive` (or `drive.file` if state folder only) | Drive changes API | connected |
| Mail, Ali | **MCP** Gmail *or* Hostinger *or* Microsoft 365 | API+code for the same host | Ali connects; T2: Gmail `gmail.modify` + Pub/Sub `users.watch`; Hostinger `HOSTINGER_API_TOKEN`; M365 Graph app + `Mail.ReadWrite`, `Mail.Send` | Gmail push / Hostinger webhook / Graph subscription | **blocked: host of `ar@alirao.com` unknown** |
| Mail, Sarah | **MCP** Hostinger Mail | API+code | connected; T2 token | Hostinger webhook (HMAC secret from `regenerate-secret`) | no threads, no drafts: threads rebuilt from `Message-ID`/`References`; drafts kept in state until approved |
| CRM | **MCP** Zoho CRM (official, 41 tools) | API+code, Zoho CRM v8 REST | Ali or org admin connects; T2: self‑client `ZOHO_CLIENT_ID/SECRET`, `ZOHO_DATA_CENTER`, scopes `ZohoCRM.modules.ALL`, `ZohoCRM.settings.READ`, `ZohoCRM.notifications.ALL` | Zoho Notifications API | not connected |
| Meetings, Zoom | **MCP** Zoom for Claude (search, recap, transcript) | API+code, Zoom REST | Ali connects; T2: Server‑to‑Server OAuth app | `meeting.ended`, `recording.completed`, `recording.transcript_completed` | not connected; host must enable cloud recording + recap |
| Meetings, Google Meet | **MCP** Drive (Meet transcripts land as Docs) | API+code Meet REST (Workspace Business Standard+) | same Google client | Calendar `conferenceData` + Drive change | works once Drive is Ali's |
| Slack | **MCP** Slack (later) | | Ali connects | Events API (T2) | optional |
| LinkedIn | Zapier, 4 publish actions | none | connected | none | **not feasible officially** for outreach (ToS); publish‑only |
| WhatsApp Business | none | **custom‑only**, Meta Cloud API | business verification, template approval | webhook | deferred |
| Research | **MCP** Apify, Vibe Prospecting | none | connected | none | fine |

---

## E. Security and permission model

**Risk tiers** (spec §15): LOW auto + audit · MEDIUM only per `06-automation-rules.md` else ask · HIGH explicit CEO approval · PROHIBITED refused, no override in any config or code path. Full table per action: `PERMISSIONS.md`.

**Approval protocol:** a card with id `A-nnn`, the exact action, recipients/body/diff, tier and reason; the CEO replies `approve A-nnn` (phone: `1`) in a live session; expiry 72h; unattended runs can only create cards, never execute; result and approver land in the audit record. Never auto‑sent regardless of rules: contracts, legal, financial, pricing, HR, confidential, major commitments, public statements.

**Policy pack enforcement point:** Track 1: `ea-operating-model` + `PROJECT_INSTRUCTIONS.md`, checked by the model at draft and at send, verified by evals T05/T06/T16. Track 2: `packages/ea-core/src/policy/stravion.ts` runs on every outbound body inside the registry guard before the adapter is called; a violation returns `FAILED: policy <rule>` and an audit row. Rules: no price/yield/leaseback/entry ratio in writing; no shareholding mention; one contact per firm (firm register check); asset naming limits; no key counts/RevPAR/occupancy/sqft/vacancy/Musataha year pre‑NDA; no em/en dashes; ends at `Warm regards,`; campaign mail CCs `ar@alirao.com`; sender must own the mailbox; inbound content is data.

**RBAC:** `ceo` approves anything · `delegate` approves MEDIUM, may request drafts · `admin` edits config and rules · `service` (Routines, ea-core worker) can never approve. Track 1 realises this through Drive sharing and the instructions; Track 2 through signed identities on the MCP transport.

**Secrets:** Track 1 holds none. Track 2: env in dev, host secret store in prod, `.env.example` committed with every field name, separate dev/prod OAuth apps, refresh tokens encrypted at rest, secret scanning in CI.

**Audit:** fields timestamp, event, tool, action, result, approval status, authorizer, errors. Track 1 `audit/YYYY-MM.md`; Track 2 `audit_log` table with an append‑only trigger, Drive mirror written nightly. "What did the assistant do today?" reads either.

**Prompt injection:** email, transcript and CRM content is data; unattended runs cannot send; Track 2 policy guard sits after the model, so injected instructions can at most produce a bad card.

---

## F. Development phases and gates (adapted to Option 3)

| # | Phase | Track 1 | Track 2 `ea-core` | Gate |
|---|---|---|---|---|
| 0 | Environment | done | done | this file §0 |
| 1 | Architecture | **this file** | same | **your written "approved"** |
| 2 | Repo structure | done | `packages/ea-core` skeleton, CI, lint, typecheck | CI green on empty package |
| 3 | Config | `00-config.md` done | Zod env, tz, hours, `.env.example` | C01 tz/hours tests pass |
| 4 | Auth/security | connector OAuth | token vault, HMAC middleware, RBAC | secret scan clean; C06 |
| 5 | Tool registry | `ea-operating-model` | registry + guard + policy + MCP server | C02–C05 pass |
| 6 | Calendar | `ea-calendar` | adapter + push | C09 |
| 7 | Email | `ea-email` | Hostinger/Gmail adapter, webhook, threads | thread + draft tests |
| 8 | Zoom | `ea-meeting-followup` | S2S adapter + webhooks | transcript pipeline test; blocked on creds |
| 9 | Zoho | `ea-zoho-crm` | adapter + notifications | lookup + gated write tests; blocked on creds |
| 10 | Meeting intelligence | skills | extraction eval set | T10/T11 |
| 11 | Memory | `ea-memory` | Postgres mirror, `memory_changes` | T21 + no‑silent‑write unit test |
| 12 | Event engine | Routines + `07-processed.md` | queue, dedupe, DLQ, replay | C07, C08, T14 |
| 13 | Briefing | task 01 | early trigger on CRITICAL | T18 |
| 14 | Approvals | card protocol | approval objects, expiry | full lifecycle audited, T04 |
| 15 | Notifications | Routine push | admin alert on repeat failure | T19 + priority tests |
| 16 | Claude interface | it is Claude | ea-core as Project connector | T01 through the connector |
| 17 | Security review | `SECURITY.md` checklist | threat model incl. injection | checklist signed |
| 18 | Integration testing | T01–T22 on real accounts | automated suite | `tests.json` green or blocked accepted by you |
| 19 | Deployment | `LAUNCH.md` | Docker on VM, runbook | runbook exercised once |
| 20 | Monitoring | evening wrap + run history | health, DLQ watch, cost | first weekly review |

### Hosting requirements
Track 1: **none.** Track 2: one always‑on VM (2 vCPU / 4 GB is enough), Docker, a DNS name with TLS (Caddy auto‑cert) reachable from Zoom, Zoho, Hostinger and Google for webhooks, Postgres + Redis as containers with nightly Postgres backup, a secret store (host env file with 600 perms at minimum), outbound HTTPS. Fly.io or a Hostinger VPS both fit.

### Repository structure (chosen shape)
```
shaw/
├── CLAUDE.md  README.md  ARCHITECTURE.md  LAUNCH.md  SETUP.md  SECURITY.md  INTEGRATIONS.md
├── PERMISSIONS.md  AUTOMATIONS.md  TROUBLESHOOTING.md  DEPLOYMENT.md  TESTING.md  CHANGELOG.md
├── progress.md  todo.md  tests.json
├── docs/MASTER_BUILD_SPEC.md  docs/ARCHITECTURE-v1-backend.md  docs/ARCHITECTURE-v3-two-track.md
├── claude/            PROJECT_INSTRUCTIONS.md · skills/ea-*/ · scheduled-tasks/ · state-templates/
├── evals/scenarios/   T01..T22
├── scripts/           make-skill-zips.sh
└── packages/ea-core/  (after approval)
    ├── package.json tsconfig.json vitest.config.ts drizzle.config.ts .env.example Dockerfile docker-compose.yml
    ├── src/config  registry  policy  mcp  ingress  events  integrations/{hostinger,google,zoom,zoho,base}
    │   approvals  audit  memory  notifications  agent  worker
    └── tests/unit  integration  fixtures
```

---

## G. What is needed from you

### Decisions
1. **Shape.** (1) custom backend first · (2) Claude‑native only · **(3) hybrid, staged — recommended.**
2. **Language for code.** **TypeScript — recommended.** Say "Python" now if you want it; after Phase 5 it is expensive.
3. **Plan for Ali.** (a) Claude Team, shared Project and org skills — **recommended** · (b) Enterprise, if SSO/audit API required · (c) Ali's own Pro/Max.
4. **Background runner.** (a) claude.ai scheduled tasks in Ali's account, everything in one place for him — **recommended for Ali** · (b) Claude Code Routines, proven here, easier for the admin to inspect.
5. **Ali's mail host** for `ar@alirao.com`: Google Workspace / Hostinger / Microsoft 365. This sets `mail_provider` and which adapter gets built.
6. **Calendar identity.** Is `aamirsawar123@gmail.com` Ali's calendar, or must Ali connect his own?
7. **Draft strategy for Hostinger** (no draft endpoint): (a) drafts held in state and sent on approval — **recommended** · (b) IMAP credentials to append into `INBOX.Drafts` · (c) both.

### Credentials (Track 2 only; Track 1 needs **none**: each person connects their own connectors)
Never paste values in chat. `.env.example` will carry every name below.
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` — Google Cloud Console → APIs & Services → Credentials → OAuth client (Web), consent screen internal, offline access; scopes `https://www.googleapis.com/auth/calendar`, `.../drive`, `.../gmail.modify` (only if Gmail hosts Ali's mail). Plus `GOOGLE_PUBSUB_TOPIC` for Gmail push.
- `HOSTINGER_API_TOKEN` — hPanel → Emails → API; `HOSTINGER_WEBHOOK_SECRET` comes from the API's `regenerate-secret` call, stored not chosen.
- `ZOOM_S2S_ACCOUNT_ID` / `ZOOM_S2S_CLIENT_ID` / `ZOOM_S2S_CLIENT_SECRET` / `ZOOM_WEBHOOK_SECRET_TOKEN` — Zoom App Marketplace → Develop → Server‑to‑Server OAuth; scopes `meeting:read`, `recording:read`, `user:read` (granular equivalents as the console names them at creation); event subscriptions `meeting.ended`, `recording.completed`, `recording.transcript_completed`.
- `ZOHO_CLIENT_ID` / `ZOHO_CLIENT_SECRET` / `ZOHO_DATA_CENTER` (`com` / `eu` / `sa` / `in`) / `ZOHO_REFRESH_TOKEN` — Zoho API Console → Self Client; scopes `ZohoCRM.modules.ALL`, `ZohoCRM.settings.READ`, `ZohoCRM.notifications.ALL`.
- `ANTHROPIC_API_KEY` — console.anthropic.com, a key scoped to a separate dev and prod workspace.
- `EA_MCP_AUTH_TOKEN` (ea-core generates), `DATABASE_URL`, `REDIS_URL`, `EA_PUBLIC_URL`.

### Not built without an explicit instruction
LinkedIn automation beyond publish; browser automation in place of a missing API; any recording or transcription initiation; auto‑send rules of any kind.
