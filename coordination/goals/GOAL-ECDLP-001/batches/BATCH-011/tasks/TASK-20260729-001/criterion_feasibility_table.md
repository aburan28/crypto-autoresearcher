# EXP-YIELD-001 criterion feasibility table

Task: TASK-20260729-001. Goal: GOAL-ECDLP-001. Batch: BATCH-011.
Records frozen alongside this file: `H-YIELD-001` (status `specified`),
`experiments/EXP-YIELD-001/specification.yaml` (status `review_required`).

**Why this file exists.** `DEFER-BATCH009-003` requires a criterion feasibility
table inside every contract *before* it is frozen: every pre-registered success,
falsification, stopping and invalidation threshold is evaluated with shown
arithmetic at the exact cells that will actually run, and marked CAN FIRE or
CANNOT FIRE. A threshold that cannot fire at any runnable cell is not a
criterion. Two frozen contracts in this campaign died at review on exactly this
defect — `EXP-IC-001` v3's two-operation window, and `EXP-ENDO-001`'s branch that
could not succeed — and `DEC-20260728-003` R-5 struck `EXP-SUBRES-001`'s success
criterion S2 as unreachable *after* the compute was spent. This table is the
compensating control moved before the spend.

**Result of the exercise, up front.** Three criteria inherited from
`IDEA-20260727-006` CANNOT FIRE or CANNOT DISCRIMINATE at the cells that will
run. All three are removed or replaced here, before the freeze, with the
arithmetic shown. One of the three removals — the upward branch — is the branch
whose occurrence is the only event on the present frontier that would reopen a
prime-field exponent below one half.

**Authoring limits.** This file was written by a Coordinator session with **no
shell**: no git, no validator, no allocator, no interpreter. Every number below
is derived in place from stated definitions and is checkable on paper. No number
is imported from an unarchived probe, a recollection or an estimate. Where a
quantity depends on a prime or a curve that will only be fixed at execution, the
arithmetic uses an explicitly stated approximation with its error bounded, and
says so.

---

## 1. The cells that will actually run

**Definitions used throughout.** `p` is the field prime; `E/F_p` has **prime**
group order `N`; `L = round(p^beta)` is the x-interval length; the factor base is
`F = {P : x(P) in {0,...,L-1}}` with **measured** size `B = |F|`; `m` is the
arity; `S_m` is the set of sums of `m`-element multisets from `F`;
`h = B^m/(m! p)` is the counting heuristic; `C_all = C(B+m-1, m)`;
`C_red = sum_{k=1..m} C(B/2,k) C(m-1,k-1) 2^k` is the cancellation-free multiset
count; `P_pred = N(1-exp(-C_red/N)) + |S_(m-2)| exp(-C_red/N)` with `|S_0| = 1`
and `|S_1| = B`; `R = (|S_m|/N)/h`; `E = |S_m|/P_pred`.

**Arithmetic basis, stated rather than assumed.** The four primes are the
smallest primes at or above `2^k` for `k in {12,14,16,18}`; the exact values are
computed by the driver and recorded in the manifests. This table evaluates every
threshold at `p = 2^k`. The exact prime differs from `2^k` by well under 0.1 per
cent at every size, which cannot move any threshold below by more than the third
decimal. `N` is unknown until the curve is selected; by Hasse
`|N - (p+1)| <= 2 sqrt(p)`, so `p/N` lies within `2/sqrt(p)` of 1, i.e. within
3.13% (k=12), 1.56% (k=14), 0.78% (k=16), 0.39% (k=18). Every use of `p/N` below
uses those bounds, never a guessed `N`.

**Interval length `L = round(2^{k beta})` at the frozen beta grid**
(step 0.025 from 0.200 to 0.600). `B` is close to `L` — about half the x in the
interval admit points, each such x giving two — with fluctuation of order
`sqrt(L)`; **all criteria are evaluated on measured `B`, never on `L`**, and this
table uses `B = L` as its arithmetic basis.

