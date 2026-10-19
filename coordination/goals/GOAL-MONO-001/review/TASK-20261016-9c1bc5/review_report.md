# Review report, TASK-20261016-9c1bc5 (REVIEW-MONO-20261016-9c1bc5)

Reviewer role: validator-breakthrough (policy review-breakthrough, effort max), fresh independent session.
Branch `claude/quotient-summation-ecc2k-130-4y7t3o`, HEAD `c59b45a85ad1d8289a1ff3a19dad0fd722956630`.
Joints owned: J1, J2, J3, the proves-too-much control, and the blind re-derivation. No whole-goal verdict is given (RC-3, CU7-C8).

This file is written in the order the work was done, and that order is kept visible: Part 0 (custody and
reading log up to the blind section), Part 1 (blind re-derivation, written and frozen BEFORE any
`blind_from` path or any record under review was opened), then Parts 2 to 6 (J1, J2, J3, the
proves-too-much control, questions and observations), written after the sequenced unblinding.

## Part 0. Custody and the reading log before the blind section

### 0.1 Input custody (recomputed at HEAD c59b45a85a, before any of the three files was read)

| file | sha256 recomputed by this session | matches value given by the top-level session |
| --- | --- | --- |
| `ledger/evidence/EV-MONO-1ef611.yaml` | `ae686fe956993212b4dd706df69e5477d2c57bd4210c37ca696866c25a9a3fbe` | yes |
| `ledger/corrections/CORR-20261005-a53ac8.yaml` | `cfbbd928e1ca32acf71c2bbeae0ae84fa1287b3fcafba2c2e3a58e935dd76d36` | yes |
| `coordination/review/mono-20260930-44adf9/review-plan-amendment-01.yaml` | `af7ff9570d0fb7c43a18f1c63b06d38e23fd047564cf4832b1a17569c107d103` | yes |

No custody finding. The three files were hashed, not read, at this point.

### 0.2 Sibling-report check (RC-9)

`coordination/goals/GOAL-MONO-001/review/` contained exactly one entry, `TASK-20260930-40470a/` (the
predecessor round, a sequenced input). No report from this round exists. `read_sibling_reports: false`.

### 0.3 Reading log up to the end of the blind section (RC-1), in order

1. `ledger/handoffs/TASK-20261016-9c1bc5.yaml` at `c59b45a85a`, in full. DISCLOSURE: this file embeds the
   Coordinator's `coordinator_prior` (its lines 295 to 316); it was therefore seen before the blind
   section. It names the shape "leading coefficient in T is S_{m-1}^2" and a degree-drop worry. Nothing
   below is taken from it: the leading-coefficient identity is proved in 1.2 step 2 and checked
   symbolically and numerically, and the degree-drop question is tested on constructed instances.
2. `agents/validator.md`, in full.
3. `AGENTS.md`, in full. (`CLAUDE.md` was injected by the runtime at session start.)
4. `docs/claims-and-verification.md`, in full.
5. Hash only (contents not read): the three custody files of 0.1.
6. Directory names only: `coordination/goals/GOAL-MONO-001/review/`, `coordination/goals/GOAL-MONO-001/batches/`.
7. `templates/research-records.md` lines 768 to 807 (the `review_attestation` template), by grep.
8. `orchestration/model-bindings.yaml` (grep hits for `review-breakthrough`; lines 170 to 200; backend
   headers) and grep hits in `orchestration/model-bindings.local.example.yaml`.
9. `tools/check_review_independence.py`: grep hits, lines 296 to 370, 880 to 940 and 985 to 1032
   (verdict vocabulary, joint labels, blind_from handling).
10. Tool output: `python3 tools/check_runtime_bindings.py --list` (validator-breakthrough rows:
    policy review-breakthrough, effort max, sourced from the agent file for claude_code);
    `python3 -m orchestration.adapter resolve --role validator-breakthrough` (errors: the adapter has no
    default policy for the variant role name; nothing resolved).

No path under `experiments/EXP-MONO-4b50b6/`, `coordination/goals/GOAL-MONO-001/batches/BATCH-003/` or
`coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/` was opened before Part 1 was complete,
and neither `EV-MONO-1ef611` nor `DEC-20260930-8553d4` (permitted pre-reads) was opened either: Part 1
is derived from the quantity statement and parameters in `review_plan.blind_rederivation` alone.

## Part 1. Blind re-derivation (written first, RC-2; frozen at 2026-10-16T17:2xZ before unblinding)

### 1.1 The quantity, as given by the plan

For p > 3, nonsingular E: y^2 = x^3 + a x + b over F_p, and affine P_1, ..., P_{m-1} in E(F_p) with
x_i = x(P_i): (i) the root multiset in P^1 of S_m(x_1, ..., x_{m-1}, T); (ii) its affine degree in T as a
function of the base tuple; (iii) the fraction of generic fibres (squarefree, full degree 2^{m-2}) on which
Frobenius acts non-trivially on the roots. Derived from the group law and the defining property of the
summation polynomials (S_m(x_1..x_m) = 0 iff there are points Q_i on E with x(Q_i) = x_i and
Q_1 + ... + Q_m = O), with my own S_4 and S_5.

Notation. For a sign vector eps = (eps_1, ..., eps_{m-1}) with eps_1 = +1 ("sign class"; there are
2^{m-2} of them), R_eps := sum_i eps_i P_i in E(F_p), and x(O) := infinity in P^1. "O-class" means a sign
class with R_eps = O. The lift P_i -> -P_i does not change the multiset {x(R_eps)}_eps (flipping P_1
maps the family to its negatives, flipping P_j for j >= 2 permutes it), so the multiset is a function of
the x-tuple alone.

### 1.2 Derivation

**Step 0 (the one external input).** Semaev's theorem (I. Semaev, "Summation polynomials and the discrete
logarithm problem on elliptic curves", 2004, Theorem 1; provenance: recalled, used only for the zero-set
characterisation, and that characterisation is re-verified below on my own S_3, S_4, S_5 over the algebraic
closure): for every m >= 2 and all x_1, ..., x_m in the algebraic closure, S_m(x_1, ..., x_m) = 0 iff there
exist Q_i in E with x(Q_i) = x_i and Q_1 + ... + Q_m = O; S_m is symmetric of degree 2^{m-2} in each
variable for m >= 3, and S_m = Res_X(S_{m-1}(x_1..x_{m-2}, X), S_3(x_{m-1}, x_m, X)).

**Step 1 (S_3 from the group law, no formula recalled).** For P_1 = (x_1, y_1), P_2 = (x_2, y_2) with
x_1 != x_2, x(P_1 + P_2) = lambda^2 - x_1 - x_2 with lambda = (y_2 - y_1)/(x_2 - x_1). So
P_1 + P_2 + P_3 = O forces (x_3 + x_1 + x_2)(x_2 - x_1)^2 - (y_2 - y_1)^2 = 0. Eliminating y_1 then y_2
against y_i^2 = f(x_i) (two resultants, `derive_s3_s4.py`) gives the norm over the four sign choices,
which factors as (x_1 - x_2)^4 times the square of one irreducible factor of degree 2 in each variable.
That factor is my S_3:

S_3 = (x_1 - x_2)^2 x_3^2 - 2[(x_1 + x_2)(x_1 x_2 + a) + 2b] x_3 + (x_1 x_2 - a)^2 - 4b(x_1 + x_2),

checked symmetric under all transpositions, and checked to equal
[((x_3 + x_1 + x_2)(x_2 - x_1)^2 - f(x_1) - f(x_2))^2 - 4 f(x_1) f(x_2)] / (x_1 - x_2)^2 exactly. Its
leading coefficient in x_3 is (x_1 - x_2)^2 = S_2(x_1, x_2)^2.

**Step 2 (recursion, degrees, and the leading coefficient in T).** Define, with FORMAL degrees
(2^{m-3} in X for the first argument, 2 in X for the second),
S_m(x_1..x_{m-1}, T) := Res_X( S_{m-1}(x_1..x_{m-2}, X), S_3(x_{m-1}, T, X) ).
The formal-degree Sylvester determinant is the universal resultant polynomial evaluated at the
coefficients, so a specialisation at which a leading coefficient vanishes is still the specialisation of
the generic S_m (an "actual-degree" resultant would not be; this matters exactly on the degenerate
sublocus, and my code uses formal degrees throughout). Degree in each variable: 2^{m-2}.
Leading coefficient in T: writing g(X) = S_3(x_{m-1}, T, X) = T^2 (X - x_{m-1})^2 + (lower order in T),
the coefficient of T^{2 deg_X f} in Res_X(f, g) is Res_X(f, (X - x_{m-1})^2) = f(x_{m-1})^2 (the sign is +
because deg f times deg g is even). Hence, exactly,

  lc_T S_m(x_1, ..., x_{m-1}, T) = S_{m-1}(x_1, ..., x_{m-1})^2      (m >= 3; for m = 3, S_2 = x_1 - x_2).

Checked: symbolically for m = 4 (the quotient lc_{x_4}(S_4) / S_3(x_1, x_2, x_3)^2 simplifies to exactly 1,
`derive_s3_s4.out`), and numerically for m = 5 on 36 random x in F_p^4 off the locus and on every tested
base tuple (`lc_equals_Sprev_squared` true throughout, `blind_results.json`).

