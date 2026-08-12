# SECTION C1 — AM-14 (c), (d), (e) — execution report

    task        TASK-20260809-97d6cf   (executor)
    batch       BATCH-9e3584
    goal        GOAL-MLKEM-005
    section     C1
    claim_tier  TOY
    run         1 of 1
    wall clock  0.25 s

> ### **THIS IS A RE-SCORE OF COMMITTED BATCH-cbe023 DATA UNDER A POST-BATCH THRESHOLD.**
> It is **not** a fresh measurement. No new draw was taken, no frame was built,
> no projection was run. It does **not** reinstate the frozen Section C label
> and it does **not** establish that label's negation. Every statement below is
> about a **condition** — floor versus `tau_rel`, `|t|` versus `|t|crit` — and
> never about that label.

Notarization gate verified; all four sha256 values agree. `certificate.kind:
none`. Claim tier **TOY**.

---

## 1. AM-14(c) — the floor, re-derived from the rebuilt null's own distribution

The design rule of BATCH-cbe023 prereg 4.4 is **carried unchanged**: `tau_rel` =
`1.67x` the top of the measured range of the **null's own median relative
difference**. Only its *input* moves — from the superseded instrument's nulls to
**this batch's rebuilt nulls** — which is exactly what AM-14(c) requires.

| rebuilt null | median relative difference |
| --- | --- |
| `N-A d100_b40` | `0.00645684` |
| `N-A d140_b40` | `0.00976958` |
| `N-B d100_b40` | `0.00768319` |
| `N-B d140_b40` | `0.01496443`  ← top of range |

    tau_rel = 1.67 x 0.01496443 = 0.02499060...  ->  0.025

> ### **THE RE-DERIVED FLOOR IS `tau_rel = 0.025`, against the frozen `0.15`.** Stated in the notarized pre-registration §4.1 **before** any re-scoring, and reproduced here from the committed nulls. It matches the figure AM-14(c) itself names.

**`N-C` is excluded, and the reason is declared rather than assumed.** `N-C` is
the secondary **Gaussian instrument check**. For Gaussian errors,
`R ~ Beta(beta/2, (d-beta)/2)` **exactly** for every orthonormal frame, so
`D = q_emp/q_Beta - 1` is driven to `~0` on **both** sides and the *denominator*
`max(|D_GR|, |D_TL|)` of the relative difference collapses. Its median relative
differences — `1.021643` and `1.004966` — are therefore an artifact of a
vanishing denominator, not a measure of null central tendency. `N-C` also ran at
`R = 60`, below the frozen `R_min = 200`. AM-14(c) names exactly the four
`N-A`/`N-B` medians. **Both the exclusion and the two excluded numbers are on
the record.**

## 2. Every target, at both floors

`SE_2way` and every derived quantity are **recomputed from the committed raw
`8 x 4` `Delta` table**, and reproduce the committed scoring to `0.0` relative
deviation at all ten targets (tolerance `1e-12`).

| cell | target | `\|t\|/\|t\|crit` | rel. diff | floor | FALSIF @ 0.15 | FALSIF @ 0.025 | `SE_2way/SE_naive` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `d100_b30` | `graded_t0.0025` | 0.1738 | 0.01882 | 0.10832 | False | False | 1.0416 |
| `d100_b30` | `graded_t0.0050` | 0.5521 | 0.07270 | 0.13168 | False | False | 1.2196 |
| `d100_b30` | `unreduced` | 0.0702 | 0.03201 | 0.45621 | False | False | **0.3635** |
| `d100_b40` | `graded_t0.0025` | 0.0665 | 0.00260 | **0.03909** | False | False | 1.0736 |
| `d100_b40` | `graded_t0.0075` | 0.5002 | 0.09426 | 0.18843 | False | False | 1.2299 |
| `d100_b40` | `unreduced` | 0.2556 | 0.04342 | 0.16991 | False | False | **0.8495** |
| `d140_b30` | `graded_t0.0025` | 0.2991 | 0.03461 | 0.11573 | False | False | 1.3686 |
| `d140_b40` | `graded_t0.0025` | 0.0901 | 0.03670 | 0.40720 | False | False | **0.9651** |
| `d140_b40` | `graded_t0.0050` | **0.8850** | 0.14117 | 0.15951 | False | False | 1.1810 |
| `d140_b40` | `unreduced` | 0.0120 | 0.00393 | 0.32666 | False | False | **0.8397** |

**`0` FALSIFYING pairs at `0.15`. `0` FALSIFYING pairs at `0.025`. All ten
verdicts are INVARIANT to the repair.** This was declared in advance
(prereg §4.5): with a non-degenerate detection floor of `~10.8%` relative and a
re-derived floor of `2.5%`, the floor is **no longer the binding term** — the
`|t|` clause is — so this section **cannot** produce a falsification the carried
scoring did not already produce. It can only change labels and expose near
misses. That limit was stated before the re-score so it could not be discovered
afterwards and reported as a result.

