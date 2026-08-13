# BATCH-a44d08 pre-registration — the three measurements, frozen before any data

TASK-20260806-843c40 / BATCH-a44d08 / GOAL-MLKEM-005
Executor artifact. **Claim tier TOY.** Nothing in this document, and nothing any
measurement it governs can produce, bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.

Governing authority: `ledger/decisions/DEC-20260806-14ac13.yaml`, amendments
**AM-3** (monotonicity criteria must declare a computed false-failure rate and a
multiplicity policy), **AM-4** (adjudicator invariance), and **AM-5** (the
`D_A(beta_2)/D_A(beta_1)` observable is withdrawn and the matched-`V`
cross-family comparison replaces it). Everything in `DEC-20260806-00deff` not
superseded by that decision remains in force, including the AM-1 13-point `t`
grid, which is **RETAINED and not re-litigated**.

This document governs three measurement tasks:

| task | section | what it runs |
|---|---|---|
| TASK-20260806-3084bc | **A** | `k != d/2` — the discriminating test between the two spill mechanisms |
| TASK-20260806-e17677 | **B** | the AM-1 graded family re-scored under the AM-3 replacement gate |
| TASK-20260806-c973e6 | **C** | the matched-`V` cross-family comparison, F-A1's replacement |

---

## 0. What this document is, and what was NOT done to produce it

### 0.1 The declaration

**No measurement of any kind was performed in producing this document.** No
lattice was generated, no lattice was reduced, no basis was built, no GSO frame
was computed, no error draw was sampled, no quantile was estimated, no `V`, `D`,
`E_I` or arm statistic was evaluated, and no `fpylll`, `numpy` RNG or lattice
code was executed.

Three classes of number appear below and every one is labelled:

* **[carried]** — a structural constant of the design, fixed by
  `DEC-20260806-00deff` / `DEC-20260806-14ac13` or carried verbatim from the
  committed frozen text of BATCH-436ddd / BATCH-f19c37.
* **[quoted: source]** — a value read out of a committed artifact, with its
  source named.
* **[closed form]** — evaluated here from an algebraic expression in
  `(d, k, beta, q, N, n)` alone, using `scipy.stats.t` for Student-`t` tail
  quantiles and elementary arithmetic for the projector algebra. These are
  properties of the *design*, computable before any object exists, and computing
  them is what AM-3 requires. **No [closed form] number below is a function of
  any lattice, any frame, any draw, or any measurement.**

Section 6 enumerates every constant with its class and provenance so a reviewer
can check this claim mechanically rather than take it on trust.

### 0.2 Why the producer split exists and is retained unchanged

`EV-MLKEM-94c773` records that BATCH-f19c37 closed the notarization gap **by
construction**: the freeze was a separate commit, made by a separate task,
containing nothing but the frozen text, and an ancestor of every commit carrying
a measurement artifact — a property of the repository rather than an assertion
by the producer. That pattern is retained here without modification.
TASK-20260806-0a1072 snapshot-commits this directory **before** any of
TASK-20260806-3084bc, -e17677 or -c973e6 is dispatched. Each measurement loads
this file read-only, re-hashes it, compares against the notarized receipt, and
**aborts on mismatch**.

Two carried corrections to that pattern, both binding on the successor tasks:

* **V-7.** BATCH-f19c37's measurement asserted the notarizing commit's PARENT,
  so its own ancestry check would have passed had the notarization never
  happened **[quoted: validation_report.yaml N-1 / V-7]**. Each measurement here
  asserts `git merge-base --is-ancestor <notarizing commit> HEAD` against the
  **notarizing commit itself**, and records the sha it asserted.
* **No early durability commit.** BATCH-f19c37's producer archive was REJECTED
  by `tools.research_dispatch.GitRepositoryVerifier` because three artifacts
  entered at a prior durability commit **[quoted: `DEC-20260806-14ac13`
  rationale]**. No measurement task in this batch makes one.

### 0.3 The arrangement in which THIS card could not fail, and why it is not running in it

**Named arrangement.** A pre-registration written *after* the numbers exist, or
written with thresholds chosen because the writer already knows what the data
will do, cannot fail: every falsifier it declares is one it has already seen
pass. This is the same failure the program has now recorded six times in other
dress — a check scored exactly where its own defect is invisible.

**Why this card is not in it.**

1. The freeze is externally notarized *before* the measurement tasks are
   dispatched (§0.2). The ordering is a property of the git record, not a
   statement by me. What that ordering cannot exclude is off-repository
   pre-computation, and §0.1 is the declaration that answers it; that residue is
   closed by harness structure, not by cryptography **[quoted:
   validation_report.yaml N-2]**.
2. Every threshold below is either **[carried]** from a committed decision or
   **[closed form]** from the design parameters. §6 lists all of them. A reader
   can recompute each one without any data from this batch.
3. **I am forbidden the one shortcut that would make this card easy.** The
   validator's item-3 counterfactual ("a gate-commensurable tolerance would
   return TIE in all four cells and hence PARTIAL") is POST-HOC and is
   prohibited by AM-3 from being cited as a result or as grounds for preferring
   a repair. It is not used anywhere below. §3.3 states the ground on which the
   Section B repair *was* chosen, and that ground is an operating-characteristic
   argument computable with no data at all.
4. The residual I cannot close: I chose which observables to freeze, and a
   different choice would test a different proposition. §2.7, §3.6 and §4.6
   name, per section, the specific proposition each section's observable does
   **not** reach.

---

## 1. Constants carried unchanged into all three sections

All **[carried]** from `DEC-20260805-4823db` / `DEC-20260806-00deff` as
implemented in the committed frozen text of BATCH-436ddd and BATCH-f19c37:

* `q = 3329`; error law `CBD_{eta=2}` (`mu_4 = 2.5` exactly).
* Statistic `R = ||Q^T e||^2 / ||e||^2`, `Q` the orthonormal tail-`beta` GSO
  frame taken as the last `beta` columns of `Q` from `QR(B^T)`.
* Estimator `q_emp(p) = sort(R)[round(p*N) - 1]` at `N = 2^20` draws per cell;
  index `1023` at `p = 2^-10`. `D = q_emp(2^-10)/q_Beta(2^-10) - 1`.
* `8` draws per arm (`draws_per_arm = 8`), every arm including every null.
* Gate: `SE_diff(A) = sqrt(sd_A^2/8 + sd_haar^2/8)`,
  `shift_SE(A) = (mean_j r_A - mean_j r_haar)/SE_diff(A)`,
  `gate(A) = |shift_SE(A)| >= 4.0`. **`4.0` is a nominal factor, not a
  p-value**, and the validator measured the realized one-sided false-positive
  rate at `0.0015-0.0025` against a nominal `3e-5`, a factor of about 60
  **[quoted: validation_report.yaml item 4 / V-5]**. Every report in this batch
  that cites the gate states this.
* Seeds carried: `seed_basis(d,beta,i) = 700000 + d*1000 + beta*10 + i`;
  `seed_error(d) = 20260805 + d`;
  `seed_haar(d,beta,j) = 900000 + d*1000 + beta*10 + j`;
  `seed_graded(d,beta,j) = 500000 + d*1000 + beta*10 + j`. **The seeds are the
  cache**; BATCH-f19c37 regenerated 32 of 32 reductions at max deviation `0.0`
  against both prior batches **[quoted: `EV-MLKEM-94c773`]**.
* Graded family `Q_t = QR( sqrt(1-t) * E_S + sqrt(t) * G )`, `(S_j, G_j)` drawn
  once per draw `j` from `seed_graded` **before and independently of the `t`
  list** and reused across every `t`, so the family is a path.
