# EXP-CZLIFT-ae0a13 analysis (H-CZLIFT-6d4ed1, RQ-CZLIFT-b9f765, GOAL-CZLIFT-1516d5)

Written for DEC-20261023-36b4f0 and EV-CZLIFT-ad28f5. Runs RUN-CZLIFT-dab752
(seed 20261009) and RUN-CZLIFT-5b2581 (seed 20261010). Reviews: validation
VAL-20261022-31a388 (`reports/validation-20261022/validation_report.yaml`,
passed, TASK-20261022-93fb1c) and red team RT-20261023-5636c1
(`reports/redteam-20261023/redteam_report.yaml`, TASK-20261023-1d45b5).
Sections are strictly Observation, Comparison, Inference, Limitation.

## Observation

Validity, re-checked before any reading (Coordinator, from the manifests and
execution receipts; the hash and replay work is the validator's):

- O-1. Run count 2 of 2 planned trials (`trial-plan.json`). Both receipts
  `output_validated`, returncode 0, check_returncode 0. Both manifests
  `completed_valid`, commit 03479a00cb79 with dirty false, source hashes equal
  to the frozen trial plan, seeds equal to the plan. 36 curves per seed (24
  cm_canonical, 12 random_naive). The validator matched 59/59 hashes,
  recomputed 79/79 metrics per seed from `raw-result.json` with 0 mismatches,
  and replayed 557/557 and 559/559 rows byte-for-byte.
- O-2. Realized pairs 557 and 559 of 576 attempted per seed. The 19 + 17
  missing samples are all S = P + [d2]P = O at d2 = n - 1, skipped by
  `run.py` lines 87-88. The rule depends only on d2 and is independent of P,
  d and every lift (validator, replay probe). The specification does not state
  it and the manifest records no excluded count.

Producer measurements (both seeds, toy scale: 50 <= p <= 600, 11 <= n <= 613,
precision k = 4):

- O-3. Torsion section: canonicity_rate, homomorphism_rate_torsion,
  degeneracy_rate_torsion, torsion_reduces_rate and
  scalar_mult_equivariance_rate each 1.0 on 557 and on 559 pairs (1116 of 1116
  in total). torsion_cost_mean_additions 58.04 and 55.24 complete additions over
  Z/p^4; torsion_cost_within_bound true; row-wise, 0 violations of
  2(bits(n) + bits(p^k)) + 1, minimum slack 15 additions (validator).
- O-4. identity_rate (Smart ratio equals tau-ratio) 1.0 for hensel_random,
  naive and teichmuller on both arms and both seeds: 0 failures in 3 x 1116
  section-rows.
- O-5. Identity-readout success (ratio == d mod p), successes / pairs, with the
  recorded per-arm mean 1/p reference and frozen z:

  | seed | arm | ref 1/p | hensel_random | naive | teichmuller |
  |---|---|---|---|---|---|
  | 20261009 | cm_canonical (n = 371) | 0.00436 | 0 (z -1.27) | 4 (z +1.88) | 1 (z -0.49) |
  | 20261009 | random_naive (n = 186) | 0.00634 | 0 (z -1.09) | 0 (z -1.09) | 0 (z -1.09) |
  | 20261010 | cm_canonical (n = 378) | 0.00500 | 2 (z +0.08) | 0 (z -1.38) | 1 (z -0.65) |
  | 20261010 | random_naive (n = 181) | 0.00641 | 1 (z -0.15) | 1 (z -0.15) | 1 (z -0.15) |

  Counts are success_rate x n from the manifests (integers by construction).
- O-6. arm_difference z: seed 20261009 hensel_random null (0/371 against
  0/186, difference 0.0, pooled SE 0), naive +1.421, teichmuller +0.709; seed
  20261010 -0.035, -1.446, -0.534.
- O-7. Undefined ratios (vP = 2, vQ = 1) on 1+6, 3+4 and 3+3 rows
  (hensel_random, naive, teichmuller; seed 20261009 + 20261010), all counted as
  non-successes. No non-torsion row has valuation >= 3.
- O-8. Secondary, unexpected and preserved: teichmuller cm_canonical
  homomorphism_rate_prec2 = 0.0212 (8/378) on seed 20261010 against a 1/p
  reference near 0.005. The excess sits on j = 0 curves, on the rows whose d2
  is a nontrivial cube root of unity mod n (3/3 and 7/7 hits; validator).

Reviewer measurements (independent code, committed in the review folders; not
producer runs):

- O-9. Validator blind re-derivation (sealed before any producer file was
  read): its own s_tor, from two formulas and two Hensel starts each, equals
  the producer's s_tor(P) mod p^4 on 1116 of 1116 replayed pairs;
  v_p(z([n]s_tor)) >= 4 on every pair; v_p(z([n]P^)) = 1 on all 284 blind
  Hensel starts.
- O-10. Proves-too-much object s_leak = s_tor + [log_P R]T: success 1.0 on both
  arms and seeds, frozen z +172 to +292 (validator PTM-1; red team rt_probe A).
- O-11. Precision sweep on 3 curves (p = 67, 157, 557): v_p(z([n]s_tor(P))) = k
  at k = 2, 3, 4, 6, 8; v_p(z([n]naive(P))) = 1 at every k (rt_probe D).
- O-12. Exhaustive control over all base points and all d (4,078,200 cells per
  section and lift, 71 curves), identity-readout successes against a same-shape
  random-odd-function null: ratio 0.967 to 1.058 per arm, lift and section
  (|z| <= 2.08); pooled 0.980 to 1.029. The null mean is 0.9969 of the analytic
  sum of cells/p (rt_probe B, rt_probe_summary).
- O-13. Multiplier sets {d : g(dR)/g(R) independent of R}: {n - 1} on every
  curve, lift and section, except the Teichmuller section on all 16 integral
  j = 0 CM models, where it is mu_6 minus {1} and the Smart ratio at lambda is
  the matching root of unity mod p; on a perturbed lift of the same reduction it
  collapses to {n - 1} (16 of 16; rt_probe B).
- O-14. On the 16 j = 0 canonical lifts a Frobenius lift exists, fixes s_tor and
  not the naive lift, and iterating it from the naive lift raises
  v_z(pi^j(naive P) - s_tor P) through 2, 3, 4 and reaches s_tor mod p^4
  (16 of 16; rt_probe C).
- O-15. Planted sections s_tor + [f(log_P R)]T with f(x) = n - x and
  f(x) = x^2 mod n: identity-readout success 0.000 to 0.0026, frozen z -1.39 to
  -0.55, so both pass the frozen test on both arms and seeds, while an attacker
  who knows f recovers d on 0.990 to 1.000 of pairs with at most 4 candidates
  (rt_probe A).
- O-16. Power (red team, on the realized rows): the frozen per-arm 4-sigma rule
  needs 7, 6, 8, 6 successes (4.33x, 5.09x, 4.23x, 5.17x the reference;
  cm/random, seed 20261009/20261010). The per-arm rule fires on both seeds with
  probability 0.962/0.836 (cm/random) at 8/p and >= 0.989 at a uniform leak of
  rate p^-1/2. The arm-difference rule (|z| > 3 on both seeds) fires with
  probability 0.002 at a CM-arm leak of 8/p, 0.035 at 10/p, 0.161 at 12/p,
  0.909 at 20/p (rt_power, rt_power_armdiff_ext).

## Comparison

- C-1. Frozen success criterion, per entry. Five torsion rates = 1.0: met on
  both seeds. Every identity_rate = 1.0: met. Every section |z| <= 4 on each
  arm: met (largest |z| 1.878). Every arm_difference |z| <= 3: met on the 5
  evaluable entries (largest |z| 1.446); the entry hensel_random on seed
  20261009 has z null and is recorded as NOT EVALUABLE, not as met (red-team
  O8). torsion_cost_within_bound: met. Falsification criterion: not triggered on
  either seed under any convention the validator computed.
- C-2. Against the preregistered prediction: the exact clauses (torsion rates,
  identity_rate) hold with 0 exceptions in 1116 and 3 x 1116 rows. The rate
  clauses hold inside the stated windows.
- C-3. Against the null for the identity readout: every per-arm cell is below
  its frozen detection floor of 4.2x to 5.2x of 1/p. Descriptively, and not as
  a preregistered test (the three sections share pairs, so cells are not
  independent): 11 successes in 3 x 1116 section-rows against about 17.5
  expected at 1/p. The exhaustive control (O-12) agrees with the same-shape null
  within 0.97x to 1.06x.
- C-4. Against the arm control. The frozen arm-difference test has
  essentially no power below a 10x leak (O-16), and the two arms also differ in
  curve family, p, n and class number, so a difference could not be attributed
  to the lift. The matched-lift control (same reduction, canonical integral
  model against a perturbed lift; O-12, O-13) shows no difference in the
  identity-readout rate (0.97x to 1.06x on both lifts) and a structural
  difference the frozen test cannot see: Aut(E^)-equivariance of the
  Teichmuller section on the canonical j = 0 lift only.
- C-5. Against the proves-too-much object: s_leak and the planted f-sections are
  non-canonical sections whose information about d is total; s_leak fails the
  frozen test and the f-sections pass it (O-10, O-15).
- C-6. Against the theory's degeneracy prediction: the torsion valuation equals
  the working precision at every k tested (O-11), so the vanishing is not a
  saturation artifact.
- C-7. Against the baseline (red team baseline_comparison): a section
  "attack" costs 55 to 58 complete additions per attempt and succeeds with
  probability about 1/p per re-randomized attempt, about p x 60 additions in
  expectation, against about sqrt(pi n / 4) group operations for Pollard rho.
  At n ~ p ~ 2^256 that is about 2^264 against 2^128. Dominated on time, equal
  on memory (O(1)).

## Inference

### I-A. Theorem-grade clauses (derivation; uniform in p; not machine-checked)

This is the derivation note cited by EV-CZLIFT-ad28f5 `proof_refs`, together
with the red-team report (R1, obstruction_and_resource_reading,
narrowest_supported_statement) and KN-TECH-73630e. It is a checkable argument,
labelled `derivation`, never "proved" (docs/claims-and-verification.md).

Setting S. p >= 5 prime; E/F_p an elliptic curve; P in E(F_p) of prime order
n != p; E^ any Weierstrass model over Z_p with good reduction E (the integral
CM model or an arbitrary integer lift); z = -x/y; E^_j the points of
E^(Q_p) with v_p(z) >= j; precision k >= 2.

- D1 (formal group). For p >= 3 the formal logarithm gives group isomorphisms
  E^_j -> p^j Z_p for every j >= 1, with v_p(log t) = v_p(z(t)). Hence E^_1 is
  torsion-free and [m] preserves each E^_j whenever p does not divide m. Standard
  (Silverman, AEC IV.6.4, recalled pointer only); it is the input already
  recorded at derivation tier in KN-TECH-73630e, and O-11 checks its
  consequence at k = 2..8.
- D2 (prime-to-p torsion is invisible to the formal group). Since n is a unit
  in Z_p, [n] is a bijection of E^_1 that preserves valuation; so E^_1[n] = 0
  and Hom(Z/n, E^_1) = 0.
- D3 (existence, uniqueness, formula, cost). Reduction E^(Q_p) -> E(F_p) is
  surjective (Hensel) with kernel E^_1. For R in <P> and any lift R^, put
  t = [n]R^ in E^_1 and m = n^{-1} mod p^k. Then log([n][m]t) = nm log t =
  log t mod p^{k+1}, so s(R) = R^ - [m]t satisfies [n]s(R) in E^_{k+1}: it
  reduces to R and is n-torsion at precision k. Two such points differ by
  u in E^_1 with [n]u in E^_{k+1}, so u in E^_{k+1} by D2: s(R) is unique at
  precision k and, as k grows, converges to the unique point of E^(Q_p)[n] over
  R. This is s_tor. It costs two double-and-add scalar multiplications (by n and
  by m < p^k) and one addition: at most 2(bits(n) + bits(p^k)) + 1 complete
  additions, counting doublings.
- D4 (canonicity). By uniqueness: s_tor does not depend on the Hensel start;
  s_tor(R1) + s_tor(R2) = s_tor(R1 + R2); [c]s_tor(R) = s_tor([c]R); and
  phi(s_tor(R)) = s_tor(phi(R)) for every endomorphism phi of E^ over Z_p whose
  reduction preserves <P>, since phi maps n-torsion to n-torsion. If sigma is
  any homomorphic section over <P>, sigma - s_tor is a homomorphism
  <P> -> E^_1, hence 0 by D2. So s_tor is the unique homomorphic section, and it
  is also the unique [c]-equivariant one.
- D5 (canonical lift, Frobenius reading). On the canonical lift a Frobenius
  lift F exists (Deuring, Lubin-Serre-Tate; retrieved by the red team in
  Chambert-Loir, Bourbaki 968, section 3.2.1). F reduces to the p-power
  Frobenius, which fixes E(F_p) pointwise, so F fixes s_tor(R) by D4; on E^_1,
  F reduces to an inseparable map and so carries E^_j into E^_{j+1}. Hence
  F - 1 is invertible on E^_1, s_tor is the only F-fixed section, and iterating
  F from any lift converges to s_tor, gaining one p-adic digit per step. O-14
  matches this on 16 of 16 j = 0 curves (2, 3, 4).
- D6 (Smart functional and the tau-identity). For any section s put
  tau_R = s(R) - s_tor(R) in E^_1. Then [n]s(R) = [n]s_tor(R) + [n]tau_R with
  [n]s_tor(R) in E^_{k+1}, and z([n]u) = n z(u) + O(z(u)^2) on E^_1. So
  z([n]s_tor(R)) vanishes at precision k, and whenever v_p(z(tau_P)) =
  v_p(z(tau_Q)) = 1 the Smart ratio z([n]s(Q))/z([n]s(P)) mod p equals
  z(tau_Q)/z(tau_P) mod p (n cancels). The readout sees tau only.

Theorem (scope S). (i) There is exactly one homomorphic section of reduction
over <P>, s_tor; it is the unique [c]-equivariant section, it commutes with
every Z_p-endomorphism of E^ preserving <P>, and on the canonical lift it is
the unique Frobenius-fixed section. (ii) It is computable from any Hensel
start in at most 2(bits(n) + bits(p^k)) + 1 complete additions at precision
k. (iii) The Smart functional z([n]s(R)) vanishes identically on it. (iv) For
every section s the Smart ratio equals the leading-digit tau-ratio. (v)
s_tor carries the whole discrete-log relation, s_tor(Q) = [d]s_tor(P), and
moves the DLP isomorphically into E^(Q_p)[n], which is the same instance
(KN-TECH-73630e); the formal logarithm is what vanishes on it, not the
information.

Reading of the user's H2 clause "a computable canonical section of
E(Q_p) -> E(F_p) would be a full break". Under every reading in which
"canonical" constrains the section (homomorphic, filtration-splitting, [c]-,
End- or Frobenius-equivariant, the CM/special-j route H2 itself names), the
canonical section exists, is computable in polynomial time, and is not a
break: the clause is FALSE as a statement, by the theorem, at every p >= 5 with
n != p, on every lift. Under the one remaining reading, "a section whose Smart
residue recovers d", the clause is circular (such a section is a discrete-log
oracle by definition) and by (i) it cannot be canonical in any sense above.
The runs do not establish this; they confirm the instruments against it
(O-3, O-4, O-9, O-11).

