# EXP-CZLIFT-1a3453 analysis: character spectrum of torsion-section digits

Coordinator evidence review, 2026-10-23. Hypothesis H-CZLIFT-fba874, question
RQ-CZLIFT-b9f765, goal GOAL-CZLIFT-1516d5. Evidence record EV-CZLIFT-764f54,
decision DEC-20261023-2e7447. Review plan REVIEW-CZLIFT-1A3453-EVIDENCE-20261023
(validator TASK-20261022-8ebef8 → VAL-20261022-55676f; red team
TASK-20261023-792040 → RT-20261023-dcb217; ledger archive TASK-20261023-4d7449).

Notation used below: for a digit function f(k), h = (n-1)/2 is the half range,
T(p,n) = ln((p-1)n) + 12 is the frozen threshold, and
X = max over t != 0 and j of |sum_{k=1..h} e(t f(k)/p) e(-jk/n)|^2 / h.
Every term has modulus 1, so X <= h. X >= T exactly when some single pair has
normalised correlation tau = |sum|/h >= rho_min(p,n) = sqrt(T/h).

## Validity (checked before interpretation)

- Run count: the trial plan has 2 trials and both exist. RUN-CZLIFT-037e5f
  has seed 20261009 and RUN-CZLIFT-d37ca4 has seed 20261010. Both are
  `output_validated`, with returncode 0 and check returncode 0. No other run
  directory exists (VAL-20261022-55676f, artifact_checks).
- Manifests are schema-complete: run.id, status, code (commit 3d48a8e6,
  dirty false), environment, inputs, timing and result are all present. Of
  the hashed artifacts, 18/18 match the execution receipts and 41/41 match the
  ledger receipt TASK-20261009-619333. The contract was frozen in 172ec3c94f
  before the run commit.
- Seed integrity: the independent replay (j2_replay.py) uses its own F_p
  arithmetic, its own Newton-iteration torsion lift and its own spectrum. It
  regenerates all 72 curves from the recorded seeds.
- Raw/summary agreement: every manifest metric was recomputed from
  raw-result.json and is equal. The replay matches every max_power,
  shuffled_max_power, uniform_max_power and threshold to 8e-14 relative, and
  all 2160 spike counts are equal.
- Controls ran: digit 0, the shuffled series and the uniform series exist on
  every row. The uniform control is clean (0 spikes), so no invalidation rule
  fires. The shuffled control turns out not to be a valid null for the real
  series; see Comparison.
- Certificates: no solve or relation is claimed. `certificate.kind: none` is
  correct.

The run set is valid as a measurement. Its numbers are evidence. Whether they
bear on the hypothesis is a separate question, answered below.

## Observation

- Both seeds record spikes_total = spikes_digit0 = spikes_higher_digits =
  shuffled_spikes_total = uniform_spikes_total = 0, over 36 curve records per
  seed (24 CM-canonical, 12 random-naive) and 10 digit rows per record (x and
  y, digits 0..4).
- Closest real approach on the higher digits:
  - RUN-CZLIFT-037e5f: -3.942 (D=-3, p=571, n=541, y2: 20.697 against T 24.639, trivial character t=0).
  - RUN-CZLIFT-d37ca4: -4.070 (D=-163, p=347, n=383, x4: 19.725 against T 23.794, at t=110).
- Closest shuffled approach: -4.191 on RUN-CZLIFT-037e5f and -4.650 on
  RUN-CZLIFT-d37ca4. Mean threshold: 22.150 and 21.345.
- Power (rt_scope_output.json, agreeing with VAL PTM-1):
  - 30 of 72 records have h <= T. All of them have n <= 41: 12 on seed
    20261009 (6 CM, 6 random) and 18 on seed 20261010 (9 CM, 9 random). On
    these records X <= h <= T holds for any digit sequence at all.
  - The other 42 records (n >= 47; 33 CM, 9 random; 42 distinct (p, n);
    53 <= p <= 571, 47 <= n <= 613) have rho_min between 0.284 and 0.978,
    median 0.502. 21 of the 42 need tau >= 0.5 to register.
- Planted object PTM-1 (f(k) = floor(p k / n) mod p) through the frozen
  instrument: it spikes on 42/42 power-bearing records and 0/30 blind ones
  (excess +1.01 to +281.2, median +65.8). Instrument and validator spectra
  agree to 9.1e-13.
