# TESTING

See `evals/README.md` and `evals/scenarios/`. 22 behavioural scenarios map to spec §21. Registry: `tests.json`.

Run order for first acceptance: T01, T03, T04, T05, T06, T16 (safety) → T07, T08, T09 (calendar) → T10, T11, T12, T13 (intelligence and CRM) → T14, T15, T18, T19, T20 (unattended behaviour) → T02, T17, T21, T22.

Never run T04, T09, T13 against a real counterparty. Use a test recipient, a Zoho sandbox, or stop at the card.