* `V = sum_a (P_aa - beta/d)^2 = sum_a P_aa^2 - beta^2/d` for `P = Q Q^T`, with
  the exact Haar expectation `E[V]_haar = 2*beta*(d-beta) / (d*(d+2))`. This is
  a theorem, re-derived independently by the validator from
  `P_aa ~ Beta(beta/2, (d-beta)/2)` and confirmed bit-exactly in four cells plus
  a 20,000-frame Monte Carlo **[quoted: validation_report.yaml item 4]**.

### 1.1 One correction of scope carried into every section

`V`, and every observable in Section A, is a property of a basis
**presentation**, not of a lattice. The red team demonstrated that an ambient
isometry `B -> BH` moves `V` from `9.32` to `0.27` to `0.40` on one lattice at
`(100,30)`, inverting the verdict of a predicate built on it **[quoted:
red_team_report.md §3.3]**. `AM-4` therefore REFUSES any such statistic as an
**adjudicator** of a claim about a lattice.

**This batch does not contest that and does not need to.** The propositions
Sections A and C test are propositions about the **q-ary construction's own
frame geometry** — where the tail GSO window of a specific basis presentation
sits relative to that presentation's own blocks, and whether the tail quantile
`D` is a function of `V` alone. Those are questions about the presentation, so a
presentation-dependent observable is the correct instrument for them. What
follows from any verdict below is therefore a statement about the construction
and about the statistic, and **never** a statement about a lattice invariant,
about reduction hardness, or about ML-KEM. Every report in this batch states
this in its own words.

---

## 2. SECTION A — `k != d/2`, the discriminating test

Run by TASK-20260806-3084bc. Named as unevaluated in five records across four
batches and never run **[quoted: `DEC-20260806-14ac13` next_actions, V-8].**

### 2.1 The two mechanisms, stated so that each can lose

The unreduced q-ary basis has two coordinate blocks: the block carrying the
identity part, written `K_I` with `|K_I| = k`, and the block carrying the
`q`-scaled rows, written `K_q` with `|K_q| = d - k`. Write
`Pi_I`, `Pi_q` for the coordinate projectors onto them, and for a rank-`beta`
tail frame `P = Q Q^T`:

```
E_I(beta) = tr(P Pi_I) / beta = (1/beta) * sum_{a in K_I} P_aa
E_q(beta) = 1 - E_I(beta)
```

