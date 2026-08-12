# EXP-YIELD-001 v2 amendment — independent re-derivation and traced outcome cases

Task: `TASK-20260729-011`. Goal: `GOAL-ECDLP-001`. Batch: `BATCH-011`.
Verdict: **PASS**, with four pre-execution conditions. Companion file:
`amendment_review.yaml`.

**What this file is.** Every number the amendment asserts that I could check, and
every outcome case the card mandates, re-derived in this session from the
contract's own definitions. Not copied from the amendment, not copied from
`TASK-20260729-003`. Where my value differs from either, the difference is
stated.

**Compute status.** ZERO CURVE COMPUTE. No census, no elliptic-curve arithmetic,
no driver, no summation polynomial. Bash was read-only: git queries and file
reads. The deterministic integer and floating-point evaluations below were run in
a scratch directory **outside the repository**; they are **UNARCHIVED AND NOT
EVIDENCE**, and every one of them is reproducible on paper from the formulas
shown. **No stochastic probe was run, and no conclusion in either artifact rests
on one.** That distinction is deliberate: an earlier session in this program
drove a decision from an unarchived probe that then failed to reproduce, and this
review is written so that a reader who distrusts my arithmetic can redo it by
hand rather than having to trust an unrepeatable run.

---

## 0. What was verified against Git before any arithmetic

| check | result |
|---|---|
| `59f2e930ab60` reachable from `HEAD` (`e7fdadd1`) | yes, ancestor |
| first parent | `b00efa320b87…` — matches receipt |
| changed paths | **2**: `v1_to_v2.yaml` (added), `dispatch_queue.json` (modified) |
| declared source paths in the archive | **1** |
| `sha256` of both committed blobs | match the receipt exactly |
| worktree files vs committed blobs | byte-identical |
| `specification.yaml` blob at `82327a02` / `b00efa32` / `59f2e930` / `HEAD` / worktree | `586914984c4c…` at **all five** |
| `H-YIELD-001.yaml` blob at `b00efa32` / `59f2e930` / `HEAD` | `c136df499ed8` — unchanged |
| `criterion_feasibility_table.md` at `82327a02` … `HEAD` | `8e0eb377d55a` — unchanged |
| `TASK-20260729-003/contract_review.yaml` at `b00efa32` … `HEAD` | `9a174ac4b82a` — unchanged |
| `ledger/evidence/EV-ECDLP-008*`, `ledger/decisions/DEC-20260729-*` | absent — reserved and unwritten |
| `H-YIELD-001` status | `specified` — unmoved |

**Ruling on the overrun.** The archive is correctly rejectable *and* it still
binds my inputs. I did not take that from the receipt; I checked it. The single
undeclared path is the dispatch queue carrying `QUEUE-AMEND-20260729-001`, whose
diff I read: append-only, four new cards, two commit-set declarations, and a
rewiring of `TASK-20260729-005` to depend on `-011` and `-013`. **It touches no
input to this review.** Combined with the four immutable blobs verified unchanged
across the amendment commit, the evidential binding I actually rely on — blob
hash, reachability, declared parent — is intact independently of the archive's
declaration. Full reasoning in `amendment_review.yaml`
§`snapshot_integrity.ruling_on_the_disclosed_overrun`, including one defect the
receipt does not disclose: its `declared_set.total: 2` counts a path that lives
in a *different* commit.

---

## 1. RT-1 — recount from the predicate

Predicate as frozen: `h = B^m/(m! p) <= 0.5` **AND** `C_red(B) >= 500`, over all
136 cells, with `L = round(p^beta)` and the illustrative basis `B = L`.

```
C_red(m=2) = B^2/2
C_red(m=3) = B + B(B-2) + B(B-2)(B-4)/6
```

I checked that closed form against the contract's own series
`C_red = sum_{k=1..m} C(B/2,k) C(m-1,k-1) 2^k` (generalised binomial for
half-integer `B/2`) at `B = 15, 21, 22, 23, 31, 34, 42, 79`. **They agree
exactly at every one.**

