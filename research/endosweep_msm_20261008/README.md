# Endomorphisms in Pippenger MSM, and α-adic expansions on chain curves

Two follow-ups from the endomorphism-sweep shortlist, both about constant
factors of scalar multiplication.  Neither is an ECDLP result or a security
claim, and no ledger, knowledge or coordination record is touched.

Every figure below is either **modelled** (an operation count from
`costmodel.py`'s or `curvesweep.py`'s constants) or **measured** (field
operations actually executed and counted, or results verified on points),
and is marked as such.

## Commands

```sh
# frozen curve inputs (n, p, omega eigenvalue, chain catalogue) for Bandersnatch,
# CryptoPro-B, CP6-782, Tom-384; needs a J08nY/std-curves checkout at
# 77fe6e3585ca2c2225b59d7df24b7c775437276f
python -m harness.endosweep.msm --freeze --std-curves STD_CURVES_CHECKOUT --out-dir research/endosweep_msm_20261008
# item 1: modelled sweep N = 2^6..2^22 on six curves + counted validation on secp256k1 (about 5 min)
python -m harness.endosweep.msm --out-dir research/endosweep_msm_20261008
# item 2: alpha-adic expansions, 1000 scalars per configuration (about 1 min)
python -m harness.endosweep.alphaadic --out-dir research/endosweep_msm_20261008
python -m pytest -q tests/test_endosweep_msm.py
```

`--markdown-only` on either module rewrites its `.md` from its `.json`.

---

## Item 1 — Endomorphisms in Pippenger multi-scalar multiplication

**Question.**  The hypothesis handed to this session: in a bucket MSM of
`N` points with `b`-bit scalars and window `c`, the dominant term
`(b/c)·N·A` depends only on the total number of scalar bits, which a GLV
split conserves (`N×b → 2N×b/2`).  GLV therefore only shrinks the bucket
aggregation term `≈ (b/c)·2^c·2A`, and pays `N·C_α` for the images.
Predicted break-even `C* ≈ b·A/(c(c+1))`, about 6 M at `N = 2^20` and
27 M at `2^10` (`b = 256`, `A ≈ 6 M` batched affine).  Predicted gains:
ζ₃ GLV ≈ 5–6 % at `2^20`; Bandersnatch's `√−2` 0–2 % at `2^20` and ≈ 10 % at
`2^10`; chain endomorphisms (CryptoPro-B `4+ω`, CP6-782, Tom curves) lose for
`N ≥ 2^6`.

### What was built (`harness/endosweep/msm.py`)

* **An explicit Pippenger operation count.**  Signed-digit windows
  (digits in `[−2^(c−1), 2^(c−1)]`, the sign absorbed by negating the point),
  buckets `1..2^(c−1)`, bucket accumulation, running-sum aggregation
  (`R += S_j; T += R`), and window combination (`c` doublings and one
  addition per window).  The window `c` is **searched** (1..22) for every
  `N`, variant and setting; nothing is assumed about it.
* **Three variants.**  (i) `plain`; (ii) `glv` — Babai rounding against the
  reduced lattice of `lattice.py`, `2N` points with coefficients of
  `bitlen(provable Babai bound)` bits (128, 128, 127, 128, 190, 192 bits for
  the six curves), plus `N` images; (iii) `fold`, for `D = −3` only —
  `z = k₁ + k₂ω ∈ Z[ω]` expanded in radix `2^c` with digits from the
  hexagonal Voronoi cell of `2^c·Z[ω]` (a complete residue system, tested),
  each digit moved by a unit into the sector `{x ≥ 1, y ≥ 0}`, so one bucket
  per unit orbit: `≈ 4^c/6` buckets, a third of the `4^c/2` of a plain
  window of the same width.  The window sum `Σ δ'·S` is `X + ω(Y)` with
  `X = Σ x·S`, `Y = Σ y·S`, each a column/row grouping and a running sum;
  `2N` unit images (`βx`, `β²x`) are charged.  Radix 2 (`c = 1`) is refused:
  `−1` has digit `1` and `(−1 − 1)/2 = −1` is a fixed point.
