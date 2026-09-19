# Executive Assistant for Ali Rao — built inside Claude

An AI executive assistant for the CEO of Stravion Investments (Dubai) that runs entirely in Claude: a Project with custom instructions, nine skills, three scheduled tasks, official connectors (Google Calendar, Drive, mail, Zoho CRM, Zoom), and a Google Drive folder as its memory, approval queue and audit log. Nothing to host.

**Launch:** [LAUNCH.md](LAUNCH.md) — admin setup on a computer (30 min), Ali connects his tools (5 min), then it lives in his phone app. Detailed reference in [SETUP.md](SETUP.md).

| | |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | v3: spec‑vs‑v2 gap table, Track 1 (Claude‑native, built) + Track 2 (`ea-core`, proposed), stack, integration map, phases, what is needed. **Awaiting approval.** |
| [claude/PROJECT_INSTRUCTIONS.md](claude/PROJECT_INSTRUCTIONS.md) | the assistant's brain; paste into the Project |
| [claude/skills/](claude/skills/) | `ea-operating-model`, `ea-email`, `ea-calendar`, `ea-meeting-prep`, `ea-meeting-followup`, `ea-zoho-crm`, `ea-morning-briefing`, `ea-memory`, `ea-commitments` |
| [claude/scheduled-tasks/](claude/scheduled-tasks/) | 10:00 briefing, hourly sweep, 21:30 wrap |
| [claude/state-templates/](claude/state-templates/) | the Drive folder `EA — Ali Rao` |
| [PERMISSIONS.md](PERMISSIONS.md) · [SECURITY.md](SECURITY.md) | risk tiers, approval protocol, controls and limits |
| [INTEGRATIONS.md](INTEGRATIONS.md) · [AUTOMATIONS.md](AUTOMATIONS.md) | connectors and triggers |
| [TESTING.md](TESTING.md) · [evals/](evals/) · [tests.json](tests.json) | 22 behavioural scenarios |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) · [DEPLOYMENT.md](DEPLOYMENT.md) · [CHANGELOG.md](CHANGELOG.md) | |
| [todo.md](todo.md) · [progress.md](progress.md) | project state across sessions |

The one rule: it never sends, changes a meeting with outsiders, or writes to a CRM deal without an approval card and an explicit "approve" in the same conversation. Scheduled runs never execute such actions at all.
