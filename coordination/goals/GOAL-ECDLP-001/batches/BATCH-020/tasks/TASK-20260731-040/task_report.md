# TASK-20260731-040 — Author PA-DS-001-v2-ctrl-unplanted

## Status

Completed (authoring). Snapshot archive is TASK-20260731-041.

## Inputs

- DEC-20260731-018 inconclusive; exact next_action CTRL-RT025-UNPLANTED
- RT-20260731-038 (RT038-B7; CTRL-RT025-UNPLANTED / PLANT-LIVE still required)
- EXP-DS-001 `specification.v2.yaml` (sha256 `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a`)
- Parent approval snapshot `65f3c82b` / DEC-20260731-022

## Deliverables

- `experiments/EXP-DS-001/amendments/v2_ctrl_unplanted.yaml` (`PA-DS-001-v2-ctrl-unplanted`)
- `experiments/EXP-DS-001/controls/CTRL-RT025-UNPLANTED.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/QUEUE-AMEND-20260731-003.md`
- This task report

## Control cell (smallest decisive)

| bits | B | m | seed |
|---|---|---|---|
| 20 | 64 | 4 | 101 |

Unplanted uniform (or sparse with success-probability accounting); same
backend id `ds001-v2-point-sum-membership+charged-units-v1`;
`smoothness_abort=false`; `relations_target=200` or honest resource stop;
plus live /4 plant without synthetic known-answer.

## Non-actions

- No edit to `specification.yaml` / `specification.v2.yaml` / v1 freeze blob
- No Executor run authorized by this task
- No full 54-cell matrix re-run
- No HEUR re-run
- No change to H-IC-001 or H-STR-002
- EV-DS-002 planted package remains operative until a later control ledger
