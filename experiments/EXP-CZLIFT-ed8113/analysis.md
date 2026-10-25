# EXP-CZLIFT-ed8113 analysis (evidence review DEC-20261023-488023)

Hypothesis H-CZLIFT-cb95b8, restated as tested by CORR-20261023-4ffd7e.
Question RQ-CZLIFT-b9f765; goal GOAL-CZLIFT-1516d5. Runs RUN-CZLIFT-c3f8a8
(seed 20261009) and RUN-CZLIFT-218843 (seed 20261010). Review inputs:
VAL-20261022-b08129 (`reports/validation-20261022/validation_report.yaml`,
passed) and RT-20261023-d796bb (`reports/redteam-20261023/redteam_report.yaml`,
R1, R2 and PTM-1 break). Evidence record EV-CZLIFT-ee9b23. Written by the
Coordinator without a shell. Every number below is a recorded run value or a
reviewer value read by key from the committed review artifacts. The only
values computed here are the hand identities in I-1.

## Observation

O-1. Validity, checked before interpretation:

- Run count: 2 of 2 planned trials (trial-plan.json), both receipts
  `output_validated` with returncode 0 and check_returncode 0. 2 of 4
  budgeted runs used. Wall times 199.40 s and 200.39 s against 3600 s.
- Manifests: schema-complete; run commit 025949c406 descends from the freeze
  commit 172ec3c94f, and every frozen source is hash-identical. dirty false
  (computed at write time). 9 of 9 artifact hashes per run recompute. The
  six required artifacts are present.
- Seeds: 20261009 and 20261010 agree across specification, trial plan,
  command, manifest and stdout.
- Raw/summary agreement: the validator recomputed every frozen metric from
  `raw` (j2_recompute.py) with no mismatch. It replayed all 3200 trials and 48
  controls with a sealed blind search on inputs regenerated through the
  frozen sampler: 3200 of 3200 outcomes agree, and mean heights agree to
  <= 1.8e-14. 16 cells per seed, 100 valid trials per cell, 0 singular
  exclusions.
- Controls: planted (2, -1) detected 24 of 24 on each seed and 48 of 48 in
  the blind re-derivation. Edge-of-bound probe: (5, -6) and (6, -5, -1) are
  found, and (6, -7) is correctly not found.
- Certificates: both runs declare `certificate.kind: none` (measurement
  runs). The one recorded dependence is not an attack solve. It was
  re-verified by independent code: the validator's exact rational blind
  search and the red team's PARI ellmul/elladd. See I-1 for the hand check.

The run set is admissible evidence. Nothing goes back to the Executor.

O-2. Primary metrics (recorded, recomputed):

| seed | run | dependent / valid | rate | r = 2 | r = 3 | one-sided 95% upper | controls |
|---|---|---|---|---|---|---|---|
| 20261009 | RUN-CZLIFT-c3f8a8 | 1 / 1600 | 0.000625 | 0.00125 | 0.0 | 0.00296 | 24 / 24 |
| 20261010 | RUN-CZLIFT-218843 | 0 / 1600 | 0.0 | 0.0 | 0.0 | 0.00187 | 24 / 24 |
| pooled | both | 1 / 3200 | 0.0003125 | 1 / 1600 | 0 / 1600 | 0.00148 | 48 / 48 |

The pooled two-sided exact 95 percent interval is [7.9e-6, 1.74e-3]
(rt_stats.json). The single dependence is at p = 101, r = 2, seed 20261009,
trial index 61. The inputs are (a, b) = (90, 49) mod 101 and points
(77, 86) and (48, 86), with lifts P~1 = (-24, -15) and P~2 = (48, -15). The
fitted curve is Y^2 = X^3 - 1728 X - 27423, and the recorded relation is
[-2, -1].

O-3. Secondary metric: height_ratio_point_over_log_p, recorded per prime,
computed over the r = 2 cell only (validator F2; differs from a pooled
definition by <= 0.0159):

- seed 20261009: 0.6318, 0.6888, 0.7316, 0.7403, 0.7711, 0.7989, 0.8079, 0.8099
- seed 20261010: 0.6553, 0.7136, 0.7170, 0.7513, 0.7742, 0.7912, 0.7901, 0.8308

The primes run from p = 101 to p = 12809 in both lists.

