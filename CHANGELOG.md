# CHANGELOG

## 0.6.0 — 2026-09-21
- Added the `executive-assistant` entry skill so the assistant triggers on plain language anywhere in Ali's Claude, not only inside a Project. Ten skill zips now build.
- LAUNCH.md rewritten as the one-agent, always-on install path, with the three real limits stated.

## 0.5.0 — 2026-09-21
- ARCHITECTURE.md v4 in the A–F shape: three shapes judged on six criteria, unmet requirements named, per‑integration auth and event sources, hosting, credential field names. v3 archived to `docs/ARCHITECTURE-v3-two-track.md`.
- Added `docs/MASTER_BUILD_SPEC.md` (spec of record) and `CLAUDE.md` (repo working rules, gate state).
- tests.json v4: C11, C12 planned.

## 0.4.0 — 2026-09-19
- ARCHITECTURE.md rewritten as v3: master spec reconciled against v2 line by line (§B); two‑track design, Track 1 Claude‑native (built) + Track 2 `ea-core` TypeScript service (proposed) for code‑enforced policy, webhooks and automated tests.
- Environment re‑inspected: Claude Code Routines verified as a working always‑on mechanism in this account; no Drive state folder yet; Zoom/Zoho still unconnected.
- tests.json v3: C01–C10 planned automated tests for Track 2 alongside T01–T22.


## 0.3.0 — 2026-09-19
- LAUNCH.md: computer + phone launch path for Ali, admin part for Sarah.
- Phone‑first output rules, tool‑call budget, hot cache in `00-config.md` refreshed by the evening wrap, numbered one‑tap approvals, dictation tolerance, learning loop.

## 0.2.0 — 2026-09-19
- Redesigned as Claude‑native: Project instructions + 9 skills + 3 scheduled tasks + Drive state folder. No backend.
- Principal set to Ali Rao; Sarah Shaw as delegate.
- Verified official connectors exist for Zoom, Zoho CRM, Gmail, Slack.
- Added SETUP, SECURITY, PERMISSIONS, INTEGRATIONS, AUTOMATIONS, TESTING, TROUBLESHOOTING, DEPLOYMENT, 22 eval scenarios.

## 0.1.0 — 2026-09-19
- Phase 0 inspection and custom‑backend architecture proposal (now Appendix B).
