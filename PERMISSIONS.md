# PERMISSIONS

Risk tier per action. The authoritative text is `claude/skills/ea-operating-model/SKILL.md`; this is the quick table.

| Action | Tier | Unattended run | Chat |
|---|---|---|---|
| Read mail, calendar, CRM, Drive, Zoom assets | LOW | yes | yes |
| Summarize, classify, triage | LOW | yes | yes |
| Write prep pack, meeting note, briefing, draft | LOW | yes | yes |
| Append audit, processed IDs, approval cards | LOW | yes | yes |
| Add/update commitment line | MEDIUM (M‑1) | yes | yes |
| Add CRM note (no terms) | MEDIUM (M‑2) | yes | yes |
| Create internal‑only event | MEDIUM (M‑3) | no (needs Ali's ask) | yes |
| Move/label mail | MEDIUM | if ruled | ask |
| Update preferences / VIPs | MEDIUM, always confirmed | no | after yes |
| Send / reply / forward email | HIGH | never | card + approve |
| Create/move/cancel event with external attendee | HIGH | never | card + approve |
| Change CRM deal stage, amount, owner, contact/account fields | HIGH | never | card + approve |
| Share a Drive file externally | HIGH | never | card + approve |
| Message on Slack/WhatsApp/LinkedIn externally | HIGH | never | card + approve |
| Payments, transfers, contracts, legal/pricing in writing | PROHIBITED | never | refused |
| Delete mail, folders, files, CRM records, events (except an approved cancel) | PROHIBITED | never | refused |
| Enable recording, change permissions | PROHIBITED | never | refused |

Roles: **Ali** approves anything. **Sarah** may approve MEDIUM and request drafts; may not approve HIGH in Ali's name. **Admin** edits `00-config.md` and `06-automation-rules.md`.
