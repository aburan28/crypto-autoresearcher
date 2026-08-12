# TASK-20260731-076 — Executor (ADMITTED)

**Status:** running (admitted)  
**Approval:** TASK-20260731-075 `APPROVED` @ `badafcdf80aaaa2d7fabb5824fd35afc4fbccb6b`  
**Amend snapshot:** `f41fd196`  
**Run id:** `RUN-DS-001-ctrl-plant-contrast`  
**Control:** `CTRL-PLANT-CONTRASTIVE-F2`

## Objective

Execute plant-contrastive control. Interpret nothing.

Credit `planted_bug_detected` only if plant-OFF `null_gate_f2_shape` false AND plant-ON true. Default cell 20/64/4/101 is known non-discriminative (EV-DS-006) — hunt ≤6-cell ladder or report honest `contrastive_fail`.

## Constraints

- MAKE NO COMMIT (TASK-077 archives)
- Prefer hash-object staging if `ds001_driver.py` is assume-unchanged
- Do not launder BATCH-021 theater WIP
- No H-IC-001 / H-STR-002 edits; toy ceiling
- Do not edit specification.v2.yaml / theater-r2 / rejected freezes

## Deliverables

See handoff `ledger/handoffs/TASK-20260731-076.yaml`.
