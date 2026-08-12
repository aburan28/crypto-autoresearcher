# TASK-20260729-003 — independently re-derived feasibility arithmetic

Reviewer session: fresh, non-originating. Reviewing the committed blobs at
`82327a02bb3041af70566a3f8edfb4468dd2d52d` only. Nothing was executed on a
curve. All arithmetic below was recomputed in this session from the definitions
in the committed contract, not quoted from the producer's table.

---

## 0. Snapshot verification (performed, not assumed)

| check | result |
|---|---|
| commit reachable from `HEAD` (`4fa44557`) | YES (`git merge-base --is-ancestor`) |
| first parent | `93d961e012d4db59641933a90ce03587e2ba189e` — matches receipt |
| changed-path set | exactly 3 paths, all `A` (added), matches receipt `committed_paths` |
| SHA-256 of each committed blob | matches receipt `path_sha256` for all three |
| SHA-256 of worktree copy vs blob | identical for all three (no working-tree drift) |

Not verified: whether `tools/allocate_id.py --check` was in fact run before the
commit (the receipt asserts it; the contract's own `id_check` block says the
authoring session could not run it). Untested claim, recorded as such.

---

## 1. The interval-length basis table (contract §1)

Recomputed `L = round(2^{k*beta})` for all 68 (k, beta) pairs.

**66 of 68 entries reproduce. One is wrong.**

- `L(k=12, beta=0.225)`: `2^2.7 = 6.4980`, `round = 6`. The table says **7**.

Consequence: none. That cell has `C_red = 38` (m=3) and `18` (m=2), both far
below the 500 cut, so it is not criterion-evaluable under either value.

---

## 2. Derivation D-1, re-derived from scratch — the upward branch

**The bound is correct.** Let `F` be any finite subset of any abelian group `G`
with `|F| = B`, and let `S_m` be the set of sums of `m`-element multisets from
`F`. The map (multiset) -> (sum) is onto `S_m`, so

```
|S_m| <= #{m-multisets from F} = C(B+m-1, m) = B(B+1)...(B+m-1)/m!
```

and dividing by `N` and by `h = B^m/(m! p)`,

```
R = (|S_m|/N)/h <= (p/N) * C(B+m-1,m) * m! / B^m = (p/N) * prod_{j=0}^{m-1}(1+j/B)
```

This needs no curve, no interval, no prime order, and no genericity. It is
elementary and, as the contract says, near-certainly folklore; I claim no
novelty for it either and retrieved no external source.

**Monotonicity, checked.** `prod_{j<m}(1+j/B)` is strictly decreasing in `B`;
at fixed `beta`, `B ~ p^beta` grows with `p`; and `p/N -> 1` by Hasse. So
`R_max` decreases monotonically to 1 as `p` grows at fixed `beta`. Confirmed
numerically across the full 136-cell grid.

**Design-wide maximum, recomputed.** Using the *exact* Hasse supremum
`p/N <= p/(p+1-2*sqrt(p))` rather than the linearisation `1 + 2/sqrt(p)`:

| cell | m | B | prod(1+j/B) | p/N sup | R_max |
|---|---|---|---|---|---|
| k=12, beta=0.200 | 3 | 5 | 1.6800 | 1.03200 | **1.7338** |

The contract states **1.733**; I get **1.7338**. The 0.0008 gap is the
producer's use of `1 + 2/sqrt(p) = 1.03125` where the true supremum is
`4096/3969 = 1.03200`. Immaterial to every threshold, but it is an
understatement in a table whose declared purpose is checkable arithmetic, and
the same linearisation understates all four `p/N` bounds (3.13% vs 3.20% at
k=12).

**Where the "CANNOT FIRE anywhere" statement is over-stated.** `R_max > 2`
requires:

