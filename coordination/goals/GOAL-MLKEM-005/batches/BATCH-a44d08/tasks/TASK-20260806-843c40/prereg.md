# BATCH-a44d08 pre-registration — `k != d/2`, the AM-3 gate, and F-A1's replacement

TASK-20260806-843c40 / BATCH-a44d08 / GOAL-MLKEM-005
Executor artifact. **Claim tier TOY.** Nothing in this document, and nothing any
measurement it governs can produce, bears on ML-KEM security, on any FIPS 203
parameter set, or on any attack cost.

Governing authority: `ledger/decisions/DEC-20260806-14ac13.yaml`, amendments
**AM-3** (a monotonicity criterion must declare a computed false-failure rate and
a multiplicity policy before any data), **AM-4** (an adjudicator must be shown
invariant under the transformations that preserve the object it adjudicates), and
**AM-5** (`D_A(beta_2)/D_A(beta_1)` at fixed reduction is not an admissible
observable and may not be frozen about again). AM-1's 13-point `t` grid is
**RETAINED** and is not re-litigated anywhere below.

---

## 0. What this document is, and what was NOT done to produce it

This is the complete frozen specification of three measurements:

* **Section A** — `k != d/2`, the discriminating test between L2's `beta <= k`
  spill boundary and the superseded `beta <= d-k` mechanism (TASK-20260806-3084bc).
* **Section B** — AM-3, the replacement for the withdrawn G3 tolerance
  (TASK-20260806-e17677).
* **Section C** — the matched-`V` cross-family comparison, F-A1's replacement
  (TASK-20260806-c973e6).

**No measurement of any kind was performed in producing it.** No lattice was
generated, no lattice was reduced, no GSO frame was formed, no CBD draw was
sampled, no arm statistic was computed, no quantile was estimated, no `V`, `W` or
`D` was evaluated, and no Monte-Carlo null was run. Two computations were
performed and both are pure mathematics with no research datum in them:

1. **Closed-form algebra** on the models of §A.2, cross-checked against `V`
   values already committed in `BATCH-f19c37/tasks/TASK-20260806-ca4377/report.md`.
   Reading a committed number and doing algebra with it is not a measurement.
2. **Student-`t_7` tail probabilities and quantiles** (§B.3), computed from the
   elementary odd-degrees-of-freedom closed form and cross-checked by independent
   numerical quadrature of the `t_7` density. These are mathematical constants.
   Anyone can recompute them; §B.3 gives the formula.

Every number below is (a) fixed by `DEC-20260806-14ac13` or an earlier committed
decision — marked **[carried]**; (b) quoted from a committed artifact with its
source named — marked **[quoted: source]**; (c) derived here in closed form from
(a) and (b) — marked **[derived here]**; or (d) a threshold set here, with its
justification stated — marked **[set here]**.

**Category (c) is the one to audit hardest**, and it is flagged at every use. A
derivation made by the same agent that will not run the measurement is still a
claim; §A.2 states exactly which parts are rigorous and which are models, and the
measurement is required to report the disagreement rather than absorb it.

This task is split from the three measurements so that the freeze is notarized by
an external git record rather than self-reported. TASK-20260806-0a1072 snapshot-
commits this file and `prereg_sha256.txt` **before** TASK-20260806-3084bc,
-e17677 or -c973e6 is dispatched. Each measurement re-hashes this file and
**aborts on mismatch**. That pattern is carried unchanged from BATCH-f19c37,
where the validator confirmed it closed the notarization gap by construction
**[quoted: `validation_report.yaml` item_1]**.

---

## 1. Carried unchanged, and the one place a successor must not be misled

**[carried]** from `DEC-20260805-4823db` via BATCH-436ddd and BATCH-f19c37:

* `q = 3329`; error law CBD_{eta=2} with `mu_4 = 2.5` exactly; `N = 2^20` error
  draws per cell; frozen estimator `q_emp(p) = sort(R)[round(p*N)-1]`, so index
  `1023` (0-based) at `p = 2^-10`; `8` draws per arm; gate factor `4.0` in
  `SE_diff` units.
* Statistic `R = ||Q^T e||^2 / ||e||^2`, `Q` the orthonormal tail-`beta` GSO
  frame taken as the last `beta` columns of `Q` from `QR(B^T)`.
* `V(Q) = sum_a (P_aa - beta/d)^2`, `P = Q Q^T`, exact, zero error draws, with
  the exact Haar expectation `mu_0 = 2 beta (d-beta)/(d (d+2))` — a theorem, the
  validator re-derived it independently from `P_aa ~ Beta(beta/2,(d-beta)/2)` and
  confirmed it bit-exactly in four cells plus a 20,000-frame Monte Carlo
  **[quoted: `validation_report.yaml` item_4]**.
* Seed scheme, unchanged and **not modified by this document**:
  `seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i`;
  `seed_error(d) = 20260805 + d`;
  `seed_haar(d,beta,j) = 900000 + d*1000 + beta*10 + j`;
  `seed_graded(d,beta,j) = 500000 + d*1000 + beta*10 + j`;
  `seed_gauss_error(d) = 20260806 + d`.
  **The seeds are the cache.** No `.npz` reduction cache exists in the
  repository; 32 of 32 reductions regenerate at max deviation `0.0` against both
  prior batches **[quoted: `report.md` §3]**. Sections B and C reuse exactly
  these five families and change none of them; §B.6 and §C.10 say which.

**The one thing a successor must not be misled about.** `V` is a property of a
basis **presentation**, not of a lattice, and AM-4 refuses `V`-style statistics as
**adjudicators** for that reason: the red team showed an ambient isometry assigns
three different P3 verdicts to one lattice **[quoted: `red_team_report.md` §3.3]**.
Sections A and C use presentation-dependent statistics deliberately, and the
scope is correspondingly narrow: **both mechanisms under test in Section A are
themselves claims about where the departure sits in the canonical q-ary
presentation**, so a presentation-dependent statistic is the matching instrument
and not a category error. Neither section proposes a statistic as an adjudicator
of any hypothesis about lattices, neither claims AM-4 admissibility, and neither
may be cited as having established one. §A.9, §B.8 and §C.9 restate this against
each section's own failure mode.

---

# SECTION A — `k != d/2`

## A.0 The question, and why four batches structurally could not answer it

L2 locates the departure in a `beta`-dimensional subspace confined to a
`k`-dimensional coordinate block, putting the spill boundary at `beta <= k`. The
superseded mechanism (the "`q*I` story") put it at `beta <= d - k`
**[quoted: BATCH-f19c37 prereg §6.4]**. Every cell measured in four batches has
`k = d/2`, where `k = d - k`, so the two boundaries are the same number.

**The card asks for `k != d/2` AND `k != d-k`. These are one condition, not two:**
`k = d - k` if and only if `k = d/2`. I record that rather than pretending to
satisfy two constraints, and I state the non-degeneracy conditions that actually
bind in §A.4.

This is named as unevaluated in five records — `EV-MLKEM-94f036`, the AM-1
`could_not_evaluate` block, `DEC-20260806-00deff` `next_actions`, the AM-2 report
§8.5, and validator finding V-8 — and has never been run **[quoted:
`DEC-20260806-14ac13` next_actions]**.

## A.1 The two mechanisms, stated so that each can lose

Write `m_lead(Q) = sum_{a <= k} P_aa`, the frame mass in the leading `k`
coordinate block, and

```
W(Q) = m_lead(Q) - beta*k/d
```

`W` is exact, deterministic, costs no error draws, and is the red team's degree-1
statistic **[quoted: `red_team_report.md` §3.4]**. `0 <= m_lead <= min(k, beta)`
is forced for every rank-`beta` orthogonal projector, since `P_aa in [0,1]` and
`sum_a P_aa = beta`.

**Mechanism L2 — the departure is confined to the LEADING `k`-block.** The frame
puts as much mass as it can in the leading block, saturating when the block is
full:

```
m_L2(beta)  = beta          for beta <= k
            = k             for beta >  k
W_L2(beta)  = beta*(d-k)/d  for beta <= k
            = k*(d-beta)/d  for beta >  k
```

**Mechanism SUP — the superseded mechanism, the departure is confined to the
TRAILING `d-k` block.** Mirror image:

```
m_SUP(beta) = 0                    for beta <= d-k
            = beta - (d-k)         for beta >  d-k
W_SUP(beta) = -beta*k/d            for beta <= d-k
            = -(d-k)*(d-beta)/d    for beta >  d-k
```

Both are **[derived here]** from the one-line statement of each mechanism plus
the forced constraint `0 <= m_lead <= min(k,beta)`. They are continuous, they
agree with the mechanisms' stated boundaries by construction, and each has a
turning point exactly at its own boundary: `W_L2` attains its **maximum** at
`beta = k`; `W_SUP` attains its **minimum** at `beta = d-k`.

**This is the whole discriminating content, and it is why `k = d/2` is fatal:**
the two turning points sit at `k` and at `d-k`, which are the same `beta` when
and only when `k = d/2`.

## A.2 The closed-form `V` shapes, and what they show about the degeneracy

For a frame whose mass is confined to a block of size `m` and spread Haar-like
within it, **[derived here]**:

```
confined  (beta <= m):  V_0 = beta^2 (d-m) / (m d)          + 2 beta (m-beta) / (m (m+2))
saturated (beta >  m):  V_0 = m (d-beta)^2 / (d (d-m))      + 2 (beta-m)(d-beta) / ((d-m)(d-m+2))
```

