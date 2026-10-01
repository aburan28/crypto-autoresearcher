# Blind re-derivation — TASK-20260913-7fb774 (attempt 2)

Review round `REVIEW-SEMBIN-20260913-251fd3`. Joint owned: `blind_rederivation`.
Role: Validator, independent session, `review-adversarial` requested,
`claude-fable-5-1-thinking-xhigh` resolved, `xhigh` effort, `model_verified: false`,
`fallback_used: false`.

**What this is.** I derived the quantity from the task card's statement plus the
sources in the READ SCOPE and nothing else. I have not seen the producer's
implementation, its outputs, the review plan, any sibling report, or any value to
compare against. Numbers live in `rederived-values.json`; the script that produced
them is `scratch/rederive.py` (seed 20260914), projected onto the deliverable
schema by `scratch/make_values.py`. Raw script output is `scratch/rederive-output.json`.
No code was imported or copied from any `experiments/` directory; every formula
below is written from the statement and the papers.

**Blindness.** I did not open `experiments/EXP-SEMBIN-db9bc3/code/` or `.../runs/`,
anything under `coordination/review/` other than my own task directory, anything
under `coordination/goals/` or `coordination/bus/`, `ledger/goals/GOAL-SEMBIN-5078bc.yaml`,
or `ledger/decisions/DEC-20260913-c224bb.yaml`; I ran no `git log` and read no commit
message; I ran no repository-wide search. One consequence is recorded in
§8 (A-0): my assigned write scope already contained a `rederivation.md`, a
`rederived-values.json` and a `scratch/` directory when I started. Since attempt 1
"was cut … before writing anything", their provenance was not established, so I
moved them **unread** to `preexisting-unread/` rather than open, diff, or overwrite
them. `sources_read` in the attestation lists exactly what I opened.

**Scope disclaimers, stated once and binding throughout.** Every figure is
arithmetic in the log2 domain under stated conventions. No curve was instantiated,
no system solved, no Gröbner basis run, no degree measured or asserted (Proposition 5
and the first fall degree assumption are *granted*, per H-SEMBIN-4a80f3's own
`assumptions`). Nothing here is a statement about the security of any curve, in
either direction, and nothing here is a claim that Nagao's Theorem 1 is right or
wrong — Theorem 1 is `O(n^{8w+1})` with unstated `C` and `n_0`, and an evaluation at
one `n` can neither confirm nor contradict it.

---

## 1. The two cells and the statement being derived

| | cell A | cell B |
|---|---|---|
| p | 2 | 2 |
| n | 571 | 571 |
| ω | 2.807 | 3.0 |
| C_0 | 8 | 3 |
| d_F | 4 | 4 |
| monomial reading | binomial `C(N + d_F, d_F)` | binomial `C(N + d_F, d_F)` |

Five named terms, then a charge, then a baseline, then margins:

- `T1 = log2(monomials)` on `N = n(m − 1)` variables, `m = n / C_0`.
- `T2 = (ω − 1) · T1`, so `T1 + T2 = ω · log2(monomials)` = one solve.
- `T3 = log2 #Fb`, `#Fb = m · p^{C_0}` = relations to collect.
- `T4 = log2(1 / Pr[a decomposition succeeds])`, `Pr = 1 − exp(−λ)`,
  `λ = Π_i #Fb_i / #E(F_{p^n})`, `#E ~ p^n`, each `#Fb_i` a binomial count of
  mean `~ p^{C_0}` (HEUR-1).
- `T5` = memory in field elements: `T1` (frozen width) or `2·T1` (dense width²).
- charged time = `log2(2^{T1+T2+T3+T4} + 2^{ω·T3})`; charged memory = `T5`.
- vOW: `W = 0.886 · 2^{n/2}`, `T = W(1/M + 1/w)`, `Mem = 3n · max(w, M)`.
- margins = Nagao − vOW, under `time_only` and `time_memory_product`.

Cross-check against the sources: this is the same decomposition Nagao's Section 7
performs (`(nm)^{4w} · p^{C_0}/C_0 · n` for the decompose step, `(#Fb)^w` for the
linear algebra), with two terms he does not charge — the `1/Pr` factor, because he
asserts the success probability is `O(1)`, and memory, which the paper never
mentions — made explicit. The identity `m · p^{C_0} = n · (p^{C_0}/C_0)` at
`m = n/C_0` confirms that the statement's `#Fb` is Nagao's own `#Fb ~ m·p^k`.
`T1 + T2 = ω·T1` matches Lemma 2's `O(N^{d_F · w})` = (monomial count)^ω.

