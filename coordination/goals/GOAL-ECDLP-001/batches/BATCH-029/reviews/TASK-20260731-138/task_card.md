# TASK-20260731-138 — Validate RUN-DS-001-ctrl-sparse-p-success

**Role:** validator  
**Admitted run snapshot:** `9ac393ca` (TASK-137)  
**Approval gate:** `e3b82f7b` / DEC-20260731-038  
**Package:** `0d6a1a94`  
**Control:** CTRL-RT025-SPARSE-P-SUCCESS  
**Amendment:** PA-DS-001-v2-ctrl-sparse-p-success  

## Objective

Validate integrity of the committed SPARSE-P-SUCCESS run package against the approved control. Do not interpret S1_met / support / asymptotic.

## Read via git show at snapshot

- `git show 9ac393ca:experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-sparse-p-success/`
- `git show 9ac393ca:experiments/EXP-DS-001/results/ctrl_sparse_p_success/`
- Control/PA at `0d6a1a94`; approval at `e3b82f7b`

## Write scope ONLY

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-029/reviews/TASK-20260731-138/`

## Deliverables

- `validation_report.yaml`
- `receipt.json`

## Constraints

- Independent session; MAKE NO COMMIT
- Toy ceiling; quarantine; no EXP-IT / BATCH-027/028 launder
- H-IC-001 / H-STR-002 untouched; no STR; no lane death
- Recommended ledger targets: EV-DS-010 / DEC-20260731-039 (Coordinator authors)
