---
name: ea-commitments
description: "Tracks commitments made by and to Ali Rao: promises in email, meetings and chat, with owner, due date, status. Answers 'what are my outstanding commitments', 'who owes me what', 'follow up with everyone I promised to contact this week', and feeds the briefing. Use for tasks, promises, follow-ups, deadlines."
---

# Commitments

Load `ea-operating-model` first. Adding or updating a line is MEDIUM (allowed by default rule M-1 in the template). Chasing someone by email is HIGH.

## The file: `04-commitments.md`

One line per commitment:

```
C-041 | 2026-09-17 | Ali → Khalid (Emaar) | send title deed copy | due 2026-09-24 | OPEN | src: email 17 Sep
C-042 | 2026-09-10 | Ahmed → Ali | Q3 financials | due 2026-09-23 | OVERDUE | src: Zoom 10 Sep
C-043 | 2026-09-20 | Sarah → Ali | revised proposal, Media City | due 2026-09-24 | OPEN | src: chat
```

Statuses: `OPEN`, `OVERDUE` (set automatically by comparing the date), `DONE <date>`, `DROPPED <reason>`.

## Capture

From email (`ea-email`), meeting follow-up (`ea-meeting-followup`), or Ali saying "I told Khalid I'd send the deed". Direction matters: `Ali → X` is something Ali owes; `X → Ali` is owed to him. If the owner or date is missing, capture with "No date" and flag in the next briefing.

## "What are my outstanding commitments?"

`Ali → *` lines that are OPEN or OVERDUE, overdue first, then by due date. Then `* → Ali`. One line each, plus the source so he can check.

## "Follow up with everyone I promised to contact this week"

1. List `Ali → *` lines due this week with "contact", "reply", "call", "send" in the action.
2. For each, draft the message (`ea-email`) or propose the call slot (`ea-calendar`).
3. One approval card per outbound, or one batch card if `01-preferences.md` says so.
4. Mark `DONE` only after the send is confirmed.

## Chasing what is owed to Ali

Draft a polite chase for `X → Ali` items more than 2 days overdue, but only produce cards when Ali asks; chasing is his call. Internal people (Ahmed, Sarah) can be chased on Slack if connected and rule M-4 allows.
