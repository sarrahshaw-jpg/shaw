# TROUBLESHOOTING

| Symptom | Cause | Fix |
|---|---|---|
| "FAILED: state folder not found" | Drive folder renamed or not shared with this account | name must match `00-config.md`; share with the account running the task |
| Briefing arrives at wrong hour | cron is UTC | Dubai 10:00 = `0 6 * * *`; see scheduled‑tasks/README |
| Assistant "cannot see Zoho" | connector not connected for *this* user or not enabled in the Project/task | Settings → Connectors; enable in Project and in each scheduled task |
| Zoom meeting has no transcript | host did not cloud‑record or recap disabled | Zoom settings → Recording → cloud recording + Meeting Summary |
| Hostinger calls failing mid‑sweep | 300 req/window limit | skills already cap fetches; reduce sweep scope or move to Gmail |
| Same email triaged twice | `07-processed.md` not written (Drive write failed) | check Drive permissions; the file must be editable |
| Draft not in Drafts folder | Hostinger has no drafts endpoint | drafts are in `drafts/` in the state folder by design |
| Assistant sent nothing after "looks good" | approval requires "approve A‑n" or "send it" | by design |
| Card expired | older than 72h | re‑issue by asking again |
