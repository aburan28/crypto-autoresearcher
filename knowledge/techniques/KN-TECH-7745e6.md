---
id: KN-TECH-7745e6
type: technique
title: Calibrate small-n matched-null bands before trusting a heavy-tailed higher-moment ratio statistic
tags: [null-calibration, bootstrap, heavy-tail, higher-moment, multiple-comparison, sample-size, matched-null, ordering-control, false-positive-rate, methodology, statistics, calibration]
confidence: reported
complexity: >-
  not a cost model - a discipline for calibrating a fixed-band pass/fail rule
  against a matched-null control before trusting any cell it labels
  "above band"; the operative quantity is the empirical false-positive rate
  of the band itself, not its width in the units of the statistic
applicability: >-
  every program instrument that reports a ratio of an m-th-moment (m>=3)
  quantity in a treatment arm to the same quantity in a small-sample
  (n roughly 30) matched-null arm, and classifies the ratio into a fixed
  multiplicative band (e.g. [0.7,1.4]) as "in band" / "above band" /
  "below band"
source_refs: [EV-MONO-b84b24, EXP-MONO-c819ba, H-MONO-663fb4, KN-TECH-052]
added: '2026-08-30'
superseded_by: null
---

## Method

EXP-MONO-c819ba pre-registered fixed multiplicative bands
(`[0.7,1.4]` at m=3, `[0.85,1.15]` at m=4) for the ratio of a treatment arm's
higher-moment character-bias statistic to a matched-null arm's, with the
null arm built from `n=30` random symmetric-subset draws per cell. One cell
(the j=0 curve at F=N/2) reproduced above-band on both seeds and was
escalated, per the frozen contract's own `falsification_criterion(d)`, as a
candidate exceptional-locus signal.

Two independent reviewers, using disjoint methods, converged on retracting
that escalation and diagnosing why: the band itself was never calibrated
against its own null. A 20,000-trial bootstrap recalibration of the band,
run under the null hypothesis being exactly true, found an **empirical
false-positive rate of approximately 65% at m=4** — not the few percent a
nominal fixed band implicitly assumes — because the underlying statistic
(`Var_R N_m(R)` at m>=3) is severely right-skewed and a 30-draw null sample
cannot estimate its spread reliably. This was independently reconfirmed by:

1. **A second, unrelated curve landed the same way.** RO3, a curve the
   original run had itself labelled `IN_BAND`, showed the same heavy-tailed
   null shape under recalibration — evidence the miscalibration is a
   property of the instrument's design, not of the one escalated cell.
2. **Draw-count sensitivity flips the label.** Re-running the *identical*
   cell (same curve, same field, same F) with `n=200` null draws instead of
   30 moved the observed ratio from 1.165-1.170 (above band) to 1.133
   (below band) — the classification of a fixed real-world observation
   changed sign purely from widening the null sample.
3. **A null-object control quantifies the base rate.** With a held-out
   random subset standing in for the "real" arm (so no real effect can be
   present by construction), 3,000 replicates showed `P(>=1 cell
   reproducible above-band across both seeds, panel-wide) = 0.996` — a
   reproducible-looking exceedance is nearly certain to occur *somewhere*
   in a panel this size purely from the band's own miscalibration.
4. **Multiple-comparison correction removes every surviving cell.**
   Applying a Bonferroni correction over the ~96 cells actually tested in
   the archived run leaves no cell significant at nominal 0.05.
5. **An independent, larger-scale replication found no effect at all.**
   Constructing 254 wholly new curves (124 j=0, 130 matched random-ordinary)
   and running the same instrument found no enrichment of the escalation
   pattern on j=0 curves (12.1% vs 20.0%, Fisher p=0.092, direction opposite
   to the original claim) — the escalated signal does not reproduce outside
   the archived panel at all.

## The rule this establishes

