# Scheduled tasks (the always-on layer)

These three prompts are the assistant's background heartbeat. They run as Claude **scheduled tasks** in Ali's account, each in a fresh session that has this Project's instructions, the `ea-*` skills and the connectors listed. No server, no webhooks, nothing to host.

| # | Task | Dubai time | Cron (UTC, Dubai is UTC+4 with no DST) | Connectors |
|---|---|---|---|---|
| 1 | Morning briefing | 10:00 daily | `0 6 * * *` | Google Calendar, mail, Google Drive, Zoho CRM, Zoom |
| 2 | Working-hours sweep | hourly 11:00 to 21:00 | `0 7-17 * * *` | same |
| 3 | Evening wrap | 21:30 daily | `30 17 * * *` | same |

If `state/00-config.md` changes the timezone or hours, recompute the cron. Do not hard-code Dubai anywhere except here.

## Creating them

In claude.ai: Scheduled tasks (or Routines, depending on your client) → New → paste the prompt from the matching file → set the schedule above → enable the connectors → turn on push and email notification on completion. In Claude Code / Cowork: the same via the `create_trigger` tool with `create_new_session_on_fire: true` and `connectors` set.

Each prompt is self-contained because the fired session starts from nothing. It must name the Drive state folder and load `ea-operating-model` first.

## What the background layer honestly can and cannot do

- **Can**: catch every new email, calendar change, ended Zoom meeting and CRM change within an hour during operating hours; prepare packs and drafts; queue approval cards; deliver the briefing at 10:00; suppress everything but CRITICAL outside hours (by simply not running).
- **Cannot**: react within seconds. A meeting that ends at 14:05 is processed at 15:00. If minute-level reaction ever matters, that is the point to add the custom backend described in `ARCHITECTURE.md` Appendix B; nothing in these prompts would change.
- **Never**: execute a HIGH-risk action. Unattended runs prepare and queue; Ali approves in a conversation.

## Idempotency

Every run reads `state/07-processed.md` first and appends to it after handling an item. Two runs overlapping (a slow run plus the next hour's) can therefore still double-process an item; a duplicate approval card is the worst case, and a duplicate send is impossible because unattended runs never send.
