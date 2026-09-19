# T14 Duplicate prevention in scheduled sweep
Setup: run the sweep prompt twice within the hour with the same unread email.
Must: second run skips the email because its ID is in `07-processed.md`; no second approval card.
