# BATCH-468520 checkpoint

- experiment: EXP-CRYPTO-9225d2 (`goal_id` remains null; GOAL-CRYPTO-001 is context only)
- decision: DEC-20260912-be822c
- opening snapshot: TASK-20260912-d2eee8 (Coordinator-only; not a dispatch-queue producer)
- base parent: `b967e055f6ba9f59d278d64c35b1664fd2bc3759`
- status: opening authority recorded; independent review not yet run
- scientific_execution_authorized: false (unchanged)

## Ranked next action

Independent implementation re-review of the repaired EXP-CRYPTO-9225d2
tree. Owed by DEC-20260912-34c82d, BATCH-53f590, and MSG-20260912-2c3feb.
Repair of C6/C9/C11/C12 is on main (`TASK-20260912-f821b2` /
`TASK-20260912-688e64`). TASK-20260912-c08c1b later landed documentation
follow-ups; live hashes differ from the 53f590 snapshot. Reviewer binds
current HEAD bytes.

`scientific_execution_authorized` stays false. Two hosts, independent
checker authorship, fixtures, cgroup delegation, and the locked 40-job
plan remain undischarged. Coordinator does not implement or execute.

## Queue

Dispatchable tasks in `coordination/design/BATCH-468520/dispatch_queue.json`:

1. TASK-20260912-87064e — Validator, review-adversarial / xhigh, independent session, maximum_runs: 0.
2. TASK-20260912-875c15 — Coordinator snapshot of the review report (depends on 87064e).

Opening snapshot TASK-20260912-d2eee8 binds the authority records of this
batch. It is completed in the same Coordinator session that opened the
batch. It is not a queue producer: the dispatcher assigns every non-archive
task to exactly one archive, and the opening records are not a producer
artifact set.

A later ledger DEC after the review may close or refuse the ffb734
findings. That later DEC still must not set scientific_execution_authorized
true unless spec admission gates are separately discharged.

## Live implementation hashes at opening (recompute at review time)

These are the current `origin/main` / HEAD bytes the reviewer must bind.
Do not use BATCH-53f590 `TASK-20260912-688e64` hashes; they are superseded.

- `experiments/EXP-CRYPTO-9225d2/implementation/arithmetic.py`: `f46b5a5a1109eb3b320267679c1273709ae4969310410758f0279b0e5a3142a6`
- `experiments/EXP-CRYPTO-9225d2/implementation/rho.py`: `d5f4ff8a313a18c2c9a5777a0e2568d4ba5cd714112de5d21e0d7d5614557245`
- `experiments/EXP-CRYPTO-9225d2/implementation/driver.py`: `79c1527090056de2c7bd669338d7d232f804bf284085534c5ac8958240fb127f`
- `experiments/EXP-CRYPTO-9225d2/implementation/repair-report.yaml`: `0f29d730ddfa6dc22194c7448b194252aa12dd2b75c3620ee1653b69d0a1d3d3`
- `experiments/EXP-CRYPTO-9225d2/specification.yaml`: `751d812547b24d37fca2835f72b97c12dd78112d4e1d09803cc547aaad27066b`
