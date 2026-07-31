# TASK-20260731-094 — Author / restore PA-DS-001-v2-ctrl-structure-null-r2

## Status

Completed (authoring + DEC-025 restore). Snapshot archive is TASK-20260731-095.

## Scope choice

Selected **CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2** (RT079-B3 / RT070-B3) under
SG-ECDLP-001 on **fresh `-r2` paths**.

**dominated_by vs pivot:** SG-ECDLP-002 / IDEA-20260731-008 is dominated by
finishing this residual. BATCH-024 failed on `abandoned_before_archive` stubs —
integrity failure, not residual discharge. `R_null≪1` still blocks structure
reading of H-DS-001.

## Race correction

Commit `1aa3b957` (DEC-024) cancelled the `-r2` package and pivoted to EXP-IT.
**DEC-20260731-025** supersedes that fork for execution and restores
`status: executable` content. EXP-IT/H-IT at `303ae797` are not laundered as
this batch's official freeze. Abandoned BATCH-024 stubs at `32165e30` untouched.

## Executable markers

- `status: executable` on PA and CTRL (not abandoned/cancelled stubs)
- Encodes `structure_null_ok` as `R_null >= 0.9`
- Encodes `structure_gate_eligible`, `structure_direction_pass`, `structure_direction_fail`
- Honest `structure_direction_fail` when advantageous R holds but R_null stays `< 0.9`

## Artifacts

- `experiments/EXP-DS-001/amendments/v2_ctrl_structure_null_r2.yaml`
- `experiments/EXP-DS-001/controls/CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2.yaml`
- `ledger/decisions/DEC-20260731-025.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/QUEUE-AMEND-20260731-013.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/SCOPE-RESTORE-DEC025.md`
- this report

## Pass semantics (for Executor if later APPROVED)

`structure_direction_pass` only if `R < 0.5` AND `R_null >= 0.9` (or documented
rising ladder toward 1). Else honest `structure_direction_fail` (not infra; not
lane death).

No run authorized by this task. Claim ceiling: toy.