**M-K — "confined to the `k`-block" (L2's mechanism).** The tail-`beta` GSO
window lies inside `K_I`, spread generically within it. The spill boundary is
`beta <= k`, because a `beta`-dimensional subspace fits inside a
`k`-dimensional coordinate block only while `beta <= k`.

**M-D — "confined to the `q·I` block" (the superseded mechanism).** The window
lies inside `K_q`. The spill boundary is `beta <= d - k`.

Both are zero-free-parameter claims. Under "generic within a coordinate block of
size `c`", `P_aa = beta/c` on the block and `0` off it, and for `beta > c` the
block fills and the excess `beta - c` dimensions spread generically over the
complement. That gives, exactly **[closed form]**:

```
E_I^{M-K}(beta) = min(1, k/beta)                 E_I^{M-D}(beta) = max(0, 1 - (d-k)/beta)

V_c(beta) = beta^2 (d-c) / (c d)                                    for beta <= c
V_c(beta) = c (1 - beta/d)^2 + (d-c) ((beta-c)/(d-c) - beta/d)^2    for beta >  c

M-K predicts V = V_k(beta);   M-D predicts V = V_{d-k}(beta).
```

Two committed anchors show these curves are the right *shape* and are the reason
the question is worth asking rather than an argument that either wins. At
`k = d/2` the two curves COINCIDE identically, which is exactly why four batches
cannot separate them: `V_k(30) = 9.00` against a committed `9.3628` at
`(100,30)`, `V_k(40) = 16.00` against `16.2446`, `V_k(30) = 6.43` against
`6.7504` at `(140,30)`, `V_k(40) = 11.43` against `11.8075`, and the `beta > c`
branch gives `V(60) = 16.00` at `(100,60)` against a committed `16.269`
**[quoted: red_team_report.md §3.1 and §5; `EV-MLKEM-94c773`]**. Every one of
those anchors is a `k = d/2` value at which M-K and M-D are numerically
identical, so **none of them is evidence for either mechanism** and none is
scored as such.

### 2.2 The cells, and why each `k` separates the two mechanisms

`k != d/2` and `k != d - k` are the **same condition** (`k = d-k` iff
`k = d/2`), and it is satisfied by every cell below.

| `d` | `k` | `d - k` | `k/d` (Haar null `E_I`) | `V_k/V_{d-k}` at `beta <= min` |
|---|---|---|---|---|
| 100 | 30 | 70 | 0.3000 | 5.444 |
| 100 | 70 | 30 | 0.7000 | 0.184 |
| 140 | 40 | 100 | 0.2857 | 6.250 |
| 140 | 100 | 40 | 0.7143 | 0.160 |

`d in {100, 140}` is **[carried]**. The two `k` at each `d` are a matched pair
`(k, d-k)`, which is deliberate: the pair has the same *set* of block sizes with
the roles of `K_I` and `K_q` **exchanged**, so a statistic that responds to block
*size* or to coordinate *index range* rather than to block *identity* returns the
same answer in both cells of a pair and is detected (§2.6).

`beta` grid per `d`, chosen to bracket both candidate boundaries from below, at,
and from above **[closed form: `{min, max} = {k, d-k}` per `d`]**:

```
d = 100 (boundaries 30 and 70):  beta in {15, 25, 30, 35, 50, 65, 70, 75, 85}
d = 140 (boundaries 40 and 100): beta in {20, 35, 40, 45, 70, 95, 100, 105, 120}
```

### 2.3 The frozen prediction table

All entries **[closed form]** from §2.1. `M-K/M-D` is the ratio of the two `V`
predictions and is the `V` arm's discriminating power at that `beta`.

**d = 100, k = 30** (`d-k = 70`, Haar `E_I = 0.3000`)

| beta | `E_I` M-K | `E_I` M-D | `|diff|` | `V` M-K | `V` M-D | `V` Haar | M-K/M-D |
|---|---|---|---|---|---|---|---|
| 15 | 1.0000 | 0.0000 | 1.0000 | 5.2500 | 0.9643 | 0.2500 | 5.444 |
| 25 | 1.0000 | 0.0000 | 1.0000 | 14.5833 | 2.6786 | 0.3676 | 5.444 |
| 30 | 1.0000 | 0.0000 | 1.0000 | 21.0000 | 3.8571 | 0.4118 | 5.444 |
| 35 | 0.8571 | 0.0000 | 0.8571 | 18.1071 | 5.2500 | 0.4461 | 3.449 |
| 50 | 0.6000 | 0.0000 | 0.6000 | 10.7143 | 10.7143 | 0.4902 | **1.000** |
| 65 | 0.4615 | 0.0000 | 0.4615 | 5.2500 | 18.1071 | 0.4461 | 0.290 |
| 70 | 0.4286 | 0.0000 | 0.4286 | 3.8571 | 21.0000 | 0.4118 | 0.184 |
| 75 | 0.4000 | 0.0667 | 0.3333 | 2.6786 | 14.5833 | 0.3676 | 0.184 |
| 85 | 0.3529 | 0.1765 | 0.1765 | 0.9643 | 5.2500 | 0.2500 | 0.184 |

**d = 100, k = 70** (`d-k = 30`, Haar `E_I = 0.7000`)

| beta | `E_I` M-K | `E_I` M-D | `|diff|` | `V` M-K | `V` M-D | `V` Haar | M-K/M-D |
|---|---|---|---|---|---|---|---|
| 15 | 1.0000 | 0.0000 | 1.0000 | 0.9643 | 5.2500 | 0.2500 | 0.184 |
| 25 | 1.0000 | 0.0000 | 1.0000 | 2.6786 | 14.5833 | 0.3676 | 0.184 |
| 30 | 1.0000 | 0.0000 | 1.0000 | 3.8571 | 21.0000 | 0.4118 | 0.184 |
| 35 | 1.0000 | 0.1429 | 0.8571 | 5.2500 | 18.1071 | 0.4461 | 0.290 |
| 50 | 1.0000 | 0.4000 | 0.6000 | 10.7143 | 10.7143 | 0.4902 | **1.000** |
| 65 | 1.0000 | 0.5385 | 0.4615 | 18.1071 | 5.2500 | 0.4461 | 3.449 |
| 70 | 1.0000 | 0.5714 | 0.4286 | 21.0000 | 3.8571 | 0.4118 | 5.444 |
| 75 | 0.9333 | 0.6000 | 0.3333 | 14.5833 | 2.6786 | 0.3676 | 5.444 |
| 85 | 0.8235 | 0.6471 | 0.1765 | 5.2500 | 0.9643 | 0.2500 | 5.444 |

**d = 140, k = 40** (`d-k = 100`, Haar `E_I = 0.2857`)

| beta | `E_I` M-K | `E_I` M-D | `|diff|` | `V` M-K | `V` M-D | `V` Haar | M-K/M-D |
|---|---|---|---|---|---|---|---|
| 20 | 1.0000 | 0.0000 | 1.0000 | 7.1429 | 1.1429 | 0.2414 | 6.250 |
| 35 | 1.0000 | 0.0000 | 1.0000 | 21.8750 | 3.5000 | 0.3697 | 6.250 |
| 40 | 1.0000 | 0.0000 | 1.0000 | 28.5714 | 4.5714 | 0.4024 | 6.250 |
| 45 | 0.8889 | 0.0000 | 0.8889 | 25.7857 | 5.7857 | 0.4301 | 4.457 |
| 70 | 0.5714 | 0.0000 | 0.5714 | 14.0000 | 14.0000 | 0.4930 | **1.000** |
| 95 | 0.4211 | 0.0000 | 0.4211 | 5.7857 | 25.7857 | 0.4301 | 0.224 |
| 100 | 0.4000 | 0.0000 | 0.4000 | 4.5714 | 28.5714 | 0.4024 | 0.160 |
| 105 | 0.3810 | 0.0476 | 0.3333 | 3.5000 | 21.8750 | 0.3697 | 0.160 |
| 120 | 0.3333 | 0.1667 | 0.1667 | 1.1429 | 7.1429 | 0.2414 | 0.160 |

**d = 140, k = 100** (`d-k = 40`, Haar `E_I = 0.7143`)

| beta | `E_I` M-K | `E_I` M-D | `|diff|` | `V` M-K | `V` M-D | `V` Haar | M-K/M-D |
|---|---|---|---|---|---|---|---|
| 20 | 1.0000 | 0.0000 | 1.0000 | 1.1429 | 7.1429 | 0.2414 | 0.160 |
| 35 | 1.0000 | 0.0000 | 1.0000 | 3.5000 | 21.8750 | 0.3697 | 0.160 |
| 40 | 1.0000 | 0.0000 | 1.0000 | 4.5714 | 28.5714 | 0.4024 | 0.160 |
| 45 | 1.0000 | 0.1111 | 0.8889 | 5.7857 | 25.7857 | 0.4301 | 0.224 |
| 70 | 1.0000 | 0.4286 | 0.5714 | 14.0000 | 14.0000 | 0.4930 | **1.000** |
| 95 | 1.0000 | 0.5789 | 0.4211 | 25.7857 | 5.7857 | 0.4301 | 4.457 |
| 100 | 1.0000 | 0.6000 | 0.4000 | 28.5714 | 4.5714 | 0.4024 | 6.250 |
| 105 | 0.9524 | 0.6190 | 0.3333 | 21.8750 | 3.5000 | 0.3697 | 6.250 |
| 120 | 0.8333 | 0.6667 | 0.1667 | 7.1429 | 1.1429 | 0.2414 | 6.250 |

### 2.4 Where the predictions coincide again, declared and excluded

**`beta = d/2` — the `V` arm is NON-DISCRIMINATING and is excluded from the `V`
verdict there.** At `beta = d/2` the two `V` curves cross exactly
(`V_k(50) = V_{70}(50) = 10.7143` at `d = 100`; `V_{40}(70) = V_{100}(70) =
14.0000` at `d = 140`) — the `M-K/M-D` column reads `1.000` **[closed form]**.
Agreement of the measured `V` with "the prediction" at `beta = d/2` is agreement
with **both** and is recorded as NOT DISCRIMINATING regardless of what it shows.
`beta = 50` at `d = 100` and `beta = 70` at `d = 140` are retained in the grid
because the `E_I` arm still discriminates there (`0.6000` vs `0.0000`, and
`0.5714` vs `0.0000`), and because dropping a point after seeing the design
would be the same error in the opposite direction.

**No `k` in §2.2 makes the two predictions coincide.** `E_I^{M-K} - E_I^{M-D}`
is `(d - beta)/beta` for `beta > max(k, d-k)` and larger below, so it is bounded
below by `0.1667` over the entire grid **[closed form]**; the `V` ratio departs
from `1` at every `beta != d/2`.

### 2.5 Detection floor, thresholds, and the two verdicts

Per `(d, k)`: `n = 8` independent bases, `i = 0..7`. `E_I` and `V` are exact
deterministic scalars of each frame — no error draws, no quantiles. The only
noise is between-instance dispersion, measured by the red team at under `1%` of
the value on unreduced arms **[quoted: red_team_report.md §3.1]**.

```
SE_X = sd_i(X) / sqrt(8)                    [ddof = 1],  X in {E_I, V}
tol_E    = max( 4.0 * SE_{E_I} , 0.02 )
tol_V(m) = max( 4.0 * SE_V     , 0.02 * V_pred(m) )      m in {M-K, M-D}
```

`4.0` is **[carried]** from the gate factor; the absolute components `0.02` and
`2%` are **set here**, at the order of the measured between-instance dispersion
and of the `<= 2%` agreement the closed-form `V` already shows against committed
`k = d/2` values, and they exist to keep the criterion from becoming arbitrarily
sensitive as `SE -> 0`. **This is the AM-3 lesson applied to Section A**: a
tolerance denominated only in a shrinking noise scale collapses exactly where
the effect it polices vanishes, and BATCH-f19c37's `t = 0` anchor produced
`SE ~ 0` and `z ~ 3e16` in practice **[quoted: validation_report.yaml item 6,
cosmetic defect]**. If `SE_X == 0` exactly, the absolute component governs and
the point is flagged `DEGENERATE_EXACT`; no division by zero is performed.

Per `(d, k, beta)`, for each mechanism `m`:

* `E_I` arm: `m` is **FALSIFIED at that point** iff
  `|E_I_meas - E_I^m(beta)| > tol_E`.
* `V` arm: `m` is **FALSIFIED at that point** iff
  `|V_meas - V_c(beta)| > tol_V(m)`, excluding `beta = d/2` (§2.4).

Per `(d, k)` cell:

* **SUPPORTS M-K** — M-K is falsified at no point and M-D is falsified at at
  least one discriminating point.
* **SUPPORTS M-D** — the mirror.
* **NEITHER** — both falsified at at least one point each. The measured curve is
  reported in full beside both predictions, and **this is a real deliverable**,
  not a failed run: it answers a question five records have deferred.
* **NOT SEPARATED** — neither falsified anywhere. Reported as an upper bound:
  "the two mechanisms differ by at most `<tol>` in `E_I` / `V` units at `n = 8`
  bases", never as a statement that either is correct.

The overall Section A result is the four cell results reported side by side. No
cell result is aggregated into a single verdict, because the four cells are two
mirrored pairs and averaging a mirrored pair destroys exactly the contrast the
design is built on.

**Wording, frozen.** No arm may be reported as "absent", "no departure",
"vanishes", "consistent with zero" or any synonym. Every negative is an upper
bound at the floor above, stated with the floor. This is a completion-gate item
**[carried: `DEC-20260806-00deff`]**.

### 2.6 Construction, seeds, and the null objects — all declared now

**The basis is built explicitly by the measurement, not by `fpylll`.** Reason:
the `fpylll` `qary` generator's block convention (which coordinate range carries
`I_k` and which carries `q I_{d-k}`) is **indistinguishable from committed data,
because every committed run has `k = d/2`**, where the two conventions give
identical `V`. Building the basis explicitly removes the ambiguity entirely and
removes any `2k <= d` restriction the generator may impose. Frozen construction,
in exact integer arithmetic:

```
seed_basis_k(d,k,i) = 810000 + d*1000 + k*10 + i,   i = 0..7
rng = numpy.random.default_rng(seed_basis_k(d,k,i))
A   = rng.integers(0, q, size=(k, d-k))             q = 3329  [carried]
B   = [[ I_k , A ], [ 0 , q * I_{d-k} ]]            K_I = coords 1..k ; K_q = coords k+1..d
frame: last beta columns of Q from QR(B^T), float64
```

**Structural disclosure, not a scored arm:** the measurement additionally calls
`IntegerMatrix.random(d, "qary", k=d//2, q=3329)` once at `d = 100` and reports,
by inspecting the integer entries alone, which coordinate range carries the
`q`-scaled rows. This is a read of an integer matrix, not a statistic, and it is
reported so the record finally states the convention. If `fpylll` is
unavailable, this disclosure is recorded as not obtained — **infrastructure, not
a result** (`AGENTS.md` rule 3).

**Arms.** `A-unreduced` (primary — the arm both mechanisms are about) and
`A-lll` (LLL-only, secondary). **NO BKZ**: the batch thesis forbids new BKZ and
no committed reduction exists at these `k`. If LLL exceeds its share of the
budget the `A-lll` arm is reported as not measured, as infrastructure.

**Null objects, run identically and scored identically** (`docs/inventor-protocol.md`,
controls before belief):

* **N-A1 — Haar frame.** `seed_haar_k(d,k,j) = 910000 + d*1000 + k*10 + j`,
  `j = 0..7`; one `d x d` Haar orthogonal matrix per `j` (QR of a standard
  normal `d x d`, columns sign-fixed by `sign(diag(R))`), tail `beta` columns
  taken for every `beta`, so the family is nested across `beta` exactly as the
  real arm is. Prediction: `E_I = k/d` and `V = 2 beta (d-beta)/(d(d+2))`
  **[closed form, exact]**. A Haar arm that departs from these is an instrument
  fault and is reported as one.
* **N-A2 — ambient coordinate permutation.** The same `B`, with a random
  permutation `pi` of the ambient coordinates applied
  (`seed_perm(d,k,i) = 920000 + d*1000 + k*10 + i`), scored against the
  **unpermuted** index ranges `1..k` and `k+1..d`. Prediction: `E_I -> k/d`, the
  Haar value. This separates "the statistic measures the block" from "the
  statistic measures low coordinate indices".
* **N-A3 — block swap.** `B' = [[ q I_{d-k} , 0 ], [ A^T , I_k ]]` with the
  **same** `A`, so `K_q = coords 1..d-k` and `K_I = coords d-k+1..d`. Prediction
  under M-K: `E_I` follows the `I`-block to its new coordinate range, i.e. the
  M-K curve is unchanged when scored against the *relocated* `K_I`. If instead
  the measured quantity follows the coordinate range, the observable is
  measuring index position and Section A is INADMISSIBLE — declared now, and the
  run reports that as its result if it happens.

### 2.7 The arrangement in which Section A could not fail, and why it is not running in it

**Named arrangement, precisely.** For every rank-`beta` projector `P` and every
coordinate set `S`, `tr(P Pi_S) <= min(beta, |S|)` — a sum of squared cosines of
principal angles. Therefore `E_I(beta) <= min(1, k/beta)` **identically**, for
the real arm, for a Haar frame, for `Z^d`, for anything. A design that declared
"M-K predicts confinement breaks above `beta = k`" and then scored "`E_I < 1` for
`beta > k`" would be reporting an algebraic identity as a measurement, and it
would confirm M-K on a Haar frame. That is the P3 failure in new clothes: an
anchor placed exactly where the statistic attains its bound.

**Four reasons this section is not in it.**

1. **The scored quantity is the signed distance from BOTH closed-form curves**,
   not the bound. In the region `beta <= min(k, d-k)` — nine of the grid points
   per `d` across the two cells — the capacity bound is `1` for **both** blocks,
   so it forbids neither mechanism, and M-K and M-D differ by the full `1.0000`
   in `E_I`. That region carries the section's primary weight.
2. **The Haar null N-A1 is scored on the identical code path** and its
   prediction `E_I = k/d` is nowhere near either mechanism's. If the real arm and
   the Haar arm return the same curve, the observable is measuring nothing and
   the section says so.
3. **The mirrored `k` pairs** `(30, 70)` at `d = 100` and `(40, 100)` at
   `d = 140` make the prediction tables exact mirrors of one another. Any
   statistic responding to block *size* or index *position* rather than block
   *identity* gives the same answer in both members of a pair; the design detects
   that without needing a separate control. **N-A3** tests it directly by
   physically exchanging the blocks' coordinate ranges.
4. **I state the one place M-K genuinely cannot be falsified upward.** In the
   window `min(k,d-k) < beta <= max(k,d-k)` with `k < d/2` — `beta in {35, 50,
   65}` at `(100,30)` and `{45, 70, 95}` at `(140,40)` — M-K's prediction
   `E_I = k/beta` **is** the capacity bound, so it can only be falsified
   downward. It can be, and M-D's prediction of `0.0000` there is well inside the
   permitted range `[0, k/beta]`, so the comparison is still two-sided *between
   the mechanisms*. Declared now rather than discovered by a reviewer.

**What Section A does not reach.** It measures where the tail window of a
specific unreduced (and LLL-only) basis presentation sits relative to that
presentation's own blocks. It says nothing about any lattice invariant, nothing
about reduction, nothing about the `2^-10` tail law, and nothing about ML-KEM
(§1.1). It is not offered as an AM-4 adjudicator and does not claim to satisfy
AM-4.

