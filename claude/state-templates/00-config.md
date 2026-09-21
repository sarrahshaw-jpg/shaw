# EA configuration

Only Ali or the admin edits this file. The assistant reads it at the start of every task.

| Key | Value |
|---|---|
| assistant_name | Noor (change this one value to rename her everywhere; the skills read it from here) |
| wake_words | noor, nour, nur, noora (spoken and typed; transcription variants included on purpose) |
| principal | Ali Rao <ar@alirao.com> |
| delegate | Sarah Shaw <sarah@stravion.ae> (may approve MEDIUM actions; may not approve HIGH on Ali's behalf) |
| timezone | Asia/Dubai |
| operating_hours | 10:00 to 22:00 |
| booking_hours | 10:00 to 18:00 |
| briefing_time | 10:00 |
| evening_wrap_time | 21:30 |
| state_folder | EA — Ali Rao |
| mail_provider | hostinger (decided 2026-09-21; Ali connects Hostinger Mail for ar@alirao.com himself) |
| principal_mailbox | ar@alirao.com |
| secondary_mailbox | sarah@stravion.ae (Hostinger, resource AC17d75d6399ce66bff0357b5c5ef8) |
| calendar | Ali's own Google Calendar, connected by Ali (decided 2026-09-21; never aamirsawar123@gmail.com) |
| crm | Zoho CRM, all modules |
| meetings | Zoom (cloud recordings with recap enabled by host), Google Meet |
| chat | none yet (Slack optional) |
| draft_flow | hostinger_drafts: a draft is written and kept; if Ali says "read it to me" it is read back verbatim; if he says "send it" it goes out after the approval card; otherwise it stays as a draft for him to send with one tap (decided 2026-09-21) |
| voice_mode | on: spoken answers are shorter and speakable, drafts are always read back before a spoken send, approvals require the words "send it" or "approve" |
| approval_expiry_hours | 72 |
| critical_vip_wait_hours | 24 |
| unanswered_high_hours | 48 |

## Hot cache

Refreshed by the 21:30 evening wrap from the other state files so that most tasks need only this one read. Do not edit by hand; edit the source file.

| Key | Value |
|---|---|
| vip_domains | stravion.ae (add domains from 02-vip-contacts.md) |
| vip_names | Sarah Shaw |
| firm_register_count | 0 |
| last_approval_seq | A-000 |
| open_approvals | none |
| overdue_commitments | 0 |
| meeting_default_min | 30 |
| buffer_min | 15 |
| outbound_rules | no dashes; end at "Warm regards,"; no price/yield/ratio; no shareholding; one contact per firm |
| cache_refreshed | never |
