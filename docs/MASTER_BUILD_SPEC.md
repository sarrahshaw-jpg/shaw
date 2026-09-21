# CEO AI EXECUTIVE ASSISTANT — MASTER BUILD SPECIFICATION

Verbatim record of the specification issued on 2026‑09‑19 (reissued 2026‑09‑21 in condensed form). References elsewhere in this repo of the form "spec §N" point to the numbered sections below. This file is the authority; the condensed prompt and ARCHITECTURE.md derive from it.

## §1 Core objective
Build an AI Executive Assistant that can: understand natural‑language instructions from the CEO; manage email; draft and send emails; manage calendar and scheduling; prepare meeting briefings; process meeting transcripts; extract decisions and action items; create follow‑up tasks; update CRM records; search company information; interact with Zoom; interact with Google Meet / Google Workspace where applicable; interact with Zoho; eventually interact with Slack/Teams; eventually support WhatsApp Business/API workflows; eventually support approved LinkedIn workflows; provide daily executive briefings; proactively notify the CEO when something requires attention; operate automatically during configured working hours; maintain persistent state and memory; maintain an audit trail of important actions; require human approval for sensitive actions.
The system must NOT depend on the CEO manually starting Claude for every event.

## §2 Architectural principle — four layers
- **Layer A, AI/reasoning:** Claude determines what the user wants, which tools are required, what information is relevant, what actions should be taken, whether approval is required.
- **Layer B, tools/integrations:** MCP and APIs. Gmail/Outlook, Google Calendar/Microsoft Calendar, Google Drive/SharePoint, Zoom, Zoho, Slack/Teams, custom company systems.
- **Layer C, always‑on orchestration:** detects events and triggers workflows: new important email, calendar event approaching, meeting ended, transcript available, CRM record changed, task deadline approaching, scheduled morning briefing.
- **Layer D, persistent state:** CEO preferences, assistant configuration, task state, approval state, workflow state, audit logs, important contacts, VIP contacts, communication preferences, automation history. Do not put all persistent state inside prompts.

## §3 Operating hours
Default window 10:00–22:00. Inside: actively process authorized events and generate notifications. Outside: only critical/background processing, suppress non‑critical notifications, do not disturb the CEO unless the event meets the emergency/critical threshold. Hours configurable. Timezone configurable, default `Asia/Dubai`, never hard‑coded throughout the application.

## §4 CEO command interface
Natural language, no command syntax. Examples: "What do I have today?" "What's important in my inbox?" "Find time with Ahmed next week." "Move my 3 PM meeting to Thursday." "Draft a reply to John." "Send it." "Prepare me for my next meeting." "What did we discuss with ABC last time?" "What are my outstanding commitments?" "Which clients need my attention?" "Follow up with everyone I promised to contact this week." "Schedule a Zoom with Sarah and Ahmed." "Summarize everything important from yesterday." "Update Zoho with the outcome of this meeting."

## §5 Email
Support: search, read, summarize threads, classify priority, identify unanswered messages, identify VIP communications, draft responses, revise drafts, reply, forward, send, create follow‑up tasks, associate email with CRM records. Sending is permission‑controlled. Defaults: READ allowed, SUMMARIZE allowed, DRAFT allowed, SEND approval required. Configurable rules engine so specific categories can later be auto‑sent. Never automatically send: contracts, legal commitments, financial commitments, pricing negotiations, sensitive HR communications, confidential information, major business commitments, public statements, unless explicitly authorized.

## §6 Calendar
Support: read, find availability, create, modify, reschedule, cancel, add participants, generate meeting links where supported, add agenda, add preparation notes, create buffers. Default rules: avoid double booking; protect focus time; avoid unnecessary meetings; prefer 30‑minute meetings; add buffers where practical; respect working hours; respect existing priority/VIP meetings; never cancel a high‑priority meeting automatically; ask approval for sensitive rescheduling/cancellation. Preferences configurable, not hard‑coded.

## §7 Zoom
Official API/MCP where available. Meetings, metadata, transcripts, summaries, recordings where authorized, participants, follow‑ups, action items. When an authorized meeting ends: (1) detect end, (2) retrieve transcript/summary, (3) send to Claude, (4) extract decisions, action items, owners, deadlines, commitments, follow‑ups, (5) update CRM when appropriate, (6) create tasks, (7) prepare follow‑up emails, (8) notify CEO if approval required. Do not secretly record. Only process legally and technically authorized recordings/transcripts.

## §8 Google Meet / Google Workspace
Integrate Gmail, Google Calendar, Google Drive, Meet‑related meeting information where available. Treat Google and Zoom as interchangeable meeting sources; "What did we agree with ABC?" must work without knowing the platform.

## §9 Zoho
Official APIs/MCP. Initially: Zoho CRM, Zoho Mail, contacts, accounts, deals/opportunities, activities, tasks, notes. "What is happening with ABC?" combines Zoho CRM + email + calendar + meeting history into a concise executive summary. Support controlled CRM write actions.

## §10 Executive memory
Persistent memory for: CEO preferences, preferred meeting times, communication style, VIP contacts, important clients, recurring commitments, company priorities, current projects, important policies, delegation rules, approval rules. The AI must not silently invent permanent memories; important memory changes are logged.