| m | B | R_max (k=12) |
|---|---|---|
| 3 | 2 | **3.096** |
| 3 | 3 | **2.293** |
| 3 | 4 | 1.935 |
| 3 | 5 | 1.734 |
| 2 | 1 | **2.064** |
| 2 | 2 | 1.548 |

So `R > 2` is excluded exactly when `B >= 4` at `m=3` and `B >= 2` at `m=2`.
The contract's step "Every cell in the design has `B >= 5`" is evaluated on
`B = L`, but the contract elsewhere (correctly and repeatedly) insists that
every criterion is evaluated on **measured** `B`, which is `2 x` the number of
x-values in the interval admitting points and is therefore a random-looking
quantity with fluctuation of order `sqrt(L)`. At the single smallest cell
(`L = 5`), a measured `B = 2` means `F = {P, -P}`, `S_3 = {3P, P, -P, -3P}`,
`|S_3| = 4 = C_all`, and `R = 3p/N ~ 3.0 > 2` exactly. That is not a
hypothetical: it is the case "only one of the five x-values in the interval is
a square", which is not a rare event.

**Narrowest valid statement.** Over the criterion-evaluable set the smallest
`B` is 15 (m=3) and 34 (m=2), where `R_max = 1.248` and `1.062`; the bound is
robust there to any plausible fluctuation of measured `B`. And the inherited
criterion is a *composite* — `R > 2` **and increasing across three consecutive
sizes** — which requires the degenerate `B` at three sizes at once. So:

> `R > 2.0 and growing` cannot fire at any criterion-evaluable cell, and the
> composite three-size form cannot realistically fire anywhere in the design.
> The design-wide ceiling **1.7338** is conditional on `B = L`; at the smallest
> cell it rises to **3.096** if the measured `B` collapses to 2.

**What the bound does and does not settle.** `B^m/(m! p)` is a first-moment
(union-bound) estimate of the decomposition probability. That the number of
*distinct* sums is at most the number of *objects generating them* is close to
definitional, so D-1 does not deliver new information about any exponent — it
shows that `IDEA-20260727-006`'s falsification condition 1 was **malformed at
birth**, because it asked whether a first-moment upper bound could be exceeded
by a factor of two. That is a genuine and valuable pre-freeze catch. It is not
"an answer to the exponent question in the pessimistic direction", and the
contract should not narrate it as one (see objection RT-7).

**Scope, checked in both directions.**

- The bound covers **more** than the declared scope: it holds for any finite
  subset of any abelian group, so the declared restriction to
  "fixed-factor-base, fixed-arity, unweighted decomposition shape" is
  conservative in the safe direction. Good.
- The consequence claim covers **less** than advertised in one specific way:
  `R` bounds distinct **coverage**, not decomposition **multiplicity**, i.e.
  relations harvested per unit work. Index calculus operates in the saturated
  band (`beta > beta*`), where coverage is 1 by definition and the priced
  quantity is multiplicity, which this argument does not bound above at all.
  `H-YIELD-001` interpretation limits do exclude multiplicity explicitly, which
  is correct; the feasibility table's REMOVED-1 narration and the snapshot
  receipt drop that qualifier.

---

## 3. Derivation D-2 and D-3 — recomputed

**Saturation-forced cells (`h >= 1.594`).** Recomputed over all 136 cells:
**9 at m=2, 33 at m=3, 42 total.** Matches the contract exactly. The closed
forms `beta >= 0.5 + 0.8365/k` (m=2) and `beta >= (3.258+k)/(3k)` (m=3) are
both correct (`ln 3.188/ln 2 = 1.6726`, `ln 9.564/ln 2 = 3.2578`).

**`beta*(m) = (1 + log_p m!)/m` — the m=3 row is wrong at three of four sizes.**

| k | contract m=2 | recomputed m=2 | contract m=3 | recomputed m=3 |
|---|---|---|---|---|
| 12 | 0.5417 | 0.5417 | 0.4051 | 0.4051 |
| 14 | 0.5357 | 0.5357 | **0.3982** | **0.3949** |
| 16 | 0.5313 | 0.5312 | **0.3930** | **0.3872** |
| 18 | 0.5278 | 0.5278 | **0.3892** | **0.3812** |

