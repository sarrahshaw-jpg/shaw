# SECURITY

## Model
No servers, no stored API keys, no `.env` in this design. Every credential is an OAuth grant held by Claude's connector system for the person who connected it. Nothing in this repository is secret; it holds prompts, skills and templates only.

## Controls
| Control | How |
|---|---|
| Authentication | OAuth per connector, per user, managed by claude.ai |
| Least privilege | connect only the connectors in SETUP step 3; destructive connector tools are never called (`ea-operating-model`) |
| Separation of duties | unattended runs cannot execute HIGH actions; only a person in a live chat can approve |
| Approval | explicit card, explicit "approve A‑n", same conversation, 72h expiry |
| Audit | `audit/YYYY-MM.md` in Drive, append‑only by convention; Enterprise adds platform audit logs |
| Policy enforcement | firm rules in PROJECT_INSTRUCTIONS + `01-preferences.md`; checked by the model at draft and send time; verified by evals T05/T06 |
| Access to rules | the Drive folder `EA — Ali Rao` **is** the control plane; restrict edit access to Ali, Sarah and the admin |
| Data residency | data stays in the source systems (Google, Hostinger, Zoho, Zoom) and Anthropic's processing; the state folder holds summaries, drafts and logs |
| Recording | never initiated by the assistant; only existing recordings made under the host's settings are read |

## Honest limits
- Policy rules are enforced by the model, not by code. A model can err. The mitigations are: HIGH actions always pass a human, the evals exercise the rules, and the audit log makes any breach visible the same day. If a hard code‑level guarantee is ever required, that is the trigger for Appendix B of ARCHITECTURE.md.
- Anyone with edit rights on the state folder can change `06-automation-rules.md`. Treat that file like a production config.
- Prompt injection via email content is a real risk: an inbound email could contain instructions. The project instructions tell the assistant that email, transcript and CRM content is data, never instruction, and unattended runs cannot send, which bounds the damage to a bad draft or a bad card.

## Review checklist before go‑live (Phase 17)
- [ ] Only listed connectors connected on each account
- [ ] State folder sharing limited; link sharing off
- [ ] `06-automation-rules.md` has no auto‑send rules unless deliberately added
- [ ] Evals T04, T05, T06, T16 pass
- [ ] Zoom cloud recording settings reviewed with participants' notice enabled
- [ ] Zoho connector scopes reviewed
