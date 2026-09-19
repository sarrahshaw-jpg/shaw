# CEO AI Executive Assistant — Architecture (v2, Claude‑native)

**Principal:** Ali Rao, CEO, Stravion Investments (Titans Real Estate LLC), Dubai
**Delegate:** Sarah Shaw, Director of Sales & Strategy
**Runs in:** Claude (Project + Skills + Scheduled tasks + Connectors). Nothing to host.
**Timezone:** `Asia/Dubai`, set once in `state/00-config.md`. **Hours:** 10:00–22:00, configurable.
**Status:** built as a package; not yet installed in Ali's account. Follow `SETUP.md`.

## Why this shape

You asked for it to live inside Claude so nobody needs a separate tool, and so Ali can be handed it. The first proposal (a TypeScript backend) assumed Zoom and Zoho had no Claude connectors. They do: the claude.ai directory has official **Zoom for Claude**, **Zoho CRM**, **Gmail**, **Slack** connectors alongside the already‑connected **Google Calendar**, **Google Drive** and **Hostinger Mail**. With those plus Claude's **scheduled tasks** for the always‑on part and a **Google Drive folder** for persistent state, every layer of the spec maps onto Claude itself.

## The four layers, in Claude

```
LAYER A  Reasoning        Claude, in a Project whose custom instructions are claude/PROJECT_INSTRUCTIONS.md
                          + 9 skills (claude/skills/ea-*) that hold the procedures
                                     │
LAYER B  Tools            Official connectors, each user's own OAuth:
                          Google Drive · Google Calendar · Gmail | Hostinger | M365 · Zoho CRM · Zoom · (Slack)
                                     │
LAYER C  Always-on        3 scheduled tasks in Ali's account, fresh session each run, same connectors:
                          10:00 briefing · hourly sweep 11:00–21:00 · 21:30 wrap   (claude/scheduled-tasks/)
                                     │
LAYER D  State            Google Drive folder "EA — Ali Rao"  (claude/state-templates/)
                          config · preferences · VIPs · firm register · commitments · approvals · rules
                          processed IDs · audit/ · drafts/ · meetings/ · briefings/
```

Both entry paths, a live chat and a scheduled run, load the same instructions and skills, read the same state, and log to the same audit file. The only difference: a scheduled run can never execute a HIGH‑risk action.

## How a request flows

1. Ali types naturally in the Project (mobile or desktop). Instructions map intent to a skill.
2. The skill reads state from Drive first, then calls connectors.
3. The action is classified LOW / MEDIUM / HIGH / PROHIBITED (`ea-operating-model`).
4. LOW executes. MEDIUM executes if `06-automation-rules.md` allows. HIGH produces an approval card and stops until "approve A‑n" in the same conversation. PROHIBITED is refused.
5. Outcome is reported as `SUCCESS` / `PARTIAL SUCCESS` / `FAILED` / `WAITING FOR APPROVAL`, and an audit line is appended.

## How the background works

Each scheduled task starts a fresh session, reads `07-processed.md`, handles only new items, appends their IDs, queues approval cards into `05-approvals.md`, and ends with a message that becomes the task's push/email notification. Latency is up to one hour; that is the deliberate trade for having no infrastructure. Outside 10:00–22:00 nothing runs, which is how quiet hours are enforced.

## Integration map

| Capability | Connector | State |
|---|---|---|
| Mail (Ali) | Gmail, Hostinger Mail or Microsoft 365, whichever hosts `ar@alirao.com` | to connect; set `mail_provider` |
| Mail (Sarah) | Hostinger Mail `sarah@stravion.ae` | connected |
| Calendar | Google Calendar | connected (`Asia/Dubai`) |
| Documents, state, Meet transcripts | Google Drive | connected |
| CRM | Zoho CRM (official, all modules) | to connect |
| Meetings | Zoom for Claude (search, recap, transcript); Google Meet via Drive transcripts | to connect |
| Chat | Slack (optional) | later |
| LinkedIn | Zapier, publish only | limited by LinkedIn's API |
| WhatsApp | no official connector found | deferred |