Errors up to +0.008. Consequence: none for any criterion — the D-3 comparison
`beta_cert(3) = 0.6667` vs `beta*(3) ~ 0.381` has 0.28 of margin, and the
criterion-evaluable predicate uses the `h <= 0.5` band, whose four values
(0.3774 / 0.3711 / 0.3664 / 0.3627 at m=3) I reproduce **exactly**.

**D-3 itself is correct.** `beta_cert(m) > beta*(m) <=> p > (m!)^{2/(m-1)}`,
giving 4.0 / 6.0 / 8.3 / 11.0 / 13.6 / 24.5 / 86.2 at m = 2/3/4/5/6/10/20 —
all reproduce. The stated reversal for fixed small `p` and large `m` is real and
is disclosed rather than hidden. Stage 2 is correctly cut, and
`beta_cert - beta_adm` is correctly declared unadjudicated.

---

## 4. The criterion-evaluable set — the contract undercounts by one

Predicate as frozen: `h <= 0.5` **AND** `C_red >= 500`. Evaluated over all 136
cells on the `B = L` basis:

| arity | contract | recomputed |
|---|---|---|
| m = 2 | 27 | **27** |
| m = 3 | 16 | **17** |
| total | 43 | **44** |

The missing cell is **(m = 3, beta = 0.375, k = 12)**: `B = 23`,
`h = 23^3/(6 * 4096) = 0.4951 <= 0.5`, `C_red = 2035.5 >= 500`. The contract's
§5 m=3 table stops at `beta = 0.350` because it applied the **tightest**
`h <= 0.5` band (0.3627, the k=18 value) as a global cut, where the predicate is
per-size and the k=12 band is 0.3774.

Effect on columns: none. The new cell is alone in its column, so the count of
columns carrying at least three sizes is still **nine** — six at m=2
(0.375–0.500) and three at m=3 (0.300, 0.325, 0.350). Both reproduce exactly.

Effect on execution: real. `run_plan` instructs the null arms to run at "the 43
criterion-evaluable cells", and `criterion_evaluable_cell` says "There are 43
such cells of the 136". An Executor that implements the predicate gets 44 and an
Executor that copies the enumeration gets 43. Under ST-3 that is an ambiguity to
stop and report on, which costs the batch a stop.

**Second, sharper ambiguity: the predicate is defined on measured `B`, but the
set is frozen as an enumeration on `B = L`.** Two evaluable cells sit on the
knife edge:

- `(m=2, k=18, beta=0.500)`: `h = 512^2/(2 * 262144) = 0.5000` **exactly**. A
  measured `B` of 514 gives `h = 0.5039` and drops the cell.
- `(m=3, k=12, beta=0.375)`: `h = 0.4951`. A measured `B` of 24 gives
  `h = 0.5625` and drops the cell.

The contract does not say which governs. It must.

---

## 5. Chance fluctuation of E — the null control is not shape-matched

The producer's variance arithmetic is right *for the model it uses*. For `C`
balls in `N` bins, `Var(distinct) = N e^{-L}(1 - (1+L)e^{-L})`, `L = C/N`; I
reproduce 0.12% (k=18, m=2, beta=0.500), 1.04% (k=12, m=2, beta=0.425) and
1.05% (k=12, m=3, beta=0.325), and the design-wide maximum 1.052%.

**But `S_m` is not a set of independent throws.** `F` is closed under negation
and `N` is odd, so `S_m = -S_m` exactly. On multisets, `M -> -M` is an involution
with **no fixed point** among the cancellation-free multisets (a fixed point
would need `P` and `-P` both present), so the `C_red` balls arrive in exactly
`C_red/2` antipodal **pairs**, each pair covering a `{g, -g}` bin-pair.

