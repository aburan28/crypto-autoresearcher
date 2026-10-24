# EXP-CZLIFT-a255fc analysis

Hypothesis H-CZLIFT-9a32e9, question RQ-CZLIFT-b9f765, goal GOAL-CZLIFT-1516d5.
Runs RUN-CZLIFT-74f172 (hmax 1e5, twists) and RUN-CZLIFT-490b33 (hmax 3e5,
ladder only). Evidence EV-CZLIFT-376eee, decision DEC-20261023-26a6de. Review
inputs: validation VAL-20261022-9ab683 (`reports/validation-20261022/`), ruling
CORR-20261023-0657da, red team RT-20261023-481827 (`reports/redteam-20261023/`).
Clause labels C1 to C5 follow the red-team report: C1 growth law, C2 uniform
reduction, C3 H_half scaling, C4 "global lifts are useless" (exponential
height), C5 twists and E(K).

## Observation

Validity of the run set (checked before anything below was read as evidence):

- O-V1. Run count: the frozen trial plan has 2 trials, and there are 2 run
  directories, mapped one to one (census-h1e5-with-twists -> RUN-CZLIFT-74f172,
  census-h3e5-ladder-only -> RUN-CZLIFT-490b33). Both execution receipts read
  `status: output_validated`, `returncode: 0`, `check_returncode: 0`, with plan
  sha256 b23422ba... and launch authority commit d13377cd. Both manifests read
  `status: completed_valid`, `valid: true`, `seed: null`, `deterministic: true`.
- O-V2. Custody and recomputation (VAL-20261022-9ab683 J1, MR-1 to MR-6): 20 of
  20 run files hash to their receipts, the frozen sources match the trial plan,
  and every frozen metric recomputes bit-identically from raw-result.json on
  both runs. An implementation that shares no producer code reproduces all 64
  grid counts and 1024 coverage cells per run up to H = 3e4, and all 172 twist
  rows. The red team's own sieve reproduces the same counts and the `distinct`
  values of all 2048 coverage cells with H <= 3e4 (0 mismatches).
- O-V3. Seeds: the enumeration is deterministic, and the spec lists
  `replication.seeds: []`. There is nothing to check.
- O-V4. Controls. Control 1 (11a1 constant at 5) and invalidation rule 3 fire
  as written at H = 10, where the count is 3. That count is arithmetically
  correct (blind search and group-law enumeration). CORR-20261023-0657da scopes
  the control and the rule to H >= 16. Under that ruling both runs are
  admissible: N_E(H) = 5 for every grid H >= 30 on both runs. Control 2 holds
  on the coverage rows; on twist rows O is counted twice (+1). Control 3 holds
  (88 of 88 sample points verify; the H = 300 recounts are 5 and 21). Control 4
  holds.
- O-V5. Recorded defects that leave the results valid. check.py imports the
  driver, so it is not an independent checker; the validator's recomputation
  and replay stand in for it. Manifest code.commit for RUN-CZLIFT-490b33 is
  cab1e1eb against launch commit d13377cd, because the revision was read after
  the run (AC-5); the executed sources are pinned by hash. No library versions
  and no memory record are kept (AC-6).

Frozen metrics (manifest values):

- O-1. Coverage ratio (distinct residues / N_p(1 - (1 - 1/N_p)^N), frozen cells
  with N >= 30 and modelled coverage <= 0.9 N_p): median 1.033040 over 693 cells
  (RUN-CZLIFT-74f172) and 1.033250 over 785 cells (RUN-CZLIFT-490b33). The
  fraction of cells above 1.5 is 0.0 and the fraction below 0.5 is 0.0 on both
  runs. Cell ratios range over [0.8533, 1.4262] and [0.8501, 1.4577].
- O-2. Growth slopes (OLS of log N_E on log log H, H in [100, hmax]),
  main / replication, against r/2. 37a1 0.535 / 0.517 (0.5); 389a1 0.992 /
  1.001 (1.0); 5077a1 1.421 / 1.409 (1.5); 234446a1 1.966 / 1.965 (2.0);
  19047851a1 2.310 / 2.290 (2.5); 5187563742a1 2.837 / 2.874 (3.0);
  382623908456a1 3.181 / 3.220 (3.5). The largest deviation is 0.319 / 0.280
  (rank 7). 11a1 has N_E(hmax) = 5 and is exempt.
- O-3. H_half scaling slopes on the frozen grid (log log H_half on log p, at
  least 3 resolved primes), main / replication, against 2/r. 5077a1 0.590 /
  0.590 (0.667, 4 primes); 234446a1 0.415 / 0.415 (0.5); 19047851a1 0.406 /
  0.406 (0.4); 5187563742a1 0.375 / 0.364 (0.333); 382623908456a1 0.320 /
  0.312 (0.286). 11a1, 37a1 and 389a1 have fewer than 3 resolved primes.
