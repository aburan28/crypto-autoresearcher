# EXP-CZLIFT-17b7eb analysis: Smart's attack against the Serre-Tate canonical lift

Hypothesis H-CZLIFT-889c9d · question RQ-CZLIFT-b9f765 · goal GOAL-CZLIFT-1516d5.
Runs RUN-CZLIFT-041d05 (seed 20261009) and RUN-CZLIFT-6709c9 (seed 20261010).
Reviewed under DEC-20261023-147f9f, evidence EV-CZLIFT-712fe4, corrections
CORR-20261023-1869c3 and CORR-20261023-9f2176. Review inputs:
`reports/validation-20261022/validation_report.yaml` (VAL-20261022-3232db,
TASK-20261022-282b02) and `reports/redteam-20261023/redteam_report.yaml`
(RT-20261023-0b2a4f, TASK-20261023-856638).

Every number below is read from a run manifest, from the validator's
recomputation or from a red-team output file, named at the point of use. The
Coordinator computed nothing new. Where it compares two recorded numbers, the
section says so.

## Observation

Validity (validator J1, J2, J3; re-checked here against both manifests and
execution receipts):

- Both planned trials ran (2 of 2), with status `output_validated`, returncode
  0 and check_returncode 0. Seeds are 20261009 and 20261010, as frozen. Commit
  dcaa880ab6, clean tree.
- Each run has 29 curves and 7,308 rows. The validator's independent replay
  reproduced 14,616/14,616 rows with its own p-adic code. Manifest metrics
  equal raw-result metrics on both runs.
- The sealed blind re-derivation (J3) used independent curve models, with
  precision 10. It agrees with the producer on every class.

Primary metrics (both seeds; RUN-CZLIFT-041d05 / RUN-CZLIFT-6709c9):

| quantity | 041d05 | 6709c9 | source |
|---|---|---|---|
| rule_agreement (flag v_p(z([p]P^)) >= 2 vs v_p(Δj) >= 2e) | 7,308/7,308 | 7,308/7,308 | manifest |
| rule_disagreements | 0 | 0 | manifest |
| non-degenerate rows (v_p(Δj) < 2e) on which Smart recovers d | 2,052/2,052 | 2,052/2,052 | manifest; validator |
| degenerate rows (all v_p >= 2) | 5,256 | 5,256 | validator |
| next-digit successes on degenerate rows | 93 | 87 | validator j2_recompute |
| canonical class frac_degenerate (each of 29 curves) | 1.0 | 1.0 | manifest; validator T1 |

Degenerate next-digit rate against each definition's null
(CORR-20261023-9f2176, from `rt_r2_nulls_output.json` and
`rt_r2_actual_lifts_output.json`):

| definition and null | 041d05 z | 6709c9 z |
|---|---|---|
| frozen reading: all v_p >= 2 with preregistered 1/p (pooled SE, validator) | -0.0191 | -0.6463 |
| all v_p >= 2 with matching null 1/(p+1) (expected 86.84) | +0.684 | +0.018 |
| producer code vQ >= vP with 1/p (recorded in manifest) | +0.573 | -0.102 |
| symmetric vQ = vP with 1/(p-1) | +0.279 | -0.343 |
| exact null conditioned on the actual lifts (expected 79.96 / 80.61) | +1.539 | +0.751 |

Per section, against the exact null conditioned on the lifts
(`rt_r2_actual_lifts_output.json`; 1,752 rows per section and seed):

| section | 041d05 obs / exp_exact (z) | 6709c9 obs / exp_exact (z) |
|---|---|---|
| hensel_random | 41 / 28.93 (+2.322) | 32 / 28.87 (+0.602) |
| naive | 36 / 28.25 (+1.592) | 35 / 27.80 (+1.487) |
| teichmuller | 16 / 22.78 (-1.480) | 20 / 23.94 (-0.843) |

Further observations:

- Teichmuller's deficit is all in D = -3. There it has 2 successes per seed out
  of 660 rows. The exact expectation is 4.98 and 5.69, against 15.63 under 1/p.
  On every mu_6 \ {±1} pair on canonical and isomorphic j = 0 lifts, at all 11
  primes from 7 to 919, Teichmuller has 0 successes. At p = 7 its exact rate is
  0 on every j = 0 lift (`rt_r2_exact_output.json`, keys `mu6_forced_failure`
  and `exact_rates."-3|7|teichmuller"`).
