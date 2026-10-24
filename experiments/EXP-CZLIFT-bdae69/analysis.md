# EXP-CZLIFT-bdae69 analysis (Coordinator, review-evidence, 2026-10-23)

Hypothesis H-CZLIFT-d37231; question RQ-CZLIFT-b9f765; goal GOAL-CZLIFT-1516d5.
Runs RUN-CZLIFT-0cefcd (seed 20261009) and RUN-CZLIFT-a5c1da (seed 20261010).
Reviews: VAL-20261022-8caa0c (TASK-20261022-2d255e, verdict passed) and
RT-20261023-2411b8 (TASK-20261023-20d7d9; R1 breaks on the transfer clause
only, R2 holds with corrected nulls, PTM-1 holds). Evidence record
EV-CZLIFT-f2a401; decision DEC-20261023-039ddf.

Every number below is either recorded in a run manifest or raw-result.json,
or computed by a named reviewer artifact. Reviewer-only computations are
labelled "review-side" and are not run evidence.

## Observation

- **O-1 Validity.** 2 of 2 planned trials, both `output_validated`,
  return code 0, checker return code 0, commit `ca89e1a9f0` clean, seeds as
  frozen, 40 distinct primes in (50, 2000) x 40 rows per seed, precision 4,
  every d in [2, p-3]. VAL-20261022-8caa0c: all receipt hashes match (32
  paths), every frozen metric recomputes exactly from raw rows, an
  implementation-independent replay reproduces all five fields of all three
  sections on 3200/3200 rows, and the producer replays deterministically. No
  run claims a solve or relation; certificate kind is `none` on both
  manifests, so no certificate applies.
- **O-2 Teichmuller section.** Per seed: homomorphism 1600/1600,
  functional vanishing 1600/1600, ratio defined 0/1600, success 0/1600
  (z = -1.433, -1.828). The recorded vanishing flag is evaluated at s(g)
  only, 40 distinct points per seed (VAL D3); the validator's own evaluation
  at omega(g^d) gives 3200/3200.
- **O-3 Naive integer section.** Success 13/1600 (seed 20261009) and
  20/1600 (seed 20261010); recorded z = 7.648 and 9.136; ratio defined
  1600/1600 on both seeds. Recorded reference mean 1/p = 0.0012823 and
  0.0020839, i.e. 2.05 and 3.33 expected successes.
- **O-4 Random-Hensel section.** Success 1/1600 and 2/1600; z = -0.735 and
  -0.731; ratio defined 1599 and 1596 (undefined rows counted as failures).
- **O-5 Homomorphism counts.** Naive 10/1600 and 10/1600; Hensel 0/1600 and
  0/1600.
- **O-6 Per-row decomposition of the naive successes** (review-side;
  red-team `r2_nulls_output.json`, own code, and validator J2/J3
  independently). The recorded success bit equals the closed-form criterion
  "q_p(g) != 0 mod p and g^d mod p^2 < p" on 3200/3200 rows and the red
  team's own precision-4 p-adic ratio on 3200/3200 rows.

  | seed | region | rows | successes | exact conditional expectation |
  |---|---|---|---|---|
  | 20261009 | sub-p (g^d < p) | 11 | 11 | n/a (certain) |
  | 20261009 | band (p <= g^d < p^2) | 14 | 0 | 0 (impossible) |
  | 20261009 | rest (g^d >= p^2) | 1575 | 2 | 2.479 (P >= obs 0.71) |
  | 20261010 | sub-p | 13 | 13 | n/a (certain) |
  | 20261010 | band | 20 | 0 | 0 (impossible) |
  | 20261010 | rest | 1567 | 7 | 4.106 (P >= obs 0.12) |

  Total exact conditional expectations: 11.549 and 17.643.
- **O-7 Naive homomorphism rule** (review-side): naive hom equals
  (x*y < p as integers) on 3200/3200 rows; exact expectations 9.353 and
  12.960 over F_p^* minus {1}.