- O-4. Twists (main run only): twist union ratio median 1.0036 over 129 cells,
  0 cells above 1.5.

Reviewer computations, read from the committed review artifacts:

- O-5. Coverage calibration. The seeded uniform null with independent cells
  (VAL PTM-1, 200 reps, seed 20261022) has median of medians 1.0017 with 95
  percent band [1.0010, 1.0023] (main) and 1.0016 [1.0007, 1.0022]
  (replication); 0 of 200 reps reach the observed median. The nested,
  negation-paired uniform null (rt_a, seed 20261023) gives 1.0025
  [1.0010, 1.0041] on both runs. The random-lattice-ball null (rt_b) gives
  1.0125 [1.0074, 1.0179] and 1.0134 [1.0087, 1.0179], with 0 of 200 reps
  reaching the observed median.
- O-6. Cell-level tails (rt_a). Under the exact negation-paired occupancy null,
  97 (main) and 123 (replication) frozen cells have upper-tail probability
  below 1e-6, and 2 and 6 cells have lower-tail probability below 1e-6.
  Collision-free cells are 0.569 and 0.557 of cells observed, against 0.244
  and 0.237 expected under the paired null. Lost residues are 0.67 and 0.70 of
  the model's.
- O-7. Mechanism controls on cells with H <= 3e4, which are identical in both
  runs. With the actual point set in exact Mordell-Weil coordinates under a
  random homomorphism (rt_e, 598 cells, observed 1.0322) the null is 1.0116
  [1.0080, 1.0164], 0 of 200 reps. An index-matched random homomorphism (rt_g
  R0, 470 cyclic cells, observed 1.0338) gives 1.0139 [1.0089, 1.0192], 0 of
  100 reps. The same, conditioned on lambda1^2(ker) >= 2 log p (rt_g R1), gives
  1.0350 [1.0294, 1.0398], with 69 of 100 reps at or above the observed value.
- O-8. Kernel floor (rt_f, rt_h Q3). Over 86 cyclic (curve, p) pairs, the
  minimum of lambda1^2(ker red_p) - 2 log p is +0.91 nats of PARI canonical
  height, at 234446a1. The per-curve minima for ranks 5..7 are 2.27, 2.32 and
  3.36.
- O-9. Index (rt_c). red_p(E(Q)) is a proper subgroup on 14 of 112 rank >= 1
  (curve, p) pairs. For 37a1 at p = 211, N_p = 225 and the image has order
  45 (index 5). At p = 293, N_p = 296 and the image has order 74 (index 4).
  Coverage at H = 3e5 is 0.1378 and 0.1047. Every 37a1 coverage row is
  maximally spread: distinct = min(N, N_p) on 144 of 144 rows (main) and 160
  of 160 (replication) (VAL PTM-1).
- O-10. Volume law (rt_h Q1, RUN-CZLIFT-490b33, PARI regulators from height
  Grams of the census points). N_E(H) / (V_r (log H)^{r/2} / sqrt(Reg)) lies in
  [0.963, 1.309] for 1e3 <= H <= 3e5 on ranks 1..7, and in [0.987, 1.085] at
  H = 3e5. r independent points are verified on every rank >= 1 curve; rank
  upper bounds are not.
- O-11. H_half off the grid (rt_d, rt_h Q2; threshold N = N_p ln 2), slope
  +- 1-sigma OLS SE, main / replication, against 2/r. r=3 0.696 +- 0.019
  (0.667); r=4 0.500 +- 0.020 / 0.507 +- 0.015 (0.5); r=5 0.416 +- 0.022 /
  0.419 +- 0.017 (0.4); r=6 0.356 +- 0.008 / 0.352 +- 0.006 (0.333);
  r=7 0.298 +- 0.006 / 0.296 +- 0.005 (0.286). The fits use 4 to 9 primes in
  p = 103..2417.
- O-12. Half-coverage height (rt_h Q5). On every resolved (curve, p),
  log H_half / log p <= 1.71 (maximum at 234446a1, p = 839). For ranks 5..7
  the maxima are 1.531, 1.696 and 1.619. Rank 2 resolves only p = 103 (1.49).
- O-13. Twist content (rt_d, VAL MR-7). 21 of 172 twist rows contain a twist
  point besides O, and 3 of 24 (curve, D) twists have any: 11a1 D=-7, 11a1
  D=13 and 389a1 D=-1. The 8 frozen twist cells with a twist point all come
  from 389a1 D=-1. Counting O once leaves 86 cells with median 1.0242
  (conventional) or 1.0253 (upper).