**Detection-floor citation, carried with its qualifier:** the `3.91%` figure in
the table above belongs to a target flagged **NEGATIVE-VARIANCE-COMPONENT**
(`d100_b40 graded_t0.0025`, `nu_eff = 21` by the residual-df fallback) and is
never cited without that qualifier. The tightest **non-degenerate** floor is
`10.83%` relative and the family-level bound over targets with a well-defined
two-way SE is `~10.8%` relative.

## 3. AM-14(d) — the widened SUGGESTIVE band

Carried band: `|t| ∈ [0.8|t|crit, |t|crit)` **and** relative difference above
`tau_rel`. Widened band: `|t| ∈ [0.8|t|crit, |t|crit)` **regardless of the
relative floor**.

    carried band admits    0 of 10 targets
    widened band admits    1 of 10 targets
    admitted ONLY by the widened band:   d140_b40 / graded_t0.0050

That target has `|t| = 4.5295` against `|t|crit = 5.1179` — a ratio of `0.8850`,
comfortably inside the band — and a relative difference of `0.14117`, which fell
`0.00883` short of the frozen `0.15` and so was excluded by the carried band's
floor condition.

> **A near miss that the carried instrument discarded is now on the record.**
> It is **SUGGESTIVE, NOT FALSIFYING**, and nothing more: it does not meet
> clause (i), and it is a single target in a re-score of committed data.

## 4. AM-14(e) — `SE_2way / SE_naive` at every target

Range over the ten targets: **`0.3635` to `1.3686`**.

> ### **FOUR of ten targets have `SE_2way/SE_naive < 1`, and they are disclosed here explicitly, per target, as AM-14(e) requires:**
> `d100_b30 / unreduced` **0.3635**; `d100_b40 / unreduced` **0.8495**;
> `d140_b40 / graded_t0.0025` **0.9651**; `d140_b40 / unreduced` **0.8397**.
>
> A ratio below `1` is **in tension with AM-7 clause (1)**, which expects the
> two-way construction to be the more conservative one. All four are
> `unreduced` or `d140_b40` targets; the most extreme, `0.3635`, is more than a
> factor of two below the plain sample SE of its own table.

This is reported as an observation about the instrument. **No verdict in this
section depends on it, and none is drawn from it.**

## 5. Predictions, against their falsifiers

| # | prediction | realized | verdict |
| --- | --- | --- | --- |
| **P-C1a** | lowering the floor from `0.15` to `0.025` moves at least one target **out of** "floor ≥ `tau_rel`" into a decidable state | at `0.15`: **4** targets have floor `<` `tau_rel`; at `0.025`: **0** do | **FALSIFIED** |
| **P-C1b** | at least one pair enters the widened band that the carried band excluded | `1` target | **HOLDS** |
| **P-C1c** | at least one target has `SE_2way/SE_naive < 1` | `4` targets | **HOLDS** |

**P-C1a is falsified, and it was pointed the wrong way — the arithmetic could
have told me so before the run.** The floors are unchanged by the repair;
*lowering* `tau_rel` can only make "floor ≥ `tau_rel`" **more** common, never
less. The realized direction is the opposite of the one predicted: at the frozen
`0.15`, four targets had a floor *below* the threshold; at `0.025`, **none**
does, because the smallest floor in the family (`0.03909`, and that one
degenerate) already exceeds `0.025`.

This is recorded as a falsification rather than quietly reinterpreted. Its
substantive consequence is stated as a **condition**, not as a label: at
`tau_rel = 0.025`, **every** target has floor ≥ `tau_rel`, which is the
condition attached to the frozen "UNDERPOWERED — UPPER BOUND" branch; at
`tau_rel = 0.15`, four targets did not satisfy it. **No label is asserted or
negated here in either direction** — the branch conditions are reported and the
adjudication is the Coordinator's.

## 6. Load-bearing clause, and invariance to the repair (AM-14 a)

`tau_rel` is the quantity under repair and it **is** rebuilt here. The verdict
is checked for invariance to it: all ten targets are reported at **both** `0.15`
and `0.025`, and **all ten verdicts are invariant**. That invariance is
disclosed as the section's principal finding about itself — a verdict determined
entirely by a threshold the section did not move is not the section's result,
and none is offered as one.

## 7. What this does NOT establish

* It does **not** reinstate the frozen Section C label and does **not**
  establish its negation.
* **BATCH-a44d08 is not rescored in any respect;** its Section C verdict and
  detection floors remain **VOID IN BOTH DIRECTIONS**.
* No new measurement was performed, so nothing here can strengthen or weaken any
  proposition about tail sufficiency in either direction.
* No algorithm, cost model or attack is proposed, so there is no cryptographic
  baseline and no `dominated_by` / `sota_delta` that could be non-null.
* Claim tier **TOY**.

Per-target detail is in `results_c1.json`. Durable `command.txt`, `stdout.log`
and `stderr.log` are in this task directory.