---

## 2. T1 and T2 — the monomial count

`monomials = C(N + 4, 4)` counts monomials of degree ≤ 4 in `N` variables, and
`T1 = log2` of that. I computed `C(N+4, 4)` as an **exact integer** with
`math.comb` and took `log2` of the exact integer (for integers past 1000 bits I
shift down by `bit_length − 1000` and add the shift back, so no intermediate float
overflow). For the non-integer-`m` variant I used `lgamma`; the two agree to
7e-11 bits at `N ≈ 40000` (`self_checks.log2_binom_real_vs_int_at_N_40000`).

Hand anchor, so a reader can spot-check: at cell A with `m = 71`,
`N = 571·70 = 39970` and `4·log2(39970) − log2(24) = 56.5616`, against the exact
`log2 C(39974,4) = 56.5619` — the 3e-4 bits is the `(N+1)(N+2)(N+3)` correction to
`N^4/24`.

`T2 = (ω − 1)·T1` by definition, and `T1 + T2 = ω·T1` exactly. Both are in
`rederived-values.json` per cell per rounding.

Two variants are recorded rather than chosen (both immaterial here, and both
recorded because they are the kind of thing that is *not* immaterial at small N):

- **Exact `EQS4` variable count.** Definition 7/8 of the paper put `X_i` in `V_i`
  (`C_0` F_p-coordinates each, `m` of them) and `U_i` in `F_{p^n}` (`n` each,
  `m − 2` of them), so the honest count is `m·C_0 + n(m − 2)`. This equals
  `n(m − 1)` exactly when `m·C_0 = n`, and differs by `m·C_0 − n` otherwise.
  At both cells the difference in `T1` is ≤ 4.3e-4 bits.
- **Square-free monomials.** With the field equations `X² = X` present, the
  monomial count is `Σ_{d≤4} C(N, d)`, not `C(N+4, 4)`. At `N ~ 10^5` these agree
  to ~1e-5 bits. Recorded in `T1_variants.squarefree_sum_C_N_d`.

For contrast only (the statement fixes the binomial reading), Nagao's Lemma 2
`O(N^{d_F})` form gives `4·log2 N`, which is `log2 24 ≈ 4.585` bits *above* the
binomial count per solve-unit, i.e. `ω·4.585 = 12.9` bits (cell A) / `13.8` bits
(cell B) more in `T1 + T2`. Reported as `nagao_lemma2_loose_N_to_dF`; it is not
part of the asked-for quantity.

---

## 3. Rounding m — the first ambiguity

`m = n / C_0` is not an integer at either cell: `571/8 = 71.375`, `571/3 = 190.333`.
Nagao writes `m ~ n/C_0` with a tilde and never rounds. The statement asks for the
value under each rounding I consider; I carried four:

| rounding | cell A m | m·C_0 − n | cell B m | m·C_0 − n |
|---|---|---|---|---|
| floor | 71 | −3 | 190 | −1 |
| ceil | 72 | +5 | 191 | +2 |
| nearest | 71 | −3 | 190 | −1 |
| exact real | 71.375 | 0 | 190.333 | 0 |

The rounding is nearly free in `T1` (spread 0.082 bits at cell A, 0.031 at cell B)
and in `T3` (0.020 / 0.008). **It is not free in `T4`,** because `T4` depends on
`λ = p^{m C_0 − n}` and the exponent is an integer that the rounding chooses:
+5 at cell A ceil means `λ = 32` and `T4 = 0.000`, while −3 at cell A floor means
`λ = 1/8` and `T4 = 3.089`. So a 1-unit rounding decision on `m` moves the charged
time by 3.03 bits at cell A and 1.22 bits at cell B under the arithmetic reading.
This is an ambiguity in the statement, not a defect in it: "m = n/C_0" at
non-dividing `C_0` does not determine `λ`.

The `exact_real` rounding is the only one that reproduces HEUR-2's nominal
operating point (`m·C_0 = n`, `λ = 1`) exactly, at the price of a non-integral
number of cosets — which the algorithm cannot have.

---

## 4. T3 — the relation count

`#Fb = m · p^{C_0}`; `T3 = log2 #Fb`. At cell A floor, `#Fb = 71·256 = 18176` and
`T3 = 14.1497`; at cell B floor, `#Fb = 190·8 = 1520`, `T3 = 10.5699`.

