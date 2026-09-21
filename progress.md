# Progress Log

Append-only. Newest entry at the top. Keeps project state across Claude Code sessions.

---

## 2026-09-21 — Session 3, part 2 — decisions recorded, Drive state folder created

**Your decisions:** Ali connects his own Google Calendar; his mail is Hostinger; drafts stay as drafts, are read aloud when he asks, go out when he says "send it", and otherwise wait for him to send with one tap.

**Done**
- Recorded in `00-config.md` (`mail_provider`, `calendar`, new `draft_flow` row), the `ea-email` skill (a Draft flow section with the three exits), `SETUP.md` and `ARCHITECTURE.md` §G decision log.
- Created the Drive state folder **`EA — Ali Rao`** (id `10QygQqVM3FkQ7M0jhVwO9EHkQevcXI-A`) in the admin Drive: README, 00-config, 01-preferences, 02-vip-contacts, 03-firm-register, 04-commitments, 05-approvals, 06-automation-rules, 07-processed, and subfolders `audit/` (with `2026-09.md`), `drafts/`, `meetings/`, `briefings/`. Verified by listing the folder.

**Verified, not assumed:** all 13 items listed back from Drive after upload.

**Honest limit found:** the Hostinger API has no draft endpoint, so a draft cannot be placed in Ali's mail-app Drafts folder. "One tap" means tapping 1 on the card in Claude. A draft visible in his mail app needs IMAP credentials, noted as a Track 2 item and not built.

