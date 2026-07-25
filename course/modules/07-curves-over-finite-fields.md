# Module 07 — Curves over Finite Fields and the ECDLP

> **Goal.** The arithmetic of E(F_q): Hasse's bound via the Frobenius
> endomorphism, group structure, torsion, a sketch of Schoof point
> counting, and the discrete logarithm problem with its generic √n
> attacks.
>
> **Labs:** [`lab03_elliptic_curves.py`](../labs/lab03_elliptic_curves.py)
> (counting, orders, structure) and
> [`lab04_ecdlp.py`](../labs/lab04_ecdlp.py) (BSGS, Pollard rho).

## 1. How many points?

Each x contributes 1 + χ(x³ + ax + b) points, where χ is the Legendre
symbol (χ(0) := 1 counts the single y = 0 point... more precisely
1 + χ(v) equals 2, 1, 0 for v a QR, zero, non-QR). Adding O:

  #E(F_p) = p + 1 + Σ_x χ(x³ + ax + b).

If the χ values behaved like independent coin flips, the sum would be
O(√p) — and that heuristic is a theorem:

**Theorem (Hasse, 1933).** #E(F_q) = q + 1 − t with **|t| ≤ 2√q**.

t is the **trace of Frobenius**. Where it comes from: the Frobenius map

  π : (x, y) ↦ (x^q, y^q)

fixes exactly the F_q-rational points (module 05 §3) and satisfies, as a
map on points, the quadratic equation

  **π² − tπ + q = 0**  (t ∈ ℤ),

"like a complex number of absolute value √q" (its eigenvalues are
complex conjugates α, ᾱ with |α| = √q — the elliptic-curve analogue of
the Riemann hypothesis, proved by Hasse). Then
#E(F_q) = #ker(π − 1) = (1 − α)(1 − ᾱ) = q + 1 − t.

Bonus: the same α gives all extension counts —
#E(F_{q^k}) = q^k + 1 − (α^k + ᾱ^k). With #E(F_p) = p + 1 (t = 0,
foreshadowing supersingularity), α = ±i√p and
#E(F_{p²}) = p² + 1 − (−2p) = (p + 1)² — the count lab 03 verifies for
y² = x³ + x, p = 23, and the reason "every supersingular point dies
under multiplication by p + 1" in lab 06's tests.

## 2. Group structure and torsion

**Theorem.** E(F_q) ≅ ℤ/n₁ × ℤ/n₂ with n₁ | n₂ (and n₁ | q − 1).

At most two cyclic factors — the promised "rank ≤ 2" (module 02 §5).
The reason lies in the geometric torsion:

**Theorem.** For gcd(m, q) = 1: E[m] := ker[m] over F̄_q ≅ (ℤ/m)².

E[m] has m² points, matching deg[m] = m². Two independent "directions"
of m-torsion — think of E over ℂ as a torus ℂ/lattice, where m-torsion
is visibly (ℤ/m)². Any *rational* subgroup E(F_q) ⊆ E(F̄_q) inherits
rank ≤ 2.

The case m = ℓ prime is the star: **E[ℓ] ≅ (ℤ/ℓ)² is a 2-dimensional
vector space over F_ℓ**, containing exactly ℓ + 1 subgroups of order ℓ
(count the lines through the origin in a plane: (ℓ² − 1)/(ℓ − 1)).
Each line will be the kernel of one ℓ-isogeny (module 09), which is why
every vertex of the ℓ-isogeny graph has degree ℓ + 1 (module 10) — the
3-regularity your lab 06 verified for ℓ = 2 is a fact about lines in
F_ℓ², decided right here.

**Division polynomials** ψ_m(x, y) ∈ F_q[x, y] vanish exactly on
E[m] \ {O}; they give polynomial handles on torsion (degree ~m²/2 in x).

## 3. Counting fast: Schoof's idea

Brute-force counting (lab 03) is O(p) — useless at p ≈ 2²⁵⁶. Schoof
(1985), the first polynomial-time algorithm:

1. for many small primes ℓ, compute **t mod ℓ** by letting Frobenius act
   on E[ℓ]: check which residue τ satisfies π² + q = τπ on points of
   E[ℓ], computing with polynomials modulo ψ_ℓ (never enumerating
   points);
2. once ∏ℓ > 4√q, recover t by **CRT** (module 04's algorithmic
   pattern, verbatim) inside the Hasse window;
3. #E = q + 1 − t. Complexity O(log^8 q)-ish; the SEA refinements —
   which replace ψ_ℓ by factors coming from the **modular polynomials
   Φ_ℓ** you'll meet in module 09 — make it practical.

You don't need Schoof's internals later; you need its *shape*: local
information at each small ℓ (action on E[ℓ]) glued globally by CRT — the
same shape as Pohlig–Hellman below and half of isogeny-based
cryptanalysis.

## 4. The ECDLP