Algorithm 2's loop is `while i ≤ #Fb`, i.e. it collects `#Fb + 1` relations (one
more than the factor-base size, so the relation matrix has a kernel). I report
`T3_plus_one_relation = log2(#Fb + 1)` beside `T3`; the difference is 7.9e-5 bits
(cell A) and 9.5e-4 bits (cell B). No ceiling arises in `T3` itself — `p^{C_0}` is
an integer and the only rounding is the one on `m` already in §3.

---

## 5. T4 — the inverse yield, and where the statement stops determining the answer

This is the term the statement leaves genuinely open, and it is the finding of this
re-derivation. `Pr = 1 − exp(−λ)` is fixed; `λ = Π_i #Fb_i / #E` is a **random
variable**, because HEUR-1 makes each `#Fb_i` a binomial count. The statement asks
which expectation I take. Taking it in different places gives materially different
answers, and at cell B they differ by 20 bits.

### 5.1 The two binomial parametrisations of HEUR-1

HEUR-1 says `#Fb_i` is "a binomial count with mean `~ p^k`". Two parametrisations
deliver that mean, and they are *not* interchangeable for this purpose because they
differ in `P[#Fb_i = 0]`:

- **P-b, point-into-coset.** Each of the `#E ~ p^n` points lands in a given coset
  with probability `p^{C_0 − n}`, so `#Fb_i ~ Bin(p^n, p^{C_0−n})`, which is
  `Poisson(p^{C_0})` to within `O(p^{−n})`. `P[empty] = exp(−p^{C_0})`. This is the
  parametrisation whose empty-coset probability matches HEUR-1's own
  coupon-collector wording (`p^k = Ω(log m)`).
- **P-a, x-coordinate pairs** (p = 2). HEUR-1's random-model justification says the
  x-coordinate map is 2-to-1 onto a set of density `~1/2`. So each of the `2^{C_0}`
  x-values in the coset is on the curve with probability `~1/2` and then carries two
  points: `#Fb_i = 2·Bin(2^{C_0}, 1/2)`. Mean `2^{C_0}`, and
  `P[empty] = 2^{−2^{C_0}}`.

Both have the right mean and the same variance to leading order. Their empty
probabilities diverge enormously at small `C_0`:

| | mean | `P[empty]` P-b | `P[empty]` P-a |
|---|---|---|---|
| cell A, C_0 = 8 | 256 | `e^{−256}` ≈ 1e-112 | `2^{−256}` ≈ 9e-78 |
| cell B, C_0 = 3 | 8 | `e^{−8}` = 3.355e-4 | `2^{−8}` = 3.906e-3 |

At cell B with `m = 190` cosets, `P[every coset nonempty]` is 0.9382 under P-b and
**0.4754** under P-a. That is the coupon-collector condition Nagao's own parenthesis
warns about ("if one takes k = 1, it sometimes happens `#Fb_i = ∅`"), firing at
`C_0 = 3`: under the parametrisation HEUR-1's *justification* implies, a majority of
factor-base draws at cell B contain an empty coset. I measure it; I draw no
conclusion about C1 (that is not my joint).

### 5.2 Four readings of "which expectation"

- **R1, nominal.** HEUR-2 is stated at its operating point: `Π_i #Fb_i ~ #E` gives
  `λ ~ 1` and `Pr ~ 1 − 1/e`, "so the inverse yield charged is ~0.663 bits".
  Taking `λ := 1` gives `T4 = −log2(1 − 1/e) = 0.6617` at both cells, independent of
  the rounding of `m`. This reproduces HEUR-2's own stated figure to its stated
  precision, which is a useful consistency anchor on my `T4` machinery.
- **R2, arithmetic — expectation of the product.**
  `E[λ] = E[Π_i #Fb_i]/p^n = Π_i E[#Fb_i]/p^n = p^{m C_0 − n}` (cosets independent,
  each mean `p^{C_0}`). Then `T4 = −log2(1 − exp(−E[λ]))`. Values: cell A
  0.000 (ceil) / 3.089 (floor); cell B 0.027 (ceil) / 1.346 (floor).
