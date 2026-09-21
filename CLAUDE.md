# CLAUDE.md — working rules for this repository

Project: AI Executive Assistant for the CEO of Stravion Investments. Authority order: `docs/MASTER_BUILD_SPEC.md` (the spec) → `ARCHITECTURE.md` (the approved design, once approved) → this file → everything else.

## Gate state
- Phases 0–1 delivered. **Waiting for the owner's written "approved"** before any application code, scaffolding or runtime dependency. Check `progress.md` top entry and `todo.md` `[!]` items before doing anything.

## Hard rules (spec §15, §17, §24; condensed prompt §1)
- No application code before "approved". No demos that skip phases.
- Never claim something works without a recorded test. Outcomes are exactly one of `SUCCESS` · `PARTIAL SUCCESS` · `FAILED` · `WAITING FOR APPROVAL`.
- Never invent credentials or endpoints. Name exact fields and console paths; never ask for secret values in chat.
- `.env.example` only; `.env*` ignored; no keys in source or docs.
- PROHIBITED actions have no override flag anywhere: money, payments, contracts, deleting critical records, legal commitments, impersonating the CEO on high‑risk decisions.
- Never initiate or enable recording. Never build ToS‑breaching automation (LinkedIn outreach, browser bots).
- Timezone (`Asia/Dubai`), hours (10:00–22:00), scheduling prefs, VIPs and rules come from configuration (`claude/state-templates/00-config.md` or the Track 2 config module), never constants.
- Persistent state lives in Layer D, never only in prompts. Memory changes are proposed → confirmed → logged.
- Unattended runs never execute HIGH actions. Same event never processed twice.

## Repo map
| Path | What |
|---|---|
| `claude/` | Track 1, Claude‑native package: `PROJECT_INSTRUCTIONS.md`, `skills/ea-*`, `scheduled-tasks/`, `state-templates/` |
| `evals/scenarios/T01..T22` | behavioural tests, registered in `tests.json` |
| `docs/` | superseded architecture versions, the master spec |
| `packages/ea-core/` | Track 2 service (does not exist until approved) |

## Conventions
- `todo.md`: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked on the owner.
- `progress.md`: append‑only, newest at top, sections Done / Verified / Not done / Blocked on / Next.
- `tests.json`: never `pass` without `last_run` and `ran_by`; `blocked` needs a note; keep `summary` counts current.
- Work batch: inspect code → inspect architecture → update todo → one component → tests → fix → docs → progress → small commit.
- Prose style in docs: no em or en dashes in anything that could be pasted into outbound mail; plain sentences.
- Identities seen in this environment: `titanarshian@gmail.com` (operator account), `aamirsawar123@gmail.com` (connected calendar), `sarah@stravion.ae` (connected mailbox), `ar@alirao.com` (principal, host unconfirmed). Confirm which backs an integration before wiring it.
