# Module 01 — Integers, Divisibility, and Modular Arithmetic

> **Goal.** Build complete fluency with arithmetic in ℤ/nℤ — the number
> system underneath every finite field, every curve, and every isogeny in
> this course.
>
> **Lab:** [`lab01_arithmetic.py`](../labs/lab01_arithmetic.py)

## 1. Divisibility and the gcd

For integers a, b we say **a divides b** (written a | b) if b = ac for
some integer c. The **greatest common divisor** gcd(a, b) is the largest
integer dividing both.

The **Euclidean algorithm** computes it by repeated division with
remainder, using the invariant gcd(a, b) = gcd(b, a mod b):

```text
gcd(240, 46): 240 = 5·46 + 10 → 46 = 4·10 + 6 → 10 = 1·6 + 4
            → 6 = 1·4 + 2 → 4 = 2·2 + 0   ⇒ gcd = 2
```

Running the divisions backwards expresses the gcd as an integer
combination — **Bézout's identity**, the single most-used fact in this
course:

**Theorem (Bézout).** For all integers a, b there exist x, y with
ax + by = gcd(a, b).

The *extended* Euclidean algorithm (`xgcd` in lab 01) computes x and y
alongside the gcd. For 240, 46: `240·(−9) + 46·47 = 2`.

## 2. Congruences and ℤ/nℤ

Fix n ≥ 1. We write **a ≡ b (mod n)** when n | (a − b). Congruence mod n
is an equivalence relation compatible with + and ×, so the n classes

  ℤ/nℤ = { 0̄, 1̄, …, (n−1)‾ }

form a number system where you add and multiply representatives and
reduce mod n. Two mental models, both useful later:

* **clock arithmetic** — the numbers wrap around (see the *Modular
  playground* tab of the [interactive explorer](../interactive/));
* **remainder projection** — the map ℤ → ℤ/nℤ forgets everything about
  an integer except its remainder. (In algebra language, module 03: a
  ring homomorphism with kernel nℤ.)

### Worked example

In ℤ/7ℤ: 5 + 4 = 2, 5·4 = 6, 3⁶ = 729 = 104·7 + 1 = 1.

## 3. Inverses: when can you divide?

a is **invertible mod n** iff there is x with ax ≡ 1 (mod n). By Bézout,
this happens **iff gcd(a, n) = 1**: from ax + ny = 1, read x as the
inverse; conversely a common divisor of a and n also divides 1.

So division mod n is not always possible: in ℤ/6ℤ, 2 has no inverse
(2x is always even), and worse, 2·3 ≡ 0 with both factors nonzero
(**zero divisors**). But:

**Corollary.** If p is prime, *every* nonzero class mod p is invertible:
ℤ/pℤ is a **field**, henceforth written **F_p**.

This dichotomy — composite moduli have zero divisors, prime moduli give
fields — is why cryptographic constructions live over primes.

Computing inverses: `modinv(a, p)` via `xgcd`, or (prime modulus only)
via Fermat's little theorem a^(p−2) mod p — module 04.

### Worked example

Inverse of 7 mod 431: xgcd(7, 431) gives 7·308 − 5·431 = 1, so
7⁻¹ ≡ 308 (mod 431). Check: 7·308 = 2156 = 5·431 + 1. ✓

## 4. Fast exponentiation

Computing a^e mod n by e−1 multiplications is hopeless for
cryptographic e (think e ≈ 2²⁵⁶). **Square-and-multiply** uses the
binary expansion of e:

```text
a^13 = a^(1101₂) = ((a² · a)² )² · a      — 5 multiplications, not 12
```

⌊log₂ e⌋ squarings plus at most that many multiplications: O(log e)
work. Burn this loop into your fingers now — the *identical* algorithm
reappears in module 07 as **double-and-add** for computing n·P on an
elliptic curve, with "multiply" replaced by the group law.

## 5. Self-check

<details><summary><b>Q1.</b> Solve 17x ≡ 3 (mod 431).</summary>

gcd(17, 431) = 1, and xgcd gives 17·330 ≡ 1 (mod 431) (check:
17·330 = 5610 = 13·431 + 7 ... recompute: 13·431 = 5603, 5610 − 5603 = 7 ≠ 1,
so 330 is wrong — always verify!). Redo: 431 = 25·17 + 6,
17 = 2·6 + 5, 6 = 1·5 + 1. Back-substitute: 1 = 6 − 5 = 6 − (17 − 2·6)
= 3·6 − 17 = 3(431 − 25·17) − 17 = 3·431 − 76·17. So
17⁻¹ ≡ −76 ≡ 355 (mod 431), and x ≡ 3·355 = 1065 ≡ 1065 − 2·431 = 203.
Check: 17·203 = 3451 = 8·431 + 3. ✓ (The deliberately wrong first answer
is the lesson: *always* multiply back.)
</details>

<details><summary><b>Q2.</b> In ℤ/12ℤ, list the invertible elements and
the zero divisors.</summary>

Invertible: classes coprime to 12 → {1, 5, 7, 11} (each is its own
inverse — try it). Zero divisors: {2, 3, 4, 6, 8, 9, 10}. Together with
0 that's all 12 classes: mod a composite, *every* nonzero class is
either a unit or a zero divisor (true in any finite ring, module 03).
</details>

<details><summary><b>Q3.</b> How many multiplications does
square-and-multiply need for a^(2²⁵⁶) mod n? For a general 256-bit
exponent?</summary>

For 2²⁵⁶ exactly 256 squarings. General 256-bit e: 255 squarings + one
multiply per set bit ≈ 128 on average ⇒ ~383 multiplications. Compare
with ~2²⁵⁶ for the naive method: this gap *is* modern cryptography.
</details>

## 6. Where this goes

* ℤ/pℤ = F_p is the base field of every curve we will draw (module 05).
* `xgcd` powers every field inversion, hence every group-law λ
  (module 06).
* The mod-n wraparound is your first example of a **finite abelian
  group** — formalized next, in module 02.

**Next:** [Module 02 — Groups](02-groups.md)