The two branches agree at `beta = m` (both give `m(d-m)/d`), and the pair is
exchanged by `beta <-> d-beta`, `m <-> d-m`. The first term is the between-block
dispersion; the second is the within-block Haar dispersion, the same
`2 beta (m-beta)/(m(m+2))` that `mu_0` is for `m = d`.

**Cross-check against committed values, on the unreduced arm at `k = d/2`**
(model computed here; measured values **[quoted: `report.md` §4, §7, §9]**):

| `d` | `k` | `beta` | model `V` | committed `V` | relative |
|---|---|---|---|---|---|
| 100 | 50 | 30 | 9.4615 | 9.362794 | +1.05 % |
| 100 | 50 | 40 | 16.3077 | 16.244628 | +0.39 % |
| 100 | 50 | 50 | 25.0000 | 24.995 | +0.02 % |
| 100 | 50 | 60 | 16.3077 | 16.269 | +0.24 % |
| 140 | 70 | 30 | 6.9048 | 6.750435 | +2.29 % |
| 140 | 70 | 40 | 11.9048 | 11.807462 | +0.82 % |

The model is **systematically high by 0.02–2.29 %** and I record that as a known
defect of the model rather than rounding it away. `beta = 60 > k = 50` at
`d = 100` is the one committed point past a spill boundary, and the saturated
branch reproduces it to 0.24 %.

**The degeneracy, exhibited exactly.** Substituting `m = k` and `m = d-k` into the
formulas above, the leading terms are equal iff `(d-k)/k = k/(d-k)` iff
`k = d/2`. So at `k = d/2` the two mechanisms predict **the identical `V` at every
`beta`** — I verified this numerically over the whole Section A grid, and every
`k = d/2` row returns `V_L2 / V_SUP = 1.000` exactly. Off `k = d/2` the ratio is
`2.14` to `4.62` at `d = 100` and `2.17` to `4.82` at `d = 140`.

**This is the mechanical reason four batches of `V`- and `D`-based measurement
could not separate the mechanisms, and it is not a defect of those batches.**

## A.3 What the canonical q-ary form FORCES — declared before the run

The basis form is `B = [[I_k, A],[0, q I_{d-k}]]` with `A` uniform mod `q`
**[quoted: `red_team_report.md` §3.1]**. The measurement **must verify this
convention empirically on the generated `B` before scoring anything** and report
a mismatch as an instrument fault, because I have not verified fpylll's row
convention myself and am relying on a quoted description.

Let `U = rowspan([I_k | A])`, dimension `k`. Then, **[derived here]**:

* **(D1, rigorous.)** `U^perp = { (-Az, z) : z in R^{d-k} }`, dimension `d-k`,
  since `(x, xA).(y,z) = x.(y + Az)`.
* **(D2, rigorous given D1.)** `b*_1..b*_k` span `U` and `b*_{k+1}..b*_d` are an
  orthogonal basis of `U^perp`. Hence for `beta <= d-k` the tail-`beta` GSO frame
  is a subspace of `U^perp`, and for `beta > d-k` it is `W' (+) U^perp` with
  `W' subset U` of dimension `beta - (d-k)`.
* **(D3, rigorous modulo genericity, and it applies only when `k >= d-k`.)** If
  `A` has full column rank, `||Az|| >> ||z||` for every nonzero `z`, so every unit
  vector of `U^perp` carries trailing-block energy of order `1/(k q^2)` — order
  `1e-8` at these parameters. **Therefore, for `k >= d/2` and `beta <= d-k`,
  `m_lead = beta` up to `O(beta / (k q^2))` is FORCED BY THE ECHELON FORM.**
* **(D4.)** A generic vector of `U` is `(x, xA)` with `||xA|| >> ||x||`, so `U`
  sits almost entirely in the **trailing** block. With (D2) this gives, for
  `k >= d/2`, `m_lead = min(beta, d-k)` up to `O(q^-2)`.
* **(D5.)** For `k < d/2`, `ker A` has dimension `d-2k` and contributes vectors
  `(0,z)` lying entirely in the trailing block, so no forcing argument of the
  (D3) kind holds. The block split is **not determined** by (D1)–(D2) and is
  measured.

Three consequences, all declared now:

1. **The unreduced arm at `k >= d/2` is FORCED and carries no mechanism
   information.** Any agreement between the measured `m_lead` there and any
   mechanism is scored as **FORCED — NO INFORMATION**, never as support. This is
   the direct application of the lesson in `DEC-20260806-14ac13` that a check must
   not be scored where its own defect is invisible.
2. (D4) predicts saturation at `d-k`, which agrees with **both** mechanisms at
   `k = d/2` and with **neither** off it. **(D4) is NOT entered as a third
   competing mechanism and must not be scored as one.** Freezing a model derived
   by the producer as a candidate winner is exactly the error
   `DEC-20260806-14ac13` records against the geometry model. Its only role is the
   FORCED declaration in (1). If the measurement disagrees with (D4) where (D4)
   is rigorous, that is a derivation fault or an instrument fault, reported as
   such, and it is evidence for neither mechanism.
3. **The informative arm is therefore `lll_only`,** where the basis is no longer
   in echelon form and no forcing argument above applies. Section A's primary
   scoring is on `lll_only`; `unreduced` is secondary and is scored as a check on
   (D3)/(D4).

## A.4 The frozen grid

**Dimensions and `k` values [set here]:**

| `d` | `k` values | `d-k` | role |
|---|---|---|---|
| 100 | **30** | 70 | `k < d/2`; turning points 30 vs 70 |
| 100 | *50* | 50 | **`k = d/2` NEGATIVE CONTROL** |
| 100 | **70** | 30 | `k > d/2`; turning points 70 vs 30 |
| 140 | **42** | 98 | `k < d/2`; turning points 42 vs 98 |
| 140 | *70* | 70 | **`k = d/2` NEGATIVE CONTROL** |
| 140 | **98** | 42 | `k > d/2`; turning points 98 vs 42 |

**`beta` grids [set here]:** `d = 100`: `beta in {20,30,40,50,60,70,80}`;
`d = 140`: `beta in {28,42,56,70,84,98,112}`. Both grids contain their `d`'s three
`k` values exactly and bracket them on both sides.

**Why each `k` is not degenerate**, stated per value:

* `k = 30` at `d = 100`: `k != d/2` (30 vs 50), so `k != d-k` (30 vs 70). The two
  turning points sit `|2k - d| = 40` apart, four grid spacings. L2 predicts
  saturation at `beta = 30` and SUP at `beta = 70`; the mechanisms' `V`
  predictions differ by a factor `2.14`–`4.62` across the grid.
* `k = 70` at `d = 100`: the exact mirror of `k = 30` (`k <-> d-k`). Same
  separation, opposite assignment: L2 now predicts the *later* turning point.
  **The pair `{30, 70}` is what makes the design symmetric under exchanging the
  two mechanisms**, which is the answer to §A.9's first failure mode.
* `k = 42` and `k = 98` at `d = 140`: the same mirror pair, `|2k - d| = 56`, four
  grid spacings of 14. They test that any `d = 100` result is not a `d = 100`
  accident.
* `k = 50` at `d = 100` and `k = 70` at `d = 140`: **degenerate by construction and
  included on purpose as the negative control.** Here the two mechanisms' `V`
  predictions are identical at every `beta` and their turning points coincide, so
  the `V`-based and turning-point tests **must return NOT SEPARATED**. A `V`-based
  separation at these cells is an implementation fault and is reported as one.

**`beta` values excluded as degenerate:** `beta = 0` and `beta = d`, where
`W_L2 = W_SUP` identically. `W_L2(beta) = W_SUP(beta)` requires
`beta (d-k)/d = -beta k/d` (i.e. `beta = 0`) in the doubly-confined regime and
`(d-beta)(k + (d-k)) = 0` (i.e. `beta = d`) in the doubly-saturated regime, and
has no solution in between. **[derived here]** No `beta` on either grid is
excluded by this; both extremes are outside the grids.

**Arms [set here]:** `unreduced` and `lll_only`, `n = 8` bases per `(d,k)`, plus a
`haar_null` arm of `n = 8` Haar frames per `(d,k,beta)`.

**BKZ is OUT OF SCOPE for Section A**, on the batch-level "NO NEW BKZ" constraint
in the dispatch queue's `batch_thesis`. The cost of that exclusion is stated
plainly: the arm on which the departure is smallest and most interesting is not
tested, and Section A's result does not transport to it. The named successor is a
BKZ arm at `beta <= 40` at `d = 100` only, at the committed 46.6 s per basis
**[quoted: `report.md` §11]**.

**Cost note.** The tail-`beta` frame for every `beta` on the grid comes from a
single `QR(B^T)` per basis, so one QR per basis serves all seven `beta`. The whole
Section A grid is 48 bases, 48 LLL reductions, 96 QR decompositions of size
`<= 140`, and no error draws at all.

## A.5 The observables and their nulls

Per `(d, k, beta, arm)`, over `n = 8` frames: `Wbar`, `s_W` (ddof=1),
`SE_W = s_W/sqrt(8)`; and `Vbar`, `s_V`, `SE_V`.

**Exact Haar null for `W`, [derived here]:**