What the derivation does NOT give. Recovery through the identity readout
needs tau_{dP}/tau_P = d mod p; through a general readout it needs any
efficiently invertible f with tau-ratio f(d) (red-team O6). A computable
section of that kind is a discrete-log oracle and the derivation says nothing
about whether one exists; nothing here bears on the hardness of the ECDLP.

### I-B. Measured clauses (toy scale, empirical)

- For hensel_random, naive and teichmuller on these 36 + 36 curves, the event
  "Smart ratio = d mod p" occurs at a rate consistent with 1/p on the
  CM-canonical and the arbitrary-integer arm alike, on both seeds. The data
  exclude, per arm and seed, only excesses of about 4.2x to 5.2x of 1/p and
  above (80 % power on both seeds near 6x to 8x), and exclude a uniform leak at
  the rho-parity rate p^-1/2 with power >= 0.989. The red-team exhaustive
  control puts naive and Teichmuller within 0.97x to 1.06x of a same-shape
  null on both lifts.
- The "alike" clause rests on the two per-arm tests and the matched-lift
  exhaustive control (C-4), not on the frozen arm-difference test, which carries
  no inferential weight in either direction.
- The 1/p reference rests on an unnumbered random-model assumption, stated here
  as H-1: the Smart residue of a choice-free section is uniform on F_p and
  independent of d outside the Aut(E^)-orbit of d. O-12 and O-13 are its
  validation at toy scale (71 curves, 2 lifts, 2 sections); O-13 shows the
  orbit exception is real on canonical j = 0 lifts.
