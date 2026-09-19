---
name: ea-morning-briefing
description: "The daily executive briefing for Ali Rao at 10:00 Asia/Dubai (or on demand): schedule, important meetings, prep needs, unanswered and incoming important email, decisions pending, outstanding commitments, CRM activity, follow-ups due, conflicts. Concise, fixed format. Use for 'morning briefing', 'what's my day', 'summarize yesterday', or the scheduled 10:00 run."
---

# Morning briefing

Load `ea-operating-model` first. LOW risk. Runs unattended at the time in `00-config.md` (default 10:00 Dubai) and on demand.

## Gather (each step is skipped, not faked, if its connector is missing)

1. `00-config.md`, `01-preferences.md`, `02-vip-contacts.md`, `04-commitments.md`, `05-approvals.md`, `07-processed.md`.
2. Calendar today and tomorrow (`ea-calendar`).
3. For each external meeting today: is there a `meetings/` pack? If not and it starts within 24h, build one (`ea-meeting-prep`) and link it.
4. Inbox triage since yesterday 10:00 (`ea-email`): waiting-on-Ali, VIP, CRITICAL/HIGH.
5. Zoho: deals modified in the last 24h, tasks due today, anything from "which clients need attention" (`ea-zoho-crm`).
6. Commitments due today or overdue, both directions.
7. Approval cards pending or expired.
8. Conflicts: overlaps, missing buffers, unprepared meetings, a deadline and a meeting colliding.

## Write, exactly this shape, under 250 words

```
GOOD MORNING · Thu 24 Sep · Heavy day

Today
10:30  Board meeting · boardroom
12:00  ABC Capital · Zoom · prep attached
14:00  Strategy · internal
16:30  Client call · Zoom · no prep yet

Needs your attention
• ABC Capital reply, 2 days waiting (A-017 drafted, say "send it")
• Pricing decision on Media City block, Sarah needs it before 12:00
• Contract approval: DMCC lease renewal, due Friday

Meeting preparation
ABC Capital: last meeting 10 Sep, they owe NDA countersign. Pack: meetings/2026-09-24-abc-capital.md

Outstanding
Ahmed → financials, due yesterday
Sarah → revised proposal, due today
You → call Khalid re site visit

CRM
Media City block moved to Negotiation. 2 tasks overdue on Palm hotel.

Watch
12:00 and 14:00 have no buffer. 16:30 attendee not in CRM.
```

Omit any section that is empty. Never add a section. Bold nothing except a CRITICAL item.

## Delivery

On the scheduled run, the briefing is the run's final message, so it reaches Ali through the scheduled task's notification. Also save a copy to `briefings/YYYY-MM-DD.md` in the state folder so "what did you tell me this morning?" is answerable.

"Summarize everything important from yesterday" uses the same gather with the window set to the previous day, and the audit log for what the assistant did.