```
E_haar[W]   = 0                                            (exact)
Var_haar[W] = 2 beta k (d-beta) (d-k) / ( d^2 (d-1) (d+2) ) (claimed exact)
```

The mean follows from `E[P] = (beta/d) I`. The variance is a closed form I derived
here; it passes four independent consistency checks: it reduces to
`Var(P_aa) = 2 beta (d-beta)/(d^2 (d+2))` at `k = 1`, it vanishes at `k = d` and at
`beta = d`, and it is symmetric under `beta <-> k` as it must be, being the
variance of `tr(P Pi)` for two projectors of ranks `beta` and `k`.

**It is NOT taken from any source and I have not verified it numerically.** The
measurement **MUST verify it by Monte Carlo over Haar frames before using it**,
report the deviation in MC-SE at every `(d,k,beta)` on the grid, and — if the
deviation exceeds `4` MC-SE anywhere — report an **instrument fault**, fall back
to the Monte-Carlo null, and record the discrepancy. A theorem asserted by a
producer and never checked is exactly the thing this program has been burned by;
the validator's re-derivation of `mu_0` is the standard **[quoted:
`validation_report.yaml` item_4]**.

Reference magnitudes from the formula, for the floor discussion in §A.7:
`sd_haar(W) = 0.31595` at `(100,30,40)` and `(100,70,40)`, `0.31638` at
`(140,42,56)` and `(140,98,56)`, `0.32246` at `(100,50,30)`.

## A.6 The falsifiers — what falsifies EACH mechanism, separately

Two tests, both frozen here. Thresholds are stated as a **maximum of an absolute
floor and a noise-scaled term**, so that neither can collapse when the other does.
That construction is the direct transfer of AM-3's lesson to Section A.

**A-P — the sign-and-turning-point test. PRIMARY. Applies to every arm.**

Declare `beta` **resolved** at `(d,k,beta,arm)` iff

```
|Wbar| > FLOOR_W(d,k,beta,arm) := max( 4 * s_W/sqrt(8) ,  4 * sd_haar(W)/sqrt(8) )
```

Then, per `(d, k, arm)`:

* **L2 is FALSIFIED** iff some resolved `beta` has `Wbar < 0`. (L2 puts the excess
  mass in the leading block, so `W > 0` at every `beta`.)
* **SUP is FALSIFIED** iff some resolved `beta` has `Wbar > 0`.
* **Turning-point clause**, evaluated only when at least three `beta` resolve:
  report `beta_hat = argmax_beta |Wbar(beta)|`. **L2 is additionally FALSIFIED**
  if `|beta_hat - k| > 1` grid spacing while `|beta_hat - (d-k)| <= 1` grid
  spacing; **SUP is additionally FALSIFIED** in the mirror case. If fewer than
  three `beta` resolve, the clause is **NOT EVALUABLE** and is reported as such,
  never as agreement.

**A-S — the full-shape test. SECONDARY. `unreduced` arm only.**

```
E_X = max_beta | Wbar(beta) - W_X(beta) |,   X in {L2, SUP}
X is FALSIFIED iff  E_X > max( 0.05 * beta_max ,  4 * max_beta SE_W(beta) )
```

`beta_max` is the largest `beta` on that `d`'s grid (80 or 112), so the absolute
tolerance is `4.0` and `5.6` block-mass units respectively **[set here]**: five
percent of the largest frame mass being scored. A-S is reported for the
`lll_only` arm too, as a diagnostic with **no verdict attached**, because the
shapes describe complete confinement and a partially-confined reduced arm can
fail both without either mechanism being wrong about direction.

**Outcome mapping, frozen:**

| A-P result | recorded outcome |
|---|---|
| exactly one of L2/SUP falsified | the other is **NOT FALSIFIED at the stated floor** — never "confirmed", never "supported" |
| both falsified | **NEITHER** — report the measured `W` profile and both deviations; propose no replacement mechanism |
| neither falsified, some `beta` resolved | **NOT SEPARATED** — report the largest `abs(W_L2 - W_SUP)` over the grid against the floor |
| no `beta` resolved | **NOT SEPARATED, BELOW FLOOR** — report the floor as an upper bound at every `beta` |

The **NEITHER** branch deserves its own sentence, because it is a live outcome and
the temptation it creates is the one this program keeps losing to: if both
mechanisms are falsified, the run reports the measured profile and **does not
fit, name, or freeze a replacement mechanism**. A model formulated after seeing
the profile it explains is not a prediction.

## A.7 Detection floor, in the statistic's own units

`FLOOR_W` above is in **block-mass units** — the same units as `W` itself,
dimensionless, on a scale where the total frame mass is `beta`. It has two parts
and takes the larger:

* `4 * s_W/sqrt(8)`, the realized floor, measured per arm per cell;
* `4 * sd_haar(W)/sqrt(8)`, an a-priori floor from the closed form of §A.5, which
  **cannot collapse** because `sd_haar(W)` is a positive closed form of
  `(d,k,beta)` alone. At the grid's centre this is `4 * 0.316 / 2.828 = 0.447`
  block-mass units **[derived here]**.

**Frozen wording requirement.** Every negative verdict is reported as

> `|W| < FLOOR_W = <number>` block-mass units (upper bound at `n = 8` frames)

and **never** as "absent", "no departure", "the mechanism is confirmed",
"consistent with zero" or any synonym. The measurement must contain no code path
able to emit "absent" about a Section A arm. This is a completion-gate item.

**Power, stated in advance and honestly.** Against the a-priori floor of `0.447`,
the mechanisms' separation `|W_L2 - W_SUP|` runs from `10` to `70` block-mass
units across the grid — a margin of `22x` to `157x`. **On the `unreduced` arm the
test is therefore decisive by a wide margin, and on the `unreduced` arm it is
also largely FORCED (§A.3).** On the `lll_only` arm the realized `s_W` is unknown
and the departure is 15–50x smaller than unreduced **[quoted: `report.md` §7]**,
so **it is entirely possible that no `beta` resolves on the informative arm.** I
pre-register that as a likely outcome, not as a failure, and §A.8 says what it
means. Its costed successor is `n`: the floor scales as `1/sqrt(n)` and each
extra frame is one LLL reduction, so quadrupling `n` halves the floor at a cost
the run must report as a concrete number of core-seconds.

## A.8 What I will conclude if the two mechanisms are NOT separated

**A null result here is a real deliverable and is pre-registered as one.**

If Section A returns NOT SEPARATED on the informative arm, the run records
exactly this and nothing more:

> At `(d, k, beta)` on the frozen grid, `n = 8` frames, on the `lll_only` arm of
> q-ary bases at `q = 3329`, the leading-block excess `W` did not resolve above
> `FLOOR_W = <number>` block-mass units at any `beta`. The `beta <= k` and
> `beta <= d-k` spill boundaries are therefore **not separated by this observable
> at this floor**, and the separation the two mechanisms require is `<number>`
> block-mass units, i.e. `<ratio>x` the achieved floor.

That is an answer to the five-record question, in the form of a bound rather than
a verdict, and it is reported as the batch's Section A result. It is **not** a
licence to reach for a different observable mid-run: the frozen specification is
run as written, and a proposed better observable is recorded in the report as
forward guidance for a successor, exactly as BATCH-f19c37's executor did with the
grid it had.

Three further branches, all pre-registered:

* **NOT SEPARATED on `lll_only`, SEPARATED on `unreduced`.** The `unreduced`
  result is reported with the FORCED declaration of §A.3 attached at every use,
  and the run states that the discriminating content rests on an arm whose value
  is (for `k >= d/2`, rigorously) a consequence of the basis's echelon form.
* **NEITHER mechanism survives.** Reported as in §A.6, with no replacement.
* **The `k = d/2` control separates.** Implementation fault. The run reports it as
  such, and the entire Section A result is marked `invalid_measurement`.

## A.9 The arrangement in which Section A's check could not fail

Named before the run, with the demonstration that it is not the arrangement being
run.

1. **Testing only `k > d/2`.** The q-ary construction is built around the leading
   identity block, so a design that only ever asks "is the mass in the leading
   block?" in the regime where L2 says yes cannot falsify L2. **Not in it:** the
   design runs the mirror pair `{k, d-k}` at each `d` (`{30,70}` and `{42,98}`).
   Relabelling which mechanism is called L2 maps the `k = 30` cells onto the
   `k = 70` cells exactly. The design is invariant under exchanging the two
   mechanisms, so neither can win by the arrangement.
2. **Scoring only `V`, which is blind to the distinction at `k = d/2`.** This is
   the actual historical failure — four batches of `V`- and `D`-based measurement
   on `k = d/2` cells. **Not in it:** the primary statistic is `W`, which is
   first-order and signed; `V` is secondary; and the `k = d/2` control is included
   precisely to *exhibit* `V`'s blindness rather than to be caught by it.
3. **Measuring on the arm where the echelon form forces the answer.** This is the
   sharpest one and the design is **partly in it**, which is why §A.3 exists: the
   `unreduced` arm at `k >= d/2` is FORCED for `beta <= d-k`, declared forced
   before the run, and scored as carrying no mechanism information. The
   informative arm is `lll_only`. Being partly in this arrangement and saying so
   is the honest position; claiming the `unreduced` separation as mechanism
   support would be the sixth instance of this program's characteristic error.