- Known-leaking digit functions through the unchanged run.spectrum (RT R1):
  - CHIRP floor(p (k^2 mod n)/n) and INV floor(p (k^-1 mod n)/n) determine k on
    the half range. The frozen rule fires on neither, on any of the 72
    records.
  - LEGMSB, a digit whose Legendre symbol is one exact bit of k, stays at or
    below 0.68 T on all 72 records.
  - SPARSE (a planted leak on about 0.6 sqrt(T h) positions) is invisible on
    40/42 power-bearing records. WEAK (a planted leak with per-k probability
    0.6 rho_min) is invisible on 38/42.
  - LSB (k mod 2 in a low bit) is detected on 29/42.
  - The generator-covariant fold FOLD_j spikes in 182/210 cases: all records
    with n >= 109, but only 37/65 cases with 47 <= n < 100.
- Digit 0 (x(kP) mod p) determines k up to sign. Its real maxima sit below
  the Exp(1) expectation: mean excess -1.03 on the 64 non-D=-3 power-bearing
  rows.
- CM D=-3 y-digits 1..4 (40 power-bearing rows): mean excess of the row maximum
  over ln(N/2) + gamma is +2.60 real, +3.65 shuffled and +0.04 uniform. The
  maximum sits at t=0 in 32/40 real rows and 36/40 shuffled rows. The order-3
  automorphism identity y(s_tor([lambda k]P)) = y(s_tor([k]P)) holds exactly on
  10/10 records (RT R2, rt_d3.py, with a third independent torsion lift).
- Unexpected observation, preserved: on RUN-CZLIFT-037e5f, D=-3, p=439,
  n=151, y4, the non-DC maximum is 17.72 at (a=33, t=39), where
  t(1-lambda) = -1 mod n. It exceeds all 300 symmetry-matched and all 300
  uniform null draws, and stays below T = 23.10. The pooled test of that
  frequency class on the other 39 rows gives Fisher chi^2 = 76.0 on 78 dof.

## Comparison

- Against the frozen criteria: the success criterion is met on both seeds and
  the falsification criterion is not met. No invalidation rule fires
  (VAL frozen_criteria). This repeats the observation DEC-20261009-6aef7a
  recorded.
- Against the uniform control, on the 420 uniform power-bearing rows: row
  maxima fit ln N - 0.92 + 0.90 G, where G is standard Gumbel. Real maxima
  outside D=-3 y-digits sit at the same level: mean excess -0.29 on the
  higher digits against -0.28 uniform. Within the instrument's floor, the real
  higher-digit spectra are indistinguishable from uniform digits.
- Against the shuffled control, the comparison is not valid as designed. The
  shuffled series has three problems (RT R2):
  - It shares the permutation-invariant t=0 term with the real series.
  - It samples a random half of the full range, which reintroduces the
    negation mirror that the half-range design removed from the real series:
    x(-k) = x(k), and a_i(y(-k)) = p-1-a_i(y(k)).
  - On D=-3 it inherits the mu_6 orbits.

  Its per-row spike probability at margin 12 reaches 0.167 (p=571, n=541, y1),
  against a stated null of about e^-12. The probability that both seeds show
  zero shuffled spikes was about 0.47. Under the per-digit aggregate reading
  of the falsification rule, this artifact would veto a real spike on seed
  20261009 with probability up to 0.22. The bias runs toward the hypothesis.
- Against a symmetry-matched null for D=-3 (a random mu_6-invariant function
  with y(-k) = -y(k)): the real DC maxima have mean rank 0.44, and the non-DC
  maxima average +0.14 above the matched mean. The D=-3 elevation is fully
  explained by the symmetry. No real excess is hidden in these runs.
- Against the planted leak PTM-1: the instrument separates a gross linear leak
  from noise on every power-bearing record. Against CHIRP, INV, LEGMSB, sparse
  and weak leaks, and digit 0 itself, it does not.
- Arms: both arms give 0 spikes. 33 CM records and 9 random records bear
  power, so the "arbitrary lift" arm rests on 9 records, each with one naive
  integer lift.
- Threshold: margin 12 gives a per-seed family-wise level of 1.8e-3 over the
  288 higher-digit rows. A 5% Bonferroni margin would be 9.98. Using it would
  unblind 3 of the 30 blind records and lower rho_min by a median factor of
  0.955. Power is limited by h (n <= 613) and by the maximum over about 10^5
  pairs, not by the margin.

## Inference

- The data support this narrow statement:

  > On the 42 power-bearing records of RUN-CZLIFT-037e5f and RUN-CZLIFT-d37ca4,
  > no single-digit function a_i(x(s_tor([k]P))) or a_i(y(s_tor([k]P))),
  > i = 0..4, has half-range normalised correlation tau >= rho_min(p,n) with any
  > single pair (nontrivial additive character of F_p, character of Z/n).
  >
  > The 42 records are 33 CM-canonical class-number-one integer models and 9
  > random curves with one naive integer lift, with 53 <= p <= 571,
  > 47 <= n <= 613, one random generator per record and precision 5.
  > rho_min ranges from 0.28 to 0.98 (median 0.50). For generator-covariant
  > leaks through the even x-digits at n < 109, the floor is about 1.44 times
  > higher.

  Equivalently: no improvement meeting the predefined threshold was observed
  over the tested instances, parameters, solver and resource budget. On the j = 0
  pair the statement concerns digit-value bias, not dependence on k.