- O-14. Planted control (VAL PTM-1). A maximally spread planted set on the
  frozen cells gives median 1.0514 with frac_above_1.5 0.027 (main), and 1.0548
  with 0.032 (replication). Both pass the frozen success criterion. Any point
  set satisfies ratio <= min(x,1)/(1 - e^-x) with x = N/N_p, so the ratio
  exceeds 1.2 only for x > 0.376. The median x over frozen cells is 0.10.

## Comparison

- C-1. Frozen success criterion against O-1 to O-4: coverage median in
  [0.8, 1.2] holds on both runs; frac_above_1.5 < 0.05 holds on both runs;
  every growth slope lies within 1 of r/2 on both runs; the twist median lies
  in [0.8, 1.2] on the main run. The frozen criterion reads met, as
  DEC-20261009-9f9254 recorded. The frozen falsification criterion does not
  fire. No protocol amendment changes either criterion.
- C-2. Discriminating power of the frozen coverage criterion (O-14): a
  maximally spread planted set passes it, and on these cells no point set can
  push the median above 1.2 or frac_above_1.5 to 0.05. The upper side of the
  criterion cannot fail. Its lower side would catch clustering (a clustered
  planted set gives median 0.016).
- C-3. Observed median against calibrated nulls (O-5, O-7): 1.0330 / 1.0333
  lies above every uniform null band (upper edges 1.0023 to 1.0041), above the
  random-lattice null (upper edge 1.0179), above the actual-point-set random
  homomorphism (upper edge 1.0164) and above the index-matched homomorphism
  (upper edge 1.0192). It lies inside the kernel-floor-conditioned structured
  null [1.0294, 1.0398] (observed 1.0338 on the same 470 cells).
- C-4. Excess decomposition (O-5, O-7). Generic lattice geometry accounts for
  about 0.012 of the 0.032 excess. The kernel-floor condition accounts for the
  rest within the band.
- C-5. Growth slope against r/2 (O-2) and count against the volume law
  (O-10). The slope deviations (at most 0.32) are well inside the frozen
  tolerance of 1. That tolerance also admits r +- 1 for every curve, so it does
  not separate adjacent ranks. The constant-bearing volume law agrees within
  [0.963, 1.309].
- C-6. H_half slope against 2/r. On the grid (O-3), all slopes lie within the
  frozen [0.5, 2] x 2/r. 234446a1 at 0.415 +- 0.030 lies 2.8 SE below 0.5.
  Off the grid (O-11), every slope equals 2/r within 0 to +10 percent. The
  frozen tolerance cannot separate r from r +- 1.
- C-7. Toy-scale half-coverage height against "exponential in p^{2/r}"
  (O-12): at every resolved toy prime, H_half <= p^{1.71}, which is polynomial
  in p. The target log p = 177.4 (p = 2^256) is 23 to 31 times the largest
  fitted log p (7.79).
- C-8. Twist clause against the instrument (O-13). The prediction concerns
  E(K) points, which grow like (log H)^{(r + r_D)/2}. The instrument counts
  E(Q) union E^D(Q), which grows like (log H)^{max(r, r_D)/2}. Only one twist
  contributes twist-bearing frozen cells.

## Inference

Derivation note. This is the refutation artifact for EV-CZLIFT-376eee
(`proof_status: derivation`). Each step is checkable by an independent reader.
Ingredients marked "recalled" are classical and were not re-derived here.

- D1 (homomorphism). Let p be a prime of good reduction for the minimal model.
  red_p : E(Q) -> E(F_p) is a group homomorphism (recalled: Silverman, AEC,
  VII.2.1). For any S in E(Q), red_p(S) lies in the subgroup
  G_p = red_p(E(Q)) of index k_p in E(F_p). Two points P != Q of S have the
  same reduction iff P - Q lies in ker red_p.
- D2 (kernel height floor). A point K != O of E(Q) is in ker red_p iff x(K)
  has negative p-adic valuation, i.e. x(K) = a/d^2 in lowest terms with p | d.
  Then H(x(K)) >= d^2 >= p^2 and h(K) = log H(x(K)) >= 2 log p. With the
  bounded difference |h^ - h| <= c_E on E(Q) (recalled: Silverman's
  difference bound; PARI normalization h^ = lim h(nP)/n^2), every non-zero
  kernel vector has h^(K) >= 2 log p - c_E. O-8 is consistent: measured
  lambda1^2(ker) >= 2 log p + 0.91.
