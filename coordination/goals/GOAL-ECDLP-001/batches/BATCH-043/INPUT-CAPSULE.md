# BATCH-043 input capsule — relay verbatim

## Objective

Produce one new superseding amendment record for `EXP-IT-001` v3 that closes
all RT-20260802-244 blocking and major findings against
`PA-IT-001-v3-rc36-repair-2`. Do not edit `specification.v3.yaml`, any prior
amendment, implementation code, or any run/result artifact. Do not implement
or run the experiment.

## Authoritative inputs

- `ledger/decisions/DEC-20260802-212.yaml` and `ledger/evidence/EV-IT-003.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-036/tasks/TASK-20260802-244/verdict.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-036/tasks/TASK-20260802-244/red-team-report.md`
- `experiments/EXP-IT-001/specification.v3.yaml`
- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc36-repair-2.yaml`
- Prior overlays under `experiments/EXP-IT-001/amendments/` (read-only)
- BATCH-030 reviews under
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/reviews/`

## Mandatory closures (RT-244)

1. **B1 — Split C_special limbs.** Freeze `C_special_smart` as the anomalous
   (CTRL-ANOMALOUS-TRACE1) pass threshold with disclosed Smart-scale cost
   (~O(log p) / calibrated Smart ops). Freeze `C_special_field_DLP` only for
   MOV / embedding comparator columns. Anomalous pass threshold must use
   Smart limb, never field-DLP `ceil(2*sqrt(N*))`.
2. **B2 — Quantitative Pareto.** Every deliverable carries `dominated_by` and
   explicit three-axis `sota_delta` with numeric or `not_applicable` values for
   time, memory, and data/query versus matched Pollard rho, plus an explicit
   non-solver scope sentence when using `not_applicable`.
3. **B3 — Single binding command.** Freeze exactly one command string and one
   entrypoint. Delete any language permitting Executor CLI flag adjustment.
   Any other invocation is `contract_invalid`.
4. **M1 — Transfer certificate.** Require `start_j_speciality: nonspecial` and
   recovered path is reverse of planted walk, plus existing end-nonspecial /
   pullback / relation-reverified fields.
5. **M2 — Null recompute script.** Include
   `recompute_null_plant_from_ledger.py` in `implementation_archive_manifest`
   (path declared; script may be authored before a future pre-run snapshot) or
   make its absence an R-FIX invalidation blocking `completed_valid`.
6. **M3 — Comparator wording.** Ban old MOV formula only as anomalous /
   transfer pass threshold; allow labeled comparator column for k>=2.

Also preserve the six BATCH-030 / BATCH-036 capsule intents already present in
rc36 where they do not conflict with the above (trace-1 plant typing, genuine
non-special transfer, live null packaging gate + raw ledger, density CI,
pre-run archive list).

## Required amendment contents

Mechanism and test boundary; predictions; controls; metrics; deterministic
seeds; budgets; stopping and invalidation rules; success and falsification
criteria; exactly one future Executor command string; exact run IDs reserved
without claiming execution; exact artifact paths; memory/data accounting;
unexpected-observation policy; and Pareto fields with quantitative axes.

## Deliverables

Write exactly:

- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc43-repair-3.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-043/tasks/TASK-20260802-312/amendment-rationale.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-043/tasks/TASK-20260802-312/control-matrix.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-043/tasks/TASK-20260802-312/artifact-and-cost-plan.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-043/tasks/TASK-20260802-312/provenance.yaml`

No other file may be written. No implementation, run, state transition,
knowledge promotion, support, rejection, SOTA, closure, or breakthrough claim.
