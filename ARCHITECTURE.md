# CEO AI Executive Assistant — Architecture (v3, reconciled with the master spec)

**Principal:** Ali Rao, CEO, Stravion Investments (Titans Real Estate LLC), Dubai
**Delegate / operator:** Sarah Shaw, Director of Sales & Strategy (`sarah@stravion.ae`)
**Timezone:** `Asia/Dubai`, one setting in `state/00-config.md`. **Hours:** 10:00–22:00, configurable.
**Status:** PROPOSED. Phases 0–1 complete. No application code exists. Awaiting your approval of the track choice in §F.

---

## 0. Where this stands

| Session | What happened |
|---|---|
| 1, part 1 | Phase 0 inspection; **v1** proposal: TypeScript backend (Fastify, BullMQ, Postgres). Kept in `docs/ARCHITECTURE-v1-backend.md`. |
| 1, part 2–3 | Your direction: "everything inside Claude, no separate tool, principal is Ali". **v2** built: Project instructions, 9 skills, 3 scheduled‑task prompts, Drive state templates, 22 behavioural evals, full doc set. Nothing installed yet. |
| 2 (this) | Master spec re‑issued. Environment re‑inspected (§A). v2 checked line by line against the spec (§B). This document reconciles the two and proposes a staged track (§C). |

Nothing in v2 is thrown away. The question this document answers is whether v2 alone meets the spec, and where it does not, what the smallest addition is.

---

## A. Environment inspection (re‑verified 2026‑09‑19, session 2)

### Host (this dev container)
Ubuntu 24.04, 4 vCPU, 15 GiB, Node 22.22, npm 10.9, Python 3.11.15 (uv 0.8), Docker 29.3, Postgres 16 and Redis 7 clients. Egress only through a policy proxy. **No public inbound URL**, so nothing here can receive a webhook.

### Live connectors in this session (each called, not assumed)
| System | State | Evidence |
|---|---|---|
| Google Calendar | connected | calendar `aamirsawar123@gmail.com`, tz `Asia/Dubai`, plus UAE holidays |
| Google Drive | connected | search works; **no `EA — Ali Rao` folder exists yet** |
| Hostinger Mail | connected | one mailbox `sarah@stravion.ae`, rate limit 300/window, webhooks endpoints present, no thread model, no draft‑create |
| Zapier | connected | LinkedIn only (4 actions, 1 connection) |
| Apify, Vibe Prospecting, Indeed | connected | research only |
| Zoom, Zoho CRM, Gmail, Microsoft 365, Slack | **not connected** | official connectors exist in the claude.ai directory (verified session 1) |

