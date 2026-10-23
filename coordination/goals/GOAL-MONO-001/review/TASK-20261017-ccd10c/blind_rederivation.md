# Blind re-derivation report — TASK-20261017-ccd10c (joint RB)

Goal GOAL-MONO-001, batch BATCH-dce635, round REVIEW-MONO-20261017-8aff64.
Role: validator-breakthrough (policy review-breakthrough, effort max), fresh
independent session. Zero runs. Everything below was derived from the card's
statement and parameters alone; every script, command, seed and raw output is
embedded as text in `computations.json` beside this file.

## 0. Provenance and discipline

- Card sha256 given in the launch prompt:
  `e19e3601fc79a2bfa19156ded500eeb756a7749b7b3848841e9a8b78362edd7c`.
  Card sha256 computed by this session (`sha256sum`): identical.
- **No `blind_from` path was opened.** Paths read, in order:
  1. `ledger/handoffs/TASK-20261017-ccd10c.yaml`
  2. `AGENTS.md`
  3. `agents/validator.md`
  4. `.claude/agents/validator.md` — NOT on the card's whitelist (the
     whitelist names `.claude/agents/validator-breakthrough.md`); opened
     because the launch binding's text directs the reader to it. Not a
     `blind_from` path; contains nothing about the quantities. Reported per
     RB-9, not hidden.
  5. `docs/agent-runtime-core.md`
  6. `docs/inventor-protocol.md` — NOT on the whitelist; opened for the same
     reason (the binding text names its §6). Not a `blind_from` path;
     contains nothing about the quantities. Reported per RB-9.
  7. `.claude/agents/validator-breakthrough.md`
  8. `templates/research-records.md`, lines 764–853 only ("Review
     attestation" section, located with `rg`).
  9. `docs/claims-and-verification.md`

  Nothing else in the repository was read. No `kb/` retrieval, no web, no
  repository code was imported or executed; `git rev-parse HEAD`,
  `git branch --show-current` and `git status --short` (empty output) were
  run once at the start to record the snapshot (`467b24d0a1`).
- Tools: CPython 3.11.15 (`-I`), numpy 2.4.6, sympy 1.14.0. All arithmetic
  (F_p, F_{p^2}, curve group law, univariate polynomials, distinct-degree
  factorisation, multivariate evaluation, Sylvester determinants,
  interpolation) is in `semaev_lib.py`, written in this session. sympy is used
  for the symbolic S_3/S_4, for rewriting symmetric coefficients in elementary
  symmetric functions, for permutation groups, and as an independent
  cross-check of my factoring code. No GAP/Magma/PARI/Sage is present.
- Public knowledge recalled (pointers only, never support): the resultant
  recursion and degree 2^{m-2} of Semaev polynomials; the standard facts on
  Kummer extensions, Galois theory of symmetric functions, affine permutation
  groups, and the Chebotarev density theorem for function fields. Every fact
  actually used is re-derived or computed below.
- Scale: toy only (50 < p < 2000). Nothing here is an ECDLP result.

## 1. Setting, notation and three lemmas

E: y² = f(x) = x³ + ax + b over F_p, p > 3, 4a³ + 27b² ≠ 0; K = algebraic
closure. n := m − 1. For indeterminates x_1..x_n write
L = K(x_1..x_n), L_0 = K(e_1..e_n) (e_j the elementary symmetric functions),
y_i := √f(x_i), N := L(y_1..y_n), P_i := (x_i, y_i) ∈ E(N).
F(T) := S_m(x_1..x_n, T).

**Lemma A (root set).** For any x_1..x_n ∈ K with f(x_i) ≠ 0, fix P_i with
x(P_i) = x_i. The zero set of F(T) in K is
{ r_ε := x(Σ ε_i P_i) : ε ∈ {±1}^n } minus ∞, and r_ε = r_{−ε}.
*Proof.* By the defining property, F(t) = 0 iff there are Q_1..Q_n, Q_m with
x(Q_i) = x_i, x(Q_m) = t, ΣQ_i + Q_m = O. The points with x-coordinate x_i are
±P_i, so Q_m = −Σ ε_i P_i and t = x(Σ ε_i P_i) (x is even). ∎

**Lemma B (degree).** deg_T S_m = 2^{m−2}, and deg_{x_i} S_m = 2^{m−2} for all
i. *Proof.* S_3 has degree 2 in each variable (explicit, §2). Res_X(A, B) is
homogeneous of degree deg_X B in the coefficients of A and deg_X A in those of
B; by induction on the recursion S_m = Res_X(S_{m−k}, S_{k+2}) each variable
has degree 2^{m−k−2}·2^{k} = 2^{m−2}. Equality (not just ≤) holds because the
specialisations in §3 exhibit 2^{m−2} distinct roots. ∎
(Verified: my S_3, S_4, S_5 have degree exactly 2, 4, 8 in every variable on
all eight curves.)

**Lemma C (generic independence).** For independent indeterminates
x_1..x_n, the points P_1..P_n ∈ E(N) are Z-linearly independent.
*Proof.* If Σ k_i P_i = O with k_1 ≠ 0, then x(k_1 P_1), a non-constant
rational function of x_1 alone (division polynomials), lies in
K(x_2..x_n, y_2..y_n), which is algebraically independent of x_1; so it is
constant, contradiction. ∎

**Corollary.** For generic x, the 2^{n−1} values r_ε (ε modulo global sign)
are finite and pairwise distinct (r_ε = r_δ ⇒ Σ ε_i P_i = ±Σ δ_i P_i ⇒
Σ (ε_i ∓ δ_i) P_i = O ⇒ ε = ±δ by Lemma C), hence by Lemmas A–B
F = lc(x) · Π_{ε mod ±} (T − r_ε) with lc ≠ 0 and F squarefree.
(Verified at 4,800 random specialisations: §6, check C, including 161
degenerate cases where the identity still holds with multiplicity.)

## 2. Own construction of S_3, S_4, S_5 (card parameters, step 3)

*S_3.* P_1 + P_2 + P_3 = O ⇔ x_3 = x(P_1 + P_2) = λ² − x_1 − x_2,
λ = (y_2 − y_1)/(x_2 − x_1). Hence (x_1 − x_2)²(x_1 + x_2 + x_3) =
f(x_1) + f(x_2) − 2y_1y_2, so with
B := (x_1 − x_2)²(x_1 + x_2 + x_3) − f(x_1) − f(x_2) = −2y_1y_2 we get
B² − 4f(x_1)f(x_2) = 0. sympy shows B² − 4f(x_1)f(x_2) is divisible by
(x_1 − x_2)² with zero remainder; the quotient is

S_3 = x_1²x_2² + x_1²x_3² + x_2²x_3² − 2x_1²x_2x_3 − 2x_1x_2²x_3 − 2x_1x_2x_3²
      − 2a(x_1x_2 + x_1x_3 + x_2x_3) − 4b(x_1 + x_2 + x_3) + a²,

symmetric, degree 2 in each variable, leading coefficient (x_1 − x_2)² in
x_3, and disc_{x_3} S_3 = 16 f(x_1) f(x_2) (computed). Its zero set is exactly
{x(P_1 ± P_2)} (the squaring step adds no spurious zeros because the two sign
choices of y_1y_2 are exactly the two roots), which is the defining property.

*S_4* = Res_X(S_3(x_1,x_2,X), S_3(x_3,x_4,X)), computed symbolically over
Z[a,b]: 540 terms, degree 4 in each x_i, symmetric under all 24 permutations
(checked). *S_5* = Res_X(S_3(x_1,x_2,X), S_4(x_3,x_4,x_5,X)).

Numerically, for each curve, S_4 and S_5 were built by exact interpolation of
the full-size (formal-degree) Sylvester determinants on the grids {0..4}^4 and
{0..8}^5 (inverse Vandermonde mod p along each axis; the determinant of the
formal Sylvester matrix specialises correctly even where a leading coefficient
vanishes). The interpolated S_4 equals the symbolic S_4 reduced mod p on all
eight curves (exact dictionary equality); S_5 has degree 8 in every variable,
is invariant under all 120 permutations (exact), has 18,822–54,657 nonzero
terms depending on (a, b), and agrees with a direct 6×6 determinant at 50
random points per curve.

**Defining-property check (card: ≥ 200 tuples per m, points from the group
law).** Per curve (8 curves) and per m ∈ {3,4,5}, 200 tuples for each of five
checks — (A) random F_p-points P_1..P_{m−1}, P_m = −ΣP_i: S_m(x(P)) = 0;
(B) the same with random F_{p²}-points (generic Tonelli–Shanks in F_{p²}),
evaluated in F_{p²}; (C) random (x_1..x_{m−1}) ∈ F_p^{m−1}:
F(T) = lc·Π(T − r_ε) as polynomials over F_{p²} with r_ε from the group law;
(D) random full tuples in F_p^m: S_m(x) = 0 ⇔ x_m ∈ {r_ε}; (E) x_m := a
random r_ε (in F_{p²}): S_m(x) = 0. Result: **24,000 of 24,000 pass**; in the
161 degenerate (C) tuples (coincident r_ε, which occur with non-negligible
frequency at p ≈ 100, especially with full rational 2-torsion) the zero-set
identity and even the multiset identity hold in every case. Seeds are
sha256-derived from master seed 20261017 and listed in the output.

## 3. Q1 — ordered base K(x_1..x_{m−1})

**Derivation.** f(x_1), …, f(x_n) are multiplicatively independent modulo
squares in L (each is squarefree in its own variable and the variables are
disjoint), so by Kummer theory N/L is Galois with group C_2^n, the element
ε acting by y_i ↦ ε_i y_i, i.e. P_i ↦ ε_i P_i. On the roots, ε·r_δ = r_{εδ}:
C_2^n acts on {±1}^n/± by translation. The splitting field M = L(r_ε) ⊆ N is
C_2^n-stable, so Gal(M/L) = C_2^n / Gal(N/M), and Gal(N/M) = {ε : r_{εδ} = r_δ
∀δ} = {±(1,…,1)} by the Corollary. Hence:

- deg_T F = 2^{m−2};
- Gal(M/L) ≅ C_2^n/⟨−1⟩ ≅ (Z/2)^{m−2}, order 2^{m−2};
- it acts on the 2^{m−2} roots by translation of {±1}^n/±: **one orbit,
  transitive, regular** (free and transitive), elementary abelian 2-group;
  m = 3: C_2; m = 4: V_4 = C_2²; m = 5: C_2³.
- **Arithmetic group over F_p(x_1..x_n): the same group.** The Kummer
  argument is identical over F_p(x) (the same n independent non-squares), the
  kernel is the same {±1}, and the constant field of N_arith = F_p(x, y) is
  F_p (function field of the geometrically integral E^n), so no constant
  extension can enlarge the splitting field. Equivalently, the arithmetic and
  geometric groups coincide because M_arith ⊗ K = M.

**Corroboration.** (i) `groups.py`: the image of the sign group on
{±1}^n/± has order 2, 4, 8, 16, 32 for m = 3..7, is regular and elementary
abelian, kernel of order 2. (ii) Frobenius statistics (§5): only the two
cycle types of this group occur, and the identity class has frequency
≈ 1/2^{m−2} — Chebotarev's identity density is 1/|G_arith|, so a larger
arithmetic group (e.g. 1/8 instead of 1/4 at m = 4) is excluded by the data
in Table 5.2–5.3 (4σ ≈ 0.008 at N = 50,000).

## 4. Q2 — symmetric base K(e_1..e_{m−1})

**Derivation.** [L : L_0] = n! with group S_n (symmetric functions), and
[N : L] = 2^n, so [N : L_0] = 2^n n!. The signed permutations — sign changes
y_i ↦ −y_i and simultaneous permutations of the pairs (x_i, y_i) — are
2^n n! distinct automorphisms of N fixing L_0, so N/L_0 is Galois with group
W = C_2 ≀ S_n (hyperoctahedral group B_n), and its fixed field is L_0 (the
function field of Sym^n(E/±1) = Sym^n(P^1) = A^n). On the roots,
w = (χ, σ) sends r_ε to r_{ε'} with ε'_{σ(i)} = χ_i ε_i: W acts on
{±1}^n/± through its natural signed-permutation action. The splitting field
M_0 = L_0(r_ε) is W-stable and Gal(M_0/L_0) = W/ker, ker = pointwise
stabiliser of the roots. From δ = (1,…,1): χ = ±(1,…,1); then
δ∘σ^{−1} = ±δ for all δ. For n ≥ 3 this forces σ = id (a single −1 cannot move
to the complement), so ker = ⟨−1⟩ of order 2. For n = 2 (m = 3) the swap also
fixes both roots x(P_1 ± P_2), so ker = ⟨−1⟩ × S_2 of order 4.

Therefore, with V := C_2^n/⟨(1,…,1)⟩ ≅ F_2^n/⟨1⟩ (dimension n − 1) acting
regularly on the roots:

| m | n | roots | W | **Gal(M_0/L_0)** | order | structure |
|---|---|---|---|---|---|---|
| 3 | 2 | 2 | order 8 | C_2 | **2** | (M_0 = L_0(√(f(x_1)f(x_2))); kernel of order 4) |
| 4 | 3 | 4 | B_3, 48 | B_3/Z = **S_4** | **24** | natural action on 4 points (the 4 space diagonals of the cube) |
| 5 | 4 | 8 | B_4, 384 | V ⋊ S_4 | **192** | imprimitive |
| 6 | 5 | 16 | B_5, 3840 | V ⋊ S_5 = 2^4:S_5 ≤ AGL(4,2) | **1920** | primitive |
| 7 | 6 | 32 | B_6, 46080 | V ⋊ S_6 | **23040** | imprimitive |

General formula for m ≥ 4: order 2^{m−2}(m−1)!.

*Primitivity / block systems.* G = V ⋊ S_n acts on V affinely
(v ↦ σ(v) + t); the point stabiliser of 0 is S_n. A block containing 0 is a
union of S_n-orbits closed under translation by its own elements, i.e. an
S_n-invariant subspace of V; conversely every invariant subspace gives a
block system (its cosets). So G is primitive iff V = F_2^n/⟨1⟩ is an
irreducible F_2 S_n-module. For n odd, F_2^n = ⟨1⟩ ⊕ U (U = even-weight
vectors) and V ≅ U is irreducible (n = 3: U is the natural 2-dim module of
S_3 ≅ GL(2,2); n = 5: U has no fixed vector, no 2-dim submodule because S_5
has no quotient in GL(2,2) acting nontrivially with the right fixed points,
and no 3-dim submodule by self-duality). For n even, 1 ∈ U and U/⟨1⟩ is a
proper nontrivial submodule of V of dimension n − 2, and it is the only one
(it is irreducible for n = 4, 6, V has no fixed vector since a transposition
(ij) moves v by (v_i + v_j)(e_i + e_j) ∉ {0, 1} unless v_i = v_j for all pairs,
and any other submodule would meet U/⟨1⟩ in a proper submodule). Hence:

- **m = 5: imprimitive, exactly one nontrivial block system, two blocks of
  size 4**; **m = 7: imprimitive, exactly one nontrivial block system, two
  blocks of size 16**. The blocks are the two parity classes of the number of
  minus signs in ε (well defined modulo global sign because n is even): sign
  changes swap the blocks, permutations preserve them.
- **m = 4 and m = 6: primitive** (m = 4 is the full S_4, 4-transitive).

*Isomorphism type at m = 4:* S_4 — B_3 = S_4 × ⟨−1⟩ (full cube symmetry group =
rotations × central inversion) and −1 is exactly the kernel, so
B_3/⟨−1⟩ ≅ S_4 acting faithfully and naturally on the four antipodal vertex
pairs. Class/cycle-type distribution on the 4 roots: 1^4: 1/24, 2·1²: 6/24,
2²: 3/24, 3·1: 8/24, 4: 6/24.

*Arithmetic version over F_p(e_1..e_n):* the same group, by the same
constant-field argument as in Q1.

**Reduction of the Galois action to a permutation-group computation (as the
card permits for m = 6, 7).** Gal(M_0/L_0) is the image of W in Sym(roots),
with roots ↔ {±1}^n/± and the action above; Gal(M/L) is the image of the
sign subgroup. `groups.py` builds these images with sympy for m = 3..7
(generators: the n coordinate sign changes and the n − 1 adjacent
transpositions) and finds: orders 2, 24, 192, 1920, 23040 (kernel of order
4, 2, 2, 2, 2); all transitive; primitive exactly for m = 3, 4, 6; the unique
minimal block system at m = 5 is {{++++, ++−−, +−+−, +−−+}, {rest}} (two
blocks of 4 = the parity classes), and at m = 7 two blocks of 16, again the
parity classes; m = 4 is verified to be the full Sym(4) with class counts
1, 6, 3, 8, 6. Since the only nontrivial block containing a point must contain
a minimal block and the minimal blocks already have size 2^{n−2}, the block
systems found are the only ones. Further invariants: centre trivial and
derived subgroup of order 12, 48, 960, 5760 at m = 4, 5, 6, 7.

## 5. Q3 — Frobenius rule (ordered base, x_i ∈ F_p)

**Derivation.** Let x_1..x_n ∈ F_p with f(x_i) ≠ 0 and F squarefree of full
degree. Put χ_i := (f(x_i)/p) ∈ {±1} and P_i := (x_i, y_i) with
y_i ∈ F_{p²}, y_i² = f(x_i). The p-power Frobenius π satisfies
π(P_i) = (x_i, y_i^p) = (x_i, χ_i y_i) = χ_i P_i (Euler's criterion; this holds
whether or not x_i is the x-coordinate of an F_p-point — χ_i = −1 is the
twist case). Since the group law and x are defined over F_p,
π(r_ε) = x(Σ ε_i χ_i P_i) = r_{χε}. By Lemma A and the squarefree/full-degree
hypothesis the roots of F are exactly the 2^{n−1} distinct r_ε, so the
Frobenius permutation of the roots is translation by the class of
χ = (χ_1,…,χ_n) in C_2^n/⟨−1⟩ — the Frobenius element in the group of Q1.

**Rule.** The cycle type of Frobenius on the roots of F is
- **1^{2^{m−2}} (all roots in F_p) iff χ_1 = χ_2 = … = χ_{m−1}**, i.e. iff the
  f(x_i) are all squares or all non-squares in F_p;
- **2^{2^{m−3}} (no root in F_p, all roots in F_{p²}) otherwise.**
The set of cycle types that occur is exactly {1^{2^{m−2}}, 2^{2^{m−3}}}
(m = 3: {1², 2}; m = 4: {1⁴, 2²}; m = 5: {1⁸, 2⁴}); F never splits partially,
and never has an irreducible factor of degree > 2. For m = 3 this is the
discriminant statement: disc = 16 f(x_1) f(x_2) is a square iff χ_1 = χ_2.

**Finite-p frequencies.** Over the population {x ∈ F_p^n : f(x_i) ≠ 0} the
number of all-χ-equal tuples is exactly N_+^n + N_−^n, where
N_+ = #{x : f(x) nonzero square} = (p − t − N_0)/2, N_− = (p + t − N_0)/2,
N_0 = #{x : f(x) = 0}, t the trace of Frobenius; so the exact identity
frequency is (N_+^n + N_−^n)/(p − N_0)^n = 2^{−(n−1)}[1 + C(n,2)(t/M)² + …],
M = p − N_0, which tends to the Chebotarev density 1/|G| = 1/2^{m−2} with
relative error ≤ C(n,2)·4/p. The tuples excluded by the hypothesis (F not
squarefree or degree drop) form the ramification locus of the cover; at m = 4
it is {∃ i ≠ j : P_i ± P_j ∈ E[2]} ∪ {x_i = x_j}, of density O(N_0 n²/p).
When the 2-torsion point involved is F_p-rational the relation forces
χ_i = χ_j, so this locus is enriched in the identity class; this is visible
at p ≈ 100 (Table 5.1) and negligible at p ≈ 1000 (Table 5.2). The declared
bound for every frequency comparison below is
|observed − predicted| ≤ 4σ_binomial + β (+ |q_exact − q_Chebotarev| when
comparing with the limit density), with β the fraction of excluded tuples
within the population the prediction describes; for exhaustive enumerations
there is no binomial term.

**Observed vs predicted — two independent paths per tuple.** *Observed*:
distinct-degree factorisation of F over F_p (my `ddf_pattern`, cross-checked
against sympy's `factor_list` on 7,200 random squarefree polynomials of
degrees 2, 3, 4, 8 at the six primes, 0 disagreements, with all 5 cycle types
of S_4 and 18–20 of the 22 of S_8 detected — the detector is not blind to any
class). *Predicted*: Legendre symbols of f(x_i) only.

Table 5.1 — exhaustive enumeration over F_p^{m−1}, p ≤ 150 (card: ≥ 1 curve):

| curve (p, a, b) | m | tuples | f(x_i)=0 | deg drop | F not sqfree | admissible | rule agreement | observed types | N_+^n+N_−^n vs enumerated | id. freq among admissible / exact over f≠0 / 1/2^{m−2} |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 (101, 2, 3) | 3 | 10,201 | 201 | 100 | 0 | 9,900 | 9,900/9,900 | 1²: 4,918; 2: 4,982 | 5,018 = 5,018 | 0.4968 / 0.5018 / 0.5 |
| C1 (101, 2, 3) | 4 | 1,030,301 | 30,301 | 9,836 | 58,628 | 931,536 | 931,536/931,536 | 1⁴: 214,416; 2²: 717,120 | 252,700 = 252,700 | 0.2302 / 0.2527 / 0.25 |
| C6 (103, 0, 7) | 3 | 10,609 | 0 | 103 | 0 | 10,506 | all | 1²: 5,226; 2: 5,280 | 5,329 = 5,329 | 0.4974 / 0.5023 / 0.5 |
| C6 (103, 0, 7) | 4 | 1,092,727 | 0 | 10,555 | 31,314 | 1,050,858 | all | 1⁴: 250,938; 2²: 799,920 | equal | 0.2388 / 0.2535 / 0.25 |
| C7 (101, 5, 0) | 3 | 10,201 | 597 | 98 | 0 | 9,506 | all | 1²: 4,706; 2: 4,800 | 4,804 = 4,804 | 0.4951 / 0.5002 / 0.5 |
| C7 (101, 5, 0) | 4 | 1,030,301 | 89,109 | 9,216 | 109,832 | 822,144 | all | 1⁴: 173,568; 2²: 648,576 | equal | 0.2111 / 0.2503 / 0.25 |
| C8 (101, 0, 1) ss | 3 | 10,201 | 201 | 100 | 0 | 9,900 | all | 1²: 4,900; 2: 5,000 | 5,000 = 5,000 | 0.4949 / 0.5 / 0.5 |
| C8 (101, 0, 1) ss | 4 | 1,030,301 | 30,301 | 9,800 | 58,616 | 931,584 | all | 1⁴: 211,584; 2²: 720,000 | equal | 0.2271 / 0.25 / 0.25 |

In every exhaustive run: 100 % per-tuple agreement, only the two predicted
cycle types, and the all-χ-equal count equals N_+^n + N_−^n to the integer
(e.g. C1, m = 4: 214,416 admissible + 38,284 excluded = 252,700 = 47³ + 53³).
The admissible-population identity frequencies at m = 4 lie below 0.25 by
0.011–0.039, within the declared bound β + |q_exact − 0.25| (β = 0.068, 0.038,
0.127, 0.068 for C1, C6, C7, C8), and the deficit is largest for C7, the curve
with full rational 2-torsion (N_0 = 3), exactly as the ramification-locus
mechanism predicts.

Table 5.2 — random tuples, p ≥ 500, m = 4 (card: ≥ 50,000 on ≥ 2 curves):

| curve (p, a, b) | seed | admissible / 50,000 | rule agreement | observed | id. freq (adm.) | exact over f≠0 | all-χ-equal over f≠0 (binomial z) | bound met (exact / limit) |
|---|---|---|---|---|---|---|---|---|
| C2 (1009, 0, 7), a = 0, p ≡ 1 (3) | 20261018 | 49,816 | 100 % | 1⁴: 12,505; 2²: 37,311 | 0.2510 | 0.25027 | 0.25236 (z = +1.08) | yes / yes |
| C3 (1013, 5, 0), b = 0, p ≡ 1 (4) | 20261019 | 49,517 | 100 % | 1⁴: 12,373; 2²: 37,144 | 0.2499 | 0.25142 | 0.25224 (z = +0.42) | yes / yes |
| C4 (1019, 0, 1), supersingular | 20261020 | 49,542 | 100 % | 1⁴: 12,097; 2²: 37,445 | 0.2442 | 0.25 exactly | 0.24652 (z = −1.79) | yes / yes |
| C5 (997, 1, 5) | 20261021 | 49,520 | 100 % | 1⁴: 12,313; 2²: 37,207 | 0.2487 | 0.25059 | 0.25045 (z = −0.07) | yes / yes |

Table 5.3 — random tuples, p ≥ 500, m = 5 (card: ≥ 2,000 on ≥ 2 curves; 5,000 used):

| curve | seed | admissible / 5,000 | rule agreement | observed | id. freq (adm.) | exact over f≠0 | z (binomial) | bound met |
|---|---|---|---|---|---|---|---|---|
| C2 | 20261022 | 4,957 | 100 % | 1⁸: 598; 2⁴: 4,359 | 0.1206 | 0.12527 | −0.44 | yes / yes |
| C3 | 20261023 | 4,892 | 100 % | 1⁸: 593; 2⁴: 4,299 | 0.1212 | 0.12642 | +0.47 | yes / yes |
| C4 | 20261024 | 4,879 | 100 % | 1⁸: 585; 2⁴: 4,294 | 0.1199 | 0.125 exactly | −0.14 | yes / yes |
| C5 | 20261025 | 4,864 | 100 % | 1⁸: 576; 2⁴: 4,288 | 0.1184 | 0.12559 | −0.25 | yes / yes |

The chi-square p-values of the admissible frequencies against the exact
f≠0 prediction are 0.70, 0.43, 0.0028, 0.32 (m = 4) and 0.32, 0.27, 0.28,
0.13 (m = 5). The low value for C4, m = 4 is the admissibility selection
(194 of the 316 excluded tuples are all-χ-equal, shifting the admissible
identity frequency down by 0.0023) on top of a −1.8σ fluctuation of the
Legendre statistics themselves; it is within the declared bound.

## 5b. Symmetric base at m = 4 — frequencies and a per-tuple rule

The card requires frequencies only; a per-tuple rule follows from Q2 and was
also checked. Over (e_1, e_2, e_3) ∈ F_p³ the x_i are the roots of
g(X) = X³ − e_1X² + e_2X − e_3; the Frobenius element in W/⟨−1⟩ = S_4 is
(χ, σ) with σ the Frobenius permutation of the x_i and χ the signs
π(P_i) = χ_i P_{σ(i)}. Computing the induced permutation of {±1}³/± gives:
g split: 1⁴ if χ_1 = χ_2 = χ_3 else 2²; g = (X − r)·q with q irreducible:
w² = ((s, s, 1), id) with s = χ_1χ_2, so the type is 2·1² if s = +1 and 4 if
s = −1, where s = (N_{F_{p²}/F_p} f(r_1) / p) = ((f(r_1)f(r_2))/p) is computable
in F_p as (α²v − αβu + β² / p) for q = X² + uX + v and f ≡ αX + β (mod q); g
irreducible: 3·1 (w³ ∈ ⟨−1⟩, w ∉ ⟨−1⟩). The exact finite-p class counts over
Ω = {e : g squarefree, gcd(g, f) = 1} follow by counting: 1⁴: C(N_+,3) +
C(N_−,3); 2²: C(p − N_0, 3) − that; 2·1²: (p − N_0)·Q_+; 4: (p − N_0)(Q − Q_+);
3·1: (p³ − p)/3 − [f irreducible]; with Q = (p² − p)/2 − N_0'/2 the number of
monic irreducible quadratics not dividing f, Q_+ = (#E(F_{p²}) − 1 − (2p − N_0)
− N_0')/4 the number of them whose roots r have f(r) a square in F_{p²}
(#E(F_{p²}) = p² + 1 − (t² − 2p), N_0' = number of roots of f in F_{p²}∖F_p).
These tend to the S_4 densities 1/24, 3/24, 6/24, 6/24, 8/24.

F(T) was written in (e_1, e_2, e_3, T) by rewriting each symmetric
T-coefficient of the symbolic S_4 in elementary symmetric functions (zero
remainder for all five; the rewritten form equals direct evaluation at 200
random x-triples per curve). *Observed* = DDF pattern of F_e(T); *predicted* =
the rule above (DDF of g, Legendre symbols; no use of F).

Table 5.4 — 20,000 random (e_1, e_2, e_3) per curve (card: ≥ 20,000 on ≥ 2):

| curve | seed | admissible | rule agreement | observed 1⁴ / 2·1² / 2² / 3·1 / 4 | exact finite-p freq | z vs exact | χ² (4 df) p vs exact / vs S_4 densities | bound met |
|---|---|---|---|---|---|---|---|---|
| C2 | 20261030 | 19,954 | 100 % | 813 / 4,998 / 2,454 / 6,769 / 4,920 | .0415 / .2502 / .1248 / .3337 / .2498 | −0.5, +0.1, −0.8, +1.7, −1.1 | 0.47 / 0.39 | yes / yes |
| C3 | 20261031 | 19,933 | 100 % | 845 / 5,071 / 2,448 / 6,650 / 4,919 | .0416 / .2498 / .1244 / .3340 / .2502 | +0.6, +1.5, −0.7, −0.1, −1.1 | 0.50 / 0.49 | yes / yes |
| C4 | 20261032 | 19,923 | 100 % | 788 / 4,985 / 2,476 / 6,696 / 4,978 | .0414 / .2502 / .1246 / .3340 / .2498 | −1.3, 0.0, −0.2, +0.6, 0.0 | 0.76 / 0.61 | yes / yes |
| C5 | 20261033 | 19,927 | 100 % | 829 / 4,848 / 2,581 / 6,597 / 5,072 | .0415 / .2501 / .1245 / .3340 / .2500 | +0.1, −2.2, +2.1, −0.9, +1.5 | 0.043 / 0.066 | yes / yes |

(β = 0.001–0.002; max |q_exact − q_S4| ≤ 0.0007; C5's p = 0.043 is a 2σ
fluctuation in two classes, within the declared 4σ bound.)

Exhaustive symmetric base on C1 (p = 101, all 1,030,301 e-triples): 10,201
with g not squarefree (= p², as it must be), 10,100 with gcd(g, f) ≠ 1,
|Ω| = 1,010,000 — equal to the closed form; the predicted-class counts over
Ω are 39,641 / 254,100 / 122,059 / 343,400 / 250,800 (1⁴ / 2·1² / 2² / 3·1 /
4) — **equal to the exact formula in every class**; 990,294 admissible,
rule agreement 990,294/990,294; admissible frequencies .0361 / .2466 / .1207 /
.3434 / .2533 versus Ω-frequencies .0393 / .2516 / .1209 / .3400 / .2483,
within β = 0.0195 (the excluded F-ramified locus is again enriched in the
identity class: 3,905 of 19,706).

All five S_4 cycle types occur on every curve, with the identity at ≈ 1/24:
by Chebotarev this certifies that the arithmetic (hence geometric) group at
m = 4 is all of S_4 and not a proper subgroup (A_4 has no 4-cycles or
transpositions, D_4 no 3-cycles, and any proper subgroup has identity density
≥ 1/12).

## 6. Q4 — dependence on the curve

**None of the answers to Q1–Q3 depends on (a, b)**, provided only that
4a³ + 27b² ≠ 0 and p > 3. The derivations use (i) the group law and the 2:1
map x: E → P¹, (ii) Kummer theory for the n independent non-squares f(x_i),
(iii) Z-linear independence of generic points, (iv) π(x, y) = (x, χ(f(x)) y)
for x ∈ F_p, and (v) the structure of Sym^n(E/±) over A^n. None of these sees
the j-invariant. In particular:

- **a = 0 (j = 0, extra automorphisms of order 6)** and **b = 0 (j = 1728,
  order 4)**: the extra automorphisms do not act on the cover E^n → A^n
  compatibly with the coordinates x_i (they move x), so they do not enter the
  monodromy; the groups and the rule are unchanged. Verified on C2
  (y² = x³ + 7, p = 1009 ≡ 1 mod 3, ordinary, t = −19), C6 (p = 103), C3
  (y² = x³ + 5x, p = 1013 ≡ 1 mod 4, ordinary, t = 44) and C7 (p = 101):
  identical behaviour in every table.
- **Supersingular curves** (C4: y² = x³ + 1 over F_1019, C8: y² = x³ + 1 over
  F_101, both with #E(F_p) = p + 1, t = 0, confirmed by point counting): the
  groups and the rule are unchanged; the only effect is on the finite-p
  counts, where t = 0 gives N_+ = N_− and makes the exact ordered-base
  identity frequency exactly 1/2^{m−2} at every p (observed 0.5, 0.25, 0.125
  in Tables 5.1–5.3). The derivation of the Frobenius rule uses π(P) = ±P
  on points with x ∈ F_p, which holds for every curve; supersingularity
  (π² = −p on the Tate module) plays no role.
- What **does** depend on the curve is only the finite-p arithmetic:
  the exact frequencies through t, N_0, N_0', #E(F_{p²}), and the size of the
  excluded ramification locus through the number of F_p-rational 2-torsion
  points (largest for C7 with N_0 = 3). These effects vanish as p → ∞
  (O(1/p) relative) and leave the Chebotarev densities — hence the groups
  — unchanged.
- Out of scope by the card's hypotheses: p ∈ {2, 3} (different model) and
  singular cubics (no group law).

## 7. What could not be determined, and limitations

- Nothing in Q1–Q4 is left undetermined. Statements beyond the card
  (isomorphism types at m = 5, 6, 7) are given only structurally (V ⋊ S_n
  with the computed invariants), which the card does not require.
- The derivations are checkable written arguments plus finite computations
  (claim status: derivation, not machine-verified proof). Lemma C uses the
  standard non-constancy of x([k]P) as a function of x(P); the S_n-module
  statements for n ≤ 6 are also confirmed by the computed block systems.
- Group orders at m = 6, 7 rest on the stated reduction plus the sympy
  permutation-group computation, as the card allows; the reduction's
  ingredients (W = Gal(N/L_0), the action on {±1}^n/±, the kernel) are the
  same ones verified empirically at m = 3, 4, 5.
- Corroboration is toy scale (p ≤ 1019) and the sampling bounds are the
  declared 4σ + β; two of the ~30 goodness-of-fit p-values are below 0.05
  (0.0028 and 0.043), both within the declared bounds and both explained
  above. The exact finite-p counts for the symmetric base were verified
  exhaustively at one prime (p = 101) and by sampling at four others.
- An accounting slip in the first run of the defining-property script
  (resampled tuples whose point sum was O were counted as attempts, so an
  `all_pass` flag read false although no check had failed) was fixed and the
  script re-run; the embedded `defining_property.log` and
  `defining_property_out.json` are from the re-run. The first run's output
  (zero failures, same per-check counts) was observed in the session
  transcript only, since the re-run overwrote its log. The first build
  summary mislabelled one informational field (pure-monomial coefficient
  instead of the x_3-leading coefficient (x_1 − x_2)²); the build was re-run
  after the fix, and an in-session comparison found the regenerated
  S_3/S_4/S_5 dictionaries identical to the first build's (the build is
  deterministic and reproducible from the embedded script). The embedded
  `s_build.log` / `build_out.json` are from the re-run.

## 8. RB verdict

**CONCUR — RB holds.** Each of Q1–Q4 is determined from the statement and
parameters alone, and each determination is internally consistent: the
derived groups (ordered base (Z/2)^{m−2} regular; symmetric base of order
2, 24, 192, 1920, 23040 with S_4 at m = 4, primitive at m = 6, one block
system of two blocks at m = 5 and m = 7; arithmetic = geometric) agree with my
own Frobenius cycle-type frequencies under Chebotarev at and above the
declared sample sizes (exhaustive F_p^{m−1} at m = 3, 4 on four curves with
p ≤ 150; 50,000 tuples at m = 4 and 5,000 at m = 5 on four curves with
p ≥ 997; 20,000 symmetric-base points at m = 4 on four curves plus one
exhaustive enumeration), the Frobenius rule predicts every one of the
5,180,000-odd admissible tuples' cycle types correctly, and my own S_3, S_4,
S_5 pass the defining-property check on 24,000 tuples. This is a verdict on
joint RB only; it says nothing about any goal, criterion, route or other
review.