- **O-8 Generator controls** (review-side, red-team
  `ptm1_generator_controls_output.json`, exhaustive in d over all 288 primes
  in (50, 2000)). Population naive success rate as a multiple of mean 1/p:
  rule A smallest primitive root (the frozen run.py) 5.03; rule B random
  primitive root 1.11 (sub-p 0.108 + rest 1.016); rule C smallest root
  > sqrt(p) 0.956; rule D rule A restricted to g^d >= p^2 0.910. Simulated
  frozen-protocol z (mean, sd): A 7.54, 2.45; B 0.184, 1.205; C -0.050,
  1.089; D -0.164, 1.167.
- **O-9 Elliptic integral-section computation** (review-side, red-team
  `r1_elliptic_analogue_output.json`, own code). 37a1 short model
  y^2 = x^3 - 16x + 16, P~ = (0, 4), integral multiples d in {2..6}, 284 good
  non-anomalous p in (50, 2000): balanced integer section ratio = d on
  1420/1420 rows at d in {2..6}; the [0, p-1] section 1136/1136 at
  d in {2, 4, 5, 6} and 0/284 at d = 3; random-Hensel 2/1420 against 2.99
  expected; off the integral set naive 21, balanced 22, Hensel 25 against
  21.7 at 1/p. y^2 = x^3 + 17, P~ = (-2, 3): balanced section 287/287 at
  d = 2, [0, p-1] section 0/287.
- **O-10 Proves-too-much (Teichmuller, VAL PTM-1)**: on 23040 fresh rows
  (288 primes x 40 x 2 seeds) Teichmuller success 0 and ratio defined 0;
  Teichmuller lifts perturbed by 1 + p^j t (j = 1, 2, 3) succeed at the random
  rate (z between -0.25 and +1.35).

## Comparison

- **C-1 Against the frozen criteria.** Teichmuller rates = 1.0 on both seeds:
  met. |hensel.z| <= 4 on both seeds: met. |naive.z| <= 4: **not met on
  either seed** (7.65, 9.14). The success criterion fails and the
  falsification criterion ("a non-canonical section with z > 4 on both
  seeds") is met by the naive section. The instrument-invalidity clause (a
  Teichmuller identity failing) is not triggered. The outcome is robust to
  every z variant the validator computed (Poisson-binomial 7.65/9.15,
  distinct-(p, d) rows 7.24/8.51).
- **C-2 Naive counts against the hypothesis's own 1/p model.** 13 against
  2.05 and 20 against 3.33; the 4-SE acceptance bounds are 7.8 and 10.6
  successes. Pooled 33 against 5.39, ratio 6.13 (95% CI 4.22-8.61). Against
  the generator-specific exact null (criterion above, conditional on the
  drawn primes and generators) 33 against 29.19, ratio 1.13 (CI 0.78-1.59).
- **C-3 Hensel against 1/p.** Pooled 3 against 5.39, ratio 0.56 (CI
  0.12-1.63). The |z| <= 4 band admits up to 3.8x and 3.2x of 1/p per seed,
  so the clause is supported only to the pooled upper bound 1.63x (RT O5).
- **C-4 Homomorphism counts against the stated "near 1/p".** Naive 10 and 10
  against 2.05 and 3.33 under 1/p (P(>= 10) = 5.7e-5 and 2.4e-3) and
  against 9.35 and 12.96 under the exact rule x*y < p. Hensel 0 and 0
  against 2.05 and 3.33 under 1/p (P(0) = 0.129, 0.036) and against
  2.2e-5 and 2.3e-4 under the exact p^-3.
- **C-5 Generator arms (review-side).** The excess is present only under
  rule A and vanishes when the sub-p chain is removed by the generator rule
  (C) or by excluding its rows (D); under a random root (B) the residual
  0.108 x (1/p) excess is the same no-carry mechanism acting on roots below
  sqrt(p).
- **C-6 Against the recorded Coordinator prior**
  (REVIEW-CZLIFT-BDAE69-EVIDENCE-20261023, written before any reviewer ran):
  "Teichmuller and Hensel hold" was confirmed; "the naive falsification is a
  smallest-root artifact" was confirmed (C-5); "it has no elliptic analogue"
  was **overturned** by O-9.
- **C-7 Against the earlier observation decision DEC-20261009-44c288.**
  Its count "24 of the 33 are the pairs with g^d < p ... the remaining 9 at
  the random rate (about 5 expected)" agrees with O-6 (9 rest successes
  against 5.11 at 1/p and 6.585 under the exact conditional null, ratio 1.37,
  CI 0.63-2.60). Its sentence "it has no elliptic analogue because point
  addition always reduces" disagrees with O-9.
