# Module 08 — j-Invariants, Twists, Endomorphisms, Supersingularity

> **Goal.** Sort curves by their symmetries. Isomorphisms and the
> j-invariant; twists; the endomorphism ring; and the
> ordinary/supersingular dichotomy that names half of this course.
>
> **Lab:** lab 03 (`j_invariant`, `quadratic_twist`, and the
> supersingular counts in its self-checks); lab 06's
> `is_supersingular_probably`.

## 1. Isomorphisms and j

The only maps between short Weierstrass models that preserve the shape
and O are

  (x, y) ↦ (u²x, u³y), u ∈ K^×, sending (a, b) to (u⁴a, u⁶b)
  (read in the target's coordinates: a′ = u⁴a, b′ = u⁶b).

**Theorem.** Over an algebraically closed field, E ≅ E′ ⟺ j(E) = j(E′),
with j = 1728·4a³/(4a³ + 27b²) as in module 06.

Given any j₀ there is a curve with that j-invariant, e.g. (lab 06's
`curve_from_j`): for j₀ ≠ 0, 1728, take c = j₀(1728 − j₀) and

  E: y² = x³ + 3c x + 2c(1728 − j₀);  j = 0: y² = x³ + 1; 
  j = 1728: y² = x³ + x.

So over F̄_p, "a curve" = "a j-invariant": one scalar (in F_{p²}, it
turns out, for the supersingular ones) names the whole object. The
isogeny graphs of module 10 take these scalars as vertices.

## 2. Twists: same j, different group

Over a *non*-closed field the j-invariant is coarser than isomorphism.
For a non-square d ∈ F_q^×, the **quadratic twist**

  E^(d) : y² = x³ + a d² x + b d³

has j(E^(d)) = j(E) but is not F_q-isomorphic to E (u would need
u² = d). Point counts are complementary:

  **#E(F_q) + #E^(d)(F_q) = 2q + 2**  (traces t and −t)

— for each x, the twisted cubic value flips its QR status unless zero,
so points migrate from one curve to the other. Lab 03 checks this
identity exactly. For j ≠ 0, 1728 the twist is the *only* ambiguity:
each j has exactly two F_q-forms (j = 0 has six, j = 1728 has four —
the extra-automorphism curves again).

Working consequence (used silently by lab 06): a construction that only
knows j may land on "the wrong twist", but any statement invariant under
twisting — like *which j's are 2-isogeny-adjacent* — comes out right
regardless. That's why `curve_from_j` never needs to care.

## 3. The endomorphism ring

An **endomorphism** is an isogeny E → E (plus 0); they form a ring
End(E) under + (pointwise) and ∘ (composition). Always present:

* ℤ, as m ↦ [m] (multiplication maps);
* over F_q: the **Frobenius π**, with π² − tπ + q = 0 (module 07).

If t² ≠ 4q, π ∉ ℤ (its "eigenvalues" are irrational), so End(E) is
strictly bigger than ℤ: finite-field curves always have extra
symmetries. How much bigger is a trichotomy — and over finite fields
only two of the three branches occur:

**Theorem (Deuring).** For E over a finite field, End(E) (over F̄_p) is
either
* an **order in an imaginary quadratic field** ℚ(√(t² − 4q)) —
  E is **ordinary**; or
* a **maximal order in the quaternion algebra B_{p,∞}** (a
  4-dimensional *non-commutative* algebra over ℚ ramified exactly at p
  and ∞) — E is **supersingular**.

(The characteristic-0 branch, End = ℤ, and the CM branch are the ℂ
story; reduction mod p can only gain symmetries.)

Don't fear the quaternion algebra yet; here is the honest minimum:
B_{p,∞} = ℚ + ℚi + ℚj + ℚk with i² , j² negative rationals depending
on p and ji = −ij. "Maximal order" = a lattice ℤ-span of 4 elements,
closed under multiplication, as large as possible — the quaternionic
analogue of a ring of integers. What matters operationally: END(E) IS
4-DIMENSIONAL AND NON-COMMUTATIVE for supersingular E, versus
2-dimensional commutative for ordinary E. Twice the symmetries, none of
the commuting — this single line explains most of module 10–11's
behavior (and module 11's Deuring correspondence turns it into a
signature scheme, SQIsign).

## 4. Supersingular: five equivalent definitions

For E over F̄_p, p > 3, the following are equivalent, and such E are
called **supersingular** (else **ordinary**):

1. E[p] = {O} — the p-torsion is trivial (ordinary: E[p] ≅ ℤ/p);
2. the multiplication-by-p map [p] is purely inseparable;
3. **t ≡ 0 (mod p)** for E over F_q (for q = p: t = 0 exactly, by
   Hasse |t| ≤ 2√p < p for p ≥ 5, so **#E(F_p) = p + 1**);
4. End(E) is a maximal order in a quaternion algebra (non-commutative);
5. π and "everything else" fail to commute: End(E) ⊋ any commutative
   subring containing π.

Intuition for 1↔3: over F_p, #E(F_p) = p + 1 − t ≡ 1 − t (mod p); if
t ≡ 0 the group order is prime to... no — the *geometric* p-torsion
statement is deeper: reducing the mod-p world kills the p-part of the
torus picture either partially (ordinary, one ℤ/p survives) or
completely (supersingular, nothing survives). "Supersingular" ≠
"singular curve": these curves are perfectly smooth; the name is
historical ("having singularly many symmetries").

### Recognition rules you'll actually use

* p ≡ 3 (mod 4): **y² = x³ + x (j = 1728) is supersingular**.
  Proof for the culture (and lab 03's exercise 3.1): with
  f(x) = x³ + x odd and χ(−1) = −1 (module 04!), the counts at x and −x
  cancel: Σχ(f(x)) = 0, so #E = p + 1. ∎
* p ≡ 2 (mod 3): **y² = x³ + 1 (j = 0) is supersingular** (same trick
  with cube residues).
* These are lab 06's `starting_j` — the entry doors into the
  supersingular graph.

## 5. Where supersingular curves live: F_{p²} and the count

**Theorem.** Every supersingular j-invariant lies in **F_{p²}**.
(Sketch: π² has degree p² and, with t ≡ 0-type constraints, acts as a
scalar; a curve isomorphic to its own p²-power conjugate has
j^(p²) = j, i.e. j ∈ F_{p²} — module 05's membership test.)

So the infinite F̄_p collapses: the whole supersingular world is
defined over one quadratic field. Moreover, up to isomorphism it is
*finite and small*:

**Theorem (Eichler–Deuring mass formula, exact form).** The number of
supersingular j-invariants in characteristic p is

  ⌊p/12⌋ + ε, ε = 0, 1, 1, 2 for p ≡ 1, 5, 7, 11 (mod 12).

Lab 06 verified this on the nose: p = 83 ⇒ 8, p = 431 ⇒ 37,
p = 1013 ⇒ 85. About p/12 vertices — big enough to hide in
(p ≈ 2²⁵⁶ ⇒ ~2²⁵² vertices), small enough to be one field's worth.

Ordinary curves, by contrast, scatter across ~4p j-invariants (over
F_p, organized into CM classes by their quadratic orders) — a different,
commutative world with its *own* isogeny graphs ("volcanoes"), used by
CSIDH (module 11) but not our main road.

## 6. Automorphisms: the j = 0 and j = 1728 quirks

Aut(E) (isomorphisms E → E) is generically {±1}. Exceptions:

* j = 1728: also (x, y) ↦ (−x, iy), i² = −1 — Aut ≅ ℤ/4;
* j = 0: also (x, y) ↦ (ζx, −y), ζ³ = 1 — Aut ≅ ℤ/6.

Effect you already saw in data (lab 06, p = 83): these vertices fold
several isogenies onto each other, producing loops/multi-edges and the
*only* asymmetries of the 2-isogeny multigraph — which is why
`verify_graph` excuses exactly those two vertices when checking edge
symmetry.

## 7. Self-check

<details><summary><b>Q1.</b> #E(F_p) = p + 1 for a supersingular curve
over F_p. Why does that make it catastrophically weak for ECDLP?</summary>

The group order p + 1 has no reason to have a big prime factor
(choose-your-prime attacks), but worse: t = 0 means the embedding
degree is tiny — π² = −p gives p² ≡ 1 mod n for n | p + 1... via the
Weil/Tate pairing (MOV/Frey–Rück), ECDLP transfers into F_{p²}^×, where
index calculus is subexponential. Moral of the whole course: the same
curves that are *broken* as ECDLP groups are *golden* as isogeny-graph
vertices — the hardness lives in the graph, not the group.
</details>

<details><summary><b>Q2.</b> Compute the number of supersingular
j-invariants for p = 101, 103, and 2³¹ − 1 (mod-12 arithmetic
only).</summary>

101 ≡ 5 (mod 12): ⌊101/12⌋ + 1 = 8 + 1 = 9.
103 ≡ 7: 8 + 1 = 9.
2³¹ − 1 = 2147483647 ≡ 7 (mod 12) (2³¹ ≡ 8): ⌊(2³¹−1)/12⌋ + 1 =
178956970 + 1 = 178956971.
</details>

<details><summary><b>Q3.</b> Take j ≠ 0, 1728. Are E and its quadratic
twist E^(d) isomorphic over F_p? Over F_{p²}? And what changes at
j = 1728 when p ≡ 3 (mod 4)?</summary>

Generic j: over F_p, no — an isomorphism needs u with u⁴a = ad² and
u⁶b = bd³, forcing u² = d, unsolvable for a non-square d. Over F_{p²}:
yes — every F_p element becomes a square there (module 05 §2); twists
always die in a quadratic extension. At j = 1728 (b = 0), only the
u⁴ = d² constraint survives, and u² = −d works too; for p ≡ 3 (mod 4),
−d IS a square, so the "quadratic twist" is secretly isomorphic to E
over F_p — the genuinely new forms of j = 1728 are *quartic* twists
(Aut ≅ ℤ/4). The special curves are special everywhere.
</details>

<details><summary><b>Q4.</b> True or false: a supersingular curve
defined over F_p has End_{F_p}(E) commutative even though End_{F̄_p}(E)
is a quaternion order.</summary>

True — and important. F_p-rational endomorphisms must commute with π,
which pins them into ℤ[π] ≅ ℤ[√−p]-ish, an imaginary quadratic order.
The full quaternionic symmetry only appears over F_{p²}. CSIDH
(module 11) lives precisely in this commutative F_p-sliver of the
supersingular world; the Delfs–Galbraith attack exploits the same
subfield structure.
</details>

## 8. Where this goes

You can now say precisely what a supersingular curve is, count them,
recognize one, and name their symmetry algebra. Module 09 finally
constructs the maps *between* curves — isogenies, kernels, Vélu — and
module 10 assembles all ⌊p/12⌋ + ε vertices into the expander graph
whose walks are the cryptography.

**Next:** [Module 09 — Isogenies](09-isogenies.md)
