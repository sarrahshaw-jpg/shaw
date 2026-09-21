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
- [x] Host of `ar@alirao.com`: **Hostinger** (your decision, 2026-09-21)
- [x] Calendar: **Ali connects his own**; `aamirsawar123@gmail.com` is not used (your decision, 2026-09-21)
- [!] Ali connects Drive, Calendar, mail, Zoho CRM, Zoom for Claude (LAUNCH.md Part 2)
- [x] Hostinger draft strategy: draft kept, read aloud on request, sent on "send it", otherwise he sends it himself (your decision, 2026-09-21)
- [!] VIP list for `02-vip-contacts.md` (10 to 20 names, firm, why they matter)
- [!] Background runner and plan: assuming claude.ai scheduled tasks on Team until you say otherwise
- [ ] Create Project, paste instructions, upload 9 skill zips
- [x] Create Drive folder `EA — Ali Rao` from templates (done 2026-09-21, folder id `10QygQqVM3FkQ7M0jhVwO9EHkQevcXI-A` in the admin Drive `titanarshian@gmail.com`; 9 files, subfolders audit/drafts/meetings/briefings)
- [!] Share that folder with Ali as Editor once his address is confirmed; keep link sharing off
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