* **Two addition settings, constants derived, not assumed** (`costmodel.py`
  constants, `S = 0.8 M`, `I = 100 M`):
  * `mixed`: Jacobian buckets; accumulation is `mADD` (7M + 4S = 10.2 M);
    aggregation and combination are `ADD` (11M + 5S = 15 M).
  * `batch_affine`: affine buckets; an affine addition given `1/(x₂−x₁)` is
    `λ` (1M), `x₃ = λ² − x₁ − x₂` (1S), `y₃` (1M); Montgomery's trick gives
    `m` inverses for `3(m−1)` M + 1 I (prefix products `m−1`, two
    multiplications per element on the way back).  So **A = 2M + 1S + 3M =
    5.8 M** per accumulation addition, plus a share of one inversion per
    round of a pairwise tree batched over every bucket of every window
    (`⌈log₂ max load⌉` inversions in all).  Running sums use `mADD` and `ADD`.
* **Endomorphism images.**  ζ₃: `(x, y) ↦ (βx, y)`, 1 M, affine in and out.
  Chains: the optimised-evaluator count of the cheapest element from the
  earlier sweeps (Bandersnatch `ω = √−2`: 5M + 1S; CryptoPro-B and Tom-384
  `4 + ω` as `7·5·5`: 78M + 2S; CP6-782 `4 + ω` as `7·3·5`: 63M + 2S), whose
  output is Jacobian, **plus** the batched conversion to affine that mixed
  and affine accumulation need: `3M` (batch) `+ 3M + 1S` = 6.8 M per point
  + `I/N`.  The tables also give the gain without that conversion.
* **Curve inputs.**  secp256k1 and BLS12-381 G1 from `targets.py`; the four
  chain curves frozen in `curves.input.json` from the std-curves checkout,
  the arkworks export and the chain/curve sweeps, each re-verified
  (`targets.verify`; `n` prime; the ω eigenvalue a root of ω's minimal
  polynomial mod `n`).

### Validation (measured)

A counted implementation of all three variants in both settings runs on
secp256k1 (`dbl-2009-l`, `add-2007-bl`, `madd-2007-bl`, the affine pairwise
tree with Montgomery batch inversion, the hexagonal fold with real `βx`
images), every field multiplication, squaring and inversion counted.  Points
are `P_i = [r_i]G` with independent random `r_i`; every MSM result equals
`[Σ k_i r_i]G`, and for `N = 256` also the naive `Σ k_i P_i`.  The field
counters equal the operation-type counts times the formula counts exactly.
`N = 2^8 .. 2^12`, 2 trials each, the model evaluated at the window it chose:

| setting / variant | runs | mean error | max \|error\| |
|---|---|---|---|
| mixed / plain | 10 | −0.01 % | 0.11 % |
| mixed / glv | 10 | +0.03 % | 0.20 % |
| mixed / fold | 10 | +0.20 % | 0.56 % |
| batch_affine / plain | 10 | −0.01 % | 0.08 % |
| batch_affine / glv | 10 | +0.06 % | 0.20 % |
| batch_affine / fold | 10 | +0.27 % | 0.75 % |

**Stated tolerance: 1 % per run; met by all 60 runs** (largest 0.75 %).  Two
modelling details were forced by the measurement and are documented in the
code: the windows near the top are computed exactly from the magnitude
distribution (uniform on `[0, n)` for plain, the trapezoid of Babai rounding
for GLV, the integer points of the scaled Babai parallelogram for fold) with
the carry propagated; and the inversion count follows the largest bucket of
any window, including the near-empty top window.  The first model draft,
with only the top window non-uniform, was off by up to 3 % for GLV; points in
arithmetic progression made affine partial sums collide and were replaced.

### Results (modelled; tables in `msm.md`, data in `msm.json`)

**Break-even image cost `C*(N)`** (M per image; GLV wins iff the image costs
less), batched affine, secp256k1 (the other curves track it within a few M at
equal `b`; the 377/384-bit curves sit higher):