**Count: 27 at m = 2, 17 at m = 3, total 44.** Obtained twice — once with
`p = 2^k` (the feasibility table's stated basis) and once with `p =` the smallest
prime at or above `2^k` (`4099, 16411, 65537, 262147`). **The count is 44 under
both**, so it is not an artifact of the table's approximation.

My enumeration, which is **identical to the amendment's `corrected_enumeration`
at every one of the 44 entries including every `B`**:

```
m = 2  (27)
  k=12  0.425[34] 0.450[42] 0.475[52] 0.500[64]
  k=14  0.375[38] 0.400[49] 0.425[62] 0.450[79] 0.475[100] 0.500[128]
  k=16  0.325[37] 0.350[49] 0.375[64] 0.400[84] 0.425[111] 0.450[147]
        0.475[194] 0.500[256]
  k=18  0.300[42] 0.325[58] 0.350[79] 0.375[108] 0.400[147] 0.425[201]
        0.450[274] 0.475[375] 0.500[512]
m = 3  (17)
  k=12  0.325[15] 0.350[18] 0.375[23]   <- 0.375 is the cell v1 omits
  k=14  0.300[18] 0.325[23] 0.350[30]
  k=16  0.250[16] 0.275[21] 0.300[28] 0.325[37] 0.350[49]
  k=18  0.225[17] 0.250[23] 0.275[31] 0.300[42] 0.325[58] 0.350[79]
```

The omitted cell, arithmetic shown: `B = 23`, `h = 23^3/(6·4096) = 12167/24576 =
0.495085 <= 0.5`; `C_red = 23 + 23·21 + 23·21·19/6 = 23 + 483 + 1529.5 = 2035.5
>= 500`. **Inside the predicate on both clauses.**

**Nine evaluable columns, confirmed**, and the split C-12 asserts is confirmed
with it: six carry four sizes, three carry three — `m=2 beta 0.375`,
`m=2 beta 0.400`, `m=3 beta 0.300`. Those three are the 1-df columns.

**Cause of the v1 undercount, confirmed.** The `h <= 0.5` band at `m = 3` is
`beta <= 0.3774 / 0.3711 / 0.3664 / 0.3627` at `k = 12/14/16/18`. The v1 table
applied the *tightest* (0.3627, the `k = 18` value) as a global cut and stopped
its `m = 3` section at `beta = 0.350`. The predicate is per size, and at `k = 12`
the band reaches 0.3774, which admits `beta = 0.375`.

**Robustness the amendment did not check.** Under a *realisable* basis with `B`
forced even (see §2):

| basis | m=2 | m=3 | total | max `E_max` | cells with `E_max < 1.10` |
|---|---|---|---|---|---|
| `B = L` | 27 | 17 | **44** | 1.4215 at (3, 12, 0.375, B=23) | 17 |
| `B` = nearest even `<= L` | 27 | 16 | 43 | 1.3871 at (3, 12, 0.375, B=22) | 17 |
| `B` = nearest even `>= L` | 28 | 16 | 44 | — | — |

The correction survives parity: the recovered cell still carries the design's
largest counting ceiling under either basis.

**RT-1: REPAIRED.**

---

## 2. RT-2 — the parity argument

**The argument holds.** `F = {P : x(P) ∈ I}`. `N` is prime and, being a group
order near `p >= 4099`, odd. A point with `y = 0` has order 2, which an odd `N`
forbids. The identity has no `x`-coordinate, so it is never in `F`. Therefore
every `x ∈ I` admitting a point contributes exactly two points `(x, y)` and
`(x, -y)`, and

```
B = 2 · #{x ∈ I : x admits a point}   ⇒   B is EVEN.
```

Consequences, all verified:

- `B = 15, 21, 23, 31, 79` are **unattainable as measured counts**.
- The half-integer `C_red` values that follow — `567.5, 1550.5, 2035.5, 4975.5,
  82199.5` — **correspond to no realisable configuration**. I reproduced all
  five from both the closed form and the series.
- More strongly: the closed form is *derived from* `C(B/2, k)`, which
  presupposes `B` even. At odd `B` the enumeration's own formula is not merely
  improbable, it is **undefined**.

So the `B = L` enumeration can only ever have been illustrative, and **RT-2 is
settled structurally**, exactly as the card anticipated. `R-1` makes the
measured-`B` predicate the sole authority and `R-2` freezes each cell's class
from measured `B` *before* `S_m` exists, so the class can never be a function of
an outcome.

**One correction to the amendment's provenance.** The parity fact is **not** this
session's or the amendment session's discovery. The **frozen v1 specification
already states it**, in `inputs.curve_selection_rule`:

> "Prime `N` … guarantees no point of order 2 (so the factor base is closed under
> negation and `B` is even)"

That makes v1 **self-contradictory** — declaring `B` even in one block and
enumerating the evaluable set on odd `B` in another — which is a *stronger* case
for the repair than the one the amendment makes.

**RT-2: REPAIRED.** New objection RT-14 attaches (§7).

---

## 3. RT-4 — the antipodal null, re-derived

**Fixed-point-freeness.** `F` is closed under negation and `N` is odd, so
`S_m = -S_m`. On cancellation-free multisets, `M ↦ -M` has no fixed point: a
fixed point needs the induced permutation to pair each `P` with `-P` (a
cancelling pair, excluded), and any unpaired element would need `-P = P`,
impossible with `N` odd and the identity absent from `F`. So the `C_red`
multisets pair into exactly `C_red/2` antipodal pairs.

