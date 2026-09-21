# BATCH-044 input capsule

## Objective

Produce one new superseding amendment record for `EXP-IT-001` v3:
`PA-IT-001-v3-repair-4` that closes all remaining `RT-20260802-314` blockers
under `DEC-20260802-233`.

No implementation or run may occur under this batch.

## Authoritative inputs

- `ledger/decisions/DEC-20260802-233.yaml` and `ledger/evidence/EV-IT-005.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-043/tasks/TASK-20260802-316/synthesis.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-043/tasks/TASK-20260802-314/`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-043/tasks/TASK-20260802-315/`
- `experiments/EXP-IT-001/specification.v3.yaml`
- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc43-repair-3.yaml`
- `experiments/EXP-IT-001/amendments/` (read-only; historical overlays only)

## Mandatory closures

This repair must address all of the following:

1. **B1 — Explicit anomalous Smart calibration.** Recalibrate
   `C_special_smart` so that the anomalous-transfer `R_xfer < 0.7` criterion holds
   at the *pinned anomalous plant bit* under matched rho, and add an explicit
   supersession clause overriding `specification.v3.yaml`’s quadratic Smart charge
   where it conflicts with this calibration.

2. **B2 — Plant bit and rho pinning.** Pin the anomalous plant bit size used in
   transfer-gate accounting and restate `matched_rho` in terms that are frozen
   for the new contract.

3. **B3 — Density protocol restoration.** Restore or re-freeze the density abscissa
   to the pinned protocol used in the BATCH-036 closure with a justified justification
   in the control matrix and implementation manifest.

4. **B4 — Preserve already-closed, non-conflicting RC-43 fixes.** Keep in-force
   RC-43 fixes for command binding, transfer certificate fields, null-recompute
   manifest inclusion, and comparator wording where they do not conflict with B1–B3.

## Required amendment contents

Mechanism and test boundary; predictions; controls; metrics; deterministic
seeds; budgets; stopping and invalidation rules; success and falsification
criteria; exactly one future Executor command string; exact run IDs reserved
without claiming execution; exact artifact paths; memory/data accounting;
unexpected-observation policy; and Pareto fields with quantitative axes.

## Deliverables

Write exactly:

- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc44-repair-4.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-044/tasks/TASK-20260803-003/amendment-rationale.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-044/tasks/TASK-20260803-003/control-matrix.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-044/tasks/TASK-20260803-003/artifact-and-cost-plan.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-044/tasks/TASK-20260803-003/provenance.yaml`

No other file may be written by TASK-20260803-003.