Consequences, derived on paper:

- **Mean unchanged.** `C_red/2` throws into `(N-1)/2` bin-pairs, each covering
  2 bins, gives `E[distinct] = (N-1)(1-e^{-lambda})` with
  `lambda = C_red/(N-1)`. `P_pred` is therefore correct to `O(1)`.
- **Variance doubled.** `Var = 4 * ((N-1)/2) e^{-lambda}(1-(1+lambda)e^{-lambda})
  = 2 x` the independent-throw variance. Relative sd multiplied by `sqrt(2)`.

Confirmed by a pure integer balls-in-bins probe (`N = 4099`, `C = 568`, 4000
replicates, no curve arithmetic): independent throws give mean 530.6, sd 5.52
(1.040%); antipodal-pair throws give mean 530.4, sd 8.08 (1.523%); variance
ratio 2.14. Analytic mean 530.4. **This probe ran outside the repository, is not
archived, and is NOT evidence — it only confirms an inequality already derived
on paper.**

`CTRL-NULL-SUMSET` as frozen throws "`C_red` uniformly random elements of `G`",
which is the independent model, not the antipodal one. So:

| quantity | contract | corrected |
|---|---|---|
| max chance sd of E over evaluable set | 1.05% | **1.49%** |
| +/-10% band, in sigma | 9.5 | **6.7** |
| F1's 0.80 threshold, in sigma | 19 | **13.4** |

The criteria survive — both remain structure thresholds, and the NOISE-LIMITED
cut at 2% still excludes nothing. What does **not** survive is (i) every sigma
figure quoted in §5 and §6, and (ii) the two tail checks and the standardised
`(|S_m| - P_pred)/sd` bulk check, which divide by an *empirical* sd drawn from
the mis-shaped Monte Carlo and would therefore inflate every standardised
deviation by a systematic factor of 1.41, manufacturing an apparent tail excess
across all 44 cells.

Fix, one line: draw `g` uniformly and insert both `g` and `-g`, `C_red/2` times.

---

## 6. Can S1 fail? Can F1 fire? Is E bounded?

**Bounded above — yes, and the contract does not say so.** `|S_m| <= min(C_all, N)`
gives an exact ceiling `E_max = min(C_all, N)/P_pred`. Recomputed over the 44
evaluable cells:

- lowest ceiling **1.0184** (m=2, k=18, beta=0.350, B=79);
- highest ceiling 1.421 (the high-lambda m=3 cells);
- **17 of 44 evaluable cells have `E_max < 1.10`.**

So at 39% of the evaluable cells the upper edge of the S1 band is
**mathematically unreachable**, and an out-of-band deviation there can only be
downward. This does not break S1 (a ceiling inside the band makes the success
side easier, not impossible) but it makes the band one-sided, and it is exactly
the kind of fact the feasibility table exists to surface. `R_max` is reported
per cell; `E_max` is not, although E is the metric all criteria now run on.

**Bounded below — essentially no, and now with a proof rather than an
assertion.** The contract asserts "nothing in the design bounds E from below".
That is not literally true: `G` has prime order, so `G ~ Z/N` and
Cauchy–Davenport applies, giving `|S_m| >= min(N, mB - m + 1)`. Recomputed over
the 44 evaluable cells, the largest resulting floor is

> **E >= 0.1241** (m=2, k=12, beta=0.425, B=34), and below 0.02 at the largest
> cells.

Far below F1's 0.80. So the contract's claim is **correct in the operative
sense**, and I have replaced the assertion with a rigorous bound. F1's negative
outcome is genuinely reachable.

**S1 can fail**: any one of 44 cells outside [0.90, 1.10], any column slope
outside +/-0.05, a void calibration, an unrecovered null, or any invalidation.
Nothing forces S1.

