# Progress Log

Append-only. Newest entry at the top. Keeps project state across Claude Code sessions.

---

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
