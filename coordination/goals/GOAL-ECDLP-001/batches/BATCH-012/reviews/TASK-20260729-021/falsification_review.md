# TASK-20260729-021 — falsification review of the EXP-YIELD-002 result

**Role**: red-team. **Bound snapshot**: `c7189f80225bad0d0d2aa28cbbbb11e672d30dd6`,
parent `f49670fa165e63cb8970ab137a4311c3d8223fd0`, receipt at
`.../BATCH-012/archives/TASK-20260729-019/snapshot_commit_receipt.json`.
**Governing contract**: `specification.yaml` at `f291a624` AS AMENDED by
`amendments/v1_to_v2.yaml` at `e3c9cb45` and `amendments/v2_to_v3.yaml` at
`0548d8cc` — v3 governs, then v2, then v1.

**Independence**: independent non-originating session; no shared conversation
lineage with TASK-20260729-014, -016, -018, -020, -023, -025 or -027.
**MODEL INDEPENDENCE IS NOT AVAILABLE AND IS NOT CLAIMED (INT-BATCH012-D).**
Requested policy `review-adversarial`, effort `xhigh`; resolved model
self-reported `claude-opus-5`, `model_verified: false`, no adapter probe run,
`fallback_used: false`.

**This review makes no commit, changes no status, edits nothing under review,
and creates no evidence, decision or knowledge record.** Every number I computed
myself is an **UNARCHIVED PROBE, RUN OUTSIDE THE REPOSITORY, AND IS NOT
EVIDENCE**; it is arithmetic on already-committed integers and doubles, with
**zero curve compute**.

---

## 0. Snapshot verification, performed by this session

- `git show c7189f80` — parent `f49670fa`, 11 files, all additions, matching the
  receipt's `committed_paths` exactly.
- All eleven `path_sha256` values recomputed from the Git blobs at that commit:
  **all eleven match the receipt**.
- `specification.yaml` unchanged since `f291a624`; `v1_to_v2.yaml` present only
  at `e3c9cb45`; `v2_to_v3.yaml` present only at `0548d8cc`. `git diff f291a624
  HEAD` over `experiments/EXP-YIELD-002/specification.yaml` and
  `amendments/` shows the two amendments added and **the frozen specification
  untouched**. OI-9 immutability re-verified by this session.
- The twelfth declared path is the `-019` receipt itself, deferred by
  construction under INT-BATCH007-T. Strict subset, no extras, no deletions.
- Working tree clean at `256f417a` at entry and left as found.

---

## 1. THE RULING — what P-CORE licenses and what it forbids

### 1.1 Sentences that MAY now be written

Each is verbatim-adoptable. Each is scoped to the 48 declared tuples, one
unreplicated curve-free run set, claim tier **toy**.

> **S-1.** A balls-in-bins process that pre-marks `|S_(m−2)|` bins chosen
> uniformly at random from all `N` bins and then throws `C_red/2` antipodal
> pairs reproduces the unchanged, hash-bound `P_pred` of the committed
> `EXP-YIELD-001` package at all 48 declared parameter tuples, under both
> pre-registered denominator readings and with the pre-registered upward shift,
> with `CR-1`, `CR-2` and `CR-3` firing sets all empty on set identity and
> `n_neg` = 16 inside the pre-registered `[14, 34]` window.

> **S-2.** The arithmetic content of `EV-ECDLP-008` observation `O-4` — that the
> shortfall of the committed antipodal null below `P_pred` is the omitted term
> `|S_(m−2)| e^(−C_red/N)` — is now supported by a measurement of a process, and
> not only by a derivation and by arithmetic on the committed numbers.

> **S-3.** A re-implementation of the no-pre-marking antipodal process, written
> from the contract text without reading
> `experiments/EXP-YIELD-001/driver/yield_census.py`, reproduces the committed
> `RUN-YIELD-001-NULL-RANDOM-SUMSET` antipodal arm at 48 of 48 tuples: `IV-1a`
> and `IV-1b` fire at zero tuples.