| beta | k=12 | k=14 | k=16 | k=18 |
|---|---|---|---|---|
| 0.200 | 5 | 7 | 9 | 12 |
| 0.225 | 7 | 9 | 12 | 17 |
| 0.250 | 8 | 11 | 16 | 23 |
| 0.275 | 10 | 14 | 21 | 31 |
| 0.300 | 12 | 18 | 28 | 42 |
| 0.325 | 15 | 23 | 37 | 58 |
| 0.350 | 18 | 30 | 49 | 79 |
| 0.375 | 23 | 38 | 64 | 108 |
| 0.400 | 28 | 49 | 84 | 147 |
| 0.425 | 34 | 62 | 111 | 201 |
| 0.450 | 42 | 79 | 147 | 274 |
| 0.475 | 52 | 100 | 194 | 375 |
| 0.500 | 64 | 128 | 256 | 512 |
| 0.525 | 79 | 163 | 338 | 699 |
| 0.550 | 97 | 208 | 446 | 955 |
| 0.575 | 119 | 265 | 588 | 1305 |
| 0.600 | 147 | 338 | 776 | 1783 |

Census cell count: 17 beta x 4 sizes x 2 arities = **136 cells**.

---

## 2. Derivation D-1 — the counting bound, and what it does to the upward branch

**Claim.** Every decomposable target is the sum of at least one `m`-element
multiset from `F`, and the number of such multisets is exactly
`C_all = C(B+m-1, m) = B(B+1)...(B+m-1)/m!`. Hence

```
|S_m| <= min(C_all, N)
R = (|S_m|/N) / (B^m/(m! p)) <= (p/N) * (C_all * m! / B^m)
                              = (p/N) * prod_{j=0}^{m-1} (1 + j/B)  =:  R_max
```

This is a counting bound, not an expectation. It holds for every curve, every
prime, every interval and every arity. **The counting heuristic is therefore an
upper bound on the yield, up to a factor that tends to 1 as `B` grows.**

**`R_max` at the extreme cells of this design** (`p/N` bounded as in section 1):

| cell | m | B | prod (1+j/B) | p/N bound | R_max |
|---|---|---|---|---|---|
| k=12, beta=0.200 (smallest B in the whole design) | 3 | 5 | 1 x 1.2 x 1.4 = 1.680 | 1.0313 | **1.733** |
| k=12, beta=0.325 (smallest criterion-evaluable B, m=3) | 3 | 15 | 1.0667 x 1.1333 = 1.2089 | 1.0313 | 1.247 |
| k=18, beta=0.350 | 3 | 79 | 1.0127 x 1.0253 = 1.0383 | 1.0039 | 1.042 |
| k=12, beta=0.425 (smallest criterion-evaluable B, m=2) | 2 | 34 | 1.0294 | 1.0313 | 1.062 |
| k=18, beta=0.500 | 2 | 512 | 1.00195 | 1.0039 | 1.006 |

**The design-wide maximum of `R_max` over all 136 cells is 1.733**, attained at
the single smallest cell, and it *falls* toward 1 as `p` grows at fixed `beta`.

### Verdict on the inherited upward criterion

> `IDEA-20260727-006` prediction 1 and falsification condition 1: *"a ratio
> exceeding 2.0 and increasing with p across at least three consecutive sizes"*.

**CANNOT FIRE.** `R > 2.0` requires `R_max > 2`, i.e. `prod (1+j/B) (p/N) > 2`,
which at `m = 3` requires roughly `B < 3` and at `m = 2` requires `B < 1`. Every
cell in the design has `B >= 5`. Worse for the criterion: the ceiling *shrinks*
with `p` at fixed `beta`, so "an excess growing in p" is bounded by a quantity
that decreases to 1. The criterion cannot fire at any cell, at any size, under
any outcome — and, since D-1 is scale-free, not at cryptographic sizes either.

**Disposition: REMOVED as a success/falsification criterion, RETAINED as
invalidation rule INV-1.** An observation of `R > R_max` is mathematically
impossible, therefore it is an implementation defect: the run is INVALID and it
is never an observation of outcome (b).

