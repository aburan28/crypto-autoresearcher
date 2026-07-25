# Module 06 — Elliptic Curves and the Group Law

> **Goal.** Define elliptic curves properly (including the point at
> infinity), build the chord-and-tangent group law, and derive the
> addition formulas you implemented in
> [`lab03_elliptic_curves.py`](../labs/lab03_elliptic_curves.py).
> The interactive playground's **ℝ-curve** and **F_p-curve** tabs are
> this module in clickable form.

## 1. The curve

Over a field K of characteristic ≠ 2, 3 (always true here: our p are
large-ish), an **elliptic curve** is

  E : y² = x³ + a x + b,  with Δ = −16(4a³ + 27b²) ≠ 0,

together with one extra point **O "at infinity"** (§2). The condition
Δ ≠ 0 says the cubic x³ + ax + b has three distinct roots, i.e. the
curve is **smooth** — no self-crossings (nodes) or spikes (cusps). Try
a = −3, b = 2 (Δ = 0) in the ℝ-tab of the playground and watch the node
appear; the tangent there is ambiguous and the group law dies.
Singular "curves" are excluded *because the group law fails*, and in
fact their smooth part degenerates to the boring groups (K, +) or
(K^×, ×) — where discrete logs are easy. Smoothness is a security
assumption in disguise.

(General Weierstrass form y² + a₁xy + a₃y = … is needed only in
characteristics 2 and 3; completing the square/cube reduces to the short
form otherwise.)

## 2. Where the point at infinity lives: the projective plane

Affine solutions (x, y) miss something: a vertical line x = c meets the
curve in only 2 points, while other lines meet it in 3 (with
multiplicity). The fix is the **projective plane** ℙ²:

* points of ℙ² = nonzero triples (X : Y : Z) up to scaling;
* affine points embed as (x : y : 1); the extra points with Z = 0 form
  the **line at infinity**, one point per direction of parallel lines;
* homogenize the curve: Y²Z = X³ + aXZ² + bZ³. Setting Z = 0 forces
  X³ = 0, so the curve has **exactly one** point at infinity:
  O = (0 : 1 : 0) — the direction of vertical lines.

So: every vertical line passes through O, and O is a genuine, smooth
point of the projective curve. Now *every* line meets E in exactly 3
points counted with multiplicity (Bézout's theorem for a line and a
cubic). That trichotomy is the engine of the group law.

## 3. The group law

**Rule.** Three collinear points on E sum to O. Equivalently:

  P + Q := the reflection across the x-axis of the third intersection
  of line PQ with E.

* **identity** O: line through P and O is vertical, third point is
  (x, −y), reflected back to P. ✓
* **inverse**: −(x, y) = (x, −y); P + (−P) uses a vertical line whose
  third point is O.
* **doubling**: the "line through P twice" is the tangent at P
  (smoothness needed!).
* **commutativity**: the line PQ doesn't care about order.
* **associativity**: the one hard axiom. Provable by (painful) direct
  computation, by the Cayley–Bacharach theorem on cubics through 8
  points, or — the modern viewpoint — because the map
  P ↦ [P] − [O] identifies E with its degree-0 **Picard group**
  (divisor classes), which is a group by construction. Take
  associativity on faith today; lab 03's self-check verifies it on
  thousands of random triples.

Play with this now: in the playground's ℝ-tab, click two points and
watch the chord, the third intersection, and the reflection.

## 4. The formulas

Let P = (x₁, y₁), Q = (x₂, y₂), neither O.

* If x₁ = x₂ and y₁ = −y₂: P + Q = O.
* Otherwise, with slope
  λ = (y₂ − y₁)/(x₂ − x₁) if P ≠ Q, λ = (3x₁² + a)/(2y₁) if P = Q:

  x₃ = λ² − x₁ − x₂,  y₃ = λ(x₁ − x₃) − y₁.

*Derivation.* Substitute y = λ(x − x₁) + y₁ into the curve; the cubic in
x has roots x₁, x₂, x₃, and the coefficient of x² gives
x₁ + x₂ + x₃ = λ². Reflect for y₃. ∎

Notice **the formulas are rational functions of the coordinates with
coefficients in K** — so if P, Q have coordinates in K, so does P + Q:
E(K) is a group for *every* field K containing a, b. The same curve
equation gives ℝ-pictures for intuition and F_p / F_{p²} groups for
cryptography. This "one equation, many fields" flexibility is also why
lab 03's code, written once over an abstract field interface, runs over
both `Fp` and `Fp2` unchanged.