> **S-4.** A pass of `P-CORE` is not evidence that the repaired null is exact:
> it is evidence that the null does not fall short by a large fraction of `T`,
> and under a perfectly correct repaired null this design records `P-CORE` only
> about 0.659 of the time, `MISS-MARGINAL` 0.291 and `MISS-STRUCTURED` 0.050.
> *(C-20 makes this mandatory on every record. It must be carried — but see
> objection **RT21-1**: the clause of the original sentence about a shortfall of
> 5 percent of `T` is FALSE, and must not be carried without the correction
> supplied there.)*

### 1.2 Sentences that MAY NOT be written

> **F-1.** *"`P_pred` is certified / correct / validated."* — **FORBIDDEN.**
> What is certified is that the *repaired control object* has the mean the
> derivation says it has. `P_pred` as a model of the decomposition census is not
> touched, and the contract says so in terms
> (`preregistered_prediction.what_the_prediction_does_NOT_say`).

> **F-2.** *"`INV-4` should not have fired / is un-fired / is re-disposed."* —
> **FORBIDDEN** (X1, admission_and_ceiling, PD-9). `INV-4` fired at 4 of 49
> criterion-evaluable cells of the `BATCH-011` package under that contract's own
> rule, and that firing stands untouched.

> **F-3.** *"Some `BATCH-011` `E` value is now readable / recoverable / was
> always fine."* — **FORBIDDEN**, and see §1.3.

> **F-4.** Any efficiency `E`, any yield ratio `R`, or the number `0.85` quoted
> as a measurement. — **FORBIDDEN** (X2, X4). None appears anywhere in the
> package; I checked and found none.

> **F-5.** Any statement about decomposition yield, `H-YIELD-001`, `H-STR-002`
> or any other hypothesis, in either direction. — **FORBIDDEN** (X3).

> **F-6.** Any determination of `INV-5`. — **FORBIDDEN** (X5, `O-8`).

> **F-7.** Any cost-model consequence, re-charge, flag or defence. —
> **FORBIDDEN** (X6). The counterfactual branch on the committed data is `O-6`,
> **not `O-4`**, and **even a fully certified null yields no cost-model
> consequence whatever.**

> **F-8.** Any target-class, exponent, attack, closure or impossibility reading.
> — **FORBIDDEN** (X7, rule A1).

> **F-9.** *"`RC-F` is discharged"* or *"`IV-1` passing is progress on
> `RC-F`."* — **FORBIDDEN** (PD-7, C-12, C-21). See §4.

> **F-10.** *"The repaired null is exact"*, or *"the shift measured in the
> high-precision block confirms `T` to within 0.05 percent."* — **FORBIDDEN**;
> the second is the specific over-read `DEV-4` creates. See **RT21-8**.

### 1.3 Does any `BATCH-011` `E` value become readable? — **NO.**

**I rule with the dispatching session's reading, on three independent grounds,
any one of which suffices.**

1. **Procedural.** `INV-4` is a rule of the `EXP-YIELD-001` contract, evaluated
   on the `EXP-YIELD-001` run. Nothing in `BATCH-012` evaluates, re-evaluates or
   can evaluate a rule of another contract on another run. Un-firing it would
   require either an edit to an immutable committed contract (forbidden) or a
   new run of `EXP-YIELD-001` under a corrected control (does not exist).
2. **Evidential.** The `BATCH-011` red team's ruling was that `INV-4` did not
   show `P_pred` was *wrong* but that `P_pred` was **never certified**.
   `P-CORE` certifies the **control object**, not the **census**. The `E`
   values were normalised against a control that this batch has now confirmed
   was mis-constructed. Certifying a *replacement* control after the fact does
   not supply a denominator for a quantity that was computed against the
   *original* one. No such re-normalisation exists in any committed run, and
   this review computes none.
3. **Structural.** The half of `O-4` that is a claim about the census — that the
   correct null pre-marks the `|S_(m−2)|` bins *a cancelling multiset reaches
   deterministically* — is **not what was measured**. `RC-A` and this contract
   pre-mark a **uniformly random `s`-subset**, and the contract states in terms
   that this is *not* the structurally exact set (at m = 2 the structurally
   correct bin **is** bin 0; at m = 3 it is `B/2` whole antipodal pairs). See
   **RT21-3**.

**Therefore: no `E` value becomes readable, no yield ratio may be quoted, and
the `VOID` stands in full.**

### 1.4 Is `EV-ECDLP-008` observation `O-4` confirmed, superseded, or left standing?

