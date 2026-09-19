# AUTOMATIONS

| Trigger | Mechanism | Handler | Latency |
|---|---|---|---|
| SCHEDULED_BRIEFING | scheduled task 01, `0 6 * * *` UTC | `ea-morning-briefing` | on time |
| NEW_EMAIL / VIP_MESSAGE | scheduled task 02, hourly 07–17 UTC | `ea-email` triage → draft → card | ≤ 60 min |
| CALENDAR_CHANGED | task 02 | `ea-calendar` conflicts, `ea-meeting-prep` | ≤ 60 min |
| MEETING_ENDED / TRANSCRIPT_AVAILABLE | task 02 (Zoom assets, Meet Docs) | `ea-meeting-followup` | ≤ 60 min after Zoom finishes the recap |
| CRM_UPDATED | task 02 | `ea-zoho-crm` VIP account changes | ≤ 60 min |
| TASK_DUE | task 03 evening + task 01 morning | `ea-commitments` | daily |
| APPROVAL_REQUIRED | any run | card in `05-approvals.md` + final message → notification | immediate on run |
| Quiet hours | tasks simply do not run outside 06–18 UTC; task 02 also checks `00-config.md` | | |

Event dedupe: `07-processed.md`. Retry: once per connector call, then report. Replay: an unprocessed item is picked up by the next run automatically because it is not in `07-processed.md`.

## Runner options (verified 2026‑09‑19)
Two equivalent ways to host the three background runs, both fresh‑session, both with connectors and push notifications:
1. **claude.ai scheduled tasks** in Ali's account (LAUNCH.md Part 1 step 4).
2. **Claude Code Routines** (`create_trigger`, hourly minimum). Three Routines already run daily in this account for the LinkedIn project, so the mechanism is proven here. A failed run is visible in run history; add an admin alert on two consecutive failures.

Sub‑hour reaction (webhook‑driven) needs Track 2 `ea-core`; see ARCHITECTURE.md §C.