4. **A threshold denominated in a noise scale that collapses where the effect
   vanishes** — the G3 defect. **Not in it:** `FLOOR_W` takes the maximum of the
   realized SE and an a-priori closed-form floor that is a positive function of
   `(d,k,beta)` alone and cannot collapse.
5. **Reading the turning point off the measured curve and then declaring which
   mechanism predicted it.** **Not in it:** `W_L2` and `W_SUP` are closed forms of
   `(d,k,beta)` with no free parameter, written above, notarized before the data
   exists, and the turning-point clause names `k` and `d-k` in advance.
6. **The producer's own derivation (D4) quietly becoming the winner.** **Not in
   it:** (D4) is barred from scoring by §A.3(2), and a disagreement with it is
   declared in advance to be a fault report, not evidence for either mechanism.

## A.10 Seeds introduced by Section A

New families are required because `k != d/2` cannot reuse committed bases. All
are `< 2^31` so no 32-bit seed API can silently truncate, and all are disjoint
from every committed family (which all lie below `2.1e7`) and from each other.

```
seed_basis_k(d,k,i)      = 1000000000 + d*10^6 + k*10^4 + i        [i in 0..7]
seed_haar_k(d,k,beta,j)  = 1200000000 + d*10^6 + k*10^4 + beta*10 + j   [j in 0..7]
seed_mcnull_k(d,k,beta)  = 1400000000 + d*10^6 + k*10^4 + beta*10
```

Validity conditions, which the measurement **must assert at startup**: `d < 1000`,
`k < 100`, `beta < 1000`, `i < 10^4`, `j < 10`. Ranges: bases `[1.100e9, 1.141e9]`,
Haar `[1.300e9, 1.341e9]`, Monte-Carlo null `[1.500e9, 1.541e9]`. `k = 98` is the
largest `k` used and satisfies `k < 100`; a successor extending to `k >= 100` must
mint a new scheme rather than overflow this one.

Basis generation is `IntegerMatrix.random(d, "qary", k=k, q=3329)` with
`FPLLL.set_random_seed(seed_basis_k(d,k,i))` — the committed call with `k` now a
free parameter rather than `d//2`. The Haar arm draws from
`numpy.random.default_rng(seed_haar_k(...))` by QR of a `d x beta` standard normal.
`lll_only` is `LLL.reduction` at the committed default parameters.

---

# SECTION B — AM-3, the G3 replacement

## B.0 The declaration that has to come first: this is not blind

**The AM-3 re-run's data already exists and is committed.** TASK-20260806-e17677
re-runs the AM-1 graded family on the same 13-point grid, the same
`seed_graded`/`seed_error`/`seed_haar` families, with no new BKZ. BATCH-f19c37
established that this pipeline is bit-reproducible: 24 of 24 shared grid points
were **bitwise identical** across batches, difference `0.0` exactly **[quoted:
`report.md` §10.1]**. It follows that every `Delta_i` and every `SE_step(i)` the
AM-3 gate will be applied to is already recorded in
`BATCH-f19c37/.../results.json`, and I have read the report that tabulates them.

**Therefore Section B pre-registers a RULE, not an outcome.** What is genuinely
frozen in advance is the gate, its false-failure rate on a flawless instrument,
and its multiplicity policy — all three of which are properties of the rule and
are computable without the data. What is **not** blind is the verdict. No record
arising from Section B may describe the AM-3 verdict as an out-of-sample test, and
the run report must carry this paragraph's substance verbatim.

**The validator's item-3 counterfactual.** I have read it. It is **POST-HOC** — it
was computed after seeing which steps violated, which is the move BATCH-f19c37's
§7.5 forbids and which that batch's executor correctly declined to make. I use it
for its **forward content only**: it establishes that *the choice of denominator,
not the data, decides this verdict*, which is why AM-3 exists. I do **not** cite
it as a result, I do **not** cite its "PARTIAL in all four cells" as a verdict,
and I do **not** offer "it would have given PARTIAL" as an argument that the
repair below is the right one. `DEC-20260806-14ac13` AM-3 `prohibition` binds and
is honoured. Three concrete steps I took so that this is checkable rather than
asserted, in §B.2: I chose the **stricter** of the two margins the counterfactual
priced, I added a multiplicity correction the counterfactual did not have, and the
rule's rate is derived from a distributional theorem rather than fitted to any
step.

## B.1 What is withdrawn and is not available

`DEC-20260806-14ac13` `amendment_disposition.AM-1.G3`: the tie-tolerant form
denominated in `SE_step_paired` is **WITHDRAWN AS FROZEN** and may not be re-used;
its "record the more severe of the two readings" clause is additionally a
one-sided safeguard, since `SE_paired < SE_unpaired` in 47 of 48 steps. Neither is
used below. Setting the margin of §B.2 to zero and the quantile to `1.0` would
recover the withdrawn rule; **neither substitution is permitted**, and the
measurement must not compute or report the withdrawn rule's verdict at all.

Reference figures on the withdrawn rule, both **[quoted]** and neither
recomputed as a verdict: the validator counted the 24 of 48 steps with neither
endpoint clearing the gate and obtained `P(at least one FAIL) = 0.9902`, noting
that most of it is multiplicity; the red team counted the 3 plateau steps the grid
guarantees per cell and obtained `P(4-cell FAIL) = 0.9014` against
`P(PASS) = 0.00025`.

## B.2 The chosen repair, and the frozen rule

**Repair chosen: (c), the equivalence/non-inferiority form, with its margin
denominated in repair (a)'s units.**

For each of the 12 consecutive pairs `(t_i, t_{i+1})` of the retained 13-point
grid, in each of the 4 cells:

```
Delta_i          = m(t_{i+1}) - m(t_i)                                  [as before]
SE_step_paired(i)= sd_j( r_j(t_{i+1}) - r_j(t_i) ) / sqrt(8)   [ddof=1]  [as before]
delta_i          = K_delta * SE_diff(t_i),      K_delta = 1.0            [set here]

  STEP i IS A VIOLATION   iff   Delta_i  -  t*_7 * SE_step_paired(i)  >  delta_i
```

`SE_diff(t_i)` is the gate's own two-arm standard error at the step's **lower
endpoint** — the same quantity the design already uses to decide whether an arm
carries any signal. `t*_7` is the `1 - alpha` quantile of Student-`t` on 7 degrees
of freedom with `alpha = 0.05/48` (§B.3, §B.4).

**In words:** a step is a violation only when the one-sided lower confidence bound
on the true step, at the multiplicity-corrected level, exceeds a
practically-negligible increase. It is an equivalence-test framing: the design
must *establish* an increase, not merely fail to rule one out.

**Why `K_delta = 1.0`.** The design declares a difference detectable at
`4 * SE_diff`; `1.0 * SE_diff` is one quarter of the design's own resolution, so a
step below it is practically negligible **by the frozen design's own standard**,
not by a standard invented here. The validator priced two readings, `1 x SE_diff`
and the full gate width `4 x SE_diff`; **I take the stricter one.** Committed gate
widths `4 * SE_diff` run `0.0032`–`0.0069` in `r` units across the four cells
**[quoted: `report.md` §4]**, so `delta_i` will be of order `0.0008`–`0.0017`.

**The paired/unpaired ambiguity is resolved in advance, not by severity.** The
AM-3 verdict is computed with `SE_step_paired` only, because the paired form is
the correct SE for this design — `(S_j, G_j)` is shared across `t` within a draw
**[quoted: BATCH-f19c37 prereg §1.1]**. The unpaired reading is reported per step
as a diagnostic and **is not an alternative verdict**. Selecting the correct SE in
advance replaces "record the more severe of the two", which the reviews showed
reduces to "always paired" in 47 of 48 steps and is therefore a one-sided
safeguard wearing a two-sided label.

**Note that `SE_step_paired` appears here as the standard error inside a
confidence bound, never as the tolerance.** The withdrawn rule's threshold was
`1.0 * SE_step_paired`, which tends to `0` as the noise collapses. This rule's
threshold is `delta_i + t*_7 * SE_step_paired(i)`, which tends to
`delta_i = 1.0 * SE_diff(t_i) > 0`. **The threshold cannot collapse where the
effect vanishes**, which is the exact defect AM-3 was written to remove, and the
proof of that is one line of algebra a reviewer can check without any data.

## B.3 The false-failure rate on a flawless instrument — derived and printed

**Definition of a flawless instrument**, as both reviews used it: the true mean
curve `m(t)` is non-increasing, so the true step `Delta_i^0 <= 0` at every step.

**Derivation.** For a step whose 8 paired differences are i.i.d. Gaussian with
true mean `Delta^0`, `(Delta_hat - Delta^0)/SE_step_paired ~ t_7` exactly. The
validator states this is the exact reference distribution for this statistic, with
no approximation involved **[quoted: `validation_report.yaml` item_3
`false_flag_arithmetic.model`]**. Then, for any `Delta^0 <= 0` and any
`delta_i >= 0`:

```
P(violation) = P( Delta_hat - t*_7 * SE  >  delta_i )
             <= P( Delta_hat - t*_7 * SE  >  0 )                [since delta_i >= 0]
             =  P( (Delta_hat - Delta^0)/SE  >  t*_7 - Delta^0/SE )
             <= P( t_7 > t*_7 )                                 [since Delta^0 <= 0]
             =  alpha
```

Three properties of this bound, each of which the withdrawn rule lacked:

