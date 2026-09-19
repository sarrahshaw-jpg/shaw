---
name: ea-email
description: "Email for Ali Rao's EA: inbox triage, priority and VIP classification, thread summaries, unanswered detection, drafting, revising, replying, forwarding and the approval-gated send. Works with whichever mail connector is connected (Gmail, Hostinger Mail, Microsoft 365). Use for anything about inbox, mail, replies, drafts, sending."
---

# Email

Load `ea-operating-model` first. Sending is always HIGH.

## Which connector

Read `state/00-config.md` → `mail_provider`. Then:

| Provider | Read | Threads | Drafts | Send |
|---|---|---|---|---|
| Gmail | `search_messages`, `get_message`, `get_thread` | native | `create_draft` (preferred) | `send_message` / reply |
| Hostinger Mail | `email_call_api_read` on `/folders/{folder}/messages`, `/search`, `/messages/{uid}/text` | **none**: rebuild from `In-Reply-To` and `References` in `/messages/{uid}/source` | **none**: save to `drafts/` in the state folder | `email_call_api_write` `POST /mailboxes/{id}/send` |
| Microsoft 365 | `outlook_email_search` | native | via connector if exposed, else `drafts/` | via connector if exposed |

Hostinger rate limit is 300 requests per window. On a busy inbox, page with `perPage=50`, fetch bodies only for messages that survive triage, and never fetch source for more than 20 messages in one run.

## Triage ("what's important in my inbox?")

1. Fetch unread and unanswered from the last 48 hours (or since the last sweep in `07-processed.md`).
2. For each message classify:
   - **VIP** if sender domain is in the `vip_domains` hot cache (open `02-vip-contacts.md` only for a name match on an unknown domain).
   - **Waiting on Ali** if the last message in the thread is inbound and asks a question or requests something.
   - **Priority**: CRITICAL / HIGH / NORMAL / LOW per the project instructions. Legal, money, a counterparty deadline, or a VIP waiting more than 24h is at least HIGH.
   - **Category**: deal, investor, operations, legal, HR, admin, newsletter, other.
3. Output, grouped by priority, one line each: `sender · subject · what they want · age`. Nothing else. Offer to draft for any that are waiting on Ali.

## Thread summary

Give: who is involved, what was asked, what was agreed, what is still open, and the last message's ask. Quote verbatim only where the wording matters (a date, an amount, a condition). Never paraphrase a commitment into something stronger than it was.

## Drafting

1. Read `01-preferences.md` for tone rules and signature. Read the last two messages in the thread.
2. Apply firm rules: no dashes, nothing after "Warm regards,", no price or yield or ratio, no shareholding, location granularity, pre-NDA detail limits.
3. Check the recipient's firm against `03-firm-register.md` if this is a first contact.
4. Write it. Then store it:
   - Gmail: `create_draft` in the thread. Report the draft exists.
   - Hostinger: write `drafts/<date>-<recipient-slug>.md` in the state folder with `To`, `CC`, `Subject`, body. Report the path.
5. Say "Draft ready. Say 'send it' to send, or tell me what to change." Do not produce an approval card yet; the card is produced when he says send, so the content he approves is final.

Revisions ("make it shorter", "firmer", "add the Thursday option") edit the same draft in place.

## Sending

Only on an explicit instruction in this conversation. Then:

1. Produce the approval card with the final `To`, `CC`, `Subject`, body verbatim.
2. On "approve" / "send it": call the provider's send tool. Confirm from the tool result. Append the recipient's firm and address to `03-firm-register.md` if new. Log to `audit/`. Update the card to `EXECUTED`.
3. If the tool result is not a clear success, report `FAILED` with the error. Do not retry a send more than once; a duplicate email is worse than a late one.

If `06-automation-rules.md` lists an auto-send category (for example "acknowledge receipt of documents from existing counterparties"), a message matching it may be sent without a card, but is still logged with `auto (rule S-n)`. By default that file has no auto-send rules.

## Forwarding

HIGH. Same card. Strip anything the new recipient is not entitled to see; when in doubt, ask.

## Follow-up tasks from email

When a message contains a commitment by or to Ali, add a line to `04-commitments.md` (`ea-commitments` skill) rather than a calendar event.

## CRM association

If the sender's firm exists in Zoho, note the message in the account's timeline via `ea-zoho-crm` only when Ali asks or an automation rule allows; adding a note is MEDIUM.