**Novelty accounting, declared now.** That the window sits in the `I` block
rather than the `q·I` block was already measured **at `k = d/2`**: window energy
in the `q·I` block `0.00000`, and the `beta = 60 > k` energy fraction
`0.83333 = k/beta` exactly **[quoted: BATCH-436ddd red_team_report.md §2]**. The
block-identity result at these new `k` is therefore a **REPRODUCTION at new block
sizes** and the report must label it so. What is **NOVEL** here, and unavailable
at `k = d/2` by construction, is (i) the boundary — `k` or `d-k` — and (ii) the
`V` magnitude, whose two predictions differ by a factor `((d-k)/k)^2` of `5.44`
to `6.25` at `k != d/2` and by exactly `1` at `k = d/2`.

---

## 3. SECTION B — the AM-3 replacement for the withdrawn G3

Run by TASK-20260806-e17677, on the AM-1 13-point `t` grid, which is
**RETAINED** and not re-litigated. Only the gate changes. G1 and G2 are
**[carried]** verbatim from BATCH-f19c37 §4 and are reported separately per cell.

### 3.1 The withdrawn rule, and the exact property that made it defective

`DEC-20260806-14ac13` WITHDRAWS the `1.0 * SE_step_paired` tie tolerance. Its
defect, stated as a property rather than as a count: **its rejection region
converges to `{Delta > 0}` as the precision improves.** A threshold that is a
fixed multiple of an *estimated* standard error can never become lenient,
because the thing it is a multiple of shrinks exactly as fast as the precision
does; `P(t_7 > 1.0) = 0.175309` and the `nu -> inf` limit is `0.1587`
**[quoted: red_team_report.md §2.1; validation_report.yaml item 3]**. Twenty-four
of forty-eight steps had neither endpoint clearing the design's own gate, and
`P(at least one FAIL) = 0.9902` on a flawless instrument. The rule is not
available to me and is not used.

### 3.2 The AM-3 criterion, frozen

Repair (a) **and** (c) of AM-3's permitted list, combined: the tolerance is
denominated in the **gate's own units**, and the criterion is stated as a
one-sided test against a pre-registered practically-negligible increase.

For each of the 12 consecutive pairs `(t_i, t_{i+1})` of the 13-point grid, per
cell, with `m(t) = mean_j r_A(2^-10)`:

```
Delta_i        = m(t_{i+1}) - m(t_i)                             (an increase if > 0)
SE_step(i)     = sd_j( r_j(t_{i+1}) - r_j(t_i) ) / sqrt(8)       [ddof = 1, paired]
epsilon_i      = 1.0 * SE_diff(A, t_i)                           (gate units, lower endpoint)

STEP VIOLATION  iff  ( Delta_i - epsilon_i ) / SE_step(i)  >  t_crit
t_crit = t_{7, 0.998} = 4.2071245566046755                       [closed form, scipy.stats.t]
```

`SE_diff(A, t)` is the arm-versus-Haar SE the design already uses to decide
whether a frame carries information at all, so `epsilon_i` is **one quarter of
the `4.0 * SE_diff` gate width** at the step's lower endpoint. Degenerate cases,
frozen now: if `SE_diff(A, t_i) == 0`, use `SE_diff(A, t_{i+1})`; if both are
`0`, or if `SE_step(i) == 0`, the step is flagged `DEGENERATE` and scored as a
violation iff `Delta_i > epsilon_i` directly, with no division.

Per cell:

* **AM3-PASS** — no step has `Delta_i > 0`.
* **AM3-TIE** — some step has `Delta_i > 0`, and no step is a VIOLATION.
* **AM3-FAIL** — at least one step is a VIOLATION.

Validity table **[carried, BATCH-f19c37 §4.2]**, with AM3 in G3's place:
`G1 clears + G2 does not fire + PASS = VALID`; `... + TIE = PARTIAL`;
`... + FAIL = INVALID`; `G1 fails` or `G2 fires` = INVALID. The overall verdict
is the most severe cell verdict. INVALID remains an **instrument outcome** and is
never evidence about lattices in either direction.

### 3.3 The false-failure rate on a flawless instrument — computed, with derivation

**Definition of "flawless instrument", frozen:** the true mean curve `m(t)` is
non-increasing in `t`, i.e. the true `Delta_i <= 0` at every step, and the paired
per-draw differences are exchangeable across the 8 draws.

**Per-step rate.** Under a true `Delta_i = 0`, the paired statistic
`Delta_i / SE_step(i)` is exactly Student-`t` on `7` degrees of freedom: 8 paired
draws, sample sd with `ddof = 1`. This is the exact reference distribution, not
an approximation **[quoted: validation_report.yaml item 3, false_flag_arithmetic;
red_team_report.md §2.1]**. Since `epsilon_i >= 0` **pointwise** — it is a
positive multiple of a standard error — we have, for any realization of
`epsilon_i` whatsoever, including one correlated with `SE_step(i)`:

```
P( VIOLATION )
  = P( Delta_i - epsilon_i > t_crit * SE_step(i) )
 <= P( Delta_i           > t_crit * SE_step(i) )            since epsilon_i >= 0
  = P( t_7 > t_crit )
  = P( t_7 > 4.2071245566046755 )
  = 0.002000                                                [closed form]
```

and for a true `Delta_i < 0` it is strictly smaller. **The bound is free of every
nuisance parameter**: it does not depend on `epsilon_i`, on `SE_diff`, on the
ratio `SE_step/SE_diff`, on the number of saturated steps, or on how flat the
family is. That is the reason this form was chosen over a bare `K * SE_diff`
threshold, whose false-failure rate is a function of the realized
`SE_step/SE_diff` ratio and would therefore be declared **conditional on a
nuisance quantity the run itself supplies** — which is the AM-3 failure mode, not
a repair of it.

**Multiplicity policy, explicit.** The AM-3 family is exactly

```
12 steps  x  4 cells  =  48 comparisons
```

and nothing else. G1 and G2 are **not** in this family: they are two per-cell
gates carried unchanged, they are reported separately, and no p-value or
significance level is claimed for them anywhere (as `DEC-20260806-00deff` froze).
The overall verdict is the max over the 48, so the rate that matters is the
family-wise one. Per-step level is set at `alpha = 0.002` and:

```
FAMILY-WISE FALSE-FAILURE RATE (union bound, valid under ANY dependence
among the 48 steps, and steps sharing an endpoint are dependent):

    P( at least one VIOLATION | flawless instrument )  <=  48 * 0.002  =  0.096

Reference figure under the independence approximation (Sidak), reported for
comparison only and NOT the declared rate:

    1 - (1 - 0.002)^48  =  0.0916233087376801
```

> ### **DECLARED FALSE-FAILURE RATE ON A FLAWLESS INSTRUMENT: 0.096**
> **Per-step level `alpha = 0.002`; multiplicity family `12 x 4 = 48`
> comparisons; union bound `48 x 0.002 = 0.096 <= 0.10`.**

This is an upper bound holding under arbitrary dependence, and the realized rate
is strictly below it whenever any true step is strictly decreasing. Against the
withdrawn rule's `0.9902` **[quoted]**, the change is a factor of about ten in
the exponent of the wrong outcome — but the figure that binds is `0.096`, and it
is declared here, before any datum of this batch exists, which is what AM-3
requires and what AM-1 did not do.

### 3.4 Power — what the AM-3 gate can still catch

A criterion with a low false-failure rate that can never fire is the mirror
defect, so the operating point is declared too. A step whose **true** increase is
`Delta` is flagged with probability `1/2` at approximately

```
Delta_50%  =  epsilon_i + t_crit * SE_step(i)
           =  1.0 * SE_diff + 4.2071 * (SE_step / SE_diff) * SE_diff
```

