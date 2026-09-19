# DEPLOYMENT

There is nothing to deploy. "Deployment" is SETUP.md steps 1–6 performed in Ali's Claude account (or the Team org), plus the Drive folder. Rollback is: disable the three scheduled tasks and remove the Project's connectors. Upgrade is: replace skill zips and re‑paste PROJECT_INSTRUCTIONS.md; state in Drive is untouched.

Monitoring (Phase 20): the evening wrap reports what ran and what failed; scheduled‑task run history in claude.ai shows failures; `audit/` shows every consequential action. Review weekly for the first month.

If the design ever needs a real backend (sub‑minute reaction, code‑enforced policy, or a non‑Claude interface), see ARCHITECTURE.md Appendix B; all skills, state files and rules carry over unchanged.