- At p > 500, the per-section successes over both seeds (1,200 rows each) are:
  hensel_random 3, naive 1, Teichmuller 2. The null expectation is 1.39. A
  1/sqrt(p) leak would give 40.3 and a 10/p leak 13.9
  (`rt_r2_section_largep_output.json`).
- In the red-team full-fiber sweep, the red team's own p-adic code covered
  12,778 lifts over all 29 curves. It found 0 rule disagreements and 0 point- or
  section-dependent flags. Each curve has exactly one degenerate class mod p^2,
  the CM class (`rt_r1_fiber_output.json`, key `summary`).
- The red team also ran 10 non-CM anomalous curves (p = 53 to 211; red-team
  data, not frozen evidence). On each, the two lift directions have exactly one
  degenerate t each, and the two degenerate lifts share j mod p^2.
- Generator deviation (validator D2). On each seed one pert_p-labelled lift
  (D = -43, p = 11) has v_p(Δj) = 2 = 2e. It is flagged predicted-degenerate by
  the j-distance instrument before any point is measured, and gives 36
  degenerate rows. Class-label pert_p success is 0.98420 and 0.98659.
- Of the 5,256 degenerate rows, 78 (seed 20261009) and 81 (seed 20261010) have
  vQ < vP. 73 and 72 have vQ > vP. The model expectation is 86.84 on each side
  (`rt_r2_nulls_output.json`).

## Comparison

- **Preregistered criteria.** The success criterion is rule_agreement = 1.0,
  nondegenerate_success_rate = 1.0 and |degenerate_z_score| <= 4, on both
  seeds. It is met on both seeds under every definition-and-null pairing above.
  The largest |z| is 1.539. The falsification criterion (any disagreement; any
  non-degenerate failure; z > 4 on both seeds) is not triggered under any
  pairing.
- **Recorded prior.** The prior in review plan
  REVIEW-CZLIFT-17B7EB-EVIDENCE-20261023 was written before the red team ran.
  It expected the rule to hold as a restatement of Serre-Tate theory, the
  non-split recovery to be Smart's theorem, and the split-lift rate to sit at
  1/p. The first two parts were concurred with. The third was partly
  overturned: 1/p is not the matching null for the governing definition, and
  it does not hold per cell for deterministic sections.
- **Controls.** pert_p was run on its stated object (v_p(Δj) < 2e): 2,052/2,052
  rows recover d on both seeds. The isomorphic re-model matches the canonical
  model, with frac_degenerate 1.0 and success counts consistent with the null
  (validator C2). d = ±1 was excluded. At p <= 19 the pooled degenerate
  success is 56 against 60.26 and 60.76 expected, with no excess (validator C4).
- **Sections against their nulls.** hensel_random's exact rate is 0.98 to 1.01
  times 1/(p+1) for p <= 43, which matches the random-section model.
  Teichmuller's deficit against 1/p (validator T2: z = -2.74 and -1.84) falls to
  z = -1.48 and -0.84 against its exact null. naive is above its exact null on
  both seeds (z = +1.59 and +1.49). Neither naive value is near the threshold,
  and at p > 500 naive has 1 success against 1.39 expected.
- **Power (red team, `rt_r2_power_output.json`).** Per seed, the pooled test
  detects a uniform multiplicative leak lambda/(p+1) at lambda >= 1.42 (50 %
  power) and 1.52 (80 %). 68.5 % of the null mass comes from p <= 19, which is
  14.4 % of the rows. Against a 1/sqrt(p) leak confined to one section at
  p > 500, the power is 0.05.

## Inference

1. **The rule is a theorem, and the experiment calibrates instruments.** On
   every Z_p-lift of an anomalous ordinary curve, the two predicates are the
   same predicate. This follows from the reduction sequence
   0 -> E_1 -> E^(Q_p) -> Z/p -> 0, from the Kummer class of E^[p] in
   Ext^1(Z/p, mu_p) = Z/p as a homomorphism on the Serre-Tate deformation
   space, and from the ramification of j at j = 0. The derivation is red-team
   R1 (`redteam_report.yaml`, `joint_findings.R1.derivation_two_sides_identical`),
   and the Coordinator checked it step by step. Belding 2007, section 7
   (arXiv:math/0703906, retrieved and read by TASK-20261023-856638), states the
   core: the DLP attack requires a non-canonical lift. rule_agreement = 1 could
   therefore have failed only through an implementation error. What it shows
   is that two code-independent instruments are correct on 14,616 rows, and on
   12,778 further lifts in the red-team sweep. It is not independent evidence
   for the statement, and the experiment discovered no obstruction.