- **R3, geometric — expectation of the logarithm.**
  `E[log2 λ] = m·E[log2 #Fb_i] − n·log2 p`. This is the reading that treats the
  typical factor base rather than the mean one, and it is strictly smaller than R2
  by Jensen. **Unconditionally it is degenerate**: `P[#Fb_i = 0] > 0` for every `i`,
  so `E[log2 #Fb_i] = −∞`, `λ = 0` on a positive-probability set of factor bases,
  and for such a factor base *no* `R` has a decomposition of this shape at all —
  `Pr = 0`, `T4 = +∞`. I record that (`T4 = inf`, `time = inf`) rather than drop it,
  because it is the honest value of that reading and it is exactly the failure mode
  HEUR-1's empty-coset condition exists to exclude. Conditioning on every coset
  being nonempty — which is what an implementer would do, resampling the offsets
  `v_i`, at an expected 1.07 draws (P-b) or 2.10 draws (P-a) at cell B — gives a
  finite value:

  | | P-b conditional | P-a conditional |
  |---|---|---|
  | cell A (floor) | 3.278 | 3.279 |
  | cell B (floor) | 20.246 | 19.908 |

  The per-coset Jensen deficit is 0.0028 bits at `C_0 = 8` and 0.101 / 0.0995 bits
  at `C_0 = 3`; multiplied by `m` that is 0.20 bits at cell A and **19.2 bits** at
  cell B. Cell B's `T4` is therefore an artefact of `C_0` being small enough that
  `log2 #Fb_i` has real dispersion: the standard deviation of `log2 λ` over the 190
  cosets is 7.9 bits, so even "the" geometric `T4` has an ~8-bit per-instance
  spread.
- **R4, Monte Carlo — expectation of the probability.** Neither R2 nor R3 is
  `E[Pr]`, which is what "the probability that a decomposition succeeds" most
  directly names if the factor base is redrawn. I sampled 200000 factor bases per
  (cell, parametrisation) — `2·popcount(getrandbits(2^{C_0}))` for P-a, exact; PTRS
  transformed rejection for P-b Poisson — formed `λ` per draw, averaged
  `1 − exp(−λ)`, and report both the unconditional average and the average
  conditional on no empty coset. Cell A: 3.115 bits, which sits between R2 and R3
  as it must. Cell B: 7.089 (P-b) / 7.801 (P-a) unconditional, 6.997 / 6.726
  conditional. `E[Pr]` is dominated by the upper tail of `λ` (the few percent of
  draws with `λ ≳ 1` saturate `Pr` at 1), which is why it sits 13 bits *below* the
  geometric reading.

So at cell A the whole of `T4` lives in `[0.000, 3.279]` (3.28 bits of ambiguity,
most of it the §3 rounding), and at cell B in `[0.027, 20.246]` — **20.22 bits**,
plus a `+∞` branch — driven by which expectation is taken and under which
parametrisation of HEUR-1. Every one of these is in `rederived-values.json` keyed by
reading. I do not pick one.

### 5.3 Cost bookkeeping

The charge `T1 + T2 + T3 + T4` is per-attempt cost × relations needed × inverse
success probability, in the log domain: one solve (`T1+T2`), times `#Fb` relations
(`T3`), times `1/Pr` attempts per relation (`T4`). That is the form
`agents/validator.md` §"Cost bookkeeping" requires, and the probability is taken
from the stated heuristic rather than assumed to be 1.

---

## 6. T5 and the charged time

`T5_frozen = T1`, `T5_dense = 2·T1`, both in field elements, by the statement.
Cell A: 56.562 / 113.124 (floor). Cell B: 62.294 / 124.587 (floor).

Charged time is `log2(2^{T1+T2+T3+T4} + 2^{ω·T3})`. The index-calculus linear
algebra term is **numerically inert at both cells**: `ω·T3` is 39.72 (cell A) /
31.71 (cell B) against a decompose step of 173–218, so the log-add contributes
`< 1e-38` bits and the reported `time` equals `T1+T2+T3+T4` to every decimal
reported. This matches Nagao's own remark that the linear algebra step is
"`O(n^w)` and very very small", and it means the log-add in the statement is a
formality here rather than a computation — worth recording, since a reader could
otherwise assume the second term does work.

Charged time, over all readings: cell A `[173.169, 176.198]`; cell B
`[197.576, 217.696]` (plus the `+∞` branch of R3-unconditional).

---

## 7. The van Oorschot–Wiener baseline

`W = 0.886 · 2^{n/2}` group operations, so `log2 W = 285.5 + log2 0.886 = 285.3254`
at `n = 571`. `T = W(1/M + 1/w)`, `Mem = 3n·max(w, M)`.