**CONFIRMED IN PART AND LEFT STANDING IN PART. It is NOT superseded, and it is
NOT confirmed as a whole.** `O-4` is a compound observation and the batch
touches its three components differently:

| `O-4` component | Disposition after `P-CORE` |
|---|---|
| **(a)** The shortfall equals `\|S_(m−2)\| e^(−λ)` at every cell. | **Already DETERMINED arithmetic on committed data before this batch.** Reconfirmed. Not newly established. |
| **(b)** A process that *also* pre-marks `\|S_(m−2)\|` bins has mean `P_pred`. | **CONFIRMED BY MEASUREMENT for the first time** — this is the batch's genuine increment, and it is what the frozen `success_criterion` says `P-CORE` establishes. |
| **(c)** `CTRL-NULL-SUMSET` as *implemented in* `BATCH-011` realises only the first term. | **SUPPORTED, NOT INDEPENDENTLY ESTABLISHED.** `IV-1` is clean, but `P-ASRECORDED` was transcribed from a contract text written after the Coordinator read the `BATCH-011` driver, so `IV-1` cannot distinguish *faithful* from *co-defective* (C-12, C-21). |
| **(d)** The bins are the ones *a cancelling multiset reaches deterministically*. | **UNTOUCHED AND STILL UNARCHIVED.** The experiment pre-marks a uniform random subset instead. |

The contract's own `success_criterion` text — *"`EV-ECDLP-008` observation `O-4`
is thereby CONFIRMED BY MEASUREMENT for the first time"* — is **correct only for
component (b)** and must not be adopted unqualified. The verbatim-adoptable
form is **S-2** in §1.1, plus:

> **S-5.** `EV-ECDLP-008` observation `O-4` is **not superseded**. Its
> null-construction component is confirmed by measurement at the 48 declared
> tuples; its component about which bins the correct null should pre-mark is
> untouched by `EXP-YIELD-002`, which pre-marks a uniformly random subset by
> design, and remains supported by argument rather than by measurement.

---

## 2. ATTACKING THE HIT (T2)

The card requires the realised outcome to be attacked as under-informative.

### 2.1 What would have had to happen for the test to fail?

`CR-1` and `CR-2` are **near-tautological**. The contract itself proves, exactly,
`E[distinct] = N − (1 − s/N)[(N−1)A + C] = P_pred + (1 − s/N) f(λ)` with
`f(λ) = e^(−λ)(1+λ) − e^(−λ/2)` bounded at 0.0752 SEM over the declared set, and
`RT-20260729-016` re-derived it from scratch and confirmed it. So `CR-1`/`CR-2`
test **whether numpy's `default_rng` and a thirty-line marking loop reproduce a
proved expectation over 100 or 30 replicates.** For `CR-1` to have failed, the
*implementation* would have had to be wrong — which is what `IV-2`'s eight
known-answer cases were separately built to catch, and they passed.

The non-tautological content is **`CR-3` alone**, because `CR-3` is the only
criterion whose statistic contains a number produced in a *different batch by a
different implementation*. And `CR-3` is anchored by `IV-1`, which C-12 and C-21
declare contaminated.

**Consequence, and it is the sharpest thing I have to say about this batch:**
the strongest evidential content of the run — that the committed `BATCH-011`
antipodal arm *is* a correct realisation of the process without the pre-marking
— **did not require the run.** UNARCHIVED PROBE, NOT EVIDENCE: taking the
committed `mu_001`, `s_001`, `N`, `C_red` from the package and the exact
no-pre-marking mean `N − [(N−1)A + C]`, the standardised residual
`(mu_001 − E_asrec_exact)/sem_001` over the 48 tuples has mean **−0.0122**, sd
1.1303, SEM 0.1631 (t = −0.075). The `BATCH-011` arm is **dead centred on the
exact analytic mean of the process it is now said to have realised**, by pure
arithmetic on already-committed constants. That is what `O-4` asserted, and the
Monte Carlo was not needed to see it.

### 2.2 Could the agreement be manufactured by a simulator built to reproduce the formula it is tested against?

**Partly — and the part that is not manufacturable is what saves it.**

