# EXP-CZLIFT-f5e06c analysis

Hypothesis H-CZLIFT-bd2017 (question RQ-CZLIFT-b9f765, goal GOAL-CZLIFT-1516d5).
Runs RUN-CZLIFT-032a92 (seed 20261009) and RUN-CZLIFT-6447f0 (seed 20261010).
Evidence record EV-CZLIFT-e9a7cf; decision DEC-20261023-9de83a. Independent
reviews: validation VAL-20261022-1d018a (`reports/validation-20261022/`, passed)
and red team RT-20261023-fbf42f (`reports/redteam-20261023/`; R1 breaks, R2
breaks, PTM-1 holds).

## Observation

Validity, checked before any reading:

- 2 of 2 planned trials are present, and the run directories hold nothing else.
  Both manifests read `status: completed_valid`, `code.dirty: false`, commit
  5c769342fa, and seeds 20261009 and 20261010, as in the frozen trial plan.
  Wall time was 10.85 s and 11.21 s against the advisory 3600 s. Both receipts
  read `output_validated` with checker exit 0.
- The validator found that manifest `result.metrics` equals the raw-result
  metrics block field for field (141 of 141 per seed). Its own recomputation
  from raw rows matches every count and rate exactly. A full replay reproduces
  both raw-result.json files byte for byte. A sealed blind re-derivation
  agrees with the recorded valuations on all 48 anomalous curve draws.
- Controls were present. The lane-1 drivers ran unmodified and hash-bound
  (single commit 6756a75613). Both torsion arms are present. The positive
  control (pert_p lift) and the negative controls (canonical, isomorphic,
  pert_p2) gave the expected outcomes. PTM-1 (non-anomalous curves rejected
  before any measurement) holds.
- 0 rows were dropped. Every anomalous curve has 96 rows and every torsion
  curve has 12.

Anomalous arm, 24 class-number-one CM anomalous curves per seed, precision p^8:

| quantity | RUN-CZLIFT-032a92 | RUN-CZLIFT-6447f0 |
|---|---|---|
| p range | 11719 to 89153 | 11719 to 89269 |
| rows (4 lift classes x 3 sections x 8 samples x 24 curves) | 2304 | 2304 |
| rule_agreement (disagreements) | 1.0 (0) | 1.0 (0) |
| nondegenerate rows, Smart ratio = d | 576/576, all pert_p | 576/576, all pert_p |
| degenerate rows (canonical, isomorphic, pert_p2) | 1728, 0 successes | 1728, 0 successes |
| expected successes under 1/p | 0.0591 | 0.0557 |
| degenerate_z_score (recorded) | -0.24321 | -0.23607 |

- The two seeds share 7 curves, so the arm covers 41 distinct curves of the 84
  class-number-one CM anomalous primes in [10^4, 10^5] (red-team population
  count). D = -3 accounts for 20 of the 48 draws.
- Each lift class has one fixed lift distance. With e = 1, v_p(j - j_CM) is 1
  (pert_p), 2 (pert_p2) and 8 (capped; canonical and isomorphic). With e = 3 it
  is 3, 6 and 8. The valuation pattern is v = 1 on pert_p and v = 2 on every
  other class.

Torsion arm, 24 odd-order curves per seed (16 CM curves on their canonical
model and 8 random curves on naive integer lifts), precision p^4:

| quantity | RUN-CZLIFT-032a92 | RUN-CZLIFT-6447f0 |
|---|---|---|
| p range | 10007 to 93319 | 15161 to 97813 |
| n range | 109 to 93001 | 149 to 64633 |
| pairs | 288 | 288 |
| canonicity, homomorphism, degeneracy, reduction, scalar equivariance | all 1.0 | all 1.0 |
| identity_rate, 3 sections x 3 arm cells | 1.0 in all 9 | 1.0 in all 9 |
| section successes per section (all arms) | 0/288 | 0/288 |
| expected successes per section under 1/p | 0.0075 | 0.0085 |
| z per section (all / cm / random) | -0.0869 / -0.0630 / -0.0598 | -0.0920 / -0.0696 / -0.0601 |
| arm_difference z | null (pooled rate 0) | null |
| torsion_cost_mean_additions | 107.17 (sum 30864, bound 42576) | 107.75 (sum 31032, bound 41928) |

- The non-vacuity control: `homomorphism_rate_prec2` = 0.0 and
  `frac_valuation_1` = 1.0 in every section cell.