Details and caveats in `INTEGRATIONS.md`. The two that matter: Hostinger has no thread or drafts endpoints (the email skill compensates), and Zoom only exposes recordings the host made with cloud recording and recap enabled.

## Security and permissions

Risk tiers, approval card, audit format and the firm‑wide rules (price never in writing, one contact per firm, no shareholding, asset detail limits, no dashes, "Warm regards," terminal) are in `PROJECT_INSTRUCTIONS.md` and `ea-operating-model`. Summary tables in `PERMISSIONS.md`; controls and honest limits in `SECURITY.md`. The important limit: policy is enforced by the model and by a human approval step, not by code. The audit log makes any slip visible the same day.

## Sharing with Ali

Claude **Team** is the right plan for two or three people: shared Project, org‑provisioned skills, admin‑controlled connectors; each person still connects their own Google, mail, Zoho and Zoom. **Enterprise** adds SSO, admin audit logs and a compliance API if governance demands them. If Ali wants it today on his own account, `SETUP.md` works as‑is on Pro/Max and upgrades in place.

## Phases (spec §22) — where each one landed

| Phase | Where it lives |
|---|---|
| 0 Environment | this file §Why, `progress.md` |
| 1 Architecture | this file |
| 2 Repo structure | `claude/`, `evals/`, `scripts/`, docs |
| 3 Configuration | `state-templates/00-config.md` |
| 4 Auth/security | connectors' OAuth; `SECURITY.md` |
| 5 Tool abstraction | `ea-operating-model` (tiers, guard, audit) |
| 6 Calendar | `ea-calendar` |
| 7 Email | `ea-email` |
| 8 Zoom | `ea-meeting-followup`, `ea-meeting-prep` |
| 9 Zoho | `ea-zoho-crm` |
| 10 Meeting intelligence | `ea-meeting-prep`, `ea-meeting-followup` |
| 11 Memory | `ea-memory`, state files |
| 12 Event engine | `scheduled-tasks/`, `07-processed.md`, `AUTOMATIONS.md` |
| 13 Briefing | `ea-morning-briefing`, task 01 |
| 14 Approvals | `ea-operating-model` card protocol, `05-approvals.md` |
| 15 Notifications | priority in instructions; task completion notifications |
| 16 Claude/mobile | it *is* Claude; nothing extra |
| 17 Security review | `SECURITY.md` checklist, open |
| 18 Integration testing | `evals/`, `tests.json`, open |
| 19 Deployment | `SETUP.md`, `DEPLOYMENT.md` |
| 20 Monitoring | evening wrap + audit + task run history |

## Appendix A — Environment inspection (2026‑09‑19)

Repo was empty. Host: Ubuntu 24.04, Node 22, Python 3.11, Postgres 16 and Redis 7 clients, Docker. Connectors verified live: Google Calendar (`aamirsawar123@gmail.com`, `Asia/Dubai`), Google Drive, Hostinger Mail (one mailbox `sarah@stravion.ae`, 300 req/window, webhooks present, no threads, no drafts), Zapier (LinkedIn only), Apify, Vibe Prospecting, Indeed. Not connected: Microsoft 365, Notion, ScrapeGraphAI, Zoom, Zoho, Slack. Directory search confirmed official Zoom, Zoho CRM, Gmail and Slack connectors exist. MX lookup for `alirao.com` was blocked by egress policy, so Ali's mail host is unconfirmed.

## Appendix B — When to build a backend instead

Do this only if one of these becomes true: reaction must be faster than the hourly sweep; a rule must be enforced in code rather than by the model plus human approval; or a non‑Claude interface (WhatsApp bot, web dashboard) is required. The original v1 design for that case is kept in `docs/ARCHITECTURE-v1-backend.md`: TypeScript, Fastify webhooks, BullMQ, Postgres, the same tool registry and the same state schema. Every skill, rule and state file here would carry over unchanged.