- **Manufacturable.** The driver and the closed form were written by **one
  session from one contract text**. A misreading of that text shared by both
  would produce agreement, and `KA-3` at N = 11 would not catch it, since
  `KA-3` compares the simulator against the *driver's own* evaluation of the
  closed form.
- **NOT manufacturable, and this is decisive.** The target `P_pred` is
  **QUOTED**, not recomputed by this contract, from `IN-1` at
  `2fb2bb7a111d999859612e52990eea7dc6bbac1a`, SHA-256-pinned, with `IV-4`
  firing on any mismatch. The number the repaired null landed on was committed
  in a **different batch at a different commit**, and this batch could not move
  it. `CR-1` and `CR-2` are therefore **not circular**, whatever else they are.

### 2.3 The alternatives, marked EXCLUDED or NOT EXCLUDED

| Alternative reading of the hit | Status under the committed package |
|---|---|
| Simulator defect masquerading as agreement | **EXCLUDED** by `IV-2` KA-1..KA-8, four of them at zero tolerance, plus the twelve-tuple bit-identical reproducibility spot check. |
| Circularity (the target was recomputed to match) | **EXCLUDED**. `P_pred` is QUOTED and hash-bound; `IV-4` re-derivation agrees at max abs diff 0.0. |
| Post-hoc branch selection | **EXCLUDED**. `C-1`'s residual `MISS-MARGINAL` makes the three branches disjoint and exhaustive by construction; `C-16` pre-registered the two expected chance offenders **by name** and neither fired (`\|z_shift\|` 1.9806 and 1.5698). |
| The agreement is a chance pass over a real partial shortfall | **NOT EXCLUDED for φ ≲ 0.02**, **EXCLUDED for φ ≳ 0.04** — see §3 and RT21-1. |
| The `BATCH-011` driver did something other than what the contract said | **NOT EXCLUDED** (`RC-F`, C-12, C-21). |
| The structurally correct pre-marked set differs from the uniform one in a way that matters | **NOT EXCLUDED by measurement**; excluded *for the mean* by a derivation bounding the difference at 0.0895 SEM (m = 2) and below 0.001 SEM (m = 3). No variance claim is made or available (C-13). |
| A third unmodelled term in the repaired null | **STRONGLY DISFAVOURED**, see §5. |

---

## 3. HOW MUCH DOES A SINGLE `P-CORE` ESTABLISH? (adjudication item 2)

**Quantified.** UNARCHIVED PROBE, NOT EVIDENCE; normal reference, exact
Poisson-binomial for `n_neg`, using committed `T_i`, `sem_001,i` and the exact
process bias; `CR-3` folded in as the committed constant factor 0.770 so that
the φ = 0 row reproduces the committed `P(P-CORE) = 0.659`.

| uniform φ | P(`CR-1` or `CR-4` fires) | P(`P-CORE`) ≈ | likelihood ratio vs φ = 0 |
|---|---|---|---|
| 0.000 | 0.124 | 0.659 *(committed)* | 1 |
| 0.010 | 0.170 | 0.64 | 1.0 |
| 0.015 | 0.266 | 0.57 | 1.2 |
| 0.020 | 0.442 | 0.43 | **1.5** |
| 0.025 | 0.663 | 0.26 | 2.5 |
| 0.030 | 0.849 | 0.12 | **5.7** |
| 0.040 | 0.990 | 0.0075 | 87 |
| 0.050 | 0.9999 | 8e-05 | **~8,600** |
| 1.000 | 1.000 | ~0 | ~∞ |

**Reading, and it is a two-sided one.**

- A single `P-CORE` is **decisive** against a uniform shortfall of 5 percent of
  `T` or more (≈ 8,600:1), and **strong** at 4 percent (87:1).
- It is worth **less than 2:1** against a uniform shortfall of 2 percent of `T`
  or less. That regime is genuinely untouched.
- **All of that power sits in three tuples.** `T/sem_001` is 124.73 at
  `T-18-3-B16`, 59.95 at `T-16-3-B16` and 57.56 at `T-18-3-B24`, and below 3 at
  25 of the 29 m = 2 tuples. Against a shortfall that is **not** proportional to
  `T` — a constant offset in bins, or one localised at m = 2 — the design has
  essentially **no** power anywhere.
