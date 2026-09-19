# CEO AI Executive Assistant

An always-on AI executive assistant for Stravion Investments, using Claude as the reasoning layer, with permission-gated integrations for email, calendar, meetings and CRM.

**Status:** architecture proposed, awaiting approval. No application code yet.

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | environment findings, design, integration map, security model, phases, open decisions |
| [todo.md](todo.md) | phase-by-phase task state |
| [progress.md](progress.md) | session log |
| [tests.json](tests.json) | test registry |
| [.env.example](.env.example) | required configuration (never commit `.env`) |

Design principle: the CEO talks to one assistant in plain language. MCP, OAuth, queues and webhooks are implementation details they never see.