- O-8 is explained by O-13: on the canonical j = 0 lift the Teichmuller section
  is Aut(E^)-equivariant, so the identity readout is deterministic on the mu_6
  orbit of d. The information it leaks is that orbit (probability 4/(n - 3) for
  a random d in [2, n - 2]), which Pollard rho with automorphism classes already
  uses.

### I-C. Not inferred, and why

- Not "the non-torsion sections carry no information about d": one readout was
  tested and planted discrete-log oracles pass it (O-15).
- Not "the canonical curve lift contributes nothing": it adds
  Aut(E^)-equivariance to the Teichmuller section (O-13). It contributes
  nothing to the prime-to-p splitting (theorem) and nothing measurable to the
  identity-readout rate (O-12).
- Not "every non-canonical section recovers d at the random rate 1/p"
  (RQ-CZLIFT-b9f765 decision_target (a)): false, by O-10 and O-15.
- Not "s_tor carries no information about d" (DEC-20261009-9f9254
  claim_boundary): s_tor carries all of it (theorem (v)).
- Not "contradicted at toy scope" for the two H2 structural clauses
  (DEC-20261009-9f9254): they are contradicted by a theorem uniform in p, and
  the runs check the instrument against it.
- Not "so no choice of lift removes it" from identity_rate = 1.0
  (DEC-20261009-9f9254): s_leak also has identity_rate 1.0 and is a choice of
  lift with no noise. What holds: no homomorphic section removes the noise
  (each zeroes the signal), any section that removes it is a discrete-log
  oracle, and the three tested choice-free sections do not remove it.

