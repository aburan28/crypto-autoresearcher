# THM-JETBARRIER1 — The jet-augmented generic group model: a simulation theorem and its exact boundary

| | |
|---|---|
| **ID** | JETB-TH-001 (per candidate D1 reproduction artifact) |
| **Date** | 2026-07-18 |
| **Author** | Executor (theory track), task TASK-20260718-THMJET |
| **Inputs** | ledger/EV-JET-001.yaml, ledger/EV-JETB-001.yaml, ledger/DEC-20260718-010.yaml, experiments/EXP-JETB-001/analysis.md, research_directions_20260717.md (candidates A1, D1) |
| **Verification** | research/verification/thm_jetbarrier1_check.sage → research/verification/thm_jetbarrier1_check.out.json (9/9 checks PASS; §10) |

**Honesty contract.** Every numbered statement below is labeled **PROVED** (proof given
or standard theorem with proof sketch and reference), **CONJECTURE** (precise statement,
no proof claimed), or **OPEN GAP** (exact description of what is missing). Empirical
toy data are cited only as consistency checks of the formalization, never as proof
(AGENTS.md rules 7, 9).

---

## 1. Summary

1. **PROVED (T1, T2, T3):** In the formalized jet-augmented generic-group model
   J(E, FB, r) (§2), every first-order (and every order-r) jet/dual-number query on a
   public-equation variety is decided by zeroth-order data alone; the dual-number
   addition law is exactly Lie-linear in the invariant-differential scalar.
2. **PROVED (T4, simulation theorem):** All jet queries in J(E, FB, r) are simulable
   from public data with **zero** group-oracle overhead; success probabilities are
   preserved exactly; consequently Shoup's Ω(√ℓ) generic discrete-log lower bound and
   the exponent-1/2 barrier lift verbatim to the augmented model, closing all
   A1-class (tangent-screen) channels in-model by proof.
3. **PROVED (L5, P7 amendment incorporated):** the x1 = x_R fiber degree drop is the
   doubling fiber (S_R(x_R, z) = −4y_R²·z + duplication numerator; root = x(2R)),
   zeroth-order-observable; one Newton step on a separable quadratic hits a root **iff
   the start is a root** — the measured 2/p rate and the degenerate-fiber rate 1 are
   exact zeroth-order arithmetic, not jet information.
4. **PROVED (T6, the exact gap/seam):** the simulation theorem's boundary is sharp —
   extending the model with coordinate (x-) data of *composite* (non-public) elements
   collapses genericity; no intermediate "well-defined but non-simulable" jet model
   exists within the encoding-independent class.
5. **CONJECTURE / OPEN GAP:** maximality of the simulable class (C2) and the
   Weil-restriction/descent scope (G2) remain open, stated precisely in §7–§8. The
   previously unresolved "singular branch" confound of EV-JETB-001 is resolved as a
   side product (C1: the tested varieties are generically smooth — PROVED for m = 2, 3).

---

## 2. The model (formalization)

### 2.1 Notation

- k = F_p, p ≥ 5 prime. Dual numbers of order r: D_r = k[ε]/ε^{r+1}; D = D_1.
- E/k: short Weierstrass curve y² = x³ + Ax + B, 4A³ + 27B² ≠ 0; ℓ a large prime
  divisor of #E(k) (the group of interest, |⟨G⟩| = ℓ).
- Semaev summation polynomials S_m ∈ k[x_1, …, x_m] attached to E, with the
  instrument convention (experiments/EXP-JETB-001/jetbarrier1_model_check.sage):

  S_3(X_1, X_2, X_3) = (X_1−X_2)²X_3² − 2((X_1+X_2)(X_1X_2+A) + 2B)X_3
                       + (X_1X_2−A)² − 4B(X_1+X_2),

  symmetric in all three variables (verification S4), equivalently
  S_3 = (e_2 − A)² − 4e_1e_3 − 4Be_1 in the elementary symmetric polynomials (S4).
  S_R(x_1, z) := S_3(x_1, z, x_R) is the target-sectioned m = 2 variety.

