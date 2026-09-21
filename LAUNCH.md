# LAUNCH — putting Noor into Ali's Claude

**Noor** is the assistant's name. Arabic for light, and a woman's name heard every day in Dubai. One syllable, soft, impossible to mistype, and it survives a bad voice transcript. To rename it, change one value, `assistant_name` in `00-config.md`, and it is called that everywhere from the next conversation. Nothing else needs editing.

The goal, stated plainly: **one agent living inside Ali's own Claude**, on his phone and laptop, awake on its own schedule, that he talks to in ordinary words. No app to install beyond Claude itself, nothing to host, no syntax to learn.

Three things make that true, and all three are set up once:

| | What it is | What it gives Ali |
|---|---|---|
| **The skills** | 10 skill files uploaded to his account | the agent itself. It activates wherever he types, in any chat, because the `executive-assistant` skill recognises what he is asking for |
| **The memory** | a Google Drive folder, `EA — Ali Rao` | it remembers his preferences, VIPs, commitments, approvals and everything it has done, across every conversation and device |
| **The schedule** | 3 scheduled tasks in his account | it works while he is not looking: the 10:00 briefing, an hourly sweep through the day, a 21:30 wrap. This is what "always on" means |

Take away the schedule and it is a very good assistant that waits to be asked. With it, it comes to him.

---

## Part 1 — Admin, once, on a computer, about 30 minutes

### 1. Upload the skills
Ten zip files are in `dist/` (run `scripts/make-skill-zips.sh` to rebuild them).

- **Team or Enterprise**: Admin settings → Skills → upload each zip as an organisation skill. Everyone in the org gets them.
- **Pro or Max**: Settings → Capabilities → Skills → upload each zip.

Upload `executive-assistant` first; it is the one that makes the agent answer to plain language. The nine `ea-*` skills are the procedures it calls. Keep `stravion-outreach` installed alongside them.

### 2. Build the memory folder
A Google Drive folder named exactly **`EA — Ali Rao`** holding the eight state files and four subfolders. It already exists in the admin Drive:

https://drive.google.com/drive/folders/10QygQqVM3FkQ7M0jhVwO9EHkQevcXI-A

To recreate it elsewhere, upload everything in `claude/state-templates/` keeping the names, and create empty `audit/`, `drafts/`, `meetings/`, `briefings/`.

Then, before go-live:
- Open `02-vip-contacts.md` and add the ten to twenty people who matter most, with their email domains. Copy those domains into the `vip_domains` row of `00-config.md`.
- Share the folder with `ar@alirao.com` as **Editor**. Nobody else. Link sharing off. Whoever can edit this folder can change the assistant's rules.

### 3. Optional: a Project as his front door
A Claude Project named **Executive Assistant**, with `claude/PROJECT_INSTRUCTIONS.md` pasted into its custom instructions, gives Ali one obvious place to go and keeps the connectors switched on. It is no longer required, because the `executive-assistant` skill triggers anywhere, but it is a nicer front door on the phone. On Team, share the Project with him.

---

## Part 2 — Ali, on his computer, 5 minutes

Only he can do this step: connectors sign in as him.

1. claude.ai → **Settings → Connectors**. Connect **Google Drive**, **his own Google Calendar**, **Hostinger Mail** (his mailbox `ar@alirao.com`), **Zoho CRM**, **Zoom for Claude**.
2. Type: **"What do I have today?"** A schedule comes back, it works.

## Part 3 — The always-on part, in Ali's account

Scheduled tasks run in whoever's account created them, using that person's connectors, so these must be created while signed in as Ali. claude.ai → Scheduled tasks → New, three times, pasting the prompts from `claude/scheduled-tasks/`:

| | Prompt file | Schedule (UTC) | Dubai time |
|---|---|---|---|
| Morning briefing | `01-morning-briefing.md` | `0 6 * * *` | 10:00 |
| Working-hours sweep | `02-working-hours-sweep.md` | `0 7-17 * * *` | hourly, 11:00 to 21:00 |
| Evening wrap | `03-evening-wrap.md` | `30 17 * * *` | 21:30 |

Enable the same connectors on each task, and turn on **push and email notification on completion**. Nothing runs outside those hours, which is how quiet hours are kept.

What he will actually notice: a briefing at 10:00, a notification during the day only when something genuinely needs him, and a wrap at 21:30. Between those, he can open Claude and ask for anything.

---

## Part 4 — Ali, on the phone, every day

Install the Claude app, sign in, allow notifications. Then talk to it, by thumb or by voice:

- "Noor, what do I have today?" · "What's important in my inbox?" · "Prepare me for my next meeting"
- "Draft a reply to Khalid saying Thursday works" → "Read it to me" → "Send it" → a card appears → reply **1** and it goes
- "What did we agree with ABC last time?" · "Which clients need me?" · "Update Zoho with the outcome" · "What did you do today?"

Saying just "Noor" gets a one word answer and a wait. He does not have to repeat the name once a conversation is running. No commands, no menus. If he does not say send, a draft simply waits for him.

### Voice, and where the line honestly falls

**What works.** Open the Claude app, use voice mode, and speak. Noor answers in speech shaped for listening: three or four sentences, no tables or bullets read aloud, times said in full, one question at a time. Dictated text in the normal chat box works the same way. He can run a whole exchange without looking at the screen: ask what is in the inbox, ask for a reply to be drafted, have it read back, say send it.

**The safety rule in voice.** Before anything he approved by ear actually goes out, Noor reads the recipient, the subject and the body back word for word and asks once more. He cannot see a card he never looked at, so hearing it is the only way he knows what he approved. If the transcript is garbled, Noor says it did not catch that and asks rather than guessing at a name or a figure.

**What does not exist, so nobody is disappointed.** There is no always listening hotword. Ali cannot say "Noor" to a locked phone on a table and have it wake up, the way Siri does. That is an operating system capability, and Claude does not offer a custom wake word. He opens the app, or the existing conversation, and then speaks. The name is what activates the assistant *inside* Claude, not what wakes the phone.

**One thing worth trying on iPhone.** Open the Shortcuts app and search for a Claude action. If one is offered, make a shortcut named "Noor" that opens Claude, and "Hey Siri, Noor" will then hand him straight into the app with the mic live. That is Apple's wake word doing the waking and Claude doing the work, which is as close to Siri behaviour as this can get. I have not been able to verify from here whether that action is exposed, so treat it as a two minute experiment rather than a promise.

**The standing promise:** nothing is sent, no meeting with an outsider is changed, and nothing is written to a CRM deal without a card and his explicit yes. The scheduled runs cannot do any of those things at all, by design.

---

## What is not possible, stated honestly

- **Reaction is hourly, not instant.** The sweep runs every hour during the day. A meeting that ends at 14:05 is followed up by 15:00, not at 14:06. Making it instant needs a hosted service with webhooks, which is the Track 2 work in `ARCHITECTURE.md`.
- **Drafts live in Claude, not in his mail app's Drafts folder.** The Hostinger email API has no endpoint for creating drafts. His one tap is on the card in Claude, which sends through the connector. Putting drafts into his actual mail app needs IMAP credentials, also Track 2.
- **Rules are enforced by the model plus his approval step, not by code.** Every HIGH action passes a human, the audit log shows everything the same day, and the eval scenarios test the rules. A hard code-level guarantee is Track 2.

## If something is off
`TROUBLESHOOTING.md`. The usual three: a connector not enabled for the chat or task, a scheduled task created in the wrong account, or a briefing at the wrong hour because the schedule is in UTC and Dubai is UTC+4.