| log₂ N | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22 |
|---|---|---|---|---|---|---|---|---|---|
| C* (model) | 98.7 | 49.7 | 33.0 | 21.4 | 13.9 | 11.9 | 8.2 | 7.2 | 6.8 |
| `b·A/(c(c+1))` | 74.2 | 35.4 | 26.5 | 16.5 | 13.5 | 8.2 | 7.1 | 5.5 | 4.3 |
| C*, mixed | 130.9 | 70.0 | 44.2 | 31.8 | 23.3 | 12.1 | 18.1 | 9.0 | 8.6 |

`C*` is not monotone above `2^16`: it moves with `b mod c`
(256 = 16·16 leaves plain a 17th window holding only the carry; 255 bits on
BLS12-381 does not), so at `2^17–2^22` it ranges 2.5–10 M across the six
curves and two settings.

**Gain of GLV (and fold) over plain Pippenger**, % of the plain total,
batched affine / mixed:

| curve, image cost | 2^6 | 2^8 | 2^10 | 2^12 | 2^14 | 2^16 | 2^18 | 2^20 | 2^22 |
|---|---|---|---|---|---|---|---|---|---|
| secp256k1 ζ₃ (1 M), GLV | 18.5 / 16.8 | 13.8 / 12.8 | 12.4 / 10.5 | 10.1 / 9.4 | 7.8 / 8.2 | 7.8 / 4.9 | 5.9 / 8.4 | **5.9 / 4.5** | 6.1 / 4.8 |
| secp256k1, hexagonal fold | 28.0 / 21.0 | 28.2 / 16.7 | 25.9 / 13.0 | 23.0 / 11.5 | 20.6 / 10.5 | 20.0 / 7.6 | 18.2 / 11.6 | **15.3 / 6.8** | 15.7 / 9.0 |
| BLS12-381 G1 ζ₃, GLV | 17.9 / 16.7 | 14.4 / 13.3 | 12.8 / 9.8 | 10.2 / 9.5 | 7.8 / 7.9 | 7.9 / 4.9 | 6.9 / 7.9 | **3.9 / 2.4** | 4.9 / 4.8 |
| BLS12-381 G1, hexagonal fold | 27.4 / 20.9 | 28.3 / 16.8 | 25.8 / 11.9 | 23.1 / 11.6 | 20.7 / 10.4 | 20.2 / 7.8 | 18.1 / 10.4 | **12.9 / 4.4** | 14.6 / 9.0 |
| Bandersnatch √−2 (5.8 + 6.8 M) | 15.9 / 15.1 | 11.8 / 11.8 | **8.2 / 7.6** | 3.9 / 5.8 | −0.3 / 2.3 | −0.8 / 1.7 | −4.0 / −0.2 | **−7.7 / −4.1** | −10.5 / −3.4 |
| Bandersnatch, image as in curves.md only (5.8 M) | 17.5 / 16.2 | 13.8 / 13.1 | 10.9 / 9.3 | 7.3 / 7.9 | 3.9 / 4.8 | 4.2 / 4.7 | 1.7 / 3.3 | −1.0 / −0.1 | −3.0 / +0.9 |
| CryptoPro-B 4+ω (79.6 + 6.8 M) | **1.8 / 5.7** | −9.9 / −2.6 | −20.4 / −11.3 | −32.1 / −16.7 | −43.7 / −23.4 | −53.5 / −32.6 | −64.2 / −34.9 | −79.5 / −47.0 | −85.2 / −49.0 |
| CP6-782 4+ω (64.6 + 6.8 M) | **9.4 / 10.4** | **0.7 / 4.4** | −7.4 / −1.0 | −14.7 / −5.4 | −21.0 / −9.3 | −28.4 / −15.8 | −37.0 / −17.8 | −42.0 / −23.7 | −48.4 / −26.7 |
| Tom-384 4+ω (79.6 + 6.8 M) | **7.7 / 9.3** | −0.4 / **3.0** | −10.0 / −3.6 | −20.2 / −9.2 | −26.9 / −13.3 | −33.5 / −18.3 | −41.0 / −22.3 | −49.1 / −28.2 | −57.1 / −31.8 |

