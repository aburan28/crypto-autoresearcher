# TASK-20260731-094 — Author PA-DS-001-v2-ctrl-structure-null-r2

## Status

Completed (authoring). Snapshot archive is TASK-20260731-095.

## Scope choice

Selected **CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2** (RT079-B3 / RT070-B3) under
SG-ECDLP-001 on **fresh `-r2` paths**.

**dominated_by vs pivot:** SG-ECDLP-002 / IDEA-20260731-008 is dominated by
finishing this residual. BATCH-024 failed on abandoned stubs (DEC-022), not by
discharging RT079-B3. Uncommitted EXP-IT WIP is not official.

## Executable markers (anti-stub)

- `status: executable` on PA and CTRL (not `abandoned_before_archive`)
- Encodes `structure_null_ok` as `R_null >= 0.9`
- Encodes `structure_gate_eligible`, `structure_direction_pass`, `structure_direction_fail`
- Does **not** edit abandoned BATCH-024 stub blobs at 32165e30

## Deliverables

- `experiments/EXP-DS-001/amendments/v2_ctrl_structure_null_r2.yaml`
- `experiments/EXP-DS-001/controls/CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/SCOPE-DECISION.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/QUEUE-AMEND-20260731-011.md`
- `ledger/decisions/DEC-20260731-023.yaml`
- This task report

## Pass semantics

`structure_direction_pass` only if `R < 0.5` AND `R_null >= 0.9` (or documented
rising ladder toward 1). Else honest `structure_direction_fail` (not infra; not
lane death; not reject_scoped).

## Cycle cap

RC-25: one amendment/review cycle. REVISE at TASK-096 ⇒ BATCH-025 non-execution.

## Non-actions

- No Executor run authorized
- No edit to abandoned stubs / specification.v2.yaml / EXP-IT WIP
- No H-IC-001 / H-STR-002 edits; no STR reopen
