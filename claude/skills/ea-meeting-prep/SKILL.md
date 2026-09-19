---
name: ea-meeting-prep
description: "Meeting preparation packs for Ali Rao: participants, relationship history, previous discussions, outstanding commitments, objectives, relevant numbers, unresolved issues, suggested questions, required decisions. Pulls from calendar, email, Zoho CRM, Zoom/Meet history and Drive. Use for 'prepare me for', 'brief me on', 'who am I meeting'."
---

# Meeting prep

Load `ea-operating-model` first. This skill is LOW risk: it reads and writes only to `meetings/` in the state folder.

## Trigger

Ali asks, or the morning briefing or hourly sweep finds an external meeting within 24 hours with no file at `meetings/YYYY-MM-DD-<slug>.md`.

## Gather, in this order, stopping when a source is unavailable

1. **Calendar**: the event, its description, attendees, any attached docs or links.
2. **Contacts**: each external attendee against `02-vip-contacts.md` and `03-firm-register.md`.
3. **CRM** (`ea-zoho-crm`): the account, open deals and stage, last activities, notes, open tasks.
4. **Email**: last 90 days with those attendees or their domain. Pull the last three threads' summaries.
5. **Meetings**: previous Zoom meetings with the same participants (`search_meetings`, `get_meeting_assets` for summary), and Google Meet transcripts in Drive (`search_files` for the participant names in the "Meet Recordings" folder). Also any earlier `meetings/*.md` with the same firm.
6. **Commitments**: `04-commitments.md` filtered to this firm or these people.
7. **Drive**: documents named for the firm or the asset under discussion (NDA, proposal, term sheet). Read only what is relevant; cite file names.

## Write the pack

Save to `meetings/YYYY-MM-DD-<firm-or-topic-slug>.md`, then show it. Format:

```
# <Title>  ·  Thu 24 Sep 12:00  ·  Zoom
Participants: <name, role, firm> (VIP if so)
Relationship: <two lines, factual: first contact date, who introduced, stage>
Last time: <date> · <three bullets of what was discussed and agreed>
Outstanding: <commitments either way, with owner and due date>
Objective for this meeting: <one line, from the invite or Ali's note; if none, "Not stated"> 
Numbers that matter: <only figures already shared with this party or internal ones Ali may cite; never price>
Unresolved: <open questions from previous threads>
Questions to ask: <3 to 5>
Decisions needed: <what Ali may be asked to decide>
Sources: <email dates, meeting dates, file names>
```

## Rules

- **Never fabricate.** A section with no evidence says "Nothing found" and the Sources line shows what was searched.
- Do not include price, yield, leaseback, entry ratio or the shareholding in a pack, even though the pack is internal; packs get forwarded.
- Keep it under 400 words. Ali reads it walking into the room.
- If the meeting has no external attendees, ask before building a pack; internal meetings usually need only the agenda.