The ratio `SE_step_paired / SE_diff` was measured at `0.3599` and `0.4228` at the
two failing steps of BATCH-f19c37 **[quoted: validation_report.yaml item 3]**.
**Conditional on that ratio recurring** — and it is a measured quantity, so this
statement is conditional and the false-failure rate of §3.3 is not:

```
Delta_50%  ~=  2.52 to 2.77  x SE_diff   =  0.63 to 0.69  of the 4.0*SE_diff gate width
```

So AM-3 flags a monotonicity violation at roughly two thirds of the width the
design calls detectable. It is not a gate that cannot fire.

### 3.5 The mandatory positive control, frozen now

Because §3.4's power statement is conditional on a measured ratio, it is not
allowed to stand alone. The measurement **must** run, and report, an injected
positive control on its own recorded paths:

> For each cell, take the recorded per-draw graded paths, add a constant
> `c * SE_diff(A, t_i)` to every draw at one grid point `t_{i+1}` (creating a
> known monotonicity violation of exactly that size at step `i`), and re-score
> the AM-3 criterion, for `c in {1, 2, 3, 4, 6}` and for `i` = the step whose
> lower endpoint has the **largest** `SE_diff` in that cell (the hardest step to
> flag, fixed by a data-independent rule). Report the smallest `c` at which the
> cell returns AM3-FAIL.

**Frozen admissibility clause: if any cell fails to return AM3-FAIL at
`c = 6`, the AM-3 gate is declared INADMISSIBLE for this goal and the
demonstration reports that as its result**, with no verdict on the real arms.
A gate that cannot flag a violation `1.5` times the width its own design calls
detectable is not a criterion.

The injection is arithmetic on already-recorded values; it reduces no lattice,
draws no error, and is not an additional measurement of any object.

### 3.6 The arrangement in which Section B could not fail, and why it is not running in it

**Named arrangement, two forms.**

* *Form 1 — the mirror of AM-1.* Setting `alpha` and `epsilon` so loose that no
  real path can ever violate. Then "the instrument is VALID" is a property of the
  gate, exactly as "INVALID" was a property of the withdrawn gate. Six times this
  program has scored a control where its defect was invisible; buying a `0.096`
  false-failure rate with a gate that cannot fire would be the seventh.
* *Form 2 — the AM-3 loophole.* Declaring a rate that is secretly conditional on
  a nuisance quantity the run supplies, so that the declaration is not a
  pre-registration at all.

**Why this section is not in either.**

1. Against Form 1: the pre-registered **positive control** of §3.5, with a
   frozen INADMISSIBLE branch, plus the explicit operating point of §3.4. The
   gate is required to demonstrate that it fires, on this batch's own data, at a
   declared violation size, and the demonstration is scored on the *hardest* step
   in each cell by a data-independent rule.
2. Against Form 2: the derivation in §3.3 is a bound over **all** values of
   `epsilon_i` and `SE_step(i)`. Nothing measured enters it. The one statement
   that *is* conditional — the power in §3.4 — is labelled conditional and is
   backed by §3.5, which is not.
3. Against the withdrawn rule's specific defect: `epsilon_i > 0` means the
   rejection region converges to `{Delta > epsilon}` and not to `{Delta > 0}` as
   `SE_step -> 0`. The paired SE reappears as the test statistic's scale — it is
   the correct SE for a paired design and the validator confirmed it — but the
   **rule** that was withdrawn, a fixed multiple of that SE with no absolute
   floor and no multiplicity policy, is not reused. This decomposition is stated
   plainly so a reviewer can challenge it rather than having to discover it.
4. The validator's item-3 counterfactual played no part in choosing this repair
   and is not cited. §3.3's ground is an operating characteristic computable with
   no data at all.

**What Section B does not reach.** A VALID or PARTIAL verdict licenses only what
G1, G2 and monotonicity license about the *instrument*. It adjudicates no law,
and `EV-MLKEM-94c773` records that this instrument at 8 draws is `9-13x` too
coarse to resolve the residual that survives reduction **[quoted:
validation_report.yaml item 5]**. That limit is unchanged by a new gate, and any
negative on a real arm is an upper bound at the §5.1 floor of the AM-1
pre-registration, never a statement of absence.

---

## 4. SECTION C — the matched-`V` cross-family comparison, F-A1's replacement

Run by TASK-20260806-c973e6. AM-5 withdraws `D_A(beta_2)/D_A(beta_1)` at fixed
reduction as an observable and names this comparison as the replacement.

### 4.1 The proposition under test

L2's mechanism content, stripped of its magnitude map, is: **`D` depends on the
frame only through `V`.** The frozen F-A1 scored that on the NOVEL subset, which
the pre-registration itself defines as graded-path points only; along that path
`V(t)` and `D(t)` are both monotone in `t`, so "zero violating pairs" was forced
by the construction **[quoted: red_team_report.md §4.1; `EV-MLKEM-94c773`]**. The
recorded CONSISTENT verdict stands and is not rescored. What is frozen here is a
comparison the earlier design did not contain.

The boundary is already measured and is stated so the section does not overclaim
in either direction: `Var(e^T P e) = 2 beta + (mu_4 - 3)(V + beta^2/d)` **is** a
function of `V` alone, so **L2's derivation is correct at second order**; the
open question is only whether the `2^-10` tail quantile inherits that, its third
cumulant involving `sum_a P_aa^3` independently of `V` **[quoted:
`DEC-20260806-14ac13` rationale]**. A falsification below refutes the
**tail-level** claim and **not** the variance-level derivation, and the report
must say so in those words.

### 4.2 The two families and the matching rule

* **GR — the graded family**, `Q_t = QR(sqrt(1-t) E_S + sqrt(t) G)`, seeds
  `seed_graded(d,beta,j)`, on the AM-1 13-point grid. **[carried]** Pure numpy;
  the committed frames regenerate exactly from the seed scheme.
* **TL — the two-level family.** A rank-`beta` projector supported on `2 beta`
  coordinates with `P_aa in {u, 1-u}`, `beta` coordinates of each, `u in
  [1/2, 1]`. Constructed as `P = sum` of `beta` mutually orthogonal rank-1
  projectors on the 2-dimensional coordinate pairs `(a, a+beta)`, each with
  diagonal `(u, 1-u)`. With `m = beta/d`, exactly **[closed form]**:

```
V_TL(u)  = beta[ (u-m)^2 + (1-u-m)^2 ] + (d - 2 beta) m^2          increasing on [1/2, 1]
m3_TL(u) = beta[ (u-m)^3 + (1-u-m)^3 ] + (d - 2 beta) (-m)^3
inverse : u = 1/2 + sqrt( S/2 - (1/2 - m)^2 ),  S = ( V - (d-2beta) m^2 ) / beta
```

Reachable `V` interval per cell, `[V_TL(1/2), V_TL(1)]` **[closed form]**:

| cell | `2 beta <= d` | reachable `V` | Haar `E[V]` |
|---|---|---|---|
| (100, 30) | yes | `[6.000000, 21.000000]` | 0.411765 |
| (100, 40) | yes | `[4.000000, 24.000000]` | 0.470588 |
| (140, 30) | yes | `[8.571429, 23.571429]` | 0.331992 |
| (140, 40) | yes | `[8.571429, 28.571429]` | 0.402414 |

**V-matching tolerance, frozen: `|V_TL - V_GR| <= 1e-9` absolute**, achieved by
the closed-form inverse above in float64; the measurement **reports the achieved
`|V_TL - V_GR|` for every pair**. A target `V` outside the reachable interval is
declared `UNREACHABLE` and excluded, with the exclusion reported.