* **No nuisance parameter.** It holds for every unknown noise scale `sigma`,
  because the pivot is a `t` statistic. The withdrawn rule's rate also had this
  property; what it lacked is that its rate was `P(t_7 > 1) = 0.175308` per step.
* **No dependence assumption is needed for the family-wise bound** (§B.4), because
  the union bound is used.
* **The random margin does not weaken it.** `delta_i` is a positive multiple of a
  standard error, hence `>= 0` almost surely, so the violation event with a random
  `delta_i` is a subset of the event with `delta_i = 0`.

**THE PRINTED RATE.** With `alpha = 0.05/48` and `M = 48` comparisons:

```
multiplicity            M       = 48        (12 steps x 4 cells)
per-comparison level    alpha   = 0.05/48   = 0.0010416667
critical value          t*_7                = 4.750074
DECLARED FALSE-FAILURE RATE ON A FLAWLESS INSTRUMENT
   P(overall INVALID)  <=  M * alpha        =  0.050000
   (exact value if the 48 comparisons were independent: 0.048795)
```

**0.050000 <= 0.10. The AM-3 requirement is met.**

`t*_7 = 4.750074` was computed two independent ways and agrees to 10 decimal
places: the elementary odd-`nu` closed form
`P(|T|<=t) = (2/pi)[theta + sin(theta)(cos + (2/3)cos^3 + (8/15)cos^5)]` with
`theta = arctan(t/sqrt(7))`, and direct Simpson quadrature of the `t_7` density
`f(t) = 48/(15 pi sqrt(7)) (1 + t^2/7)^{-4}`. Both give
`P(T > 4.750074) = 0.0010416671`. The same closed form reproduces the published
`t_7` one-sided quantiles `1.894579` at `0.05`, `2.364624` at `0.025`,
`2.997952` at `0.01` and `3.499483` at `0.005` to six decimals, and reproduces the
reviews' `P(t_7 > 1) = 0.175308` **[quoted]**. Anyone can recheck all of it in ten
lines of Python with no lattice and no data.

**The Gaussian assumption is declared, not hidden.** The bound rests on the 8
paired differences being i.i.d. Gaussian. They are means over `2^20` draws across
8 independent frames, so this is a CLT-across-frames assumption, not a theorem.
The measurement **must report the 8 per-frame paired differences for every step**
so a reviewer can inspect it, and **must not rescore** if they look non-Gaussian:
a departure is recorded as a qualification on the declared rate, and the frozen
verdict stands.

## B.4 Multiplicity policy

**`M = 48` comparisons: 12 steps x 4 cells.** Declared unconditionally, before any
data, and fixed regardless of how many steps turn out to be informative.
Correction: **Bonferroni**, `alpha = 0.05/M`, giving a family-wise false-failure
rate `<= 0.05` **under arbitrary dependence** among the 48 comparisons. Šidák
(`alpha = 0.00106804`, `t* = 4.744`) would be very slightly sharper but assumes
independence, which adjacent steps sharing an endpoint and cells sharing a Haar
arm do not have; the difference is immaterial and the assumption-free bound is
taken.

**Why the multiplicity count is not made data-dependent.** Repair (b) — restrict
G3 to steps with at least one endpoint clearing the gate — would cut `M` from 48
to about 24 **[quoted: `validation_report.yaml`, 24 of 48 saturated]** and halve
the bound. It is deliberately **not** used, because which steps clear is decided by
the data, so `M` would be a random variable and the declared rate would no longer
be computable before the run. Declaring `M = 48` is conservative in the correct
direction: any restriction can only lower the realized family-wise rate below the
declared bound.

Sensitivity of the declared bound to a mis-stated count, so the claim is auditable:
`M = 12 -> 0.0125`; `M = 24 -> 0.0250`; `M = 48 -> 0.0500`; `M = 96 -> 0.1000`.
**The declared rate stays at or under 0.10 even if the true comparison count were
double what I declared**, which is the margin I want against my own bookkeeping.

## B.5 Power, and the gate's own detection floor — the cost, stated

A rule that cannot fail is as defective as one that cannot pass, and this rule is
much less sensitive than the one it replaces. Stating the cost:

The rule fires when `Delta_i > delta_i + t*_7 * SE_step_paired(i)`. Using the
validator's measured ratio `SE_step_paired / SE_diff = 0.36`–`0.42` at the two
failing steps **[quoted: `validation_report.yaml` item_3]**, the threshold is
approximately

```
1.0 * SE_diff  +  4.750 * (0.36..0.42) * SE_diff   ~=   2.7 .. 3.0 * SE_diff
```

so the AM-3 gate flags a true step of roughly **3 `SE_diff`**, against the
withdrawn rule's `0.36`–`0.42 SE_diff` — about **7x less sensitive**. That figure
is an **estimate contingent on a quoted ratio measured on two steps**, not a
measurement, and it is labelled as such. Two things follow, both declared now:

* **It is coherent with the design.** The design calls a difference detectable at
  `4 * SE_diff`. A gate that fires at `~3 * SE_diff` is *more* sensitive than the
  design's own detectability standard, so any step the design would itself call
  real is flaggable. The rule is not so permissive that it cannot fire.
* **G3's detection floor, in `r` units:** the smallest true step the gate can flag
  is `delta_i + t*_7 * SE_step_paired(i)`, computed and **reported per step** in
  the run's own units. Every non-violating step is reported as
  `true step < <number>` (upper bound at 8 draws), never as "the family is
  monotone at that step".

## B.6 Retained verbatim, and not re-litigated

* **The AM-1 13-point `t` grid**, exactly: `[0, 0.0025, 0.005, 0.0075, 0.01,
  0.015, 0.02, 0.03, 0.05, 0.1, 0.25, 0.5, 1.0]`. No point added, removed,
  reordered or re-spaced. `DEC-20260806-14ac13` retains it and records that no
  successor re-litigates it.
* **G1** (`gate(t=0)` clears in all four cells) and **G2** (`gate(t=1)` does not
  clear in any cell), unchanged. G1, G2 and the AM-3 gate are reported
  **separately, per cell**.
* **The verdict table**, unchanged in shape: G1 fails or G2 fires -> INVALID;
  otherwise no violation and no positive step -> **VALID**; no violation but some
  positive step -> **PARTIAL**; some violation -> **INVALID**. Overall verdict is
  the most severe cell verdict. Retaining PARTIAL for the no-violation-but-some-
  increase case is the **conservative** retention: an equivalence framing could
  argue for promoting it to VALID, and this document deliberately does not, so
  that no one can say the repair was chosen to manufacture a better headline. A
  successor may argue for the promotion; it is not argued here.
* **Seeds: unchanged, and I confirm I did not change them.** Section B uses
  `seed_graded(d,beta,j) = 500000 + d*1000 + beta*10 + j` for the graded family,
  `seed_haar(d,beta,j) = 900000 + d*1000 + beta*10 + j` for the Haar null arm,
  `seed_error(d) = 20260805 + d` for the CBD draws, and
  `seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i` for the committed bases —
  the cache verified at 32/32, max deviation `0.0` **[quoted: `report.md` §3]**.
  Section B introduces **no new seed** except the null-object simulation of §B.7.
  The measurement re-verifies the 32/32 reproduction and reports its max deviation
  before scoring anything.
* **`(S_j, G_j)` is drawn from `seed_graded` before and independently of the `t`
  list**, in the committed draw order, so the paths are unperturbed. Retained.

**If the frozen gate returns INVALID again, it is reported as frozen.** No
rescoring, no reaching for the withdrawn tolerance, no post-hoc alternative
computed and placed beside the verdict.

## B.7 A null-object simulation of my own gate — required, not optional

`docs/inventor-protocol.md` §3 requires the identical measurement against a null
object of the same shape before a signal is believed. The signal here is the
gate's declared rate, so the null object is a flawless instrument. **Frozen
requirement:** the measurement simulates the AM-3 rule on synthetic flawless data
— true steps set to zero, Gaussian paired differences at the realized per-step
`SE_step_paired`, `10^5` synthetic 4-cell experiments, seeded from
`seed_g3null = 1450000000` **[set here]** — and reports:

1. the **empirical family-wise false-failure rate** against the declared `0.05`;
2. the **empirical power** at true steps of `1`, `2`, `3` and `4 * SE_diff`, so
   the §B.5 power estimate is replaced by a measured curve;
3. the same two quantities for `M` counted as 24 rather than 48, as a robustness
   check on §B.4.

This is pure numpy on synthetic Gaussians, seconds of compute, and it touches no
lattice. **If the simulated family-wise rate materially exceeds `0.05`, that is a
fault in MY GATE**, reported as an instrument fault against this pre-registration,
and the AM-3 verdict is reported alongside it as provisional. It is not a finding
about the graded family in either direction.

## B.8 The arrangement in which Section B's check could not fail

1. **A threshold denominated in a noise scale that collapses where the effect
   vanishes.** The historical defect. **Not in it**, and provably so: as
   `SE_step_paired -> 0` the threshold tends to `delta_i = 1.0 * SE_diff(t_i) > 0`,
   not to `0`. One line of algebra, no data needed.
2. **A gate so permissive it cannot fire — the mirror defect, and exactly the one
   a repair chosen to avoid a second INVALID would have.** **Not in it**, and
   §B.5 quantifies it: the gate fires at about `3 * SE_diff`, below the design's
   own `4 * SE_diff` detectability standard, and §B.7 requires the power curve to
   be measured rather than argued.