Averaged over `N = 2^10 .. 2^21` (the range of the literature note below),
BLS12-381 G1: GLV split **+7.4 %** (batched affine) / **+7.1 %** (mixed);
hexagonal fold **+19.5 %** / **+9.7 %**.

### Findings

1. **The mechanism holds, as an operation count.**  At a common window the
   split leaves the accumulation count unchanged and halves the bucket
   aggregation (a test checks both at `N = 2^16`, `c = 13`).  What it also
   saves, and the hypothesis leaves out, is half the window-combination
   doublings and the freedom to re-optimise `c`; that is why the modelled
   `C*` exceeds `b·A/(c(c+1))` by 3–58 % at the tabulated sizes (e.g. 33.0 vs
   26.5 M at `2^10`, 7.2 vs 5.5 M at `2^20`), and falls below it only at a
   few sizes where the `b mod c` quantisation bites (e.g. `2^17`).  The
   formula has the right shape and the right order of magnitude; as a
   predictor of the break-even it is mostly low.
2. **ζ₃ GLV at `2^20`: 5.9 % (secp256k1) and 3.9 % (BLS12-381), batched
   affine; 4.5 % and 2.4 % mixed.**  The predicted 5–6 % holds for secp256k1
   batched affine and is 1.5–3.5 points high otherwise; the spread between the
   two curves at the same `N` is the `b mod c` quantisation, not the
   endomorphism.  At `2^22` both are 4.8–6.1 %.
3. **Unit folding is worth more than the split where it applies.**  The
   hexagonal fold beats the split at every `N` on both `D = −3` curves:
   12.9–15.3 % at `2^20` batched affine, 4.4–6.8 % mixed.  It is larger in the
   affine setting because the column/row groupings are themselves batched
   affine additions (5.8 M) while the Jacobian setting pays 15 M for them.
4. **Bandersnatch: ≈ 8 % at `2^10` (prediction ≈ 10 %: roughly held),
   −4 to −8 % at `2^20` (prediction 0–2 %: not held).**  With only the
   curves.md chain cost (5.8 M, i.e. assuming an affine image for free) it is
   −1.0 / −0.1 % at `2^20`, just below the predicted range; the
   batched conversion of the Jacobian image to affine (6.8 M + I/N) is what
   moves it clearly negative.  GLV stops paying at `2^14` (affine) / `2^18`
   (mixed).
5. **Chain endomorphisms do not lose from `2^6` on — they lose from `2^7–2^10`
   on.**  At `N = 2^6` all three chain curves still gain (CryptoPro-B
   +1.8 / +5.7 %, CP6-782 +9.4 / +10.4 %, Tom-384 +7.7 / +9.3 %); CP6-782 and
   Tom-384 still gain at `2^8` in at least one setting.  The first loss in the
   sweep: CryptoPro-B `2^7` / `2^8`, Tom-384 `2^8` / `2^10`, CP6-782 `2^9` / `2^10`
   (batched affine / mixed).  So the prediction "lose for `N ≥ 2^6`" is
   refuted at the small end; at every `N ≥ 2^10` all three lose, by 1–85 %.
6. **Comparison with Le–Sica (KN-LIT-b901b9).**  The note records only the
   ePrint abstract and metadata ("Full text, measurements and code were not
   independently inspected"): it reports, for BLS12-381 with 2^10–2^21 points,
   "an average 6% improvement over Pippenger", and 7 % fewer curve operations
   than Luo–Fu–Gong.  Its method is **not a plain GLV split**: it
   "optimize[s] bucket sets and Hamiltonian traversal for
   endomorphism-assisted multi-scalar multiplication", i.e. a bucket-set
   construction in the same family as the unit folding here.  This model's
   plain split averages 7.1–7.4 % over the same range and its hexagonal fold
   9.7–19.5 %, both against a plain signed-digit Pippenger.  The ζ₃ split
   figure is of the note's order, but the two are not the same method and the
   baselines are not known to match (the note's "Pippenger" baseline, batch
   sizes and counting unit could not be checked), so **no agreement or
   disagreement is claimed**; that the fold model exceeds the reported 6 %
   says at most that the note's baseline is likely stronger than this one
   (unverified).

### Scope

* Operation counts under `costmodel.py`'s constants (Jacobian EFD formulas,
  `S = 0.8 M`, `I = 100 M`), not timings; memory traffic, scheduling and
  bucket-conflict handling of real implementations are not modelled.  XYZZ
  bucket coordinates and twisted-Edwards arithmetic (natural for
  Bandersnatch) are not in `costmodel.py` and are not used.