**Step 3 (the generic identity).** Let L = F_p(x_1, ..., x_{m-1}) (independent indeterminates) and
K = L(y_1, ..., y_{m-1}) with y_i^2 = f(x_i); K/L is Galois with group G = (Z/2)^{m-1} acting by
P_i -> -P_i. Put Phi(T) = prod_eps (T - x(R_eps)) in K[T] (generic points: no R_eps is O). G permutes the
family {x(R_eps)} (flipping P_1 sends R_eps to -R_{eps'} for the complementary class eps', and x(-R) =
x(R)), so Phi is G-invariant and lies in L[T]; it is monic of degree 2^{m-2}. By step 0 applied over an
algebraic closure of L, the zero set of S_m(x, T) in T is exactly {x(R_eps)}: "if" because
R_eps + Q = O with x(Q) = x(R_eps); "only if" because S_m(x_1..x_{m-1}, tau) = 0 gives Q_i with x(Q_i) =
x_i, i.e. Q_i = +-P_i, and Q_m with x(Q_m) = tau, so tau = x(+-R_eps) for some eps. For generic
independent points the 2^{m-2} values x(R_eps) are pairwise distinct (R_eps = +-R_eps' would be a
non-trivial relation 2 sum_{i in D} eps_i P_i = O or 2(P_1 + ...) = O among independent generic points).
So Phi is squarefree with 2^{m-2} roots, S_m(x, T) has degree 2^{m-2} in T and vanishes on all of them,
hence S_m(x, T) = lc_T S_m . Phi(T), i.e.

  S_m(x_1..x_{m-1}, T) = S_{m-1}(x_1..x_{m-1})^2 . prod_eps (T - x(R_eps))       in K[T].

**Step 4 (specialisation to a factor-base tuple).** Fix affine P = (P_1, ..., P_{m-1}) in E(F_p)^{m-1}.
Each x o R_eps : E^{m-1} -> P^1 is a morphism (composition of the group-law morphism and the degree-2
map x), so near P it is (X_eps : Z_eps) with X_eps, Z_eps regular at P and not both zero there. Put
Psi(T) = prod_eps (Z_eps T - X_eps), regular at P, with Psi(P; T) a NON-ZERO polynomial in T (each factor
is a non-zero linear or constant polynomial at P). Step 3 says S_m(x(.), T) = mu . Psi(T) with mu in K.
Some T-coefficient of Psi is a regular function not vanishing at P; mu is the ratio of the corresponding
coefficient of S_m (a polynomial in x, hence regular) to it, so mu is regular at P and the identity
specialises: S_m(x(P), T) = mu(P) . prod_eps (Z_eps(P) T - X_eps(P)). Finally mu(P) != 0: by step 0 at the
specialised point, the roots of S_m(x(P), T) form the finite set {x(R_eps(P)) : R_eps(P) != O}, so
S_m(x(P), T) is not the zero polynomial. All of x(P), mu(P), X_eps(P), Z_eps(P) lie in F_p because P and
the group law are F_p-rational.

**Step 5 (the three answers).** From step 4, for every m >= 3, p > 3, nonsingular E/F_p and affine
P_1..P_{m-1} in E(F_p):

(i) The root multiset of S_m(x_1..x_{m-1}, T) in P^1 is exactly {x(R_eps)}_eps over the 2^{m-2} sign
classes, WITH multiplicity, where an O-class contributes the root infinity (its factor has Z_eps(P) = 0).
Every affine root is x of an F_p-rational point, so S_m(x(P), T) splits completely over F_p.

(ii) affine degree = 2^{m-2} - #{eps : R_eps = O}. The leading affine coefficient is
c = mu(P) . prod_{R_eps != O} Z_eps(P) . prod_{R_eps = O} (-X_eps(P)), a product of non-zero elements of F_p,
so c in F_p^*. Moreover #{O-classes} >= 1 iff S_{m-1}(x_1..x_{m-1}) = 0 (step 0 for S_{m-1}: a sign choice
with sum eps_i P_i = O exists iff S_{m-1}(x(P)) = 0; equivalently, by step 2, iff lc_T vanishes iff
infinity is a root). So the affine degree is exactly 2^{m-2} iff S_{m-1}(x_1..x_{m-1}) != 0.

(iii) On every fibre over the factor-base locus, Frobenius fixes every root in P^1 (each root is x of a
point of E(F_p), or infinity). In particular on every generic fibre (squarefree, full degree) the
Frobenius cycle type is 1^{2^{m-2}}, and the fraction of generic fibres with non-trivial Frobenius action
is exactly 0, by derivation, uniformly in m, p, E and the tuple. The step that carries the F_p-rationality
is "R_eps in E(F_p) because every P_i is in E(F_p)"; it uses the rationality of the POINTS, not merely
of the x-coordinates, which is where the argument must stop on objects off this locus (Part 5).

Two remarks that the degenerate instances test. (a) If some P_j is 2-torsion, the involution flipping all
other signs sends R_eps to -R_eps (since -P_j = P_j), so roots and O-classes come in pairs: every
multiplicity is even and "exactly one O-class together with a 2-torsion base point" cannot occur at any m.
(b) When exactly one sign class sums to O, the multiplicity of infinity is 1, so the affine degree drops
by exactly 1 even though lc_T = S_{m-1}^2 vanishes to order 2 as a function on the base: the order of
vanishing of a coefficient along the base is not the multiplicity of the root in T. The data (type 3 and
every exhaustive tuple with one O-class) confirm the drop is 1.

### 1.3 Computations (all code and raw output in `computations.json`, section `blind`)

Software: Python 3.11.15, sympy 1.14.0, numpy 2.4.6; no CAS beyond these. Scripts: `derive_s3_s4.py`
(S_3 from the group law; symbolic S_4; symmetry; lc identity), `blind_main.py` (everything below).
S_4(x_1, x_2, x_3, T) is evaluated from my symbolic S_4 and cross-checked against an independent
formal-Sylvester route on 100 tuples including x_1 = x_2 (all agree). S_5(x_1..x_4, T) is the 6x6
formal-degree Sylvester determinant of my S_4(x_1, x_2, x_3, X) and my S_3(x_4, T, X), evaluated at
every t in F_p, interpolated from 9 values and re-checked at all p points. Roots are found by brute
force over F_p and multiplicities by repeated division (no use of the expected roots); infinity gets
multiplicity formal degree minus affine degree.

Curves used (my choice; neither the producers' p = 211 curve nor the predecessor's C1 to C5):

| label | curve | #E(F_p) | x-coordinates of affine points | rational 2-torsion |
| --- | --- | --- | --- | --- |
| A | y^2 = x^3 + 44x + 103 over F_131 (= (x-3)(x-17)(x+20)) | 144 | 73 | x = 3, 17, 111 (full) |
| D | y^2 = x^3 + 20x + 60 over F_61 | 70 | 35 | (8, 0) only |
| B | y^2 = x^3 + 1146x + 1754 over F_1999 | 1952 | 976 | (1680, 0) only |
| C | y^2 = x^3 + 700x + 821 over F_1009 | 1065 | 532 | none |
| (tiny) | y^2 = x^3 + 2x + 3 over F_13; y^2 = x^3 + 3x + 5 over F_17 | - | - | used only for the defining-property check |

Check 1, defining property of MY S_3, S_4, S_5 over the algebraic closure (points lifted into E(F_{p^2})),
compared with the existence of a sign choice summing to O: p = 13: S_3 on all 2197 tuples of F_13^3
(172 zeros), S_4 on all 28561 tuples of F_13^4 (2601 zeros), S_5 on 2500 random tuples of F_13^5 (275
zeros) and on all 85293 tuples with (x_1..x_4) on the locus and x_5 ranging over F_13 (23936 zeros);
p = 17: S_3 on all 4913 (297 zeros), S_4 on all 83521 (5833 zeros), S_5 on 2500 random (200 zeros).
Mismatches: 0 in every row. My polynomials are the summation polynomials, zero set included at the
degenerate points.

Check 2, exhaustive sweeps over ORDERED tuples of factor-base x-coordinates:

| curve, m | tuples | generic fibres | generic with non-trivial Frobenius | multiset mismatches | degree-rule failures | c = 0 | lc-rule failures | O-class histogram (count: tuples) | affine-degree histogram |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A (p=131), m=3 | 5329 | 4830 | 0 | 0 | 0 | 0 | 0 | 0:5256, 1:70, 2:3 | 2:5256, 1:70, 0:3 |
| A (p=131), m=4 | 389017 | 278496 | 0 | 0 | 0 | 0 | 0 | 0:378861, 1:9520, 2:630, 4:6 | 4:378861, 3:9520, 2:630, 0:6 |
| D (p=61), m=3 | 1225 | 1122 | 0 | 0 | 0 | 0 | 0 | 0:1190, 1:34, 2:1 | 2:1190, 1:34, 0:1 |
| D (p=61), m=4 | 42875 | 30600 | 0 | 0 | 0 | 0 | 0 | 0:40529, 1:2244, 2:102 | 4:40529, 3:2244, 2:102 |