3. **Declaring a rate that is a property of an assumption rather than of the
   rule.** **Not in it:** the declared `0.05` is a union bound, valid under
   arbitrary dependence and uniform over the unknown noise scale. The
   independence figure `0.048795` is a footnote, not the claim. The one genuine
   assumption — Gaussian paired differences — is named in §B.3 and its diagnostic
   is a required artifact.
4. **Non-blindness.** **The design IS in this one and §B.0 leads with it.** The
   AM-3 data is bitwise determined by committed seeds and I have read the report
   that tabulates it. What I did about it is checkable rather than asserted: the
   stricter of the two priced margins, an added multiplicity correction the
   counterfactual did not have, a rate derived from a distributional theorem
   rather than fitted, and a rule whose critical value `4.750074` was fixed by
   `0.05/48` before any step was consulted. What I cannot do is make the outcome
   blind, so no record may claim it is.
5. **Scoring the gate only where it was designed to behave.** **Not in it:** §B.7
   scores the gate on a null object built for the purpose, at `10^5` replicates,
   including the regime — a flat plateau — that destroyed the withdrawn rule.

---

# SECTION C — F-A1's replacement, the matched-`V` cross-family comparison

## C.1 What survives, and what is actually at issue

**L2's second-order derivation is correct and is not under test.** For i.i.d.
mean-zero unit-variance coordinates with fourth moment `mu_4` and symmetric `A`,
`Var(e^T A e) = (mu_4 - 3) sum_a A_aa^2 + 2 tr(A^2)`; with `A = P` a rank-`beta`
projector this is `Var(e^T P e) = 2 beta + (mu_4 - 3)(V + beta^2/d)`, which **is a
function of `V` alone** once `(d, beta, mu_4)` are fixed. The validator confirmed
the identity independently **[quoted: `validation_report.yaml` item_4]**. Nothing
in Section C may be reported as refuting it.

**The open question is narrower:** whether the `2^-10` **tail quantile** the design
measures at inherits that `V`-sufficiency. Its third cumulant involves
`sum_a P_aa^3` independently of `V`, so there is no derivation carrying the
variance result to the tail **[quoted: `DEC-20260806-14ac13` rationale]**. The red
team measured, on its own frames, `D` differing by 7 % and 20 % at exactly equal
`V`, the second at `3.45 SE`, tracking the third diagonal moment
`sum_a (P_aa - beta/d)^3` **[quoted: `red_team_report.md` §4.2]**. That probe was
not pre-registered, used its own seeds and its own error stream, and ran with
`fpylll` unavailable, so its `D` values are not absolutely comparable to the run's.

Section C pre-registers the comparison against the **committed** bases, seeds and
error stream, so the `D` values become absolutely comparable.

## C.2 The frame families

Write `M3(Q) = sum_a (P_aa - beta/d)^3`, the third diagonal moment, exact and free.

* **Family G — the committed graded family.**
  `Q_t = QR( sqrt(1-t) E_S + sqrt(t) G )` from `seed_graded(d,beta,j)`, unchanged,
  at the anchor `t` values of §C.3. Its `D` **must reproduce the committed value
  bitwise**; that reproduction is the comparability certificate and a mismatch is
  an abort.
* **Family P2 — the red team's two-level family, reproduced.** A rank-`beta`
  projector supported on `2 beta` coordinates with `P_aa in {u, 1-u}` and
  `u = (1 + sqrt(2c-1))/2`, `c = (V_target + beta^2/d)/beta`, so `V` matches in
  closed form **[quoted: `l2_vmatch.py`]**. Support chosen by a permutation from
  `seed_pair2`.
* **Family P3L — a three-level family, introduced here.** Columns
  `q_i = sqrt(u) e_{a_i} + sqrt(v) e_{b_i} + sqrt(w) e_{c_i}` on `3 beta` disjoint
  coordinates, `u + v + w = 1`. With `x = u - beta/d` etc., the constraints
  `x + y + z = 1 - 3 beta/d` and `x^2 + y^2 + z^2 = V/beta` describe a circle, and
  `M3 = beta (x^3 + y^3 + z^3)` varies along it. **[derived here]** Parametrized by
  an angle `theta` on that circle, P3L gives **a continuum of `M3` at exactly
  fixed `V`**, subject to `u,v,w in [0,1]`.

**P3L is the reason Section C is stronger than the probe it reproduces.** A single
alternative family gives one difference; a family sweeping `M3` at fixed `V` gives
a **slope**, and a slope can be zero.

## C.3 Admissible anchors, and the family floor that excludes some

P2 exists only when `2c - 1 >= 0`, i.e. `V >= beta/2 - beta^2/d`. **[derived
here]** That floor is:

| cell | `V_min = beta/2 - beta^2/d` |
|---|---|
| `d100_b30` | 6.0000 |
| `d100_b40` | 4.0000 |
| `d140_b30` | 8.5714 |
| `d140_b40` | 8.5714 |

This is exactly why the red team's third row missed its target (`V = 4.4656`
requested, `6.0000` delivered) **[quoted: `l2_vmatch.out`]**, and it is declared
here **before** the run so that a below-floor anchor cannot be quietly dropped
afterwards.

**The admissible anchors, enumerated now from committed `V` values [quoted:
`report.md` §4, §7]:**

| cell | admissible anchors (`t` or arm, with committed `V`) | excluded, below floor |
|---|---|---|
| `d100_b30` | `t=0` (21.0000), `t=0.0025` (12.9512), `t=0.005` (8.4735), `unreduced` (9.3628) | `t=0.0075` (5.8825) and all larger `t` |
| `d100_b40` | `t=0` (24.0000), `t=0.0025` (14.7785), `t=0.005` (9.5532), `t=0.0075` (6.5464), `t=0.01` (4.7448), `unreduced` (16.2446) | `t=0.015` (2.8648) and larger |
| `d140_b30` | `t=0` (23.5714), `t=0.0025` (12.4765) | `t=0.005` (7.5085) and larger; **`unreduced` (6.7504) is BELOW FLOOR and is excluded** |
| `d140_b40` | `t=0` (28.5714), `t=0.0025` (15.2348), `t=0.005` (9.0865), `unreduced` (11.8075) | `t=0.0075` (5.9694) and larger |

**Frozen anchor set:** the three highest-`V` admissible graded anchors per cell
plus the `unreduced` arm where admissible — **13 anchors in total**, listed above.
`t = 0` is retained deliberately: it is the coordinate-aligned extreme where
`V = beta(1-beta/d)` exactly, so the `V`-match is exact by construction and the
comparison is at its cleanest. **`d140_b30 unreduced` is excluded now, before the
run, and a report that quietly includes it is in violation.**

## C.4 The `V`-matching tolerance

P2 and P3L are constructed to match the **arm-mean** `V` of their graded anchor in
closed form. Frozen tolerance:

```
|Vbar_synthetic - Vbar_anchor| / Vbar_anchor  <=  1e-9        [set here]
```

achievable because the match is analytic, not searched. **The achieved tolerance
is REPORTED PER PAIR**, and any pair exceeding it is scored **NOT COMPARABLE** and
excluded with its achieved value printed — never silently re-matched. Per-frame
`V` still varies within the graded arm; the run reports the graded arm's per-frame
`V` spread beside the mean so a reviewer can see how tight the "exactly equal `V`"
claim really is.

## C.5 Estimator, draws, arms

All **[carried]**: `N = 2^20` CBD_{eta=2} draws from `seed_error(d) = 20260805 + d`;
`q_emp(2^-10) = sort(R)[1023]`; `n = 8` frames per arm; the Haar reference arm from
`seed_haar(d,beta,j)`.

```
D_raw(A) = mean_j q_emp,A(j) - mean_j q_emp,haar(j)
D_r(A)   = D_raw(A) / q_Beta(2^-10)          [the committed r-units, reported too]
```

Both are reported, `q_Beta(2^-10)` printed exactly, so the numbers are directly
comparable to the committed tables. **Every arm sees the identical error draws**,
which is the design's own discipline and is what makes the Haar term cancel
exactly in `D_B - D_A`.

**Memory, frozen, because the probe being reproduced allocated an array that does
not fit the budget.** `l2_vmatch.py` allocates `(n_frame_columns, N)` float32 —
`1680 x 2^20 x 4` bytes is about `7.0 GB` against this task's `4 GB`. The
measurement **must** stream the error draws in chunks and hold only per-frame `R`
vectors: `n_frames_total x N x 4` bytes, with **`n_frames_total <= 200` frozen as a
hard cap**, i.e. `<= 0.84 GB`. Exceeding the cap is a specification violation, not
a budget overrun to be worked around.

**Power extension, declared as an extension and not as the verdict.** The
synthetic families cost no reduction, so P2 and P3L are additionally run at
`n = 32` (frames `j = 0..31`), with the graded anchor extended to `j = 0..31` from
the same `seed_graded` family. **The scored verdict is at `n = 8`** (comparability
with the committed run and with the probe being reproduced). The `n = 32` result
is reported separately under its own pre-registered rule (F-C2) and may not be
substituted for F-C1.

## C.6 The falsifier, and the effect size that counts

For a `V`-matched pair `(A, B)` at one anchor,
`SE(Delta_D) = sqrt(s_A^2/8 + s_B^2/8)` — the Haar term cancels exactly, as the
probe's own script notes.