* Chain curves are counted on short Weierstrass models with the chain
  evaluator counts of the earlier sweeps; the fold is modelled and measured
  only for `D = −3`.
* The model was validated by execution on secp256k1 for `N ≤ 2^12`; larger
  `N` and the other curves are the same model with different constants.

---

## Item 2 — α-adic expansions on prime-field chain curves

**Claim tested.**  Expanding `k = Σ d_i α^i` with digits from a complete
residue system modulo `α` costs `C_α/log₂ N(α)` per bit — CryptoPro-B:
`80/7.45 ≈ 10.7` M per bit against ≈ 7.4 M per doubling — so α-adic
expansion is dominated by doubling.  Reviewer's objection: digit sets modulo
`N(α)` change the addition density per bit, so it must be measured.

### What was built (`harness/endosweep/alphaadic.py`)

* **Reduction first.**  `k` is reduced to `z = x + yω ∈ O_K` with
  `z ↦ k (mod n)` and small norm (Lagrange reduction of the relation lattice
  under the norm form, Babai rounding).  Measured `N(z)/n`: 12.5 ± 11.5
  (D = −619), 0.25 ± 0.17 (Bandersnatch).  The unreduced ablation (expanding
  the integer `k`) doubles the length, as it must (35 → 68 digits on
  CryptoPro-B).
* **Digit sets.**  `int`: balanced integers mod `N(α)` (`O/(α) ≅ Z/N(α)` for
  primitive α); `voronoi`: minimal-norm representatives of `O/(α)` in `O_K`
  (needs `ω(P)`); `naf<w>`: width-`w` α-NAF with minimal-norm digits prime to
  α, offered where the table `(N^w − N^(w−1))/2 ≤ 64`, i.e. only for norm 2
  and 3 (for `N(α) = 175` the width-2 table would be 15 225 points).
  Residues modulo any `α^w` come from the ideal's Hermite normal form.
* **Termination is proved, or refuted, per digit rule.**  `|T(z)| ≤ (|z| + R)/|α|`
  with `R` the largest digit, so every orbit enters and stays in the disk
  `|z| ≤ R/(|α| − 1)`; every element of that disk is iterated to 0.  84 of the
  94 rules terminate.  **The 10 `int` rules for elements with `|b| ≥ 2`
  (`15+2ω`, `37+3ω` on CryptoPro-B and on Tom-384; `5+2ω`, `1+2ω`, `15+2ω`,
  `20+3ω`, `11+2ω`, `1+4ω` on CP6-782) do not**: a cycle is found in the
  disk, so those configurations are reported as non-terminating and not
  costed (their `voronoi` rules terminate and are costed).
* **Cost.**  Horner `Q ← α(Q) + d_i·P`: `(L−1)` applications of α **to a
  Jacobian point** (every step a general step — the chain sweep's 80 M_eq for
  `4+ω` assumes an affine input, which Horner never supplies: 109 M_eq),
  `(nnz−1)` additions (mixed with an affine table, full with a Jacobian one,
  whichever is cheaper), the digit table and `ω(P)` where digits need it.
  M_eq = M + S with the curve's own Fermat inversion, as in the curve sweep.
* **Verification (measured).**  All 1000 × 94 expansions reconstruct `k`
  modulo `n` through `λ_α` (84 800 of 84 800 checked, including the
  ablations).  On CryptoPro-B, 8 Horner evaluations with the **real**
  `4 + ω` chain (rational maps from `chains.constants.json`, realised as
  `−(4 + ω)`) equal `k·P` on points (4 `int`, 4 `voronoi`).