- **C-8 Between the reviewers.** The validator's statement that "the true
  rest rate exceeds 1/p at small primes" holds for particular primes (151,
  157) but not in the population: rule-A rest-region ratio 0.984 +/- 0.085,
  bin 50-500 at 77 against 74.5 (RT O7). Both agree the seed-20261010
  residual is sampling variation (exact conditional P = 0.12).

## Inference

**I-1 Derivation note (refutation artifact; label: derivation, not a
machine-checked proof).** Let p be an odd prime, g a primitive root taken as
an integer in [2, p-1], d in [2, p-3], and q_p(a) = (a^{p-1} - 1)/p the
Fermat quotient of an integer a prime to p.

- D-1 (functional = Fermat quotient). For an integer a prime to p,
  a^{p-1} = 1 + p q_p(a), and log_p(1 + p u) = p u - p^2 u^2 / 2 + ...
  = p u mod p^2. So log_p(s(x)^{p-1}) / p = q_p(s(x)) mod p for the naive
  section s(x) in [1, p-1], and when q_p(g) != 0 mod p the recorded ratio
  reduces to q_p(r) / q_p(g) mod p with r = g^d mod p. (If the numerator has
  higher valuation the ratio is 0, which never equals d >= 2.)
- D-2 (Eisenstein's logarithmic property; retrieved and confirmed by
  RT-20261023-2411b8). q_p(ab) = q_p(a) + q_p(b) mod p, and
  q_p(a + kp) = q_p(a) - k/a mod p. Write the integer G = g^d = r + kp with
  0 <= r < p. Then q_p(G) = d q_p(g) and q_p(r) = q_p(G) + k/r mod p, so the
  ratio is d + k / (r q_p(g)) mod p. (VAL J3 writes the correction with a
  minus sign; the check p = 5, g = 2, d = 3 gives ratio 2 = 3 + 1/(3*3) mod 5,
  so the sign is +. The success criterion does not depend on the sign.)
- D-3 (exact success criterion). Since r and q_p(g) are units, success holds
  iff p | k, i.e. iff g^d mod p^2 < p. Sub-p pairs (g^d < p, k = 0) always
  succeed; band pairs (p <= g^d < p^2, 1 <= k <= p-1) never succeed; on rest
  pairs the digit k mod p is heuristically uniform, giving about 1/p.
- D-4 (homomorphism rule). s(x)s(y) and s(xy) are integers below p^4, so
  s(x)s(y) = s(xy) mod p^4 iff x*y < p as integers. For the Hensel section
  with independent random digits above p the identity holds with
  probability p^-3 per pair. Neither is near 1/p.

D-3 and D-4 reproduce every recorded naive success and homomorphism bit
(3200/3200, two independent implementations), and the count of sub-p pairs
under the smallest primitive root accounts for the excess: so the
falsification is explained exactly, not merely observed.

**I-2 Status of H-CZLIFT-d37231.** The hypothesis is false as posed in two
clauses: (a) the naive-section success clause, by the pre-registered
falsification on both seeds, explained by D-3; (b) the homomorphism-rate
clause "homomorphic on a fraction near 1/p" for both non-canonical sections,
by D-4 and C-4. The Teichmuller clause holds (theorem-level control; the
instrument is calibrated). The Hensel success clause holds within the test's
power (excess up to 1.63x of 1/p not excluded). The statement is a
conjunction, so it is rejected as posed, scoped to the tested instantiation
(smallest primitive root as frozen in run.py).

**I-3 What was refuted.** The refuted part is the hypothesis's implicit,
unnumbered random-model assumption (RT O3): that a non-canonical section's
lift of g^d is random relative to d. The naive lift is a structured object
(the integer g^d itself on the sub-p chain). The stated mechanism,
Hom(Z/(p-1), Z_p) = 0, is not tested by the naive clause and is not refuted;
the excess comes from Z (no-carry multiplication), not from F_p^*.