2. **Non-split recovery is Smart's theorem, confirmed** on 2,052/2,052 rows per
   seed. In the hypothesis's mechanism, the operative condition is "P has no
   torsion lift in E^(Q_p)". That coincides with "E^[p] non-split" only because
   #E(F_p) = p. The red-team PTM-1 measurement on non-anomalous CM curves shows
   that the detached sentence would prove too much.
3. **Clause 3 holds pooled only.** The pooled next-digit rate on degenerate
   lifts is consistent with the random-section null on both seeds, under the
   matching null and under the exact lift-conditioned null. It is false at the
   cell level for deterministic sections. On j = 0 lifts with A ≡ 0 mod p^2,
   the Teichmuller section is mu_6-equivariant, and the automorphism acts on
   E_1/E_2 by the conjugate eigenvalue. So d in mu_6 \ {±1} gives ratio
   d^{-1} != d, a forced failure. This is checkable as a counterexample
   (p = 7, y^2 = x^3 + 5, rate 0 against 1/7).
4. **What the next digit measures.** On a split lift with vP = 2, success holds
   iff s(dP) = [d]s(P) in E(Z/p^2), i.e. iff the section is d-homogeneous mod
   p^2. The red team verified this on 4,214/4,214 rows. The "noise" is a
   property of the section's non-homomorphy, not of the lift.
5. **Decision consequence.** H-CZLIFT-889c9d is supported at toy tier in the
   scoped form recorded in EV-CZLIFT-712fe4. Clauses 1 and 2 rest on the
   derivation, with this experiment as calibrated confirmation. Clause 3 holds
   pooled, with the matching null, and with the disclosed mu_6 exception. No
   transfer to non-anomalous curves, non-CM anomalous curves, ramified lifts or
   cryptographic sizes is asserted.

## Limitation

- **Scope.** The scope is 29 class-number-one CM anomalous curves with
  7 <= p <= 1373 (at most 11 bits; toy tier) and precision p^8. Lifts are
  unramified integral short-Weierstrass models in four sampled classes, with
  v_p(Δj) in {1, 2, 3, ∞} at e = 1 and {3, 6, ∞} at e = 3. Three sections were
  tested: naive, Teichmuller, and Hensel with one random x-digit.
- **j = 0 threshold.** Over Z_p every lift of a j = 0 curve has v_p(Δj) in 3Z
  or ∞, so the data pin the threshold only to (3, 6]. The value 2e = 6 is
  correct by theory but was not measured.
- **Power of the frozen statistic.** The pooled statistic is dominated by small
  p and cannot detect large-p or single-section leaks. The exclusions at
  p > 500 are post hoc red-team readings, not frozen criteria.
- **Overdispersion.** Deterministic sections have lift-specific rates with a
  relative sd of about sqrt(11/p) (red team: mean 0.035, sd 0.951 over 40
  canonical lifts at p >= 100). An i.i.d. binomial SE at 1/p understates their
  variance unless the null is conditioned on the lift.
- **Unrecorded inputs.** Rows record neither (P, d) nor the lift coefficients.
  Replays depend on the producer's RNG draw order: the red team validated it on
  406 lifts, and the validator used the producer's random_point to regenerate
  points.
- **Checker independence.** check.py imports the producer's summarize and
  curve list, so it is not independent of the producer. Independence rests on
  the validator's j2_recompute.py and replay_compare.py and on the red team's
  rt_padic.py.
- **Corrections.** The degenerate-rate definition and its null were corrected
  after observation (CORR-20261023-1869c3, CORR-20261023-9f2176). No outcome
  changes under any pairing, and no criterion was amended.
- **Pointer citations.** Katz (LNM 868) supports the standard Serre-Tate facts
  in the derivation, but only bibliographically: the full text was not
  retrieved. Smart 1999 is verified bibliographically, and its content only
  through its abstract and Belding 2007.
- **Naive-section excess.** The naive section's same-sign excess over its exact
  null (+1.59, +1.49) is unexplained. No frozen criterion tests it, and it is
  not significant at the threshold.
- **Non-CM anomalous curves.** The non-CM observations come from the red team,
  not from frozen runs.