**F1 can fire**, including its least-examined clause. With exactly three sizes
a column has 1 residual degree of freedom and `t_{0.975,1} = 12.71` — the
contract never mentions this. Worked example, `E = 1.00 / 0.90 / 0.80` at
k = 14/16/18: OLS slope of `log E` on `log p` is `-0.0805`, residual
`s = 0.00507`, `SE = 0.00259`, 95% half-width `0.0329`. The interval excludes
zero with about 2.4x of margin, and `|slope| >= 0.05` holds. So the clause is
satisfiable, but its margin is ~2x, not the ~19 sigma the table's framing
suggests, and it is the binding clause of F1 rather than the 0.80 threshold.

**F2 is the one that is effectively blocked.** F2 requires out-of-band
deviations "with NO monotone trend in p **and no consistent sign**", and its
stated meaning is "the analytic null is missing a term". A missing term in
`P_pred` is multiplicative and produces a **consistent sign** by construction —
and at 17 of 44 cells the counting ceiling makes an upward out-of-band deviation
impossible outright. So F2 excludes its own stated cause.

This opens a concrete **outcome gap**. Suppose `E ~ 0.85` at every evaluable
cell with no trend in `p` — the single most likely non-null result, since it is
what any omitted `O(1)` correction to `C_red` or `P_pred` produces. Then:

- S1 fails (`E < 0.90`);
- F1 does not fire (slope ~ 0, `E` not decreasing);
- F2 does not fire ("consistent sign");

and the run produces **no pre-registered verdict at all** for its most likely
non-null outcome. That is the `EXP-IC-001` v3 / `EXP-ENDO-001` defect class,
one step removed: not an unfirable criterion, but an unclassifiable outcome.
Deleting the four words "and no consistent sign" repairs it.

---

## 7. Calibration leg (CTRL-CALIB-AP / INV-2)

**Targets are quoted correctly.** Against `ledger/EV-STR-001.yaml` line 16:
17.5 / 214.9 (n=211), 41.9 / 924.5 (n=1009), 87.8 / 4128.6 (n=4099) for m=3/4 —
all six reproduce **verbatim**, as do the supply medians 28/8, 124/40, 477/154
(line 15). The penalty is carried as the **range 17.5x–4128.6x** in all three
committed artifacts, with an explicit prohibition on quoting 17.5x alone, in
both the contract (`convention_warning`) and the table (§7). Both trend clauses
check out: monotone in n at fixed m (17.5 < 41.9 < 87.8; 214.9 < 924.5 <
4128.6), and the m=3 -> m=4 multiplier is 12.3 / 22.1 / 47.0, i.e. superlinear.
**This requirement is met.**

The "`B = 15 / 32 / 64.5`" in §7 is quoted verbatim from `EV-STR-001` and is not
an error introduced here, but `ceil(sqrt(4099)) = 65`, not 64.5. Reverse-solving
the source record's own medians shows it used **B = 64** at n=4099:
`C(64,4)/154 = 4126` against the reported 4128.6 (0.06% off), whereas
`C(65,4)/154 = 4396` is 6.5% off. `CTRL-CALIB-AP` freezes `B = ceil(sqrt(n))`,
so it will use 65 and recover 91.6 / 4396.4 against targets 87.8 / 4128.6 —
ratios 1.04 and 1.06, comfortably inside the factor-2 window. No invalidation
risk, but the Executor should record which `B` it used.

**Can the leg fail? Yes — including for the wrong reason.** Two ways:

1. *Correctly*, if the AP admissibility predicate is implemented over the wrong
   support set. Supply would move by an order-1 to order-10 factor and INV-2
   would fire loudly. This is a real known-answer test of the AP enumerator.
2. *Spuriously*, at `(n=211, m=4)`. `EV-STR-001` itself records "supply < B in
   6/6 seeds (as low as 3 tuples)". The census leg uses master seed 110601 with
   six freshly derived per-cell seeds, so it draws **different curves** from the
   six that produced the target medians. At a median supply of 8 with per-seed
   values reaching 3, a fresh median of 3 gives a recovered penalty of 455 —
   `2.1x` the target, outside the window. INV-2 tolerates exactly one failing
   cell, so a single such miss is absorbed; a second (`n=211, m=3` has median 28
   and similar relative scatter) voids the entire census on sampling noise in an
   unrelated leg.