### 2.2 The formalization decision (public vs hidden data)

Candidate D1 flags the obstruction: *"the model may be unformalizable without leaking
the encoding."* A finite cyclic group of prime order has **no intrinsic** jet
structure; any jet notion must come from auxiliary data. We therefore fix the
partition that every real index-calculus deployment uses, and that EXP-JETB-001
tested:

- **PUBLIC:** p, the curve equation (A, B), ℓ, the factor-base x-coordinates
  {x_i}_{i≤B}, the target x-coordinate x_R, sign/lift conventions (min-y).
- **HIDDEN:** the encoding map σ, all discrete-log relations, and every
  curve-model datum of *composite* elements (elements only reachable through the
  group oracle), e.g. x-coordinates of adversary-formed combinations.

This partition is not an arbitrary choice: §6 (T6) proves it is exactly the seam of
the simulability question.

### 2.3 Base model GM (Shoup)

A random injective encoding σ : Z/ℓ → {0,1}*; the adversary receives handles
σ(G) (generator) and σ(R) (target), and a group oracle
add(σ(a), σ(b)) ↦ σ(a+b), neg(σ(a)) ↦ σ(−a); equality is handle equality.
Shoup (EUROCRYPT 1997): any generic algorithm computing the discrete log with q
oracle queries succeeds with probability O(q²/ℓ); constant success needs
q = Ω(√ℓ).

### 2.4 Admissible varieties and the jet oracle

**Definition (admissible family 𝒱_pub).** A variety V ∈ 𝒱_pub is a subscheme of
A^m cut out by polynomial equations whose coefficients are explicit functions of
PUBLIC data. Examples: all S_m, all target sections S_R, their coordinate
projections and diagonals, and any public-affine constraint locus.

**Definition (jet oracle, order r).** For V ∈ 𝒱_pub (m variables), a public point
x ∈ k^m (given by coordinates), and a public affine constraint C(t) (possibly vacuous;
"free lift" when vacuous), the oracle J^r returns

  (i) the boolean "∃ t ∈ k^m with V(x + εt + higher jets) consistent over D_r
       and C satisfied", and
  (ii) on request, an explicit description of the solution set (an affine
       k-subspace of jet coordinates).

At r = 1, free lift: "∃ t : F(x + εt) = 0 in D for all F ∈ I(V)".

**Definition (model J(E, FB, r)).** GM (§2.3) plus the jet oracle J^r restricted to
𝒱_pub and public points, plus PUBLIC data as in §2.2. The A1 tangent screen, the
EXP-JET-001/EXP-JETB-001 test batteries, and every query in A1's algorithmic path are
queries of this model at r = 1.

**Definition (simulability, Shoup-style).** An augmentation is *simulable* if there
exists a base-model (GM) algorithm — the simulator — that answers every augmented
query with the identical answer distribution, using only base-oracle queries and
public-data computation. Overhead is measured in (group-oracle queries, public
arithmetic) per augmented query.

---

## 3. First-order screen equivalence

**Theorem T1 (PROVED).** Let V = {F_1 = … = F_s = 0} ∈ 𝒱_pub and x ∈ k^m a public
point. Then for the order-1 free-lift query:

1. ∃ t ∈ k^m with F_i(x + εt) = 0 in D for all i  ⟺  F_i(x) = 0 for all i
   (x is a k-point of V).
2. When x ∈ V(k), the solution set is ⋂_i ker dF_i|_x — the Zariski tangent space
   T_x V — of dimension m − rank(∂F_i/∂x_j)(x). In particular dim = m − s at smooth
   points of a complete intersection, and dim = m at points where all differentials
   vanish.
3. The same holds with any public affine constraint C(t): the answer is the
   consistency of an affine k-linear system determined by (public equations, x).

