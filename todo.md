# TODO — CEO AI Executive Assistant

Persistent task state across Claude Code sessions. Update before and after every work block.

Legend: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked

---

## Phase 0 — Environment inspection
- [x] Inspect host runtimes, resources, git state
- [x] Inspect egress/proxy posture
- [x] Enumerate MCP connectors and their real connection state
- [x] Verify Hostinger Mail (mailbox discovery, operation list, rate limit)
- [x] Verify Google Calendar (calendars, timezone)
- [x] Probe Zapier catalog for Zoom and Zoho
- [x] Discover existing business rules (stravion-outreach skill)

## Phase 1 — Architecture
- [x] Choose language and justify (TypeScript)
- [x] Design four-layer architecture
- [x] Build integration map with honest gaps
- [x] Define risk/permission model
- [x] Define Stravion policy pack as enforced rules
- [x] Propose repository structure
- [x] Write ARCHITECTURE.md, todo.md, progress.md, tests.json
- [!] **AWAITING APPROVAL — do not start Phase 2**

---

## Blocked — need input (see ARCHITECTURE.md §F)
- [!] #1 Confirm TypeScript
- [!] #2 Hosting + stable public HTTPS URL for webhooks
- [!] #3 Identity: which of the three accounts is the principal?
- [!] #4 Zoom in scope? S2S OAuth credentials
- [!] #5 Zoho in scope? region + self-client OAuth + is it populated?
- [!] #6 Draft strategy: IMAP APPEND vs DB-held drafts
- [!] #7 Approval notification channel

---

## Phase 2 — Repository structure (not started)
- [ ] package.json, tsconfig strict, eslint, prettier
- [ ] Directory skeleton per ARCHITECTURE.md
- [ ] docker-compose (postgres 16 + pgvector, redis 7)
- [ ] CI: typecheck, lint, test, secret scan
- [ ] Remaining doc set (SETUP, SECURITY, INTEGRATIONS, PERMISSIONS, AUTOMATIONS, TROUBLESHOOTING, DEPLOYMENT, TESTING, CHANGELOG)

## Phase 3 — Config
- [ ] Zod-validated env loader, fail fast on missing
- [ ] Timezone module (Luxon), no hard-coded tz anywhere
- [ ] Operating hours + quiet hours, configurable
- [ ] .env.example covering every integration

## Phase 4 — Auth & security
- [ ] Encrypted token vault (AES-256-GCM)
- [ ] Google OAuth offline flow + refresh rotation
- [ ] Webhook HMAC middleware (raw body, timestamp window, replay cache)
- [ ] RBAC: ceo / admin / service

## Phase 5 — Tool registry
- [ ] Tool descriptor type (name, schemas, risk, approval, reversible, audit, rateLimit)
- [ ] Guard: validate → risk → policy → approval → execute → audit
- [ ] Allowlist groups; destructive tools off by default
- [ ] Policy engine + Stravion rule pack

## Phase 6 — Calendar
- [ ] Adapter (read, availability, create, update, cancel)
- [ ] Conflict + double-booking detection
- [ ] Scheduling preferences (30-min default, buffers, focus time) — configurable
- [ ] Watch channels or incremental sync for CALENDAR_CHANGED

## Phase 7 — Email
- [ ] Hostinger client + token-bucket rate limiter (300/window)
- [ ] Incremental sync, message store
- [ ] Thread reconstruction from Message-ID / In-Reply-To / References
- [ ] Priority + VIP classification
- [ ] Unanswered-message detection
- [ ] Draft creation per decision #6
- [ ] Webhook registration + NEW_EMAIL event
- [ ] Send path behind HIGH-risk approval

## Phase 8 — Zoom  [blocked: #4]
## Phase 9 — Zoho  [blocked: #5]

## Phase 10 — Meeting intelligence
- [ ] Transcript ingestion, source-agnostic (Zoom or Meet)
- [ ] Extract decisions, action items, owners, deadlines, commitments
- [ ] Meeting prep pack builder (no fabrication — cite or omit)
- [ ] Follow-up draft generation

## Phase 11 — Memory
- [ ] Preferences, VIP contacts, firm register (one-contact-per-firm)
- [ ] Semantic recall over meetings/emails (pgvector)
- [ ] No silent permanent writes; every memory change logged

## Phase 12 — Event engine
- [ ] Event taxonomy per spec §19
- [ ] BullMQ queues, deterministic job IDs for idempotency
- [ ] Exponential backoff, DLQ, replay
- [ ] Outcome states: SUCCESS / PARTIAL / FAILED / WAITING_APPROVAL

## Phase 13 — Morning briefing
- [ ] 10:00 Asia/Dubai scheduled workflow, 10 sections, concise format

## Phase 14 — Approvals
- [ ] Approval object + lifecycle + expiry
- [ ] Approval UI
- [ ] Auto-send rules engine (opt-in categories only)

## Phase 15 — Notifications
- [ ] CRITICAL / HIGH / NORMAL / LOW classifier
- [ ] Quiet hours outside 10:00–22:00, critical-only override

## Phase 16 — Claude / mobile interface
- [ ] ea-mcp-server exposing EA tools
- [ ] Natural-language command coverage for spec §4 examples

## Phases 17–20 — Security review, integration testing, deployment, monitoring
- [ ] Threat model + scope audit
- [ ] Sandbox integration suite (never against production data)
- [ ] Docker deploy, migrations, backups, runbook
- [ ] Health, alerting, DLQ watch, LLM cost tracking
