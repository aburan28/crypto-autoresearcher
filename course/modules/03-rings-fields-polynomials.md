# Module 03 — Rings, Fields, and Polynomials

> **Goal.** Two operations at once: rings and fields; then polynomials,
> the machine that manufactures new fields from old ones and describes
> every curve and every isogeny map in this course.
>
> **Lab:** the polynomial arithmetic in
> [`lab06_ss_graph.py`](../labs/lab06_ss_graph.py) (`poly_*` functions)
> is this module, executable.

## 1. Rings

A **(commutative) ring** R has two operations: (R, +) is an abelian
group, × is associative/commutative with identity 1, and distributivity
a(b + c) = ab + ac ties them together.

Examples: ℤ; ℤ/nℤ; polynomials R[x]; ℤ[i] = {a + bi}. Non-example under
multiplication only: division may fail.

* a **unit** is an element with a multiplicative inverse; the units form
  a group R^× (e.g. (ℤ/nℤ)^× from module 02);
* a **zero divisor** is a ≠ 0 with ab = 0 for some b ≠ 0;
* an **integral domain** is a ring with no zero divisors (cancellation
  law holds: ab = ac, a ≠ 0 ⇒ b = c).

## 2. Fields

A **field** is a ring where every nonzero element is a unit: you can
divide. ℚ, ℝ, ℂ, and — our fields — F_p = ℤ/pℤ for p prime.

**Characteristic.** The least n with n·1 = 0 (or 0 if none). A field's
characteristic is 0 or a prime p. In characteristic p the **freshman's
dream** is a theorem:

  (a + b)^p = a^p + b^p

because every interior binomial coefficient C(p, k) is divisible by p.
Consequence: **x ↦ x^p is a ring homomorphism** — the *Frobenius* — and
on finite fields it is bijective, hence an automorphism. Remember this;
Frobenius is arguably the protagonist of the entire course (modules 05,
07, 08).

**Finite fields preview** (proved in module 05): a finite field has
order p^n; there is exactly one for each p^n; F_p ⊆ F_{p²} ⊆ F_{p⁴} ⋯

## 3. Polynomial rings

F[x] = polynomials in x with coefficients in a field F. Its arithmetic
mirrors ℤ astonishingly well:

| ℤ | F[x] |
| --- | --- |
| absolute value | degree |
| division with remainder | polynomial division: f = qg + r, deg r < deg g |
| Euclidean algorithm, Bézout | identical, verbatim |
| primes | irreducible polynomials |
| unique factorization | unique factorization |
| ℤ/pℤ is a field | F[x]/(f) is a field for irreducible f |

The last row is the field-manufacturing machine of §5.

**Roots and factors.** f(a) = 0 ⟺ (x − a) | f. Hence a polynomial of
degree n over a *field* (or any integral domain) has **at most n roots**.
This innocuous fact does heavy lifting:

* it proves F_p^× is cyclic (module 04);
* it caps the m-torsion of an elliptic curve at m² points (module 07);
* "x^q − x is exactly the product of (x − c) over all c ∈ F_q" turns
  root-finding into gcd computations — literally how lab 06 finds the
  2-torsion of supersingular curves.

## 4. Evaluation, kernels, quotients

Fix a ∈ F. Evaluation f ↦ f(a) is a ring homomorphism F[x] → F with
kernel (x − a) = multiples of (x − a). Quotients by kernels work as for
groups; the objects F[x]/(f) are "polynomials mod f", where you reduce
every result by dividing by f and keeping the remainder.

## 5. Building fields: F[x]/(irreducible)

**Theorem.** If f ∈ F[x] is irreducible of degree n, then K = F[x]/(f)
is a field containing F, of dimension n as an F-vector space, in which f
has a root (namely x̄, the class of x).

*Why a field:* for g ≢ 0 mod f, gcd(g, f) = 1 by irreducibility, and
Bézout gives ug + vf = 1, i.e. u = g⁻¹ mod f. The same `xgcd` from
lab 01, now with polynomials.

### Worked example 1: ℂ from ℝ

x² + 1 is irreducible over ℝ; ℝ[x]/(x² + 1) = {a + bx̄} with x̄² = −1.
That *is* ℂ, constructed rather than postulated.

### Worked example 2: F₄ from F₂

x² + x + 1 is irreducible over F₂ (no roots: 0, 1 both fail). So
F₄ = F₂[x]/(x² + x + 1) = {0, 1, ω, ω + 1} with ω² = ω + 1. Check
ω³ = 1: the multiplicative group is cyclic of order 3. Note F₄ is *not*
ℤ/4ℤ (which has zero divisor 2).

### Worked example 3: the field where isogenies live

For p ≡ 3 (mod 4), −1 is a non-square mod p (module 04), so x² + 1 is
irreducible over F_p and

  **F_{p²} = F_p[i]/(i² = −1) = {a + bi}**

— "complex numbers mod p". This is `Fp2` in lab 02 and the coefficient
field of every supersingular curve in modules 10–11.

## 6. Self-check

<details><summary><b>Q1.</b> Factor x² + 1 over F₅ and over F₇. What
property of p decides?</summary>

Over F₅: 2² = 4 ≡ −1, so x² + 1 = (x − 2)(x + 2). Over F₇: squares are
{1, 2, 4}; −1 = 6 is not among them, so x² + 1 is irreducible. Decider:
whether −1 is a quadratic residue, i.e. p mod 4 (module 04).
</details>

<details><summary><b>Q2.</b> In F₄ as built above, compute (ω + 1)² and
verify it equals ω. Then verify Frobenius x ↦ x² permutes {ω, ω+1}.</summary>

(ω+1)² = ω² + 1 (freshman's dream, char 2) = (ω + 1) + 1 = ω. So
Frobenius swaps ω ↔ ω + 1 and fixes F₂ — the Galois group of F₄/F₂ in
action.
</details>

<details><summary><b>Q3.</b> Why does "degree n ⇒ at most n roots" fail
over ℤ/8ℤ? Give a quadratic with four roots.</summary>

ℤ/8ℤ has zero divisors, so (x − a)(x − b) = 0 doesn't force a factor to
vanish. x² − 1 has roots 1, 3, 5, 7.
</details>

<details><summary><b>Q4.</b> Show that a *finite* integral domain is a
field.</summary>

For a ≠ 0, the map x ↦ ax is injective (cancellation), hence surjective
by finiteness, so ax = 1 for some x.
</details>

## 7. Where this goes

Module 04 harvests concrete number theory from these structures
(Fermat, Euler, CRT, quadratic residues). Module 05 applies §5 to build
all finite fields and studies Frobenius seriously. And the polynomial
mindset — curves as polynomial equations, maps as rational functions,
kernels as polynomial gcds — *is* algebraic geometry in the small, which
is all an isogeny ever was.

**Next:** [Module 04 — The Number Theory Toolkit](04-number-theory.md)
