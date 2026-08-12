# SECTION C2 — AM-14 (b): a positive control that ACTUALLY INJECTS — execution report

    task        TASK-20260809-3eb72c   (executor)
    batch       BATCH-9e3584
    goal        GOAL-MLKEM-005
    section     C2
    claim_tier  TOY
    run         1 of 1
    wall clock  0.24 s

**This is a control ON THE INSTRUMENT.** It says nothing about tail sufficiency
in either direction, and it neither reinstates nor negates the frozen Section C
label. Notarization gate verified; all four sha256 values agree.
`certificate.kind: none`.

---

## 1. What was actually done

AM-14(b) exists because closed-form arithmetic *in the SE the control is meant
to validate* cannot detect SE inflation and is therefore not a control. So:

* the declared offset was added to **every entry of the committed raw `8 x 4`
  `Delta` table**;
* the **entire** scoring path was re-run **from that table** at every rung —
  two-way variance decomposition, `SE(Delta_bar)`, Satterthwaite `nu_eff`,
  `|t|`, `|t|crit`, relative difference, and the FALSIFYING-PAIR verdict under
  both clauses;
* **no closed-form shortcut is used anywhere.**

Ladder, declared in advance in prereg §5.2, in units of each target's committed
`SE`: `0, 0.5, 1, 2, 3, 4, 6, 8, 12`. Scored at **both** `tau_rel = 0.15`
(frozen) and `tau_rel = 0.025` (re-derived by Section C1), so no C2 verdict is
determined by a threshold this batch did not rebuild.

## 2. The instrument is clean on the axis AM-14(b) targets

| check | result |
| --- | --- |
| reproduction at `delta/SE = 0` — `Delta_bar`, `SE`, `nu_eff`, `\|t\|`, verdict | **10 of 10** targets, max relative deviation **`0.0`** |
| `SE` recovered at every rung `delta > 0` vs the committed `SE` | max relative deviation **`8.53e-16`** over all targets and all rungs |
| **SE inflation detected** | **0 of 10 targets** |
| `\|t\|` monotone non-decreasing in `delta` above the committed `\|Delta_bar\|` | **10 of 10** targets |

> ### **P-C2e HOLDS: the recovered `SE` matches the committed `SE` to floating-point rounding at every target and every rung. The two-way decomposition is invariant to a constant additive offset in the implementation, not merely in the algebra — which is what AM-14(b) asked to be shown rather than assumed.**

## 3. Predictions, against their falsifiers

| # | prediction | realized | verdict |
| --- | --- | --- | --- |
| **P-C2a** | at `delta/SE = 0` every target reproduces its committed scoring to `1e-12` relative | 10 of 10, deviation `0.0` | **HOLDS** |
| **P-C2b** | `\|t\|` monotone non-decreasing in `delta` once `delta` exceeds `\|Delta_bar_committed\|` | 10 of 10 | **HOLDS** |
| **P-C2c** | **no** target returns FALSIFYING at `delta/SE <= 1.0` | **1 target does**, at both floors | **FALSIFIED** |
| **P-C2d** | every target with `\|t\|crit < 8` returns FALSIFYING at `delta/SE = 12` | 6 of 6, at both floors | **HOLDS** |
| **P-C2e** | recovered `SE` = committed `SE` to `1e-12` relative at every target | max dev `8.53e-16`, 0 targets inflated | **HOLDS** |

**Detection floor:** `0.5 SE`, the ladder's bottom rung. Nothing below `0.5 SE`
is tested and nothing below it is claimed.

## 4. P-C2c is FALSIFIED — and the diagnosis is a defect in my own pre-registration, not in the instrument

The target is `d140_b40 / graded_t0.0050`:

    committed  Delta_bar = 3.626896e-03    SE = 8.007297e-04    |t| = 4.5295    |t|crit = 5.1179
    delta/SE = 0.5   |t| = 5.0295   rel 0.15676   FALSIFYING False
    delta/SE = 1.0   |t| = 5.5295   rel 0.17234   FALSIFYING TRUE   <- fires at the "should not catch" rung

