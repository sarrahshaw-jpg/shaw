# SETUP — launching the assistant in Ali's Claude

Time: about 45 minutes, done once. Nothing to host, no code to run. Everything is inside Claude plus one shared Google Drive folder.

## 0. Choose the plan

| If | Then |
|---|---|
| You and Ali want one shared assistant, shared skills, and connectors managed centrally | **Claude Team** (shared Projects, org‑provisioned skills, admin‑toggled connectors). Recommended. |
| You additionally need SSO, admin audit logs, a compliance API, longer context | **Claude Enterprise** |
| Only Ali will use it, right now | His own Pro or Max account works; he follows this file himself. Upgrade later without redoing anything. |

Team and Enterprise differences are summarized in INTEGRATIONS.md → Plans.

## 1. Create the Project

1. In claude.ai → Projects → New project → name it **Executive Assistant**.
2. Open Project settings → Custom instructions → paste the entire contents of `claude/PROJECT_INSTRUCTIONS.md`.
3. Project knowledge: upload nothing yet. State lives in Drive so it stays current; project knowledge is a snapshot and would go stale.
4. On Team/Enterprise: share the Project with Ali (and Sarah if she operates it).

## 2. Install the skills

Skills are folders with a `SKILL.md`. Run `scripts/make-skill-zips.sh` to produce one zip per skill in `dist/`, then:

- **Team/Enterprise**: Admin settings → Skills → upload each zip as an organization skill. Every member gets them.
- **Pro/Max**: Settings → Capabilities → Skills → upload each zip.

Install all nine: `ea-operating-model`, `ea-email`, `ea-calendar`, `ea-meeting-prep`, `ea-meeting-followup`, `ea-zoho-crm`, `ea-morning-briefing`, `ea-memory`, `ea-commitments`. Keep the existing `stravion-outreach` skill; the EA skills reference its rules and do not replace it.

## 3. Connect the tools (each person connects their own)

Settings → Connectors. Connect, in this order:

| Connector | Why | Notes |
|---|---|---|
| **Google Drive** | the state folder; Meet transcripts | required first |
| **Google Calendar** | schedule | **Ali's own calendar, connected by Ali** (decided 2026-09-21). Not `aamirsawar123@gmail.com`. |
| **Hostinger Mail** | inbox, drafts, send | `ar@alirao.com` is on Hostinger (decided 2026-09-21); `mail_provider` is already `hostinger`. Drafts follow the `draft_flow` row in `00-config.md`. |
| **Zoho CRM** | accounts, deals, notes, tasks | official Zoho CRM connector from the directory; sign in with the org's Zoho account, it routes to the correct data centre automatically |
| **Zoom for Claude** | meeting search, recaps, transcripts | only sees recordings the host made with cloud recording and recap/transcript enabled |
| Slack | internal chasing | optional, later |
| Zapier | LinkedIn posting, long‑tail apps | optional |

Then, in the Project, make sure these connectors are enabled for chats.

## 4. Create the state folder in Drive

1. Create a folder named exactly **`EA — Ali Rao`** in Google Drive (shared drive if on Workspace).
2. Upload every file from `claude/state-templates/` keeping names. Create empty subfolders `audit/`, `drafts/`, `meetings/`, `briefings/`.
3. Edit `00-config.md`: set `mail_provider`, confirm the mailbox addresses and hours.
4. Edit `02-vip-contacts.md`: add the ten to twenty people who matter most.
5. Share the folder with Ali (edit) and Sarah (edit). Nobody else.

## 5. Seed the firm register

In a chat inside the Project: "Read the Sent folder of sarah@stravion.ae and ar@alirao.com for the last 12 months and build the firm register in 03-firm-register.md. Do not send anything." Review the result; this table is what stops a second approach to a firm already contacted.

## 6. Create the three scheduled tasks

Follow `claude/scheduled-tasks/README.md`. Paste each prompt as written. Enable the same connectors on each task. Turn on completion notifications (push and email) so the briefing and any CRITICAL item reach Ali's phone.

## 7. Smoke test, in this order, in a Project chat

1. "What do I have today?" — expect a schedule in the fixed format.
2. "What's important in my inbox?" — expect grouped triage, nothing sent.
3. "Draft a reply to <someone real>" then "send it" — expect a draft, then an approval card, then a send only after "approve A‑001", then an audit line and a firm‑register line.
4. "What did you do today?" — expect a summary read from `audit/`.
5. Run the morning‑briefing task manually once ("Run now"). Check `briefings/` in Drive received a copy.

Record each result in `tests.json` (`evals/README.md` explains the statuses).

## 8. Hand over to Ali

Send him: the Project link, this file's step 3 (he connects his own Google, mail, Zoho and Zoom), and the sentence "Talk to it like a chief of staff; it will never send anything without asking you."

## Where things are

| | |
|---|---|
| The assistant's behaviour | `claude/PROJECT_INSTRUCTIONS.md` + `claude/skills/` |
| Its memory, tasks, approvals, audit | Google Drive folder `EA — Ali Rao` |
| Its background schedule | three scheduled tasks in Ali's account |
| Firm rules | `01-preferences.md`, `06-automation-rules.md`, `stravion-outreach` skill |