### I-D. The frozen decision_impact

The on_positive branch applies with the scope above: H-CZLIFT-6d4ed1 is
supported, its torsion-section and tau-identity clauses at derivation tier and
its rate clauses at toy tier, and the user's clause is recorded as answered
negatively by derivation (not "at this scope"). The mechanism sentences "the
canonical curve lift ... contributes nothing" and "a section recovering d
would need tau(dP)/tau(P) = d for all d" are not supported as written (red-team
O5, O6). The construction cost is a polynomial cost of building the section,
not a cost to break; any attack reading of it is dominated (C-7).

## Limitation

- L-1. Toy scale only: 50 <= p <= 600 (at most 10-bit fields), 11 <= n <= 613,
  precision 4, 36 curves per seed, 557 and 559 realized pairs. No
  cryptographic-size statement for the measured clauses; the derivation needs no
  transfer argument and makes none about hardness.
- L-2. Detection floor 4.2x to 5.2x of 1/p per arm and seed; smaller excesses
  are not excluded by the frozen test.
- L-3. One readout (identity, f = id). Rows record booleans and valuations
  only, not d, d2, the base point or the residue (red-team O7), so no other
  readout can be evaluated without a replay.
- L-4. The arm comparison is confounded (family, p, n, h) and powerless below
  about 12x to 20x; it is excluded from the evidential basis. Its seed-20261009
  hensel_random entry is not evaluable (z null).