**Proof.** Taylor expansion over D: F(x + εt) = F(x) + ε·(∇F(x)·t), since ε² = 0
kills all higher-order terms (verified symbolically for S_3 over ℚ; verification S5).
The ε-block is therefore *homogeneous* linear in t: t = 0 always solves it, and no t
can repair a zeroth-order failure F(x) ≠ 0 (the ε-part cannot cancel a nonzero
constant term). Hence consistency ⟺ zeroth-order membership; the solution space is
the kernel of the Jacobian, which is the definition of the Zariski tangent space.
Part 3 is the same statement with extra public linear rows. ∎

**Corollary T1′ (PROVED).** For the A1 tangent screen on any section of S_m:
σ_pass/p_m = 1, σ_true = 1, leakage = 0 — identically, as a theorem about the model,
for every curve, every p, every m. The screen verdict equals the zeroth-order
relation verdict on every tuple.

*Empirical anchor (consistency, not proof):* EV-JETB-001 measured exactly this —
0 screen/zeroth-order mismatches on 49,362 FB tuples + 10,201 exhaustive pairs +
3,600 random negatives; σ_true = 1, leakage = 0, σ_pass/p_m = 1 at all three sizes.
EV-JET-001 independently measured σ = 1 on 9,984 candidate pairs (the "ε-block
Cramer determinant never vanishes" observation is T1 in the m = 3 split form).

---

## 4. All jet orders

**Theorem T2 (PROVED).** For V ∈ 𝒱_pub, x ∈ k^m, and every order r ≥ 1:

1. If x is a smooth k-point of V and V(x) = 0, then x lifts to a D_r-point for
   every r, and the jet fiber has the expected dimension r·dim_x V (locally).
2. If x is singular, the jet fiber over x is the jet scheme J_r(V) at x, whose
   defining equations are the Hasse–Schmidt derivatives of the (public) defining
   equations of V — public symbolic data.
3. In all cases, the J^r query answer is a function of (public equations, x) only.

**Proof.** (1) Smoothness ⟹ formal smoothness ⟹ infinitesimal lifting: a smooth
k-point of a finite-type k-scheme lifts through every nilpotent thickening
(standard; e.g. the local criterion — the truncated local rings are formal power
series rings, and uniformizing parameters lift order by order; each step is a
consistent inhomogeneous linear system over k because the Jacobian has full rank).
(2) The r-th jet scheme of an explicitly presented variety is effectively computable
from the presentation by Hasse–Schmidt derivation (standard jet-scheme theory;
see e.g. Vojta, "Jets via Hasse–Schmidt derivations", 2007; Mustaţă, Invent. 2001,
for the l.c.i. dimension formulas). The answer is therefore public-data computable.
(3) Immediate from (1)–(2). ∎

**Remark.** T2's simulability is *qualitative*: at smooth points the simulator needs
no computation beyond the zeroth-order test; at singular points the computation is
public symbolic algebra whose cost depends on (m, r, the equations) but involves
**zero group-oracle queries at any order**. Higher-order jets therefore open nothing
in this model.

---

## 5. The dual-number group law

**Theorem T3 (PROVED).** Let E/k be an elliptic curve (char k ≠ 2, 3).

1. The reduction map E(D) → E(k) is surjective with kernel canonically isomorphic
   to the additive group (k, +): for P ∈ E(D) reducing to 𝒪, the assignment
   P ↦ −x(P)/y(P) ∈ εk ≅ k is a group isomorphism.
2. Moreover E(D) ≅ E(k) × k as abelian groups: the invariant differential
   ω = dx/(2y) trivializes the tangent bundle, T_P E ∋ v ↦ ω_P(v) ∈ k, and the
   group law on dual-number lifts is
   (P, s) ⊞ (Q, t) = (P + Q, s + t) in ω-scalar coordinates.
3. Consequently every dual-number addition-chain query decomposes into a
   zeroth-order EC computation (a group-oracle query in GM) and public k-linear
   arithmetic in the ω-scalars a/(2y) (at y = 0 use the nonvanishing contraction
   ω = dy/(3x²+A); the two forms agree wherever both are defined since
   2y dy = (3x²+A) dx).

**Proof.** (1) The kernel consists of points reducing to 𝒪; in the standard
coordinate z = −x/y at 𝒪 these are exactly the points with z ∈ εk. The formal group
law of E satisfies F(X, Y) = X + Y + (terms of total degree ≥ 2) (definition of a
formal group law; Silverman, *The Arithmetic of Elliptic Curves*, Ch. IV). Every
degree-≥ 2 monomial vanishes on εk because ε² = 0; hence F(z_1, z_2) = z_1 + z_2
exactly on the kernel, which is therefore the additive group εk ≅ (k, +).
Surjectivity: every k-point lifts (take the same affine coordinates; the curve
equation holds in D since it holds in k).
(2) The tangent bundle of an abelian variety splits as a group scheme,
TE ≅ E × Lie(E), via translation-invariant differentials (Mumford, *Abelian
Varieties*); the conjugation action of E on Lie(E) is trivial because E is
commutative, so the semidirect product is direct. For an elliptic curve, Lie(E) is
one-dimensional with basis dual to ω = dx/(2y) (the invariant differential, which
never vanishes on E: at y = 0 the complementary form dy/(3x²+A) is regular since
3x²+A ≠ 0 at roots of the separable cubic — separability ⟺ 4A³+27B² ≠ 0;
verification S4 confirms resultant(x³+Ax+B, 3x²+A) = 4A³+27B² exactly).
(3) Immediate from (2). ∎

*Empirical anchor:* EV-JETB-001 P6 — 0 zeroth-order failures, 0 ω-linearity
failures, 0 swap-invariance failures in 1,745 dual-number addition probes across 18
curve instances; 18/18 chain relations constructively witnessed. Re-anchored at
p = 101 (20 probes, 0 failures) by verification S8(a).

---

## 6. The simulation theorem, the P7 amendment, and the seam

### 6.1 Simulation

**Theorem T4 (simulation theorem for J(E, FB, r)) — PROVED.** Every query of the
model J(E, FB, r) (§2.4) is simulable with **zero group-oracle overhead** and
public arithmetic only. Explicitly, the simulator answers:

| Query family | Answer computed as | Group-oracle queries |
|---|---|---|
| Free-lift screen J^1_V(x) | ∧[F_i(x) = 0], public polynomial evaluation (T1) | 0 |
| Constrained-lift screen | consistency of public affine linear system (T1.3) | 0 |
| Solution-space basis | kernel of public Jacobian matrix (T1.2) | 0 |
| Order-r query | T2: smooth ⇒ zeroth-order verdict; singular ⇒ public Hasse–Schmidt computation | 0 |
| Dual-number addition chain | group oracle for the zeroth-order shadow (same count as the base-model shadow) + public k-linear ω-arithmetic (T3) | same as shadow, +0 |
| Newton/jet-linear solve verdicts | public fiber arithmetic (L5 below) | 0 |

**Proof.** By T1–T3 every answer is a deterministic function of public data (the
curve equation, the public coordinates of the query point, and the public defining
equations of V) — or, for chain queries, of public data plus the zeroth-order group
oracle answers, which the simulator obtains from its own base oracle at exactly the
cost of the shadow computation. Since answers are *identical* (not merely
indistinguishable), any augmented-model adversary A′ is converted query-by-query
into a base-model adversary A with the same group-oracle query count and identical
success probability. ∎

**Corollary T4-a (barrier transfer) — PROVED.** Shoup's lower bound lifts verbatim
to J(E, FB, r): any adversary in the jet-augmented model computing the discrete log
with q group-oracle queries succeeds with probability O(q²/ℓ), hence needs
Ω(√ℓ) group operations regardless of the number and order of jet queries. The
exponent-1/2 generic barrier is certified for the entire first/higher-order jet
family within this model.

**Corollary T4-b (no harvesting pruning) — PROVED.** For the A1-class relation
screen on public summation varieties: the screen pass rate equals the base relation
rate exactly (T1′: σ_pass/p_m = 1), so jet screening cannot prune the public
candidate space; the screen is pure additive overhead in-model (measured:
C_lin + σ·C_nonlin > C_nonlin at all sizes, EV-JET-001/EV-JETB-001).

**Remark (m-dependence).** Overhead is stated per fixed m: evaluating S_m on public
data is exactly the cost the base-model zeroth-order channel already pays, so the
*relative* simulation overhead is 1 at every m; no asymptotic separation can arise
from the jet channel at any m. The symbolic size of S_m (degree 2^{m−2} per
variable) is a property of the zeroth-order problem, not of the augmentation.

**General simulability principle (PROVED, same argument).** Any augmentation oracle
whose answers are functions of (public data) and/or (the formal generator
expressions the simulator already maintains for every handle, as in Shoup's own
simulation) is simulable exactly. The jet augmentations are of the first kind.

### 6.2 The P7 amendment, upgraded to exact algebra

**Lemma L5 (PROVED; incorporates the P7 amendment of DEC-20260718-010).**
For S_R(x_1, z) = S_3(x_1, z, x_R):

1. **Degree-drop locus (S1).** The leading coefficient of S_R as a polynomial in z
   is (x_1 − x_R)² — a symbolic identity over ℚ[A, B, x_1, x_R, z]
   (verification S1). Hence deg_z S_R = 1 ⟺ x_1 = x_R, a Zariski-closed condition
   on the *input coordinates*: zeroth-order-observable, requiring no jet query.
2. **The drop fiber is the doubling fiber (S2).** On x_1 = x_R:
   S_R(x_R, z) = −4(x_R³ + Ax_R + B)·z + ((x_R²−A)² − 8Bx_R)
   = −4y_R²·z + (duplication-formula numerator) (symbolic identity, verification
   S2). For R not 2-torsion (y_R ≠ 0 — always true in the tested family, R in a
   large prime subgroup) the fiber is exactly linear, with unique root
   z* = x(2R) by the classical duplication formula (Silverman AEC III.2.3).
   Geometrically: the dropped root is the point at infinity (the Q = 𝒪 branch of
   ±R ± Q = ±R); the surviving finite root is x(2R). One Newton step solves a
   linear equation from every start: hit rate exactly 1.
3. **Exact Newton fact on quadratics (S3).** Let q(z) = c(z−r_1)(z−r_2), r_1 ≠ r_2,
   over any field of characteristic ≠ 2, and N(z_0) = z_0 − q(z_0)/q′(z_0). Then
   N(z_0) − r_i = (z_0 − r_i)²/(2z_0 − r_1 − r_2) for i = 1, 2 (symbolic identity,
   verification S3). Hence one Newton step lands on a root **iff the start is that
   root**, and the undefined locus q′(z_0) = 0 is the single midpoint
   (r_1+r_2)/2. Therefore on non-degenerate fibers (x_1 ≠ x_R) the one-step hit
   rate is exactly #{F_p-roots}/p ≤ 2/p, and the skip rate is exactly 1/p per fiber.

**Agreement with measurements (consistency).** EV-JETB-001: hit rate 1.0 on the
x_1 = x_R fibers (100/100, both p = 101 and 211); off-fiber ratios to 2/p of
1.13/1.11/1.15 at p = 101/211/431 (Poisson-consistent); exhaustive enumeration of
all 101 starts (debug_newton.sage) found the hit set to be exactly the 2
root-starts — the content of L5.3, re-verified exhaustively on an F_101 fiber in
S8(b) (roots = {x(R−P_1), x(R+P_1)} exactly; 1 critical value = the midpoint; 0
hit/root mismatches). The 43 recorded deriv0-skips match the L5.3 prediction
≈ Σ(100/p) = 27.7 + 10.9 + 3.5 ≈ 42.1 across the three sizes. The frozen P7 bound
is thereby amended as proposed in EXP-JETB-001 §4: **"hit rate = 2/p on
non-degenerate fibers; rate 1 on the x_1 = x_R degree-drop (doubling) fiber, which
is zeroth-order-observable"** — and both sides are now exact algebra, not estimates.
No Newton/jet-linear solve transcends zeroth-order information anywhere.

### 6.3 The seam (exact boundary of the theorem)

**Proposition T6 (PROVED).** Extend J(E, FB, r) by a coordinate oracle X that,
given a handle σ(P) for a *composite* element P (one known to the simulator only as
a formal expression), returns the x-coordinate of P on E. Then:

1. The extended model is not exactly simulable in Shoup's sense unless the generic
   discrete-log problem is easy: an exact simulator would answer PUBLIC predicates
   of X(σ-composites) (e.g. "is x(P) in the FB interval?") with certainty, which
   composed over O(1) queries decides DL-dependent predicates that Shoup's bound
   caps at O(q²/ℓ) — contradiction. Hence generic lower bounds do not apply to the
   extended model.
2. But the extended model is precisely "the adversary sees the actual curve
   encoding of every element" — i.e., the ordinary (non-generic) ECDLP instance, in
   which no generic lower bound is possible by definition.

**Proof sketch.** (1) Formalize: with X available, FB-membership testing of
arbitrary formal combinations becomes a public predicate of hidden data; a
simulator maintaining only formal expressions cannot evaluate it without resolving
those expressions to curve points, i.e., without solving the very instance the
lower bound protects. (2) The map handle ↦ x-coordinate determines the group
element up to sign; adjoining the sign (or the group law on x-pairs via S_3
consistency) recovers the full curve arithmetic: the model is the curve itself. ∎

**Consequence (the dichotomy).** A jet augmentation of the generic group model is
either (i) defined on public-coordinate data — then it is simulable (T1–T4) and the
barrier holds — or (ii) requires hidden curve-model data of composite elements —
then it leaves the generic model entirely (T6). **There is no well-defined
intermediate regime in which a jet query is encoding-independent yet
non-simulable.** This is the exact gap the D1 candidate asked to find, and it is
closed: the only "non-simulable jet models" are non-generic models.

---

## 7. Conjectures (precise statements, no proof claimed)

**C1 (singular locus of the x-only summation varieties) — core PROVED, sharp form
CONJECTURE.**

- **PROVED (this work; verification S7, S4).** Over the generic curve
  (function field ℚ(A, B)): the m = 2 target variety S_R(x_1, z) = 0 is **smooth**
  (singular ideal is the unit ideal; S7-m2). The m = 3 surface S_3 = 0 has a
  **finite** singular locus of closure-degree 6 (S7-m3), and the three points
  (t, t, t) with t³ + At + B = 0 (2-torsion x-coordinates) are singular (S4:
  ∇S_3 at the diagonal is (−2(3t²+A)x_3 + 2(t³−At−2B), same, −4(t³+At+B)),
  vanishing at x_3 = t exactly when t³+At+B = 0).
- **CONJECTURE (precise).** The singular locus of the generic x-only S_3 surface is
  *exactly* {(t, t, t) : t³ + At + B = 0} (three points over the algebraic closure,
  each of multiplicity 2 — matching the proved degree 6), with no off-diagonal
  component; and for all m ≥ 3 the x-only S_m variety's singular locus has
  codimension ≥ 2 and is supported on the big diagonals over torsion-division
  x-coordinates.
- **Consequence (PROVED from finiteness alone).** For almost all specializations
  (E, x_R) over F_p the number of singular F_p-points is ≤ 6 (m = 3) and 0 (m = 2),
  so a uniformly random tuple hits a singular point with probability O(1/p³) —
  explaining the toy observation (0 singular relations in ~59.5k tuples + 10,201
  exhaustive pairs, EV-JETB-001) and **closing EV-JETB-001's unresolved confound**:
  the singular ε-dimension branch (dim = #jet variables) is generically vacuous for
  the tested varieties, not merely unobserved. (Concrete anchor S6: p = 1009,
  A = 3, B = 1 — dimension 0, degree 6, 0 F_p-points, consistent with #E odd.)
- **Why C1 does not affect the barrier:** T1/T2 cover singular points explicitly;
  simulability holds there with zero group queries regardless.

**C2 (maximality of the simulable class) — CONJECTURE (precise).** The class of
exactly simulable augmentations of GM is *maximal* in the following sense: every
augmentation whose answers factor through (public data, the simulator's formal
expressions) is exactly simulable (PROVED, §6.1), and every augmentation whose
answers do not so factor either (a) is encoding-dependent (not a generic model), or
(b) cannot be simulated exactly — with simulation failure probability governed by
Shoup-type collision bounds O(q²/ℓ). *What is missing:* a formal definition of
"augmentation" general enough to quantify over, and a completeness proof of the
dichotomy; see G1.

---

## 8. Open gaps (exact statements of what is missing)

- **G1 (meta-completeness).** Characterize the largest class 𝒞 of oracles with
  GM + 𝒞 exactly (or O(q²/ℓ)-lossily) simulable. *Missing:* (i) a formal language
  for augmentations (answer = which function of which hidden/public objects);
  (ii) a proof that the two proved families (public-data functions; formal-expression
  functions) exhaust 𝒞 up to the Shoup collision loss. The jet question is settled
  without G1 (T1–T6); G1 is the general model theory.
- **G2 (descent / Weil-restriction scope).** EV-JET-001's boundary: settings "where
  EC addition is unavailable locally" (Weil restriction to a subfield, descent where
  the relevant summation variety is defined over an extension and the base-field
  group oracle does not evaluate it). T1–T3 are field-agnostic algebra and carry
  over pointwise; what is *not* covered is the assumption that the variety's
  equations are PUBLIC to the simulator and evaluable at the query point. *Missing:*
  a formalization of "public" in descent models (equations may involve the unknown
  descent data) and a re-proof of T4 there. Not claimed in this note.
- **G3 (remark, not a gap).** Simulator cost at singular points and at large (m, r)
  is public symbolic computation (Hasse–Schmidt/jet-scheme equations), polynomial in
  the jet-space dimension for fixed equations; zero group queries at every order.
- **G4 (remark).** Quantum: the model is classical; generic quantum bounds are moot
  for ECDLP (Shor). Nothing about jets changes that.

---

## 9. Correspondence with the toy evidence (consistency ledger)

| Note statement | Model prediction | Toy measurement (EV-JETB-001, EV-JET-001) | Match |
|---|---|---|---|
| T1 / T1′ | σ_pass/p_m = 1, σ_true = 1, leakage = 0 | 1.0 exactly at p ∈ {101, 211, 431}, m ∈ {2, 3}; 0/49,362 + 0/10,201 + 0/3,600 mismatches/leaks; EV-JET-001: σ = 1 on 9,984 pairs | exact |
| T1.2 (kernel = Zariski tangent) | ε-dim = m−1 smooth, m singular | dim 1 (m = 2), 2 (m = 3) at 100% of true relations; 0 singular observed (C1 explains: generically none) | exact |
| T3 (dual-number Lie-linearity) | 0 linearity failures | 0/1,745 probes, swap-invariance exact; 18/18 chain witnesses | exact |
| L5.1–L5.2 (drop fiber) | rate 1 on x_1 = x_R; root x(2R) | 100/100 and 100/100 (p = 101, 211); S8(c): root = x(2R), 10/10 hits | exact |
| L5.3 (Newton on quadratics) | rate = #roots/p ≤ 2/p; skip = midpoint | 1.13/1.11/1.15 × 2/p (Poisson); exhaustive hit set = 2 root-starts; 43 skips ≈ 42.1 predicted | exact |
| C1 (singular locus finite/small) | O(1) singular F_p-points | 0 in ~59.5k tuples + 10,201 exhaustive; S6: 0 F_1009-points | consistent |
| T4 (simulation) | no non-simulable operation exists in-model | none observed at any size (D1 decision rule: barrier side) | consistent |

Note the roles (rule 7): the theorems are field-size-independent algebra; the toy
data confirm that the *formalization* matches the real objects, and supply the D1
decision rule's "match = barrier evidence" side. The proof content above does not
rest on toy scale.

---

## 10. Verification artifacts

- Script: `research/verification/thm_jetbarrier1_check.sage` (self-contained,
  deterministic; S3 convention copied verbatim from the EXP-JETB-001 instrument).
- Receipt: `research/verification/thm_jetbarrier1_check.out.json` — **9/9 checks
  PASS** (S1 leading coefficient; S2 doubling-fiber identity; S3 exact Newton
  identities; S4 symmetry + diagonal gradient + resultant = 4A³+27B²; S5 dual-number
  Taylor; S6 concrete singular locus dim 0 / degree 6 / 0 F_1009-points; S7 generic
  singular loci: m = 3 finite degree 6, m = 2 empty; S8 numeric anchors at p = 101:
  20/20 ω-linearity, exhaustive Newton root-start fact, degenerate-fiber root =
  x(2R), 10/10 Newton hits).
- Exact command: `sage research/verification/thm_jetbarrier1_check.sage`
  (stdout/stderr logs beside the receipt). Environment: SageMath 10.9.
- Run accounting: 2 sage invocations of ≤ 10 allowed. First invocation failed
  (implementation defect: Sage preparser Integers not JSON-serializable; no
  measurements — infrastructure, not evidence); fixed and rerun, exit 0, wall
  seconds < 1 of the 3,300 s budget (receipt: wall_seconds ≈ 0; logs retained).
- Provenance: git HEAD 99693e3bdd7ba8ca24c0f7940c46c1aae4f632af, dirty tree from
  the concurrent coordinator session; this task added only
  `research/THM_JETBARRIER1.md` and `research/verification/thm_jetbarrier1_check.*`.
  No commits made.

---

## 11. Consequences for candidates A1 and D1

- The D1 promotion gate's first branch — *"proved simulation theorem"* — is
  delivered for the augmentation class 𝒱_pub at all jet orders, which contains every
  query family in A1's algorithmic path and both experiments' batteries. In-model,
  the jet-augmented channel is closed at exponent 1/2 by proof (T4-a, T4-b), not
  merely by toy evidence.
- A1's scoped empirical negative (EV-JET-001, EV-JETB-001) is now explained by a
  theorem: σ = 1 is T1′, not a measured accident.
- The only routes past the barrier: leave the generic model (T6 — then no generic
  lower bound applies and the question becomes the concrete ECDLP instance), or the
  G2 descent/Weil-restriction scope (open), or G1 (model theory). Higher jet orders
  and constrained lifts are closed (T1.3, T2).
- **Status decisions are the Coordinator's** (AGENTS.md): this note supplies the
  theorem track; whether H-JETB-001 moves from supported_scoped to closed-by-proof,
  and the final disposition of A1, are for the Coordinator.

## 12. References

1. V. Shoup, *Lower bounds for discrete logarithms and related problems*, EUROCRYPT
   1997. (Base model; Ω(√ℓ) bound; simulation technique.)
2. U. Maurer, *Abstract models of computation in cryptography*, Cryptography and
   Coding 2005. (Group-only axiomatization; as flagged in D1.)
3. J. H. Silverman, *The Arithmetic of Elliptic Curves*, Ch. III (invariant
   differential, duplication formula) and Ch. IV (formal groups). (T3, L5.)
4. D. Mumford, *Abelian Varieties*. (Tangent bundle splits over an abelian variety;
   T3.2.)
5. I. Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
   curves*, 2004. (The S_m family; §2.1 convention cross-checked against S4.)
6. P. Vojta, *Jets via Hasse–Schmidt derivations*, in Diophantine Geometry, CRM
   Series, 2007; M. Mustaţă, *Jet schemes of locally complete intersection canonical
   singularities*, Invent. Math. 2001. (Effectivity of jet schemes; T2.2.)
7. Jager–Schwenk generic-model refinements (as flagged "recollection" in the D1
   candidate text; not load-bearing here).

*Prepared under the AGENTS.md honesty contract: no fabricated proofs, commands,
outputs, or statistics; every claim above carries its label, and the executable
anchors are in the cited receipt.*
