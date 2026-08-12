# TASK-20260731-115 — Execute RUN-DS-001-ctrl-ci-identity

**Role:** executor (`executor-implementation`)  
**Admitted approval snapshot:** `405b8422` (TASK-114 / DEC-20260731-033)  
**Package:** `07232da8` — PA-DS-001-v2-ctrl-ci-identity / CTRL-RT025-CI-IDENTITY

## Authorized run

- Run id: `RUN-DS-001-ctrl-ci-identity`
- Control: `CTRL-RT025-CI-IDENTITY`
- Results: `experiments/EXP-DS-001/results/ctrl_ci_identity/`
- Primary cell: bits=20, B=64, m=4, seed=101 (optional secondary 16/128/4/102)

## Requirements

Record required fields including `ci_of_cost_identity_R`, `ci_identity_pass|fail`.
Honest `ci_identity_fail` is admissible science, not infrastructure failure.

## Constraints

- Toy ceiling. No S1_met / support / asymptotic.
- MAKE NO COMMIT (TASK-116 archives).
- Do not launder EXP-IT / BATCH-027 / theater WIP.
- Watch assume-unchanged on `ds001_driver.py`.
- No STR. No H-IC/H-STR edits.

## Deliverables

- `experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-ci-identity/manifest.json` (+ run records)
- `experiments/EXP-DS-001/results/ctrl_ci_identity/summary.json`
- `experiments/EXP-DS-001/results/ctrl_ci_identity/ci_identity_report.json`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/tasks/TASK-20260731-115/execution_report.yaml`
