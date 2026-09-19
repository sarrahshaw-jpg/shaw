# LAUNCH — putting the assistant on Ali's computer and phone

Two people, two roles. **Sarah (or the admin)** does the one‑time setup on a computer, about 30 minutes. **Ali** does 5 minutes on his computer, then lives in the phone app. Everything is account‑level in Claude: set up once, it works on his laptop, the desktop app and the iPhone/Android app.

---

## Part 1 — Admin, once, on a computer (Sarah)

### Choose how Ali gets it
- **Fastest today:** Ali's own Claude account (Pro or Max). Send him Part 2; he does it himself in 10 minutes. Everything below still applies, he just does it in his own account.
- **Right for the firm:** Claude **Team**. You create the Project and skills once in the organisation, share the Project with Ali, and each of you connects your own tools. Enterprise only if you need SSO and admin audit logs.

### 1. Google Drive: the assistant's memory
1. Create a folder named exactly **`EA — Ali Rao`**.
2. Upload every file in `claude/state-templates/` (keep names). Create empty subfolders `audit/`, `drafts/`, `meetings/`, `briefings/`.
3. Open `02-vip-contacts.md` and add the 10 to 20 people who matter most, with their email domains. Copy those domains into the `vip_domains` row at the bottom of `00-config.md`.
4. Share the folder with `ar@alirao.com` as **Editor**. Nobody else. Link sharing off.

### 2. Skills
Run `scripts/make-skill-zips.sh` → nine zips in `dist/`.
- Team: Admin settings → Skills → upload each zip (organisation skills, everyone gets them).
- Pro/Max: Settings → Capabilities → Skills → upload each zip.
Keep `stravion-outreach` installed too.

### 3. The Project
1. claude.ai → Projects → New → name **Executive Assistant**.
2. Settings → Custom instructions → paste all of `claude/PROJECT_INSTRUCTIONS.md`.
3. Team: share the Project with Ali.

### 4. Scheduled tasks (the background)
In claude.ai → Scheduled tasks → New, three times, from `claude/scheduled-tasks/`:
| | Prompt file | Schedule (UTC) | Dubai |
|---|---|---|---|
| Briefing | `01-morning-briefing.md` | `0 6 * * *` | 10:00 |
| Sweep | `02-working-hours-sweep.md` | `0 7-17 * * *` | hourly 11:00–21:00 |
| Wrap | `03-evening-wrap.md` | `30 17 * * *` | 21:30 |
Enable the connectors on each (Drive, Calendar, mail, Zoho CRM, Zoom). Turn on **push and email notification on completion**. These must be created in **Ali's account** so they use his connectors; if you set up on Team, have Ali create them from his login in Part 2 step 4, or do it while signed in as him.

### 5. Seed the firm register
In a chat inside the Project: "Read the Sent folders of sarah@stravion.ae and ar@alirao.com for the last 12 months and fill 03-firm-register.md. Do not send anything." Check the result.

---

## Part 2 — Ali, on his computer, 5 minutes

Connectors are the only thing that must be done by Ali himself, because they sign in as him. Do this on a computer once; the phone uses the same connections.

1. Open claude.ai → **Settings → Connectors**. Connect: **Google Drive**, **Google Calendar**, your **email** (Gmail if your mail is Google Workspace; Hostinger Mail if it is with Hostinger; Microsoft 365 if Outlook), **Zoho CRM** (sign in with the firm's Zoho login), **Zoom for Claude** (sign in with your Zoom).
2. Open the **Executive Assistant** Project. Check the connectors above are enabled in it.
3. If the admin did not do it in your account: create the three scheduled tasks in Part 1 step 4 while signed in as you.
4. Type: **"What do I have today?"** If a schedule comes back, it works.

---

## Part 3 — Ali, on the phone, every day

1. Install the Claude app. Sign in with the same account. Turn on notifications.
2. Open **Projects → Executive Assistant**. Every conversation you start inside it is the assistant. Start a new chat each day or keep one running; the memory lives in Drive, not in the chat.
3. Speak or type naturally:
   - "What do I have today?" · "What's important in my inbox?" · "Prepare me for my next meeting"
   - "Draft a reply to Khalid saying Thursday works" → "Send it" → it shows an approval card → reply **1** to send, **2** to edit, **3** to drop
   - "What did we agree with ABC last time?" · "Which clients need me?" · "Update Zoho with the outcome" · "What did you do today?"
4. At **10:00** the briefing arrives as a notification. Hourly during the day you get a notification only if something needs you. At **21:30** a wrap.
5. Anything it wants to send, move with an outsider, or change in the CRM comes to you as a card first. Nothing goes out without your **1**.

Nothing to install beyond the app. Nothing to configure on the phone.

---

## What makes it fast on a phone

- It reads one small config file per task, not the whole memory; the evening wrap refreshes that file's hot cache.
- Replies are under 8 lines unless you ask for more, one item per line, no wide tables.
- Approval cards end in `1 approve · 2 edit · 3 drop`.
- "Send it", "go ahead", "yes" in reply to a card count as approval; "hold" leaves it pending.
- It runs independent lookups at the same time and never re‑reads what it already has.

## If something is off
`TROUBLESHOOTING.md`. The most common: a connector not enabled inside the Project (enable it), a scheduled task created in the wrong account (recreate it signed in as Ali), a briefing at the wrong hour (the schedule is in UTC; Dubai is UTC+4).
