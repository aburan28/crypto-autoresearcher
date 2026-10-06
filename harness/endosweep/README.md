# endosweep — an endomorphism-ring sweeper for scalar-multiplication decompositions

`python -m harness.endosweep` enumerates, for every target group it knows,
**every way the endomorphism ring can be used to shorten a variable-base
scalar multiplication**, reduces each candidate's relation lattice exactly,
costs it under one explicit operation-count model, labels what it finds
with the literature construction it reproduces — or with *no literature
match found* — and then **builds the winning endomorphism on the real curve
and verifies it on points** (`harness.endosweep.explicit`). It is a
hypothesis generator with certificates, not a benchmark: a configuration
that beats the known ones on paper is a candidate for an implementation and
a measured experiment, nothing more.

Run:

```sh
python -m harness.endosweep --out-dir outputs/endosweep                       # every target
python -m harness.endosweep --targets "CryptoPro-B,FourQ,genus-2" --max-dim 8
python -m harness.endosweep.explicit --target "GOST CryptoPro-B"              # build + verify the best chain
python -m harness.endosweep.explicit --target "GOST CryptoPro-B" --element 0,1 # a chosen element (omega: 5 then 31)
python -m harness.endosweep.corpus --std-curves /path/to/std-curves --out-dir outputs/corpus
python -m harness.endosweep.fourq                                            # FourQ's maps, evaluated and verified
python -m harness.endosweep.genus2 --bits 9                                   # genus-2 rank-4 structure, toy proof
python -m harness.endosweep.toyverify --bits 26                               # explicit maps on toy curves
python -m pytest -q tests/test_endosweep.py
```

`python-flint` is optional; with it installed the explicit builder factors
division polynomials and computes `x^p mod f_ell` at C speed, which is what
makes steps up to ell ≈ 50 and class-number-24 chains practical.

## What a decomposition can and cannot do (the bound the sweep is built on)

Let the cheap endomorphisms used as generators be `g_1 = 1, g_2, ..., g_d`,
acting on the prime-order subgroup as scalars `λ_i`.  A decomposition writes
`k ≡ Σ k_i λ_i (mod n)` with `|k_i| < 2^c`; the multi-scalar multiplication
then needs about `c` doublings instead of `log2 n`.  Three facts bound `c`:

1. **Rank.**  All generators live in `R = End(E) ⊗ Q`, of Z-rank `r` (2 for an
   ordinary elliptic curve, 2 for every commutative subring of a supersingular
   one — non-commuting endomorphisms have no common eigenvector, so they
   cannot both act as scalars on one cyclic subgroup; `2g` for a Jacobian with
   CM by a degree-`2g` field).  Write each generator in a Z-basis of `R`; let
   `H` be the largest coordinate that appears (the *height*).  Every sum
   `Σ k_i g_i` is an element of `R` with coordinates at most `d·2^c·H`, and
   `n` distinct residues must be reachable, so

   > `(d · 2^c · H)^r ≳ n`, i.e. `c ≳ (log2 n)/r − log2 H − log2 d`.

   With `H = O(1)` this is the familiar `c ≈ (log2 n)/r`: 2-GLV on an
   ordinary curve, 4-dimensional on a Jacobian with quartic CM.

2. **Height is the only way past the rank, and it is paid for in degree.**
   Any endomorphism of degree `ℓ` has height about `sqrt(ℓ)` in the ring, so
   lowering `c` by one bit through a generator costs a factor 4 in degree.
   A *separable* map of degree `ℓ` costs `Θ(ℓ)` field operations (Vélu) or
   `Θ(sqrt ℓ)` (√élu), so a single map can never supply a useful height.  A
   *chain* can: a closed walk of `k` steps on the `ℓ`-isogeny graph that
   returns to `E` is an endomorphism of degree `ℓ^k` and height `≈ ℓ^{k/2}`
   evaluated at cost `k · cost(ℓ-step)`.  The sweep calls such a generator an
   **isogeny-cycle pump**; its price is `2·cost(ℓ-step)/log2 ℓ` field
   multiplications **per bit of height**, i.e. per doubling saved.  With the
   SIDH-literature x-only counts (2-isogeny 4M, 3-isogeny 4M+2S) that is
   8.0 M/bit and 7.1 M/bit, against 6–7.4 M for a doubling: paid pumps sit at
   parity with the doublings they replace, and the sweep's job is to show
   exactly where under an explicit cost table.

