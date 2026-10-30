# Blind re-derivation: TASK-20261029-3ac467

- Card: `ledger/handoffs/TASK-20261029-3ac467.yaml`, sha256
  `0b7bcb3240ed18748fbdbc6582b816c3715e5358c204475caeee327f17736577`, verified in a
  worktree at `26a72871e7d7559d200024b8d1c4c2a240a947c3`.
- Role: Validator in blind re-derivation mode (`agents/validator.md`, "Blind
  re-derivation tasks"). This is not a validation, so no `validation_report` is issued.
  Joints owned: J1, J2, J3, J4, J5. Verdicts are per joint, not on any claim.
- Premises used, all whitelisted:
  - KN-FIND-4f0d84: the root structure of the fibre over the factor-base locus, over F_p.
  - KN-FIND-bdcd60 item (3): the Frobenius rule.
  - KN-FIND-007: read. Its statement coincides with the Q1 multiset identity, which is
    re-derived below rather than taken from it.
- Nothing in `blind_from` was read (see `review_attestation.yaml`).
- Corroboration (RD-3) is in `computations.json`, cited below by step id in brackets.
  - Pure Python 3.11, standard library only. The field, polynomial, resultant, group-law
    and Semaev code (`rd_lib.py`) was written for this task.
  - S_3 is checked against the group law. S_4 and S_5 fibres are built by Sylvester
    resultants with formal degrees; S_4 is also computed by the closed quadratic
    resultant, and the two agree on every tested tuple [t0_selftest].
  - Fields used: F_p (p ≤ 101), F_{p^2} (p ≤ 31) and F_{p^3} (p ≤ 7). Zero experiment runs.

## 0. Readings adopted where the card leaves room (RD-2)

- **RD-a, targets.** R is uniform over all N elements of G unless a target set is stated.
- **RD-b, fibre.** The fibre is S_{n+1}(x_1..x_n, T), built by Semaev's resultant
  recursion with formal (generic) degrees. Specialising the Sylvester determinant then
  equals specialising the generic polynomial. "Splits completely over F_Q" means the
  nonzero polynomial is a product of linear factors over F_Q; lower degree and repeated
  roots are allowed. No fibre was the zero polynomial in any computation.
- **RD-c, root hits.** For a target R ≠ O, the root hits are the sum over ordered x-tuples
  ξ ∈ X^n of the multiplicity of x(R) as a root of S_{n+1}(ξ, T). By Q2 this is T_S(R).
  - Primary all-target mean: over the affine x-classes, because the proxy model spreads
    roots over x-classes.
  - Secondary all-target mean: over R ∈ G, with R = O contributing 0, since x(O) is not
    an affine root.
- **RD-d, Q2 multisets.** "No two elements (equal or not) that sum to O" means no two
  distinct positions of the multiset sum to O. So an element of order 2 occurs at most
  once, and P and −P never both occur.
- **RD-e, Q4 premise.** The premise is applied over F_Q. I also re-derive it from
  Frob_Q(x, y) = (x, χ(f(x)) y), because degenerate fibres, which the premise excludes,
  enter the error term.
- **RD-f, Q5.** n = c log2 q is treated as a real number, with n! = Γ(n+1). Rounding n
  to an integer changes no order stated below.

## Q1 (J1): conservation and the T_A / T_M ratio

**Determination.** Let G be finite abelian of order N and D ⊂ G \ {O} with |D| = B. The
sums below hold for any D; symmetry is not needed.

1. Every ordered tuple in D^n has exactly one sum, so `Σ_R T_A(R) = B^n`.
2. Every size-n multiset has exactly one sum, so `Σ_R T_M(R) = C(B+n-1, n)`.
3. Therefore `E[T_A] = B^n / N` and `E[T_M] = C(B+n-1, n) / N`.
4. The ratio of the all-target means is

   `E[T_A]/E[T_M] = B^n / C(B+n-1, n) = n! · Π_{i=1}^{n-1} B/(B+i)`.

5. Two-sided bound. Use `e^{-i/B} ≤ (1 + i/B)^{-1} ≤ 1`:

   `n! · exp(-n(n-1)/(2B)) ≤ E[T_A]/E[T_M] ≤ n!`.

   - Equality on the right holds iff n = 1.
   - An alternative lower bound is `n! (1 + (n-1)/B)^{-(n-1)}`. It is the stronger one
     only when (n−1)/B ≳ 2.5.
   - The ratio increases to n! as B → ∞, with
     `ratio = n! (1 − n(n−1)/(2B) + O(n^4/B^2))`.
6. T_A in terms of multisets. A multiset M with multiplicities m_P(M) has exactly
   `n!/Π_P m_P(M)!` distinct orderings, all with sum ΣM. So

   `T_A(R) = Σ_{M : ΣM = R} n! / Π_{P∈D} m_P(M)!`.

   - It follows that `T_M(R) ≤ T_A(R) ≤ n!·T_M(R)`.
   - The upper equality holds iff every multiset summing to R has n distinct members.
7. Specialisation to B = q, N = q^n:

   `E[T_M] = C(q+n-1, n) / q^n = (1/n!) Π_{i=0}^{n-1} (1 + i/q)`.

   - This lies in `[1/n!, e^{n(n-1)/(2q)}/n!]`, and its limit as q → ∞ at fixed n is
     **1/n!**.
   - Also `E[T_A] = q^n/q^n = 1` exactly.

**Corroboration** [q1_conservation]. 75 cases checked: 60 on abstract groups and 15 on
elliptic-curve factor bases. All checks pass (`all_checks_pass: true`).

- Abstract groups: Z/97, Z/2×Z/48, Z/2×Z/2×Z/24, Z/3×Z/3×Z/11 and Z/4×Z/30, with random
  symmetric D, t2 ≤ 3 and n = 1..4.
- Elliptic-curve factor bases: D = {P : x(P) ∈ F_p} in E(F_{7^2}), E(F_{11^2}),
  E(F_{13^2}), E(F_{5^3}) and E(F_{7^3}), with n = 1..3.
- Checks:
  - both sums;
  - the ratio, exact to 1e-9;
  - the two-sided bound;
  - `T_A(R) = Σ multinomials` at every R.
- In the specialisation table, n!·E[T_M] at q = 10^6 equals 1.000001, 1.000003,
  1.000006 and 1.000010 for n = 2..5. Each lies inside `[1, e^{n(n-1)/(2q)}]`.

**Joint J1: holds.**

## Q2 (J2): T_S, T_M − T_X, the n = 2 counts at O, and cancellation-free multisets

**Determination.** Set t(P) = #{i : P_i ∈ G[2]} for P ∈ D^n.

### T_S(R) for 2R ≠ O

1. The map φ(ξ, ε) = (ε_1 l(ξ_1), ..., ε_n l(ξ_n)) from X^n × {±1}^n onto D^n is
   surjective. Its fibre over P has size `2^{t(P)}`: the sign does not matter on a
   2-torsion lift, and gives the two distinct points of the x-class otherwise.
2. A class {ε, −ε} has members with sums s and −s.
3. When R ≠ −R, the classes with s ∈ {R, −R} correspond bijectively to the sign vectors
   with sum exactly R. Hence

   **`T_S(R) = Σ_{P ∈ D^n, ΣP = R} 2^{t(P)} = Σ_{j=0}^{n} 2^j · T_A^{(j)}(R)`**

   where T_A^{(j)}(R) counts the ordered tuples with sum R and exactly j entries in G[2].
4. Consequences:
   - `T_A(R) ≤ T_S(R) ≤ 2^n T_A(R)`;
   - `T_S(R) = T_A(R)` whenever t2 = 0;
   - T_S does not depend on the choice of lifts.
5. Extra case, R ∈ G[2]: `T_S(R) = ½ Σ_{ΣP = R} 2^{t(P)}`.

### T_M(R) − T_X(R)

For a size-n multiset Ξ of X, define:

- a(Ξ, R) = the number of D-multisets M with x(M) = Ξ and ΣM = R;
- μ(Ξ, R) = the number of sign classes whose signed lift sum lies in {R, −R}.

Then:

1. `T_M(R) = Σ_Ξ a(Ξ,R)`.
2. Negation M ↦ −M preserves x(M) and maps R to −R, so a(Ξ, −R) = a(Ξ, R).
3. Ξ is counted in T_X(R) iff a(Ξ, R) ≥ 1. Hence

   **`T_M(R) − T_X(R) = Σ_Ξ (a(Ξ,R) − 1)_+`**.

4. Root multiplicity. The fibre factors as `c·Π_{classes, s≠O}(T − x(s))` with c ≠ 0.
   So μ(Ξ, R) is exactly the multiplicity of x(R) in S_{n+1}(Ξ, T).
   - This is KN-FIND-4f0d84, carried from F_p to F_Q and corroborated below.
5. Each M over Ξ with sum R arises from w(M) sign vectors, where k_x is the multiplicity
   of x in Ξ and j_x is the number of copies of +l(x) in M:

   `w(M) = Π_{x not 2-torsion} C(k_x, j_x) · Π_{x 2-torsion} 2^{k_x}`

6. So `μ(Ξ,R) = Σ_M w(M) ≥ a(Ξ,R)`, with **equality when Ξ consists of n distinct
   x-values none of 2-torsion** (a simple Ξ).
7. Therefore

   `T_M(R) − T_X(R) = Σ_{Ξ simple} (mult_{x(R)} S_{n+1}(Ξ,T) − 1)_+  +  Σ_{Ξ non-simple} (a(Ξ,R) − 1)_+  ≤  Σ_Ξ (mult_{x(R)} − 1)_+`.

   On simple multisets, the excess of T_M over T_X equals the excess of the root
   multiplicity of x(R) over 1.
8. Corollary at n = 2 with 2R ≠ O: a(Ξ, R) ≤ 1, so T_M(R) = T_X(R).

### n = 2 at O

1. `T_A(O) = B`: each P_1 ∈ D forces P_2 = −P_1, which lies in D because D = −D.
2. `T_M(O) = (B − t2)/2 + t2 = (B + t2)/2 = |X|`. The multisets are one {P, −P} per
   non-2-torsion pair, plus {T, T} for each 2-torsion T.

### Multisets with no two members summing to O

1. Each of the (B − t2)/2 non-2-torsion pairs {P, −P} contributes
   `1 + 2z/(1−z) = (1+z)/(1−z)`: use neither, or j ≥ 1 copies of exactly one of them.
2. Each 2-torsion element contributes `1 + z`.
3. The count is therefore

   **`[z^n] (1+z)^{t2} ((1+z)/(1−z))^{(B−t2)/2} = [z^n] (1+z)^{(B+t2)/2} (1−z)^{−(B−t2)/2}`**
   `= Σ_j C(|X|, j) · C((B−t2)/2 + n − j − 1, n − j)`.

**Corroboration** [q2_counts]. 43 cases, all passing (`all_checks_pass: true`).

- Abstract groups: 31 cases on Z/41, Z/2×Z/30, Z/2×Z/2×Z/12 and Z/4×Z/12, with
  t2 ∈ {0, 3, 7} and n = 1..4.
- Elliptic curves: 12 cases on E(F_{7^2}), E(F_{11^2}) and E(F_{5^3}), plus one curve
  over F_{7^2} with all three roots of f in F_7 (t2 = 3), with n = 1..3.
- Checks at every target:
  - the T_S formula, with 0 failures, including the ½ factor at 2-torsion targets;
  - `T_M = Σ_Ξ a`, and `T_M − T_X = Σ (a−1)_+`;
  - a ≤ μ, with a = μ on every simple Ξ;
  - the n = 2 counts at O;
  - the generating-function count, which matches brute force in every case (for example
    515 at B = 15, t2 = 7, n = 3).
- On the elliptic-curve cases, the multiplicity of x(R) as a root of the resultant-built
  S_3 and S_4 fibre equals μ(Ξ, R) in all **10,011** checks.
- Non-simple multisets do produce a < μ. The total excess Σ(a−1)_+ falls strictly below
  Σ(μ−1)_+ on, for example, 56 targets of Z/2×Z/30 with B = 11, t2 = 3, n = 3. The
  relation off simple multisets is therefore an inequality, not an equality.

**Joint J2: holds.**

## Q3 (J3): coverage bounds

**Determination.**

1. Upper bound. For integer T ≥ 0, `1{T ≥ 1} ≤ min(1, T)` pointwise, so
   **`c ≤ min(1, μ_M)`**.
   - This is the best bound in terms of μ_M alone. It is attained by T ∈ {0, 1} when
     μ ≤ 1, and by T ≥ 1 everywhere when μ ≥ 1.
   - Among actual bases it is attained by a non-symmetric B_n-type base. One was found
     in Z/31 at n = 2.
   - Equality c = μ_M ≤ 1 holds iff T_M(R) ∈ {0, 1} at every target.
2. Lower bound. By Cauchy–Schwarz, `μ_M = E[T·1{T≥1}] ≤ sqrt(E[T²]·c)`, so
   **`c ≥ μ_M² / E[T_M²]`**.
   - It is tight for two-point laws on {0, E[T²]/μ}.
   - It always dominates Chebyshev's `1 − Var/μ²`.
3. **No base of size B, symmetric or not, can have coverage above min(1, μ_M).** The
   inequality is pointwise.
4. Symmetric bases with n ≥ 2 and |X| ≥ 2 obey a strictly lower ceiling.
   - Removing cancelling pairs maps every size-n multiset to a cancellation-free one of
     size n − 2k with the same sum. So the number of distinct sums is at most
     `Σ_k F(n−2k) = [z^n] (1+z)^{|X|−1}(1−z)^{−(B−t2)/2−1} =: N·μ_sym`, where F is the
     Q2 count.
   - Coefficientwise `(1+z) ≤ 1/(1−z)`, so `μ_sym < μ_M`, with `μ_sym/μ_M = 1 − O(n²/B)`
     at fixed n.
   - Hence `c ≤ min(1, μ_sym)`, and **a symmetric base never attains c = μ_M when
     μ_M ≤ 1**. Two cancelling pairs {P, −P} and {Q, −Q} added to any size-(n−2)
     multiset give the same sum. At n = 2 this is T_M(O) = |X|.
5. Values of `log2(μ/(1 − e^{−μ}))` at μ = 1/n!:

| n | μ = 1/n! | μ/(1−e^{−μ}) | log2, three decimals |
|---|---|---|---|
| 2 | 0.5 | 1.270747 | **0.346** |
| 3 | 0.166667 | 1.085647 | **0.119** |
| 4 | 0.041667 | 1.020978 | **0.030** |
| 5 | 0.008333 | 1.004172 | **0.006** |

**Corroboration** [q3_coverage]. All bound checks pass (`all_bound_checks_pass: true`).

- Exhaustive sweeps over every symmetric base of a given size: 7 sweeps with 91 to 8,568
  bases each, in Z/31, Z/37, Z/61, Z/2×Z/16 and Z/2×Z/2×Z/8, at n = 2, 3.
  - 0 bases lie above min(1, μ_M).
  - 0 bases attain μ_M.
  - 0 bases violate the lower bound or the symmetric ceiling.
  - In 5 of 7 sweeps the maximum coverage equals min(1, μ_sym) exactly. For example, in
    Z/61 at n = 3 and B = 6, max c = 0.7213 = μ_sym, while μ_M = 0.9180.
- Non-symmetric control: a base attaining c = μ_M exactly was found in Z/31.
  - At n = 2, B = 6: c = μ = 0.6774.
  - At n = 2, B = 5: c = μ = 0.4839.
  - At n = 3, B = 5, none was found in 20,000 random draws in Z/61. This is a search
    limit only.
- Matched comparison in elliptic-curve groups: the factor base, 40 seeded random
  symmetric bases, and a greedy low-collision symmetric base of the same B.
  - In every group, coverage stays ≤ min(1, μ_sym) ≤ min(1, μ_M).
  - The greedy base reaches μ_sym exactly in E(F_{31^2}) at n = 2: c = 0.2539, versus
    0.2274 mean random and μ_M = 0.2644.
- Random symmetric bases in a large cyclic group follow the Poisson value 1 − e^{−μ}
  only when B is large.
  - At N = 4001, n = 2, B = 62: c = 0.3893 versus 0.3862.
  - At small B they fall below it, because of forced cancellations. At N = 2003, n = 3,
    B = 10: c = 0.0860 versus 0.1040.

**Joint J3: holds.**

## Q4 (J4): complete splitting of the fibre

**Determination.**

Setup. Write N = |E(F_Q)| = Q + 1 − a and let t ∈ {0, 1, 3} be the number of roots of f
in F_Q. For x ∈ F_Q, set p_+ = P(χ(f(x)) = +1) = (N − 1 − t)/(2Q), p_0 = t/Q and
p_− = 1 − p_+ − p_0.

### Frobenius action

- For P_i = (x_i, y_i) with y_i² = f(x_i) ∈ F_Q, we have `Frob_Q(P_i) = χ(f(x_i))·P_i`.
  A 2-torsion P_i (f(x_i) = 0) is rational and equals −P_i.
- The roots of the fibre, with multiplicity, are x(Σ ε_i P_i) over the sign classes with
  nonzero sum.
- This reproduces the premise on nondegenerate fibres, and extends to every fibre as
  follows.

### All nonzero χ values equal

- If every nonzero χ(f(x_i)) equals σ, then `Frob(Σ ε_i P_i) = σ·Σ ε_i P_i`.
- Every root is then fixed, so the fibre **splits completely**. This includes degenerate
  fibres: repeated roots, degree drops, and 2-torsion entries.
- The exact probability of this event is `M_n = (p_+ + p_0)^n + (p_− + p_0)^n − p_0^n`.

### Mixed χ values

- Write the class sum as α + γ, where α collects the χ ≥ 0 coordinates
  (Frob α = α) and γ the χ = −1 coordinates (Frob γ = −γ).
- The root x(α + γ) is rational iff 2α = O or 2γ = O. The case α + γ = O forces 2α = O.
- Requiring this for every class forces one side, of size at least 2, to have
  all signed sums in E(F_Q)[2]. Flipping one sign then gives 2P_i ∈ E(F_Q)[2].
- So every coordinate of that side lies in `W' = x(E[4] \ {O}) ∩ F_Q`, with |W'| ≤ 9.
- Hence the probability δ that a mixed tuple splits satisfies
  `0 ≤ δ ≤ P(≥ 2 coordinates in W') ≤ C(n,2)·(|W'|/Q)²`.
- **δ = 0 when t = 0**, because no rational 2-torsion means no side can qualify.

### Generic tuple: the result

1. **`P_split(generic) = 2^{1−n}(1 + η) − (t/Q)^n + δ`**, where
   `η = ½[(1 + (t−a)/Q)^n + (1 + (t+a)/Q)^n] − 1`.
2. Here η is exact, and `0 ≤ η ≤ e^{3n/Q} cosh(2n/√Q) − 1`, using Hasse's bound
   |a| ≤ 2√Q. That is `η = nt/Q + O(n²/Q)` for n = O(√Q).
3. **Leading value 2^{1−n}.** The error is
   **`O(n² 2^{−n}/Q) + O(n²/Q²)`**, a relative error of `O(n²/Q) + O(n² 2^n/Q²)`.
4. In the regime Q = q^n this is `O(n²/q^n)` relative.
5. At n = 1 the formula gives exactly 1.

### On the locus

- For tuples x_i = x(P_i) with P_i ∈ E(F_Q), every χ is 0 or +1.
- So the probability is **exactly 1**, including all degenerate tuples. This is the
  statement of KN-FIND-4f0d84, carried to F_Q.

### Exact root hits against the proxy model

1. Exact: every ordered tuple ξ ∈ X^n splits. The total of root multiplicities over the
   affine x-classes is `Σ_ξ deg S_{n+1}(ξ,T) = 2^{n−1}|X|^n − Z_0`, where
   `Z_0 = #{(ξ,[ε]) : sum = O} = T_S(O)`.
2. Proxy: the total is `|X|^n · P_split(generic) · 2^{n−1}`. The proxy spreads it over
   the same K affine x-classes.
3. **Ratio of all-target means = `(1 − ζ)/P_split(generic)`**, where
   `ζ = T_S(O)/(2^{n−1}|X|^n) ∈ [0, 1/|X|]`.
   - At n = 2, `ζ = (|X| + t2)/(2|X|²)`.
   - **Leading value 2^{n−1}**, with relative error `O(1/|X|) + O(n²/Q) + O(n²2^n/Q²)`.
4. The per-R version uses `Σ_{R≠O} hits = 2^n|X|^n − 2Z_0 − Z_t` against
   `(N−1)|X|^n P 2^{n−1}/K`, where Z_t counts the class sums in G[2] \ {O}. It has the
   same leading value.

**Corroboration** [q4_split], [q4b_mixed].

Generic tuples (Part A), selected rows. All fibres were built by resultants; every row
has 0 zero fibres and 0 Frobenius-rule failures on nondegenerate fibres. "fraction" is
the split fraction; "exact M_n" is M_n from the formula. In the last column, w is the
number of elements of W' for that curve, from [q4b_mixed]; "–" means δ = 0 needs no
bound or was not computed.

| field | t | n | tuples | fraction | 2^{1−n} | exact M_n | δ measured | C(n,2)(w/Q)² |
|---|---|---|---|---|---|---|---|---|
| F_101 | 0 | 2 | 10,201 exh. | 0.511028 | 0.5 | 0.511028 | 0 | – |
| F_{23^2} | 0 | 2 | 279,841 exh. | 0.501303 | 0.5 | 0.501303 | 0 | – |
| F_31 | 1 | 3 | 29,791 exh. | 0.278171 | 0.25 | 0.278171 | 0 | 0.0031 |
| F_{7^2} | 1 | 3 | 117,649 exh. | 0.278311 | 0.25 | 0.277087 | 0.001224 | 0.0112 |
| F_{5^3} | 1 | 3 | 1,953,125 exh. | 0.257980 | 0.25 | 0.257789 | 0.000190 | 0.0017 |
| F_{5^3} | 3 | 3 | 1,953,125 exh. | 0.284666 | 0.25 | 0.284347 | 0.000319 | 0.0048 |
| F_{7^3} | 0 | 3 | 40,000 sample | 0.2537 | 0.25 | 0.250771 | 0 | – |
| F_13 | 1 | 4 | 28,561 exh. | 0.168096 | 0.125 | 0.168096 | 0 | 0.0355 |
| F_{5^2} | 3 | 4 | 390,625 exh. | 0.215780 | 0.125 | 0.202509 | 0.013271 | 0.24 |
| F_61 | 1 | 4 | 8,000 sample | 0.1405 | 0.125 | 0.136734 | 0 | – |

- Across all 22 Part A rows:
  - every tuple whose nonzero χ values are all equal splits (0 exceptions);
  - every exhaustive row with t = 0 has δ = 0;
  - the split fraction equals the exact M_n plus the measured δ.
- [q4b_mixed], 10 exhaustive runs:
  - every mixed split tuple is degenerate (0 nondegenerate ones);
  - every mixed split tuple has at least two coordinates in W' (0 exceptions);
  - δ ≤ P(≥2 coordinates in W') ≤ C(n,2)(|W'|/Q)² in every run;
  - the ψ = x(2P) formula has 0 failures;
  - every rational point with x in W' has order dividing 4.
- Locus (Part B): all of the following split, and their root multisets equal
  {x(Σε_iP_i)} with multiplicity.
  - Exhaustive over E(F_Q)^n at F_13 (n = 2, 3, on two curves) and F_{7^2} (n = 2).
  - Seeded samples with forced degeneracies at F_31, F_{7^2} and F_{5^3} (n = 3, 4),
    and on a curve over F_{7^2} with rational 2-torsion.
  - Totals over 11 rows: 18,358 of 18,358 tuples split, 18,358 of 18,358 root multisets
    correct.
- Ratio (Part C): on 9 factor bases in E(F_{p^2}) and E(F_{p^3}), the measured
  exact/proxy ratio per x-class equals `(1 − ζ)/P_split` to machine precision.
  - Examples: 1.9236 at F_{23^2}, n = 2, with |X| = 14 and ζ = 0.0357; 3.8763 at
    F_{5^3}, n = 3, with ζ = 0.
  - With the leading P = 2^{1−n}, the ratio is 2^{n−1}(1 − ζ).
  - Where small |X| or small Q moves it away from 2^{n−1}, the formula accounts for the
    whole deviation.

**Joint J4: holds.**

## Q5 (J5): orders as q grows with n = c log2 q

**Determination.**

1. Stirling gives ln n! = n ln n − n + O(log n). So
   **`log_q(n!) = (c/ln 2)(ln ln q + ln(c/ln 2) − 1) + O(ln ln q / ln q) = Θ(log log q)`**.
   It is unbounded.
2. **`log_q(2^{n−1}) = c − ln 2/ln q → c = Θ(1)`**.
3. Multiplying the rate 1/n! by 2^{n−1} changes log_q(1/rate) by −c + o(1) in absolute
   terms. The relative change is
   **`−(n−1) ln 2 / ln(n!) = −ln 2/(ln n − 1)·(1 + o(1)) = −Θ(1/log log q) → 0`**.
4. 1/rate = n! = q^{Θ(log log q)} = exp((c/ln 2 + o(1)) ln q ln ln q). The factor
   2^{n−1} = q^c/2 is polynomial in q.
5. **The change does not alter the exponent class of 1/rate.** The class stays
   q^{Θ(log log q)}, and its leading constant c/ln 2 is unchanged. Only a polynomial
   factor q^{c} is removed.

**Corroboration** [q5_asymptotics], for c ∈ {0.5, 1, 2} and log2 q from 10 to 10^6:

- log_q(n!) tracks the leading form: 8.8843 versus 8.8792 at c = 1, log2 q = 1280.
- log_q(2^{n−1}) → c: 0.9992 at c = 1, log2 q = 1280.
- The relative change tends to 0 like −ln2/(ln n − 1): −0.1125 versus −0.1126 at
  log2 q = 1280, and −0.0541 at 10^6.
- log_q(n!)/ln ln q climbs slowly toward c/ln 2: 1.3747 versus 1.4427 at c = 1,
  log2 q = 10^6.

**Joint J5: holds.**

## Objects O1 to O4

**O1, a structured symmetric base matched in size to a random symmetric base (Q3).**

- Both have the same μ_M = C(B+n−1, n)/N (Q1), and both are capped by min(1, μ_M).
- Neither can exceed it.
- The structured base can exceed the random one only by coverage, never by mean. The gain
  is at most min(1, μ_M)/c_random, and per realisation at most E_random[T_M²]/μ_M when
  μ_M ≤ 1.
- If c_random is read as the Poisson value 1 − e^{−μ}, the gain cap at μ = 1/n! is
  2^{0.346}, 2^{0.119}, 2^{0.030} and 2^{0.006} for n = 2..5.
- Being symmetric, the structured base also obeys the strictly lower ceiling
  min(1, μ_sym) at n ≥ 2. It cannot be a Sidon-type base in the multiset sense:
  T_M(R) ≥ 2 on every sum of a size-(n−2) multiset. So a base attaining c = μ_M, as in
  KN-FIND-007's Sidon example, cannot be symmetric.
- Measured: a greedy symmetric base beat the mean of 40 matched random symmetric bases by
  1.116 in E(F_{31^2}) at n = 2 and by 1.243 in E(F_{23^2}) at n = 2. In both cases it
  stayed below its ceiling.
- Random symmetric bases at small B fall below 1 − e^{−μ}. There the observed
  min(1,μ)/c_random exceeds μ/(1−e^{−μ}): for example 1.277 versus 1.056 at N = 2003,
  n = 3, B = 10. The Poisson reading is a large-B model, not an exact value.

**O2, tuples on the factor-base locus, x_i = x(P_i) with P_i ∈ E(F_Q) (Q4).**

- The fibre splits completely with probability 1, against 2^{1−n}(1 + O(n²/Q)) + O(n²/Q²)
  for a generic tuple.
- On the locus, complete splitting carries no information. The proxy model, which treats
  locus fibres as generic, undercounts the exact all-target mean of root hits by the
  factor (1 − ζ)/P_split. Its leading value is 2^{n−1}.

**O3, a non-symmetric base D' holding one point from each ± pair (Q2).**

- D' = l(X) has |D'| = |X| = (B+t2)/2.
- Q1 conservation holds for it: Σ T_A' = |X|^n and Σ T_M' = C(|X|+n−1, n).
- T_S depends only on X. It therefore equals the symmetric closure D's value,
  Σ_{ΣP=R} 2^{t(P)}, and is unchanged by dropping half the base. D' itself sees only the
  all-plus class:
  - T_A'(R) + T_A'(−R) ≤ T_S(R);
  - Σ_R T_S(R) = 2^n|X|^n − Z_0 − Z_t, about 2^n·Σ_R T_A'(R).
- At n = 2: T_A'(O) = T_M'(O) = t2, against B and |X| for D.
- No-cancellation count: [z^n] (1+z)^{t2} (1−z)^{−(B−t2)/2}.
- The identity T_M − T_X = Σ(a − 1)_+ uses D = −D and does not transfer. For D' the
  order reverses: T_M'(R) ≤ T_X(R) ≤ T_M(R).
- Nothing forces collisions on D', so c = μ' is attainable (non-symmetric control in
  Q3).
- Corroboration: all O3 checks in [q2_counts] pass. Measured Σ T_S / Σ T_A' is 2.0, 3.8,
  7.93 and 15.72 for n = 1..4 in Z/41 with B = 10. The identity predicts 2^n minus a
  small correction. At n = 2, where Z_0 = |X| = 5 and Z_t = 0, it gives exactly 3.8.
  The correction at n = 3, 4 was not separately recomputed.

**O4, n = 1.**

- Q1: T_A = T_M = 1_D, both sums equal B, and the ratio is 1 = 1!. The bounds collapse to
  1 = 1.
  - The specialisation B = q, N = q is infeasible, since O ∉ D forces B ≤ N − 1.
  - Formally C(q,1)/q = 1 = 1/1!, and the limit is 1.
- Q2:
  - T_S(R) = 1_D(R) for 2R ≠ O, as the formula gives.
  - S_2(ξ, T) = ξ − T is linear, so μ ≤ 1 and T_M − T_X = 0.
  - The n = 2 statements do not apply.
  - The generating function gives B, since every singleton is cancellation-free.
- Q4:
  - The fibre has degree 1 = 2^0 and always splits, so P_split = 1 = 2^{1−1} exactly.
    The formula gives (p_+ + p_0) + (p_− + p_0) − p_0 = 1, with δ = 0.
  - On the locus the probability is 1.
  - The ratio is 1, because Z_0 = 0 when O ∉ D.
  - The Frobenius-rule premise (m ≥ 3) does not cover m = 2, and is not needed there.
- Corroboration: the n = 1 rows of [q1_conservation] and [q2_counts] pass.

## Verdict per owned joint (RD-5)

| joint | question | verdict |
|---|---|---|
| J1 | Q1 | holds |
| J2 | Q2 | holds |
| J3 | Q3 | holds |
| J4 | Q4 | holds |
| J5 | Q5 | holds |

"holds" means my own determination is complete under the readings in section 0, is
self-consistent, and passed every corroboration listed. It is not a verdict on any claim,
and no other derivation was seen.

## Limitations and observations

- Toy scale only.
  - Fields up to Q = 961 for counting and Q = 1,953,125 tuples for splitting.
  - n ≤ 4 computed. n = 5 enters only through the Q3 numbers and the Q5 asymptotics.
  - The error terms in Q4 are derived bounds. They were corroborated only at small Q.
- The factorisation of the fibre over F_Q for P_i ∈ E(F_Q) extends KN-FIND-4f0d84,
  which is stated over F_p. It was corroborated over F_p, F_{p^2} and F_{p^3}
  (Part B, and 10,011 root-multiplicity checks in Q2).
- Semaev's theorem was not read. Its defining property is used only as the card states
  it, and was checked numerically for S_3, S_4 and S_5.
- Observation, not asked for. When E has a, b ∈ F_q, the base size is not q.
  - |D| = 2q − t_q when n is even, because every element of F_q is a square in F_{q^2}.
  - |D| = |E(F_q)| − 1 when n is odd, because χ_Q restricted to F_q is χ_q.
  - Verified with 0 exceptions on 42 curve/field pairs [q4_split Part D].
  - For a, b generic in F_Q, B fluctuates around q. Measured B was 22 at q = 31.
  - So B = q in Q1 is the card's specialisation, not an identity.
- Every random choice is seeded (recorded in `computations.json`). Sampled rows are
  labelled as samples.
- The model identity is self-reported and not probe-verified (see the attestation).