**What this costs the batch, stated plainly and not softened.** Outcome (b) —
yield exceeding the heuristic by a factor growing in `p` — is *the only
measurable event on the present frontier that would reopen a prime-field exponent
below one half* (`GOAL-ECDLP-001` status note, BATCH-011 opening). D-1 shows it
cannot occur **on this metric, for this decomposition shape, at any scale**. That
is an answer to the exponent question, in the pessimistic direction, obtained by
counting rather than by measurement. It is scoped in `H-YIELD-001`
interpretation limits to the fixed-factor-base, fixed-arity, unweighted
decomposition shape, and it says nothing about weighted decompositions, adaptive
factor bases, decomposition *multiplicity*, or extension fields. The measurement
that remains is the *size and trend of the shortfall*, which is outcome (a)
versus outcome (c).

---

## 3. Derivation D-2 — saturation, and what it does to the downward branch

`h = B^m/(m! p)` is the heuristic decomposition probability. It exceeds 1 —
the heuristic predicts every target decomposes — once `B^m > m! p`, i.e. once

```
beta > beta*(m) = (1 + log_p(m!)) / m
```

| m | k=12 | k=14 | k=16 | k=18 |
|---|---|---|---|---|
| 2 | 0.5417 | 0.5357 | 0.5313 | 0.5278 |
| 3 | 0.4051 | 0.3982 | 0.3930 | 0.3892 |

Under the occupancy null, `R_null = (1 - exp(-h))/h`, so `R` is *forced* down as
`h` grows with no structural content at all: `R_null` = 0.995 at h=0.01, 0.952 at
h=0.1, 0.885 at h=0.25, **0.787 at h=0.5**, 0.500 at h=1.594.

### Verdict on the inherited downward criterion

> `IDEA-20260727-006` prediction 1: *"the competing outcome (c) is a ratio below
> 0.5 and decreasing"*.

**CANNOT DISCRIMINATE.** `R < 0.5` is *forced by saturation alone* at every cell
with `h >= 1.594`, i.e. `beta >= 0.5 + 0.8365/k` at m=2 and
`beta >= (3.258 + k)/(3k)` at m=3:

| m | fires by saturation alone at |
|---|---|
| 2 | beta >= 0.5697 (k=12), 0.5598 (k=14), 0.5523 (k=16), 0.5465 (k=18) |
| 3 | beta >= 0.4238 (k=12), 0.4109 (k=14), 0.4012 (k=16), 0.3936 (k=18) |

That is **42 of the 136 cells** (m=3: beta 0.425–0.600 at all four sizes, plus
beta 0.400 at k=18 — 33 cells; m=2: beta 0.575–0.600 at all four sizes, plus
beta 0.550 at k=18 only, since 0.550 sits just below the k=16 threshold of
0.5523 — 9 cells), at which the criterion returns "outcome (c)" *whatever the
curve does*. Conversely, inside the unsaturated band
(`h <= 0.5`, so `R_null >= 0.787`), `R < 0.5` requires the structure to remove at
least 36.5% of the occupancy-predicted reachable targets — an insensitive
threshold sitting roughly 35 chance standard deviations out (section 5).

**Disposition: REPLACED.** All criteria are moved onto the occupancy-normalised
efficiency `E = |S_m|/P_pred`, whose null value is 1 **by construction** rather
than by fitting, and are restricted to *criterion-evaluable cells* defined as

```
h <= 0.5   AND   C_red >= 500
```

---

## 4. Derivation D-3 — the certification threshold lies above saturation, so stage 2 is cut

`IDEA-20260727-006` stage 2 locates an empirical crossover `beta` and compares it
with the derived `beta_cert(m) = (m+1)/(2m)` — 0.75 at m=2, 0.6667 at m=3.

Compare with `beta*(m)` from D-2:

```
beta_cert(m) > beta*(m)
  <=>  (m+1)/2  >  1 + log_p(m!)
  <=>  (m-1)/2  >  log_p(m!)
  <=>  p^{(m-1)/2}  >  m!
  <=>  p  >  (m!)^{2/(m-1)}
```

