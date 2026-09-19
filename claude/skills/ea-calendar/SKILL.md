---
name: ea-calendar
description: "Calendar for Ali Rao's EA via Google Calendar (or Microsoft 365): today's schedule, availability, finding time with people, creating, moving, cancelling meetings, buffers, focus time, conflict detection, meeting links. Use for anything about schedule, availability, booking, rescheduling."
---

# Calendar

Load `ea-operating-model` first. Any create/move/cancel involving an external attendee is HIGH. Internal-only changes are MEDIUM (allowed if `06-automation-rules.md` permits).

## Preferences (read from `01-preferences.md`, defaults below)

- Default meeting length **30 min**; 60 only if the other side asks or it is a board or investor meeting.
- **Buffer 15 min** before and after external meetings; none needed between internal ones.
- **Focus blocks** are protected; never book over an event titled "Focus", "Hold", "Do not book" or marked private.
- Working hours from `00-config.md` (default 10:00 to 22:00, but prefer 10:00 to 18:00 for booking unless Ali says otherwise). Never propose Friday afternoon or weekend slots to external parties unless asked.
- Never double book. Overlap with any existing event is a conflict unless the existing one is marked free or is an all-day informational event (holiday calendar).
- VIP meetings (attendee in `02-vip-contacts.md`) are never moved or cancelled automatically, and a request to move one is always HIGH.

## "What do I have today?"

`list_events` for today 00:00 to 24:00 Dubai (also fetch tomorrow for context). Output one line per event: `HH:MM  title  ·  who  ·  where/link`. Flag: back-to-back with no buffer, any event with no agenda in the description, any external meeting with no prep pack in `meetings/`. Then one line of shape: "Heavy day, 5h in meetings" or "Open afternoon".

## Availability and finding time

"Find time with Ahmed next week":
1. Read Ali's free slots for the range (`suggest_time` or `list_events` and compute).
2. Apply preferences: length, buffers, hours, no focus blocks.
3. If Ahmed's calendar is visible, intersect. If not, propose 3 slots spread across different days and times.
4. Present: `Tue 23 Sep 11:00 · Wed 24 Sep 15:30 · Thu 25 Sep 11:30`. Ask which to hold. Do not send invites yet.

## Creating

1. Confirm: title, attendees, length, location or "Zoom" or "Meet", agenda line.
2. Conflict check against the final slot including buffers.
3. Internal only → MEDIUM. Any external attendee → approval card.
4. `create_event` with the description containing the agenda and, if available, a link to the prep pack. Add a Meet link via the connector when the meeting is virtual and no Zoom link was supplied; for Zoom, ask Ali for the link or use the standing personal link from `01-preferences.md`.
5. Confirm from the tool result. Log.

## Moving and cancelling

"Move my 3pm to Thursday":
1. Identify the event unambiguously (`search_events`). If two match, ask.
2. If it has external attendees or a VIP → approval card that names the old and new time and the attendees who will be notified.
3. Never cancel a VIP or board meeting. Propose alternatives and let Ali decide.
4. On approval, `update_event` or `delete_event` only for a cancel Ali explicitly approved; a cancel is the one delete this skill may perform, and only with a card.

## Conflicts

Before every create or move, and in every briefing: overlapping events, events with no buffer around an external meeting, two external meetings in different physical locations less than 45 min apart, meetings outside working hours.

## Agenda and prep

When creating an external meeting, ask whether Ali wants a prep pack (`ea-meeting-prep`). For meetings created by others, the morning briefing flags any within 24h that lack one.
