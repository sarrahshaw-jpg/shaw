# TODO

`[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked on you

## Phase 0–1 (this session)
- [x] Re‑inspect environment; record in ARCHITECTURE.md §A
- [x] Gap table: master spec vs v2 (ARCHITECTURE.md §B)
- [x] Reconciled architecture v3: Track 1 Claude‑native + Track 2 `ea-core` (§C)
- [x] Update todo / progress / tests.json / CHANGELOG
- [!] **Approve the track choice and TypeScript** (ARCHITECTURE.md §H 1–2). Nothing past Phase 1 starts before this.

## Track 1 — install (no code; needs accounts)
- [!] Choose plan: Team (recommended) / Enterprise / Ali's own account
- [!] Tell me where `ar@alirao.com` is hosted → sets `mail_provider`
- [!] Ali connects Drive, Calendar, mail, Zoho CRM, Zoom for Claude (LAUNCH.md Part 2)
- [!] VIP list for `02-vip-contacts.md`
- [!] Background runner: claude.ai scheduled tasks vs Claude Code Routines (§H 7)
- [ ] Create Project, paste instructions, upload 9 skill zips
- [ ] Create Drive folder `EA — Ali Rao` from templates (does not exist yet, verified)
- [ ] Seed firm register from both Sent folders
- [ ] Create the 3 background runs with push notifications on
- [ ] Run evals T01→T22 against real accounts; record in tests.json
- [ ] Phase 17 checklist in SECURITY.md

## Track 2 — `ea-core` (only after approval and Track 1 evals)
- [ ] Phase 2: `packages/ea-core` skeleton, CI, lint, typecheck
- [ ] Phase 3: Zod config, tz + hours, `.env.example`
- [ ] Phase 4: token vault, HMAC middleware, RBAC
- [ ] Phase 5: tool registry + policy guard + MCP server; unit tests
- [ ] Phase 7/8/9: Hostinger, Zoom, Zoho webhooks (blocked on credentials + hosting)
- [ ] Phase 12: BullMQ queue, idempotency, DLQ, replay
- [ ] Phase 18: automated suite green in tests.json
- [ ] Phase 19: Docker on VM with public HTTPS name

## Later
- [ ] Slack connector and rule M‑4 for internal chasing
- [ ] WhatsApp when an official connector or WABA credentials exist
- [ ] Propose automation rules after three identical approvals (ea-memory)