**The inferential link from this leg to the census is asserted, not
established.** INV-2's stated warrant is "if the harness cannot recover a known
penalty ... its yield numbers are not trustworthy". But the leg shares no code
path with the census: it enumerates AP supports at `B = ceil(sqrt(n))` on curves
of order 211/1009/4099 and reports `C(B,m)/supply`, while the census computes
`distinct(S_2 + F)` in a DL image on curves of order ~2^k and reports
`|S_m|/P_pred`. Passing tells you nothing about the sumset estimator, and
failing voids data it never touched. `CTRL-DL` is the control that actually
stands behind the census.

**Executability of the named risk: the predicate IS resolvable.** From the
committed `EXP-STR-001` contract: `factor_base` is "x-interval: first B liftable
x >= 0, canonical y = min(y, p-y), ordered by x" (line 19), an AP support is
`{x, x+d, ..., x+(m-1)d}` with `d` in `D = 1..64` on **x-coordinates** and
non-wrapping (fixed by the negative control's closed form
`sum_{d in D} max(0, p-(m-1)d)`, line 38), one point per x (canonical y), each
support counted once (`D` is positive only), and `yield_penalty = C(B,m)/ap_supply`
is defined verbatim at line 53. I reconstructed the supply from that reading
alone — first `B` liftable x occupy a window of about `2B` integers at density
~1/2, so `supply ~ sum_d (2B - (m-1)d)/2^m` — and obtained:

| n | m | reconstructed | EV-STR-001 median |
|---|---|---|---|
| 211 | 3 | 26.3 | 28 |
| 211 | 4 | 8.4 | 8 |
| 1009 | 3 | 124.0 | 124 |
| 1009 | 4 | 40.7 | 40 |
| 4099 | 3 | 520 | 477 |
| 4099 | 4 | 172 | 154 |

Four of six land essentially on the reported median and the other two within
10%. A predicate that reproduces the source record's own supplies to that
accuracy from the committed text alone is resolvable. **ST-3 should not fire
here**, and the Executor should record the reading it used rather than stop.

---

## 8. Does the budget carry the cells?

Cost model as frozen: `S_2 = distinct(F+F)` costs `B^2/2` modular additions;
`S_3 = distinct(S_2 + F)` costs `|S_2| * B`; memory is one `N`-bit set plus the
DL table.

Recomputed per cell:

| item | recomputed | contract |
|---|---|---|
| DL tables, all four sizes | 348,160 point additions | ~348k |
| largest single cell (k=18, beta=0.600, m=3, B=1783) | 4.674e8 | 4.67e8 |
| all m=3 cells at k=18 | 1.2e9 | ~1.4e9 |
| **entire criterion-evaluable set (44 cells)** | **9.3e5** | not stated |
| **largest single criterion-evaluable cell** | **2.5e5** | not stated |
| peak memory (N-bit set at k=18) | 32,768 bytes + DL table (~262k entries) | << 1 GB |

**Verdict: the budget carries every criterion by roughly three orders of
magnitude, under any implementation, in any language.** The whole evaluable set
is under a million modular additions. The 1.2e9 figure lives entirely in the
priority-3 saturated cells at k=18, which are observations only.

One unstated dependency: the table's "vectorised: seconds" presumes a numpy
implementation, which the contract does not require (it requires exactly one
file and forbids helper modules, but says nothing about vectorisation). A pure
Python driver would spend roughly 10–30 minutes on the priority-3 m=3 cells at
k=18 and would hit ST-2 there. Because `cell_priority_order` runs criteria
first and `reduced_scope_core` preserves every criterion-evaluable cell, the
consequence is a named gap in the observation-only tier — a declared, acceptable
outcome. ST-1's 5e8 cap sits only 7% above the largest cell's 4.674e8
projection, so a measured `B` above ~1907 at that cell trips the cap; that cell
is not criterion-evaluable, so nothing is lost.

