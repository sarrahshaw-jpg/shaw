---
name: ea-meeting-followup
description: "After a meeting: retrieve the Zoom recap/transcript or the Google Meet transcript from Drive, extract decisions, action items, owners, deadlines, commitments and follow-ups, write the meeting note, update commitments, propose CRM updates and draft the follow-up email, all approval-gated. Use for 'what did we agree', 'follow up on the meeting', 'process the transcript', 'update Zoho with the outcome'."
---

# Meeting follow-up

Load `ea-operating-model` first. Reading transcripts and writing notes is LOW. Adding commitments is MEDIUM. CRM writes and follow-up emails are HIGH.

## Sources, treated as interchangeable

| Where the meeting was | How to get the record |
|---|---|
| Zoom | `search_meetings` for the meeting by title/date/participant → `get_meeting_assets` (summary, transcript, action items where Zoom produced them) → `get_recording_resource` for the transcript text |
| Google Meet | Meet writes transcripts as Google Docs in the "Meet Recordings" Drive folder → `search_files` by date and title → `read_file_content` |
| Neither / in person | Ask Ali for his notes, or a voice memo transcript in Drive |

Only process recordings that already exist. If there is none, say "No recording or transcript exists for this meeting" and offer to take Ali's dictated notes instead. Never suggest enabling recording on someone else's meeting.

## Idempotency

Before processing, check `07-processed.md` for the Zoom meeting UUID or the Drive file ID. Skip if present. Append after writing the note.

## Extract

From the transcript or summary, produce:

- **Decisions**: what was decided, by whom, verbatim where the wording matters.
- **Action items**: `owner · action · due date · source line`. If no owner was named, write "Unassigned" and flag it. If no date, "No date" and flag it.
- **Commitments by Ali**: anything Ali said he would do or send.
- **Commitments to Ali**: anything the other side said they would do.
- **Open questions**: raised, not resolved.
- **Sensitive**: anything about price, terms, exclusivity or legal exposure, listed for Ali's eyes only and never carried into external text.

Do not infer a decision from a discussion. "We should probably" is not a decision. When unsure, put it under open questions.

## Write

1. Meeting note to `meetings/YYYY-MM-DD-<slug>.md` (append to the prep pack if one exists, under `## Outcome`).
2. Each action item and commitment → `04-commitments.md` via `ea-commitments`.
3. Propose CRM updates via `ea-zoho-crm`: note on the account, task per action item, deal stage change if a decision warrants it. Each write is its own approval card, or one card listing them all if Ali prefers (`01-preferences.md`).
4. Draft the follow-up email per `ea-email`: thank, restate decisions and next steps, no price or terms, owners and dates. Save as a draft; produce an approval card only when Ali says send.

## Report to Ali

```
<Meeting> · <date> · <duration> · <participants>
Decisions (n): ...
Actions (n): owner · what · when
Ali owes: ...
They owe: ...
Open: ...
Proposed: CRM note + 2 tasks (A-021), follow-up email drafted (say "send it")
```

End with the outcome state.