**Not done:** Project and skills not installed (needs Ali's account); folder not yet shared with Ali (address to confirm); no scheduled tasks; evals not run.

**Blocked on:** VIP list; Claude plan and runner choice; Ali connecting his five connectors.

**Next:** on Ali's account, install skills and Project, share the folder, then run T01.

## 2026-09-21 — Session 3 — Condensed prompt; architecture v4

**Input:** the self‑contained "Claude‑ready" prompt for the same project, asking for Phases 0–1 in a fixed A–F shape and a stop.

**Verified by direct call**
- Host, Calendar (`aamirsawar123@gmail.com`, Asia/Dubai), Drive (no `EA — Ali Rao` folder), Hostinger (`sarah@stravion.ae`, 300/window), Zapier (LinkedIn only): unchanged since 19 Sep. Zoom, Zoho, Gmail, M365, Slack still not connected in this session.
- `CLAUDE.md` and `docs/MASTER_BUILD_SPEC.md` did not exist; created.

**Done**
- ARCHITECTURE.md v4: Options 1/2/3 judged on the six criteria; Option 3 hybrid staged recommended; every unmet spec requirement named with trade‑off; continuous vs Claude‑direct; integration classification with auth per system; hosting requirements; credential field names with console paths; phases with gates; repo structure. v3 moved to `docs/ARCHITECTURE-v3-two-track.md`.
- tests.json v4 (C11 firm register, C12 memory write), todo, CHANGELOG 0.5.0, README.

**Not done, deliberately:** no application code, no scaffolding, no dependencies.

**Blocked on:** written approval and decisions §G 1–7.

**Next on approval:** Track 1 install with Ali's connectors → T01–T22 → Phase 2 `packages/ea-core` skeleton.

## 2026-09-19 — Session 2 — Master spec re‑issued; architecture v3

**Input:** the full master build specification, re‑sent, asking for Phase 0–1 and a stop for approval.

**Verified by direct call**
- Host unchanged (Ubuntu 24.04, Node 22.22, Python 3.11.15, Docker 29.3, Postgres 16 / Redis 7 clients). No public inbound URL.
- Google Calendar (`aamirsawar123@gmail.com`, Asia/Dubai), Google Drive, Hostinger Mail (`sarah@stravion.ae`, 300 req/window), Zapier (LinkedIn only), Apify, Vibe Prospecting, Indeed: connected. Zoom, Zoho CRM, Gmail, M365, Slack: not connected.
- Drive has **no** `EA — Ali Rao` folder; Track 1 was never installed.
- **New:** this account runs three Claude Code Routines daily (LinkedIn prep ×2, DMC reply watch) with Drive/Hostinger/Calendar/Zapier connectors, push notifications, run history; one run failed on 18 Sep. Proven Layer C at hourly granularity.

**Done**
- ARCHITECTURE.md v3: gap table spec vs v2; two‑track design; stack (TypeScript for Track 2, reasons); integration map; security model; phases per track; repo structure; needs list.
- todo.md, tests.json (v3, C01–C10 planned), CHANGELOG 0.4.0, README, AUTOMATIONS updated.

**Decisions taken:** none that are architectural. Recommendation only: Track 1 now, Track 2 after evals, TypeScript.

**Not done, deliberately:** no application code (spec §26).

**Blocked on:** ARCHITECTURE.md §H items 1–7.

## 2026-09-19 — Session 1, part 3 — launch path and phone efficiency

Added LAUNCH.md (admin on computer, Ali connects tools, then phone app). Made the agent phone‑first: under 8 lines, one item per line, `1 approve · 2 edit · 3 drop` cards, dictation tolerance. Efficiency: single `00-config.md` read with a hot cache refreshed nightly, parallel lookups, no re‑reads, one‑call answers for the common questions. Pushed after GitHub access was granted.

## 2026-09-19 — Session 1, part 2 — Claude‑native redesign (v2)

**Direction from you:** everything inside Claude, no separate tool; principal is Ali Rao; shareable with him (Team/Enterprise); Zoom sometimes; Zoho all modules, UAE; email per my recommendation.

**Verified**
- claude.ai directory has official connectors for Zoom ("Zoom for Claude": search, recordings, meeting assets), Zoho CRM (41 tools), Gmail, Slack. Zoho docs list no UAE‑specific data centre; the connector routes by account so it does not matter.
- MX lookup for alirao.com blocked by egress policy; Ali's mail host unconfirmed. Package supports Gmail / Hostinger / M365.

**Built:** `claude/PROJECT_INSTRUCTIONS.md`; skills ea-operating-model, ea-email, ea-calendar, ea-meeting-prep, ea-meeting-followup, ea-zoho-crm, ea-morning-briefing, ea-memory, ea-commitments; three scheduled‑task prompts with UTC crons; Drive state templates; full doc set; 22 eval scenarios; zip script. v1 backend design moved to `docs/ARCHITECTURE-v1-backend.md` as Appendix B.

**Not done:** installation in Ali's account (needs his connectors); evals not run (no target account yet); push blocked by GitHub App access (403).

## 2026-09-19 — Session 1 — Phases 0 and 1

**Done**
- Phase 0 environment inspection, complete. Findings in `ARCHITECTURE.md` §0.
- Phase 1 architecture proposal, complete. Awaiting approval.
- Created `ARCHITECTURE.md`, `todo.md`, `progress.md`, `tests.json`, `.gitignore`, `.env.example`, `README.md`.

**Verified by direct call, not assumed**
- Repo `sarrahshaw-jpg/shaw` is empty, zero commits, branch unborn.
- Node 22.22.2, Python 3.11.15, Postgres 16 client, Redis 7 client, Docker 29.3.1.
- Hostinger Mail connected. One mailbox: `sarah@stravion.ae` (`AC17d75d6399ce66bff0357b5c5ef8`). Rate limit 300/window. Webhook endpoints present. No thread model. No draft-create endpoint.
- Google Calendar connected as `aamirsawar123@gmail.com`, timezone already `Asia/Dubai`.
- Google Drive, Apify, Vibe Prospecting, Indeed connected.
- Zapier connected but only LinkedIn enabled (4 actions).
- Microsoft 365 and Notion `connect_incomplete`; ScrapeGraphAI `needs_reconnect`.
- Zoom and Zoho CRM: **not connected**. Present in Zapier catalog only; Zoho CRM is Premium tier.

**Three findings that shaped the design**
1. Email is Hostinger, not Gmail/Outlook. It has webhooks (good) but no threads and no drafts endpoint (work to do).
2. The MCP connectors are session-scoped and cannot serve an always-on backend. The backend must hold its own credentials. This is the difference between the spec's requirement and a demo.
3. The `stravion-outreach` skill already encodes the operating policy in prose. It should become an enforced policy pack in code, not a prompt instruction.

**Decisions taken**
- Recommend TypeScript over Python. Rationale in `ARCHITECTURE.md` §B.
- Recommend direct Zoom/Zoho APIs over Zapier, because the event engine needs inbound webhooks.
- Business rules move from prompt to a mechanical policy engine at the tool boundary.

**Not done, deliberately**
- No application code. Spec §26 says stop at architecture and wait for approval.

**Blocked on**
- Seven decisions in `ARCHITECTURE.md` §F, chiefly hosting (#2), principal identity (#3), and whether Zoom (#4) and Zoho (#5) are genuinely in scope.

**Next**
- On approval: Phase 2 repository skeleton, then Phase 3 config, then Phase 5 tool registry before any integration.