- The two seeds share no torsion curves, so the arm covers 48 distinct curves.

From the driver sources, read by the Coordinator in this review:
- In `experiments/EXP-CZLIFT-17b7eb/implementation/run.py` (lines 79-86), the
  anomalous driver draws a fresh point P and multiplier d for every row.
- In `experiments/EXP-CZLIFT-ae0a13/implementation/run.py` (lines 80-118), the
  torsion driver draws one (P, d) per sample and uses it for all three
  sections.
- Both drivers count #E(F_p) with `EllipticCurve.order()`, which is a naive
  O(p) loop (`harness/toycurve.py` lines 80-81).

## Comparison

Against the frozen success criterion (both seeds):
- rule_agreement = 1.0 and nondegenerate_success_rate = 1.0: met.
- The five torsion rates = 1.0 and every identity_rate = 1.0: met.
- Every |z| ≤ 4: met.
- The falsification criterion did not fire.

Against the hypothesis statement, clause by clause:

- **Exact anomalous clauses** (rule agreement; Smart ratio = d on nondegenerate
  rows). These match the toy runs (EXP-CZLIFT-17b7eb, p ≤ 1500, exhaustive) on
  new curves with p up to 89269.
  - The rows are not 4608 independent tests of the rule. Degeneracy is a
    property of the curve lift, so the effective units are 164 curve x
    lift-class cells over 41 curves. With 0 disagreements, the one-sided 95%
    upper bound on the disagreement rate is 1.81% per cell (red team R1-b).
  - The sealed validator code reproduces the valuation pattern on all 48
    draws, so these clauses have independent-code corroboration.
- **Exact torsion clauses** (five rates; tau-ratio identity; cost bound). These
  match the toy run (EXP-CZLIFT-ae0a13, 50 ≤ p ≤ 600) on 48 new curves with p
  up to 97813.
  - With 0 failures in 576 pairs, the one-sided 95% upper bound on the failure
    rate is 0.52% per pair.
  - The evidence comes from the same code only. Per-row torsion and identity
    booleans were checked by recomputing aggregates and by a byte-identical
    replay of the producer code. No independent implementation of the torsion
    section was run.
- **1/p clauses** (degenerate next-digit rate; section success rate).
  - Observed successes: 0 in 3456 anomalous-degenerate rows, and 0 in 576 rows
    per torsion section over both seeds.
  - One-sided 95% upper bounds (Clopper-Pearson with 0 successes):
    - anomalous, per seed (n = 1728): 1.73e-3, which is 51x and 54x the mean 1/p;
    - anomalous, both seeds (n = 3456): 8.66e-4, which is 26x the mean 1/p;
    - torsion, per section per seed (n = 288): 1.03e-2, which is 352x to 395x
      the mean 1/p;
    - torsion, per section over both seeds (n = 576): 5.19e-3, which is 187x
      the mean 1/p.
  - The red team's common-rate bound over all three sections (n = 1728,
    1.73e-3) assumes independent rows. The torsion driver reuses (P, d) across
    sections, so that bound does not stand. The per-section bounds stand. On
    the anomalous arm the rows are independent draws, so the row bounds stand.
  - The recorded z equals the design-only value -sqrt(sum 1/p_i) to within
    1.2e-15 in every frozen cell.
  - One chance success in the anomalous cell of seed 20261010 would give
    z = 4.0001 and break the frozen bound. On seed 20261009 one success gives
    z = 3.87.
  - The frozen clause passes on both seeds with probability 0.900 at rate 1/p
    and with probability 1.000 at rate 0. P(all zero | 1/p) = 0.850, so the
    likelihood ratio of 1/p to 0 is 0.85.
- **1/p clauses against p^-1/2.** Over the tested primes, p^-1/2 lies in
  [3.35e-3, 9.24e-3] on the anomalous arm and in [3.20e-3, 1.00e-2] on the
  torsion arm.
  - The anomalous bound is below the whole band on each seed alone (1.73e-3)
    and over both seeds (8.66e-4).
  - The torsion per-section bound is above the band on one seed (1.03e-2). Over
    both seeds (5.19e-3) it is inside the band, so on its own it does not
    exclude a section succeeding at about p^-1/2.
- **Arm-difference clause of H-CZLIFT-6d4ed1.** Not evaluated: z is null on
  both seeds. It is not part of the H-CZLIFT-bd2017 statement or the frozen
  criterion.