3. **Frobenius is a free pump.**  Over `F_{p^m}` the `p`-power Frobenius has
   degree `p` and height `≈ sqrt p` but costs nothing (a conjugation in a
   suitable basis).  That single fact is the whole of GLS, Longa–Sica 4-GLV,
   FourQ, the Galbraith–Scott G2 decomposition and the τ-adic expansion on
   Koblitz curves: `m` free generators of exponentially growing height drive
   `c` down to `(log2 n)/(rm)` — or, for tiny `p`, to a constant.

So the search space is `{rank} × {free pumps} × {paid pumps} × {cost table}`,
and that is exactly what `sweep.py` enumerates.

## The case the bound does not forbid: class number above one

On a curve with CM discriminant `D_K` and class number `h > 1`, no single
small prime ideal is principal, so the cheapest endomorphism is a **chain
through the class group**: a primitive element of norm `∏ ℓ^e` generates
`∏ 𝔭_ℓ^e`, a walk of `e` cyclic `ℓ`-isogenies per prime through neighbouring
curves that ends back at `E`, costing the sum of the step costs whether or
not the individual prime ideals are principal.  The inventory therefore runs
to eight times the minimum non-scalar degree `(|D_K|+1)/4` and prices every
element as a chain; this is what makes GOST CryptoPro-B (`D_K = −619`,
`h = 5`, minimum degree 155) come out at `4+ω` of degree `5²·7` for about
53 M rather than at a prime-norm element as one large Vélu map, and what
finds the `7·11³` chain on Tom-521 (`h = 24`).

## Modules