### Results (1000 random scalars per configuration; mean ± sd; modelled cost, measured digit statistics)

Comparators are the same curve's best width-w NAF and best 2-GLV with its
cheapest chain from `curvesweep.scalar_model` (M_eq); `costmodel.py`'s
analytic figures (S = 0.8 M, I = 100 M) are in `alphaadic.md`.

| curve | α (N) | digits | length | non-zero density | table M_eq | total M_eq | per bit | wNAF | 2-GLV |
|---|---|---|---|---|---|---|---|---|---|
| CryptoPro-B | 4+ω (175) | int | 35.0 ± 0.2 | 0.995 | 1 368 | 5 609 ± 30 | 21.9 | 2 805 | 1 990 |
| CryptoPro-B | 4+ω (175) | voronoi | 35.0 ± 0.2 | 0.994 | 2 480 | 6 721 ± 29 | 26.3 | | |
| CryptoPro-B | 54+ω (3125) | int | 22.9 ± 0.3 | 1.000 | 24 968 | 28 740 ± 44 | 112.3 | | |
| Tom-384 | 4+ω (175) | int | 52.7 ± 0.5 | 0.993 | 1 370 | 7 822 ± 66 | 20.4 | 4 932 | 3 234 |
| CP6-782 | 4+ω (105) | int | 56.9 ± 0.2 | 0.989 | 809 | 6 950 ± 36 | 18.4 | 4 467 | 2 990 |
| Bandersnatch | √−2 (2) | naf5 | 250.5 ± 2.2 | 0.169 | 170 | 3 577 ± 39 | 14.1 | 3 286 | 2 159 |
| Bandersnatch | 1+√−2 (3) | naf3 | 158.3 ± 1.4 | 0.290 | 154 | **3 547 ± 40** | 14.0 | 3 286 | 2 159 |

The best α-adic configuration per curve is **2.0× / 1.59× / 1.56× / 1.08×**
the width-w NAF and **2.82× / 2.42× / 2.33× / 1.64×** the 2-GLV
(CryptoPro-B / Tom-384 / CP6-782 / Bandersnatch).  No configuration of the
94 beats either comparator on any curve.

**On the reviewer's objection.**  The density moves in the claim's favour,
not against it: with `N(α) = 175` almost every digit is non-zero (0.995), but
there are only `log₂ 175 = 7.45` bits per digit, so additions per bit are
0.134 — fewer than width-5 NAF's 1/6.  What the per-bit estimate misses is
elsewhere: (a) α is applied to a Jacobian point (109 M_eq, not 80), and
(b) the table of `(N−1)/2 = 87` multiples costs 1 368 M_eq (5.3 M_eq per bit).
Measured per bit on CryptoPro-B `4+ω` (the cheaper Jacobian table is
chosen): loop 16.6 M_eq (α 14.5 + full additions 2.1), table 5.3, total 21.9 — against 10.7 claimed for α
alone, 11.0 for the whole wNAF and 7.8 for the whole 2-GLV.

### Obstruction (closure record, `docs/inventor-protocol.md` §4)