**time_only.** The statement declares the point `M = 1, w → ∞`: `T = W(1 + 1/w) → W`,
so the charge is `log2 W = 285.3254`. I record one thing about the framing: under
`time_only` the curve has **no interior Pareto minimum** — `inf_{w,M} T = 0`, since
`T → 0` as `w → ∞` at any fixed `M > 0`. So `log2 W` is the *total work*, charged at
a declared operating point, not a minimised time. The statement supplies that point
explicitly, so the quantity is determined; but "Pareto minimum … under time_only" is
not literally what is being computed, and a later reader comparing a time-only
margin against a time-minimised one would be comparing different objects.

**time_memory_product.** Minimise `T·Mem` over `(w, M)`:

```
T · Mem = 3n·W·(1/M + 1/w)·max(w, M) = 3n·W·(1 + max(w/M, M/w)) ≥ 6n·W,
```

with equality **iff `w = M`** — the whole diagonal ray, at any common value, not a
single point. The product is scale-invariant along it, which is why the minimum is a
locus rather than a point. So

```
min log2(T·Mem) = log2(6n) + log2 W = 11.7423 + 285.3254 = 297.0677 bits at n = 571.
```

I also record the variant in which vOW memory is counted in **points** rather than
bits (`Mem = max(w, M)`, dropping the `3n` bits-per-point factor): the minimum
becomes `log2 2 + log2 W = 286.3254`, i.e. 10.74 bits lower. It is recorded only
because the unit choice on the two sides is not symmetric (§8, A-6), not because I
think the points reading is the intended one.

---

## 8. Margins, and the ambiguity register

Margins are Nagao − vOW, positive meaning Nagao is worse. **No unit conversion is
applied** between F_2 operations and group operations, or between field elements and
bits: the `time_only` margin subtracts a count of F_2 operations from a count of
group operations, and the `time_memory_product` margin subtracts
(group ops × bits) from (F_2 ops × field elements). Both are therefore
convention-dependent in the sense this program has already written down, and the
figures should not be read as if the units matched. I say so here because the
statement instructs me to say so explicitly, and because it bounds what any margin
below can support.

Ranges over all readings (full table per reading in `rederived-values.json`):

| | cell A | cell B |
|---|---|---|
| `margin_time_only` | −112.16 … −109.13 | −87.75 … −67.63 |
| `margin_product_frozen` | −67.25 … −64.31 | −37.17 … −17.08 |
| `margin_product_dense` | −10.61 … −7.75 | +25.16 … +45.22 |

Two observations I record as arithmetic, not interpretation: every `time_only` and
every `frozen`-memory margin at both cells is negative under every reading I
considered; the `dense`-memory margin is negative at cell A under every reading and
positive at cell B under every reading. The sign at cell B under the dense reading
is therefore robust to the 20-bit `T4` ambiguity, while its magnitude is not.

### Ambiguity register

- **A-0 (procedural).** My assigned write scope was non-empty on arrival:
  `rederivation.md`, `rederived-values.json` and `scratch/` were already present,
  with mtimes after the stated start of this round. Attempt 1 is reported to have
  written nothing, so I could not establish their provenance without reading them,
  and reading them could have spent the blindness this task exists to buy. I moved
  them unread to `preexisting-unread/` and wrote fresh files. I did not open them
  and cannot say what they contain. A Coordinator comparing my values should treat
  that directory as unexamined by me.
- **A-1. Rounding of `m`.** `n/C_0` is not an integer at either cell and Nagao
  writes `m ~ n/C_0`. Worth 0.08 bits in `T1` but up to 3.03 bits (cell A) and 1.22
  bits (cell B) in the charged time via `λ = p^{m C_0 − n}`. Values given under
  floor / ceil / nearest / exact-real.
- **A-2. Which expectation (the material one).** Arithmetic `E[λ]`, geometric
  `E[log λ]`, and `E[Pr]` are three different quantities; the statement's phrase
  "λ = Π_i #Fb_i / #E … each `#Fb_i` a binomial count" does not choose among them.
  At a fixed rounding (floor) the expectation choice alone is worth 0.190 bits at
  cell A and **18.900 bits at cell B**; combined with A-1 and A-3 the `T4` range is
  3.279 (cell A) / 20.219 (cell B) bits, and the charged-time range 3.029 / 20.120.
  Plus a `+∞` branch (A-4).