- The data do not discriminate on the hypothesis's title claim, that no p-adic
  digit of the torsion section correlates with the discrete logarithm. Digit 0
  determines k up to sign and is white, and so is a uniform digit that is
  independent of k. The statistic separates "single-character-correlated above
  rho_min" from "not", and nothing finer. On the title claim this experiment
  is inconclusive. It is not support.
- The 30 records with n <= 41 carry no information. Their whiteness is the
  trivial bound X <= h <= T, a derivation that needs no data
  (VAL PTM-1 scope_restriction).
- The clause of H-CZLIFT-fba874 that reads "exactly as for the same digits
  re-indexed by a random permutation" held by chance (probability about 0.47).
  It does not confirm the null calibration.
- decision_impact.on_positive in the specification is not warranted. It would
  close the canonical-section clause of H2 at the character level and add a
  pointer to KN-TECH-73630e. The excluded class is single-character
  correlation tau >= 0.28-0.98 at n <= 613. By the red team's
  order-of-magnitude estimate, that is about 50 bits of correlation away from
  the attack-relevant regime (tau* ~ n^{-1/4} up to polylog factors, about
  2^-53 at 256-bit n), and no scaling law connects the two.
- Resource reading. This measurement is not an obstruction. It is a toy-scale
  sanity check of a hypothesis that another theory needs:
  - s_tor is a computable homomorphism, so g(k) = psi(a_i(s_tor([k]P))) has
    exact shift-query access, g(d + r), through Q + [r]P.
  - The Fourier mass tau = max_j |g^(chi_j)| is then the parameter of a
    Fourier-learning hidden-number attack (Boneh-Venkatesan;
    Akavia-Goldwasser-Safra), which costs about tau^-2 polylog(n) s_tor
    evaluations.
  - Whiteness for every j is the hypothesis under which that route fails.
  - The exponent-relevant unknown is how max_j tau scales with n for digits
    i >= 1. For digit 0, Weil-type subgroup-sum bounds give O(sqrt p)
    cancellation. For digits i >= 1, no such bound is known.

  This is filed as KN-OPEN-d3a6f0.

## Limitation

- Toy tier: p <= 571 (fields of at most 10 bits) and n <= 613. Nothing
  transfers to larger n, to cryptographic sizes or to any deployed curve.
  rho_min falls only like sqrt(ln(pn)/n).
- The tested class is narrow:
  - additive characters of F_p on one digit, against characters of Z/n, one
    pair at a time, on the half range;
  - precision 5, so digits 0..4 only;
  - one Weierstrass model per curve (the CM integer model, or the naive (a, b)
    lift) and one random generator per record.

  Not tested: multiplicative characters of digits, multi-digit or nonlinear
  functions, other models or lifts, and other generators. Digit functions
  depend on the model, because a change of Weierstrass model over Z_p mixes
  digits.
- The shuffled control is contaminated, and the shuffled-versus-real
  comparison is graded not_isolated. This caps evidence strength at
  preliminary.
- The pre-registered null (|S|^2/h ~ Exp(1) per pair, Gumbel maximum) is an
  unnumbered random-model heuristic. It fails for D=-3 y-digits, for digit 0
  (whose maxima sit below the null) and for the shuffled series. The margin of
  12 absorbed these deviations but was not calibrated to them.
- The frozen falsification criterion has two readings: per curve-row, or per
  digit aggregated over curves. Under the aggregate reading, a planted DL
  function would not falsify (VAL PTM-1 decision_rule_note). The zero counts
  here make the ambiguity moot for this run set. It is load-bearing for any
  successor.
- The leak-class results (CHIRP, INV, LEGMSB, SPARSE, WEAK, FOLD) use one
  seeded instance per (p, n) and kind. Their power fractions are indicative,
  not power curves. The breakeven tau* is the red team's order-of-magnitude
  estimate with unoptimised constants.
- The environment records no numpy or sympy version, no runtime lock and no
  peak memory. This is mitigated by the exact independent replay on numpy
  2.5.3 and Python 3.13.16.
- This analysis was written without a shell. Every number above is read from
  the run manifests, rt_scope_output.json, VAL-20261022-55676f or
  RT-20261023-dcb217. No raw run artifact was recomputed here.
