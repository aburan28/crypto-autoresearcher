# EXP-PMA-001 Analysis

Experiment: EXP-PMA-001 ("Toy validation of the divisor-parity obstruction
predicate for ordinary PMA4 reciprocal-minor tables over k(t), char k != 2,
against independent brute-force matrix existence")

Hypothesis: H-PMA-001. Claim tier: **toy**. Authorization: DEC-20260906-9f036a
(re-approval that repaired a fabricated-citation defect in the original
TASK-20260727-011 handoff; see that decision and `specification.yaml`'s own
`status_enactment_note`).

This document reports observations only, per `agents/executor.md` item 13
("for heuristic-validation experiments, report the frozen prediction
reference and the comparison statistics only -- never a conclusion that the
heuristic is supported or refuted") and item 12 (an observation that does not
fit the prediction is preserved, not discarded). No conclusion about
H-PMA-001's status is drawn here; that is a Coordinator/Validator/Red-Team
matter for `/review-evidence`.

## Frozen prediction (verbatim reference)

`specification.yaml preregistered_prediction.formula`:

> `predicate_bruteforce_agreement = 1.0` exactly (every decided instance:
> OBSTRUCTED iff no matrix over k(t) exists);
> `nonvacuous_obstruction_count >= 1`; `false_obstruction_count = 0`;
> `false_compatibility_count = 0`; char-2 inputs refused or flagged.

## Measured comparison statistics (RUN-PMA4-001-d, `raw-result.json`)

| metric | measured value | frozen target |
| --- | --- | --- |
| `predicate_bruteforce_agreement` | 0.6538461538461539 (34/52 decided instances) | 1.0 exactly |
| `nonvacuous_obstruction_count` | 16 | >= 1 |
| `false_obstruction_count` | 0 | 0 |
| `false_compatibility_count` | 18 | 0 |
| `existence_witness_verification_failures` | 0 | 0 |

### Instance count reconciliation

- F_3: 18 instances (8 grid + 2 perturbed + 8 widened; widening triggered
  because the base 10-instance F_3 grid yielded zero non-vacuous
  obstructions), classification `agreement_compatible_confirmed` on all 18.
- F_5: 18 instances (8 grid + 2 perturbed + 8 widened; widening triggered
  for the same reason), classification `false_compatibility` on all 18.
- F_7: 10 instances (8 grid + 2 perturbed, no widening: 10/10 already
  `agreement_obstructed_confirmed`).
- Q: 6 instances (4 grid + 2 perturbed, no widening: 6/6 already
  `agreement_obstructed_confirmed`).
- Total instances in the agreement grid: 18 + 18 + 10 + 6 = 52.
- Degenerate-excluded instances in this grid: 0.
- `n_decided` = 52.
- `n_agreement` = (F_3: 18 `agreement_compatible_confirmed`) + (F_7: 10
  `agreement_obstructed_confirmed`) + (Q: 6 `agreement_obstructed_confirmed`)
  = 34.
- `predicate_bruteforce_agreement` = 34 / 52 = 0.6538461538461539. Matches
  the recorded metric exactly.
- `false_compatibility_count` = 18 (all from F_5).
- `false_obstruction_count` = 0.
- `nonvacuous_obstruction_count` = 10 (F_7) + 6 (Q) = 16. Matches.

The Groebner cross-check subsample (CTRL-PMA4-GROEBNER, 4 pre-declared
instances: 2 from the F_7 grid, 2 from the F_3 grid) is a separate,
non-overlapping-in-purpose measurement: all 4 compare as `agree` against the
independent decider (0 disagree, 0 undecided/skipped).

## Falsification-criterion classification (frozen, exactly as specified)

- **Direction 1 (soundness: OBSTRUCTED by predicate but a valid matrix
  exists)**: NOT falsified on this grid. `false_obstruction_count = 0`
  across all 52 decided instances.
- **Direction 2 (exact-classifier: NOT_OBSTRUCTED_BY_THIS_GATE but no matrix
  exists)**: **FALSIFIED**. 18 instances -- the entirety of the F_5 grid --
  are `false_compatibility`: Module A judges all three anchor-triple
  discriminants square in F_5(t) (predicate verdict
  `NOT_OBSTRUCTED_BY_THIS_GATE`), while Module B's independent constructive
  decider finds no sign combination among its 8 orientation branches
  reproduces all 16 prescribed principal minors (verdict `NOT_EXISTS`; every
  branch's closest mismatch count in `raw-result.json`'s `branch_log` is 1
  or 2 minors out of 16, never 0). Per `specification.yaml`'s own
  `falsification_criterion`, this falsifies H-PMA-001 as frozen (exact
  classifier on the grid), while the one-directional obstruction mechanism
  (direction 1) is not refuted by this direction and holds on this grid.
- **Non-vacuity**: non-vacuous. 16 instances (F_7: 10, Q: 6) are OBSTRUCTED
  with an independently reverified odd-valuation witness (Module A's
  `finite_valuations`/`valuation_at_infinity` certificate, disclosed per
  instance in `secondary_metrics.obstruction_witnesses` of
  RUN-PMA4-001-d's `raw-result.json`) and a brute-force `NOT_EXISTS`
  confirmation from Module B.

## Controls

- `CTRL-PMA4-GROUND-TRUTH`: PASS. `existence_witness_verification_failures
  = 0`; every EXISTS verdict (all 18 F_3 instances) carries a 16/16
  `witness_verifier.py` reverification (`witness_reverified_16_16: true`),
  and every NOT_EXISTS verdict (F_5's 18, plus any branch failures
  elsewhere) carries a complete 8-branch exhausted log or an explicit
  square-root-failure reason.
- `CTRL-PMA4-CHAR2`: PASS. F_2 and F_4 inputs are both refused by the
  predicate (`REFUSED_CHAR2`) in RUN-PMA4-001-a's calibration self-check;
  neither is ever scored `OBSTRUCTED`.
- `CTRL-PMA4-DEGENERACY`: PASS. The deliberate q_ij=0 calibration fixture
  branches to `DEGENERATE` in both Module A and Module B
  (RUN-PMA4-001-a); no instance in the actual executed grid (b/c) landed
  in the degenerate-exclusion category (`n_degenerate_in_grid = 0`,
  disclosed as an outcome, not engineered to be zero).
- `CTRL-PMA4-GROEBNER`: PASS. All 4 pre-declared subsample instances
  compare `agree` against the decider; 0 disagree.

## Success criterion

Per `specification.yaml`'s `success_criterion`, all five conjuncts are
required. `success_criterion_met = false` (RUN-PMA4-001-d): the exact-match
conjunct (`false_compatibility_count = 0`) is not met, because
`false_compatibility_count = 18`. All other conjuncts individually hold
(`false_obstruction_count = 0`; `nonvacuous_obstruction_count = 16 >= 1`;
`existence_witness_verification_failures = 0`; the char-2 and degeneracy
controls both pass).

## Scope and transfer-assumption disclosure

- Tested scope only: constant fields F_3, F_5, F_7, and Q; prescribed
  reciprocal-minor tables of the exact frozen form
  `p_S = (t+1)/(t+d_S)`; a single deterministic executor-chosen parameter
  box and grid-instance generation rule per field (disclosed in
  `implementation/grid_data.py`'s own module docstring: the specification
  pins the formula and field list but not literal `d_S` values, so this is
  a protocol-interpretation choice applied identically, never adjusted
  after runs began). No claim is made, or can be made from this run, about
  any other field, any other prescribed-table family, larger PMA sizes, or
  any generic/asymptotic behavior.
- F_3's parameter box has exactly one nonzero, non-1 element ({2}), so every
  F_3 grid instance in this execution is numerically identical (the same
  single prescribed table, generated 18 times under different instance
  labels `grid`/`perturbed`/`widened_grid`). This is disclosed as a genuine
  executability tension in the frozen contract for the smallest field (see
  `grid_data.py` docstring), not a defect introduced by this run; F_3's 18
  "instances" therefore constitute one distinct mathematical data point
  repeated, not 18 independent samples, and this materially discounts F_3's
  contribution to `predicate_bruteforce_agreement`'s numerator. This
  discount is disclosed here rather than adjusted into the metric, per the
  frozen-prediction-comparison rule (the metric is computed exactly as
  `specification.yaml` defines it; this note explains what it means).
- The direction-2 falsification is scoped to F_5 only among the four tested
  fields; F_3, F_7, and Q showed no `false_compatibility` instances in this
  grid. No claim is made about whether F_5's outcome is a field-specific
  artifact (e.g. interaction between F_5's small parameter box and the
  square-root/residual-class machinery) or a more general phenomenon; that
  would require a separate, explicitly designed follow-up, not an
  extrapolation from this toy grid.
- No ECDLP, relation, source-to-scalar, or standardized-curve computation
  was performed at any point, per `specification.yaml`'s stopping rules.
  `certificate.kind: none` throughout; no discrete-log or relation claim is
  made or implied.

## Anomalies and deviations

See `execution-report.yaml`'s `protocol_deviations` and `anomalies` fields
for the full, itemized list (driver_core.py passthrough addition, run_d.py
path-bug fix, secondary-metric additions, F_3's degenerate parameter box,
and the direction-2 falsification itself, which is recorded as an
observation here, not suppressed).
