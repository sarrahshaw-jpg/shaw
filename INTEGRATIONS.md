# INTEGRATIONS

All via official Claude connectors from the claude.ai directory (verified present on 2026‑09‑19). Each person connects their own.

| System | Connector | Used for | Notes |
|---|---|---|---|
| Google Drive | Google Drive (official) | state folder, Meet transcripts, documents | connected in this workspace |
| Google Calendar | Google Calendar (official) | schedule, availability, events | connected; calendar tz already Asia/Dubai |
| Gmail | Gmail (official) | mail if `ar@alirao.com` is on Google Workspace | native threads and `create_draft` |
| Hostinger Mail | Hostinger Mail (directory) | `sarah@stravion.ae`, and Ali's mail if Hostinger‑hosted | connected; **no threads, no drafts endpoint**, 300 req/window; skills compensate |
| Microsoft 365 | Microsoft 365 (official) | if Ali is on Outlook | currently `connect_incomplete` in this workspace |
| Zoho CRM | Zoho CRM (official, 41 tools) | accounts, contacts, deals, notes, tasks, custom modules | not yet connected; sign in with org account, routes to the correct DC. Zoho's docs list .com/.eu/.in/.com.au/.jp/.sa/.ca data centres, no UAE‑specific one; UAE orgs are typically on .sa or .com. Irrelevant with the connector. |
| Zoom | Zoom for Claude (official) | search meetings, recordings, recaps, transcripts | not yet connected; requires cloud recording + recap enabled by host |
| Slack | Slack (official) | internal chasing | optional |
| LinkedIn | via Zapier (4 actions enabled) | publishing only | LinkedIn's API does not permit automated outreach; not built |
| WhatsApp Business | none official found | | deferred; revisit when a directory connector exists |
| Research | Apify, Vibe Prospecting | counterparty verification before outreach | connected |

## Plans
Team: shared Projects, org‑provisioned skills, admin‑toggled connectors. Enterprise adds SSO/SCIM, audit logs, compliance API, RBAC on connectors, longer context. Both support scheduled tasks running in the cloud. Sources: [Team plan](https://support.claude.com/en/articles/9266767-what-is-the-team-plan), [Team and Enterprise](https://support.claude.com/en/collections/9387370-team-and-enterprise-plans), [Cowork on Team/Enterprise](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans).
