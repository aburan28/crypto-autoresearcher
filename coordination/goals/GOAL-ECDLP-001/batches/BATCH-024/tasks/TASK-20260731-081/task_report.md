# TASK-20260731-081 — Author PA-DS-001-v2-ctrl-structure-null

## Status

Completed (authoring). Snapshot archive is TASK-20260731-082.

## Scope choice

Selected **CTRL-NULL-OBJECT-STRUCTURE-DIRECTION** (RT079-B3 / RT070-B3) under SG-ECDLP-001.

**dominated_by vs pivot:** SG-ECDLP-002 / IDEA-20260731-008 is dominated by
finishing this residual — `R_null≪1` still blocks structure reading of H-DS-001
after plant-contrast (EV-DS-007). CI-IDENTITY / SPARSE-P-SUCCESS named deferred.

## Deliverables

- `experiments/EXP-DS-001/amendments/v2_ctrl_structure_null.yaml`
- `experiments/EXP-DS-001/controls/CTRL-NULL-OBJECT-STRUCTURE-DIRECTION.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-024/SCOPE-DECISION.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-024/QUEUE-AMEND-20260731-009.md`
- `ledger/decisions/DEC-20260731-020.yaml`
- This task report

## Pass semantics (scientific)

`structure_direction_pass` / any structure credit only if `R < 0.5` AND
`R_null ≥ 0.9` (or documented rising ladder toward 1) under null-object packaging.
Primary cell 16/128/4/102 is known `R_null≪1` from EV-DS-007 — Executor may hunt
a ≤6-cell harden ladder or report honest `structure_direction_fail` (not
infrastructure failure; not lane death; not reject_scoped).

## Cycle cap

RC-24: one amendment/review cycle. REVISE at TASK-083 ⇒ BATCH-024 non-execution.

## Non-actions

- No Executor run authorized
- No edit to specification.v2.yaml / rejected BATCH-021 freeze / theater-r2 / plant-contrast blobs
- No H-IC-001 / H-STR-002 edits; no STR reopen
- Unauthorized BATCH-021 theater WIP ignored