`C_red` is **even** at every cell, because every term of
`Σ_k C(B/2,k) C(m-1,k-1) 2^k` carries a factor `2^k` with `k >= 1`.

**Mean.** `C_red/2` pairs into `M = (N-1)/2` bin-pairs, `λ = (C_red/2)/M =
C_red/(N-1)`, expected distinct count `(N-1)(1 - e^{-λ})`. Against `P_pred =
N(1 - e^{-C_red/N}) + |S_{m-2}| e^{-…}` the difference is `O(1)` — at `λ = 0.5`
it is about 0.09 against a `P_pred` of 540 to 131 000. **`P_pred` needs no change
and no criterion threshold moves.**

**Variance — the factor of 2, derived independently.** With `X` the number of
occupied bin-pairs,

```
Var(X)      = M e^{-λ} (1 - (1+λ) e^{-λ})
distinct    = 2X
Var(2X)     = 4 Var(X) = 2 (N-1) e^{-λ} (1 - (1+λ) e^{-λ})
independent = N e^{-λ} (1 - (1+λ) e^{-λ})
ratio       = 2(N-1)/N
```

| `k` | 12 | 14 | 16 | 18 |
|---|---|---|---|---|
| ratio | 1.99951 | 1.99988 | 1.99997 | 1.99999 |

So the relative sd is multiplied by `sqrt(2) = 1.41421`. **The amendment writes
"EXACTLY TWICE"; it is twice to within `1/N`.** Inside the `O(1)` slack the
amendment declares elsewhere, and immaterial — recorded for accuracy only.

**Restated sigma figures — all three reproduce.** Design-wide maximum chance
relative sd over the 44 cells, under the v1 independent-throw process:

| cell | `C_red` | `λ` | `P_pred` | sd | rel sd (v1) | rel sd (antipodal) |
|---|---|---|---|---|---|---|
| m=2, k=12, β=0.425, B=34 | 578 | 0.141113 | 539.9 | 5.677 | **1.0518 %** | **1.4875 %** |
| m=3, k=12, β=0.325, B=15 | 567.5 | 0.138550 | 543.2 | 5.603 | 1.0291 % | 1.4553 % |
| m=2, k=12, β=0.450, B=42 | 882 | — | — | — | 1.0260 % | 1.4509 % |

The amendment says 1.0515 % / `P_pred` 539.8 / sd 5.676 — agreement to the fourth
digit, and the cell it names is right.

```
±10 % band       = 0.10 / 0.014875 = 6.72 σ   (amendment: 6.7)
F1's 0.80        = 0.20 / 0.014875 = 13.45 σ  (amendment: 13.4)
```

**No evaluable cell exceeds the 2 % NOISE-LIMITED rule on chance sd alone**
(largest 1.4875 %), so the disclosed 1.34× margin is right and C-14's raised
replicate counts are a proportionate response rather than a threshold move.

**The unarchived probe was correctly excluded**, and better than excluded: it is
replaced by a *declared contrast arm* that runs the v1 process alongside the
antipodal one at the same cells and counts, so the `sqrt(2)` is **measured inside
the driver and archived**. That converts an unarchived probe into a
pre-registered archived control and is the single best change in this amendment.

**One `O(1)` mismatch this session found (RT-15).** The antipodal null partitions
the `N-1` *non-identity* elements into `(N-1)/2` bin-pairs, which asserts no ball
lands on the identity. But a cancellation-free multiset **can** sum to the
identity — the contract reports that count as a secondary metric at both arities
and states the identity is in `S_m` for even `m` — and such a multiset and its
antipode both land on the identity, covering **one** bin, not two. Expected count
`≈ C_red/N <= 0.5` anywhere in the evaluable set. `O(1)`, **no threshold moves**,
recorded because RT-4's whole lesson was that an unstated shape mismatch silently
corrupted a denominator, and this is a second one two orders of magnitude
smaller.

**RT-4: REPAIRED.**

---

## 4. RT-6 / C-6 — `E_max`, one-sidedness, Cauchy–Davenport

`E_max = min(C_all, N)/P_pred`, recomputed cell by cell at all 44:

| quantity | this session | amendment |
|---|---|---|
| minimum `E_max` | **1.0184** at m=2, k=18, β=0.350, B=79 (`C_all = 3160`, `P_pred = 3103.0`) | 1.0184, same cell, same inputs |
| maximum `E_max` | **1.4215** at m=3, k=12, β=0.375, B=23 (`C_all = 2300`, `P_pred = 1618.1`) | 1.4214, same cell, same inputs |
| cells with `E_max < 1.10` | **17 of 44 (38.6 %)** | 17 |
| breakdown | m=2: 3 at k=14, 6 at k=16, 7 at k=18, 0 at k=12 (=16); m=3: exactly one, (k=18, β=0.300), `E_max = 1.09318` | identical, `1.0932` |