| module | does |
|---|---|
| `quadorder.py` | exact arithmetic in imaginary quadratic orders: norm/trace/height in the reduced basis `{1, ω}`, elements of a given norm, unit groups, the Kronecker symbol, **`small_discriminant_scan`** (one perfect-square test per fundamental discriminant — certifies `|D_K| > bound` without factoring `t²−4q`), **`smallest_principal_power`** (class order of a prime ideal by composition of binary quadratic forms, then the generator of its first principal power by Cornacchia with Hensel-lifted square roots). |
| `lattice.py` | exact LLL over `Fraction`, the relation lattice `{v : Σ v_i λ_i ≡ 0 (n)}`, Babai decomposition with a **provable** coefficient bound (sum of half ∞-norms of the reduced basis) and an empirical maximum over random scalars. |
| `costmodel.py` | one table of constants (EFD formula counts for Jacobian/Edwards doubling and addition, the same over `F_{p²}`; SIDH-literature x-only isogeny-step counts; two genus-2 Jacobian models, one measured from `genus2.py`'s affine Cantor arithmetic and one marked as an assumption) and the interleaved width-w NAF multi-scalar cost with per-generator tables, batched affine conversion and incremental endomorphism costs. |
| `targets.py` | the registry.  Eighteen deployed curves (secp256k1, P-256/384/521, brainpoolP256r1, SM2, GOST CryptoPro-A/B/C and the 2001 test set, Curve25519, Ed448, Curve1174, Curve41417, E-521, M-511, BN254 G1, BLS12-381 G1) **verified from their constants alone** (n prime, Hasse interval, a point of order divisible by n killed by h·n), structural G2 entries (ψ acts as `[p]`, `r | Φ₁₂(p)`), a synthetic GLS group over `F_{p²}`, synthetic prime-order CM curves for fourteen small discriminants of class number 1–7, FourQ (from `fourq.py`) and synthetic genus-2 Jacobians (from `genus2.py`).  An entry whose constants fail verification is skipped and reported, never swept. |
| `sweep.py` | catalogue (chain-priced inventory, cycle pumps, declared Frobenius-type and higher-order generators) → configurations (GLV pairs; unit × pump and two-pump boxes; Frobenius monomial boxes; power bases of ζ₅/ζ₈; ζ-powers × Frobenius boxes) → exact lattice reduction → cost → ranking → Markdown/JSON report. |
| `explicit.py` | **builds a predicted chain endomorphism on a real curve and verifies it on points.** Division polynomials over `F_p` (python-flint or pure Python); the kernel polynomials of the rational cyclic subgroups of order `ℓ` — by factoring for `ℓ ≤ 7`, by the **Frobenius-eigenvalue method** for larger `ℓ` (`gcd(f_ℓ, x^p·den − x·den + num)` with `(num, den)` the `x([μ]P)` formula, `μ` a root of `x² − tx + p (mod ℓ)`), and the rational roots of `x³ + ax + b` for `ℓ = 2`; Vélu in Kohel's kernel-polynomial form (codomain and evaluation by traces in `F_p[T]/(h)`, no kernel point ever needed — the points live in extension fields); a search over closed walks of the right shape through the isogeny class that prunes only the **dual** of the previous step (identified as `iso ∘ prev = ±[ℓ]`, not by j-invariant); the isomorphism back to `E` (Adleman–Manders–Miller roots, instant at any size); acceptance only if the composite acts on a point of prime order `n` as a predicted scalar; then an end-to-end GLV-2 check. About a second per chain at 256 bits; `7·11³` on a 521-bit curve in a few seconds. |
| `chainsweep.py` | **every chain realisation of the cheap endomorphisms of one curve.** The catalogue of every primitive non-scalar element with norm ≤ `nmax` and prime factors ≤ `lmax` (exact search); every distinct ordering of each element's prime-degree steps, all built on the curve with `explicit.py` (pinned ω eigenvalue, the element itself rather than its conjugate) and verified on points; an operation count that mirrors the crypto repository's two CryptoPro-B chain evaluators statement by statement (`generic`: projective Horner, order-independent; `optimised`: Jacobian steps, monic Horner, affine first step, isomorphism as `Z·u⁻¹`, order-dependent) and the scalar multiplications around them; a lower bound on the cost of every chain outside the bounds; and the frozen export of every ordering within a factor of the cheapest.  On CryptoPro-B: 76 elements, 381 orderings, all verified; 4 + ω in the order 7·5·5 is the cheapest at 80 M_eq (128 for the evaluator measured before). |
| `corpus.py` | ingests the `std-curves` database (248 standardized curves), verifies every prime-field curve, certifies its discriminant class, cross-checks against the database's own `cm_disc`/`conductor`, and for every small-discriminant curve runs the chain-priced inventory, the modelled ranking and the explicit construction. |
| `fourq.py` | FourQ with its **real endomorphisms**: `F_{p²}` arithmetic for `p = 2^127−1`, the twisted Edwards curve, and the maps `τ, τ̂, δ, δ⁻¹, φ_W, ψ_W` transcribed from the authors' Magma script.  Verifies the parameters and the FourQlib generator, derives `D_K = −40` from the trace, checks both maps are homomorphisms, finds their quadratic relations on the subgroup (`ψ² = 32`, `φ² = −80`) by search, identifies the realised eigenvalues, and checks the 4-dimensional decomposition on points. Registers FourQ as a target whose generators carry those eigenvalues and the measured operation counts. |
| `genus2.py` | Jacobians of `y² = f(x)`, `deg f = 5`: generic affine Cantor composition/reduction with counted operations; the automorphisms ζ₅ (Buhler–Koblitz) and ζ₈ (Furukawa–Kawazoe–Takahashi) on Mumford divisors; the Jacobian order from the zeta function by brute force at toy size; and the toy proof that the automorphism acts as a primitive root of unity on a prime-order divisor and that the 4-dimensional decomposition reconstructs `kD`.  Writes the measured counts into the cost table and registers structural 128-bit targets, including the `F_{p²}` variant where the ζ₅-powers × Frobenius box reproduces the 8-dimensional Bos–Costello–Hisil–Lauter decomposition. |
| `toyverify.py` | the same objects with explicit kernel points on toy curves, plus `cm_curve_from_class_polynomial` (a curve of any size with CM by a given small discriminant, from its Hilbert class polynomial) used for the 256-bit 2-isogeny-chain tests. |

## On √élu

The follow-up list asked for √élu-style evaluation of large prime steps. It
is not implemented, on purpose: √élu evaluates an isogeny from a *kernel
point*, and the kernels this pipeline meets are rational subgroups whose
points live in extension fields of degree up to `ℓ−1` (CryptoPro-B's
order-31 subgroups have no rational point).  The kernel-polynomial form
needs no point at all, and in this pipeline the cost that matters is
*finding* the kernel, which the Frobenius-eigenvalue method does in
`O(log p)` polynomial multiplications modulo `f_ℓ`; evaluation is a
polynomial of degree `ℓ`, negligible against the scalar multiplication.
A native implementation of a chain (see the `crypto` repository's
CryptoPro-B experiment) evaluates each step as `x ↦ N(x)/ψ(x)²`,
`y ↦ y·M(x)/ψ(x)³` with precomputed polynomials, which is `O(ℓ)` per step.

## What it is not

* Not a timing: all numbers are operation counts under `costmodel.py`.
  Change the table and re-run; the Markdown says which constants drove each
  conclusion.
* Not a security assessment: it says nothing about which of the synthetic
  families are safe to deploy (small-discriminant CM curves and extension
  fields each carry their own literature).
* Not a ledger record: nothing here changes any hypothesis or evidence
  status.  Promoting a configuration into the research program goes through
  `/propose-ideas` → `/design-experiment` as usual.