| m | 2 | 3 | 4 | 5 | 6 | 10 | 20 |
|---|---|---|---|---|---|---|---|
| threshold `(m!)^{2/(m-1)}` | 4.0 | 6.0 | 8.3 | 11.0 | 13.6 | 24.5 | 86.2 |

So for every arity `m` and every prime `p` above a threshold that grows only like
`m^2/e^2`, **the Weil-certification threshold lies strictly above the saturation
threshold**. At the sizes here (`p >= 4096`, `m in {2,3}`) it holds with three
orders of magnitude of margin; at cryptographic `p` it holds for every arity up
to about `e sqrt(p)`. (The inequality does reverse for a fixed small `p` and very
large `m` — at `p = 31` it fails from about `m = 16` — and that caveat is stated
rather than hidden.)

The content: at `beta = beta_cert(m)` the per-target decomposition count is about
`p^{(m-1)/2}`, so certification is only available deep inside the regime where
*every* target decomposes many times over and the yield question is trivial.

**Verdict on the inherited crossover criterion**

> `IDEA-20260727-006` prediction 2 and falsification condition 2: *"the empirical
> crossover beta agrees with (m+1)/(2m) within 0.05 for m in {2,3}"*.

**CANNOT FIRE.** `beta_cert(2) = 0.75` and `beta_cert(3) = 0.6667` both exceed
the top of the frozen grid (0.600) and, more fundamentally, both exceed
`beta*(m)` at every size, so the deviation there is dominated by the cap
`|S_m| <= N` rather than by any Weil error term. Extending the grid would not
repair it: the criterion is unevaluable *by D-3*, not by budget.

**Disposition: STAGE 2 IS CUT, in addition to the stages 4 and 5 already cut by
the BATCH-011 queue.** Consequence, recorded so no later record may overstate the
batch: **EXP-YIELD-001 does not measure `beta_cert`, does not test the
`(m+1)/(2m)` derivation, and does not adjudicate `IDEA-20260727-006`'s headline
gap claim** (which is separately undecidable here as `DEFER-BATCH011-002`, since
`beta_adm` needs an `omega_LA` that has never been measured). Heuristic H3 stays
UNVALIDATED (`DEFER-BATCH011-001`) and is recorded in `H-YIELD-001` as **not
load-bearing**, because this design invokes no Lang-Weil main term at all.

---

## 5. The criterion-evaluable cells, cell by cell

`C_red >= 500` is required so that the discreteness of `|S_m|` and the chance
fluctuation of the occupancy null are both far below the criterion band.

`C_red(m=2) = B^2/2`; `C_red(m=3) = B + B(B-2) + B(B-2)(B-4)/6`.

**m = 2** (band `beta <= 0.500` at every size, since `h <= 0.5 <=> B <= sqrt(p)`;
`C_red >= 500 <=> B >= 32`):

| beta | k=12 B / C_red | k=14 | k=16 | k=18 | evaluable sizes |
|---|---|---|---|---|---|
| 0.200–0.275 | 5–10 / 12–50 | 7–14 / 24–98 | 9–21 / 40–220 | 12–31 / 72–480 | 0 of 4 |
| 0.300 | 12 / 72 | 18 / 162 | 28 / 392 | 42 / 882 | 1 of 4 |
| 0.325 | 15 / 112 | 23 / 264 | 37 / 684 | 58 / 1682 | 2 of 4 |
| 0.350 | 18 / 162 | 30 / 450 | 49 / 1200 | 79 / 3120 | 2 of 4 |
| 0.375 | 23 / 264 | 38 / 722 | 64 / 2048 | 108 / 5832 | **3 of 4** |
| 0.400 | 28 / 392 | 49 / 1200 | 84 / 3528 | 147 / 10804 | **3 of 4** |
| 0.425 | 34 / 578 | 62 / 1922 | 111 / 6160 | 201 / 20200 | **4 of 4** |
| 0.450 | 42 / 882 | 79 / 3120 | 147 / 10804 | 274 / 37538 | **4 of 4** |
| 0.475 | 52 / 1352 | 100 / 5000 | 194 / 18818 | 375 / 70312 | **4 of 4** |
| 0.500 | 64 / 2048 | 128 / 8192 | 256 / 32768 | 512 / 131072 | **4 of 4** |