In every row the polynomial depends only on the multiset of the x-tuple (symmetry verified on all
permutations), "S_{m-1}(x) = 0 iff at least one O-class" held on every tuple, and the affine degree equalled
2^{m-2} minus the O-class count on every tuple. Worked examples from the raw output: on A at m = 3 the
2-torsion double (3, 3) gives S_3(3, 3, T) = 63, a non-zero constant (two O-classes, affine degree 0;
63 = (3 . 3^2 + 44)^2 mod 131 = f'(3)^2 as the derivation predicts); at m = 4 the three 2-torsion points
(3, 17, 111) in any order give S_4 = 43, a non-zero constant (four O-classes, affine degree 0); the triple
x = (4, 4, 44) (P_1 = P_2, P_3 with x = 44) gives coefficients [76, 4, 20, 79, 0], affine degree 3, roots
{44, 44, 124, inf}, equal to the sign-class multiset.

Check 3, constructed degenerate instances at m = 4 (each row: instances on A / on B; all pass every check):
(1) one P_i 2-torsion, others generic: 6 / 6, all four roots paired (two double roots), affine degree 4;
(2) P_i = +-P_j with no 2-torsion point: 6 / 6, one double root, affine degree 4;
(3) exactly one sign class summing to O (P_3 = -(P_1 + P_2)): 6 / 6, affine degree 3 in all twelve,
the drop is exactly 1, S_3(x_1, x_2, x_3) = 0 in all twelve;
(4) two or more O-classes: 12 / 6: (T_2, Q, T_2 - Q) gives two O-classes and a double root, affine
degree 2; the six orderings of the three 2-torsion points of A give four O-classes, affine degree 0,
c = 43 != 0;
(5) a 2-torsion point with a coincident pair (T_2, Q, +-Q), plus (T_2, T_2, T_2) and (T_2, T_2', Q): 11 / 7,
two double roots, affine degree 4.

Check 4, m = 5 with my S_5: 24 random factor-base tuples on each of B, C, A (72 in all; generic fibres
24, 23 and 7 respectively, the small curve A producing many coincident roots) and 39 degenerate tuples
(15 on A, 15 on B, 9 on C) of which 36 have S_4(x_1..x_4) = 0 (one O-class: 17 tuples, affine degree 7;
two O-classes: 13 tuples, affine degree 6, including three tuples (Q_1, Q_2, T_2 - Q_2, -(Q_1 + T_2)) with
two O-classes and NO 2-torsion base point) and 3 are coincident-pair tuples (Q, Q, R, S) with repeated
roots and full degree 8. All 111 tuples pass every check; lc_T S_5 = S_4^2 also on 36 random off-locus
x in F_p^4.

Check 5, random m = 3 and m = 4 at the large primes: 300 tuples each on B and C (1200 in all), 0 failures;
the three tuples that happened to have an O-class had affine degree 2^{m-2} - 1.

Totals: 439829 base tuples checked at m in {3, 4, 5} on four curves at p in {61, 131, 1009, 1999};
316290 generic fibres; 0 generic fibres with non-trivial Frobenius; 0 multiset mismatches; 0 incomplete
splittings; 0 degree-rule failures; 0 tuples with c = 0; 0 failures of lc_T S_m = S_{m-1}^2.

### 1.4 Blind result

(i) Root multiset in P^1 of S_m(x_1..x_{m-1}, T) = {x(sum_i eps_i P_i) : eps_1 = +1}, with multiplicity,
infinity for the classes summing to O; the polynomial splits completely over F_p.
(ii) Affine degree = 2^{m-2} - #(sign classes summing to O); equal to 2^{m-2} iff S_{m-1}(x_1..x_{m-1}) != 0;
the leading affine coefficient c is in F_p^*; the formal leading coefficient is S_{m-1}(x_1..x_{m-1})^2.
(iii) The fraction of generic fibres over the factor-base locus with non-trivial Frobenius action on the
roots is exactly 0, by derivation for every m >= 3 and p > 3 (steps 0 to 5), corroborated with zero
exceptions at m = 3, 4, 5 on the curves and tuples above. The derivation proves nothing about tuples whose
x_i are not x-coordinates of F_p-rational points, about any count that fixes T and varies the x_i, or
about rationality over a proper subfield (Part 5).

### 1.5 Blindness statement

No path in `blind_rederivation.blind_from` was opened before this Part was complete, and no record under
review was opened either. The frozen text of Parts 0 and 1 is embedded in `computations.json`
(`blind.frozen_section_text`) with its sha256, recorded before the first `blind_from` path was read.

---

## Part 1a. Sequenced unblinding (RC-2) and the reading log after the blind section

The blind section above was frozen at 2026-10-16T17:25:53Z (sha256
`244bca5607c005444c7c2893fb13d419abc3e3da2d25fabe2ebe79aa39c50afb`, recorded in `computations.json`
`blind.frozen_section_sha256`). Only then was `coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/`
opened. The complete ordered reading log is `review_attestation.yaml` `sources_read`; the order was: the
predecessor report (lines 1 to 1076) and the key structure and selected outputs of its
`s4_construction/computations.json`; then EV-MONO-1ef611, CORR-20261005-a53ac8, DEC-20260930-8553d4,
DEC-20260810-2f86db, amendment A01, DEC-20261016-5bdc04, EV-MONO-a0a89c, the predecessor plan,
DEC-20260904-dd58c3, DEC-20260802-a51c82, the goal head, DEC-20260930-6f1d85, the three checkpoint shards,
the BATCH-1f9bf0 queue notes, RQ-MONO-001, KN-OPEN-009, the cited passages of the six `spawned_ids` records,
agents/coordinator.md "Closure gate", the obstruction template, docs/inventor-protocol.md sections 4 to 7,
and git metadata and archive receipts for the quote-trail records. `experiments/EXP-MONO-4b50b6/` and
`coordination/goals/GOAL-MONO-001/batches/BATCH-003/` were never opened. No report from this round exists.

**Comparison of the blind result with the predecessor's (made only after unblinding).** My Part 1 agrees
with the predecessor's blind section and J1 corrected statement in every clause, on different curves
(none of C1 to C5; C2 = the producers' curve was not used) and with a different S_5 construction route
(formal Sylvester determinant evaluated and interpolated over F_p, in pure Python and numpy, with no PARI or
FLINT). The one derivational difference is in how the specialisation step is argued: the predecessor
used a generic curve germ and Gauss's lemma; Part 1 uses the morphism x o R_eps : E^{m-1} -> P^1 and the
regularity of the ratio mu at the base point. Both reach the same identity.

**Semaev 2004.** I attempted to retrieve https://eprint.iacr.org/2004/031.pdf twice; both attempts
returned an HTTP 403 Cloudflare challenge page (RC-6: a tooling failure, not evidence; raw headers and
hashes in `computations.json` `retrieval_attempts`). For this session the citation is `recalled`, a pointer.
Its load-bearing content for m <= 5 was verified independently on my own polynomials (Part 1, check 1);
the extent m >= 6 of "every m" rests on the published theorem, which the predecessor retrieved and read
(sha256 `1cab0ae6...c7d6`, verified_by TASK-20260930-40470a). I did not reproduce that retrieval and say so
in `independent_recomputation` below.

## Part 2. J1 - derivational soundness of the cured statement as committed scope: **CONCUR**

**Method actually used.** (1) The blind re-derivation of Part 1, from the group law and the defining
property, with my own S_3, S_4, S_5. (2) Then a clause-by-clause comparison of Part 1 with EV-MONO-1ef611
`obstruction.scope` (i), the CU-1 text of DEC-20260930-8553d4 and the predecessor's "Corrected statement".
(3) The attack the plan names first, the degree-drop count: 11,776 base tuples with exactly one O-class
(9,520 exhaustive on A at m=4; 2,244 on D at m=4; 70 on A and 34 on D at m=3; 12 constructed type-3
instances; 17 at m=5), every one with affine degree exactly 2^{m-2} - 1; and the parity argument of Part 1
remark (a). (4) The five constructed degenerate types at m=4 (>= 6 instances each on two curves) and the
m=5 suite (72 random, 39 degenerate tuples). (5) The defining-property check of my own S_3, S_4, S_5 over
the algebraic closure at p = 13 and 17, degenerate points included.

**What was built, computed or read.** Built: S_3 by elimination from the chord-tangent law; S_4 by
symbolic resultant (540 terms, symmetric, degree 4 in each variable, lc_{x_4} = S_3^2 exactly); S_5 by
formal-degree Sylvester determinant. Computed: 439,829 base tuples at m in {3, 4, 5} on four curves at
p in {61, 131, 1009, 1999}, 316,290 of them generic fibres; two independent routes to S_4 agree on 100
tuples including x_1 = x_2. Read (after Part 1): EV-MONO-1ef611, DEC-20260930-8553d4 CU-1, the predecessor
J1 and blind sections, EV-MONO-a0a89c OBS-4/OBS-5, DEC-20260810-2f86db D-1.

**Clause-by-clause result on scope (i), the CU-1 statement as committed in EV-MONO-1ef611.**

| clause of scope (i) | Part 1 result | status |
| --- | --- | --- |
| Setting p > 3, E/F_p nonsingular, P_1..P_{m-1} in E(F_p) affine, x_i = x(P_i) | same setting (1.1) | matches |
| S_m(x,T) = c . prod over sign classes with sum != O of (T - x(sum eps_i P_i)), c in F_p^* | step 4/5 (i), (ii); c != 0 on every tuple | matches |
| splits completely over F_p | step 5 (i); 0 incomplete splittings in 439,829 tuples | matches |
| degree = 2^{m-2} minus the number of O-classes; exactly 2^{m-2} iff S_{m-1}(x) != 0 | step 5 (ii); `degree_rule` and `Sprev_zero_iff_O_class` true on every tuple | matches |
| in P^1 the roots are the 2^{m-2} values x(sum eps_i P_i) with multiplicity, x(O) = infinity | step 5 (i); `multiset_match` true on every tuple | matches |
| Frobenius fixes every root; cycle type 1^{2^{m-2}} on every generic fibre over the locus | step 5 (iii); 0 of 316,290 generic fibres non-trivial | matches |
| "every m >= 3" (scope (iii), by derivation from Theorem 1 and the group law) | steps 2 to 5 are uniform in m; the only external input is the zero-set theorem | follows |

**Breaking-artifact assessment (plan J1).** Clause by clause: (1) an instance failing to split in P^1: none
(0 of 439,829). (2) A root outside the sign-class multiset: none. (3) An affine degree different from
2^{m-2} minus the O-class count: none; in particular the degree drop at exactly one O-class is exactly 1 in
all 11,776 such tuples, and a 2-torsion base point forces an even O-class count (Part 1 remark (a)), so the
Coordinator's prior worry (a drop of 2 at a single O-class with a 2-torsion P_i) cannot arise and did not.
(4) c not in F_p^*: none (0 tuples with c = 0, including the three all-O-class instances where S_m is a
non-zero constant: S_3(3,3,T) = 63, S_3(17,17,T) = 36, S_3(111,111,T) = 33 on A, S_4 = 43 at the three
2-torsion points of A). (5) A derivation that "every m" does not follow from Theorem 1 and the group law:
on the contrary, Part 1 steps 2 to 5 derive it uniformly in m from exactly those two inputs. (6) A generic
fibre in the quantity's domain with non-trivial Frobenius: none. **No clause is met.**

**Carve-out classification of every finding (RC-3).** I make no correction to the committed statement.
Every degeneracy observed falls inside a pre-declared carve-out and the statement already covers it:
repeated roots (multiplicities 2, 3, 4 observed; e.g. (T_2, T_2, T_2) gives x(T_2) with multiplicity 4)
are C1-a and the statement says "with multiplicity"; the S_{m-1}(x) = 0 sublocus is C1-b and every
instance MATCHES the stated formula (the finding that would break, a contradiction of the formula, did not
occur); roots at infinity are C1-c and are counted in P^1 as stated; non-squarefree or degree-deficient
fibres are C1-d, outside the quantity's domain, and the record claims nothing about them beyond the
splitting and multiset statements, which hold there too; p <= 3, singular curves and non-affine points are
C1-e and are excluded by the stated setting. Nothing meets the breaking artifact outside a carve-out, so
nothing composes as B-D or B-W on this joint (A01 K4c): the K4c cure of the predecessor's SC-2 is complete
on my reading, because the corrected statement is now carried verbatim as the scope of a committed record
(EV-MONO-1ef611) and this is the fresh rule-12 review of that record.

**Two observations outside the breaking artifact (not corrections).** (O-J1-a) The formal leading
coefficient lc_T S_m = S_{m-1}(x_1..x_{m-1})^2 (Part 1 step 2) is the precise form of the clause "exactly
2^{m-2} iff S_{m-1}(x) != 0"; the statement is correct as written and need not carry it. (O-J1-b) On a
curve with few points (A, #E = 144) most m=5 factor-base fibres are non-generic (17 of 24 random tuples
had coincident roots); this is a count of excluded fibres, not a defect: the quantity is defined on generic
fibres and the record says so (C1-d).

**Verdict: CONCUR.** The quantity is exactly 0 by a derivation I reproduced independently, uniformly in m
for p > 3, and the committed scope (i) states the object precisely, including the degenerate subloci.

**Reading declaration (J1).** Before the blind section: the card (with its embedded prior, disclosed in
Part 0), agents/validator.md, AGENTS.md, docs/claims-and-verification.md. After it: the predecessor report
(blind section, J1, corrected statement, proves-too-much, attestation); EV-MONO-1ef611 (obstruction block,
OB-2, OB-3, citations); DEC-20260930-8553d4 (R-J1, R-BLIND, CU-1); DEC-20260810-2f86db D-1;
EV-MONO-a0a89c OBS-4, OBS-5; amendment A01 K4. Code: derive_s3_s4.py, blind_main.py (all in
`computations.json`).

## Part 3. J2 - scope honesty of the cured object: **CONCUR**

**Method actually used.** (a) A sentence-level read of CORR-20261005-a53ac8 (prior_value, S1 to S3,
consequences_CC3, carried_prohibition, does_not) against the O-1 breaking artifact in both directions.
I recomputed the D-5 transport identity and the OBS-1 identity symbolically with my own S_3 (both
differences are the zero polynomial; `computations.json` `j2_checks`), so S1 is not taken on the
producer's word. (b) A sentence-level read of every field of EV-MONO-1ef611, including resource_check
R1 to R3 and the spawned_ids list, for any reading that closes the relation-rate question, answers the
relation-supply half of KN-OPEN-009, condemns or promotes the D-4 count, closes another statistic, or
speaks over extension fields or at cryptographic scale. (c) The O-3 counter-statement located in committed
text. (d) Q-A decided from DEC-20260904-dd58c3's own text and the goal head. (e) The R2 sentence traced
to its source and to the three committed records that take it up. (f) The "CLAIMED NOWHERE ELSE"
exclusions tested against proves-too-much object 3 (Part 5). (g) The six spawned_ids records opened at the
lines EV-MONO-1ef611 cites, to check that each says what is attributed to it and that no status is
asserted.

**(a) O-1.** CORR-20261005-a53ac8 withdraws the condemnation completely: S1 (identity holds, which I
confirmed), S2 (it governs only a swapped Frobenius or cycle-type statistic, trivial on the locus; confirmed
by object 2: 283,160 of 283,160 swapped fibres split completely), S3 (the D-4 count is NOT condemned at m=3
or at any m, on the logical gap "rational does not imply in the factor base", not on any N(R) value),
consequences_CC3 (neither branch of D-5 or N-2 is carried forward; the YES branch is withdrawn as a
non-sequitur; the NO branch is not converted into "the live relation-rate instrument"; the designation of
D-5 as D-4's falsification check is withdrawn; D-4 stays an untested proposal; nothing else in
DEC-20260810-2f86db is superseded), and carried_prohibition. It does not overreach the other way: does_not
states that it does not state that the count discriminates, varies in any curve-specific way, or bears on
relation rate, and S3_values_note quotes no N(R) figure. The goal head's immutable `next_action` still
reads "gated on its D-5 m=3 collapse check"; the additive next_action_2026_10_05 line reads that clause as
superseded by the correction (A01 K3c). One reading to avoid in any adopting text: S2's "a swapped
Frobenius or cycle-type statistic is trivial on the factor-base locus" is a statement of what the identity
shows, not a closure of that statistic as a lane; EV-MONO-1ef611 scope (ii) keeps every other statistic out
of scope. **Answered by committed text.**

**(b) O-2.** EV-MONO-1ef611's `inference` is D-2-narrowed in its own words ("It does NOT answer the
relation-rate question, it does NOT answer the relation-supply half of KN-OPEN-009, it says nothing about
any other statistic ... the imprimitivity half ... is not closed"), it refuses EV-MONO-a0a89c's inference
sentence explicitly, and its `supersedes_note` replaces the operative reading of that sentence. Boundaries
item 2 repeats the narrowing. DEC-20260930-8553d4 CU-2 carries it. **Answered by committed text.** No
sentence of EV-MONO-1ef611 or CORR-20261005-a53ac8 closes the relation-rate question or any statistic other
than the generic-fibre cycle-type census in the EXP-MONO-4b50b6 form; none speaks over extension fields or
at cryptographic scale except to exclude them.

**(c) O-3.** The counter-statement "no completion criterion of GOAL-MONO-001 has been adopted as met by
any committed decision" is in DEC-20260930-8553d4 CU-3 and official_status_changes, in the goal head
(next_action_2026_09_30, _10_05, _10_06_cu6, _10_16), and in EV-MONO-1ef611 boundaries item 3. The
immutable IMP-2 line ("NOT a blocker on GOAL-MONO-001's own already-closed criteria") stands but is
countered additively. **Answered by committed text.**

**(d) O-4 and Q-A.** The texts. DEC-20260904-dd58c3 next_action item (3): "This closes the m=4 monodromy
sub-thread that began with D-3 of DEC-20260802-a51c82: the imprimitivity half of KN-OPEN-009 at m=4 is
now resolved (full symmetric monodromy, no exceptional locus at this arity), leaving m>=5 and the
relation-rate half as the remaining live content". The same record's scope_statement: "Scoped to full S_4
monodromy at m=4 over the symmetric base, at toy scale, on 4 curves at 2 primes ... does resolve the
imprimitivity/monodromy disjunction the question's own title names, at this specific arity and scale.
Does not extend to m != 4 or to cryptographic scale." The goal head next_action_2026_09_04: "full S4
monodromy at m=4 DECISIVELY CONFIRMED, closing the m=4 imprimitivity sub-thread (H-MONO-ebd400,
DEC-20260904-dd58c3)". The overreach is the universal reading of "no exceptional locus at this arity" and
"DECISIVELY CONFIRMED" against a census of 4 curves at 2 primes (the predecessor's O-4). **Not yet
answered by any committed record** (A01 K3 effect_on_committed_report agrees); EV-MONO-1ef611 boundaries
item 4 carries it as a reading-narrowing only and leaves the K3b question open.

**Q-A decision: (i) a counter-statement carried in the adopting decision and its projections suffices
(A01 K3c); no correction record is required (A01 K3b).** Reasons. (1) K3b requires a correction record
only when the answer "narrows a committed record's own directive or disposition, rather than how the
decision reads that record". The narrowing O-4 needs ("rests on a census of 4 curves at 2 primes, on the
symmetric base, at toy scale") is ALREADY COMMITTED INSIDE DEC-20260904-dd58c3 ITSELF, as its
scope_statement and its first limitation ("Toy scale only; no claim about m>=5 ... or about arithmetic
monodromy at cryptographic-scale primes"). A counter-statement that reads item (3) under the record's own
scope_statement narrows nothing in that record; it reads the record consistently with itself. Item (3) sits
in next_action, which is not where a decision sets its scope; `scope_statement` is. (2) Item (3) is a
summary disposition, not a directive that a session could follow to close a live lead, which is the harm
K3b's exception exists for and which distinguished D-5/N-2 (whose YES branch directed a session to
"report the collapse as the result", hence CU-5). Nothing in item (3) directs any act that the route-(c)
adoption would rest on or that would close an untested successor. (3) The precedent K3 itself cites is of
exactly this kind: DEC-20260810-2f86db D-2 narrowed EV-MONO-a0a89c's own inference sentence without a
correction record, and the predecessor treated that as neutralising O-2 provided the narrowing is carried
explicitly (CU-2 then carried it). O-4 is the O-2 pattern, not the D-5/N-2 pattern. (4) The goal-head line is
a Coordinator projection that the program corrects by additive lines (CU-3 is the precedent for O-3); a
correction record against a goal-head line is not the program's form. (5) The route-(c) adoption neither
rests on item (3) nor contradicts it when read with its scope_statement; the only texts the adoption writes
that touch the imprimitivity half are the C-4 supersession and the goal-head projection, and K1d already
forbids them from stating full monodromy on KN-OPEN-009's ordered base. What the counter-statement must
say, verbatim or equivalently, in the adopting decision, its goal-head projection and the C-4 supersession
text: "DEC-20260904-dd58c3 next_action item (3) and the goal-head line next_action_2026_09_04 'DECISIVELY
CONFIRMED' are read under DEC-20260904-dd58c3's own scope_statement: full S_4 monodromy at m=4 over the
SYMMETRIC base, at toy scale, on 4 curves at 2 primes. Neither establishes the absence of an exceptional
locus at m=4 for every curve; the uniform-in-curve statement is so far a single-reviewer derivation
(DEC-20260930-8553d4 CU-9) that no committed record has re-derived. This closure neither rests on nor
asserts those statements, and asserts nothing about monodromy on KN-OPEN-009's ordered base (A01 K1d)."
Residual, stated for the composer: the conservative route (ii) is harmless and costs one CORR; I do not
require it, because on K3b's own test the answer narrows how the adopting decision reads dd58c3, not what
dd58c3 says.

**(e) R2.** EV-MONO-1ef611 resource_check R2 quotes EV-MONO-a0a89c boundaries item 4 (the "WOULD move an
exponent" sentence, itself a quotation of RT O-8b) and immediately states: "The transfer from F_p, where
every measurement here was made, to F_{q^n} is an UNTESTED EXTRAPOLATION. This record asserts nothing
about any exponent." The three records it names take the clause up as the record says: IDEA-20260803-ff7415
(status proposed) makes the compounding clause its object and pre-registers a test of exponent lever
versus double count, with its own prediction on the double-count side (its lines 4-41, read);
IDEA-20260904-a1b81b (proposed) carries the clause as a conditional on an unvalidated transfer assumption
H3 (its lines 23-30 and 745-753, read); H-MONO-663fb4 reports both counting conventions because of the
suspected double count (mechanism item (4), lines 66-74, read). The sentence is carried as an untested
extrapolation and asserted nowhere. **No overreach.** Object 3 (Part 5) is the nearest thing to a test of
the extension-field setting this review could run, and it shows the group-law argument does not even reach
factor-base membership there, which is consistent with the record's refusal to claim anything over
F_{q^n}.

**(f) "CLAIMED NOWHERE ELSE".** The exclusions (not for any other statistic, not for the D-4 count, not
over extension fields, not at cryptographic scale, not as an ECDLP or security statement) are each
consistent with Part 5: on object 2 the D-4 count varies, on object 3 the extension-field analogue varies.
**No overreach.**

**(g) spawned_ids.** Each of the six records says, at the cited lines, what EV-MONO-1ef611 attributes to it
(IDEA-20260805-a9a95d: a statistic defined on the factor base, placed where OBS-5 shows the census
degenerate; H-MONO-663fb4 P3; IDEA-20260805-90df50: a root-multiplicity statistic on the same sublocus;
IDEA-20260831-d29a71 lines 240-245 and 483-486; IDEA-20260904-a1b81b E3, with its "D-5 killed at m=3"
description now read under the correction; IDEA-20260803-ff7415, R2 only). Statuses: five `proposed`, one
`supported_scoped_...`; the record asserts none of them. Line references are accurate to within a few
lines (a9a95d D3 spans lines 41-49 rather than 42-45); immaterial.

**New finding in the cured records (sub-threshold).** **N-1 (overreach of wording; does not reach the
breaking artifact).** resource_check R1 says: "any discriminating content left in a relation-search
statistic on that locus must therefore come from factor-base membership, and factor-base membership is
what the D-4 count measures." The word "must" excludes a second source the same record lists among its own
spawned_ids: the root-multiplicity structure of the fibre, which SC-1 and Part 1 show is non-constant on the
locus (multiplicities 2, 3, 4) and which IDEA-20260805-90df50 takes as its statistic. The sentence is
explicitly "a design input only" and the record disclaims that the count discriminates, so it licenses none
of the breaking-artifact statements. Label: overreach (minor), not a DISSENT ground. Under A01 K3 it is a
cure condition: the adopting decision carries a one-clause narrowing ("or from the root-multiplicity
structure of the fibre, which is also non-constant on the locus (SC-1; IDEA-20260805-90df50)"). Because R1
is a reading, not a directive or disposition of the record, a counter-statement in the adopting decision
suffices (K3b).

**Findings table, O-1 to O-4 (plus N-1).**

| finding | what it is | answered by committed text? | where |
| --- | --- | --- | --- |
| O-1 | D-5/N-2 condemn the D-4 count on a check that cannot fail | YES, completely | CORR-20261005-a53ac8 S1-S3, consequences_CC3, carried_prohibition; DEC-20260930-8553d4 CU-4; goal head next_action_2026_10_05 |
| O-2 | EV-MONO-a0a89c inference sentence reads as closing the relation-supply half | YES | DEC-20260810-2f86db D-2; DEC-20260930-8553d4 CU-2; EV-MONO-1ef611 inference, boundaries 2, supersedes_note |
| O-3 | IMP-2 "already-closed criteria" | YES | DEC-20260930-8553d4 CU-3; goal head next_action_2026_09_30 and later lines; EV-MONO-1ef611 boundaries 3 |
| O-4 | dd58c3 item (3) and goal-head "DECISIVELY CONFIRMED" overreach their cited census | NOT yet; Q-A = (i): counter-statement in the adopting decision and its projections, text given above | EV-MONO-1ef611 boundaries 4 carries it as a reading-narrowing only |
| N-1 | R1 "must come from factor-base membership" | NOT yet; sub-threshold; K3 cure by a one-clause narrowing in the adopting decision | EV-MONO-1ef611 resource_check R1 |

**Breaking-artifact assessment (plan J2).** No reading of EV-MONO-1ef611, CORR-20261005-a53ac8, or of
DEC-20260810-2f86db as narrowed, licenses "the relation-rate question is closed or answered", "the D-4
count is condemned" or "discriminates", closure of any other statistic, any statement over extension
fields or at cryptographic scale, or criterion (a) or full monodromy on the ordered base. Not met.

**Carve-out classification (RC-3).** No correction is made to any committed text. O-4 is handled under the
plan's own Q-A (composition CU7-C4), N-1 under A01 K3 as a sub-threshold cure condition; neither is a
correction outside a carve-out. Staleness in the underclaim direction (C-7; A01 K3e): the goal head's
immutable `next_action` ("imprimitivity half ... stays LIVE and non-degenerate at m >= 4"; "fresh budget
grant"; "STILL BLOCKED ON REVIEW") and `paused_because` are stale and countered by later additive lines;
listed only, not a ground.

**Verdict: CONCUR.** The cured texts close only the generic-fibre Frobenius cycle-type census in the
EXP-MONO-4b50b6 form as a relation-rate probe; O-1 to O-3 are answered in committed text; O-4 is decided
under Q-A as (i) with the counter-statement specified; N-1 is a sub-threshold wording cure; nothing new in
the cured records overreaches.

**Reading declaration (J2).** CORR-20261005-a53ac8 (all); EV-MONO-1ef611 (all); DEC-20260810-2f86db (all);
DEC-20260930-8553d4 (all); amendment A01 (all); DEC-20260930-6f1d85 (all); DEC-20260904-dd58c3 (all);
DEC-20260802-a51c82 (all); goal.yaml (all) and the three checkpoint shards; BATCH-1f9bf0 queue notes;
EV-MONO-a0a89c (all); the predecessor report J2 and proves-too-much sections; KN-OPEN-009; RQ-MONO-001;
the cited lines of the six spawned_ids records. Code: j2_checks.py, ptm_objects.py.

## Part 4. J3 - adequacy for criterion (c) and the closure gate: **CONCUR**

**Method actually used.** The closure-gate table was built field by field from EV-MONO-1ef611.obstruction
against agents/coordinator.md "Closure gate" (lines 219-247), the obstruction template
(templates/research-records.md lines 353-370), AGENTS.md "Research direction" and
docs/agent-contract-extended.md lines 525-545, docs/inventor-protocol.md section 4, and
docs/claims-and-verification.md "Refutation artifacts". Q-B was owned explicitly. The criterion-(c) quote
trail was rebuilt from goal.yaml and the decisions, with git metadata (commit count on origin/main,
ancestry of the snapshot commits) and the archive receipts checked for the two cured records. No new
mathematics beyond Parts 1, 2 and 5.

**Closure-gate table.**

| gate field | present | adequate | reading |
| --- | --- | --- | --- |
| quantity | yes | yes | "the fraction of generic fibres over the factor-base locus (squarefree, full degree 2^{m-2}) on which Frobenius acts non-trivially on the roots" - well defined, and identical to Part 1 quantity (iii) |
| value with units | yes | yes | "0, an exact dimensionless fraction, BY DERIVATION" - a value, with its unit (a dimensionless fraction), at the derivation tier that docs/claims-and-verification.md ranks above empirical-only |
| error statement | yes | yes (see note) | "NOT a sampled estimate, so no sampling error bar applies, and none is stated", followed by the zero-exception corroboration cited by location. An exact derived value admits only this form of error statement: the uncertainty is nil at the derivation tier and the statement says so explicitly rather than leaving the field silent. The purpose of the "error bars" wording (a later reader can compare and re-scope the number) is served. Note: the block cites the corroboration counts by pointer rather than restating them; the adopting text should state them (1,196 off-diagonal pairs at m=3 per EV-MONO-a0a89c OBS-4; the predecessor's 2,401 + 117,649 + 10,404 + 182,104 exhaustive tuples; this review's 316,290 generic fibres), which costs nothing and makes the datum self-contained |
| measured_by | yes | yes at m=3; derivation beyond | [RUN-MONO-4b50b6-002, EXP-MONO-4b50b6]. RUN-002 V4, as EV-MONO-a0a89c OBS-4 records it, classifies every off-diagonal factor-base pair on every censused curve at m=3: 1,196 pairs, 0 non-split, independently reproduced by both BATCH-003 reviewers. That is this quantity at m=3 (a non-split fibre is exactly a fibre with non-trivial Frobenius; the excluded diagonal is the m=3 degree-drop sublocus). The run itself lies under blind_from and I did not open it; I recomputed the same quantity at m=3 on my own curves (6,554 exhaustive pairs plus 600 random, 0 exceptions). No RUN-* exists for m >= 4; the corroboration there is review computation (the predecessor's and mine), and the record says exactly that |
| scope | yes | yes | (i) the CU-1 statement verbatim (= Part 1); (ii) the instrument in the EXP-MONO-4b50b6 form as a relation-rate probe, no other statistic, projection or question; (iii) every m >= 3 with p > 3 by derivation, measured corroboration m=3 (run) and m <= 5 (review), toy primes, no solver, no budget; the exclusions; parts (ii), (iii) narrow (i) |
| scope match (Q-B) | - | holds; condition NOT triggered | see below |
| resource_check | yes | yes | examined true; three readings R1 (the uncondemned D-4 count as a design constraint, with N-1's wording nit), R2 (the compounding clause as an untested extrapolation, with its three committed takers), R3 (the obstruction registry, none relied on); six spawned_ids, all existing committed records, each verified to say what is attributed (Part 3 (g)); the "examined and not listed" set is explained |
| refutation-artifact basis | declared | yes | proof_status derivation; proof_refs name the predecessor report and computations, DEC-20260930-8553d4 and EV-MONO-a0a89c's own refs; DEC-20260930-8553d4 closure_gate_check: no counterexample certificate applies to a constancy statement |

**Q-B: does a closure asserted "at every m" match an obstruction whose measured scope is m <= 5 at toy
primes?** Yes, and the agents/coordinator.md condition "measured over a narrower scope than the closure
asserts" is NOT triggered. The condition targets a measured value extrapolated beyond the range it was
measured on. Here the value at every m is not an extrapolation of the m <= 5 measurements: it is derived,
uniformly in m, from the group law and the zero-set theorem (Part 1 steps 2 to 5, independently of the
predecessor's derivation), and the measurements corroborate the derivation where measurement is possible.
The record states the basis split precisely (scope (iii): "The 'every m' extent rests on the derivation
alone") and docs/claims-and-verification.md admits a derivation note as a refutation basis above
empirical-only. Two conditions on the adopting text follow, and they are composition duties already in the
plan (CU7-C2, C7), not new gaps: the closure must carry the derivation/measurement split verbatim and may
not describe the m >= 6 extent, or any prime above the toy range, as measured; and it must keep the
derivation's own hypotheses (p > 3, nonsingular E, affine F_p-rational base points). The remaining
dependence of the m >= 6 extent on Semaev's Theorem 1 is a dependence on a published theorem (retrieved by
the predecessor; recalled here), which a derivation-tier record may carry; it is not a scope mismatch.

**Criterion-(c) quote trail.**

| requirement | met by | my verification |
| --- | --- | --- |
| criterion (c): "a scoped instrument/protocol no-go is recorded" | goal.yaml completion_criteria (line 145) | read |
| committed Coordinator decision recording the no-go | DEC-20260810-2f86db, decided_by coordinator, decision reject_scoped | one commit on origin/main (07cff851de, 2026-08-10), never modified, ancestor of HEAD |
| scoped | closed_at_scope: "The generic-fibre Frobenius cycle-type census, in the frozen instrument form of EXP-MONO-4b50b6, AS A PROBE OF INDEX-CALCULUS RELATION RATE, at every m"; narrowed by D-2, by CU-1 to CU-4 and by CORR-20261005-a53ac8 | read; the narrowing chain is committed (DEC-20260930-8553d4 at 18b3b665fa; CORR at dd4dfbeca1) |
| instrument/protocol | decision_note: "WHAT IS REJECTED IS THE INSTRUMENT, NOT THE QUESTION" | read |
| no-go | D-1: "a genuine no-go for the instrument, and it is a no-go by derivation" | read; the derivation reproduced (Part 1) |
| recorded, as a datum | EV-MONO-1ef611 obstruction block (CU-6), snapshot-archived | one commit on origin/main (609bca4abb, 2026-10-06), ancestor of HEAD; receipt TASK-20261005-c96883 path_sha256 = my recomputed sha256 ae686fe9...3fbe |
| D-5/N-2 defect cured | CORR-20261005-a53ac8 | one commit (dd4dfbeca1), ancestor of HEAD; receipt TASK-20261005-7166be path_sha256 = my recomputed sha256 cfbbd928...6d36 |
| consistent with DEC-20260802-a51c82 N-2 | N-2 reasons about criterion (a) only ("criterion (a) required a census deciding full-versus-exceptional ... the derivation that did answer m=3 is not the committed decision the criterion asks for at m >= 4"); it does not examine (c) | read; no contradiction with adopting (c) |
| consistent with D-6 and D-9 | D-6 records that (c) was never adjudicated; D-9: "This decision RECORDS the no-go - as a Coordinator proposal whose adoption as official closure is gated on the rule-12 review" | read; this review is that review for the cured object |
| no hypothesis-status change | EV-MONO-1ef611 hypothesis_id names RQ-MONO-001 by convention and moves nothing; H-MONO-ebd400 is deliberately not named; H-MONO-663fb4 is listed in spawned_ids only; DEC-20260810-2f86db changes_no_hypothesis_status true | read |
| nothing beyond toy | claim_tier toy on both records; EV-MONO-1ef611 boundaries 1 and does_not (g) | read |
| K1d carried | EV-MONO-1ef611 boundaries K1d; nothing in the cured object states criterion (a) or ordered-base full monodromy | read |
| refutation basis declared | proof_status derivation on EV-MONO-1ef611 and EV-MONO-a0a89c | read |

**Gaps.** None that the cured object fails. Two composer notes, neither a gap in the object: (1) the
EV-MONO-1ef611 `strength: preliminary` and its `reviews: []` are the record's honest pre-review state; the
post-review ledger archive binds this report (BATCH-1f9bf0 queue note TOOL GAP 2 describes the two
admissible archive forms); (2) C-10 is carried in the record; this round's served model differs from the
producers' as reported (attestation `model_independence_note`), which the composer may record as reported,
never as probe-verified.

**Verdict: CONCUR.** The cured object is a scoped instrument no-go, recorded in a committed Coordinator
decision and now as a complete obstruction datum with its resource_check and a declared derivation basis;
adopting it under (c) moves no hypothesis status and nothing beyond toy tier; Q-B holds.

**Reading declaration (J3).** goal.yaml (all) and checkpoints BATCH-1f9bf0, BATCH-8609e2, BATCH-44adf9;
EV-MONO-1ef611 (all); CORR-20261005-a53ac8 (all); DEC-20260810-2f86db (all); DEC-20260802-a51c82 (all);
DEC-20260930-8553d4 (all); DEC-20260930-6f1d85 (all); DEC-20261016-5bdc04 (all); EV-MONO-a0a89c (all);
amendment A01 (all); the BATCH-1f9bf0 queue notes; agents/coordinator.md "Closure gate";
templates/research-records.md Evidence and obstruction block; AGENTS.md; docs/agent-contract-extended.md
lines 525-545; docs/inventor-protocol.md sections 4 to 7; docs/claims-and-verification.md. Git metadata
and the three archive receipts named in the attestation.

## Part 5. Proves-too-much control (all three objects; code and raw output in `computations.json` `proves_too_much`)

The argument under test, as EV-MONO-1ef611 states it: (1) the roots of S_m(x_1..x_{m-1}, T) are
x(sum eps_i P_i); (2) every P_i is in E(F_p), so every sum eps_i P_i is in E(F_p); (3) so every root is in
F_p and the fibre splits completely; (4) so the generic-fibre cycle type is constant on the locus. Run on
each object with my own code (`ptm_objects.py`, importing the blind-section modules).

**Object 1, a generic base tuple (x_i in F_p, not required to be x-coordinates of F_p-points).** The
argument stops at step (2). An x_i with f(x_i) a non-residue lifts to a point of E(F_{p^2}) outside
E(F_p), on which p-Frobenius acts as negation (y^p = -y; raw examples at p = 131 in
`failing_step_examples_p131`), so the sign-class sums need not be F_p-rational and the census statistic
varies:

| set | tuples | generic fibres | generic with non-trivial Frobenius | cycle types observed, by number of on-locus coordinates |
| --- | --- | --- | --- | --- |
| A (p=131), m=3, all of F_p^2 | 17,161 | 16,256 | 8,120 | both on-locus: 1+1 (4,830); one off-locus: 2 (8,120); both off-locus: 1+1 (3,306) |
| D (p=61), m=4, all of F_p^3 | 226,981 | 191,688 | 148,512 | 3 on-locus: 1^4 (30,600); 2 on-locus: 2+2 (84,864); 1 on-locus: 2+2 (63,648); 0 on-locus: 1^4 (12,576) |
| B (p=1999), m=4, 20,000 random | 20,000 | 19,907 | 14,888 | 3: 1^4 (2,372); 2: 2+2 (7,257); 1: 2+2 (7,631); 0: 1^4 (2,647) |

The argument does not prove constancy here (the statistic takes two values on each set); the fully
on-locus rows are the blind-section result again (0 non-trivial), so constancy on the factor-base locus is
a locus effect and the generic tuple is the null object of the same shape. Failure signature: not
triggered. Observation outside my joints (RC-8): the observed dependence of the cycle type on the on-locus
count alone is the pattern the predecessor called the delta-rule (CU-9); I report the histogram and rely
on nothing beyond it.

**Object 2, the D-4 factor-base-point count.** Definition from DEC-20260810-2f86db D-4/N-2: fix
T = x(R) and count the factor-base tuples (x_1..x_{m-1}) in V^{m-1}, V the x-coordinates of the factor
base, lying on the fibre S_m(x_1..x_{m-1}, x(R)) = 0; call it N(R). The argument transfers to the swapped
Frobenius statistic and stops at the step "rational over F_p" to "in the factor base V": the roots of
S_m(x_1, .., X, .., x(R)) in the free coordinate are x(R +- P_1 +- ...), all F_p-rational (step 3 goes
through, by the symmetry of S_m), so the swapped fibre always splits; but membership of those roots in V
is not implied, and N(R) counts membership. Measured with my own factor bases (two routes, polynomial
roots in V versus group-law sign sums, agreeing for every R):

| curve, m, factor base | #V | x(R) values | N(R) min..max (mean) | distinct values | R with N(R) = 0 | swapped fibres splitting completely |
| --- | --- | --- | --- | --- | --- | --- |
| B (p=1999), m=3, x < 400 | 204 | 976 | 44..119 (85.07) | 61 | 0 | 199,104 / 199,104 |
| C (p=1009), m=3, x < 60 | 30 | 532 | 0..12 (3.33) | 13 | 84 | 15,960 / 15,960 |
| C (p=1009), m=3, x < 250 | 128 | 532 | 40..86 (61.35) | 42 | 0 | 68,096 / 68,096 |
| D (p=61), m=4, x < 20 | 11 | 35 | 76..150 (120.51) | 22 | 0 | - |

With a small factor base the count reaches 0 for 84 of 532 targets while the swapped Frobenius statistic
is trivial on every one of the 15,960 swapped fibres: the count and the Frobenius statistic are different
objects, exactly as CORR-20261005-a53ac8 S2/S3 state. The argument in the cured object does not yield
constancy for the count; failure signature not triggered. (The N(R) figures are review computations at toy
scale on a few factor bases; they show variation and nothing else, and the correction's withdrawal does
not depend on them.)

**Object 3, the extension-field analogue (resource_check R2).** q = 131, F_{q^2} = F_q[w]/(w^2 - 2),
n = 2, E: y^2 = x^3 + (3+5w)x + (7+2w) (a general curve over F_{q^2}, not defined over F_q), factor base
{P in E(F_{q^2}) : x(P) in F_q} (74 x-values). The group-law argument gives the roots x(P_1 +- P_2) in
F_{q^2} (my S_3 with F_{q^2} coefficients vanishes at every one of them: `m3_S3_vanishes_at_every_root_over_Fq2`
true), which is "rational over the field of definition of the points"; it does not reach "in the factor
base", i.e. x in F_q, and the fraction of roots in F_q varies: over 200 random factor-base pairs at m=3,
0 of 2 roots in F_q for 191 pairs, 1 of 2 for 4, 0 of 1 for 5 (overall 1.0%); over 60 random triples at
m=4, 0/4 for 53, 1/4 for 3, 2/4 for 4. Control, a curve defined over F_q (a = 44, b = 103, the curve A
viewed over F_{q^2}): the fraction is 2/2 for 102 pairs, 0/2 for 96, 1/1 for 2 (overall 51.8%), again not
constant. A q-Frobenius statistic (fixedness of the roots under x -> x^q, i.e. membership in F_q) is
therefore not trivial on this factor base. The stopping step is exactly "rational over F_{q^2}" versus "in
F_q"; failure signature not triggered. This is consistent with EV-MONO-1ef611's exclusion of extension
fields and with its treatment of R2 as an untested transfer.

**Result.** The argument stops at the locus boundary on all three objects, at the named steps; nothing in
the cured object proves constancy, triviality or factor-base membership on any of them (A01 K4a has nothing
to compose). The generic tuple serves as the null object of the same shape: the statistic varies there and
is constant on the factor-base locus.

## Part 6. Composition questions, observations outside my joints, independent recomputation, reading declaration

**Composition questions (CU7-C5).** Beyond Q-A and Q-B (both answered above) I identify none. N-1 is a
sub-threshold J2 finding that A01 K3 already governs, not an unstated question. Two tooling observations
for the composer, neither a composition question: (T-1) `tools/check_review_independence.py` checks the
blind_from intersection mechanically and cannot express the plan's sequenced lift of the third path; my
attestation lists the predecessor paths honestly, so the checker reports that path as "leaked" (the self-run in
`computations.json` `independence_check_self_run` reports exactly that one problem and no other); the plan's
PD-2 and the attestation note explain it, and the frozen-hash record shows the order. (T-2) The post-review
ledger archive's form for EV-MONO-1ef611 (BATCH-1f9bf0 queue note TOOL GAP 2) is for the archive designer.

**Observations outside my joints (RC-8).** (i) Object 1's histogram touches the CU-9 delta-rule; reported
as data only. (ii) Nothing here touches ordered-base or symmetric-base monodromy, criterion (a), or any
security estimate. The claim-tier ceiling stays toy; no number here is an ECDLP result.

**The Coordinator's prior versus this outcome (information, not a verdict).** J1 CONCUR (prior 0.85);
J2 CONCUR with Q-A = (i) (prior 0.6 on CONCUR, 0.55 on (ii)); J3 CONCUR with Q-B not triggered (prior 0.7).
Under the plan's own CU7-C2 the conditions my joints control are met; the composition, the adopting
decision and the K1d/K3c/Q-A carries are the Coordinator's. No whole-goal verdict is issued (RC-3, CU7-C8).

### validation_report (agents/validator.md required output) and independent_recomputation

```yaml
validation_report:
  id: null                      # not minted; identified by its task and archived by TASK-20261016-548959
  task_id: TASK-20261016-9c1bc5
  run_ids: []                   # zero runs; the objects reviewed are committed records
  artifact_checks:
    - Custody: the three named files at HEAD c59b45a85a hash to the values the top-level session observed (Part 0.1); re-hashed unchanged at the end of the session (computations.json custody_recheck).
    - EV-MONO-1ef611 and CORR-20261005-a53ac8 each have exactly one commit on origin/main and are ancestors of HEAD; their archive receipts' path_sha256 equal my recomputed digests.
    - DEC-20260810-2f86db, DEC-20260930-8553d4, DEC-20260904-dd58c3, EV-MONO-a0a89c and amendment A01 each have exactly one commit on origin/main (never modified).
    - The predecessor snapshot a1a070493457 and the EV snapshot 609bca4abbca are ancestors of HEAD.
    - No sibling report exists in this round; the blind section was frozen (sha256 244bca56...50afb) before any blind_from path was opened.
  metric_recomputations:
    - The obstruction value (fraction of generic factor-base-locus fibres with non-trivial Frobenius) - RECOMPUTED as 0 on 316,290 generic fibres over 439,829 base tuples at m = 3, 4, 5 on four curves of my own, with my own S_3, S_4, S_5 (Part 1).
    - The CU-1 corrected statement, every clause - RE-DERIVED independently and RECOMPUTED (Part 1, Part 2).
    - lc_T S_m = S_{m-1}^2 - RECOMPUTED symbolically (m=4) and numerically (m=5).
    - OBS-1 identity and the D-5 transport identity - RECOMPUTED symbolically with my own S_3; both hold identically.
    - The D-4 count N(R) - RECOMPUTED on my own factor bases by two routes; it varies and reaches 0.
    - 1196/1196 (RUN-MONO-4b50b6-002 V4, m=3) - NOT recomputed as that artifact (blind_from); the same quantity recomputed at m=3 on my curves: 0 exceptions in 6,554 exhaustive and 600 random pairs.
    - The predecessor's exhaustive counts (2,401; 117,649; 10,404; 182,104; all "ok") - READ from its committed computations.json by key, NOT re-run; superseded in coverage by my own sweeps on different curves.
  control_checks:
    - Proves-too-much object 1 - PASSES (stops at step 2; statistic varies off-locus; null object of the same shape).
    - Proves-too-much object 2 - PASSES (stops at "rational" to "in the factor base"; N(R) varies, swapped Frobenius trivial).
    - Proves-too-much object 3 - PASSES (stops at "rational over F_{q^2}" to "in F_q"; fraction in F_q varies).
  heuristic_validation_checks: []   # not applicable: no heuristic-conditional claim is under review
  cost_model_checks: []             # not applicable: no cost, speedup or exponent claim; nothing to charge and no baseline ratio exists or is claimed (R2 is carried as untested and asserted nowhere)
  proof_architecture_checks:
    - Baseline fixture: my S_3 from the group law has the Theorem 1 shape (lc (x_1-x_2)^2; disc 16 f(x_1) f(x_2)); my S_4 and S_5 satisfy the defining property over the algebraic closure at p = 13, 17 with 0 mismatches (degenerate points included).
    - Quantifier order: the statement is uniform - for all m >= 3, all p > 3, all nonsingular E/F_p, all affine P_i in E(F_p); no per-instance witness is used.
    - Observation collision: the Frobenius cycle type is constant across targets R whose factor-base counts differ (object 2), so it cannot identify relation supply; this is the no-go's content, not a defect.
    - Method ceiling and nearby object: the group-law method reaches Frobenius statistics over the field of definition only; it reaches neither factor-base membership (objects 2, 3) nor off-locus tuples (object 1).
    - Strictness witness, interface preservation: not applicable (no improvement or reduction claim).
  verdict: passed
  verdict_note: >-
    Scope of this terminal verdict, as the tier defines it: the reviewed records (EV-MONO-1ef611,
    CORR-20261005-a53ac8, with DEC-20260810-2f86db as narrowed) are admissible as the cured route-(c)
    object - present, committed, unmodified, custody-matched, with every recomputable number recomputed
    and agreeing. "passed" says the receipt is admissible and nothing more. The review's content is the
    per-joint verdicts (J1 CONCUR, J2 CONCUR, J3 CONCUR), the Q-A and Q-B answers, and the control results;
    no whole-goal verdict is issued.
  limitations:
    - One reviewer owned every joint, the control and the blind re-derivation (plan PD-1); coverage, not cross-reviewer independence.
    - Semaev 2004 could not be retrieved in this session (Cloudflare challenge); for m >= 6 the "every m" extent rests on the published theorem as a recalled pointer plus the predecessor's retrieval.
    - Toy primes only (13 to 1999 here). Nothing is an ECDLP result; no security estimate moves.
    - The run RUN-MONO-4b50b6-002 and BATCH-003 artifacts lie under blind_from and were not opened; their numbers are taken as EV-MONO-a0a89c records them.
    - Model identity is as the runtime reports it; not probe-verified.
  artifact_paths:
    - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/review_report.md
    - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/computations.json
    - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/review_attestation.yaml
```

**independent_recomputation.** Recomputed myself (code and raw output embedded in `computations.json`):
S_3 from the group law; S_4 and S_5 by two routes; the defining property over the closure; the root
multiset, degree, c, leading coefficient and Frobenius census on 439,829 factor-base tuples; the five
degenerate types; the OBS-1 and D-5 identities; the D-4 count N(R) by two routes; objects 1 to 3.
Re-verified with a disjoint lineage: my S_4 (sympy resultant) against my formal Sylvester determinant
(pure Python, 100 tuples); my group law against the polynomial route on every object-2 target; the
predecessor's S_4 term count (540) and lc identity reproduced from scratch without reading its S_4; no
PARI or FLINT was used, so my lineage is disjoint from the predecessor's cross-checks as well as from the
producers' (the producers' code was never opened). Taken on the producers' or predecessor's word: the
1196/1196 count of RUN-MONO-4b50b6-002 V4 and the 193/193 count of TASK-20260802-1b4130 O-9 (blind_from;
superseded in coverage by my sweeps); the predecessor's exhaustive counts (read by key, not re-run); the
statement and attribution of Semaev's Theorem 1 (recalled; retrieval blocked); the model identities earlier
sessions recorded; the archive and receipt verification status reported by the top-level session (I
checked git reachability and receipt digests only). What would make each claim false, and whether it was
checked: J1 - a factor-base-locus fibre with a non-rational root, a root outside the sign-class multiset,
a degree not equal to 2^{m-2} minus the O-class count, or c = 0: checked on 439,829 tuples including every
degenerate type, none found. J2 - a sentence in the cured records licensing a breaking-artifact statement:
checked sentence by sentence, none found; one sub-threshold wording nit (N-1). J3 - a gate field missing or
inadequate, or a scope narrower than the closure asserts: checked field by field; none; Q-B not triggered.

**Scope findings.** None. The three declared artifacts are the only files written in the repository; all
scripts and intermediates live in the session scratchpad and are embedded in `computations.json`.

**Reading declaration.** Complete and ordered in `review_attestation.yaml` `sources_read` and `not_read`;
Part 0.3 gives the pre-blind segment. Every read happened at HEAD `c59b45a85ad1d8289a1ff3a19dad0fd722956630`
on branch `claude/quotient-summation-ecc2k-130-4y7t3o`, working tree clean apart from this task's own
directory.

## review_attestation (verbatim copy of `review_attestation.yaml`, the machine-readable artifact)

```yaml
# review_attestation for TASK-20261016-9c1bc5 (REVIEW-MONO-20261016-9c1bc5), machine-readable copy
# (DEC-20260930-8553d4 CU-10; DEC-20261016-5bdc04 Q-ATT). Written by the reviewing session itself.
# The verdict vocabulary of tools/check_review_independence.py is holds|breaks|inconclusive; the card's
# vocabulary is CONCUR|DISSENT|INCONCLUSIVE. Both are given; CONCUR = holds, DISSENT = breaks.
review_attestation:
  task_id: TASK-20261016-9c1bc5
  plan_id: REVIEW-MONO-20261016-9c1bc5
  goal_id: GOAL-MONO-001
  batch_id: BATCH-450ac7
  archived_by: TASK-20261016-548959
  role: validator-breakthrough
  reviewer_role: validator
  joints_owned:                  # the plan's joint labels (first sentence of each joint), as tools/check_review_independence.py reads them
    - "J1 - DERIVATIONAL SOUNDNESS OF THE CURED STATEMENT AS COMMITTED SCOPE"
    - "J2 - SCOPE HONESTY OF THE CURED OBJECT"
    - "J3 - ADEQUACY FOR CRITERION (c) AND THE CLOSURE GATE"
  joints_owned_short_labels: [J1, J2, J3]
  instruments_owned: [proves_too_much, blind_rederivation]
  verdicts:                      # checker vocabulary, one entry per owned joint, keyed by the plan's joint labels
    "J1 - DERIVATIONAL SOUNDNESS OF THE CURED STATEMENT AS COMMITTED SCOPE": holds
    "J2 - SCOPE HONESTY OF THE CURED OBJECT": holds
    "J3 - ADEQUACY FOR CRITERION (c) AND THE CLOSURE GATE": holds
  verdicts_card_vocabulary:      # the card's vocabulary (RC-3)
    J1: CONCUR
    J2: CONCUR
    J3: CONCUR
  verdict_reasons:
    J1: >-
      The CU-1 corrected statement, carried verbatim as EV-MONO-1ef611 obstruction.scope (i), is exactly what
      the blind re-derivation produced from the group law and the defining property, uniformly in m >= 3 for
      p > 3; corroborated with zero exceptions on 439,829 base tuples at m = 3, 4, 5 on four curves (p = 61,
      131, 1009, 1999), including every degenerate-sublocus type. No breaking-artifact clause is met; every
      finding lies inside a pre-declared carve-out (C1-a to C1-e) or matches the stated formula.
    J2: >-
      O-1 is withdrawn completely by CORR-20261005-a53ac8 S1-S3 and carried_prohibition without overreach the
      other way; O-2 and O-3 have committed answers; O-4 (Q-A) is answered (i): a counter-statement in the
      adopting decision and its projections suffices, because the narrowing is already committed inside
      DEC-20260904-dd58c3's own scope_statement. R2 is carried as an untested extrapolation and never asserted.
      One new sub-threshold wording finding (N-1, resource_check R1) composes under A01 K3 as a cure condition,
      not a DISSENT.
    J3: >-
      The cured object meets criterion (c) and the agents/coordinator.md closure gate: quantity, exact value
      with units and an explicit error statement, measured_by bearing on the quantity at m=3, scope with the
      derivation/measurement split stated, complete resource_check, refutation basis declared (derivation). Q-B:
      the "measured over a narrower scope than the closure asserts" condition is not triggered, because the
      "every m" extent is derived (re-derived here uniformly in m), not extrapolated; the adopting text must
      carry that split verbatim.
  q_a_answer: (i) counter-statement suffices (reasons in review_report.md Part 3, Q-A)
  q_b_answer: scope match holds; agents/coordinator.md narrower-scope condition NOT triggered (Part 4, Q-B)
  proves_too_much_result: >-
    The argument stops at the locus boundary on all three objects. Object 1: at the step "every P_i is in
    E(F_p)" (an off-locus x_i lifts to E(F_{p^2}) and p-Frobenius negates it); the census statistic varies
    (8,120 of 16,256 generic m=3 fibres and 148,512 of 191,688 generic m=4 fibres have non-trivial Frobenius
    off the locus). Object 2: at the step "rational over F_p" to "in the factor base"; the D-4 count N(R)
    varies (0..12 with 84 of 532 targets at N(R)=0 on one factor base; 44..119 on another) while the swapped
    Frobenius statistic is trivial (283,160 of 283,160 swapped fibres split). Object 3: at the step "rational
    over the field of definition F_{q^2}" to "in the factor base (x in F_q)"; the fraction of roots in F_q
    varies (0, 1/2, 1 all observed; overall 1.0% on a general curve, 51.8% on a curve defined over F_q).
  blind_rederivation_result: >-
    Agrees with the CU-1 statement in full: root multiset in P^1 = sign-class multiset with multiplicity;
    affine degree = 2^{m-2} minus the O-class count; c in F_p^*; lc_T = S_{m-1}^2; fraction of generic fibres
    with non-trivial Frobenius exactly 0 (316,290 generic fibres tested, 0 exceptions).
  whole_goal_verdict: none issued (RC-3; CU7-C8)
  independent_session: true
  independent_session_note: >-
    Fresh validator-breakthrough subagent session. It wrote none of the records under review, is not the
    TASK-20260930-40470a reviewer, and had read no blind_from path before the blind section was frozen.
  requested_policy: review-breakthrough
  reasoning_effort_requested: max
  reasoning_effort_as_served: max
  reasoning_effort_evidence: >-
    .claude/agents/validator-breakthrough.md frontmatter `effort: max`; CLAUDE_EFFORT=max in this session's
    tool-process environment; tools/check_runtime_bindings.py --list shows validator-breakthrough at effort
    max sourced from the agent file. Not otherwise observable from inside the session.
  resolved_runtime: claude_code 2.1.42 (Claude Agent SDK subagent; CLAUDE_CODE_CHILD_SESSION=1; remote environment cloud_default)
  resolved_model_id: claude-fable-5-1
  resolved_model_id_note: >-
    As the runtime reports it to this session ("Fable 5.1", model id claude-fable-5-1). It equals the
    `anthropic` backend binding of review-breakthrough in orchestration/model-bindings.yaml and the pin in
    .claude/agents/validator-breakthrough.md. Not probe-verified.
  model_verified: false
  model_verified_reason: no `python3 -m orchestration.adapter doctor --probe` receipt exists for this session; the identifier is the runtime's report, not a probe result.
  fallback_used: false
  fallback_reason: >-
    None needed: the served model identifier equals the policy's bound model for this runtime and backend
    (orchestration/model-bindings.yaml anthropic.review-breakthrough.model = claude-fable-5-1; agent file pin).
  degraded_allowed: false
  degraded_requirements: []
  amazon_bedrock: >-
    Not selected, configured, probed or contacted. ANTHROPIC_BASE_URL is https://api.anthropic.com and the
    resolved model identifier contains no "bedrock".
  model_independence_note: >-
    As reported by the runtimes (none probe-verified): this session ran on claude-fable-5-1, while the
    TASK-20260930-40470a reviewer, the DEC-20260930-8553d4 composer, the A01 author and the producers of
    CORR-20261005-a53ac8 and EV-MONO-1ef611 each record claude-opus-5-5, and DEC-20260904-dd58c3 records
    claude-sonnet-5. This round is therefore independent by session, role and (as reported) model family
    from the producers of the cured object. The C-10 disclosure is carried in the report.
  read_sibling_reports: false
  sibling_or_composer_materials_read: >-
    None. No report from this round exists (coordination/goals/GOAL-MONO-001/review/ held only the
    predecessor directory TASK-20260930-40470a/, a sequenced input under RC-2). No composer worksheet was read.
  producer_transcripts_read: none
  blind_from:
    - experiments/EXP-MONO-4b50b6/
    - coordination/goals/GOAL-MONO-001/batches/BATCH-003/
    - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/
  blind_from_respected: true
  blind_from_respected_note: >-
    True under the plan's own definition (blind_rederivation.blind_from_note; blindness.rationale; PD-2):
    the first two paths were never opened, listed, grepped or imported at any time; the third path was
    opened ONLY after the blind re-derivation section and its computations were complete and frozen
    (frozen text sha256 244bca5607c005444c7c2893fb13d419abc3e3da2d25fabe2ebe79aa39c50afb, recorded in
    computations.json at 2026-10-16T17:25:53Z; the predecessor report was first opened after that). The
    mechanical intersection check of tools/check_review_independence.py cannot express a sequenced lift and
    flags the third path: the self-run in computations.json independence_check_self_run reports exactly that
    one problem and no other; the composer reads it against this note and plan PD-2.
  blind_section_frozen_at_utc: '2026-10-16T17:25:53Z'
  blind_section_frozen_sha256: 244bca5607c005444c7c2893fb13d419abc3e3da2d25fabe2ebe79aa39c50afb
  order_of_work_as_followed: >-
    (1) card, role contracts, custody hashes; (2) blind re-derivation written, computed and frozen from the
    plan's quantity statement alone; (3) predecessor report and its computations.json opened; (4) records
    under review and context records read; (5) J1, J2, J3, Q-A, Q-B and the proves-too-much control
    (computations run after the D-4 definition had been read); (6) this attestation and the final report.
  sources_read:                  # every path read, in the order read; "hash only" and "listing" entries are marked
    - ledger/handoffs/TASK-20261016-9c1bc5.yaml
    - agents/validator.md
    - AGENTS.md
    - docs/claims-and-verification.md
    - CLAUDE.md (runtime-injected at session start)
    - "hash only, not read at this point: ledger/evidence/EV-MONO-1ef611.yaml; ledger/corrections/CORR-20261005-a53ac8.yaml; coordination/review/mono-20260930-44adf9/review-plan-amendment-01.yaml"
    - "directory listing only: coordination/goals/GOAL-MONO-001/review/; coordination/goals/GOAL-MONO-001/batches/"
    - templates/research-records.md (lines 768-807; later lines 290-380)
    - orchestration/model-bindings.yaml (grep hits; lines 170-200; backend headers)
    - orchestration/model-bindings.local.example.yaml (grep hits only)
    - tools/check_review_independence.py (lines 108-111, 148-160, 284-370, 880-940, 985-1032; grep hits)
    - "tool output: python3 tools/check_runtime_bindings.py --list; python3 -m orchestration.adapter resolve --role validator-breakthrough (error output)"
    - "--- blind section frozen here (2026-10-16T17:25:53Z) ---"
    - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/ (directory listing)
    - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/review_report.md (lines 1-1076, in full)
    - ledger/evidence/EV-MONO-1ef611.yaml
    - ledger/corrections/CORR-20261005-a53ac8.yaml
    - ledger/decisions/DEC-20260930-8553d4.yaml
    - ledger/decisions/DEC-20260810-2f86db.yaml
    - coordination/review/mono-20260930-44adf9/review-plan-amendment-01.yaml
    - ledger/decisions/DEC-20261016-5bdc04.yaml
    - ledger/evidence/EV-MONO-a0a89c.yaml
    - coordination/review/mono-20260930-44adf9/review-plan.yaml
    - ledger/decisions/DEC-20260904-dd58c3.yaml
    - ledger/decisions/DEC-20260802-a51c82.yaml
    - ledger/goals/GOAL-MONO-001/goal.yaml
    - "coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/s4_construction/computations.json (by key: structure, script names and sha256, outputs ptm_out.json curves/D5_transport/object2 summaries, fb_checks_out.json curves and exhaustive summaries, notes, retrieved_sources)"
    - ledger/decisions/DEC-20260930-6f1d85.yaml
    - ledger/goals/GOAL-MONO-001/checkpoints/BATCH-1f9bf0.yaml
    - ledger/goals/GOAL-MONO-001/checkpoints/BATCH-8609e2.yaml
    - ledger/goals/GOAL-MONO-001/checkpoints/BATCH-44adf9.yaml
    - coordination/goals/GOAL-MONO-001/batches/BATCH-1f9bf0/dispatch_queue.json (lines 5-113 and 172-205 by grep; notes review_requirement_assessment, archive_kind_and_tool_gap and anticipated_pre_adoption_conditions in full)
    - ledger/questions/RQ-MONO-001.yaml
    - knowledge/open-problems/KN-OPEN-009.md
    - ledger/proposals/IDEA-20260803-ff7415.yaml (lines 1-60; status line)
    - ledger/proposals/IDEA-20260805-a9a95d.yaml (lines 1-50; status line)
    - ledger/proposals/IDEA-20260805-90df50.yaml (lines 1-30; status line)
    - ledger/proposals/IDEA-20260831-d29a71.yaml (lines 236-250, 478-490; status line)
    - ledger/proposals/IDEA-20260904-a1b81b.yaml (lines 14-34, 60-80, 740-756; status line)
    - ledger/hypotheses/H-MONO-663fb4.yaml (lines 1-12, 30-78)
    - agents/coordinator.md (lines 219-247, Closure gate)
    - docs/inventor-protocol.md (section headings; lines 93-200)
    - docs/agent-contract-extended.md (lines 525-545)
    - .claude/agents/validator-breakthrough.md (lines 1-25)
    - "tool output: filtered environment (CLAUDE_EFFORT, CLAUDE_CODE_VERSION, ANTHROPIC_BASE_URL); python3 tools/goal_lanes.py lanes GOAL-MONO-001"
    - "network: https://eprint.iacr.org/2004/031.pdf attempted twice (HTTP 403 Cloudflare challenge; HTML challenge pages sha256 2c13633e6ff463523d030b261fc626a03b77f1ed541dafd9716567b9637da4dd and b615919dd01ea44f2155c55a9e475fabc4abf498f07f7a3ef2339a811b46b6bd; the PDF was NOT obtained); $HTTPS_PROXY/__agentproxy/status"
    - "git metadata only: git log / merge-base on DEC-20260810-2f86db, CORR-20261005-a53ac8, EV-MONO-1ef611, DEC-20260930-8553d4, DEC-20260904-dd58c3, EV-MONO-a0a89c, review-plan-amendment-01.yaml, DEC-20261016-5bdc04, TASK-20261016-9c1bc5"
    - coordination/goals/GOAL-MONO-001/batches/BATCH-1f9bf0/archives/TASK-20261005-c96883/archive-receipt.json (path_sha256 and archive fields by key)
    - coordination/goals/GOAL-MONO-001/batches/BATCH-8609e2/archives/TASK-20261005-41d1ff/archive-receipt.json (archive fields by key)
    - coordination/goals/GOAL-MONO-001/batches/BATCH-8609e2/archives/TASK-20261005-7166be/archive-receipt.json (path_sha256 and archive fields by key)
  not_read:
    - experiments/EXP-MONO-4b50b6/ (blind_from throughout)
    - coordination/goals/GOAL-MONO-001/batches/BATCH-003/ (blind_from throughout)
    - coordination/goals/GOAL-MONO-001/batches/BATCH-450ac7/dispatch_queue.json (the queue mirror of the card; the card file governs)
    - ledger/decisions/DEC-20260930-3a0b7b.yaml; ledger/hypotheses/H-MONO-ebd400.yaml; ledger/evidence/EV-MONO-e9dc3b.yaml; knowledge/findings/KN-FIND-c41ea9.md; experiments/EXP-MONO-0e6e8f/ (not inputs; cited by others only)
    - any producer or composer session transcript
  record_ids_reviewed:
    - EV-MONO-1ef611
    - CORR-20261005-a53ac8
    - DEC-20260810-2f86db
    - DEC-20260930-8553d4
    - DEC-20260930-6f1d85
    - REVIEW-MONO-20260930-40470a-A01
    - REVIEW-MONO-20260930-40470a
    - REVIEW-MONO-20261016-9c1bc5
    - DEC-20261016-5bdc04
    - EV-MONO-a0a89c
    - DEC-20260904-dd58c3
    - DEC-20260802-a51c82
    - GOAL-MONO-001
    - BATCH-1f9bf0
    - BATCH-8609e2
    - BATCH-44adf9
    - RQ-MONO-001
    - KN-OPEN-009
    - TASK-20260930-40470a
    - TASK-20261016-9c1bc5
    - IDEA-20260803-ff7415
    - IDEA-20260805-a9a95d
    - IDEA-20260805-90df50
    - IDEA-20260831-d29a71
    - IDEA-20260904-a1b81b
    - H-MONO-663fb4
  retrieved_sources: []
  recalled_sources:
    - citation: I. Semaev, Summation polynomials and the discrete logarithm problem on elliptic curves, IACR ePrint 2004/031, Theorem 1
      provenance: recalled
      note: >-
        Retrieval was attempted and blocked (HTTP 403 Cloudflare challenge; RC-6: a tooling failure, not
        evidence). For this session the citation is a pointer. Its load-bearing content for m <= 5 (the
        zero-set characterisation of the summation polynomials over the algebraic closure, degenerate points
        included) was verified independently on the reviewer's own S_3, S_4, S_5 (computations.json,
        blind.results.defining_property). The m >= 6 extent of the "every m" statement rests on the published
        theorem, which the predecessor retrieved (sha256 1cab0ae675996cdba6393b1e369a22113fd2e74bcf1223595743dc140631c7d6,
        verified_by TASK-20260930-40470a); that retrieval is cited as a pointer and was not reproduced here.
  zero_runs: true
  runs_launched: 0
  written_paths:
    - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/review_report.md
    - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/computations.json
    - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/review_attestation.yaml
  scope_findings: none (no other file written under or outside write_scope; scratchpad files only)
  commits_made: none (the Coordinator archives; TASK-20261016-548959)
  sessions_that_wrote_the_report: one, this validator-breakthrough session
  attested_at: '2026-10-16'
```
