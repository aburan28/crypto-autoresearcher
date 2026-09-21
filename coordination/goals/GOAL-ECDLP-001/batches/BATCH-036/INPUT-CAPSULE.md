# BATCH-036 input capsule — relay verbatim

## Objective

Produce one new amendment record for the second gated `EXP-IT-001` v3 repair.
Do not edit `specification.v3.yaml`, either prior amendment, implementation
code, or any run/result artifact. Do not implement or run the experiment.

## Authoritative inputs

- `ledger/goals/GOAL-ECDLP-001.yaml`, especially its exact `next_action`.
- `ledger/decisions/DEC-20260801-002.yaml` and `ledger/evidence/EV-IT-002.yaml`.
- BATCH-030 Validator and Red Team artifacts under
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/reviews/`.
- `experiments/EXP-IT-001/specification.v3.yaml`.
- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc30-repair-1-to-7.yaml`.
- `DEC-20260802-211` and `CORR-20260802-002`.

## Six non-negotiable repairs

1. Preserve the frozen MOV cost or formally replace it with an end-to-end
   field-DLP-inclusive formula, including the k=1 `~2*sqrt(N*)` term, and use
   an actually anomalous trace-1 curve for the anomalous positive control.
2. Define a genuine certificate-bearing isogeny transfer control on a
   non-special instance. The certificate must evaluate the pullback and the
   planted walk must end at a non-special j-invariant.
3. Pre-register one live synthetic certificate-bearing sub-0.7 null claim and
   require `CTRL-NULL-PACKAGING-GATE` to reject it; persist a raw per-edge ledger
   for `CTRL-NULL-IT-PLANT` sufficient for independent recomputation.
4. Put `dominated_by` and a quantitative `sota_delta` across time, memory, and
   data/query in every deliverable. Use `not_applicable` only with an explicit
   non-solver scope.
5. Specify a density scan over an exact bit window and prime-selection rule
   that admits `N* | p^k-1` for `k>=2` or an actual trace-1 class; pre-register
   sample sizes, estimands, multiplicity handling, and 95% confidence intervals.
6. Declare every implementation source file and require the future pre-run
   snapshot to archive the exact code, amended contract, controls, and hashes.

## Required amendment contents

Mechanism and test boundary; predictions; controls; metrics; deterministic
seeds; budgets; stopping and invalidation rules; success and falsification
criteria; exact commands planned for a future Executor; exact run IDs reserved
without claiming execution; exact artifact paths; memory/data accounting;
unexpected-observation policy; and Pareto fields.

The amendment must state whether it keeps or replaces `C_special_MOV`. It may
not leave both branches available to a future Executor. It must distinguish an
anomalous trace-1 attack from an embedding-degree-1 MOV endpoint.

## Deliverables

Write exactly:

- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc36-repair-2.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-036/tasks/TASK-20260802-242/amendment-rationale.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-036/tasks/TASK-20260802-242/control-matrix.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-036/tasks/TASK-20260802-242/artifact-and-cost-plan.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-036/tasks/TASK-20260802-242/provenance.yaml`

No other file may be written. No implementation, run, state transition,
knowledge promotion, support, rejection, SOTA, closure, or breakthrough claim.
