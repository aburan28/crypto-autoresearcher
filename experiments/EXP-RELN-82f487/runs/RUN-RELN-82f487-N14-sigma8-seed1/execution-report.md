# Execution report: RUN-RELN-82f487-N14-sigma8-seed1

Cell: rung 2^14 (N=16657, p=16649), curve_seed=101 (curve index j=1),
base_seed=201, training_seed=301, sigma=1/8 (0.125). All five arms, both
model classes (gnn, trees), both feature regimes (F0, F1). Label-permutation
null (training_seed 301 only, per spec). See `implementation.md` for
deviations (no torch/sklearn/xgboost/lightgbm installed; hand-written,
gradient-verified GNN and GBT).

## Blocking gates

- Reproduction fixtures: **ALL PASS** on every arm (closed-form total-check
  deviation exactly 0; sigma=1 slice lambda=rho=1.0 exactly; grammar
  reproduction fixture exact-match true on every arm).
- Static leak audit: **PASS** on real feature/model modules; **CORRECTLY
  REJECTS** the planted-leak diagnostic (forbidden import + forbidden
  identifier both detected). See `leak_audit.json`, `planted_leak_diagnostic.json`.
- Label-permutation null: **NO LEAK** (per spec's own wording, "a lift
  ABOVE band is a leak" -- checked per arm/regime/class; several cells sit
  BELOW band, which is not a leak per the frozen definition, only recorded).
- Canary (E/log-interval): **NO LEAK** (every lambda/rho below the upper
  band bound on every regime/class).
- Z/N-interval positive control: **PASS** for both classes at both regimes
  (lambda = rho = 7.996, ceiling 8.0, half-ceiling threshold 4.0).
- **E/random vs Z/N-random pipeline-fault check: FAILED for regime F1,
  class gnn.** rho(E/random)=1.031, rho(Z/N-random)=1.110, difference
  0.079 > tolerance (band half-width) 0.064. Z/N-random (F1, gnn) also sits
  ABOVE its own selection-null band (1.110 vs upper bound ~1.064). F0 and
  the trees class in F1 do NOT show this fault (F0: diff 0.030 and 0.002,
  both within tolerance 0.064).

Per specification.yaml's stopping_rules ("Stop the run if E/random and
Z/N-random disagree beyond band at any rung"), this is a BLOCKING, in-protocol
stop condition. It is reported plainly, not discarded or narrowed away: the
F1 regime's cells are not readable as decided evidence until this is
investigated (most likely candidate, recorded as a hypothesis for the
investigation, not asserted as fact: F1's base-summary features literally
include a histogram of D's own x-values, which on Z/N-random gives the GNN
direct access to which residues are "close to" D-derived structure --
exactly the "lookup capacity" mechanism the hypothesis record's H2 predicts
and the spec says must be subtracted, not that it should stay in-band by
itself; whether 0.079 vs tolerance 0.064 is a real fault or a boundary
artifact of only 1000 null draws needs a second seed to tell apart).
Because the frozen text does not scope this rule to "F1 only," the
conservative, non-cherry-picking reading is that the WHOLE cell's
interpretation is blocked pending audit, even though F0 alone looks clean.

## Overall verdict for this cell

`all_blocking_gates_pass = false` (due to the F1 pipeline-fault item above).
**Branch classification: INCONCLUSIVE** per specification.yaml's
`decision_paths.inconclusive` (pipeline fault) -- not a negative_observation,
not evidence for or against H-RELN-10ad6b, per AGENTS.md rule 3 and this
contract's own falsification_criterion ("a pipeline fault ... is inconclusive
and is never evidence against the hypothesis or any heuristic").

Independent of that gate, and reported for completeness/preservation (not as
a decided result): even ignoring the F1 pipeline-fault flag, a SINGLE rung
(2^14) can never fit the log-log decay slope the contract's primary metric
needs (that requires >= 2 rungs); this cell alone could at most say whether
E/x-interval's excess sits inside or outside the selection-null band at
THIS one rung, which it does for both classes and both regimes (see numbers
below) -- consistent with, but not proof of, the predicted branch, and
equally consistent with a small alive excess at the smallest rung.

## Measured numbers (E/x-interval, the primary object)

| regime | class | rho excess over null | lambda excess over null | inside band? |
|---|---|---|---|---|
| F0 | gnn   | +0.0561 | +0.0281 | yes/yes |
| F0 | trees | +0.0205 | -0.0035 | yes/yes |
| F1 | gnn   | -0.0011 | +0.0106 | yes/yes |
| F1 | trees | +0.0205 | -0.0035 | yes/yes |

GNN-minus-trees difference (E/x-interval): F0 rho_diff=+0.0356,
lambda_diff=+0.0317; F1 rho_diff=-0.0216, lambda_diff=+0.0141 -- both within
the selection-null band half-width at this rung (no replicated,
non-shrinking positive difference can be claimed from one rung/one seed).

## Cost instrumentation (measured, this machine, this implementation)

c_f (feature computation + a linear-probe inference proxy, NOT the full
trained GNN/tree inference cost -- see deviation note below) ~= 1.45e-5 s/target
~= 25.3 point-addition equivalents; Theta(B) lookup ~= 1.98e-5 s/target ~=
34.4 point-addition equivalents; c_f / (B lookups) = 0.53 < 1, so H3's
falsification condition ("c_f / (B lookups) >= 1 at every rung") is NOT
triggered at this one rung -- consistent with H3, not proof of it (one rung,
one implementation, one machine, never transferred).

DEVIATION: the c_f measurement used a placeholder linear "inference" step
(`feats.sum(axis=1)`) as a fast proxy for the trained model's own forward
pass, because isolating a single-target GNN forward pass from the batched
autodiff graph was out of scope for this pass; feature computation
dominates the measured time in this implementation regardless, but the
number is not a full apples-to-apples c_f for the trained GNN specifically.

## What ran vs what did not (this session)

Completed: Stage 0 (leak audit + planted-leak diagnostic), Stage 1 fixtures
(inline per arm), the full priority-2 cell (rung 2^14, 1 curve, 1 base seed,
1 training seed, sigma=1/8, all 5 arms, both classes, both regimes,
label-permutation null), Stage 5 cost instrumentation (one measurement,
E/x-interval arm).

NOT run (named concretely, not silently omitted): the shuffled-seed
determinism re-run (script `source/run_determinism.py` is written and ready
but was not executed this session -- see `determinism_rerun.json`);
sigma=1/32; curves/base seeds/training seeds 2 and 3 (the remaining 26 of 27
replicates per cell); rungs 2^16, 2^18, 2^20, 2^24; per-target
slice-membership/permutation-importance/partial-dependence tables (recorded
as `not_run` in `handoff/*.csv`, since the run is inconclusive and these
tables would document a null in any case per spec).

## Wall-clock

Main cell (all 5 arms, both classes, both regimes, label-permutation null):
2454.6 seconds (~41 minutes), measured by the driver's own wall-clock log
(`stdout.log`, `run_log.txt`). Cost instrumentation: <5 seconds. Stage 0:
<1 second. Total measured wall-clock this session for THIS run:
approximately 41 minutes of compute (excluding code-authoring time).