The pre-registration declared that a FALSIFYING verdict at `delta/SE <= 1.0`
would mean **"the instrument fires on nothing and is over-sensitive"**. That
consequence does **not** follow here, and I say so rather than letting the
declared reading stand:

> **This target's committed `|Delta_bar|` was already `4.5295 SE` — `88.5%` of
> its own critical value — before anything was injected. Adding `1 SE` moves
> `|t|` to `5.5295`, which crosses `|t|crit = 5.1179` by arithmetic that has
> nothing to do with the instrument's sensitivity.** A **constant additive**
> injection on top of an already-near-critical `Delta_bar` cannot distinguish
> "the instrument fires on nothing" from "the instrument fires on the sum of a
> pre-existing near-critical quantity and a small offset". The ladder's bottom
> rungs are therefore **not** a clean over-sensitivity test at any target whose
> committed `|t|` is already close to `|t|crit`.

**The design gap is in prereg §5.2's `SHOULD NOT catch` clause, which I wrote,
and it is recorded as a defect of this section rather than as a finding about
the instrument.** The other nine targets — all with committed `|t|/|t|crit`
between `0.012` and `0.552` — do **not** fire at `delta/SE <= 1.0`, which is the
behaviour the clause intended to test and which those nine do exhibit.

**The concrete repair, pre-registered here for a successor rather than run
post-hoc:** a **CENTERED** variant of this control, in which the injection is
applied to a table whose own `Delta_bar` has been subtracted off, so the rung
value is the *only* signal present. That isolates the instrument's own
sensitivity from the target's committed effect. It is deliberately **not** run
in this task: it is not in the notarized text, and adding an unregistered
analysis to rescue a falsified prediction is the failure mode this batch exists
to close.

## 5. P-C2d, and the four targets that correctly do not fire at 12 SE

Six targets have `|t|crit < 8` and **all six** return FALSIFYING at
`delta/SE = 12`, at **both** `0.15` and `0.025`. The four that do not fire are
exactly the four with `|t|crit >= 8`, and they should not:

| cell | target | `\|t\|crit` |
| --- | --- | --- |
| `d100_b30` | `unreduced` | `70.0234` |
| `d140_b40` | `graded_t0.0025` | `25.3559` |
| `d140_b40` | `unreduced` | `21.6181` |
| `d100_b40` | `unreduced` | `18.9009` |

At `delta/SE = 12` the injected `|t|` is about `12`, so a critical value above
`8` — let alone above `20` — is simply not reached. These critical values are
driven by very small `nu_eff` (`1.00` to `1.50`), which is the degenerate
regime. **The control does not fire there, and that is the correct behaviour,
not a failure.**

## 6. The arrangement in which this control could not fail — both directions

* **could-not-FIRE** — "the injection is applied to `Delta_bar` *after* the
  variance decomposition, so `SE` is unchanged by construction and inflation can
  never be detected." **This is the exact defect AM-14(b) names, and it is
  averted:** the offset goes into the **raw `S x E` table** and
  `se_decomposition()` is re-run **from that table** at every rung; the
  recovered `SE` is compared against the committed `SE` at every rung and the
  maximum deviation is reported (P-C2e).
* **could-not-PASS** — "the ladder starts so high that every rung fires, making
  'detects the injection' vacuous." **Averted:** the ladder starts at `0.5 SE`,
  below every target's `|t|crit`, and P-C2c declared in advance that the bottom
  two rungs must not fire. The control had a live failure mode at both ends —
  and, as §4 records, **the bottom end actually fired**, which is why the
  falsification is on the record rather than absent from it.

## 7. What this does NOT establish

* This is a control **on the instrument**. It says nothing about tail
  sufficiency in either direction, and it neither reinstates nor negates the
  frozen Section C label.
* **BATCH-a44d08 is not rescored in any respect.**
* No algorithm, cost model or attack is proposed, so there is no cryptographic
  baseline and no `dominated_by` / `sota_delta` that could be non-null.
* Claim tier **TOY**.

Full ladders, per target and per rung, are in `results_c2.json`. Durable
`command.txt`, `stdout.log` and `stderr.log` are in this task directory.