**The cell v1 dropped carries the design's maximum `E_max`. Confirmed by
recomputation, not by reading the prior review's range.**

**Cauchy–Davenport floor.** `N` prime ⇒ `G ≅ Z/NZ` ⇒ `|A+B| >= min(N, |A|+|B|-1)`,
iterating to `|S_m| >= min(N, mB - m + 1)`. `S_m` *is* the `m`-fold sumset (the
contract permits repetition), so the application is valid. Largest floor over the
44 cells:

```
m=2, k=12, β=0.425, B=34:  (2·34 - 1)/539.8 = 67/539.8 = 0.1241   ← largest
m=2, k=16, β=0.325, B=37:                                0.1070
m=2, k=14, β=0.375, B=38:                                0.1060
```

**0.1241 is the maximum**, and F1's 0.80 sits far above every floor, so F1
survives **on a rigorous bound** rather than on v1's assertion that "nothing in
the design bounds `E` from below". Adding the violation to INV-1 is a
strengthening, not a relaxation.

---

## 5. RT-3 — the outcome disposition table, traced

Branch conditions evaluated **mechanically as written**, in the given order,
first-match-governs. Column classes from OLS of `log E` on `log p` with
`t(0.975, 1) = 12.706` and `t(0.975, 2) = 4.3027`.

### 5.1 The cases the card mandates

| # | case | column classes | `OUT` | **branch** |
|---|---|---|---|---|
| 1 | uniform `E ≈ 0.85`, no p-trend | all FLAT (slope 0, zero residual, CI ∋ 0) | all 44, consistent low | **O-4** |
| 2a | one UNDERPOWERED column, `OUT` empty | 1 UNDERPOWERED, rest FLAT | 0 | **O-9** |
| 2b | same, 3 cells out of band | as above | 3 | **O-6** |
| 3 | two columns, significant slopes of opposite sign, both monotone | 1 DOWN-SIG (−0.0760), 1 UP-SIG (+0.0760) | 8 | **O-8** |
| 4 | three out-of-band cells, no trend | all FLAT | 3 | **O-6** |
| 5 | `E` rising with p from below (0.70/0.80/0.90/1.00) | 1 UP-SIG, slope +0.0857, CI (0.072, 0.100) | 4 | **O-7** |

**No case fired nothing. No case fired two branches.** Case 1 is the RT-3 worked
case and it lands on **O-4**, exactly as the amendment claims.

**Was a threshold moved to make case 1 land on O-4?** No. I compared every
threshold against v1: band `[0.90, 1.10]` unchanged; "more than one third"
unchanged; F1's 0.80 and −0.05 unchanged; S1's 0.05 unchanged; NOISE-LIMITED 2 %
unchanged. **The only change that makes case 1 land on O-4 is the deletion of
"and no consistent sign" — which is precisely the repair RT-3 required.**

One content change *is* present and is **disclosed accurately** in
`changed_criteria_before_and_after.F2`: `"no monotone trend in p"` becomes
`"no evaluable column is DOWN-SIGNIFICANT or UP-SIGNIFICANT"`. These are
different conditions — a column can be monotone without being significant — so
C-3's summary sentence ("what changes is coverage") understates it. The change is
justified: v1's clause is not machine-checkable at three or four points.

### 5.2 Three adversarial cases constructed in this session

**Route A — the one that matters.** A DOWN-SIGNIFICANT column with `E <= 0.80` at
its largest size, whose deviation does **not** shrink under `CTRL-NULL-FB`:

```
E = 1.00, 0.92, 0.85, 0.78 at k = 12/14/16/18
slope −0.05953,  95 % interval (−0.06224, −0.05674)  ⇒ excludes zero
non-increasing: yes.  E at largest size: 0.78 <= 0.80.  ⇒ DOWN-SIGNIFICANT.

O-2 : requires the deviation to SHRINK under CTRL-NULL-FB          → FAILS
O-3 : requires that NO DOWN-SIG column has E <= 0.80; one does     → FAILS
O-7 : requires an UP-SIG column                                    → FAILS
O-1 : requires OUT empty AND every column FLAT                     → FAILS
O-4/O-5/O-6 : all require NO DOWN-SIG or UP-SIG column             → FAIL
                                                                   ⇒ O-9
(identical case with the deviation shrinking                       ⇒ O-2)
```