**F-C1 — PRIMARY, at `n = 8`.** "`D` is a function of `V` alone" is **FALSIFIED**
at a cell iff some `V`-matched pair has

```
|D_B - D_A|  >  max( 4 * SE(Delta_D) ,  0.10 * |D_A| )        [set here]
```

Both conditions must be exceeded. `4 * SE` is the design's inherited detectability
gate **[carried: `gate_k = 4.0`]**; `0.10 * |D_A|` is an absolute relative floor so
that a statistically resolved but mechanically trivial difference cannot carry the
verdict.

**I state now what this rule does to the numbers being reproduced, because it is
adverse to a headline and must not surface later as a surprise.** The red team's
two differences were `7 %` at `1.91 SE` and `20 %` at `3.45 SE`. **Neither would
falsify under this rule** — the first fails both conditions, the second passes the
relative floor and fails the `4 SE` gate. So a plausible outcome of Section C is
**NOT FALSIFIED at `n = 8`**, and §C.7 pre-registers what that means. I chose the
program's standing `4.0` gate rather than a weaker one precisely because I already
know the probe's effect size; picking a gate at `3.0` would have been choosing the
verdict.

**F-C2 — the `M3` slope, at `n = 8` and again at `n = 32`.** Across the P3L
`theta` sweep at one anchor, `V` is exactly constant and `M3` varies. Regress
`D` on `M3` (ordinary least squares, `theta` arms as points, weights `1/SE^2`) and
report `slope`, `SE(slope)`, and the `M3` range spanned.

```
"D depends on the frame only through V" is FALSIFIED by F-C2 iff
      |slope| > 4 * SE(slope)   at that anchor
```

**F-C2 is the mechanism-level observable and is the more informative of the two.**
A difference between two families can be blamed on the families; a resolved slope
in `M3` at exactly fixed `V` cannot.

**Multiplicity, declared.** F-C1: 13 anchors x 2 synthetic families = **26
pairwise comparisons**. F-C2: **13 slopes**, one per anchor, at each of the two
`n`. No multiplicity correction is applied to either, and that is declared rather
than assumed: the `4 SE` gate is inherited from a design that explicitly claims no
p-value and no multiple-comparison correction **[quoted: BATCH-f19c37 prereg §3]**,
and changing that here would silently re-litigate an inherited constant. The cost
is stated: with 26 comparisons at a nominal `4 SE`, the family-wise false-positive
rate is **not** the per-comparison one, and any citation of F-C1 must carry the
comparison count.

## C.7 Both outcomes, pre-registered

**If the effect REPRODUCES** (some pair clears F-C1, or some slope clears F-C2),
the run records:

> At `(d, beta)` on q-ary bases from the committed seed family, `n = 8` frames,
> `N = 2^20` draws, the `2^-10` empirical quantile difference `D` differed between
> two frame families **matched in `V` to `<tolerance>`**, by `<x> SE` and `<y> %`,
> with the sign tracking `M3`. **`D` is not a function of `V` alone at these
> parameters.**

and simultaneously records, in the same paragraph, that this **does not** refute
L2's variance-level identity, which is a theorem and remains one; the observation
is that the `2^-10` tail quantile does not inherit the `V`-sufficiency of the
variance. No hypothesis status moves and none is proposed.

**If the effect does NOT reproduce**, the run records:

> `|D_B - D_A| < max(4 SE, 0.10|D_A|) = <number>` in `D` units (upper bound at
> `n = 8`, `N = 2^20`), and `|slope| < 4 SE(slope) = <number>` per unit `M3`, at
> every admissible anchor.

and **never** as "`D` is a function of `V` alone", and **never** as a refutation of
the red team's probe. A non-reproduction is not a contradiction of that probe: it
ran on different frames, a different error stream and a different Haar reference,
and at an effect size this rule was deliberately set not to detect. It is a scope
statement about the committed bases at the declared floor. Both outcomes leave the
probe standing as a probe.

**A third branch:** F-C1 not falsified at `n = 8` while F-C2's slope resolves at
`n = 32`. Reported as exactly that — an effect below the `n = 8` floor and above
the `n = 32` floor — with both floors printed, and the `n = 8` verdict recorded
unchanged as the scored one.

## C.8 The null object, BUILT and not proposed — CTRL-C-PERM

**Frozen requirement.** At every anchor, P3L is instantiated at the same `theta`
with **two different coordinate-support permutations** (`rep = 0, 1` in the seed
scheme). These two arms have **identical `V`, identical `M3`, identical diagonal
profile as a multiset**, and differ only in which coordinates carry it. If `D`
depends on the frame through `(V, M3)` and the error law is coordinate-exchangeable
— CBD is i.i.d. across coordinates — they must agree.

```
CTRL-C-PERM PASSES  iff  |D_{rep=0} - D_{rep=1}| <= max(4 * SE, 0.10 * |D|)
                          at every anchor  (the same threshold as F-C1)
```

**A CTRL-C-PERM failure is an INSTRUMENT FAULT** — it means the apparatus resolves
differences between frames that the mechanism cannot distinguish — and in that
case **F-C1 and F-C2 are reported as NOT INTERPRETABLE at that anchor**, not as
findings. This is the control whose absence the red team exploited to kill P3, and
it is the cheapest possible one: it is two extra numpy arms per anchor and it uses
the error draws already in memory.

This control is also Section C's partial answer to AM-4: it is invariance under
**coordinate permutation** of the statistic's own input, checked empirically rather
than asserted. It is **not** a full AM-4 demonstration — ambient isometry and
unimodular change of basis are not tested — and Section C therefore claims no
AM-4 admissibility for anything.

## C.9 The arrangement in which Section C's check could not fail

1. **Scoring on a single monotone family, so co-monotonicity is forced.** The
   exact defect that killed the frozen F-A1: the NOVEL subset was graded-path
   points only, where `V(t)` and `D(t)` are both monotone in `t`, so "zero
   violating pairs" was forced by the construction **[quoted:
   `red_team_report.md` §4.1]**. **Not in it:** every scored comparison holds `V`
   exactly fixed and varies the family or `M3`. Co-monotonicity in a shared
   parameter is impossible when the parameter is held constant.
2. **Building the alternative family so its `M3` differs in one fixed direction,
   guaranteeing a signed difference.** The probe being reproduced is in this
   arrangement: P2's `M3` is below G's at all three of its anchors (`0.9801` vs
   `2.2066`; `-0.5684` vs `1.2859`; `-0.6000` vs `0.8049`) **[quoted:
   `l2_vmatch.out`]**, so it can only ever produce a one-signed difference.
   **Not in it:** P3L's `theta` sweep is required to **bracket** the graded
   anchor's `M3` — at least one arm above and one below — and the run must
   **report whether bracketing was achieved at each anchor**. Where feasibility
   (`u,v,w in [0,1]`) forbids bracketing, that anchor is scored **one-sided** and
   labelled so.
3. **No null object, so any difference looks like a finding.** **Not in it:**
   CTRL-C-PERM (§C.8) is built, required, and uses the same threshold as the
   falsifier, so it cannot be passed by being weaker.
4. **Choosing anchors the families cannot match, then reporting non-reproduction.**
   **Not in it:** the `V_min` floor is derived in §C.3 and every admissible anchor
   is enumerated by name before the run, including the one exclusion
   (`d140_b30 unreduced`).
5. **Setting the effect size after knowing the probe's.** **Partly in it, and
   handled in the open:** I know the probe's effect sizes and §C.6 states that the
   frozen rule would not fire on them. The mitigation is that I took the
   program's standing inherited `4.0` gate rather than tuning one, and I recorded
   the adverse consequence in advance rather than letting it emerge as a surprise.
6. **Comparing against a `D` that is not on the same footing.** The reason this
   task exists. **Not in it:** the graded arm's `D` must reproduce the committed
   value bitwise, and that reproduction is an abort condition, not a report line.

## C.10 Seeds — reused, and introduced

**Reused, unchanged, and I confirm I did not modify them:** `seed_error(d)`,
`seed_haar(d,beta,j)`, `seed_graded(d,beta,j)`, `seed_basis(d,beta,i)` — the same
four families as §1, the cache verified at **32/32, max deviation `0.0`**
**[quoted: `report.md` §3]**. The measurement re-verifies that reproduction and
reports its max deviation before computing any `D`.

**Introduced by Section C**, for the synthetic families' coordinate supports:

```
seed_C(family, d, beta, a, h, j) = BASE[family] + d*10^6 + beta*10^4 + a*10^3 + h*10^2 + j
   BASE[P2]        = 300000000
   BASE[P3L]       = 600000000
   BASE[CTRL_PERM] = 900000000
```

`a` is the anchor index (`< 10`), `h` the `theta` index for P3L or the `rep` index
for CTRL-C-PERM (`< 10`), `j` the frame index (`< 100`). Validity conditions the
run **must assert**: `d < 1000`, `beta < 100`, `a < 10`, `h < 10`, `j < 100`.
Ranges: P2 `[3.00e8, 4.41e8]`, P3L `[6.00e8, 7.41e8]`, CTRL-C-PERM
`[9.00e8, 1.041e9]` — pairwise disjoint, disjoint from every committed family
(all below `2.1e7`), and disjoint from Section A's families (which start at
`1.100e9`). All below `2^31`.

---