- D3 (collision law). For P, Q in S_H (naive height <= H), the parallelogram
  law gives h^(P - Q) <= 2 h^(P) + 2 h^(Q) <= 4 (log H + c_E). So S_H has no
  collision mod p at all while 4 (log H + c_E) < 2 log p - c_E. Above that
  height, collisions come only from the few kernel vectors of h^ >= 2 log p -
  c_E inside a ball of radius 2 sqrt(log H + c_E). Each such K makes every
  pair (P, P - K) inside the ball collide. Collisions are therefore suppressed
  at short distance and clumped on few kernel vectors. Under N independent
  uniform draws, each pair collides with probability 1/N_p independently of
  height. The two laws differ, in both directions. That matches O-6 (97 and
  123 cells with upper tail < 1e-6, 2 and 6 with lower tail < 1e-6) and the
  clumping instances of rt_c (389a1, p = 149, H = 3e4: 28 collisions from one
  +-K).
- D4 (rank-1 exactness). Suppose S_H lies in {nP : |n| <= m} for a single P.
  rt_c verifies this for 37a1 and P = (0,0) up to H = 3e4. Then red_p is
  injective on S_H whenever ord(red_p P) > 2m, so distinct = N exactly.
  Independent uniform draws give expectation N_p(1 - (1 - 1/N_p)^N) < N for
  N >= 2. The observed maximal spread on every 37a1 row (O-9) is therefore
  structural, not a fluctuation.
- D5 (index cap). For every H, coverage <= |G_p|/N_p = 1/k_p. If k_p >= 3,
  then H_half(p) is infinite. Instances: 37a1 at p = 211 (k = 5) and p = 293
  (k = 4) (O-9). This assumes E(Q) = Z (0,0) for 37a1 (recalled: rank 1 and
  generator from the Cremona tables; only the lower bound is verified here).
  This contradicts the finite-H_half formula of C3 read uniformly in p. It
  also contradicts the "uniformly in p" scope of HEUR-CZLIFT-UNIFORM at
  heights where N > 45: at N = 0.9 N_p the model predicts about 0.59 N_p, about
  133 distinct residues, against the cap of 45 (reviewer arithmetic). In the
  tested cells 37a1 has N <= 31 < 45, so the cap binds nowhere in the data. It
  points in the direction that makes lifting harder.
- D6 (pigeonhole cap on attacker value). For any S, distinct <= |S|. Covering
  N_p/2 residues therefore needs N >= N_p/2, against N_p ln 2 under the uniform
  model. Any spread effect saves at most a factor 2 ln 2 = 1.386 in N, i.e.
  Delta log log H_half <= (2/r) ln(2 ln 2): 0.327 at r = 2, 0.093 at r = 7
  (rt_h Q4). The measured excess cannot change the exponent of H_half.
- D7 (what carries C3 and C4). Pigeonhole (coverage <= N_E(H)/N_p) and the
  volume law N_E(H) = V_r (log H)^{r/2} / sqrt(Reg) (1 + o(1)) (recalled: Lang,
  Fundamentals of Diophantine Geometry, 1983, Ch. 5, Thm 7.4, as cited in
  JKSST 2000) give, for a fixed E, log H_half >= (sqrt(Reg) N_p / (2 V_r))^{2/r}
  (1 + o(1)). The matching upper bound additionally needs k_p <= 2 and no gross
  clustering. The fitted H_half slope is this inverse growth exponent read
  through pigeonhole; it is not an independent measurement.

Clause readings:

- I-C1 (growth law): supported at toy scope. Exhaustive, independently
  replayed counts agree with the constant-bearing volume law within
  [0.963, 1.309] for 1e3 <= H <= 3e5 on ranks 1..7 (O-10), and 11a1 stays at
  its 5 torsion points for H >= 30. The frozen slope check passes (C-5) but
  does not confirm rank labels.
- I-C2 (uniform reduction): contradicted as stated. The frozen criterion is
  met (C-1) but cannot fail on its upper side (C-2), so meeting it is no
  support. Calibrated, post-hoc reviewer analyses on both runs reject
  independent-uniform reduction at the cell level and in the median (C-3,
  O-6). D1 to D4 give the mechanism: a lattice ball under a homomorphism whose
  kernel has a height floor. A one-assumption structured null reproduces the
  median (C-3, C-4). HEUR-CZLIFT-UNIFORM's random-model justification ("no
  algebraic relation ties small global points to a structured subset") is
  false: reduction is a homomorphism. The frozen falsification condition of
  HEUR-CZLIFT-UNIFORM did not fire. The adverse reading rests on D1 to D5 and
  on non-pre-registered analyses, so it is a `weaken`, not a `reject_scoped`.