**Estimator and pairing, frozen.** `D = q_emp(2^-10)/q_Beta(2^-10) - 1` with
`q_emp = sort(R)[1023]` at `N = 2^20` **[carried]**. Within a cell, **the same
error draws** (`seed_error(d)`, carried) are used for the GR and TL members of a
pair and for all 8 draws, so `D_GR - D_TL` is a paired difference;
`SE(D_GR - D_TL) = sd_j(D_GR,j - D_TL,j)/sqrt(8)`, `ddof = 1`.

### 4.3 The primary comparison set, fixed now

Per cell, the primary targets are chosen by a rule that uses no measurement:

1. Take the 13 graded grid points.
2. Drop any whose `V` is `UNREACHABLE` for TL (§4.2).
3. Drop any **degenerate** point, defined as `|V - beta(1 - beta/d)| <= 1e-9`
   (see §4.6 — at that `V` both families are coordinate projectors and agreement
   is forced).
4. Order the survivors by `t` ascending; take the **first** and the **third**.
   If exactly two survive, take both; if exactly one survives, take it; if none
   survives, the cell contributes no graded target and that is reported. `n_C` is
   recomputed from the realized count and both the declared and realized counts
   are reported, with the Bonferroni level taken at the realized `n_C`.
5. Add the **unreduced real-lattice arm** of that cell as a third target
   (its `V` is `9.3628 / 16.2446 / 6.7504 / 11.8075` in the four cells
   **[quoted: `EV-MLKEM-94c773`, red_team_report.md §3.1]**, all inside the
   reachable intervals above). This arm needs basis generation and a QR from the
   committed `seed_basis`, and **NO BKZ**.

```
n_C = 3 targets x 4 cells = 12 primary comparisons
n_C = 2 targets x 4 cells =  8 primary comparisons   if fpylll is unavailable
```

The `fpylll`-unavailable branch is declared **now** with its own critical value
so that nothing is selected after the fact; an unavailable dependency is
infrastructure and is reported as such, never as a result (`AGENTS.md` rule 3).

### 4.4 The falsification criterion and the detection floor

**Family-wise false-falsification is controlled at `0.10` by Bonferroni over the
declared `n_C`** — the same discipline Section B applies, so that the falsifier
cannot fire by multiplicity alone:

```
n_C = 12 : per-pair two-sided level 0.10/12 = 0.008333 ; |t| crit = 3.6358074219539622
n_C =  8 : per-pair two-sided level 0.10/8  = 0.012500 ; |t| crit = 3.3352949398170852
                                                          [closed form, t_7]
```

A matched-`V` pair is a **FALSIFYING PAIR** iff **both** hold:

```
(i)  | D_GR - D_TL | / SE(D_GR - D_TL)  >  |t| crit for the declared n_C
(ii) | D_GR - D_TL | / max(|D_GR|, |D_TL|)  >  0.05          (5 percent, relative)
```

Condition (ii) exists so that a statistically resolvable but practically
negligible offset is not recorded as a mechanism failure; `0.05` is **set here**,
at the order of the `1.0-1.7x` magnitude defect the map is already known to
carry, so a difference smaller than `5%` is inside the noise of the object being
claimed **[quoted: BATCH-436ddd red-team report §5, via the AM-1
pre-registration §6.1]**.

Verdicts:

* **L2 TAIL-SUFFICIENCY FALSIFIED** — at least one FALSIFYING PAIR. Refutes the
  claim that `D` is a function of `V` alone **at the `2^-10` quantile**, and
  explicitly **not** the second-order derivation (§4.1).
* **CONSISTENT** — no FALSIFYING PAIR, and at least one pair is INFORMATIVE
  (§4.5) and has a detection floor below `5%` relative.
* **UNDERPOWERED — UPPER BOUND** — no FALSIFYING PAIR and the floor
  `|t|crit * SE(D_GR - D_TL) / max(|D_GR|,|D_TL|)` exceeds `5%` for every pair.
  Reported as "any difference is bounded above by `<number>` percent at `n = 8`",
  **never** as CONSISTENT and never as absence.
* Any pair in the band `3.0 SE <= |t| < |t|crit` with `> 5%` relative difference
  is recorded as **SUGGESTIVE, NOT FALSIFYING**, with its exact values, so that
  a near-miss is on the record rather than discarded. `P(|t_7| > 3.0) =
  0.019942126131992522` per comparison **[closed form]**, which is why `3.0`
  alone is not the bar over `n_C` comparisons.

The measurement **reports `D`, `V`, `m3 = sum_a (P_aa - beta/d)^3`, the achieved
`|V_TL - V_GR|`, and `SE(D_GR - D_TL)` for every member of every pair**, scored
or not.

### 4.5 Informativeness — a pair whose third moments agree tests nothing

The candidate mechanism for a `V`-matched difference is the third diagonal
moment. A pair whose `m3` values happen to coincide therefore cannot exhibit the
effect, and scoring it would dilute the family for nothing. **Frozen: a pair is
INFORMATIVE iff `|m3_GR - m3_TL| > 0.1 * max(|m3_GR|, |m3_TL|)`.** Non-informative
pairs are reported with their values and are excluded from `n_C` **before** the
critical value is fixed; if this changes `n_C`, the Bonferroni level is
recomputed from the reduced `n_C` and both counts are reported. Because `m3` is a
deterministic function of the frames and involves no draws, this exclusion uses
no `D` value and cannot be tuned to an outcome.

### 4.6 The arrangement in which Section C could not fail, and why it is not running in it

**Named arrangement, three forms.**

* *Form 1 — the F-A1 defect itself.* Scoring co-monotonicity within a single
  monotone path, where the verdict is forced by the construction.
* *Form 2 — matching at the degenerate `V`.* At `V = beta(1 - beta/d)` — the
  global maximum of `V`, attained at `t = 0` for GR and at `u = 1` for TL — both
  families are **the same object**: a coordinate projector on `beta` axes, up to
  a permutation of coordinates that the error law's exchangeability makes
  irrelevant. `D_GR = D_TL` there is forced by identity, not by mechanism. This
  is precisely the P3 failure: an anchor placed on the one object where the
  statistic attains its bound.
* *Form 3 — a decoy second family.* Choosing a TL family whose `m3` tracks GR's,
  so equal `V` implies equal everything and agreement is again forced.

**Why this section is not in any of them.**

1. Against Form 1: **every scored pair is cross-family by construction.** The
   comparison is GR against TL at equal `V`; there is no within-path pair in the
   primary set.
2. Against Form 2: step 3 of §4.3 **excludes the degenerate point by rule**,
   before any data, at tolerance `1e-9`. The measurement is additionally required
   to **report** the degenerate point as an INSTRUMENT CHECK — it must show
   `D_GR ~= D_TL` there — and that agreement is never counted as support for
   anything.
3. Against Form 3: §4.5 requires a **declared separation in `m3`** for a pair to
   enter the family at all, and `m3` is reported for every frame. The closed-form
   `m3_TL` values reproduce the red team's independently constructed frames
   (`+0.980040` and `-0.568440` at the two `V` targets it used at `(100,30)`
   **[quoted: red_team_report.md §4.2]**), which is a check that my construction
   is the same object as theirs, and is not evidence about `D`.
4. Against the opposite defect — a falsifier that cannot fire — §4.4 declares the
   **detection floor** and forces an UNDERPOWERED verdict rather than a
   CONSISTENT one when the floor sits above the effect size.

