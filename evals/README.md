# Evals

There is no code in this system, so tests are **behavioural scenarios** run as conversations inside the Project (or with the `skill-creator` skill's eval runner). Each scenario states the setup, the exact prompt, and what must and must not happen. A scenario passes only when every "must" is observed in the tool calls and reply, and every "must not" is absent.

Statuses in `tests.json`: `not_run`, `pass`, `fail`, `blocked`. Record the date and who ran it. Never mark `pass` from memory.

Run destructive‑looking scenarios (send, CRM write, cancel) only against a test recipient, a sandbox Zoho account, or with the connector disconnected so the approval card is the terminal step.