## §11 Morning briefing
Automated daily, default 10:00. Includes: 1 today's schedule, 2 important meetings, 3 meeting preparation requirements, 4 important unanswered emails, 5 important incoming emails, 6 decisions requiring CEO attention, 7 outstanding commitments, 8 important CRM activity, 9 follow‑ups due, 10 potential conflicts/problems. Concise. Format example: `GOOD MORNING` / `Today's schedule:` one line per item / `Needs your attention:` / `Meeting preparation:` / `Outstanding:`.

## §12 Meeting preparation
Before important meetings collect authorized information from calendar, email, CRM, previous meeting notes, Drive/SharePoint, relevant company documents. Produce: participants, relationship/history, previous discussions, outstanding commitments, objectives, relevant numbers, unresolved issues, suggested questions, required decisions. Do not fabricate missing information.

## §13 Meeting follow‑up
Automatically create: meeting summary, decisions, action items, owners, deadlines, CRM updates, draft follow‑up email. Approval before sending external communication unless an explicit automation rule allows it.

## §14 Notification priority
CRITICAL immediate; HIGH promptly; NORMAL next briefing; LOW silent or daily summary. Configurable classifier.

## §15 Approval system
Every tool/action has a risk classification. LOW: execute automatically (read calendar, summarize email, prepare briefing, internal draft, search CRM). MEDIUM: per configured rules (routine meeting, internal task, CRM update, predefined administrative response). HIGH: explicit CEO approval (external email, cancelling important meetings, changing important commitments, sensitive CRM modifications, external messaging). PROHIBITED by default, never autonomous: transfer money, approve payments, sign contracts, delete critical records, make legal commitments, impersonate the CEO for high‑risk decisions.

## §16 Audit log
Log every meaningful autonomous action: timestamp, event, tool used, action, result, approval status, user/CEO authorization, errors. The CEO/admin can ask "What did the assistant do today?"

## §17 Security
OAuth wherever available; encrypted secrets; environment variables; least‑privilege permissions; separate development and production credentials; secure webhook validation; audit logging; role‑based access control. Never place API keys in source. Never commit secrets. `.env.example` only.

## §18 MCP architecture
MCP preferred where an official/appropriate server exists. Internal tool registry; every tool specifies name, description, input schema, output schema, risk level, permission level, whether approval is required, whether reversible, audit requirements. Allowlists for important tool groups. Destructive tools not exposed by default.

## §19 Always‑on event system
Events: NEW_EMAIL, MEETING_STARTED, MEETING_ENDED, TRANSCRIPT_AVAILABLE, CALENDAR_CHANGED, CRM_UPDATED, TASK_DUE, VIP_MESSAGE, SCHEDULED_BRIEFING, APPROVAL_REQUIRED. Each enters a queue/workflow. Idempotent processing; never process the same event twice.

## §20 Failure handling
If an integration fails: do not pretend success; record the failure; retry where appropriate with exponential backoff; notify admin for persistent failures; preserve the event for replay. Distinguish SUCCESS, PARTIAL SUCCESS, FAILED, WAITING FOR APPROVAL.

## §21 Testing
Automated tests before production‑ready for: email reading, drafting, approval, sending; calendar creation, conflict detection; meeting preparation; Zoom transcript processing; Zoho CRM lookup; CRM updates; duplicate event prevention; authorization; audit logging; failed integrations; retry behavior; notification priority; timezone handling. Integration tests with sandbox/test accounts. Never destructive tests against production data.

## §22 Development workflow — phases
0 Inspect environment · 1 Architecture and technical design · 2 Repository structure · 3 Configuration system · 4 Authentication/security layer · 5 MCP/tool abstraction · 6 Calendar · 7 Email · 8 Zoom · 9 Zoho · 10 Meeting intelligence · 11 Persistent memory/state · 12 Event/automation engine · 13 Morning briefing · 14 Approval system · 15 Notifications · 16 Mobile/Claude interface · 17 Security review · 18 Integration testing · 19 Deployment · 20 Production monitoring. Do not skip phases to produce a demo.

## §23 Documentation
README.md, ARCHITECTURE.md, SETUP.md, SECURITY.md, INTEGRATIONS.md, PERMISSIONS.md, AUTOMATIONS.md, TROUBLESHOOTING.md, DEPLOYMENT.md, TESTING.md, CHANGELOG.md, plus progress.md, tests.json, todo.md for persistent project state across sessions.

## §24 Claude Code behavior
Before major changes: inspect existing code, inspect architecture, update todo.md, implement one coherent component, run tests, fix failures, update documentation, update progress.md, commit when appropriate. Never claim something works without testing. Never invent credentials or undocumented endpoints. State exactly what credentials/config are needed. If a capability cannot use the official API/MCP, say so before building a fragile workaround. Prefer official APIs/MCP over browser automation.

## §25 Design principle
One AI executive assistant. The CEO never needs to understand MCP, APIs, webhooks, databases, queues, OAuth, automation engines or model routing.

## §26 First task
Phases 0–1 only: inspect environment; inspect tools and MCP; decide TypeScript vs Python; identify backend architecture; classify integrations (official MCP vs API/custom); what runs continuously vs through Claude; authentication; hosting; write ARCHITECTURE.md, todo.md, progress.md, tests.json; propose repository structure. Then STOP and show: A architecture diagram, B technology stack, C integration map, D security/permission model, E development phases, F what is needed. No implementation until the architecture is approved.