**A fixed multiplicative band around a matched-null ratio is a claim about
that null's sampling distribution, and that claim needs its own evidence
before the band is trusted — independent of whether the band "looks
reasonable."** For m<=2 statistics (means, or low-moment quantities with
roughly symmetric, well-concentrated null distributions), a fixed band at
n~30 may be adequate; nothing here contradicts that. The failure is specific
to **m>=3 ratio statistics with heavy-tailed null distributions**, where a
small null sample systematically understates the null's own spread, so a
band calibrated on eyeballing round numbers passes real noise through as
signal far more often than its nominal width suggests.

Before trusting any such band, cheaply verify it BEFORE running the
treatment arm (all four checks below are affordable at toy scale, far
cheaper than the treatment computation itself in every case observed so
far):

1. **Bootstrap the band under the null.** Resample (or re-simulate) the
   null arm many times and measure what fraction of resamples the band
   itself would flag — this is the band's actual false-positive rate, and
   it can differ from the nominal assumption by an order of magnitude.
2. **Scan draw count.** If the classification of a fixed observation flips
   as the null sample size grows, the band is not yet calibrated at the
   smaller size.
3. **Run a null-object control.** Hold out part of the null population to
   stand in for "treatment" (so no real effect is possible by construction)
   and measure how often the band alone produces a reproducible-looking
   hit across the whole panel — this is the base rate the treatment result
   must clear.
4. **Correct for the number of cells actually tested**, not just the one
   that was escalated — an uncorrected single-cell p-value from a
   multi-cell scan is not the evidence it appears to be.

## Relation to the ordering control

A distinct, sharper diagnostic was available and unused here: the frozen
contract's own `ordering_control` states that if the rule emits the same
label on a null cell and a treatment cell, "it discriminates nothing and
must be rewritten before any treatment output is read." The archived null
arm was itself `ABOVE_BAND` on 17 of 192 null-vs-null combinations,
including one reading 3.4x the escalated treatment value — which by the
contract's own literal text should have halted interpretation before any
treatment cell was read at all. This was not caught by the Executor. A
contract's ordering control is only as good as actually checking it against
the FULL null-vs-null grid, not a narrower per-cell noise screen — the
cheapest version of the four-step calibration above is often already
present in a well-designed contract and simply needs to be run to
completion.

## What this technique is not

This is not a claim that fixed multiplicative bands are wrong in general,
that H-MONO-663fb4's underlying mechanism claims are wrong, or that the
program's identities (I1)-(I3) are in doubt — all three held under
independent review. It is a narrow, quantified, convergently-demonstrated
statement about when a specific class of pass/fail instrument (heavy-tailed
higher-moment ratio, small matched-null sample) needs calibration evidence
before its verdicts can be trusted, and a cheap four-step recipe for
producing that evidence before running the expensive arm.

## Addendum (2026-08-31), disclosed per AGENTS.md immutability rules — not a retraction

An independent Red Team review of this lane's follow-on experiment
(EXP-MONO-670aa6, EV-MONO-849355) found that this entry's own worked
example above — "Applying a Bonferroni correction over the ~96 cells
actually tested in the archived run leaves no cell significant at nominal
0.05" — states a genuine fact but omits a further, orthogonal check: at
`n=30` null draws, the permutation p-value floor is `1/31 ≈ 0.032`, which
already exceeds `alpha/96 ≈ 0.00052` by ~60x, so that Bonferroni step was
GUARANTEED non-significant regardless of the data, not merely observed to
be non-significant. This does not change this entry's own conclusion (the
band-calibration failure this entry documents is real and independently
confirmed by other means, including the bootstrap and the 254-curve
replication, neither of which depends on the Bonferroni sentence), but the
Bonferroni sentence itself should have been recognized as vacuous by the
same "check your instrument's operating characteristics before trusting
its verdict" discipline this entry teaches — applied to its own worked
example. **See [[KN-TECH-95a42b]] for the general form of this check**
(floor `1/(n+1)` vs. correction threshold `alpha/m`, verified at design
time before any draw is spent) — a distinct, arithmetic failure mode from
the null-calibration bootstrap this entry's main text covers, discovered
because the SAME uncorrected arithmetic recurred, unnoticed, when this
lane's next experiment (EXP-MONO-670aa6) adopted a superficially "fixed"
200-draw design that still failed the floor-vs-threshold check this
addendum names.
