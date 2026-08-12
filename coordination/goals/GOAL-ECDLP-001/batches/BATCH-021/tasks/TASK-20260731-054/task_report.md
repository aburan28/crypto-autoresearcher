# TASK-20260731-054 — Author PA-DS-001-v2-ctrl-theater-repair

## Status

Completed (authoring). Snapshot archive is TASK-20260731-055.

## Inputs

- DEC-20260731-012 inconclusive; exact next_action BATCH-021 theater repair
- RT-20260731-047 required_controls (PLANT-INDEPENDENT, RHO-CALIB, NULL-SPLIT;
  deferred CI-IDENTITY, SPARSE-P-SUCCESS)
- EXP-DS-001 `specification.v2.yaml` (sha256 `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a`)
- Parent approval snapshot `65f3c82b` / DEC-20260731-003
- Prior control `CTRL-RT025-UNPLANTED` / EV-DS-003 (not superseded)

## Deliverables

- `experiments/EXP-DS-001/amendments/v2_ctrl_theater_repair.yaml` (`PA-DS-001-v2-ctrl-theater-repair`)
- `experiments/EXP-DS-001/controls/CTRL-RT025-PLANT-INDEPENDENT.yaml`
- `experiments/EXP-DS-001/controls/CTRL-RT025-RHO-CALIB.yaml`
- `experiments/EXP-DS-001/controls/CTRL-RT025-NULL-SPLIT-COMPOSITION.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/QUEUE-AMEND-20260731-005.md`
- `ledger/decisions/DEC-20260731-014.yaml`
- This task report

## Co-required controls (this batch)

| Control | Residual |
|---|---|
| CTRL-RT025-PLANT-INDEPENDENT | RT047-B3 echo tautology |
| CTRL-RT025-RHO-CALIB | hardcoded rho_calib=1.0 |
| CTRL-RT025-NULL-SPLIT-COMPOSITION | null_split asymmetry / destroy parameter |

Default cell: bits=20, B=64, m=4, seed=101.

## Deferred (named, not executed in BATCH-021 run)

- CTRL-RT025-CI-IDENTITY
- CTRL-RT025-SPARSE-P-SUCCESS

## Non-actions

- No edit to `specification.yaml` / `specification.v2.yaml` / v1 freeze blob
- No Executor run authorized by this task
- No full 54-cell matrix re-run
- No HEUR re-run
- No change to H-IC-001 or H-STR-002
- EV-DS-002 / EV-DS-003 remain immutable prior records
