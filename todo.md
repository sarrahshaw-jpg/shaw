# TODO

`[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked on you

## Phase 0–1 (2026‑09‑21)
- [x] Re‑inspect environment (unchanged since 19 Sep; recorded in ARCHITECTURE.md §0)
- [x] Create `docs/MASTER_BUILD_SPEC.md` (spec of record) and `CLAUDE.md` (working rules)
- [x] ARCHITECTURE.md v4: options judged on six criteria, unmet requirements named, per‑integration auth, hosting, credential fields; v3 moved to `docs/`
- [x] tests.json v4 (C11, C12 added), progress, changelog, README
- [!] **Written "approved"** with choices for ARCHITECTURE.md §G 1–7. No code before this.

## Track 1 — install (no code; needs accounts)
- [!] Plan for Ali (Team / Enterprise / own)
- [!] Host of `ar@alirao.com`
- [!] Whose calendar is `aamirsawar123@gmail.com`
- [!] Ali connects Drive, Calendar, mail, Zoho CRM, Zoom for Claude (LAUNCH.md Part 2)
- [!] VIP list; background runner choice; Hostinger draft strategy
- [ ] Create Project, paste instructions, upload 9 skill zips
- [ ] Create Drive folder `EA — Ali Rao` from templates
- [ ] Seed firm register from Sent folders
- [ ] Create the 3 background runs, notifications on
- [ ] Run T01→T22 on real accounts; record in tests.json
- [ ] Phase 17 checklist in SECURITY.md

## Track 2 — `packages/ea-core` (after approval and Track 1 evals)
- [ ] Phase 2 skeleton, CI, lint, typecheck
- [ ] Phase 3 config + `.env.example` (C01)
- [ ] Phase 4 token vault, HMAC, RBAC (C06)
- [ ] Phase 5 registry, guard, policy pack, MCP server (C02–C05, C11, C12)
- [ ] Phases 6–9 adapters + webhooks (blocked on credentials and hosting)
- [ ] Phase 12 queue, dedupe, DLQ, replay (C07, C08)
- [ ] Phase 14–15 approvals, admin alerts
- [ ] Phase 18–20 suite green, Docker on VM, monitoring

## Later
- [ ] Slack connector and internal chasing rule
- [ ] WhatsApp via Meta Cloud API when business verification exists
- [ ] Propose automation rules after three identical approvals
