# TASK-20260731-028: Archive ECTD literature snapshot

- **goal:** GOAL-ECTD-001
- **batch:** BATCH-001
- **role:** coordinator
- **state:** queued
- **priority:** 90
- **depends_on:** TASK-20260731-027
- **review_required:** False
- **archived_by:** TASK-20260731-028

## Objective

Regenerate knowledge/INDEX.md, then commit and verify the exact KN-LIT upgrades/entries and sources note before ideation or review reads them.

## Completion gate

- Git verifies parent, paths, hashes, task ID, and reachable commit; INDEX.md is regenerated and covered by the receipt.
