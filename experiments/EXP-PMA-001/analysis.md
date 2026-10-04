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

---

## Coordinator addendum (2026-09-07)

Recorded during `/review-evidence` for EXP-PMA-001, per `EV-PMA-fbdd4c` and
`DEC-20260907-90a00d`. This section is appended, not a rewrite: nothing
above this line is edited. It reconciles the original Executor report above
with two independent reviews (`VAL-20260907-ae3832`, verdict `passed`;
`RT-20260907-0df70c`, red-team, did not read the validator report) and two
corrections (`CORR-20260907-ae8418`, sample-count/box-collision/dead-widening
disclosure; `CORR-20260907-f41219`, dirty-code invalidation-clause scope
clarification). Unlike the Executor's report above, this addendum draws
Coordinator conclusions, per `agents/coordinator.md`.

### Observation

Both statistical bases for the agreement metrics, side by side. The
labeled-instance basis is exactly as originally committed by
`RUN-PMA4-001-d`/`raw-result.json`; the distinct-instance basis is
`CORR-20260907-ae8418`'s correction, computed by grouping each instance's
full `d_values` dict (no rerun), independently verified twice by the
Coordinator and matching `RT-20260907-0df70c`'s own figures exactly both
times.

| metric | labeled-instance basis | distinct-instance basis |
| --- | --- | --- |
| `n_decided` | 52 | 14 (F_3:1, F_5:5, F_7:3, Q:5) |
| `n_agreement` | 34 | 9 (F_3:1 + F_7:3 + Q:5) |
| `predicate_bruteforce_agreement` | 34/52 = 0.6538461538461539 | 9/14 = 0.6428571428571429 |
| `nonvacuous_obstruction_count` | 16 (F_7:10 + Q:6) | 8 (F_7:3 + Q:5) |
| `false_compatibility_count` | 18 (all F_5) | 5 (all F_5's 5 distinct tables) |
| `false_obstruction_count` | 0 | 0 (unaffected under either basis) |

Both reviews independently reproduced these numbers from raw data using
fresh, from-scratch code rather than trusting the committed aggregation:
the Validator reclassified all 52 labeled instances directly against
`parity_predicate.py`/`existence_decider.py` (0 mismatches against the
stored `classification` field); the Red Team additionally ran two more
algorithmically distinct, from-scratch methods on F_5 grid instance 0 that
import neither module -- a brute-force polynomial-square-root search over
`GF(5)[t]`, and an unconstrained (no WLOG diagonal-conjugation
normalization) 12-unknown, 11-equation Groebner basis computation over the
algebraic closure of `F_5(t)`, which returned the trivial ideal
(`basis = [1]`): no 4x4 matrix realization exists even over the algebraic
closure of `F_5(t)`, a strictly stronger statement than "no matrix over
`F_5(t)`".

### Comparison

**Direction 1 (necessary-condition obstruction mechanism: an odd valuation
is fatal to existence).** Predicted `false_obstruction_count = 0` exactly;
measured 0 on both bases. **UNREFUTED**, and non-vacuously confirmed: 16
labeled / 8 distinct instances (F_7's 3 distinct + Q's 5 distinct) are
OBSTRUCTED with an independently reverified odd-valuation witness and a
brute-force `NOT_EXISTS` confirmation, with zero counterexamples across
every one of the 52 labeled / 14 distinct decided instances in this run.

**Direction 2 (bidirectional exact-classifier reading -- H-PMA-001 as
frozen).** Predicted `false_compatibility_count = 0` exactly; measured 18
labeled / 5 distinct, all from F_5. **FALSIFIED**, on the 5 distinct F_5
instances this grid could reach, independently reproduced by four
algorithmically distinct methods: Module A vs. Module B inside the original
run; the Validator's from-scratch direct-module recomputation (0
mismatches across all 52/14 decided instances); the Red Team's from-scratch
brute-force square-root search plus an independently re-derived 8-branch
matrix construction (0 of 8 branches match the prescribed minors,
reproducing `raw-result.json`'s own `branch_log` mismatch pattern exactly,
branch by branch); and the Red Team's from-scratch unconstrained Groebner
basis computation over the algebraic closure of `F_5(t)`
(`RT-20260907-0df70c.yaml`'s `independent_verification.
method_4_groebner_no_normalization`), which is a **derivation-note-tier
checkable refutation artifact** under `docs/claims-and-verification.md`'s
refutation-artifact hierarchy -- closer to a proof than an empirical
observation, since it establishes non-existence over the algebraic closure,
not merely over `F_5(t)`.

### Inference

The falsification is scoped to a narrow, forced structural family, not to
"F_5" generically. All 5 distinct F_5 instances tested share the identical
shape forced by F_5's 3-element parameter box (`allowed_values` has
`q - 2 = 3` elements for `q = 5`): exactly 3 distinct rational functions,
`(t+1)/(t+2)`, `(t+1)/(t+3)`, `(t+1)/(t+4)`, each repeated across 5 of the
15 subsets. This is the *only* shape the frozen grid construction could
produce for F_5 -- not a representative sample of F_5(t)'s full
reciprocal-minor instance space (`RT-20260907-0df70c` OBJ-2;
`CORR-20260907-ae8418` item (2)). Within that narrow scope the
falsification is decisive and uncontested by any of the four independent
methods; outside it (F_3's single collapsed instance, F_7's 3 distinct
instances, Q's 5 distinct instances, and any non-repeating-value F_5(t)
table, untested) no direction-2 disagreement was observed anywhere.

This is exactly the failure mode H-PMA-001's own frozen text
pre-anticipated, not a surprise discovery: its `mechanism` field
distinguishes "the underlying mechanism claims the obstruction direction
only" from "the stronger frozen exact-classifier reading," and its
`interpretation_limits` states plainly "divisor parity plus a square
residual constant class is necessary, not sufficient." `RT-20260907-0df70c`
OBJ-5 makes the same point explicitly and asks that any promotion language
say so, which this addendum does.

### Limitation

- **Scope.** Toy scale throughout (`claim_tier: toy`); `certificate.kind:
  none` in every run; no ECDLP, relation, source-to-scalar, or
  standardized-curve claim is made or implied anywhere in this record.
- **Sample-size discipline.** Any future citation of this run's agreement
  statistics must carry *both* bases, per `CORR-20260907-ae8418`'s
  `immutability_note`. Citing "18/18," "34/52," or "the entirety of the F_5
  grid" alone overstates independent evidentiary weight: the real
  direction-2 falsification rests on 5 distinct mathematical instances, not
  18, and the real decided-instance count is 14, not 52.
- **Dead widening fallback.** As implemented, `grid_data.py`'s
  `widening_instance` is a no-op for any field whose parameter box is
  smaller than the 15-subset assignment stride's period -- F_3 and F_5 both
  hit this (`CORR-20260907-ae8418` item (3)). It cannot deliver the "+8 new
  instances" `specification.yaml`'s text describes, so the non-vacuity
  conjunct for F_3/F_5 never benefited from a genuinely enlarged box.
- **Open, unresolved question.** Whether the F_5 sufficiency failure is a
  field-specific artifact of F_5's small residual-class/box structure, or a
  general gap in the three-anchor-discriminant necessary condition
  applicable at any field or table shape, is **not resolved by this run**
  and is not claimed either way. The recommended discriminating follow-up
  (not yet designed or executed) is a grid over a field whose box does not
  collide with the 15-subset stride (F_11 or F_13, `q - 2 >= 9`) or a table
  built from >= 15 genuinely distinct rational functions, per
  `CORR-20260907-ae8418`'s `next_action` and `RT-20260907-0df70c`'s final
  `required_controls` item.
- **Dirty-code clause.** The tension `VAL-20260907-ae3832` flagged between
  the genuine `dirty_tracked_files: true` in every manifest and
  `specification.yaml`'s literal "any dirty code revision is invalid"
  clause is resolved by `CORR-20260907-f41219`: the clause targets the
  three frozen `required_artifacts` decision-logic files (independently
  confirmed via `git log` to have never been touched by the archiving
  session), not the disclosed, non-decisional orchestration-glue edits; the
  run package is not invalidated by this clause.
- This addendum records the Coordinator's evidence-review reading alongside,
  never in place of, the Executor's original observation-only report above.