**I-4 No discrete-log leverage.** The instances the naive ratio solves with
certainty (g^d < p, a log_g(p)/p fraction) are solved by an O(log p)
integer logarithm with self-verification. Elsewhere the success probability
is about 1/p per attempt, so the expected cost (per-attempt cost x inverse
success probability) is about p * O(log p), dominated by Pollard rho
O(sqrt p) and by index calculus in F_p^*.

**I-5 Transfer.** This is a G_m calibration and is not evidence about any
elliptic curve. The review-side computation O-9 shows that an elliptic
analogue exists: on a small-coefficient global model the integral section
coincides with the global point on integral multiples [d]P~, and any
homomorphic functional returns d exactly there. Its size is fixed by the
integral multiples of the global lift (finite by Siegel's theorem, recalled;
independent of p), whereas on G_m the sub-p chain grows like log_g p. It
applies only where P lifts to a small global point, where the archimedean
route already solves the DLP. Consequence: every elliptic Smart-style
success statistic in this goal that uses a naive, integral or small-height
section on a small-coefficient model must be stratified by d in the integral
set before it is read as "random rate" (red-team control C1).

**I-6 The specification's `on_negative` branch is not executed.** It says a
negative "would contradict a textbook fact and sends the instrument (log_p
series) to repair first". The instrument is verified (O-1, O-10, D-1), and
the textbook fact that applies (D-2) predicts the excess. No repair is
warranted.

**I-7 Strength.** The falsification as posed is strong: frozen protocol,
pre-registered criterion, a theorem-level control and a same-shape null,
two seeds each far beyond threshold (random-root P(z > 4 on both seeds)
about 3.3e-5), the mechanism isolated in closed form and checked on every
row by two independent implementations. The scientific content is weak: it
refutes a mis-derived prediction about an elementary archimedean effect.

Scoped negative phrasing for the clauses that held: no Teichmuller or
random-Hensel success rate exceeding the pre-registered 4-standard-error
threshold over the mean 1/p was observed over the tested primes, generator
rule, precision, implementation and budget.

## Limitation

- L-1 Toy tier: 80 primes 50 < p < 2000 (at most 11 bits), 1600 pairs per
  seed, precision 4, G_m only. Nothing about elliptic curves or deployed
  curves is measured here.
- L-2 The hypothesis says only "generator g". The generator rule
  (sympy.primitive_root, the smallest root) is fixed by the frozen,
  hash-pinned run.py named in `test_boundary.implementation`, chosen before
  any data. The rejection is of that instantiation; the random-root reading
  is a review-side computation (O-8), not run evidence.
- L-3 The z statistic assumes i.i.d. Bernoulli(1/p) rows; d is drawn with
  replacement (48 and 56 duplicate (p, d) rows) and success sets clump in d
  (dispersion index about 2). No criterion outcome changes (C-1).
- L-4 The recorded vanishing flag is evaluated at s(g) only (40 distinct
  points per seed); full-row coverage is the validator's computation.
- L-5 The checker imports the producer's code and re-runs 2 of 40 primes;
  implementation independence comes from the validator replay and the red
  team's own code.
- L-6 sympy version and peak memory are unrecorded (runtime_lock null);
  mitigated by a sympy-free replay that reproduced every prime and
  generator.
- L-7 Review procedure: tools/check_review_independence.py reports one
  problem for TASK-20261022-2d255e (the blind re-derivation J3 and the
  implementation-reading joints J1/J2 were assigned to one task without a
  `_blind_phase_assignments` split). The blind files were sealed
  (blind/SEAL.sha256, 2026-10-22T08:30:35Z) before any blind_from read, and
  the red team re-derived the criterion with its own code. Accepted as a
  procedure deviation (DEC-20261023-039ddf PD-1); it does not change any
  value used here.
- L-8 The elliptic analogue (O-9) and the Siegel bound are review-side; the
  Siegel citation is recalled, load-bearing only for "finite and independent
  of p". Elliptic section results depend on the Weierstrass model and lift
  convention (RT O9).
- L-9 The Hensel section draws fresh digits per evaluation rather than fixing
  one lift per x (VAL definition-fidelity note 5); statistically equivalent
  for these metrics.
- L-10 The run packages entered git in a queue commit titled for another
  task (08ee02a391); byte custody is intact.
