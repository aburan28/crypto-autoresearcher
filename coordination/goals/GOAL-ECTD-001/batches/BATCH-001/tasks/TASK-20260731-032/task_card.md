# TASK-20260731-032: Ledger-archive BATCH-001: evidence, decision, activate goal

- **goal:** GOAL-ECTD-001
- **batch:** BATCH-001
- **role:** coordinator
- **state:** queued
- **priority:** 50
- **depends_on:** TASK-20260731-031
- **review_required:** False
- **archived_by:** TASK-20260731-032

## Objective

Archive the independent review, a scoped literature/ideation evidence record, the batch decision (which IDEA records are admitted to experiment design), activate GOAL-ECTD-001 (draft→active) if the literature gate is satisfied, and set exactly one next action.

## Completion gate

- Evidence, decision, and goal records preserve the exact reviewed scope.
- Verified ledger commit records exactly one next action.
- GOAL-ECTD-001 batch_checkpoints includes BATCH-001 with decision and evidence IDs.
