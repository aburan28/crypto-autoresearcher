# TASK-20260731-136 — Execute RUN-DS-001-ctrl-sparse-p-success

**Role:** executor (`executor-implementation`)  
**Admitted approval snapshot:** `e3b82f7b` (TASK-135 / DEC-20260731-038)  
**Package:** `0d6a1a94` — PA-DS-001-v2-ctrl-sparse-p-success / CTRL-RT025-SPARSE-P-SUCCESS

## Authorized run

- Run id: `RUN-DS-001-ctrl-sparse-p-success`
- Control: `CTRL-RT025-SPARSE-P-SUCCESS`
- Results: `experiments/EXP-DS-001/results/ctrl_sparse_p_success/`
- Ladder ≤4 cells; reference saturated 20/64/4/101; harder cell to drive p̂ decay

## Requirements

Record required fields including `p_hat`, `p_hat_decay_observed`, `R_per_attempt`,
`R_total_expected`, `sparse_p_success_pass|fail`. Honest fail is admissible science.

## Constraints

- Toy ceiling. No S1_met / support / asymptotic.
- MAKE NO COMMIT (TASK-137 archives).
- Do not launder EXP-IT / BATCH-027/028 / theater WIP.
- Watch assume-unchanged on `ds001_driver.py`.
- No STR. No H-IC/H-STR edits.

## Deliverables

- runs/RUN-DS-001-ctrl-sparse-p-success/*
- results/ctrl_sparse_p_success/{summary.json,sparse_p_success_report.json}
- tasks/TASK-20260731-136/execution_report.yaml