- **A-3. Which binomial parametrisation.** HEUR-1 fixes the mean, not the law. P-b
  (Poisson `p^{C_0}`) and P-a (`2·Bin(2^{C_0}, 1/2)`, which is what HEUR-1's own
  2-to-1 justification implies) agree to 0.001 bits at cell A but differ by 0.34
  bits in the conditional geometric `T4` at cell B, and — far more consequentially —
  by a factor of 11.6 in `P[empty coset]`, hence 0.938 vs 0.475 in
  `P[all cosets nonempty]` at cell B.
- **A-4. Conditioning on a usable factor base.** Under any reading that takes an
  expectation of a logarithm, `T4` is `+∞` unconditionally and finite only
  conditional on no coset being empty. Whether the charge should include the
  expected `1/P[all nonempty]` factor-base redraws (1.07 draws at cell B under P-b,
  2.10 under P-a — negligible in bits, 0.09 / 1.07) is not determined by the
  statement. I report the conditional `T4` and the draw count separately, and add
  neither into the charged time.
- **A-5. `time_only` has no interior minimum.** `inf T = 0` over the vOW curve, so
  the declared point `M = 1, w → ∞` charges total work rather than a minimised time
  (§7). Determined by the statement's own declaration; recorded because the label
  "Pareto minimum" does not describe it.
- **A-6. Mixed units, twice over.** (i) No F_2-op/group-op conversion, as
  instructed. (ii) The product metric multiplies vOW's time (group ops) by its
  memory in *bits* (`3n` per point), while Nagao's product multiplies F_2 operations
  by memory in *field elements*. At `p = 2` an F_2 element is one bit only if
  bit-packed; stored one-per-machine-word it is 3–6 bits more per element, which at
  `T5_dense` would move `margin_product_dense` by that amount and nothing else does.
  I record the vOW-memory-in-points variant (10.74 bits) to expose the asymmetry.
- **A-7. Variable count `n(m−1)` vs `m·C_0 + n(m−2)`.** The statement's `N` is the
  `m·C_0 = n` slice of the paper's actual `EQS4` variable count. Immaterial here
  (≤ 4.3e-4 bits) but it is a genuine second reading, and it is the *kind* of
  substitution that has been load-bearing in this program before.
- **A-8. Monomial count with the field equations.** `C(N+4,4)` (with repetition) vs
  `Σ_{d≤4} C(N,d)` (square-free, as the field equations force). Agree to ~1e-5 bits
  at these `N`; recorded because they do not agree at small `N`.
- **A-9. `#Fb` vs `#Fb + 1` relations.** Algorithm 2 collects `#Fb + 1`. Worth
  ≤ 9.5e-4 bits.
- **A-10. The `ω·T3` log-add is inert.** `< 1e-38` bits at both cells. The statement's
  log-addition does no work here; the charged time is its first argument.

---

## 9. Verdict on my joint

**`holds`** — in the sense the task card defines: the quantity is derivable from the
statement and the cited sources *up to the ambiguities recorded above*, and I
produced a value under every reading I could defend. I reached no point where I
needed something outside the READ SCOPE.

I flag, without upgrading the verdict to `breaks`, that at cell B one of those
ambiguities (A-2/A-3/A-4) is worth 20.2 bits in `T4` and 20.1 bits in the charged
time. That is below the 46-bit ω-spread H-SEMBIN-4a80f3's C3 uses as its yardstick,
but of the same order as effects the previous round treated as decisive
(EV-SEMBIN-71e5cd O-6's 29.0 bits and the crossover move in O-7). A single `T4`
number at cell B is therefore not a
well-defined deliverable without its expectation convention and its HEUR-1
parametrisation attached. Whether that is a defect in the producer's artifact, in
the statement, or in neither is the Coordinator's composition to make, not mine —
I cannot see the producer's values by construction.

Self-checks for the machinery are in `rederived-values.json`'s source
(`scratch/rederive-output.json` → `self_checks`): `T4` at `λ = 1` equals
`−log2(1 − 1/e)` exactly; `log2 C(39974,4)` matches `4 log2 N − log2 24` to 3e-4;
`log2 W` and `log2 6n` match the hand values; the Poisson and exact-pairs empty
probabilities match `e^{−8}` and `2^{−8}` exactly; real and integer binomial logs
agree to 7e-11 bits.