**What Section C does not reach.** It compares two synthetic frame families, plus
one unreduced real-lattice frame, at `d <= 140` and `beta <= 40`. It tests the
`2^-10` tail-level sufficiency of `V` and nothing else: not the variance-level
identity, which is already established; not any reduced arm; not any lattice
invariant (§1.1). **If the effect does not reproduce against the committed
bases, that is the result and it is reported as such** — the red team's finding
is a probe on its own frames, at TOY tier, `d = 100`, `beta = 30` only, with
`fpylll` unavailable in that session so its `D` values are not absolutely
comparable, and it is not a fact this batch is required to confirm.

---

## 5. What the three measurements may not do

1. No status change, no hypothesis movement, no evidence record. Each is an
   executor artifact of observations.
2. **Claim tier TOY**, unconditionally. No number measured at `d <= 140` is
   transported to `beta = 606`, `d = 1420`, to any FIPS 203 parameter set, to any
   attack cost, or to any other parameter set, by extrapolation or by analogy.
3. No interpretation beyond the declared verdicts of §2.5, §3.2 and §4.4.
4. No "absent", "no departure", "vanishes", "consistent with zero" or any
   synonym applied to a measured arm, in any wording, without its floor. Frozen
   completion-gate item, and the scan must cover the report, the JSON and the
   script.
5. No editing of this document, no re-derivation of its thresholds, no
   substitution of a "better" grid, and no reaching for the withdrawn
   `SE_step_paired` tolerance. If a measurement believes a threshold here is
   wrong, it records the objection in its report **and runs the frozen
   specification anyway** — which is what BATCH-f19c37's executor did, correctly.
6. No post-hoc alternative rule computed and presented beside a frozen verdict.
   If one is computed for forward guidance it is labelled POST-HOC and stated to
   be uncitable as a result, exactly as AM-3 requires of the validator's own.
7. Budget exhaustion, timeout, crash, or a missing dependency is **never**
   negative mathematical evidence (`AGENTS.md` rule 3). It is reported as
   infrastructure and the affected cell is reported as not measured.
8. No AM-4 adjudicator claim. `V`, `E_I` and `D` are presentation-dependent
   (§1.1); no verdict in this batch is offered as an adjudication of a claim
   about a lattice.
9. Independence in this batch is **procedural** — separate sessions, no shared
   scratch, snapshot before review — and never model-level. Every report records
   it that way.

---

## 6. Provenance of every constant

| constant | value | class |
|---|---|---|
| `d` | `{100, 140}` | [carried] |
| `q` | `3329` | [carried] |
| error law / `mu_4` | CBD_{eta=2} / `2.5` | [carried] |
| draws per arm `n` | `8` | [carried] |
| error draws per cell `N` | `2^20` | [carried] |
| tail level / estimator | `2^-10`, `sort(R)[1023]` | [carried] |
| gate factor | `4.0 * SE_diff` | [carried] |
| AM-1 `t` grid | 13 values | [carried, RETAINED] |
| carried seed formulas | §1 | [carried] |
| `E[V]_haar` | `2 beta (d-beta)/(d(d+2))` | [closed form, exact] |
| **A**: `k` values | `{30,70}` at `d=100`; `{40,100}` at `d=140` | set here; `k != d/2`, mirrored pairs (§2.2) |
| **A**: `beta` grids | §2.2 | set here, from `{k, d-k}` alone [closed form] |
| **A**: `E_I^{M-K}` | `min(1, k/beta)` | [closed form] |
| **A**: `E_I^{M-D}` | `max(0, 1-(d-k)/beta)` | [closed form] |
| **A**: `V_c(beta)` two-regime | §2.1 | [closed form] |
| **A**: prediction tables | §2.3 | [closed form] |
| **A**: `beta = d/2` excluded from `V` | `M-K/M-D = 1.000` | [closed form] |
| **A**: `tol_E`, `tol_V` | `max(4*SE, 0.02)` / `max(4*SE, 2% of pred)` | `4.0` [carried]; absolute part set here at the order of measured instance dispersion |
| **A**: new seeds | `810000/910000/920000 + d*1000 + k*10 + i` | set here |
| **A**: committed anchors `9.3628 / 16.2446 / 6.7504 / 11.8075 / 16.269 / 0.83333 / 0.00000` | — | [quoted: `EV-MLKEM-94c773`; BATCH-436ddd red_team_report.md §2; red_team_report.md §3.1] |
| **B**: `epsilon_i` | `1.0 * SE_diff(t_i)` | set here, gate-commensurable (AM-3 repair (a)) |
| **B**: `alpha` | `0.002` | set here, from the `<= 0.10` family-wise requirement over 48 |
| **B**: `t_crit` | `t_{7,0.998} = 4.2071245566046755` | [closed form] |
| **B**: multiplicity family | `12 x 4 = 48` | [closed form from the grid] |
| **B**: declared family-wise rate | **`0.096`** (union bound); `0.0916233087376801` (Sidak, reference) | [closed form] |
| **B**: `P(t_7 > 1.0) = 0.175309`, withdrawn rule's `0.9902`, ratio `0.3599/0.4228` | — | [quoted: validation_report.yaml item 3; red_team_report.md §2.1] |
| **B**: positive-control `c` grid | `{1,2,3,4,6}`; INADMISSIBLE if no FAIL at `6` | set here |
| **C**: `V_TL(u)`, `m3_TL(u)`, inverse | §4.2 | [closed form] |
| **C**: reachable `V` intervals | table in §4.2 | [closed form] |
| **C**: V-match tolerance | `1e-9` absolute | set here |
| **C**: degeneracy exclusion | `|V - beta(1-beta/d)| <= 1e-9` | set here (§4.6 Form 2) |
| **C**: `n_C` | `12`, or `8` without fpylll | [closed form from §4.3] |
| **C**: `|t|` crit | `3.6358074219539622` / `3.3352949398170852` | [closed form, Bonferroni at family `0.10`] |
| **C**: relative-effect floor | `5%` | set here, at the order of the map's `1.0-1.7x` bias |
| **C**: informativeness | `|m3` diff`| > 10%` | set here (§4.6 Form 3) |
| **C**: `P(|t_7|>3.0) = 0.019942126131992522` | — | [closed form] |
| **C**: `m3_TL` cross-check `+0.980040 / -0.568440` | — | [quoted: red_team_report.md §4.2] |

Nothing in this table depends on a measurement that does not yet exist. The only
quantities computed at run time are those declared as such: `SE_diff`,
`SE_step`, `epsilon_i`, the measured `E_I`, `V`, `m3` and `D` per frame, the
achieved V-match residual, and the per-cell floors.

---

## 7. Notarization

* `prereg_sha256.txt` in this directory contains the sha256 of this file and
  nothing else.
* TASK-20260806-0a1072 snapshot-commits this directory in **one** commit
  containing exactly these two artifacts and its own receipt, **before**
  TASK-20260806-3084bc, -e17677 or -c973e6 is dispatched. No early durability
  commit is made for any producer, for any reason.
* Each measurement re-hashes this file, compares against the notarized receipt,
  **aborts on mismatch**, quotes the digest in its report, and asserts
  `git merge-base --is-ancestor <notarizing commit> HEAD` against the notarizing
  commit itself and not its parent.
* A mismatch is a harness failure, not a result, and the run does not proceed.
* Whether this ordering closes the notarization gap for this batch is for the
  validator (TASK-20260806-7418bc) to judge against the git record, not for this
  document to assert.

**Declaration, on the record: no lattice was generated or reduced, no basis was
built, no frame was computed, no draw was sampled, and no `V`, `E_I`, `D`,
quantile or arm statistic was evaluated in the production of this document.**
