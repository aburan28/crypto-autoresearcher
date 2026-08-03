# TASK-20260731-072 — Author PA-DS-001-v2-ctrl-plant-contrast

## Status

Completed (authoring). Snapshot archive is TASK-20260731-073.

## Scope choice

Selected **CTRL-PLANT-CONTRASTIVE-F2** (RT070-B2 / RT047-B3) under SG-ECDLP-001.

**dominated_by vs pivot:** SG-ECDLP-002 / IDEA-20260731-008 is dominated by
finishing this residual — plant non-discriminative theater still blocks reading
H-DS-001. CI-IDENTITY / SPARSE-P-SUCCESS named deferred.

## Deliverables

- `experiments/EXP-DS-001/amendments/v2_ctrl_plant_contrast.yaml`
- `experiments/EXP-DS-001/controls/CTRL-PLANT-CONTRASTIVE-F2.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/SCOPE-DECISION.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/QUEUE-AMEND-20260731-008.md`
- `ledger/decisions/DEC-20260731-018.yaml`
- This task report

## Pass semantics (scientific)

`planted_bug_detected` may be true only if plant-OFF `null_gate_f2_shape` is
false AND plant-ON is true. Default cell 20/64/4/101 is known F2_eligible on
plant-OFF from EV-DS-006 — Executor may hunt a ≤6-cell ladder (suggested
16/128/{4,5}/{102,103,101} middle_band candidates under composing) or report
honest `contrastive_fail` (not infrastructure failure; not lane death).

## Cycle cap

RC-23: one amendment/review cycle. REVISE at TASK-074 ⇒ BATCH-023 non-execution.

## Non-actions

- No Executor run authorized
- No edit to specification.v2.yaml / rejected BATCH-021 freeze / theater-r2 blobs
- No H-IC-001 / H-STR-002 edits; no STR reopen
- Unauthorized BATCH-021 theater WIP ignored