- L-5. 36 of 1152 attempted samples were skipped by a rule the specification
  does not state; outcome-independent, but 12 curves per seed have fewer than
  16 rows (worst p = 97, n = 11, 10 rows).
- L-6. The archived checker imports the producer's measure_curve and summarize
  and replays 2 of 36 curves; its exit 0 is not independent. Independence comes
  from the validator's blind re-derivation and full replay and from the red
  team's own arithmetic (rt_lib.py).
- L-7. The canonicity control's two Hensel starts differ in one p-adic digit
  and coincide on 5 of 1116 rows; start-independence rests on D4 and the
  validator's three-digit starts.
- L-8. The cm arm label "canonical lift" rests on exact j-invariants plus
  Deuring/Lubin-Serre-Tate; it is checked directly (Frobenius lift exists) only
  for D = -3. The hypothesis cites Katz (LNM 868) as recalled with no verifier;
  the red team could not locate the statement there and verified
  Deuring/Lubin-Serre-Tate in Chambert-Loir 2006. Not load-bearing for s_tor,
  which exists on every lift.
- L-9. The 1/p reference uses the heuristic H-1 (I-B), validated only at toy
  scale. Environment records no package versions (runtime_lock null) and no
  peak memory.
- L-10. Reviewer model identities are not probe-verified; independence is by
  session and role.
