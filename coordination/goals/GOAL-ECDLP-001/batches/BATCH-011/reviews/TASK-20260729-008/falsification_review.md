# TASK-20260729-008 — Red-team falsification review of EXP-YIELD-001

Companion to `red_team_report.yaml` (RT-20260729-008). Snapshot under review:
commit `2fb2bb7a111d999859612e52990eea7dc6bbac1a`, parent `81e5edc3`, 20 declared
paths, 20 committed, verified reachable from `HEAD` = `c3e2f453`. Independent
non-originating session. Model independence is not available and is not claimed.
Zero curve compute; no run was executed; nothing outside this task directory was
written.

---

## 1. The ruling

**VOID stands, and the fault is a located, repairable instrument fault. Both are
true and the decision record must carry both.**

The diagnostic is correct. I re-derived it from the frozen contract before
reading the Executor's arithmetic, and it is stronger than the Executor claimed.
It is nevertheless not grounds for re-dispositioning `INV-4` inside
EXP-YIELD-001. The repair belongs to a successor, and on the reused cells that
successor cannot be confirmatory.

### The case for VOID, at full strength

`INV-4` is not a formality. Its job is to certify `P_pred` empirically *before*
any `E` is read — the contract says so in `occupancy_prediction` ("validated
empirically by the RUN-YIELD-001-NULL-RANDOM-SUMSET arm") and in
`CTRL-NULL-SUMSET.failure_meaning`. That certification did not happen. Worse, the
control that was supposed to perform it is *still* not shape-matched to `S_m`
after the one repair the amendment cycle bought: `RT-4` correctly identified that
`CTRL-NULL-SUMSET` was not shape-matched, `C-4` repaired the antipodal-pairing
half of the mismatch, left the pre-marking half untouched, and then asserted that
the two means agree to `O(1)` — which is false at `m = 3`. The rule fired for
exactly the reason it was written, on exactly the data it was written to police,
on the more forgiving of the two available denominator readings. `RC-11`'s single
amendment cycle is spent. This program has already had to correct one contract
(`EXP-IC-001` v3) for outcome-selected criteria. And the diagnostic was *found by
a dry run of the fired rule* — its use as a repair inside this batch is
data-motivated in origin, whatever its analytic standing.

### The case against, at full strength

The fault is one deterministic term in a Monte Carlo control, not an error in any
measured quantity. `|S_m|` is exhaustive, deterministic and seed-free — there is
no seed, no sampling, no stopping rule that a dry run could have tuned. `P_pred`
is recomputable from the frozen v1 formula and I reproduced all 49 recorded
values to the printed precision. The omitted term is exact set inclusion,
`S_{m−2} ⊆ S_m`, which needs no simulation at all: at `m = 3` a multiset
`{P, −P, Q}` sums to `Q`, so `S_1 = F ⊆ S_3` with probability 1. `INV-4`'s own
frozen text voids *every `E` value*, not every measurement — that distinction is
in the contract, not invented here. And the correction was catchable with no data
whatsoever; `TASK-20260729-003` even wrote the correct fact ("`S_{m−2}` is
genuinely a subset of `S_m`") one paragraph before endorsing the mean.

### Why both, and what decides it

What `INV-4` actually established is *not* that `P_pred` is wrong. It is that
`P_pred` **was never certified**. "Not certified" and "refuted" are different,
and `VOID` is the correct word for the first. So:

- The **disposition** stands: `P0` governs, no outcome branch is evaluated, the
  batch decision is `inconclusive` plus a scoped instrument successor.
- The **diagnostic** is recorded as a located instrument fault with a named
  repair. Recording it is required by AGENTS core rule 8 (unexpected observations
  must be recorded, not silently discarded); it needs no amendment, because
  recording is not re-dispositioning.

### Licensed

| | |
|---|---|
| **L1** | `inconclusive` + a scoped **instrument** successor (`P0`). The only disposition available. |
| **L2** | Recording the diagnostic as a located fault with a named repair. |
| **L3** | Carrying forward as DETERMINED, toy-tier **observations, not evidence about yield**: `|S_m|` and identity-multiset counts at all 136 cells; `B`, `L`, `B/L`, `h`, `C_all`, `C(B,m)`, `C_red`; collision profiles; `CTRL-DL` (80,000 checks, zero mismatches); the AP calibration leg (`INV-2a` and `INV-2b` both not fired); measured rho and BSGS baselines with re-verified DL certificates. |
| **L4** | Writing a successor contract that pre-registers the repaired null. |
| **L5** | Correcting `C-4`'s `O(1)` claim and the identical slip in the `TASK-20260729-011` recheck note — **by supersession, never in place**, exactly as `C-7` handled the `TASK-20260729-002` receipt. |

### Forbidden

| | |
|---|---|
| **X1** | Re-dispositioning `INV-4` to NOT FIRED, on this or any basis. |
| **X2** | Computing `E` against a repaired `P_pred` or repaired null and reading **any** branch of the outcome table off it inside BATCH-011. |
| **X3** | Any `support`, `weaken` or `reject_scoped` label on `H-YIELD-001`, `Y2`, `H-IC-001` or any other hypothesis from this run set. (`reject_scoped` is separately forbidden on a single unreplicated empirical-only run set.) |
| **X4** | Quoting the three out-of-band cells, or `E ≈ 0.85`, as a measured yield shortfall — in either direction. |
| **X5** | Declaring `INV-5` FIRED or NOT FIRED as a finding of this batch. |
| **X6** | Re-charging, flagging or defending any index-calculus cost model on anything here. |
| **X7** | Quoting any part of this package as target-class under rule A1, as an exponent result, an attack, a closure, or an impossibility claim. |

---

## 2. Is the diagnostic correct? — YES, and stronger than claimed

**Re-derivation from the contract.** `conventions_fixed.occupancy_prediction`
gives

```
P_pred = N (1 − e^{−λ}) + |S_{m−2}| e^{−λ},   λ = C_red/N,  |S_0| = 1, |S_1| = B
```

which is algebraically identical to

```
P_pred = |S_{m−2}| + (N − |S_{m−2}|)(1 − e^{−λ})
```

— the mean of a process that **pre-marks** the `|S_{m−2}|` deterministically
reachable bins and then throws `C_red` balls uniformly over all `N` bins.
`CTRL-NULL-SUMSET`, both as frozen in v1 and as re-specified by `C-4`, throws
`C_red/2` antipodal pairs into an **empty** `N`-bit set and produces only the
first term. The gap is exactly `|S_{m−2}| e^{−λ}` (less an `O(1 − e^{−λ})` term
from the `N−1` versus `N` bin count). At `m = 2` it is `1·e^{−λ}` and invisible
against single-replicate sd of 3–100; at `m = 3` it is `B·e^{−λ}` and dominates
wherever `λ` is small.

**Combinatorics checked independently.**
`C_red = Σ_{k=1..m} C(B/2,k)·C(m−1,k−1)·2^k` counts multisets drawn from `k`
distinct antipodal classes, one sign per class, with a composition of `m` into
`k` positive parts — exactly the cancellation-free multisets. At `B = 16, m = 3`:
`16 + 224 + 448 = 688`, matching the recorded `C_red`. Both closed forms
reproduce.

**Numerical check.** Recomputing `P_pred` from the frozen formula at all 49
criterion-evaluable cells reproduces the recorded value with max absolute
difference `0.000`. The driver implements the frozen prediction; the fault is not
an implementation slip.

**The strengthening the Executor did not claim.** The reported residual after
adding the term back spans `[−0.534, +0.267]` in *single-replicate* sd units — I
reproduce that exactly. Under `DEV-4`'s stricter alternative (standard error of
the mean, at the recorded replicate counts 100/30/10) the same residual spans
`[−2.93, +2.67]` over 49 cells — precisely the range 49 standard-normal draws
should occupy, with **zero** cells outside 3. So:

| reading of "3 empirical sd" | uncorrected | corrected |
|---|---|---|
| single-replicate sd (applied, `DEV-4`) | fails 4 / 49 | passes 49 / 49, max \|z\| 0.53 |
| standard error of the mean | fails 22 / 49 | passes 49 / 49, max \|z\| 2.93 |

One term closes it under both readings. Had a second unmodelled term existed it
would appear in that residual; it does not. The fault is fully located and fully
closed.

**Where the error was born — not in the Executor and not in the run.** `C-4`'s
basis asserts the antipodal mean is `(N−1)(1 − e^{−λ})` and that "`P_pred` is
therefore CORRECT to `O(1)`", silently dropping `P_pred`'s second term. The
`TASK-20260729-011` recheck note repeats it numerically ("the difference is
`O(1)` — at `λ = 0.5` it is about 0.09"), a figure obtainable only by comparing
against the first term alone. This is a shared arithmetic slip across the
amendment and both pre-execution reviews, and `OB-4` requires it be superseded.

---

## 3. Was the pre-registration contaminated? — NO detectable contamination; one unclosable residual

**Structurally immune where it matters.** The primary metric `|S_m|` is
exhaustive, deterministic and seed-free. There is no seed, no target sampling, no
stopping rule and no estimator choice in it. Given the frozen curve-selection
rule and the frozen `β` grid, `|S_m|` is a function of the contract alone.

**What is checkable, and checks out:**

- `INV-4` is evaluated in the driver as
  `bool(abs(ma - p_pred) <= 3 * sa)` against
  `occupancy_prediction(N, cred, s_prev)` — the frozen formula, nothing
  subtracted, nothing repaired.
- The diagnostic fields (`S_m_minus_2_term`,
  `residual_after_adding_back_over_sd`) are written per cell and consumed by **no
  criterion, no threshold and no cell class**.
- Replicate counts follow `C-14` exactly: 100 where `C_red ≤ 10⁴`, 30 between
  `10⁴` and `10⁶`, 10 above — verified against every cell.
- Master seeds are the six declared in the frozen v1 `replication` block.
- Cell class is computed by `classify_cell(B, m, p)` **before** any sumset is
  built, per `C-2` rule `R-2`.
- `P_pred` is the frozen formula at all 49 cells (§2).

**The residual that cannot be closed from the snapshot.** The pre-dry-run driver
was never committed, so "only reporting changed — no threshold, criterion, seed,
control process, replicate count, cell class or measurement, and no arm added" is
a **self-attestation that cannot be diffed**. One minor tell: the
`derived_diagnostic` rollup is emitted only `if failed`, i.e. the code's shape
records that the firing was known. That is harmless in itself and is exactly what
AGENTS rule 8 asks for, but it is not independent corroboration.

**Verdict.** Not contaminated on any evidence available, and the metric that
matters is structurally immune. Record it that way — not as a clean bill. `RC-F`
closes the gap cheaply: commit the development driver's `sha256`, or have an
independent session re-implement `occupancy_prediction` and the antipodal
`occupancy_null` from the contract text alone and reproduce the four failing
cells (curve-free, archivable).

---

## 4. `R-7` drift — classing on measured `B` remains sound

**It stands, and the drift is evidence *for* the rule.**

- `R-2` freezes each cell's class from measured `B` alone *before* `S_m` exists.
  The driver implements that order. The class is never a function of an outcome,
  so the drift cannot be outcome-selected.
- All 11 movers moved because measured `B > L` — a property of the interval
  realisation, not of any `E`, which did not exist yet.
- The 44th cell `C-1` added, `(m=3, k=12, β=0.375)`, left on measurement exactly
  as `R-4` named in advance: evaluable iff `B ≤ 22` (even `B`, `B³ ≤ 3p`);
  measured `B = 28` gives `h = 0.8926`. `R-4` explicitly calls a flip an
  **ordinary event** — not a deviation, not an invalidation, no `ST-3`.
- Freezing the `B = L` enumeration instead would have evaluated criteria at three
  cells whose measured `h` is 0.552, 0.649 and 0.893 — inside the saturation band
  the entire design exists to avoid.
- `R-6` correctly applies the realised denominator `n_eval = 49` to the
  one-third clause.

**Two residual objections** (`OB-8`, `OB-9`):

1. **The drift is one-sided.** Aggregate measured `B/L` is 1.046, 1.077, 1.004,
   1.030 at `k = 12, 14, 16, 18`. The realised set gained cells almost entirely
   by crossing the `C_red ≥ 500` floor, and 8 of the 11 movers sit at
   `C_red` between 578 and 722 — the smallest-`C_red`, largest-relative-sd corner
   of the design. The realised evaluable set is biased toward its noisiest cells.
2. **`n_eval = 49` counts 48 distinct factor bases.** See §6.

Both are successor-design constraints, not defects in the drift disclosure.

---

## 5. Should `INV-5` have fired? — neither FIRED nor NOT FIRED; **UNADJUDICATED BY CONTRACT DEFECT**

| reading | count | consequence |
|---|---|---|
| strict literal ("any deviation of `E` from 1") | 16 of 49 do not shrink, ≥ 3 ⇒ **fires** | forbids any interval-structure reading |
| purposive (deviation that would drive a reading) | max \|E − 1\| among those 16 is **0.0157**, all in-band; `n_not_shrinking_and_out_of_band = 0` ⇒ **does not fire** | — |

The strict reading is unsound as an instrument: it fires on noise at in-band
cells — `E_randomFB` is itself a mean of only 3–10 draws, so at `|E − 1| ~ 0.001`
"shrink" is a coin flip — and would then forbid reading the three out-of-band
cells that **do** shrink. A trigger with that shape carries no information.

The Executor was right to refuse the determination (`ST-4`, `DEV-6`): the trigger
turns on an unquantified word and `C-13` gives the disposition a three-way
reading the Executor may not choose among.

**Nothing turns on it here.** The conservative branch — no interval-structure
reading in either direction — is what §6 requires on scope grounds anyway, and
every `E` is void regardless. Record `INV-5` as UNADJUDICATED-BY-DEFECT with both
readings and their counts, and require the successor to quantify "shrink" before
data (e.g. `|E_randomFB − 1| ≤ ½|E_interval − 1|`, evaluated only where
`|E_interval − 1|` exceeds 3 chance sd).

---

## 6. What this batch licenses about decomposition yield — and where the boundary is

**Nothing.** Every `E` is void by pre-registration.

The dispatching card states that the `m = 3, k = 12` cells at `E ≈ 0.85` are "the
shape the disposition table routes to `O-4`". **On the committed data that is
wrong, and it must not enter a decision record.**

- `O-4` requires `OUT` to exceed one third of `n_eval`. Recorded: `n_out = 3`,
  `n_eval = 49` — **6.12 %** against a one-third threshold of 16.33 cells.
- Every one of the **ten** realised evaluable columns is `FLAT` (|OLS slope| ≤
  0.05 with a 95 % interval containing zero; largest is `+0.0408` at `m = 3,
  β = 0.350`). So no column is `DOWN-SIGNIFICANT` or `UP-SIGNIFICANT`, and
  `O-8`, `O-2`, `O-3`, `O-7` are all excluded.
- `O-1` fails because `OUT` is non-empty.
- **First matching branch: `O-6`, SPARSE OUT-OF-BAND SET** — `inconclusive` at
  batch level, with the explicit instruction that **no cost model is
  re-charged**.

So the counterfactual outcome of a repair is the *weakest* branch in the table,
not the strongest. Any record mentioning the counterfactual must name `O-6`, must
not name `O-4`, and must carry that sentence.

**And the three cells are two factor bases, on one curve.**

- `(k=12, β=0.325)` and `(k=12, β=0.350)` have identical measured `B = 22`,
  identical `C_red = 1782`, identical `|S_3| = 1232`, identical `E = 0.8484`,
  identical max load 14. `L` is 15 and 18: the `x` values 15, 16, 17 admit no
  point on that curve, so the two cells select the **same factor base**. It is
  the only duplicate in the evaluable set — 49 cells carry 48 distinct
  `(k, m, B)` triples.
- All three sit on **one** curve: `k = 12`, `p = 4099`, `N = 4001`,
  `y² = x³ + 4x + 8`, the smallest size, where the contract's own declared
  weakness is exactly one curve per size.
- In both affected columns `E` rises monotonically toward 1 with `p`
  (0.848, 0.964, 0.985, 1.015 at `β = 0.325`; 0.848, 0.988, 1.014, 1.015 at
  `β = 0.350`). **The deviation shrinks with size** — the opposite direction from
  outcome (c).
- `O-6` requires stating whether the out-of-band cells sit at the smallest
  `C_red`. They do not (`C_red` 1340 and 1782 against a design minimum of 578);
  they sit at the largest `λ = C_red/N` among small-`N` cells (0.33–0.45 at
  `N = 4001`). That is a **finite-`N` / approach-to-saturation** signature, not a
  yield-heuristic signature — and the recorded collision profile says the same:
  max load 12–14 where a `Poisson(0.43)` maximum over 4001 bins is about 4–5.

**The narrowest statement the batch supports** (adoptable verbatim):

> EXP-YIELD-001 v2 supports no statement about decomposition yield. `INV-4` fired
> at 4 of 49 criterion-evaluable cells, so every occupancy-normalised efficiency
> `E` in the package is VOID rather than negative by pre-registration, no outcome
> branch is evaluated, and the void is never a negative mathematical result. What
> the batch does support, at claim tier toy and at no strength above
> `preliminary`, is one instrument finding, derived from committed quantities and
> independently re-derived at TASK-20260729-008: the occupancy null
> `CTRL-NULL-SUMSET`, as frozen in v1 and as re-specified by amendment `C-4`,
> does not simulate the process `P_pred` models, because it throws `C_red` balls
> into an empty `N`-bit set while `P_pred` is the mean of a process that also
> pre-marks the `|S_{m−2}|` bins a cancelling multiset reaches deterministically;
> the discrepancy is exactly `|S_{m−2}|·e^{−C_red/N}` at every one of the 49
> cells, invisible at `m = 2` where the term is 1 and dominant at `m = 3` where
> it is `B`; and with that term restored the antipodal null recovers `P_pred` at
> 49 of 49 cells within 3 standard deviations under both the single-replicate and
> the standard-error-of-the-mean readings of `INV-4`. Correspondingly, `C-4`'s
> claim that `P_pred` is correct to `O(1)` against the antipodal process holds at
> `m = 2` and fails at `m = 3`. Separately, and as observations rather than
> evidence: `|S_m|` is DETERMINED exhaustively at all 136 cells with no cell
> skipped and no firing of `INV-1`, `INV-2a`, `INV-3` or `INV-6`; `CTRL-DL`
> agreed on all 80,000 curve-versus-DL-image checks; and the census cost
> 2.8 × 10⁴ to 2.6 × 10⁶ times a measured Pollard-rho solve of the same instance,
> so it is not and cannot be an attack.

---

## 7. Pre-stated narrowest sentences per outcome (T4)

These were the card's deliverable and are recorded even though the realised
disposition is VOID. Each is written for verbatim adoption by a decision record.

**Outcome (a) — `O-1` / `S1` met.** *Would have justified: `support` at strength
no higher than `preliminary`, scoped, with a named replication.*

> At 12 to 18 field bits, `m ∈ {2,3}`, x-interval factor bases anchored at 0 on
> the frozen `β` grid, on one prime-order curve per size, the counting heuristic
> `B^m/(m! p)` is consistent with the exhaustively measured decomposition count
> once the multiset factor `∏(1 + j/B)` and the birthday correction are applied,
> and no residual trend in `p` is detectable at these sizes. This is toy-scale
> validation of a heuristic and nothing more: it does not upgrade the heuristic
> to a theorem, certifies it at no larger size, leaves the index-calculus lane
> permanently heuristic-conditional, and — per `C-11` — would move nothing about
> the prime-field exponent, because the binding factor there is the
> decomposition-*test* cost, which this contract deliberately excises.

**Outcome (b) — yield exceeding the heuristic by a factor growing in `p`.**
*Would have justified: nothing. It is excluded a priori on this metric.*

> Outcome (b) is arithmetically unreachable on `R` and on `E`: `R ≤ (p/N)∏(1 +
> j/B)` and `E ≤ min(C_all, N)/P_pred` per cell, and both ceilings fall toward 1
> as `p` grows. An observation above a cell's own ceiling is `INV-1`, an
> implementation defect, and is **never** an observation of outcome (b). Per
> `C-7` this closes no exponent question — `B^m/(m! p)` is a first-moment
> estimate, so "the number of distinct sums is at most the number of objects
> generating them" is close to definitional; what it establishes is that
> `IDEA-20260727-006`'s falsification condition 1 was malformed at birth. The
> qualifier that `R` bounds distinct **coverage** and not decomposition
> **multiplicity** may not be dropped.

**Outcome (c) — `O-2` / `F1` met.** *Would have justified: `weaken` **plus a
named replication** — never `reject_scoped`.*

> In at least one evaluable column, at 12 to 18 field bits only, the
> occupancy-normalised yield falls below 0.80 at the largest evaluated size with
> a significantly negative slope in `log p`, and the deviation shrinks under
> factor-base randomisation. Index-calculus cost models in this ledger that
> charge against `B^m/(m! p)` are therefore optimistic at these sizes and
> worsening with size. This **flags** those models; it does not re-charge them,
> which is separate work. It is not an attack, not a closure, not an
> impossibility claim, and not a statement about any field size outside 12 to 18
> bits.

**Realised — `P0` / VOID.** *Justifies: `inconclusive` plus a scoped instrument
successor.* See §1 and §6.

**Counterfactual after repair — `O-6`.** *Would justify: `inconclusive` at batch
level, no cost model re-charged, every out-of-band cell named individually.* See
§6.

---

## 8. Strongest available refutation artifact (T5)

Ordered per the card: counterexample certificate → derivation note → declared
`empirical_only`.

- **Counterexample certificate — not available and not applicable.** There is no
  claimed solve, relation or bound to certify against. The only certificates in
  the package are the rho and BSGS discrete-logarithm certificates, which the
  driver re-verified and which all match the DL table; they certify the
  *baseline*, not any yield claim.
- **Derivation note — AVAILABLE, and this batch can produce it now.** The
  strongest checkable artifact this result admits is a derivation note showing
  that `P_pred = |S_{m−2}| + (N − |S_{m−2}|)(1 − e^{−λ})` is the mean of the
  pre-marked process, that the specified `CTRL-NULL-SUMSET` produces only the
  first term, and that the difference `|S_{m−2}|·e^{−λ}` accounts for the entire
  recorded shortfall at all 49 cells. It requires no compute, no curve, and no
  new run — §2 above is that note. Its empirical counterpart, `RC-A`, is
  curve-free, costs of order 10⁶ RNG draws, and **must be archived under a
  successor run id or it is not evidence**. This program has already driven one
  decision from an unarchived probe that then failed to reproduce; nothing here
  repeats that.
- **Declared `empirical_only` — the correct basis for everything else.** The
  three out-of-band cells, the `B/L` bias, the collision profiles and the
  baselines are `empirical_only`, single run set, unreplicated, one curve per
  size. Declaring the basis is what matters; an undeclared basis would be the
  failure, not the absence of a proof.

---

## 9. Scope confirmation (T1, T7) and Pareto honesty (T6)

**A1 admission survives intact.** `EXP-YIELD-001` moves no exponent and is an
exponent-*deciding* screen, expressly not an exponent-targeting mechanism under
`docs/target-result-profile.md` rule A1. Claim tier reads `toy` in the summary
and in every manifest. The measured census-to-rho operation ratio is 28,384 /
147,480 / 512,582 / 2,604,442 at `k = 12/14/16/18` — the census costs
2.8 × 10⁴ to 2.6 × 10⁶ times a measured rho solve of the same instance and cannot
be an attack under any reading. **Nothing here is quotable as target-class.**

**Maximum scope any reading could ever have had:** four prime field sizes
`k ∈ {12,14,16,18}`; **one** prime-order curve per size by a deterministic rule;
x-interval factor bases anchored at 0 on the frozen 17-point `β` grid;
`m ∈ {2,3}`; unweighted decomposition with coefficients in `{+1,−1}`; multiset
repetition allowed; membership by hash lookup with no polynomial solver; one
implementation, one budget, one platform. **Out of scope, and the list is not
decorative:** other integer coefficients; adaptive factor bases; decomposition
*multiplicity*; `β_cert`; the `(m+1)/(2m)` derivation;
`IDEA-20260727-006`'s headline gap claim (`DEFER-BATCH011-002`); arity above 3;
binary and extension fields; any curve beyond the four selected; any field size
outside 12–18 bits; **every cryptographic size**.

**The toy-to-crypto step, attacked by name.** At 12–18 bits the interval factor
base is a large fraction of the field at higher `β`, so the short-box regime is
barely entered: measured `B/L` exceeds 1 at nearly every cell (aggregate 1.046 /
1.077 / 1.004 / 1.030 by size), and at `k = 12` the whole grid saturates by
`β = 0.500` with `|S_m| = N = 4001`. The regime an index-calculus cost model
actually charges — `B` a vanishing fraction of a cryptographic-size field, with
`m` growing — is not entered at all. The contract states
`correspondence: null — direct sampling`, so there is no substitute-sampling
route to scale of the kind `docs/target-result-profile.md` requires. Nothing
measured here is evidence about cryptographic-size curves in either direction.

**Pareto honesty.** `dominated_by: pollard-rho-with-negation`. Frontier rows
actually checked: **time** — census/rho 2.8 × 10⁴ to 2.6 × 10⁶, BSGS 97–810
operations; **memory** — census `O(N)` bits plus an `N`-entry DL table against
rho's `O(1)` stored points (this harness's table-based rho is declared as
`O(√N)`) and BSGS's measured 64/129/257/512 stored elements; **data/queries** —
the census is exhaustive over all `N` targets and its setup alone costs `N` group
operations, more than the `0.886√N` a rho needs to solve outright;
**specialized** — summation-polynomial index calculus (Semaev/Gaudry/Diem) has no
known sub-`√p` prime-field instantiation, so it does not dominate rho over prime
fields either, and the census does not implement it. `sota_delta`: negative on
every axis, between −4.5 and −6.4 orders of magnitude in time. There is no
favourable reading to protect, and under VOID there is no reading at all.

**Declare no lane dead.** Nothing here is an impossibility result, and the VOID
is emphatically not one — a fired validity gate is the *absence* of a
measurement, not the presence of a negative one. The decomposition-yield question
at `m ∈ {2,3}` over prime fields remains **open**, and is now cheaper to answer
than before, because the instrument fault is located and its repair is one term.

---

## 10. Objection lines not reached inside the 2400-second cap

Named explicitly, per the card:

1. The deterministic curve-selection rule was **not** re-executed — that needs
   curve compute, which this card forbids. The four recorded curves were checked
   only for plausibility (`t = 12, 5, 14, 6` candidate sums against an expected
   8–12 trials for prime order) and internal consistency (`N` prime, `N ≠ p`,
   Hasse-admissible traces 99, −207, −95, 441, generator recorded, DL walk
   closure and the `2x+1 = N` point count both true).
2. The AP calibration leg's supplies were not independently reconstructed; only
   its rollup and the `INV-2a` / `INV-2b` determinations were audited.
3. The Gumbel tail check and the standardized bulk check were not recomputed cell
   by cell — both are denominated in the same empirical sd whose consumer
   `INV-4` already voided, and `OB-9` makes their independence assumption unsound
   regardless.
4. The 87 non-criterion-evaluable cells were reviewed only in aggregate.

---

## 11. Single next concrete action

Coordinator writes `DEC-20260729-001` as **`inconclusive`** on `EXP-YIELD-001`
with the VOID upheld under `P0`, carrying `OB-1`–`OB-3` verbatim, and dispatches
**one** scoped instrument successor whose first and only gate is **`RC-A`**: the
curve-free repaired-null re-derivation at the four `INV-4`-failing cells —
pre-mark `|S_{m−2}|` bins, throw `C_red/2` antipodal pairs, compare against the
unchanged `P_pred` under both denominator readings — archived under its own run
id, **predicted in advance** to land within 3 standard deviations under both.
Nothing else in this lineage moves until `RC-A` is archived and verified, because
`RC-A` is what decides whether the fault is in the control's construction or in
`P_pred` itself, and every other successor question is downstream of that answer.