- **Fragility to name:** what `P-CORE` excludes above φ ≈ 0.03 rests
  overwhelmingly on **one tuple's 100 replicates**. A single mis-resolved
  per-cell quantity at `T-18-3-B16` would erase most of the batch's
  discriminating content. `IV-4` re-derivation at max abs diff 0.0 is what
  currently stands against that, and it is adequate — but the concentration
  should be on the record.

---

## 4. `RC-F` — what this batch does and does not contribute (asked for by the contract)

**`RC-F` IS NOT DISCHARGED, AND THIS REVIEW DECLARES NO DISCHARGE.** `RC-F`'s
second route asked an independent session to re-implement `occupancy_prediction`
and the antipodal `occupancy_null` **from the contract text alone** and reproduce
the four recorded failing cells.

- The **`P_pred` half** is archived: `KA-8` and `IV-4` re-derive `P_pred` from
  `N`, `C_red`, `|S_(m−2)|` and agree with the quoted values at max abs
  difference 0.0 at all 48 tuples including the four failing ones. This is a
  **third** independent reproduction, after `TASK-20260729-007` and `-008`. Real
  but incremental.
- The **`occupancy_null` half is NOT archived**, because the contract text the
  Executor worked from was written by a Coordinator who had read the committed
  `BATCH-011` driver and specified `P-ASRECORDED` to be *identical* to it. C-21
  records that C-3d moved the position **slightly further** from an independent
  re-derivation. `IV-1` passing is therefore **not** progress on `RC-F`.
- **Net:** `RC-F` moves from "undischarged" to "undischarged, with the `P_pred`
  sub-route closed and the null sub-route explicitly contaminated". No record may
  say more.

---

## 5. THE LOOSE THREAD — the +0.3610 `z_sem` shift

**FINDING: most consistent with a chance fluctuation in one arm of one run set,
and positively contradicted as a real bins-level bias by a control that is
already inside the committed package.** It is **not** a third analytic term.

### 5.1 Reproduction and decomposition (UNARCHIVED PROBE, NOT EVIDENCE)

| quantity over the 48 tuples | mean | sd | SEM | t |
|---|---|---|---|---|
| `z_sem` as reported | **+0.3610** | 0.9750 | 0.1407 | +2.565 |
| expected `z_sem` under a perfectly correct null (exact process bias / sem) | +0.0264 | 0.0223 | 0.0032 | — |
| **residual after removing the exact declared bias, REPAIRED arm** | **+0.3346** | 0.9744 | 0.1406 | **+2.379** |
| same residual, **AS-RECORDED arm** (independent streams) | +0.1224 | 0.9563 | 0.1380 | +0.887 |
| same residual, **committed `BATCH-011` arm** | **−0.0122** | 1.1303 | 0.1631 | −0.075 |

I reproduce the Executor's and the dispatching session's figures exactly. The
declared biases account for only +0.0264 SEM, so **+0.3346 SEM is unexplained by
anything declared** — the receipt's "roughly four times the 0.0895 bound" is if
anything an understatement of the gap against the *process* bias, which is the
only one of the two that applies to the specified process at all.

The shift is **structureless**: corr(residual, λ) = +0.02, with `sem` = +0.02,
with `N` = +0.24, with `n_rep` = −0.09; m = 2 gives +0.343 and m = 3 gives
+0.323; sd 0.974 is what N(0.33, 1) predicts. It is a broad shift, not an
outlier artifact.

### 5.2 The cheapest discriminating control — and it has already been run

**A real defect produces a fixed offset in BINS.** `z_sem` scales that offset by
`sqrt(n_rep)/sd`. So an offset large enough to give +0.3346 SEM at 100
replicates **must** give **+2.9 to +3.7 SEM at 10,000 replicates**. The
committed high-precision diagnostic block measures exactly that, at four tuples,
through the **same `draw_replicates` code path** — I read the driver and
confirmed there is **no `n_rep`-dependent branch anywhere in it**.

Measured deviation of the high-precision **repaired** leg from the exact
analytic mean (UNARCHIVED PROBE, NOT EVIDENCE; **no criterion is evaluated on
these numbers, they are not pooled with any criterion quantity, and they change
no branch**):

