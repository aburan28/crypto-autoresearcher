# TASK-20260806-983eed: Execute EXP-ECTD-001

- **goal:** GOAL-ECTD-001
- **batch:** BATCH-fca4e2
- **role:** executor
- **state:** queued
- **priority:** 100
- **depends_on:** (none — ready now)
- **review_required:** True (dependent: TASK-20260806-5bc785 validator, via snapshot TASK-20260806-4455ac)
- **archived_by:** TASK-20260806-4455ac

## Objective

Implement the frozen `experiments/EXP-ECTD-001/specification.yaml` instrumentation
(meters, planted control, three null arms, matched rho/BSGS) and execute both
planned runs exactly as specified:

1. `RUN-ECTD-001-impl` — implement meters, planted control, three null arms;
   smoke test on one small class.
2. `RUN-ECTD-001-screen` — full `>=5`-class screen within the frozen budget.

## Frozen contract (do not deviate)

- `n_bit_range [40,56]`, `min_classes 5`, `min_class_size 64`,
  `isogeny_degrees_ell [2,3,5,7]`.
- Primary meters: `semaev_m3_relation_density`, `semaev_m4_relation_density`,
  `fb_decomposition_probability`, `groebner_solving_degree_d_reg`,
  `macaulay_rank_defect_at_first_fall`.
- Mandatory controls: `CTRL-OUTSIDE-CLASS`, `CTRL-DEGREE-PROFILE`,
  `CTRL-PERMUTATION`, `CTRL-PLANTED-OUTLIER`, `CTRL-RHO`, `CTRL-BSGS`,
  `CTRL-NO-CLASS-INVARIANT-ENDPOINT`.
- `decision_table` branches: `heavy_tail_hit`, `scoped_homogeneity`,
  `instrument_void`, `resource_incomplete` — pre-registered, not tunable
  post-hoc.
- Budget: `wall_clock_seconds_per_run 7200`, `total_cpu_hours 40`,
  `maximum_memory_gb 16`, `maximum_runs 2`.
- Seeds: `[201, 202, 203, 204, 205]`; extra seeds only on class-construction
  failure, recorded as infrastructure.

## Standing prohibitions

- Do not read homogeneity or a single outlier as a trapdoor.
- No trapdoor, break, or crypto-scale language anywhere in any artifact.
  `claim_tier` stays `toy`.
- Timeouts/crashes are infrastructure signals, never mathematical negatives
  (AGENTS.md rule 5).
- `CTRL-PLANTED-OUTLIER` failing means `instrument_void` — stop; do not
  continue to a homogeneity reading on a dead instrument.

## Deliverables

See `dispatch_queue.json` task entry for the exact `artifact_paths`. In
summary: driver code manifest, both run manifests + raw results, per-class
meter tables, planted/null-arm receipts, permutation stability table,
matched rho/BSGS receipts, stdout/stderr for both runs.

## Completion gate

- Both runs reach a terminal status.
- Reported `decision_branch` matches `spec.decision_table` exactly against
  the raw data.
- All seven controls present with pass/fail recorded.
- Full artifact policy satisfied (command, commit, environment, seeds,
  policy/model provenance, validity status) per `AGENTS.md`.