### Always‑on mechanisms available today (new finding)
1. **Claude Code Routines** (`Claude_Code_Remote`): this account already runs **three** daily Routines (LinkedIn prep 06:00/06:30 UTC, DMC reply watch 05:00 UTC). Each fires a fresh cloud session with Drive, Hostinger, Calendar and Zapier connectors attached, uses Drive memory files, and sends a push notification on completion. Run history is visible; one run on 18 Sep **failed**, which shows both that failures are recorded and that a retry/alert policy is needed. Minimum interval: hourly. This is a working Layer C, in production, for a sibling project.
2. **claude.ai scheduled tasks** (v2's assumption): same shape, created in the claude.ai UI, in Ali's own account.
3. `watch_url` inbound webhooks exist on this connector but are built for the artifact service with a sealed signing key; **not verified** as usable by Hostinger, Zoom or Zoho. Treated as unavailable.

**Conclusion:** the spec's "must not depend on the CEO starting Claude" is satisfiable inside Claude, at hourly granularity, with a mechanism already proven in this account. Sub‑hour reaction (a webhook firing seconds after a meeting ends) is **not** possible without a hosted process with a public URL.

---

## B. Master spec vs v2 — the gap table

| Spec § | Requirement | v2 (Claude‑native) | Gap | Needs code? |
|---|---|---|---|---|
| 2 | Four layers | yes: Project/skills · connectors · scheduled runs · Drive folder | none | no |
| 3 | Operating hours, tz configurable | `00-config.md`; crons in UTC | none | no |
| 4 | Natural language | Project instructions map intent to skills | none | no |
| 5 | Email read/draft/send with approval; rules engine | `ea-email`, `06-automation-rules.md`; Hostinger has no drafts, skill keeps drafts in Drive | rules are prose, model‑enforced | for a *guarantee* |
| 6 | Calendar rules configurable | `ea-calendar`, `01-preferences.md` | none | no |
| 7 | Zoom: detect meeting ended → transcript → extract | hourly sweep reads Zoom recap via connector | latency ≤ 60 min, not event‑driven | for sub‑hour |
| 8 | Google Meet interchangeable | Meet transcripts read from Drive | none | no |
| 9 | Zoho CRM read + controlled write | `ea-zoho-crm` via official connector | none | no |
| 10 | Memory, no silent invention | `ea-memory`, logged proposals | none | no |
| 11 | 10:00 briefing | task 01 | none | no |
| 12–13 | Meeting prep / follow‑up | skills | none | no |
| 14 | 4‑level priority | in instructions | none | no |
| 15 | Risk tiers, prohibited list | `ea-operating-model` | enforced by model + human, not by code | for a *guarantee* |
| 16 | Audit log | `audit/YYYY-MM.md` append by convention | writable by anyone with folder edit | for tamper‑resistance |
| 17 | OAuth, secrets, webhook validation, RBAC | OAuth via connectors; no secrets exist; RBAC = Drive sharing | webhook validation N/A (no webhooks) | only if webhooks exist |
| 18 | Tool registry with schemas, risk, allowlists | tier table in prose; connector tools are the registry | not machine‑readable | for a *guarantee* |
| 19 | Event queue, idempotent | `07-processed.md` IDs; hourly runs | no push events; hourly | for sub‑hour |
| 20 | Failure handling, retry, replay, admin alert | retry once, report; unprocessed items reappear next run | no automatic admin alert on repeated failure | partly (Routine run history exists) |
| 21 | **Automated tests** | 22 behavioural eval scenarios, run by hand | **not automated** | yes |
| 23 | Doc set + progress/tests/todo | complete | none | no |

**Reading of the table:** v2 covers every *capability* in the spec. The four things it cannot deliver are all of one kind: **guarantees enforced by code** (policy, tool registry, tamper‑resistant audit, automated tests) and **sub‑hour event reaction**. Those are exactly what a backend is for, and nothing else in the spec needs one.

---

## C. Recommended architecture: two tracks, one system

```
                     ┌──────────────────────────────────────────────────────┐
   Ali (phone/desk)  │ LAYER A  Claude Project "Executive Assistant"        │
   ──── natural ───▶ │   PROJECT_INSTRUCTIONS.md + 9 ea-* skills           │
        language     │   intent → skill → risk tier → act / card / refuse   │
                     └───────────────┬──────────────────────────────────────┘
                                     │ connector tool calls (per-user OAuth)
                     ┌───────────────▼──────────────────────────────────────┐
                     │ LAYER B  Official connectors                          │
                     │  Google Calendar · Google Drive · Gmail|Hostinger|M365 │
                     │  Zoho CRM · Zoom for Claude · (Slack) · Zapier        │
                     │                                                        │
                     │  TRACK 2 adds ONE more connector here:                 │
                     │  ▸ ea-core MCP server  (our own tool registry, policy  │
                     │    guard, approvals, audit — code-enforced)            │
                     └───────────────┬──────────────────────────────────────┘
                                     │
   ┌─────────────────────────────────▼─────────────────────┐  ┌────────────────────────────┐
   │ LAYER C  Always-on (TRACK 1, no hosting)              │  │ LAYER C+ (TRACK 2, hosted) │
   │  Routines / scheduled tasks, fresh session each run:  │  │  ea-core worker:           │
   │   10:00 briefing · hourly sweep 11–21 · 21:30 wrap     │  │   webhooks in (Hostinger,  │
   │  idempotent via 07-processed.md; hourly latency        │  │   Zoom, Zoho, Google push) │
   │                                                        │  │   queue, backoff, DLQ      │
   └─────────────────────────────────┬─────────────────────┘  │   fires a Routine or calls │
                                     │                        │   Claude Agent SDK         │
                     ┌───────────────▼──────────────────────┐ └──────────────┬─────────────┘
                     │ LAYER D  State                        │                │
                     │  TRACK 1: Drive folder "EA — Ali Rao"  │◀───────────────┘
                     │   config · prefs · VIPs · firm register│   TRACK 2 mirrors the same
                     │   commitments · approvals · rules      │   schema into Postgres and
                     │   processed IDs · audit/ · drafts/     │   keeps Drive as the human
                     │   meetings/ · briefings/               │   readable view
                     └────────────────────────────────────────┘
```

### Track 1 — Claude‑native (built; install and run first)
What exists in `claude/`. Zero hosting, per‑user OAuth, hourly background, human approval on every HIGH action. It is the CEO‑facing product regardless of Track 2. Install per `LAUNCH.md`.

### Track 2 — `ea-core` (proposed; build only after Track 1 is live and only if approved)
A small TypeScript service with three jobs, and no user interface of its own:

1. **Tool registry + policy guard, exposed as an MCP server.** Every EA tool declared once (Zod): name, description, input/output schema, risk tier, approval flag, reversibility, audit level, allowlist group. The Stravion policy pack (no dashes, no price in writing, one contact per firm, CC rule, disclosure limits) runs mechanically on every outbound body. The Claude Project calls this connector for *send‑class* actions, so a model slip cannot reach a counterparty. LOW‑risk reads keep using the official connectors directly.
2. **Event ingress.** Public HTTPS endpoint with HMAC verification, replay window and idempotency keys for Hostinger, Zoom (`meeting.ended`, `recording.transcript_completed`), Zoho notifications and Google Calendar push. Each verified event becomes a queued job; the handler either fires the relevant Routine early (`fire_trigger` with context) or runs the workflow via the Claude Agent SDK.
3. **Durable state and audit.** Postgres holds the same records the Drive templates define (`approvals`, `audit_log`, `commitments`, `firm_register`, `processed_events`, `memory_changes`). Drive stays the human‑readable mirror so Ali never needs a dashboard.

Automated tests (spec §21) live in Track 2: unit tests for registry, policy, tz and hours; integration tests against sandbox accounts with recorded HTTP fixtures; the 22 behavioural evals remain for the model layer.

**Why staged and not v1 all at once:** Track 1 delivers the CEO experience in days with no infrastructure. Track 2 is 4–6 weeks of engineering and needs hosting, service credentials and a public URL. Building it first delays the thing Ali will actually touch, and half of v1's scope (a web dashboard, its own MCP client, a notifications service) is made redundant by Claude's own app, connectors and push notifications.

---

## D. Technology stack

### Language for Track 2: **TypeScript** (Node 22)
- The workload is I/O orchestration over HTTP APIs; no numeric or ML work is done by us (Claude does the analysis).
- MCP's reference SDK is TypeScript‑first and `ea-core` *is* an MCP server.
- Zod gives one declaration per tool that yields validator, static type, JSON Schema for Claude and API contract, which is exactly spec §18.
- One language for server, MCP server and any future small approval page.
- Python would win only for transcript ML or dataframe work, which the spec does not contain.

| Concern | Track 1 | Track 2 |
|---|---|---|
| Reasoning | Claude in Project (model chosen by claude.ai) | Claude Agent SDK: `claude-opus-5` for judgement, `claude-sonnet-5` for classification/extraction |
| Skills / procedures | `claude/skills/ea-*` | unchanged; skills call `ea-core` tools for send‑class actions |
| Scheduling | Routines / scheduled tasks, cron in UTC | same, plus BullMQ delayed jobs for sub‑hour work |
| Queue | `07-processed.md` | BullMQ on Redis 7 (job id = idempotency key, exponential backoff, DLQ) |
| State | Drive folder (markdown) | Postgres 16 + Drizzle, Drive mirror |
| HTTP | none | Fastify (raw body for HMAC) |
| Secrets | none exist | env vars + cloud secret manager; `.env.example` only |
| Tests | 22 behavioural evals, `tests.json` | Vitest + Testcontainers + recorded fixtures; same `tests.json` |
| Deploy | claude.ai + Drive | Docker Compose on one VM with a public HTTPS name |

---

## E. Integration map

| Capability | Track 1 route | Track 2 addition | Event source | Blocker |
|---|---|---|---|---|
| Mail: Ali | Gmail / Hostinger / M365 connector, per `mail_provider` | Hostinger token or Google refresh token for webhooks | Hostinger webhook ✅ / Gmail push ✅ | which host serves `ar@alirao.com` |
| Mail: Sarah | Hostinger connector (connected) | same | webhook ✅ | none |
| Calendar | Google Calendar connector (connected) | Calendar push channel | push ✅ | offline refresh token |
| Documents, state, Meet transcripts | Google Drive connector (connected) | Drive API | none needed | none |
| CRM | Zoho CRM official connector | Zoho self‑client OAuth for notifications | Zoho Notifications ✅ | not connected; credentials |
| Meetings | Zoom for Claude connector | Zoom S2S OAuth app | `meeting.ended`, `recording.transcript_completed` ✅ | not connected; credentials; host must enable cloud recording + recap |
| Chat | Slack connector (later) | | | optional |
| LinkedIn | Zapier (publish only) | none | | LinkedIn ToS forbids automated outreach |
| WhatsApp | none official | Meta WABA (later) | webhook | business verification |
| Research | Apify, Vibe Prospecting (connected) | none | | none |

Official MCP/connector covers: Calendar, Drive, Gmail, Hostinger, M365, Zoho CRM, Zoom, Slack. Custom code is required only for: inbound webhooks, the policy guard, and WhatsApp.

---

## F. Security and permission model

Unchanged from v2 for Track 1: risk tiers LOW / MEDIUM / HIGH / PROHIBITED (`PERMISSIONS.md`), approval card with explicit "approve A‑n" in the same conversation, unattended runs can never execute HIGH, audit lines in `audit/`, roles Ali / Sarah / Admin via Drive sharing. Honest limits are in `SECURITY.md`.

Track 2 turns three of those from convention into code: policy pack at the tool boundary, append‑only `audit_log` table, tool allowlists with destructive tools excluded by default. Plus: HMAC + timestamp window + replay cache on every webhook, encrypted refresh tokens, separate dev/prod apps, RBAC roles `ceo` / `admin` / `service`, secret scanning in CI.

---

## G. Development phases (spec §22) — mapped to tracks

| # | Phase | Track 1 (Claude‑native) | Track 2 (`ea-core`) |
|---|---|---|---|
| 0 | Environment | done (§A) | done |
| 1 | Architecture | **this document, awaiting approval** | same |
| 2 | Repo structure | `claude/`, `evals/`, docs, done | `packages/ea-core/` skeleton, CI, lint |
| 3 | Configuration | `00-config.md`, done | Zod config, tz + hours, `.env.example` |
| 4 | Auth/security | connector OAuth, done | token vault, HMAC middleware, RBAC |
| 5 | Tool abstraction | `ea-operating-model`, done | registry + guard + policy pack, MCP server |
| 6 | Calendar | `ea-calendar`, done | push channel |
| 7 | Email | `ea-email`, done | Hostinger webhook, thread reconstruction |
| 8 | Zoom | `ea-meeting-followup`, done | S2S webhooks |
| 9 | Zoho | `ea-zoho-crm`, done | notifications |
| 10 | Meeting intelligence | skills, done | extraction eval set |
| 11 | Memory | `ea-memory`, done | Postgres mirror |
| 12 | Event engine | Routines + `07-processed.md`, done | queue, DLQ, replay |
| 13 | Briefing | task 01, done | early trigger on overnight CRITICAL |
| 14 | Approvals | card protocol, done | approval objects with expiry, code gate |
| 15 | Notifications | Routine push on completion, done | admin alert on repeated failure |
| 16 | Claude/mobile | it is Claude, done | `ea-core` as a Project connector |
| 17 | Security review | checklist open | threat model |
| 18 | Integration testing | evals T01–T22, **not run** | automated suite |
| 19 | Deployment | `LAUNCH.md` | Docker on VM |
| 20 | Monitoring | evening wrap + run history | health, DLQ watch, cost |

**Immediate next steps if approved:** install Track 1 (needs Ali's connectors, §H), run evals T01→T22 against real accounts, record in `tests.json`, then decide on Track 2 with data on how often the hourly latency actually hurt.

---

## H. What is needed from you

**Decision (blocks everything):**
1. **Track choice.** (a) Track 1 only; (b) Track 1 now, Track 2 after evals — *recommended*; (c) full v1 backend first.
2. **TypeScript for Track 2**, confirm or override. This is the one expensive‑to‑reverse choice.

**Blocks Track 1 install (no code, needs accounts):**
3. Claude plan: Team (recommended, shared Project and org skills) / Enterprise / Ali's own Pro or Max.
4. Where `ar@alirao.com` is hosted (Google Workspace, Hostinger, Microsoft 365). MX lookup is blocked from here.
5. Ali connects Google Drive, Google Calendar, his mail, Zoho CRM and Zoom for Claude in his own account (`LAUNCH.md` Part 2). Connectors sign in as him; nobody can do it for him.
6. The 10 to 20 VIP contacts for `02-vip-contacts.md`.
7. Background runner: claude.ai scheduled tasks in Ali's account (v2 plan) or Claude Code Routines like the three already running here. Routines are proven in this account; scheduled tasks keep everything in one place for Ali. Either works; say which.

**Blocks Track 2 only (do not send in chat; `.env.example` will name each):**
8. Hosting with a stable public HTTPS name (VPS, Fly.io, or cloud).
9. Hostinger API token for service use; Google OAuth client with offline refresh token; Zoom Server‑to‑Server OAuth app (Account ID, Client ID, Secret, Webhook Secret Token; scopes `meeting:read`, `recording:read`, `user:read`); Zoho self‑client OAuth (Client ID, Secret, data‑centre domain).

**Things that will not be built without an explicit instruction:** LinkedIn automation beyond the official API (ToS), browser automation as a stand‑in for a missing API, covert recording or transcription.

---

## I. Proposed repository structure

```
shaw/
├── README.md ARCHITECTURE.md LAUNCH.md SETUP.md SECURITY.md INTEGRATIONS.md
├── PERMISSIONS.md AUTOMATIONS.md TROUBLESHOOTING.md DEPLOYMENT.md TESTING.md CHANGELOG.md
├── progress.md  todo.md  tests.json
├── claude/                          # TRACK 1 (exists)
│   ├── PROJECT_INSTRUCTIONS.md
│   ├── skills/ea-*/SKILL.md         # 9 skills
│   ├── scheduled-tasks/             # 3 prompts + README with UTC crons
│   └── state-templates/             # Drive folder "EA — Ali Rao"
├── evals/scenarios/T01..T22.md      # behavioural tests (exists)
├── scripts/make-skill-zips.sh       # (exists)
├── docs/ARCHITECTURE-v1-backend.md  # (exists) full‑backend design, reference
│
└── packages/ea-core/                # TRACK 2 (proposed, empty until approved)
    ├── package.json tsconfig.json vitest.config.ts drizzle.config.ts
    ├── .env.example  Dockerfile  docker-compose.yml
    ├── src/
    │   ├── config/        # Zod env, timezone, operating hours
    │   ├── registry/      # tool.ts, guard.ts, risk.ts, allowlist.ts
    │   ├── policy/        # engine.ts, stravion.ts
    │   ├── mcp/           # ea-core MCP server (the connector Claude uses)
    │   ├── ingress/       # webhooks: hostinger, zoom, zoho, google; hmac, replay
    │   ├── events/        # queue, dedupe, dlq, handlers/
    │   ├── integrations/  # hostinger, google, zoom, zoho, base (retry, breaker)
    │   ├── approvals/  audit/  memory/  notifications/
    │   ├── agent/         # Agent SDK client, model routing
    │   └── worker/        # entrypoint, scheduler
    └── tests/ unit/ integration/ fixtures/
```

---

## Appendix — Session 1 inspection (2026‑09‑19)
Repo was empty. Host as in §A. Connectors verified live: Google Calendar (`aamirsawar123@gmail.com`, `Asia/Dubai`), Google Drive, Hostinger Mail (one mailbox `sarah@stravion.ae`, 300 req/window, webhooks present, no threads, no drafts), Zapier (LinkedIn only), Apify, Vibe Prospecting, Indeed. Not connected: Microsoft 365, Notion, ScrapeGraphAI, Zoom, Zoho, Slack. Directory search confirmed official Zoom, Zoho CRM, Gmail and Slack connectors exist. MX lookup for `alirao.com` blocked by egress policy.