O-4. Sampler (validator F1; red-team rt_sampler_probe.json): harness/czlift.py
random_point never returns y = 0. On three p = 101 curves with full
2-torsion it returned 0 such points in 60000 draws, where about 1820 are
expected uniformly; 0 of 8000 replayed producer points have Y = 0. The
specification and hypothesis text do not state this restriction. The
validator's blind sampler admits y = 0 and gave 8/1600 dependent trials,
every one a 2-torsion relation at p in {101, 211}; it gave 0/1592 among
trials with no y = 0 point.

O-5. Reviewer measurements on the exactly replayed inputs. These are review
artifacts, not frozen metrics.

- Unbounded control (rt_regulator_control.json; Neron-Tate height-pairing
  determinant, PARI 2.17.2 at realprecision 77): 3199 of 3200 tuples are
  Z-independent. The minimum normalized determinant is 0.440 (r = 2) and
  0.539 (r = 3). There are no torsion points. The one dependent tuple is
  the recorded one.
- Mod-p null (rt_modp_null.json): the identical bounded search on the
  residues finds a relation with max |n| <= 6 mod p in 1261 of 3200 trials
  (r = 2: 254 of 1600; r = 3: 1007 of 1600). For r = 2 at p >= 3203 the
  count is 3 of 600.
- Lift-survival fraction: 1 of 1261 = 7.9e-4, exact 95 percent CI
  [2.0e-5, 4.4e-3]. For r = 2 it is 1 of 254, CI [1.0e-4, 0.022]; for r = 3
  it is 0 of 1007, CI [0, 3.7e-3].
- Median smallest mod-p relation, max |n|, per cell:
  - r = 2: 6, 8, 10-11, 15.5-17, 21-21.5, 29-32.5, 45.5-46.5 and 60.5-61
    for p = 101 ... 12809.
  - r = 3: 3, 3, 4, 5, 6, 8, 9-10.5 and 13.
- PTM objects (rt_ptm_torsion_object.json, rt_ptm_389a1.json):
  - In-distribution pairs (T, P) at p = 6421, with T of order 7 on
    Y^2 = X^3 - 309643 X + 61048006 and of order 8 on
    Y^2 = X^3 - 1976427 X + 1069210746. The producer's fit reproduces each
    curve, and its search returns None at bound 6 although (7, 0),
    respectively (8, 0), holds.
  - The 389a1 generators correctly return no relation at bound 6 or 12.
- Literature (red-team citations_checked; JKSST 2000 read in full):
  - Theorem 4.1 gives success < C0/p conditionally on Lang's height
    conjecture and log|D| >= C1 max hhat. C0 ~ 1e4 (r = 2) and ~ 1e12
    (r = 3).
  - Section 5 reports frequent dependence at small discriminants.
  - The paper's empirical law, applied to the replayed minimal
    discriminants, predicts 0.855 dependent trials over both seeds;
    P(0 on both seeds) = 0.43.
- Lemma 4.1 ratio, C1 = log|Delta_min| / max hhat: minimum 11.24; medians
  21.0-23.7 (r = 2) and 28.3-31.6 (r = 3).

## Comparison

C-1. Frozen success criterion (dependence_rate_overall <= 0.002 on both
seeds, control rate 1.0): met (0.000625 and 0.0; 24/24 on each seed).
Frozen falsification criterion (> 0.01 on both seeds): not met. No
invalidation rule fired. This is the reading DEC-20261009-6aef7a recorded,
and it is not re-scored.