| tuple | required if the shift were real | observed |
|---|---|---|
| `T-18-3-B16` | +3.09 | **−2.95** |
| `T-16-3-B16` | +3.66 | **+0.97** |
| `T-18-3-B24` | +2.94 | **+0.61** |
| `T-18-3-B28` | +3.24 | **−0.45** |

Four for four in the wrong place. Under the "real bins-level bias" hypothesis
this joint outcome has probability of order 1e-7.

**I flag, rather than gloss, that reading this block at all sits adjacent to its
binding label.** I evaluate no criterion on it, pool it with nothing, and treat
it as what the contract says it is — a diagnostic reported at a precision the
criteria deliberately do not use, whose declared purpose is *"to make the size
and sign of the pre-marking shift visible."* If the Coordinator rules even this
inadmissible, then my §5 finding reduces to §5.3 alone, which is weaker but
points the same way. **My computation is an unarchived probe and is not
evidence in either case.**

### 5.3 Is it a third term nobody has derived? — **No.**

Three independent reasons:

1. `E[distinct] = N − (1 − s/N)[(N−1)A + C]` is **exact**, not asymptotic, and
   was re-derived from scratch and confirmed by `RT-20260729-016` (largest gap
   between exact and asymptotic form over the 48 tuples: 3.05e-05 bins). A
   missing term would be a missing term in a two-line exchangeability argument.
2. A missing analytic term in the throwing part would appear in the
   **as-recorded** arm and in the **`BATCH-011` committed arm**. Neither shows
   it: +0.1224 ± 0.1380 and −0.0122 ± 0.1631. The `BATCH-011` arm is a
   *different implementation from a different batch* and is centred to within
   0.16 SEM.
3. The only structure unique to the repaired arm is step 1, whose contribution
   is at most ~1 bin at m = 2 — far too small to carry +0.34 SEM there — yet
   m = 2 and m = 3 show the same shift.

I also derived and **rejected** the one classical mechanism that would give a
systematic *positive* mean for a `t`-statistic on a left-skewed count:
`E[T] ≈ −γ₁/(2 sqrt(n))`. With `Var(distinct)` of order 350 at the largest
tuples, `|γ₁|` is of order 0.05 and the effect is **~0.003 SEM** — two orders of
magnitude too small. Named and dismissed quantitatively rather than left
hanging.

### 5.4 What remains NOT excluded

- **Chance.** Nominal two-sided p ≈ 0.021 against exact centring, ≈ 0.036
  against the declared bias. This was **not** a pre-registered test statistic —
  `tail_checks` names no statistic and `DEV-6` records that it fires nothing by
  construction — so a post-hoc 2.4σ in a designedly unthresholded quantity is
  worth very little. **This is the reading I adopt.**
- **A small shift common to both `BATCH-012` arms.** Pooling the two independent
  arms gives +0.2285 ± 0.0985 (t = 2.32). Such a shift would have to be a
  property of *this batch's driver, platform or numpy build* rather than of the
  process — and the high-precision block, same driver and platform, disfavours
  it too. **NOT EXCLUDED, and it is the only live non-chance hypothesis.**
- What is **EXCLUDED**: an `n_rep`-keyed code path (read the driver; there is
  none); a defect in the pre-marking (`KA-4`, `KA-5` at zero tolerance); a
  missing analytic term (§5.3).

### 5.5 Does it damage the `P-CORE` reading? — **No, and the reason is not that `CR-4`'s window absorbed it.**

The shift is **positive**: the repaired mean sits *above* `P_pred`. Every
alternative this design exists to detect is a **shortfall** — the repaired mean
*below* `P_pred`. A positive excursion is in the direction *away* from the
counterfactual and cannot manufacture a `P-CORE` that a shortfall would have
denied. `n_neg` = 16 low in `[14, 34]` is the same fact read a second way, not a
second fact.

**But it must be recorded, not absorbed**, and it constrains one sentence: no
record may say the repaired null lands **on** `P_pred`. It lands **at or
slightly above** it, by an amount larger than the declared second-order biases
account for and currently unexplained.

---

## 6. PRE-STATED NARROWEST SENTENCE PER OUTCOME (T4)

Pre-stated for all three branches, as the card requires, so that the realised
branch is not the only one on record.

**HIT (`P-CORE`) — the realised branch. Decision label: `confirm_scoped`
(instrument question only); `inconclusive` on everything else.**