**Problem.** Given P of order n and Q ∈ ⟨P⟩, find d with Q = dP.

Computing dP takes O(log d) additions (double-and-add). Inverting it is
the hard direction, the basis of ECDH key exchange and ECDSA signatures
and the object of study of this repository's research program.

**Generic attacks** (only use the group operation — lab 04 implements
all three):

* brute force: O(n);
* **baby-step giant-step**: write d = im − j, m = ⌈√n⌉; precompute
  Q + jP for j < m (babies), walk i·mP (giants), match. O(√n) time
  *and* memory;
* **Pollard's rho**: pseudorandom walk Xᵢ = aᵢP + bᵢQ; a collision
  (birthday paradox: expected ~√(πn/2) steps) gives a linear relation
  revealing d. O(√n) time, O(1) memory — the real-world attack. Lab 04's
  demo shows the √n scaling on live curves.
* **Pohlig–Hellman**: if n = ∏ℓᵉ, solve d mod each ℓᵉ inside the small
  subgroups and CRT — so ECDLP is only as hard as the *largest prime
  factor* of n. Hence standardized curves have n = (tiny cofactor) ×
  (256-bit prime).

**Theorem (Shoup 1997).** Any generic-group algorithm needs Ω(√n) group
operations. So on a well-chosen curve, 2¹²⁸ work for n ≈ 2²⁵⁶ — unless
an attack uses *non-generic* structure of the curve. None is known for
well-chosen curves; whether hidden exploitable structure exists is
exactly the open question this course's host repository probes. Contrast
F_p^×: index calculus exploits the *factorization of integers* lifted
from the group and achieves subexponential time, which is why RSA/DH
moduli are 3072-bit while EC keys are 256-bit. No usable analogue of
"factorization" is known on a random elliptic curve.

Also record the **quantum** caveat: Shor's algorithm solves ECDLP in
polynomial time on a large quantum computer — the reason
*isogeny-based* cryptography (modules 09–11) replaces "hidden exponent"
with "hidden path in a graph".

## 5. Self-check

<details><summary><b>Q1.</b> p = 61, so #E ∈ [62 − 15.6, 62 + 15.6] =
[47, 77]. Lab 03's demo curve had #E = 50. What are the possible group
structures for a curve of order 50?</summary>

50 = 2·5²; n₁ | n₂ and n₁ | 60. Options: ℤ/50 (cyclic) or ℤ/5 × ℤ/10.
Both have n₁ | q − 1 = 60. Lab 03 reported ℤ/1 × ℤ/50, i.e. cyclic. To
distinguish empirically: count 5-torsion points found among random
samples (25 ⇒ full E[5] is rational ⇒ non-cyclic).
</details>

<details><summary><b>Q2.</b> Why does n₁ | q − 1?</summary>

E[n₁] ⊆ E(F_q) (both factors contain ℤ/n₁). The **Weil pairing** — a
bilinear map e : E[m] × E[m] → μ_m onto the m-th roots of unity,
non-degenerate and Galois-equivariant — then forces μ_{n₁} ⊆ F_q^×, i.e.
n₁ | q − 1. (The Weil pairing is also the tool behind the MOV attack,
which drags ECDLP into a finite field — devastating exactly when
q^k ≡ 1 (mod n) for small k... which supersingular curves over F_p
satisfy with k ≤ 6, a first hint that supersingular curves are *bad*
for ECDLP yet — module 10 — perfect for isogeny walks, where the
pairing doesn't help the attacker.)
</details>

<details><summary><b>Q3.</b> Estimate rho's step count for n ≈ 2⁶⁴ at
10⁹ group ops/second.</summary>

√(π·2⁶⁴/2) ≈ 1.25·2³² ≈ 5.4·10⁹ steps ≈ 5.4 s. This is why 64-bit
"toy" curves are casually breakable, 128-bit curves (√n = 2⁶⁴ ≈ 10¹⁹ ≈
600 years at 10⁹/s) are for hobby attackers with clusters, and 256-bit
curves are out of reach (2¹²⁸ steps ≈ 10²² years). Feel the exponent.
</details>

<details><summary><b>Q4.</b> Frobenius on E/F_p satisfies
π² − tπ + p = 0. For a point P ∈ E(F_{p²}), express the F_{p²}-point
count using t and check it against §1's computation.</summary>

α, ᾱ = eigenvalues; #E(F_{p²}) = p² + 1 − (α² + ᾱ²) =
p² + 1 − (t² − 2p). Sanity: t = 0 gives (p² + 1 + 2p) = (p + 1)². ✓
</details>

## 6. Where this goes

We can now count, structure, and attack curve groups. Module 08
reorganizes curves by their *maps to themselves* (endomorphisms) — the
classification that produces the word "supersingular" — and module 09
finally builds maps *between* curves.

**Next:** [Module 08 — j-Invariants, Twists, Endomorphisms, Supersingularity](08-endomorphisms-supersingular.md)