C-2. Preregistered point prediction (specification preregistered_prediction
and hypothesis predictions, "0 of 1600 valid trials per seed, upper 95
percent bound 0.0019"):

- Met on seed 20261010 (0/1600, 0.00187).
- Not met on seed 20261009 (1/1600, 0.00296).
- The hypothesis statement's "upper 95 percent bound below 0.002" holds
  pooled (0.00148) but not on seed 20261009 alone.

C-3. Sampler readings:

- Under the hash-pinned y != 0 sampler, C-1 holds.
- Under the literal reading "random points of E(F_p)", the expected number
  of 2-torsion hits alone is 9.77 per seed (rate 0.0061), which lies between
  the 0.002 and 0.01 thresholds.
- P(success criterion met on one seed) = 0.012; P(on both seeds) = 1.5e-4
  (rt_stats.json, Poisson).
- The validator's literal-sampler draw gave 8/1600 = 0.005.

C-4. Against the accidental-relation expectations:

- Validator: the exact per-trial probability of the tangent family
  2 P~1 +- P~2 = O is 9.86e-4 at p = 101 and 2.46e-4 at p = 211. P(at least
  one hit in the 200 r = 2 trials at p = 101) = 0.179.
- Red team: the JKSST empirical law predicts 0.855 dependent trials, and 1
  was observed.
- The observation is consistent with both expectations.

C-5. Against the mod-p null:

- The Q-dependence count within the bound is at most the mod-p
  bounded-relation count, which falls from 58-64 percent (r = 2, p = 101) to
  0-1 percent (r = 2, p >= 6421).
- This decay tracks the pigeonhole scale (13^r - 1)/(2p).
- The flat zero at large p is the expected outcome for any lift, not a
  lift-specific measurement.

C-6. Against the attacker's regime:

- The bound 6 sits below the median smallest mod-p relation in every r = 2
  cell with p >= 211 and every r = 3 cell with p >= 3203.
- The attack-relevant coefficient scale is p^(1/r) (JKSST pp. 51-52), from
  10.05 to 113.18 for r = 2 and from 4.66 to 23.40 for r = 3.

C-7. Height clause: recorded 0.632-0.831, rising with p, against the
uniform-residue law 1 - (1 + ln 2)/ln p = 0.633 ... 0.821. A constant 0.7
matches only near p = 401.

## Inference

I-1. Counterexample to the zero clause. It is checkable by hand, and
independent code has re-checked it.

1. Take E~: Y^2 = X^3 - 1728 X - 27423 over Q.
2. P~1 = (-24, -15) lies on E~: -13824 + 41472 - 27423 = 225 = 15^2.
3. P~2 = (48, -15) lies on E~: 110592 - 82944 - 27423 = 225.
4. The tangent slope at P~1 is (3 * 576 - 1728)/(2 * (-15)) = 0. So the
   tangent is Y = -15, and it meets E~ where
   X^3 - 1728 X - 27648 = (X + 24)^2 (X - 48) = 0. That is P~1 twice and
   P~2 once, so 2 P~1 + P~2 = O, which is the recorded [-2, -1] up to sign.
5. The discriminant is -16(4(-1728)^3 + 27(27423)^2) = 5352901200, which is
   non-zero.
6. 2 P~1 = -P~2 = (48, 15). Doubling it uses slope (3 * 48^2 - 1728)/30 =
   864/5, so x(4 P~1) is not an integer. By Nagell-Lutz on this integral
   short model, 4 P~1 is not torsion, hence P~1 has infinite order. The
   relation is a genuine non-torsion dependence.
7. The reductions mod 101 are (77, 86), (48, 86) and (a, b) = (90, 49),
   which match the recorded inputs.

The same instance was found by the validator's sealed blind search
(validation_report.yaml accidental_relation_probe; j3_replay.json) and
verified exactly by the red team (rt_regulator_control.json,
rt_replay_inputs.json). It refutes the clauses "finds no relation in any of
100 trials per cell on either seed" and "dependence_rate_overall = 0 ...
upper 95 percent bound below 0.002" on seed 20261009, and the prediction
"exactly 0 on 1600 valid trials per seed". It refutes nothing else.

I-2. What the runs support. This is the narrowest valid conclusion, adopted
with the red team's narrowest_supported_statement. Setting: the eight
primes, random short-Weierstrass curves, r in {2, 3} points drawn uniformly
from affine points with y != 0 and distinct x, symmetric lifts, and the
zero-freedom rational fit. The exact search over max |m_i| <= 6 found 1
relation in 3200 valid trials: rate 3.1e-4, exact 95 percent CI
[7.9e-6, 1.7e-3]. Per seed that is 1/1600 and 0/1600; for r = 3 it is
0/1600. The planted (2, -1) control was detected 48 of 48. The one relation
is a tangent-line coincidence at the smallest prime. The count is
consistent with the JKSST empirical dependence law and with the validator's
exact tangent-family rate. Negative-result phrasing: no dependence rate
above the predefined 0.01 falsification threshold was observed over the
tested primes, sampler, fit, relation bound, implementation and budget.

I-3. What they do not support:

- (a) "Never dependent" or "no relation on either seed": refuted by I-1.
- (b) "Independent": a bounded search cannot certify independence.
  In-distribution torsion pairs pass it (PTM-1). The red team's unbounded
  determinant control shows the recorded tuples other than one are
  independent, but that control is a review finding, not frozen evidence.
- (c) The xedni obstruction, or "where the attack would need it": the
  near-zero rate at large p is forced by pigeonhole mod p (C-5), and the
  bound excludes the attacker's coefficient regime (C-6). The count is the
  downstream consequence of JKSST Lemma 4.1. It is not the obstruction
  itself, which is a conditional coefficient bound plus Lang's conjecture,
  and neither is tested here.
- (d) The mechanism's attribution: JKSST does not give dependence as
  negligible at p <= 12809. Theorem 4.1 is vacuous there (C0/p >= 0.78 for
  r = 2).
- (e) "Random points" without the y != 0 restriction: under that reading the
  success criterion fails in expectation (C-3).
- (f) "About 0.7 log p" as a constant (C-7).

I-4. Reading for the hypothesis. The hypothesis' own preregistered
prediction failed on one seed, by an exact counterexample. Its mechanism's
literature basis is misattributed. Its claim to measure the attacker's
regime is false. The experiment-level success criterion holds only under a
sampler restriction that the text did not state. The broad rarity claim,
restated as I-2, survives at toy scale and agrees with the literature. The
evidence therefore weakens H-CZLIFT-cb95b8 as worded. It does not reject a
scoped claim: the frozen falsification criterion did not fire, and a
point-zero prediction that its own cited source gave a 57 percent prior
chance of failing (red-team HC2) is a miscalibrated prediction, not a
refuted mechanism.

I-5. Resource reading of the obstruction. One xedni-style round succeeds
with probability about Pr[bounded mod-p relation] x f, where f is the
lift-survival fraction. Since Pr[bounded mod-p relation] <= (2 C2)^r / n, no
f in [0, 1] gives a sublinear attack. At the measured f the expected rounds
are about 15 n (r = 2) and 1.15 n (r = 3), and Pollard rho dominates. The
lifted relations that do occur are geometric (tangent or chord) and already
hold mod p, so any theory that exploits them is a mod-p test in disguise.
The C1 measurement (minimum 11.24) is the hypothesis of JKSST Lemma 4.1. It
holds at toy scale and does not weaken that lemma. No theory takes these
measurements as a resource; no lane is spawned.

## Limitation

- L-1. Toy tier only: p <= 12809 (14 bits), r <= 3, relation bound 6,
  symmetric lifts, zero-freedom fits, and the y != 0 sampler. Nothing about
  xedni proper (r = 4..9, discriminant minimization, reverse-Mestre
  conditions), lattice-reduced lifts, index calculus on E(Q), cost, or any
  deployed curve.
- L-2. The quantity is dominated by a pigeonhole factor that the design
  forces to decay with p. The lift-specific quantity (f = 1/1261) and the
  unbounded independence count were measured by the red team on replayed
  inputs, not frozen. PARI came from cypari2 2.2.4 installed outside the
  repository and is not pinned.
- L-3. One relation in 3200 trials; any rate statement below about 1e-3 is
  bound-limited. Per-cell resolution is coarse: 100 trials per cell, with a
  one-sided 95 percent upper bound of 0.0295 at 0/100.
- L-4. Controls:
  - The singular-fit exclusion control is vacuous by construction.
  - The planted control exercises only max |m| = 2 with r = 2. The
    validator's edge probe covers |m| = 6 and r = 3.
  - check.py imports run.py, so it checks reproducibility only. Independence
    of the numbers rests on the validator's recomputation and blind replay.
- L-5. The height metric covers r = 2 cells only. No peak-memory record
  exists.
- L-6. The JKSST empirical law is applied outside its fitted regime
  (LLL-minimized integral curves with small coordinates). The 0.855
  prediction is a consistency reading, not a calibrated null.
- L-7. Silverman-Suzuki and Huang-Kueh-Tan, cited by RQ-CZLIFT-b9f765, were
  not read in primary form. Nothing here rests on them.
- L-8. The composing Coordinator has no shell. I-1 is a hand derivation, and
  every other value is read by key from committed artifacts.
