---
id: KN-TECH-39a853
type: technique
title: "A two-point (zero-degree-of-freedom) local exponent cannot be read directionally without an independent estimate of its own sampling variance -- and lowering the moment order rescales the units, not the resolvability"
tags: [local-exponent, two-point-slope, zero-degrees-of-freedom, jackknife, standard-error-scaling, noise-floor, same-t-disjoint-window-control, coupled-null, control-blindness, methodology, hqc]
confidence: reported
complexity: not applicable; this record states a measurement-methodology lesson, not a cost
applicability: "any campaign that reads a local scaling exponent from TWO points of a noisy statistic -- alpha = -[log f(T_hi) - log f(T_lo)] / [log T_hi - log T_lo] -- and treats its sign, its magnitude, or a difference between two such exponents as a finding, where f is itself an estimator (a jackknife SE, a bootstrap SD, a resampled moment) rather than a directly observed quantity."
source_refs: [EV-HQC-4973ff, EV-HQC-e458ef, EV-HQC-927899, EV-HQC-469c08, DEC-20260817-2fb269, DEC-20260817-2b638b, DEC-20260815-176614, TASK-20260814-8bbdd2, TASK-20260815-e61cca, TASK-20260817-c603c0, TASK-20260817-b4b6e4, TASK-20260817-cddd45, TASK-20260817-785c5c]
added: 2026-08-17
superseded_by: null
---

## What this record is

GOAL-HQC-001 invented a two-point local-exponent diagnostic at
`TASK-20260814-8bbdd2` and read it directionally for five batches: sign
flips between shards, values "far outside [0.4, 0.6]", shard-to-shard
heterogeneity, and a batch-size/transition-regime explanation of the sign
pattern. Two later batches measured what the diagnostic's own noise is.
This entry states the general lesson, the cheap procedure that establishes
it, and the specific way the campaign's own escape route failed.

It is a lesson about an **instrument**, not a finding about HQC. This
program has measured nothing about HQC's IND-CCA security, its
decoding-failure rate, or assumptions A17/A5, and this entry claims nothing
about them.

## (1) The general lesson

**A two-point local exponent has zero internal degrees of freedom.** It is
one number computed from two numbers, so it carries no residual, no scatter
and no internal estimate of its own variance. Nothing about it announces
when it is noise. If `f` is itself an estimator with sampling error, the
exponent inherits that error multiplied by `1 / (log T_hi - log T_lo)`, and
a reader who has not measured that error has no basis for reading the
exponent's sign or magnitude in either direction.

The failure mode is not that the exponent is *wrong*. Every value
`GOAL-HQC-001` published is a correct, reproducible computation, and where
independently re-checked they are bit-identical. The failure mode is that
**a correct measurement was read as a finding without its yardstick**.

## (2) The cheap procedure that fixes it, and it needs no parametric model

The decisive control is a **same-parameter, disjoint-data repeat**: evaluate
`f` twice at the *same* `T`, the same object and the same procedure, on
disjoint index ranges, and take

```
D(k) = | log2( f(window_A) / f(window_B) ) |
```

Because every local exponent in this family is exactly a log-ratio of `f`,
`D` is *already in exponent units*. It is distribution-free, needs no null
model, no band, and no assumption about the estimator's law, and it usually
costs nothing because the windows have already been paid for. In
`GOAL-HQC-001` this handle was sitting inside data the campaign had already
computed and was not reported until a reviewer extracted it.

Measured there: `D_RMS` = 0.086 at k=2, 0.125 at k=5, 0.898 at k=10, 3.170
at k=17, against a total observed phenomenon of 3.702 exponent units.

**Its own limit must be stated whenever it is used: it is a SCALE, not a
distribution.** With `n = 2` contrasts no confidence interval is computable
and none may be claimed.

## (3) The sharper lesson this batch added: lowering the moment order rescales the units, not the resolvability

The obvious escape from a noisy high-order estimator is to move to a lower
order where the estimator is nearly exact. `GOAL-HQC-001` measured its own
estimator bias at `-7e-5` at k=2 against `-0.10164` at k=17 and adopted
exactly that reading. **It does not work, and the reason generalises.**

Both the deviation being read and the noise scale reading it are log-ratios
of the same estimator at the same order, so the order sets the scale of
both, and they contract together:

| k | 2 | 5 | 10 | 17 |
|---|---:|---:|---:|---:|
| deviation from 0.5, fresh set | 0.128 | 0.197 | 0.636 | 2.461 |
| same-T noise scale `D_RMS` | 0.086 | 0.125 | 0.898 | 3.170 |
| **ratio** | **1.50** | **1.58** | **0.71** | **0.78** |

From k=17 to k=2 the noise fell **37.0x** while the deviation fell only
**19.2x**. In the instrument's own units the deviation is *largest at low
k*, peaking near k=4-5, and never falls decisively below one noise scale
anywhere in k = 2..26.

**Generalised: when the statistic and its noise scale are the same
functional of the same estimator, changing the parameter that shrinks the
statistic shrinks the yardstick at least as fast. A "collapse toward the
expected value" observed in absolute units, without renormalising by a
same-parameter noise scale, is a change of units and not a change of
significance.** A campaign that reads the first as the second will conclude
its phenomenology was an artifact of the parameter, and will be wrong.