> At the 48 de-duplicated criterion-evaluable parameter tuples of the committed
> `EXP-YIELD-001` v2 package, a curve-free occupancy simulation that pre-marks
> `|S_(m−2)|` uniformly chosen bins before throwing `C_red/2` antipodal pairs
> reproduces the unchanged, hash-bound `P_pred` under both pre-registered
> denominator readings, with all three per-tuple firing sets empty on set
> identity and `n_neg` = 16 inside `[14, 34]`. This confirms by measurement, for
> the first time, that `CTRL-NULL-SUMSET` as frozen in `EXP-YIELD-001` v1 and as
> re-specified by amendment `C-4` was mis-constructed by exactly the omitted
> term, and it establishes nothing else. It does not certify `P_pred` as a model
> of the decomposition census, does not un-fire or re-dispose `INV-4`, makes no
> `BATCH-011` efficiency `E` readable, declares `INV-5` neither way, moves no
> hypothesis, and yields no cost-model consequence whatever — the counterfactual
> branch being `O-6` and not `O-4`. `EV-ECDLP-008` observation `O-4` is neither
> superseded nor confirmed as a whole: its null-construction component is
> confirmed and its component about which bins the correct null should pre-mark
> is untouched. Claim tier toy; a single unreplicated curve-free run set; not a
> cryptanalytic result.

**MISS (either branch), had it occurred. Decision label: `weaken` plus a named
replication — `reject_scoped` FORBIDDEN.**

> A single unreplicated curve-free run set missed the pre-registered prediction
> at N tuples. This weakens, and does not refute, the null-construction reading
> of the `BATCH-011` `VOID`. A simulator defect, a bin-accounting difference
> from the `BATCH-011` process, a second-order term at the fixed replicate
> count, a seed pathology and a mis-resolved per-cell quantity are enumerated;
> those the package excludes are named and the rest stand. The named successor
> is a replication of the repaired arm under a fresh master seed on a different
> interpreter and platform, which `BATCH-012` does not perform and does not
> authorize. `INV-4` stays fired, no `E` is computed, `INV-5` is declared
> neither way, no cost model is touched.

**MIXED across cells or across denominator readings. Decision label:
`inconclusive` on the instrument question.**

> The two pre-registered denominator readings disagree, or the criteria disagree
> across the declared set. The discrimination between the two live explanations
> of the `BATCH-011` `VOID` recorded at `DEC-20260729-001` rationale `R-8`
> remains undischarged. No branch of the `EXP-YIELD-001` v2 outcome disposition
> table is read, and the correct label is `inconclusive`, not a pass and not a
> refutation.

---

## 7. REFUTATION ARTIFACT (T5)

Ordered strongest first, as the card requires.

1. **Counterexample certificate** — a tuple, seed and replicate stream at which
   the pre-marked antipodal process demonstrably does *not* have mean
   `P_pred + (1 − s/N) f(λ)`. **This batch can produce none, and none can
   exist**, because that identity is an exact theorem, independently re-derived.
   Not available and correctly not claimed.
2. **Derivation note** — the exact-mean derivation with its `O(1/N)` control.
   **Available, and it is already committed**, in
   `process_specification.effect_size_arithmetic_OB_10` and re-derived at
   `RT-20260729-016`. This is the strongest artifact the batch actually
   possesses, and it is stronger than the measurement it is paired with.
3. **Declared `empirical_only`** — the 48-tuple Monte Carlo. **This is what the
   run itself is**, and it must be declared as such.

**Ruling: the batch's basis is `derivation note` for the analytic content and
`empirical_only` for everything the run adds. Any record that omits the
`empirical_only` declaration for the measured half has an undeclared basis, and
that is the failure — not the absence of a certificate.**

---

## 8. PARETO HONESTY (T6)

`dominated_by`: **`NOT_APPLICABLE_BY_CONSTRUCTION`** — and this is a checked
null, not an unchecked one. `EXP-YIELD-002` solves no instance, recovers no
discrete logarithm, computes no relation and executes **zero group operations**;
it occupies no row of any ECDLP time/memory/data frontier, so no row can
dominate it.

**Frontier rows actually checked**, so that the null is auditable:

| baseline | position | relation to this batch |
|---|---|---|
| Pollard rho | ≈ 0.886 sqrt(N) group ops, O(1) memory (the harness's variant stores visited classes, O(sqrt N)) | not comparable; this batch performs 0 group ops |
| BSGS | ≈ 2 sqrt(N) time, sqrt(N) stored elements; measured 64 / 129 / 257 / 512 stored at k = 12/14/16/18 | not comparable |
| Closest specialized: decomposition / summation-polynomial index calculus over prime fields (Gaudry–Diem line) | no known advantage over rho at these sizes; the parent census is measured at 28,384× to 2,604,442× a measured rho solve of the identical instance (`EV-ECDLP-008` `O-11`) | that position stands **unretracted and is NOT restated as a result of `BATCH-012`** |

`sota_delta`: **0 by construction.** No algorithmic task is attempted and no
operation count of any kind is produced. The standing measured delta from the
parent batch is the `O-11` range above; `BATCH-012` neither improves it,
worsens it, nor re-derives it, and **no cost model is touched (X6).**

---

## 9. SCOPE (T3) AND CLAIM TIER (T7)

**A1 admission confirmed, in full.** `EXP-YIELD-002` moves no exponent and
cannot move one; measures no yield; is a curve-free balls-in-bins simulation of
a control object over an integer residue range; claim tier **toy**; meets no
completion criterion of `GOAL-ECDLP-001` under any outcome; leaves all four
asymptotic-claim promotion gates open; claims and can claim no closure quorum.

**Largest scope supported:** the 48 declared tuples; field sizes k ∈ {12, 14,
16, 18} with quoted group orders 4001, 16619, 65633, 261707; the frozen β grid
as realised in the source package; arities m ∈ {2, 3}; the x-interval
factor-base convention with B measured; one prime-order curve per size in the
*source* package; this simulator, this budget, one platform, one numpy build
(2.4.0); the occupancy **control object** alone.

**Scopes NOT supported:** any curve; any field size not listed; any
cryptographic scale, in either direction; any decomposition-yield quantity; any
`E`; any cost model; any hypothesis; `INV-5`; any other arity, coefficient set,
factor-base convention or curve per size; **and replication — 48 parameter
tuples are not 48 replications**, and the inputs themselves come from a single
unreplicated source run set.

**Claim-tier check:** I searched the eleven committed artifacts and found **no
sentence asserting above tier**. `ST-4` is honoured — the package states no
branch disposition. The `-019` receipt correctly states the branch as the frozen
rule classifies it and correctly refuses a disposition. The one sentence in the
governing contract that *would* assert above tier if adopted unqualified is the
`success_criterion`'s *"`O-4` is thereby CONFIRMED BY MEASUREMENT"*; §1.4
narrows it. **No lane is declared dead: the decomposition-yield question remains
open.**

---

## 10. OBJECTION LINES NOT REACHED INSIDE THE CAP

Named rather than silently dropped:

1. I did not re-derive the four corrected pre-registered feasibility sets from
   `IN-1` independently. `RT-20260729-025` did, on set identity, with all four
   symmetric differences empty; I accepted that.
2. I did not re-derive the full 48-tuple conditional `CR-3` budget or the
   `P(MISS-STRUCTURED) = 0.050` figure. I checked only that my own
   `CR-1`+`CR-4` computation is *consistent* with the committed `P(P-CORE) =
   0.659` once `CR-3`'s committed 0.2296 is folded in, which it is.
3. I did not audit the eight `RT29-*` objections of `TASK-20260729-029`
   individually.
4. I did not verify the twelve-tuple bit-identical reproducibility spot check by
   re-running it.
5. I did not read the `KNOWNANSWER` `results.json` case-by-case; I relied on the
   summary and the receipt for `IV-2`.
6. I did not audit `DEV-1`, `DEV-2`, `DEV-3` or `DEV-7` beyond their summary
   text.

---

## 11. DISCLOSURE

An untracked macOS AppleDouble sidecar
`.../BATCH-012/reviews/._TASK-20260729-029` exists in the reviews directory. It
is **outside my write scope** and I did not touch it. No tracked file was
created, modified or deleted by this session outside
`.../BATCH-012/reviews/TASK-20260729-021/`, and **no commit was made**.