## 5. Infrastructure-failure disposition

**A timeout, a crash, a missing dependency, an out-of-memory kill, or an exhausted
budget is INFRASTRUCTURE SIGNAL and is NEVER negative mathematical evidence, in
either direction.** `AGENTS.md` rule 3 and `agents/executor.md` failure semantics
apply in full. Specifically:

* An affected cell is reported as **NOT MEASURED**, with the failure class named
  (`infrastructure_error` or `resource_exhaustion`), and the partial grid is
  reported with its floor. **No extrapolation across a missing cell.**
* `fpylll` unavailability is an `infrastructure_error`. It is recorded, not worked
  around by substituting the producer's own bases: substituting them is precisely
  what makes `D` values non-comparable, which is why Section C exists.
* Exceeding Section C's `n_frames_total <= 200` memory cap is a **specification
  violation**, not a budget event, and the run stops rather than reducing `N`.
* If a Monte-Carlo verification fails — the `Var_haar(W)` check of §A.5, or the
  null-object simulation of §B.7 — that is an **instrument fault or a derivation
  fault in this document**, reported as such, and it is evidence for no mechanism.
* A failure to reproduce the committed 32/32 reduction cache, or a
  `prereg.md` sha256 mismatch, is a **harness failure**: the run aborts and
  reports, and does not proceed to any verdict.

Every deviation, every infrastructure event and every unexpected observation is
recorded in the run manifest and the report. None is discarded.

## 6. `what_this_is_not`

A run under this pre-registration **could not claim**, and must not be cited as
claiming:

1. **Anything about ML-KEM security, any FIPS 203 parameter set, or any attack
   cost. Claim tier TOY, unconditionally.** Every number is at `d <= 140`,
   `beta <= 112`, `q = 3329`, on q-ary bases. Nothing transports to
   `beta = 606`, `d = 1420`, or to any other parameter set, by extrapolation or by
   analogy.
2. **Any hypothesis status change.** The Executor records observations. Sections A,
   B and C move no hypothesis, promote nothing to knowledge, and adjudicate
   nothing. Only the Coordinator may change status.
3. **That either spill mechanism is TRUE.** Section A can falsify a mechanism at a
   stated floor, or fail to separate them. "Not falsified" is not "supported", and
   the frozen wording of §A.7 enforces that.
4. **That the AM-3 verdict is an out-of-sample test.** §B.0. The data is bitwise
   determined by committed seeds.
5. **That the AM-3 gate is correct because its rate is low.** A declared rate is a
   property of a rule under a stated null and a stated Gaussian assumption. §B.7's
   simulation is what checks it, and it can fail.
6. **That L2's variance identity is refuted.** §C.1. It is a theorem and Section C
   does not touch it. Only its extension to a `2^-10` tail quantile is at issue.
7. **AM-4 admissibility for `W`, `V`, `M3` or `D`.** None is shown invariant under
   ambient isometry or unimodular change of basis, and none is offered as an
   adjudicator. CTRL-C-PERM checks coordinate permutation only.
8. **Any statement of the form "the departure is absent"**, in any wording,
   anywhere, without its floor. Every negative is an upper bound at a declared
   floor in the statistic's own units.
9. **Anything about a BKZ-reduced basis at `k != d/2`.** Section A runs no BKZ; the
   omission is declared in §A.4 with its reason and its costed successor.
10. **That the six-instance "control scored where its defect is invisible" pattern
    is confirmed or refuted.** This document applies the lesson; it does not test
    the pattern, and `DEC-20260806-14ac13` explicitly withholds that promotion.

## 7. Provenance of every constant

| constant | value | provenance |
|---|---|---|
| `t` grid | 13 values, §B.6 | **[carried]** `DEC-20260806-14ac13` retains AM-1's grid |
| gate factor | `4.0 * SE_diff` | **[carried]** `b2a.py GATE_K = 4.0` |
| draws per arm | `8` | **[carried]** `config.draws_per_arm` |
| error draws per cell | `N = 2^20` | **[carried]** `config.errors_per_cell` |
| `mu_4` for CBD_{eta=2} | `2.5` exactly | closed form; measured `2.499610 / 2.500359` **[quoted: `report.md` §3]** |
| `mu_0 = E[V]_haar` | `2 beta (d-beta)/(d(d+2))` | theorem, validator-re-derived **[quoted]** |
| all committed seed families | §1 | **[carried]** `results.json seed_scheme`; unchanged here |
| A: `k` values | `{30,50,70}` at `d=100`; `{42,70,98}` at `d=140` | **[set here]**, §A.4, mirror pairs plus a `k=d/2` control |
| A: `beta` grids | `{20..80}` step 10; `{28..112}` step 14 | **[set here]**, §A.4, each contains its `d`'s three `k` |
| A: `W_L2`, `W_SUP` profiles | §A.1 | **[derived here]** from each mechanism's one-line statement plus `0 <= m_lead <= min(k,beta)` |
| A: `V` confined/saturated shapes | §A.2 | **[derived here]**; cross-checked at 0.02–2.29 % against six committed `V` |
| A: `Var_haar(W)` | `2 beta k (d-beta)(d-k)/(d^2(d-1)(d+2))` | **[derived here]**, four consistency checks, **MC-verification required before use** |
| A: shape tolerance | `0.05 * beta_max` = `4.0` / `5.6` | **[set here]**, 5 % of the largest frame mass scored |
| A: floor | `max(4 s_W/sqrt(8), 4 sd_haar(W)/sqrt(8))` | **[set here]**; a-priori part `0.447` at grid centre **[derived here]** |
| B: repair chosen | (c), margin in (a)'s units | **[set here]** from AM-3 `permitted_repairs` |
| B: `K_delta` | `1.0 * SE_diff(t_i)` | **[set here]**; the stricter of the two readings the validator priced |
| B: multiplicity `M` | `48` | **[set here]**, 12 steps x 4 cells, declared unconditionally |
| B: family-wise target | `0.05` | **[set here]**, half of AM-3's `0.10` refusal threshold |
| B: `alpha` | `0.05/48 = 0.0010416667` | **[derived here]**, Bonferroni |
| B: `t*_7` | `4.750074` | **[derived here]**, odd-`nu` closed form, confirmed by independent quadrature to 10 dp |
| B: declared rate | `<= 0.050000` | **[derived here]**, union bound, arbitrary dependence |
| B: `P(t_7 > 1)` | `0.175308` | **[quoted]** both reviews; recomputed here as a constant check only |
| B: withdrawn-rule rates | `0.9902`, `0.9014`, `0.00025` | **[quoted]** validator and red team; not recomputed as verdicts |
| B: null-simulation seed | `1450000000` | **[set here]** |
| C: estimator index | `1023` at `p = 2^-10` | **[carried]** frozen estimator |
| C: `V_min` floor | `beta/2 - beta^2/d` | **[derived here]**; explains the probe's missed third anchor **[quoted]** |
| C: admissible anchors | 13, enumerated §C.3 | **[derived here]** from committed `V` **[quoted: `report.md` §4, §7]** |
| C: `V`-match tolerance | `1e-9` relative | **[set here]**; analytic match, not searched |
| C: F-C1 threshold | `max(4 SE, 0.10 * abs(D_A))` | **[set here]**; `4.0` **[carried]**, `0.10` set here |
| C: F-C2 threshold | `|slope| > 4 SE(slope)` | **[set here]** |
| C: comparison counts | 26 pairs, 13 slopes | **[set here]**, declared uncorrected with the cost stated |
| C: memory cap | `n_frames_total <= 200` (`<= 0.84 GB`) | **[set here]**; the probe's own allocation was ~7.0 GB |
| C: power extension `n` | `32`, unscored | **[set here]** |

Nothing in this table depends on a measurement that does not yet exist. The
quantities computed at run time are exactly: `SE_diff`, `SE_step_paired`,
`SE_step_unpaired`, `delta_i`, the measured `V`, `W`, `M3` and `D` per frame, the
per-cell floors, the Monte-Carlo verification of `Var_haar(W)`, and the null-object
simulation of §B.7.

## 8. Notarization

* `prereg_sha256.txt` in this directory contains the sha256 of this file and
  nothing else.
* TASK-20260806-0a1072 snapshot-commits this directory **before**
  TASK-20260806-3084bc, -e17677 and -c973e6 are dispatched. Each measurement
  re-hashes this file, compares against the notarized receipt, and **aborts on
  mismatch**. A mismatch is a harness failure, not a result.
* Each measurement asserts the **notarizing commit itself**, not its parent. The
  AM-1 executor asserted the parent, so its own check would have passed had the
  notarization never happened **[quoted: `validation_report.yaml` N-1, finding
  V-7]**. `git merge-base --is-ancestor <notarizing_commit> <run_HEAD>` and
  `git log --follow` on this file are the checks.
* Whether the ordering is externally established is for the validator
  (TASK-20260806-7418bc) to judge against the git record, not for this document to
  assert. Git ancestry cannot exclude off-repository pre-computation in any case,
  and §B.0 records the one place where the data demonstrably predates the rule.

**Declaration, on the record: no lattice was generated or reduced, no GSO frame
was formed, no error draw was sampled, and no `V`, `W`, `M3`, `D` or arm statistic
was computed in the production of this document. The only computations performed
were closed-form algebra over committed numbers and Student-`t_7` tail
probabilities, both reproducible in a few lines by any reader.**