**Flipping one control's result moves the design's strongest negative signal from
a named verdict to the branch that declares itself a completeness defect.** O-3's
*disposition* text already contemplates the non-shrinking case ("If the trend
does NOT shrink under CTRL-NULL-FB, INV-5 governs the reading"), so the intent
was there and the **condition** was mis-drafted by one clause. The narrow fix
would have been `"at least one column is DOWN-SIGNIFICANT and O-2 does not
apply"`.

**Route B — the column taxonomy's completeness claim is false.** The definitions
block asserts the only unnamed case is UNDERPOWERED (`|slope| > 0.05` with the
interval containing zero). There are at least two others:

- `|slope| <= 0.05` with the interval **excluding** zero — not DOWN/UP-SIG
  (magnitude too small), not FLAT (interval excludes zero), not UNDERPOWERED.
  Traced: slope `−0.01747`, CI `(−0.01752, −0.01742)`, `OUT` empty ⇒ **O-9**.
  This is a *small but well-determined* trend, a thoroughly plausible product of
  a real finite-size correction, and S1 correctly fails on it.
- a significant slope of magnitude `>= 0.05` on a **non-monotone** `E` sequence —
  excluded from DOWN/UP-SIG by the monotonicity clause and from UNDERPOWERED by
  the interval clause.

The branch table still catches both through O-9. The **taxonomy** does not, and
the taxonomy's stated completeness is what a reader relies on.

**Route C — multiplicity, with the arithmetic.** S1 and O-1 require **all nine**
evaluable columns to carry a 95 % interval containing zero, with **no
multiple-comparison correction anywhere**:

```
0.95^9 = 0.6302      P(at least one column's interval excludes zero) = 0.3698
```

If `OUT` is empty — the modal success-adjacent outcome — one such column takes
the run out of O-1 and, being neither FLAT nor significant, into O-9. So **of
order one run in three lands in the self-declared-defect branch by multiplicity
alone, with nothing wrong at all.** This is a **pre-existing defect of v1's S1**
that the prior review did not catch and the amendment did not introduce; the
amendment merely makes its consequence visible.

*Stated as an order-of-magnitude design estimate conditional on iid-like
residuals — a condition this design nowhere establishes, and one especially
doubtful at 1 and 2 residual degrees of freedom, where t-interval coverage is
very sensitive to non-normality. It is not a measurement.*

### 5.3 Ruling

**Formally the table is exhaustive and mutually exclusive.** O-9's condition is
"any realised pattern not matched above", so nothing fires nothing;
first-match-governs means nothing fires two branches. I could not construct a
counterexample to either property and I tried. **My objection is that O-9 is not
a remote residual** — it is reachable by three distinct routes, one of them the
design's strongest negative signal and one of them at probability of order one
third under the null. That is a coverage *weakness*, not a coverage *hole*.

**RT-3: PARTIALLY REPAIRED.** Pre-data readings for all three routes are fixed in
`PC-4` so that reaching O-9 is never resolved by judgement after the numbers are
seen.

---

## 6. C-12's 1-df caveat, re-derived

`E = 1.00 / 0.90 / 0.80` at `k = 14/16/18`, `x = k·ln 2`:

| quantity | this session | amendment |
|---|---|---|
| slope | **−0.080482** | −0.080481 |
| residual s | **0.0050715** | 0.0050713 |
| SE(slope) | **0.0025868** | 0.0025867 |
| half-width (`t = 12.706`) | **0.032868** | 0.032867 |
| 95 % interval | **(−0.1133, −0.0476)** | (−0.1134, −0.0476) |
| margin | **2.45×** | 2.45× |

Reproduced to five or six digits. The reading note is correct: **the
interval-excludes-zero clause, not the 0.80 threshold, is F1's binding
constraint**, and the 13.4 σ figure describes the *per-cell chance fluctuation*
of `E`, not the power of the slope clause. The three 1-df columns are `m=2` at
β = 0.375 and 0.400 and `m=3` at β = 0.300 — confirmed by my own column count.

---

## 7. RT-14 — eleven knife-edge cells, not two

Evaluating the frozen predicate at the nearest **even** `B` below and above `L`
(even because the contract's own curve rule forces it), at all 136 cells:

| cell | `L` | `C_red` at `B=L−1` (even) → `B=L+1` (even) | direction |
|---|---|---|---|
| m=2 k=12 β=0.500 | 64 | 1922 → 2178 | can **leave** |
| m=2 k=14 β=0.350 | 30 | 392 → 512 | can **enter** |
| m=2 k=14 β=0.500 | 128 | 7938 → 8450 | can **leave** |
| m=2 k=16 β=0.500 | 256 | 32258 → 33282 | can **leave** |
| m=2 k=18 β=0.275 | 31 | 450 → 512 | can **enter** |
| m=2 k=18 β=0.500 | 512 | 130050 → 132098 | can **leave** |
| m=3 k=12 β=0.325 | 15 | 462 → 688 | can **leave** |
| m=3 k=12 β=0.375 | 23 | 1782 → 2312 | can **leave** |
| m=3 k=14 β=0.275 | 14 | 292 → 688 | can **enter** |
| m=3 k=14 β=0.375 | 38 | 7788 → 10680 | can **enter** |
| m=3 k=16 β=0.250 | 16 | 462 → 978 | can **enter** |

`R-4` names **two** of these. The sharper consequence, nowhere disclosed: at
`m = 2, β = 0.500` the predicate `h <= 0.5` reduces to `B <= sqrt(p)`, while
`B ≈ L = round(p^0.5)`, so **every one of that column's four sizes is a coin
flip**. Under an independent 50/50-per-cell model,

```
P(at least 3 of 4 sizes survive) = C(4,3)·0.5^4 + 0.5^4 = 5/16 = 0.31
```

so the design's densest 4-size column is **more likely than not** to fall below
three sizes and be dropped under `R-6`, taking nine evaluable columns to eight.
*Model estimate, not a measurement.*

**Not blocking**, because the *handling* is complete even though the *disclosure*
is not: `R-5` routes any other class change through the same rule, `R-3` records
the flag, `R-6` uses realised denominators and explicitly contemplates a column
dropping with its reason recorded, and `R-7`'s four-cell drift threshold is wide
enough for a parity-driven shift of one or two. Nothing requires the Executor to
guess, and no criterion is evaluated at a cell whose measured `h` exceeds 0.5.
`PC-2` records it pre-data.

---

## 8. RT-9 and the three recorded disagreements

| item | contract / prior review | this session | ruling |
|---|---|---|---|
| `β*(3)` | 0.4051 / **0.3982** / **0.3930** / **0.3892** | 0.405138 / **0.394880** / **0.387187** / **0.381203** | amendment right, contract wrong at three of four |
| `L(k=12, β=0.225)` | 7 | `2^2.7 = 6.49802` → **6** | amendment right |
| `p/N` exact Hasse supremum `p/(p+1−2√p)` | 1.03125 / 1.015625 / 1.007812 / 1.003906 (linearised) | **1.031998 / 1.015810 / 1.007859 / 1.003918** | amendment right at **all four** |
| `C_red(m=3, β=0.275)` | 1542 (k=16), 5424 (k=18) | **1550.5** (B=21), **4975.5** (B=31) | amendment right; verified two ways |
| design-wide ceiling | 1.733 | `1.68 × 4096/3969 = 1.68 × 1.0319979 =` **1.73376 → 1.7338** | amendment right |
| degenerate ceilings | — | 3.096 (m=3,B=2), 2.293 (m=3,B=3), 2.064 (m=2,B=1); over the evaluable set 1.2476 (m=3,B=15), 1.0624 (m=2,B=34) | confirmed |

### Disagreement 1 — `β*(2)` at `k = 16`

```
β*(2) = (1 + log_p 2)/2 = (1 + 1/16)/2 = 0.53125   EXACTLY
```

The contract prints **0.5313** (round-half-away-from-zero). The prior review's
`feasibility_check.md` line 152 tabulates **0.5312** (round-half-to-even). Both
render the same exact number; **neither is a defect in the contract**.
**AMENDMENT UPHELD.** Its account of the review is also accurate: the review's
*prose* calls the `m = 2` row "exactly right" while its *table* prints a
different fourth digit, so the inconsistency is internal to the review.

### Disagreement 2 — two missed `C_red` entries

Verified two ways (closed form and `C(B/2,k)` series): **1550.5** at `B = 21` and
**4975.5** at `B = 31`, against the table's 1542 and 5424. These are genuine
errors, not roundings — contrast the table's 568 for 567.5 and 2036 for 2035.5,
which *are* roundings. The amendment's explanation is fair: the prior review
states at its line 462 that it verified `C_red` "against `C_all` by an
independent identity at m=2 (`C_all − C_red = B/2`)", which is a check of the
**identity** and not of every entry. I confirm that identity independently
(`C_all = B(B+1)/2`, `C_red = B²/2`, difference `B/2`). Neither correction changes
any cell's class, so **44 stands**. **AMENDMENT UPHELD.**

### Disagreement 3 — the `p/N` correction at all four sizes

The mathematics is on the amendment's side: the linearisation understates at
**every** size, not only `k = 12`. **UPHELD ON THE ARITHMETIC**, with a fairness
correction in *each* direction:

- *Against the amendment's account of the review*: the prior review **did** say,
  at its line 75, that "the same linearisation understates all four `p/N`
  bounds"; it merely declined to tabulate the other three. "The review corrects
  only the k = 12 bound" is true of the *correction* and misleading about the
  *finding*.
- *Against the amendment's own qualifier*: "only the `k = 12` correction is
  numerically visible in any downstream figure" is itself slightly wrong at the
  two-decimal display the contract uses, where `k = 14` moves 1.56 → **1.58** and
  `k = 16` moves 0.78 → **0.79**.

Nothing here is load-bearing and no threshold moves. Recorded at this length only
because a re-review that rubber-stamps a producer's disagreements with its
predecessor is worthless, and **two of these three needed correcting in both
directions**.

---

## 9. Budget, re-derived per arm

| arm | v1 | v2 | note |
|---|---|---|---|
| census, 44 evaluable cells | — | **1.33 × 10⁶** modular adds | largest single evaluable cell 2.6 × 10⁵ |
| the 44th cell alone | — | **6.6 × 10³** | negligible |
| occupancy MC (antipodal arm only) | 1.69 × 10⁷ draws | 2.27 × 10⁷ | C-14 replicate bands |
| occupancy MC **+ declared v1 contrast arm** | 1.69 × 10⁷ | **4.54 × 10⁷** | the arm the amendment never prices |
| `CTRL-NULL-FB` | 3.98 × 10⁶ | **6.35 × 10⁶** | 10 draws at `B <= 64` |
| `CTRL-CALIB-AP` | 36 seed-cells | **72** | fields of at most 4099 elements |
| **total added by v2** | — | **≈ 3.1 × 10⁷** | amendment claims "well under 10⁷" |

**RT-16: the amendment understates its own added compute by about 3×**, because
the C-4 contrast arm doubles the occupancy Monte Carlo and is never costed.
**The budget verdict is unaffected and I confirm it**: 3.1 × 10⁷ sits against a
design whose observation-only priority-3 tier already carries ≈ 1.4 × 10⁹ and a
criterion-evaluable core of ≈ 1.3 × 10⁶, inside 5400 s and 8 GB with orders of
magnitude to spare. Memory is unmoved — one 32 KB `N`-bit set plus the `k = 18`
DL table, well under 1 GB. **No budget field needs to move and no reduced-scope
core is triggered by the amendment.**

*Harmless convention difference*: my census total is 1.33 × 10⁶ against the
amendment's 9.32 × 10⁵ because the amendment charges `B²/2` at `m = 2` where the
feasibility table's own cost model charges `|S_1|·B = B²`.

---

## 10. RT-13 — the correction that did not reach the record

C-7's consequence block states the correction of the `TASK-20260729-002` receipt
language "is carried forward as a CORRECTION NOTE in the `TASK-20260729-012`
snapshot receipt, which is the next archive record in this lineage."

**It is not there.** Searching the committed `TASK-20260729-012` receipt for
`exponent`, `correction`, `REMOVED-1` and `coverage` returns **zero** matches.
Meanwhile the `TASK-20260729-002` receipt still carries, at its line 47:

> "That was the one event that would have reopened a sub-1/2 exponent; it is
> closed by counting, not measurement."

So the over-claim **stands uncorrected in the committed archive chain**, and the
amendment's own chosen supersession mechanism did not execute. This is the single
most consequential scope defect in the package, because that sentence is exactly
the kind downstream records quote.

**Not blocking**, because the defective record is an *archive receipt*, not the
protocol, and the correction can ride the `TASK-20260729-013` receipt — the next
archive record in the lineage, not yet written. `PC-3`.

**On the merits, C-7's replacement narration is CONFIRMED on every clause.**
`h = B^m/(m! p)` is a first-moment estimate of representations per target, and
`|S_m| <= C(B+m−1, m)` is precisely *"the probability of at least one
representation is at most the expected number of them"* — **Markov's inequality
applied to a first moment**. There is no content in it beyond that. It bounds
**coverage**, not **multiplicity**; index calculus operates in the saturated band
where coverage is 1 by definition and the priced quantity is relations harvested
per unit work, which this argument does not bound above at all. **It closes no
exponent question.** What it *does* establish — that
`IDEA-20260727-006`'s falsification condition 1 was malformed at birth, because
it asked whether `P(X >= 1) > 2·E[X]` — is a genuine and valuable pre-freeze
catch about a **criterion**, not an answer about an **exponent**.

**The A1 admission survives verbatim and intact**: moves no exponent,
exponent-*deciding* screen and expressly not exponent-*targeting* under rule A1,
no downstream record may quote it as target-class, claim tier capped at **toy**,
meets no `GOAL-ECDLP-001` completion criterion under any outcome, changes no
hypothesis status, leaves all four promotion gates open, and infrastructure
failure is never negative evidence. Every branch of the outcome table complies:
the best available label is `support` at no more than `preliminary` with a named
replication, and `reject_scoped` is forbidden under every branch.

---

## 11. Executability

**Yes, with one named exception.** `R-1` gives a single mechanical definition of
the evaluable set on measured `B`; `R-2` fixes the order of operations; `R-3`
fixes what is recorded per cell; C-4 gives a one-line null process plus its
contrast arm; C-14 gives replicate counts by `C_red` band; C-13 gives draw counts
by measured `B`; C-8 gives seed counts, a pre-registered estimator form and which
`B` to freeze. The six run identifiers, six master seeds and twenty declared
artifact paths are unchanged.

**The exception is INV-2a (RT-12).** C-8 was offered *either* routing the AP leg
through the shared routine *or* downgrading INV-2 so it cannot void. It did
**both**, leaving the half that keeps the teeth without a firing predicate:
"the shared distinct-count and membership routine fails its own known-answer
test" — the test is never defined and its pass criterion is never stated. The
only quantitative comparison the leg makes is against `EV-STR-001`'s medians, and
that is INV-2b, which explicitly cannot void. So INV-2a is either unfireable (and
S1's amended calibration clause is trivially satisfied) or fireable only on a
predicate the Executor must invent, which ST-3 forbids. **`PC-1` records the
narrow reading** — INV-2a fires iff the shared routine disagrees with an
independently computed exact value on a known-answer input, structurally the same
rule as `CTRL-DL`. The census does not depend on it: `CTRL-DL` and INV-3 are
unchanged and remain the control that actually stands behind the census.

**AP admissibility predicate — RESOLVABLE, ST-3 should not fire.** Checked
directly against the committed `EXP-STR-001` specification, not taken from either
prior session: factor base at line 19 (`x`-interval, first `B` liftable `x >= 0`,
canonical `y = min(y, p−y)`, ordered by `x`); support shape at line 9
(`{x, x+d, …, x+(m−1)d}`, `d ∈ D`); shift set at line 16 (integers 1..64);
exclusion of the degenerate `d = 0` frozen in the contract at lines 27–28;
`ap_supply` at line 48 (number of **distinct** AP support tuples);
`yield_penalty = C(B,m)/ap_supply` at line 53. Canonical `y` means one point per
`x`; `D` positive-only means each support is counted once. **Every degree of
freedom the leg needs is fixed.**

**`CTRL-CALIB-AP` false-invalidation risk — DISCHARGED, belt and braces.** The
risk was real: `EV-STR-001` line 29 records *"m=4 at p=211: supply < B in 6/6
seeds (as low as 3 tuples)"*, and the leg draws fresh curves, so a fresh median of
3 gives `C(15,4)/3 = 455`, i.e. 2.1× the 214.9 target and outside the window,
with INV-2 tolerating only one failing cell. Both closures are independently
sufficient: 24 seeds at the two `n = 211` cells makes a median of 3 from a
median-8 distribution far rarer, and the INV-2 split means even two misses give
an instrument note rather than a void census. Pre-registering the ratio of
medians removes the remaining discretion. `B` disclosure verified:
`C(64,4)/154 = 4126.5` and `C(65,4)/154 = 4396.4` against `EV-STR-001`'s 4128.6;
`C(64,3)/477 = 87.35` and `C(65,3)/477 = 91.57` against its 87.8 — so that record
used `B = 64` while the leg freezes `ceil(sqrt(4099)) = 65`, and the resulting
1.04 and 1.06 ratios sit far inside the factor-2 window.

---

## 12. What this note does not establish

- It is **arithmetic on a design**, not a measurement. No curve was chosen, no
  run exists, and nothing here is evidence for or against any hypothesis.
- The re-derivations ran **outside the repository, are unarchived, and are not
  evidence**. Every one is reproducible on paper from the formulas shown.
- The 0.37 multiplicity figure (§5.2 Route C) and the 0.31 column-survival figure
  (§7) are **model estimates conditional on stated independence assumptions**,
  not measurements, and nothing in the verdict turns on their exact values.
- **Model independence is not available and is not claimed** (`INT-BATCH011-D`):
  the adapter refuses `review-adversarial` on the `zai` backends because the
  policy requires `xhigh` and the binding ceiling is `high`, and `ZAI_API_KEY` is
  unset. This is one independently-resolved **session**, not one
  independently-resolved **model**. **No closure quorum is claimed or claimable.**
- `tools/validate_ledger.py` was not run (`INT-BATCH011-F` records it exits
  nonzero and the amendment repairs nothing there); `tools/allocate_id.py` was
  not run; no external source was retrieved to check the RT-11 positioning
  statement.
- **Nothing here is a cryptanalytic result**, nothing here bears on
  cryptographic-size curves in either direction, and **no direction is declared
  impossible** by anything in this review. Absence of evidence is not
  impossibility.