### Worked example over F_13, E: y² = x³ + x + 1

P = (0, 1), Q = (1, 4) (check: 1 + 1 + 1 = 3 ≡ 4² = 16 ✓).
λ = (4−1)/(1−0) = 3; x₃ = 9 − 0 − 1 = 8; y₃ = 3(0 − 8) − 1 = −25 ≡ 1.
So P + Q = (8, 1). Doubling P: λ = (0 + 1)/2 = 1·2⁻¹ = 7 (2·7 = 14 ≡ 1);
x₃ = 49 − 0 = 49 ≡ 10; y₃ = 7(0 − 10) − 1 = −71 ≡ −71 + 78 = 7:
2P = (10, 7). Verify both with `E.point(...)` in lab 03.

## 5. Scalar multiplication

n·P = P + ⋯ + P via **double-and-add** — the square-and-multiply of
module 01 with multiplication replaced by point addition: O(log n) point
operations. This map [n] : E → E is a group homomorphism whose kernel
E[n] (the n-torsion) will dominate modules 07–10 — and [n] is also your
first isogeny, though we won't say so until module 09.

## 6. Two invariants you must know

* **Discriminant** Δ = −16(4a³ + 27b²): nonzero ⟺ elliptic.
* **j-invariant**: 

  j(E) = 1728 · 4a³ / (4a³ + 27b²).

  Two curves are isomorphic **over the algebraic closure** iff they have
  the same j (module 08 makes this precise, including the subtlety of
  twists — same j, different group over F_p!). The j-invariant is the
  "name tag" of a curve, and the vertices of the isogeny graphs in
  module 10 are labeled by j, not by (a, b): j = the curve up to
  cosmetic changes of coordinates.

  Special values: j = 0 (a = 0, y² = x³ + b) and j = 1728 (b = 0,
  y² = x³ + ax) — the two curves with extra symmetry, which will keep
  demanding special treatment all course long.

## 7. Self-check

<details><summary><b>Q1.</b> Why exactly one point at infinity, when a
projective cubic could a priori have up to three?</summary>

Intersect Y²Z = X³ + aXZ² + bZ³ with Z = 0: X³ = 0, a triple root, i.e.
the single point (0 : 1 : 0) with multiplicity 3 — the line at infinity
is an inflection tangent there. (That triple contact is why O can serve
as the identity in "three collinear points sum to O".)
</details>

<details><summary><b>Q2.</b> On E: y² = x³ + x + 1 over F_13, compute
3P for P = (0, 1), reusing 2P = (10, 7) from §4.</summary>

λ = (7 − 1)/(10 − 0) = 6·10⁻¹; 10⁻¹ = 4 (10·4 = 40 ≡ 1); λ = 24 ≡ 11.
x₃ = 121 − 0 − 10 = 111 ≡ 111 − 104 = 7; y₃ = 11(0 − 7) − 1 = −78 ≡ 0.
3P = (7, 0) — a point with y = 0, so 6P = O: P has order 6.
</details>

<details><summary><b>Q3.</b> Points with y = 0 are exactly the points of
order 2. Why, in one sentence each: geometrically and algebraically?</summary>

Geometrically: the tangent at (x, 0) is vertical, so 2P = O.
Algebraically: −(x, 0) = (x, 0) means P = −P ⇔ 2P = O. There are at
most three such x (roots of the cubic), plus O: E[2] has at most 4
elements — and exactly 4 over an algebraically closed field, matching
E[2] ≅ (ℤ/2)² (module 07).
</details>

<details><summary><b>Q4.</b> Verify that j is invariant under the
substitution (x, y) ↦ (u²x, u³y), which maps E onto the curve with
coefficients (u⁴a, u⁶b).</summary>

j depends on a³ and b² only through the ratio a³ : b², and
(u⁴a)³ / (u⁶b)² = u¹²a³/u¹²b² = a³/b². These substitutions are exactly the
isomorphisms between short Weierstrass models (module 08) — you met
them concretely in lab 05's dual-isogeny check, where the composite
φ̂∘φ returned to the start curve only "up to u²".
</details>

## 8. Where this goes

We now have a group attached to every (curve, field) pair. Module 07
asks the arithmetic questions: how many points over F_q, what group
shape, and how hard is the discrete log — the ECDLP that motivates the
entire research program around this course.

**Next:** [Module 07 — Curves over Finite Fields and the ECDLP](07-curves-over-finite-fields.md)