- I-C3 (H_half scaling): consistent and derivative. The off-grid slopes
  match 2/r within 0 to +10 percent (C-6), as D7 predicts from C1. The
  "+ O(1)" is not uniform in p: by D5 it is infinite where k_p >= 3. This
  breaks the formula as stated, in the safe direction.
- I-C4 (exponential height; "useless"): not measured. At toy scale
  half-coverage is polynomial in p (C-7). The asymptotic statement is the
  conditional consequence D7, under transfer assumptions T1 to T4 that the
  records never stated:
  - T1: the lift has rank r fixed independently of p. The bound weakens to
    polynomial height once r reaches about r*(p) = 2 log p / log(2 log p),
    which is 60.4 at p = 2^256.
  - T2: c_E and the naive-canonical height difference stay bounded along the
    lifts.
  - T3: [E(F_p) : red_p E(Q)] <= 2.
  - T4: a fixed E/Q stands in for an attacker's p-dependent lift.

  Height is also not attack cost. log H ~ p^{2/r} bits is below p^{1/2} for
  r >= 5, so the height bound is no cost separation from Pollard rho (red-team
  O7).
- I-C5 (twists, E(K)): untested (C-8). The frozen twist median is not
  evidence about E(K), and the hypothesis's parenthetical "N_E + N_{E^D},
  still (log H)^{r_K/2}" is internally inconsistent.
- I-6 (excess and attacker relevance): the excess over the uniform model is
  real and structural, and by D6 it gives an attacker at most an O(1) shift in
  log log H_half. The kernel floor D2 makes relations among reductions of
  small global points cost h^ >= 2 log p - c_E, which works against
  relation-finding.
- I-7 (earlier readings): the observation readings in DEC-20261009-9f9254
  ("reductions cover E(F_p) like uniform points"; the twist union "covers
  E(F_p) exactly as the uniform model ... predicts"; "Consistent at toy scope"
  for global_lifts_fail_by_counting) overstate the data. DEC-20261023-26a6de
  supersedes them at clause level. The earlier record stays as written.

## Limitation

- L-1. Toy tier: p <= 20011 (15 bits); H <= 3e5. H_half is resolved only at
  p = 103..2417, with 4 to 10 primes per curve. Nothing is measured at
  cryptographic p; C4 beyond toy scale is conditional on T1 to T4.
- L-2. The adverse C2 reading uses analyses chosen after the outcome (red-team
  nulls, tails, structured null). Neither the per-cell tail nor the structured
  null was pre-registered. The two runs share every point up to H = 1e5, so
  they are not independent samples for coverage; only the 1e5 and 3e5 cells of
  the replication add data. A pre-registered replication on curves and primes
  disjoint from this census is required before any `reject_scoped`.
- L-3. Structured-null and Mordell-Weil-coordinate analyses cover cells with
  H <= 3e4 (598 cells, 470 at cyclic primes). The 95 (main) and 187
  (replication) cells at 1e5 and 3e5 were not re-modelled, and no independent
  replay covers them either. The kernel-floor analysis assumes cyclic E(F_p)
  and skips 26 of 112 (curve, p) pairs.
- L-4. Rank labels are recalled; lower bounds are verified (non-singular height
  Grams), upper bounds are not. D4 and D5 rely on the recalled Mordell-Weil
  group of 37a1.
- L-5. Specification discrepancies, none of which changes a frozen outcome:
  primes 103..20011 against "101..20000" (without p = 20011 the medians are
  1.0389 / 1.0393); cell domain "modelled coverage <= 0.9" against
  "N <= 0.9 N_p" (621 / 698 cells, median 1.0265); O double-counted in twist
  cells; the hypothesis's interpretation_limits say "10^6 on the replication"
  while 3e5 was run.
- L-6. The derivation note is a written argument (`derivation`), not a
  machine-checked proof. The counterexample instances (37a1 p = 211 / 293
  index; 389a1 p = 149 kernel point) are in rt_c output but are not yet packaged
  as certificates with an independent re-checker.
- L-7. The producer's checker is not independent of the driver. Independence
  of the numbers rests on the validator's replay and the red team's sieve.
  Environment records lack library versions and memory use.
- L-8. Citation provenance: Neron 1965 is an imprecise attribution for the
  count with its constant; Lang 1983 Ch. 5 Thm 7.4 is the cited source, seen
  through JKSST 2000. Silverman-Suzuki and Huang-Kueh-Tan are unverified
  beyond bibliography. The census quantifies only the counting ingredient of
  JKSST's Theorem 4.1, not the theorem.