The diagnostic test is the one `docs/inventor-protocol.md` section 3 already
prescribes, applied to the escape route rather than to the original claim:
name what the *noise-normalised* quantity should do if the explanation is
right. Here it should decay toward zero as k falls. Measured, it stays flat
and then rises. A quantity that fails to decay when it should is the
artifact tell -- and it can fire on the refutation side.

## (4) The replacement is usually already computed, and it is dominant

On identical data the `>= 3`-rung OLS in log-log dominates the two-point
estimator outright. Recorded verbatim as this campaign's standing
`dominated_by` value:

> **"4-rung OLS in log-log on identical data, SD 0.234334 against 0.700666,
> a 2.99x noise reduction at zero cost."**

Corroborated on independent coupled replicates at 3.652x (k=5), 3.722x
(k=10) and 3.439x (k=17), and on the real object the 4-rung ladder at k=5
returns `0.518 +/- 0.073` and `0.483 +/- 0.055` on two independent shards
over a 4x range in `T` -- both consistent with `1/sqrt(T)`, with 2 residual
degrees of freedom against the two-point estimator's zero. **This is the
campaign's first readable exponent, and it cost no new data.** Recording
`dominated_by: null` for a two-point local exponent anywhere would be a
fabrication.

## (5) A confound that travels with the replacement, and must be named with it

The ladder is dominant and it is **not** confound-free. In `GOAL-HQC-001`
the jackknife batch count is pinned (`N_JACK_BATCHES = 200`), so the
ladder's four rungs `T in {5000, 10000, 20000, 40000}` correspond to batch
sizes `25 / 50 / 100 / 200`: **with a fixed batch count, batch size and
absolute `T` are one variable and no factorial separates them; only varying
the batch count does.** Any exponent fitted across such a ladder is a
scaling in that single compound variable. Fixing it requires either varying
the batch count or persisting the per-trial data so the analysis can be
re-run at another batch count -- which is why *not* persisting raw per-trial
arrays converts a free re-analysis into an impossible one.

## (6) The parametric route is the tempting one and it failed twice, in a way worth predicting

The natural alternative to a same-parameter empirical control is a
synthetic null object with the estimator's null behaviour built in. In this
campaign it failed twice, and both failures are instructive rather than
accidental.

- **Wrong shape.** The first null drew its two arms from independent
  streams while the real pair shared 55 of 56 blocks on every trial, so the
  paired estimator *was* the unpaired estimator and the 2.3x-28.7x pairing
  gain that defines the real instrument was set to 1.
- **Right family, extremal parameter.** The corrected null coupled the arms
  but set the per-trial disagreement rate to `2p(1-p)`, which is not "a"
  coupling but the **maximum** rate any coupling preserving both marginals
  can have. Measured on real data the rate was 0.109, a 3.97x-4.19x
  over-statement of the paired-difference variance -- enough to fail the
  null's own pre-declared adequacy test at the order where adjudication
  happened. Repaired to the measured rate, every band widened by 1.26x-1.68x.

**Both times, fixing the control made the diagnostic look worse.** A
correction to a control that narrows its band deserves suspicion; one that
widens it is the ordinary case.

Two transferable rules follow. First, **when a control has a free parameter
that the real object determines, measure it -- do not choose it for
convenience**; the measurement here was one `np.count_nonzero` over a file
the task already had open. Second, **declare in advance a mechanical test of
the control's own adequacy, with a band-free fallback**, so a blind control
announces itself instead of being discovered afterwards. That test is what
caught the second failure here, before any reviewer did.

## Falsification / narrowing condition

The noise-normalised reading in section (3) rests on `D_RMS` measured from
`n = 2` same-parameter contrasts, one per shard, on the fresh windows only;
applying it across a procedural boundary assumes a transfer that has not
been discharged. **Draw a third and a fourth disjoint same-`T` window per
shard and recompute `D(k)`. If the spread collapses, `D_RMS` is an
outlier-driven `n = 2` artifact, section (3) is wrong, and this entry must
be superseded -- never edited -- by a follow-up ledger archive.** Sections
(1), (2), (4) and (6) do not depend on that measurement and would stand.

An independent parametric construction has corroborated `D_RMS` as a noise
scale at k=5 only (single-alpha SD 0.157 against `D_RMS(5)` = 0.125); at
k >= 10 the real object is 1.9x-2.2x noisier than even a correctly coupled
null, and that gap is unexplained.

## Scope labels

`EMPIRICAL`, toy-scale (HQC decode-path instrument, claim tier TOY, PS-R3
reduced parameters, one defect class, four shards, `N_JACK_BATCHES = 200`),
single campaign, not yet independently replicated outside `GOAL-HQC-001`.
The producing task and both independent reviews resolved to the same model
family, so their agreement is correlated same-model judgement and is not
distinct-model corroboration; what is not correlated is that the two reviews
ran different searches and built different instruments and reached the same
structural facts. **Not a claim about HQC's IND-CCA security, its
decoding-failure rate, or assumptions A17/A5.**