```yaml
obstruction:
  statement: >-
    An alpha-adic Horner scheme is one-dimensional: its length is
    log2 N(z) / log2 N(alpha) = b / log2 N(alpha) digits, so its endomorphism
    work per bit of k is C_alpha(Jacobian input) / log2 N(alpha), and with the
    chain evaluators' general-step count c(l) = 7.5 l - 6.5 M_eq for odd l
    (10 M_eq for l = 2) every chain has C/log2 N >= min_l c(l)/log2 l
    >= 10.0 M_eq per bit, which already exceeds the doubling that 2-GLV pays
    per bit of k (DBL/2 = 4-5 M_eq) and, for every D = -619 / -339 element,
    the whole width-w NAF per bit (doubling + additions).
  quantity: >-
    endomorphism cost per bit of the scalar in the alpha-adic Horner loop,
    min over the catalogue of C_alpha(Jacobian in) / log2 N(alpha), compared
    with the comparators' total cost per bit; and the measured total
    alpha-adic cost over the best comparator.
  value: >-
    CryptoPro-B 13.44 M_eq/bit (54+w; 14.63 for 4+w) vs wNAF 10.96 and 2-GLV
    7.77 M_eq/bit; Tom-384 13.44 vs 12.84 / 8.42; CP6-782 12.86 vs 11.85 /
    7.93; Bandersnatch 10.73 vs 12.99 / 8.53.  Best measured total over 2-GLV:
    2.82x / 2.42x / 2.33x / 1.64x (sd of the totals <= 2.0 % of the mean;
    1000 scalars per configuration, 94 configurations, 10 refuted as
    non-terminating).
  measured_by: [research/endosweep_msm_20261008/alphaadic.json]   # no RUN-/EXP- record (none created by this session)
  scope: >-
    GOST CryptoPro-B and Tom-384 (D = -619), CP6-782 G1 (D = -339),
    Bandersnatch (D = -8); every element of each curve's complete cheap-chain
    catalogue (11, 11, 18, 2 elements); short Weierstrass Jacobian
    coordinates with the optimised chain evaluator of chainsweep.py
    (affine-input first step not available inside Horner); digit sets int,
    voronoi, alpha-NAF w <= 8 (norm 2, 3 only); M_eq = M + S, Fermat
    inversion.  Not claimed for x-only/Montgomery models, other evaluators,
    curves with norm-2/3 elements other than Bandersnatch, or Frobenius-type
    free endomorphisms.
  resource_check:
    examined: true
    reading: >-
      The same per-bit price is what makes the chain worth paying ONCE per
      scalar (2-GLV: one image saves b/2 doublings) and once per point in a
      small multi-scalar multiplication (item 1: CP6-782 and Tom-384 still
      gain at N = 2^6 - 2^8), but not once per digit.  It is therefore a
      resource for amortised uses and an input to the break-even C*(N) of
      item 1; no theory was found that turns the per-digit gap into an
      advantage for alpha-adic recoding.
    spawned_ids: []
```

**Forward guidance — what would reopen it.**

* A step cheaper than half a doubling per bit: `c(ℓ)/log₂ℓ < DBL/2`.  The
  SIDH-literature x-only counts in `costmodel.py` (2-isogeny 4 M, 3-isogeny
  4M + 2S) give 4.0 and 3.5 M per bit, below `DBL/2`.  That points at
  **norm-2/3 maps on x-only models of `D = −7` (`(1 ± √−7)/2`) and `D = −8`
  (`√−2`, `1 ± √−2`) curves**, provided an α-adic analogue of the
  differential (ladder) addition exists, since x-only arithmetic has no
  general addition.  Neither the x-only cost nor such a ladder was examined
  here.
* An evaluator with an affine-input cost on every step (it would need a cheap
  normalisation per step; the inversion costs 264 M_eq on CryptoPro-B, far
  more than the 29 M_eq it would save).
* A digit-table construction that is sub-linear in `N(α)` while keeping the
  α-adic length (none known here; the width-2 α-NAF goes the other way).

Even then the comparator to beat is 2-GLV, not the doubling chain: the
Bandersnatch case (10.7 M_eq per bit, already below its wNAF's 13.0 per bit)
still loses to 2-GLV by 1.64×.

---

## Files

| file | what |
|:--|:--|
| `msm.md` | item 1 report: endomorphism costs and coefficient sizes, `C*(N)` and gain tables per setting, optimal windows, and the validation runs |
| `msm.json` | item 1 data: every curve × setting × N with the optimal plain / GLV / fold configuration and its operation breakdown; the validation rows with measured field counts |
| `alphaadic.md` | item 2 report: every curve × element × digit rule with length, density, table, total (mean ± sd), per-bit costs, comparators and termination certificates |
| `alphaadic.json` | item 2 data, including the termination certificates, the reducer bases and the on-points checks |
| `curves.input.json` | the frozen curve inputs (n, p, ω eigenvalue, chain catalogue with operation counts) for the four chain curves |
| `SHA256SUMS` | hashes of the JSON files |
