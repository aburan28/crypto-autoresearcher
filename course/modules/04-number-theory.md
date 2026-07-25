# Module 04 — The Number Theory Toolkit

> **Goal.** The classical results you will reach for daily: Fermat and
> Euler, CRT, the cyclic structure of F_p^×, quadratic residues, and
> square roots mod p. Each one maps to a function you already ran in
> [`lab01_arithmetic.py`](../labs/lab01_arithmetic.py).

## 1. Fermat and Euler

**Fermat's little theorem.** For p prime and p ∤ a: a^(p−1) ≡ 1 (mod p).

*Proof.* Lagrange (module 02) applied to a ∈ F_p^×, a group of order
p − 1. ∎

**Euler's theorem.** For gcd(a, n) = 1: a^φ(n) ≡ 1 (mod n), where φ(n) =
|(ℤ/nℤ)^×| counts residues coprime to n.

Uses everywhere:

* fast inversion in F_p: a⁻¹ = a^(p−2) (how lab 02's `Fp.inverse` works);
* primality testing: if a^(n−1) ≢ 1 (mod n), n is composite — refined
  into Miller–Rabin (`is_probable_prime`);
* every exponent in a finite field can be reduced mod (group order) —
  silently used each time a lab computes x^((q−1)/2).

## 2. The Chinese Remainder Theorem

**CRT.** If n = n₁n₂⋯n_k with pairwise coprime n_i, then

  ℤ/nℤ ≅ ℤ/n₁ℤ × ⋯ × ℤ/n_kℤ,  a ↦ (a mod n₁, …, a mod n_k)

as rings, and the inverse map is computable (Bézout again — `crt` in
lab 01).

*Worked example (Sunzi, ~4th century).* x ≡ 2 (3), x ≡ 3 (5), x ≡ 2 (7):
x ≡ 23 (mod 105).

Two consequences worth internalizing now:

* φ is multiplicative on coprime parts, φ(p^k) = p^k − p^(k−1);
* **an algorithmic pattern**: to solve a problem mod a composite, solve
  it mod each prime power and glue with CRT. Pohlig–Hellman (lab 04,
  exercise 4.2) does this to discrete logs; Schoof's algorithm
  (module 07) does it to point counting, computing #E mod ℓ for many
  small primes ℓ. When you meet "for each small ℓ, look at E[ℓ]" in
  module 09 — that is CRT thinking.

## 3. F_p^× is cyclic

**Theorem.** The multiplicative group of any finite field is cyclic.
A generator g of F_p^× is a **primitive root** mod p.

*Proof sketch.* For each d | p−1, elements of order dividing d are roots
of x^d − 1, so there are at most d of them (module 03, at-most-n-roots).
A counting argument (with φ) then forces exactly φ(d) elements of order
exactly d for every d | p − 1; in particular φ(p−1) ≥ 1 generators. ∎

*Example.* p = 13: g = 2 works: 2, 4, 8, 3, 6, 12, 11, 9, 5, 10, 7, 1 —
all twelve nonzero residues. (Try this in the interactive *Modular
playground*: pick n = 13 and watch powers of 2 sweep the circle.)

This single theorem is why "discrete logarithm" is well-posed in F_p^×,
and its failure to have small-index shortcuts on elliptic curves is why
this course's host repository exists.

## 4. Quadratic residues

a ∈ F_p^× is a **quadratic residue (QR)** if a = x² has a solution.
Squaring x ↦ x² has kernel {±1} (module 02), so exactly **(p−1)/2**
residues are QRs and (p−1)/2 are not.

**Legendre symbol.** (a/p) = +1 if a is a QR, −1 if not, 0 if p | a.

**Euler's criterion.** (a/p) ≡ a^((p−1)/2) (mod p).

*Proof.* Write a = g^k for a primitive root g. Then a^((p−1)/2) =
(g^((p−1)/2))^k = (−1)^k, since g^((p−1)/2) is a square root of 1 that
can't be +1 (g has full order). And a is a QR iff k is even. ∎

Key special values:

* **(−1/p) = +1 ⟺ p ≡ 1 (mod 4)** — this decides whether F_{p²} can be
  written as F_p[i] (module 03) and whether y² = x³ + x is supersingular
  (module 08);
* (a/p)(b/p) = (ab/p): the symbol is multiplicative — non-residue ×
  non-residue = residue;
* quadratic reciprocity (stated for culture, not needed later): for odd
  primes p ≠ q, (p/q)(q/p) = (−1)^((p−1)/2 · (q−1)/2).

**Why we care, concretely:** a point of an elliptic curve exists over
x₀ iff x₀³ + ax₀ + b is a QR. Counting points (lab 03's
`count_points_Fp`) is literally summing Legendre symbols:

  #E(F_p) = p + 1 + Σₓ ( (x³ + ax + b) / p ).

## 5. Square roots mod p: Tonelli–Shanks

Knowing a is a QR, find x with x² = a.

* **p ≡ 3 (mod 4)** (three quarters of this course's primes): 
  x = a^((p+1)/4). Check: x² = a^((p+1)/2) = a · a^((p−1)/2) = a. ✓
* **p ≡ 1 (mod 4)**: no closed form; **Tonelli–Shanks** writes
  p − 1 = q·2^s and walks the 2-Sylow subgroup: maintain candidates
  (r, t) with r² = a·t where t has 2-power order; repeatedly multiply by
  a non-residue's powers to strip t's order down to 1. O(log² p)
  multiplications; `sqrt_mod_p` in lab 01 is a full implementation.

The same algorithm runs verbatim in any finite field once you can find
a non-square — lab 02 runs it in F_{p²}, where finding a non-square
needs care because *every* element of F_p becomes a square in F_{p²}
(module 05).

## 6. Self-check

<details><summary><b>Q1.</b> Compute 2^431 mod 431 without a computer.
What does the answer tell you?</summary>

If 431 is prime, Fermat gives 2^430 ≡ 1, so 2^431 ≡ 2. (It is prime.)
The converse fails in general — Carmichael numbers like 561 pass a^n ≡ a
for all a — which is why Miller–Rabin strengthens this test.
</details>

<details><summary><b>Q2.</b> Solve x ≡ 1 (mod 4), x ≡ 2 (mod 9),
x ≡ 3 (mod 25).</summary>

Stepwise: x = 29 satisfies the first two (29 = 4·7+1 ✓, 29 = 27+2 ✓);
seek x = 29 + 36k ≡ 3 (mod 25) ⇒ 4 + 11k ≡ 3 ⇒ 11k ≡ −1 ≡ 24 (mod 25);
11⁻¹ ≡ 16 (11·16 = 176 = 7·25 + 1), k ≡ 16·24 = 384 ≡ 9 (mod 25);
x = 29 + 324 = 353. Check: 353 = 88·4+1 ✓, 353 = 39·9+2 ✓,
353 = 14·25+3 ✓.
</details>

<details><summary><b>Q3.</b> Is 2 a QR mod 431? Predict, then verify
with Euler's criterion in the lab.</summary>

The supplementary law says (2/p) = +1 iff p ≡ ±1 (mod 8); 431 = 8·54−1
≡ 7 ≡ −1, so yes. Lab 01's demo confirms: sqrt(2) ≡ 243 (mod 431).
</details>

<details><summary><b>Q4.</b> For p ≡ 3 (mod 4), show that exactly one of
a, −a is a QR (a ≠ 0). Why does this matter for curves?</summary>

(−a/p) = (−1/p)(a/p) = −(a/p). Consequence: on y² = x³ + x over such p,
x and −x contribute exactly two points between them (module 08 uses this
to prove #E = p + 1: supersingularity!).
</details>

## 7. Where this goes

You now hold every scalar tool: gcds, inverses, CRT, symbols, square
roots. Module 05 assembles them into finite fields F_{p²} (and beyond),
and from module 06 onward the same toolkit runs with x³ + ax + b in
place of a.

**Next:** [Module 05 — Finite Fields](05-finite-fields.md)
