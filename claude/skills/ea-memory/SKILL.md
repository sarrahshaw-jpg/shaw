---
name: ea-memory
description: "Executive memory for Ali Rao's EA: reading and updating preferences, VIP contacts, the firm register, company priorities, delegation and approval rules in the Drive state folder, with every change proposed, approved and logged. Use when Ali states a preference, asks 'remember that', asks what the assistant knows about someone, or when a durable fact is learned."
---

# Executive memory

Load `ea-operating-model` first. Reading is LOW. Writing to `01`, `02` or `06` is MEDIUM and, by rule, always confirmed with Ali first. Writing to `03-firm-register.md` after an approved send is automatic.

## Principle

The assistant never silently invents permanent memory. A durable fact enters a state file only when Ali confirms it, or when it is the direct record of an action he approved (a sent email → firm register entry).

## What lives where

- `01-preferences.md`: meeting lengths, buffers, preferred days and times, communication style, signature, how he wants approvals batched, delegation ("Sarah can approve X"), languages.
- `02-vip-contacts.md`: name, firm, role, why they matter, response-time expectation, sensitivities.
- `03-firm-register.md`: firm, domain, contact, date of first outbound, by whom, status. One line per firm. This is the one-contact-per-firm enforcement table.
- `06-automation-rules.md`: MEDIUM actions allowed without asking (`M-n`), auto-send categories (`S-n`). Only Ali edits this. The assistant may propose a rule after seeing the same approval three times.

## "Remember that …"

1. Restate the fact as one line in the file's format.
2. Ask "Add this to preferences?" (or VIPs, or rules).
3. On yes: `update_file`, then log `memory.update` to `audit/`.

## When a durable fact is inferred, not stated

("He has declined every Friday afternoon slot this month.") Propose it in the next briefing under Watch; do not write it.

## "What do you know about X?"

Read `02-vip-contacts.md`, `03-firm-register.md`, `04-commitments.md`, `meetings/`, then CRM and email. Answer with facts and their sources, nothing inferred.

## Semantic recall ("what did we discuss with ABC last time?")

Search `meetings/` by firm, then Zoom (`search_meetings`), then Meet transcripts in Drive, then email. Present the most recent first with dates. If nothing is found in any source, say so.