- **Tier clause** ("moving the claim tier of H-CZLIFT-889c9d and
  H-CZLIFT-6d4ed1 from toy to medium"). The largest field is F_p with
  p = 97813 < 2^17. The mechanical rule in `docs/claims-and-verification.md`
  (toy: max field bit size ≤ 32) makes both runs toy tier. The spec's
  `scale_relevance.tier: medium` and the manifests' `tier: medium` are
  mislabels. The p-adic working ring Z/p^8 is not a larger field.

## Inference

- Over toy-tier fields, at p up to 10^5, the exact clauses of H-CZLIFT-889c9d
  and H-CZLIFT-6d4ed1 hold with no exception on new curves, on two seeds.
  - On the anomalous arm, these are the j-distance degeneracy rule at lift
    distances {1, 2, ≥8} (e = 1) and {3, 6, ≥8} (e = 3), and Smart's recovery
    on every pert_p lift. They have independent-code corroboration.
  - On the torsion arm, these are the five torsion-section rates, the
    tau-ratio identity and the double-and-add cost bound. The evidence is
    same-code only.
  - This is a replication at a wider p range and the same tier. Its strength
    for these clauses is `replicated`.
- The measured identities are consequences of the derivations stated in the
  two target hypotheses: Serre-Tate splitting of E^[p] on lifts with
  v_p(q - 1) ≥ 2, Hom(Z/n, Z_p) = 0 and Smart's theorem. The mechanism does
  not depend on p. Agreement checks that the instrument matches the
  derivations on more instances. It adds instance coverage, not a new regime.
- The 1/p clauses are inconclusive at this scale. The data do not distinguish
  the predicted 1/p rate from 0. The frozen z-test is a design function that a
  never-succeeding section passes with certainty. The data support only an
  upper bound:
  - on the anomalous arm, the degenerate next-digit success rate is below
    8.7e-4 per row (95%), which is below p^-1/2 at every tested p;
  - on the torsion arm, each non-canonical section's success rate is below
    5.2e-3 per row (95%), which does not on its own exclude p^-1/2.
- The tier clause of the hypothesis cannot be met by this design, whatever the
  data. It fails on policy grounds, not because of a measurement.
- No improvement on any attack is claimed or observed. On the anomalous arm the
  only successes are Smart's classical attack on non-canonical (pert_p) lifts.
  On the canonical lift Smart's attack degenerated on every row.

## Limitation

- **Tier.** The runs are toy tier (fields of at most 17 bits). Nothing here
  bears on 33 to 96-bit fields or on any deployed curve, and no transfer
  argument is offered.
- **Independence.** The torsion-arm replication is same-code. The validator's
  independent code reached the anomalous valuations on all 48 draws, the
  sampled anomalous attack outcomes, and the sampled non-torsion-section
  outcomes, but not the torsion-section identities.
- **Sample, not census.** The anomalous arm covers 41 of 84 curves where the
  toy test was exhaustive. Lift distances are fixed per class. For e = 3 the
  levels 4 and 5 cannot occur in short Weierstrass form, so the 2e = 6
  threshold is not distinguished from 4 or 5.
- **Exact-hit counting only.** The rows record neither d nor the computed
  ratio, so partial leakage cannot be seen: a ratio biased toward d, or bits
  of d. The uniform-d design hits a structured small-d stratum (the
  EXP-CZLIFT-bdae69 mechanism) in about 1.5e-4 of rows.
- **Untested random model.** "Non-canonical sections recover d at rate 1/p" is
  a random-model assumption. It is not numbered as a heuristic in
  H-CZLIFT-889c9d, H-CZLIFT-6d4ed1 or H-CZLIFT-bd2017.
- **Confounded arms.** The arm contrast confounds lift type (canonical against
  naive) with curve type (CM against random). No arm puts a non-canonical lift
  on a CM curve.
- **Missing records.** No memory figure is recorded (validator replay: 55.2 MB
  peak RSS). No package versions are pinned.
- **Claim-text defects in the hypothesis.**
  - The nondegenerate successes are on pert_p lifts, not "against the
    canonical lift".
  - The "random-lift" curves are random curves with a naive lift.
  - The interpretation limit "CM curves only" applies to the anomalous arm
    only.
- **Scaling the drivers.** The lane-1 drivers count points in O(p), so any run
  above toy scale needs a new driver version.