**m = 3** (band `beta <= 0.3627`, the tightest of 0.3774 / 0.3711 / 0.3664 /
0.3627, so the grid's top in-band point is 0.350):

| beta | k=12 B / C_red | k=14 | k=16 | k=18 | evaluable sizes |
|---|---|---|---|---|---|
| 0.200 | 5 / 22 | 7 / 60 | 9 / 124 | 12 / 292 | 0 of 4 |
| 0.225 | 7 / 60 | 9 / 124 | 12 / 292 | 17 / 824 | 1 of 4 |
| 0.250 | 8 / 88 | 11 / 226 | 16 / 688 | 23 / 2036 | 2 of 4 |
| 0.275 | 10 / 170 | 14 / 462 | 21 / 1542 | 31 / 5424 | 2 of 4 |
| 0.300 | 12 / 292 | 18 / 978 | 28 / 3668 | 42 / 12362 | **3 of 4** |
| 0.325 | 15 / 568 | 23 / 2036 | 37 / 8454 | 58 / 32538 | **4 of 4** |
| 0.350 | 18 / 978 | 30 / 4510 | 49 / 19624 | 79 / 82200 | **4 of 4** |

**Totals: 27 criterion-evaluable cells at m=2 and 16 at m=3 — 43 of 136.**
**Columns carrying at least three field sizes: six at m=2 (beta 0.375–0.500) and
three at m=3 (beta 0.300, 0.325, 0.350).** A trend criterion requiring three or
more sizes therefore has **nine** columns to fire in. Had the criteria demanded
four sizes at m=3, only two columns would have qualified; had the beta grid used
the source record's 0.05 step, only one would have. **That is precisely the class
of defect this table exists to catch, and it was caught before the freeze.**

### Chance fluctuation of `E`, so the bands can be read as structure bands

For `C` balls in `N` bins, `Var(distinct) = N e^{-L}(1 - (1+L)e^{-L})` with
`L = C/N`, against mean `N(1 - e^{-L})`.

| cell | N | C_red | L | relative sd of E |
|---|---|---|---|---|
| k=18, m=2, beta=0.500 (largest) | 262144 | 131072 | 0.500 | 0.12% |
| k=18, m=3, beta=0.350 | 262144 | 82200 | 0.314 | 0.16% |
| k=12, m=3, beta=0.325 (smallest evaluable) | 4096 | 568 | 0.139 | **1.05%** |
| k=12, m=2, beta=0.425 | 4096 | 578 | 0.141 | 1.04% |

The largest chance sd over the evaluable set is about **1.05%**. So the
plus-or-minus 10% band is a **9-sigma** band and the 0.80 threshold is a
**19-sigma** threshold: both are structure thresholds, not noise thresholds. The
driver additionally reports the *empirical* null sd per cell from the occupancy
Monte Carlo, and any evaluable cell whose empirical sd exceeds 2% is reported as
NOISE-LIMITED and excluded from criterion evaluation with its exclusion recorded.

---

## 6. Every pre-registered threshold, evaluated

| # | criterion (as frozen) | evaluated at | verdict |
|---|---|---|---|
| S1 | `E in [0.90, 1.10]` at every criterion-evaluable cell, AND `|slope of log E vs log p| <= 0.05` with 95% interval containing 0 in every column of >= 3 sizes, AND calibration NOT-VOID, AND null recovered, AND no invalidation fired | 43 cells, 9 columns | **CAN FIRE.** Null value of E is exactly 1 by construction; chance sd <= 1.05%; nothing forces E outside the band. |
| F1 | in >= 1 column of >= 3 sizes: `E <= 0.80` at the largest size AND `E` non-increasing across sizes AND slope `<= -0.05` with 95% interval excluding 0, AND the deviation shrinks under factor-base randomisation | 9 columns | **CAN FIRE.** Nothing bounds `E` below; `E <= 0.80` is 19 sigma from the null and well inside the achievable range (`E` can in principle approach 0). Genuinely reachable negative outcome. |
| F2 | `E` outside `[0.90,1.10]` at more than one third of evaluable cells with no monotone p-trend and no consistent sign -> null model incomplete, verdict INCONCLUSIVE | 43 cells | **CAN FIRE.** Requires >= 15 of 43 cells out of band. |
| INV-1 | `R > R_max`, or `|S_m| > min(C_all, N)`, or `|S_m| < |S_(m-2)|` at any cell | 136 cells | **CAN FIRE ONLY ON A DEFECT.** Each is mathematically impossible (D-1). Retained deliberately as an implementation self-check with real teeth: it is the class of error that would manufacture a false outcome (b). Never evidence. |
| INV-2 | calibration leg fails to recover EV-STR-001's per-cell penalty within a factor 2 in >= 5 of 6 cells, or fails the monotone-in-n / superlinear-in-m trend | 6 calibration cells | **CAN FIRE** (section 7). Census numbers VOID, not negative. |
| INV-3 | discrete-log table integrity control: any of 10^4 sampled multisets disagrees between curve-side and DL-image sum | 4 sizes | **CAN FIRE.** Deterministic check; a single mismatch invalidates. |
| INV-4 | occupancy Monte Carlo fails to recover `P_pred` within 3 empirical sd at any evaluable cell | 43 cells | **CAN FIRE.** It tests the null model itself, which is a formula this contract derives rather than cites. |
| INV-5 | destroy-parameter rule: a deviation of `E` from 1 that does NOT shrink under factor-base randomisation is an estimator/curve artifact, not an interval-structure signal | 43 cells x 3 FB draws | **CAN FIRE.** Blocks an interval-structure reading in either direction. Stated as a rule, not as a criterion. |
| ST-1 | per-cell projected op count above 5 x 10^8 -> cell SKIPPED_BUDGET | 136 cells | **CAN FIRE** at the largest m=3 cells only (section 8); no criterion-evaluable cell is at risk. |
| ST-2 | 5400 s / 8 GB / 6 runs cap -> stop, name unreached cells, run declared priority order | all | **CAN FIRE.** Reduced-scope core declared in the contract. |
| — | *(removed)* `R > 2.0` and growing across 3 sizes | 136 cells | **CANNOT FIRE — REMOVED** (D-1). Design-wide ceiling 1.733. Demoted to INV-1. |
| — | *(removed)* `R < 0.5` and decreasing | 136 cells | **CANNOT DISCRIMINATE — REPLACED** by F1 on `E` (D-2). Fires by saturation alone at 42 cells. |
| — | *(removed)* empirical crossover vs `(m+1)/(2m)` within 0.05 / 0.10 | 136 cells | **CANNOT FIRE — REMOVED, STAGE 2 CUT** (D-3). `beta_cert` lies above `beta*` at every size and above the grid. |

**Every removal above is a change made BEFORE the freeze and BEFORE any data
exists.** None is a post-hoc adjustment, and no threshold below was chosen after
seeing an outcome; there are no outcomes.

---

## 7. Calibration leg feasibility (INV-2)

The leg runs in `EV-STR-001`'s own regime and nowhere else:
`B = ceil(sqrt(n))`, `m in {3,4}`, `n in {211, 1009, 4099}`, shift set
`D = {1..64}`, AP supports `{x, x+d, ..., x+(m-1)d}` as defined in
`experiments/EXP-STR-001/specification.yaml`. The recovered quantity is
`C(B,m) / supply`, against that record's per-cell medians.

Consistency check of the target figures against `EV-STR-001`'s own reported
`ap_supply` medians (28/8 at n=211, 124/40 at n=1009, 477/154 at n=4099 for
m=3/4) and `B = 15 / 32 / 64.5`:

| n | m | C(B,m) | supply median | C(B,m)/supply | EV-STR-001 median penalty | agreement |
|---|---|---|---|---|---|---|
| 211 | 3 | C(15,3)=455 | 28 | 16.3 | 17.5 | within 1.08x |
| 211 | 4 | C(15,4)=1365 | 8 | 170.6 | 214.9 | within 1.26x |
| 1009 | 3 | C(32,3)=4960 | 124 | 40.0 | 41.9 | within 1.05x |
| 1009 | 4 | C(32,4)=35960 | 40 | 899.0 | 924.5 | within 1.03x |
| 4099 | 3 | C(65,3)=43680 | 477 | 91.6 | 87.8 | within 1.04x |
| 4099 | 4 | C(65,4)=677040 | 154 | 4396.4 | 4128.6 | within 1.06x |

All six cells reconcile to better than 1.3x — the residual being the difference
between a ratio of medians and a median of ratios over six seeds. So a correct
reimplementation is expected to land inside the factor-2 window in 6 of 6 cells,
and the invalidation rule is a **real** test rather than a formality: it can fail,
and it would fail loudly if the AP supply were counted over the wrong support set.

**Two things stated rather than glossed.** (i) The penalty spans **17.5x to
4128.6x** and grows with `n` at fixed `m` and superlinearly in `m` at fixed `n`;
**the single figure 17.5x is never characteristic** and a single fixed threshold
would be met trivially at five of six cells, which is why the rule is per-cell
plus two trend clauses. (ii) The calibration convention (AP supports,
`B = ceil(sqrt(n))`, `D = {1..64}`) is **different** from the census convention
(x-interval, `B = p^beta`), so any comparison between the two legs is
**QUALITATIVE ONLY** and is labelled as such in the run record; treating
`EV-STR-001`'s figures as a cross-convention reproduction target would be a
category error and would manufacture a false calibration failure.

**Named execution risk.** The exact admissibility predicate for an AP support
must be resolved from the committed `EXP-STR-001` contract. If it cannot be
resolved unambiguously there, the Executor **STOPS AND REPORTS**; a guessed
predicate would manufacture a calibration verdict in either direction.

---

## 8. Does the budget carry the cells? (5400 s, 8 GB, six runs)

The census is computed **in the discrete-logarithm image**: one full DL table per
field size, built by walking `N` multiples of a fixed generator, after which an
`m`-sum is an integer addition modulo `N` and set membership is a bit test.
`S_2 = distinct(S_1 + F)` and `S_3 = distinct(S_2 + F)`, so the cost of a cell is
`|S_1| B + |S_2| B <= (B + min(B^2/2, N)) B` modular additions and the memory is
one `N`-bit set.

| item | count | note |
|---|---|---|
| DL tables, all four sizes | 4096 + ~16.4k + ~65.5k + ~262.1k ~= 348k point additions | seconds |
| largest single cell (k=18, beta=0.600, m=3, B=1783) | 262144 x 1783 = **4.67 x 10^8** modular adds | vectorised: seconds; the ST-1 cap of 5 x 10^8 sits just above it |
| all m=3 cells, k=18 | ~1.4 x 10^9 | dominated by the top four beta |
| all m=2 cells, all sizes | < 10^7 | negligible |
| occupancy Monte Carlo, 43 evaluable cells x 30 replicates | < 10^8 draws | seconds |
| uniform-FB null, 43 evaluable cells x 3 draws | < 10^7 | the evaluable cells are the *small-B* ones |
| calibration leg, 6 cells x 6 seeds | p x 64 x m candidate APs per cell, p <= 4099 | < 10^7 |
| baselines, 4 sizes x 16 targets | rho 0.886 sqrt(N) <= 454 ops; BSGS ~2 sqrt(N) <= 1024 ops | < 10^5 total |

**Memory.** Peak is the DL dictionary at k=18 (about 262k entries) plus one
32 KB bit set plus chunked arrays: **well under 1 GB against an 8 GB cap**.

**Verdict: the budget carries every cell with a wide margin, and the binding cost
of this experiment is implementation time, not compute.** ST-1 can only bind at
the two largest m=3 saturation cells, none of which is criterion-evaluable. If it
binds anyway, the declared reduced-scope core is: all criterion-evaluable cells at
m=2 and m=3, both nulls, the calibration leg and the baselines — i.e. **every cell
any criterion is evaluated at survives the reduced scope**.

---

## 9. RC-7 — matched baseline position, stated before the freeze

In one unit: **one elliptic-curve point addition or doubling**.

| method | time | memory |
|---|---|---|
| Pollard rho with negation | `0.886 sqrt(N)` group operations (<= 454 at k=18) | `N^{o(1)}` — O(1) stored points |
| BSGS | `~2 sqrt(N)` group operations (<= 1024 at k=18) | `sqrt(N)` stored group elements (512 at k=18) |
| EXP-YIELD-001 census, per instance | `>= N` (the DL table alone) plus `min(C_red,N) B` per cell | `O(N)` bits |

Both baselines are **MEASURED** at these toy sizes, over 16 targets per size,
each rho solve carrying a verified discrete-log certificate — not merely modelled
— and the model values above are reported beside the measurements as a
known-answer calibration.

**The census costs more group-equivalent operations than solving the instance
outright.** The ratio census-ops / rho-ops is expected to be far above 1 (of
order `10^2`–`10^6`), and it is reported per instance precisely so that no reader
can mistake a yield measurement for an attack result. A ratio below 1 would be a
red flag about the accounting, not an attack.

---

## 10. RC-8 — DETERMINED / SAMPLED labels

| quantity | label |
|---|---|
| `B`, `C_all`, `C_red`, `h`, `|S_m|`, `R`, `P_pred`, `E`, `R_max` at every census cell | **DETERMINED** (exhaustively counted or exact closed form) |
| collision multiplicity profile, m=2, all cells | **DETERMINED** |
| collision multiplicity profile, m=3, cells with `C_all <= 5 x 10^7` | **DETERMINED** |
| collision multiplicity profile, m=3, larger cells | **SAMPLED** (10^6 uniform multisets) |
| occupancy Monte-Carlo null mean and sd | **SAMPLED** (10–30 replicates per cell) |
| uniform-random factor-base null `E` | **DETERMINED per drawn factor base, SAMPLED over 3 draws** |
| AP calibration supply per cell per seed | **DETERMINED**; the median over 6 seeds is **SAMPLED** |
| rho and BSGS operation counts | **MEASURED** over 16 targets per size; the `0.886 sqrt(N)` and `2 sqrt(N)` positions are **DERIVED_MODEL** |
| any fitted slope of `log E` against `log p` | **DERIVED_FIT** over DETERMINED inputs — this third label is an explicit, declared extension of RC-8, not a silent departure from it |

Nothing in this contract is labelled DETERMINED that is in fact estimated.

---

## 11. What this table does not establish

- It is **arithmetic on a design**, not a measurement. No curve has been chosen,
  no run exists, and nothing here is evidence for or against any hypothesis.
- D-1 and D-3 are **derivations made in place**, elementary and near-certainly
  folklore. **No novelty is claimed for either, and no external source was
  retrieved.** They are offered to the independent pre-execution review
  (`TASK-20260729-003`) to be **re-derived**, not adjudicated by quotation.
- Every table entry that depends on `p` uses `p = 2^k`; every entry that depends
  on `N` uses only the Hasse bound. No curve parameter, group order or prime is
  asserted.
- `EXP-YIELD-001` **moves no exponent and is an exponent-deciding screen,
  expressly not an exponent-targeting mechanism under `docs/target-result-profile.md`
  rule A1, and no downstream record may quote it as target-class.** It meets no
  `GOAL-ECDLP-001` completion criterion under any outcome, changes no existing
  hypothesis status, and is capped at **TOY** claim tier.