---

## 9. Baseline position (RC-7)

Recomputed at k=18 (`N ~ 262144`, `sqrt(N) = 512`): Pollard rho with negation
`0.886 * 512 = 453.6` operations at O(1) memory; BSGS `2 * 512 = 1024`
operations at 512 stored elements. Both figures are correct, both are MEASURED
over 16 targets per size with a re-verified DL certificate per rho solve, and
the model positions are reported beside them. The census costs at least
`N = 262144` group-equivalent operations for the DL table alone, i.e. at least
578x a matched rho, rising to ~1.0e6x at the largest cell — the contract's
"order 10^2 to 10^6" is right, and the standing control that a ratio below 1
would be an accounting red flag rather than an attack is correctly placed.

**Gap: no specialized baseline is named.** For prime-field ECDLP the closest
specialized baseline is summation-polynomial index calculus in the
Semaev/Gaudry/Diem line, which has no known sub-`sqrt(p)` instantiation over
prime fields; the published subexponential and sub-`sqrt` results live over
extension and binary fields. Stating that in RC-7 is what would let a reader see
that the yield factor this contract measures is **not** the binding factor for
the prime-field exponent — the decomposition-test cost is, and this contract
deliberately excises it (correctly, for instrument independence under
`DEC-20260727-009`). Without that sentence, a downstream reader can mistake a
clean outcome (a) for a statement about index-calculus cost.

---

## 10. Sourcing

Every predicted number in the three committed artifacts traces to (i) a
derivation reproducible from the contract alone — D-1, D-2, D-3, `C_red`,
`P_pred`, the variance law, the cost model — or (ii) `ledger/EV-STR-001.yaml`
lines 14–16 for the six calibration targets and three supply medians, quoted
verbatim. **No number is imported from an unarchived probe**, and the contract
says so explicitly and truthfully. `C_red` was verified against `C_all` by an
independent identity at m=2 (`C_all - C_red = B/2`, the number of cancelling
pairs) and re-derived combinatorially at m=3.

One sourcing objection is not about a number but about an inference. The
contract and `H-YIELD-001` present `EV-STR-001` as "a prior pointing toward
outcome (c)". `EV-STR-001`'s own finding (line 26) reads: "The AP penalty is
**supply-side, not per-tuple**: AP tuples hit at comparable per-tuple rates, but
only supply << C(B,m) admissible AP tuples exist." A supply-side penalty is the
*designed consequence* of restricting supports to arithmetic progressions — it
is what the counting heuristic itself predicts for a restricted support class,
and it carries no information about whether the unconstrained heuristic
overstates yield. So the direction of the prior is not established, and
`H-YIELD-001`'s "it is the branch the existing evidence points toward" is an
over-read of its own source. The contract's hedge ("qualitative only", "not a
prediction for the cells tested here") is correct and should be the only
statement made.

---

## 11. Gates reached

R1 criterion firability — reached, full. R2 budget — reached, full. R3 control
integrity — reached, full. R4 sourcing — reached, full. R5 (scope and A1
admission) — reached: the exponent-deciding-screen admission, the A1
non-targeting statement, the toy claim-tier cap, the "no downstream record may
quote it as target-class" prohibition, the "meets no `GOAL-ECDLP-001`
completion criterion" statement, the no-status-change list and the
infrastructure-is-not-evidence rule are all present in the specification body
(`admission_and_ceiling`), mirrored in `H-YIELD-001.interpretation_limits`, and
repeated in the table §11. **Intact.** The single contradiction of it is
REMOVED-1's own narration (objection RT-7).

No gate was left unreached.
