# endosweep — an endomorphism-ring sweeper for scalar-multiplication decompositions

`python -m harness.endosweep` enumerates, for every target group it knows,
**every way the endomorphism ring can be used to shorten a variable-base
scalar multiplication**, reduces each candidate's relation lattice exactly,
costs it under one explicit operation-count model, and labels what it finds
with the literature construction it reproduces — or with *no literature
match found*.  It is a hypothesis generator with certificates, not a
benchmark: a configuration that beats the known ones on paper is a candidate
for an implementation and a measured experiment, nothing more.

Run:

```sh
python -m harness.endosweep --out-dir outputs/endosweep           # everything
python -m harness.endosweep --targets secp256k1,BLS12-381 --max-dim 6
python -m harness.endosweep.toyverify --bits 26                   # explicit maps on toy curves
python -m pytest -q tests/test_endosweep.py
```

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

## Modules

| module | does |
|---|---|
| `quadorder.py` | exact arithmetic in imaginary quadratic orders: norm/trace/height in the reduced basis `{1, ω}`, elements of a given norm, unit groups, the Kronecker symbol, **`small_discriminant_scan`** (one perfect-square test per fundamental discriminant — certifies `|D_K| > bound` without factoring `t²−4q`), **`smallest_principal_power`** (class order of a prime ideal by composition of binary quadratic forms, then the generator of its first principal power by Cornacchia with Hensel-lifted square roots). |
| `lattice.py` | exact LLL over `Fraction`, the relation lattice `{v : Σ v_i λ_i ≡ 0 (n)}`, Babai decomposition with a **provable** coefficient bound (sum of half ∞-norms of the reduced basis) and an empirical maximum over random scalars. |
| `costmodel.py` | one table of constants (EFD formula counts for Jacobian/Edwards doubling and addition; SIDH-literature x-only isogeny-step counts; assumptions marked as such) and the interleaved width-w NAF multi-scalar cost with per-generator tables, batched affine conversion and incremental endomorphism costs. |
| `targets.py` | the registry.  Fourteen deployed curves (secp256k1, P-256/384/521, brainpoolP256r1, SM2, Curve25519, Ed448, Curve1174, Curve41417, E-521, M-511, BN254 G1, BLS12-381 G1) **verified from their constants alone** (n prime, Hasse interval, a point of order divisible by n killed by h·n), structural G2 entries (ψ acts as `[p]`, `r | Φ₁₂(p)`), a synthetic GLS group over `F_{p²}`, and synthetic prime-order CM curves for fourteen small discriminants of class number 1–7.  An entry whose constants fail verification is skipped and reported, never swept. |
| `sweep.py` | catalogue → configurations → exact lattice reduction → cost → ranking → Markdown/JSON report. |
| `toyverify.py` | builds the actual maps on toy curves (a j=0 curve with rational 7-torsion; a curve with CM by the class-number-3 order of `Q(√−23)` from its Hilbert class polynomial) and checks every prediction by evaluating them on points: eigenvalues of ζ₃, of the degree-7 endomorphism `2+ω`, of its powers, of the closed 3-walk of 2-isogenies (degree 8, eigenvalue of `1+ω`), and that the 4-dimensional decomposition `{1, ζ, α^j, ζα^j}` reconstructs `kP` with coefficients inside the Babai bound. |

## Configurations the sweep enumerates

* `generic` — width-w NAF, one scalar.
* `GLV-2 [g]` — identity plus one cheap endomorphism: the unit (`D_K ∈ {−3, −4}`),
  or every primitive element of norm ≤ 64 as a single Vélu map.
* `pump-4 [u × cycle]` — `{1, u, α, uα}` with `α` a power of the first principal
  power of a split prime, height tuned to `n^{1/4}`; `pump-6`, `pump-8` boxes
  and two-cycle boxes without a unit.
* `frob-d` — monomial boxes `{ψ^i}` and `{u ψ^i}` in declared Frobenius-type
  generators (G2 ψ, GLS ψ).

Each configuration reports dimension, provable and empirical coefficient
bits against the balanced ideal `(log2 n)/d`, the ∞-norm bits of every
reduced basis vector (an unbalanced lattice shows up here as a vector of
norm 1), doublings, additions, endomorphism and precomputation cost, the
total, and the literature label.

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
