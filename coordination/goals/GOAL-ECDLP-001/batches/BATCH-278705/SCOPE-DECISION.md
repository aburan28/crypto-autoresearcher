# BATCH-278705 scope decision — RC-46 amendment design only

Date: 2026-08-04
Goal: `GOAL-ECDLP-001`
Authority: `DEC-20260803-004`

## One bounded uncertainty

Can a new, versioned, reproducible amendment
`PA-IT-001-v3-rc46-repair-6` cure the immutable-path/provenance collision
identified after RC-45 while preserving the live controls required by
`DEC-20260803-004`?

The only work admitted here is the design and independent review of that
proposed amendment. This opening creates neither the amendment nor an
execution authorization.

## Binding inputs and immutability

- `DEC-20260803-004` is the authoritative next-action source.
- `PA-IT-001-v3-rc45-repair-5` and all RC-45 run, result, output, manifest,
  and provenance artifacts remain immutable and out of scope.
- The frozen RC-45 command permits only its historical
  `RUN-IT-001-rc45-smoke`/`RUN-IT-001-rc45-measure` paths. It is not executed,
  replayed, edited, or treated as authorization for a successor run here.
- `ledger/goals/GOAL-ECDLP-001/goal.yaml` and every historical goal checkpoint
  remain untouched during this opening. The future ledger archive alone may
  create its new checkpoint and update the goal head after actual reviews.
- `BATCH-c259e0` is excluded and unbound. It is not authority, input,
  precedent, or a redispatch target.

## Required future amendment content

The Idea Generator may write only the proposed successor amendment and
separate rationale, control, and provenance plans. They must specify:

1. unique future run IDs and distinct future run/output/provenance paths;
2. fresh `BATCH-278705` and newly allocated future execution-task provenance;
3. a live `CTRL-ANOMALOUS-TRACE1` control at bits 20 with an independently
   verifiable anomalous-trace-1 certificate and
   `C_special = ceil(8 * log2(p))`;
4. a nonempty `CTRL_NULL_IT_PLANT` edge ledger and a live
   `CTRL-NULL-PACKAGING-GATE`;
5. `dominated_by` and quantitative `sota_delta` fields on the future run
   deliverables; and
6. a gate that makes measure eligible only after a smoke package passes every
   live control.

No implementation, execution command, run directory, result, manifest, or
provenance record is created by this batch.

## Decision branches

- **Positive:** both independent design reviews pass every required gate. The
  later ledger archive may record only a design-stage disposition to consider
  a separately allocated Executor-admission batch. It does not admit an
  Executor now.
- **Revise:** either review identifies a concrete design defect. The later
  ledger archive records only the actual verdict and a revise disposition; a
  new amendment/review chain is required.
- **Inconclusive:** the proposal or review is incomplete, ambiguous, or blocked
  by a required policy. The later ledger archive records the limitation and
  does not admit an Executor.

## Claim and proof boundaries

This batch is design-only. It makes no run, evidence, hypothesis, ECDLP,
cryptanalytic, asymptotic, proof, cost, completion, or closure claim.
`proof_search_map` is not applicable: no theorem, asymptotic bound,
certificate family, reduction, or closure argument is proposed.

## Eligibility gates

1. The control plane must be snapshot-archived by `TASK-20260804-533c6c`.
2. The author may then propose (not freeze or execute)
   `PA-IT-001-v3-rc46-repair-6`.
3. The proposed amendment and all three plans must be snapshot-archived by
   `TASK-20260804-fdc6d7`.
4. Independent Reviewer `TASK-20260804-af8ec2` and independent Red Team
   `TASK-20260804-889042` must both report actual verdicts under
   `review-adversarial` at `xhigh`.
5. `TASK-20260804-79506c` may ledger-archive only actual review verdicts and
   design-stage evidence. It must not authorize an Executor unless both gates
   actually pass; otherwise its disposition is `revise` or `inconclusive`.
