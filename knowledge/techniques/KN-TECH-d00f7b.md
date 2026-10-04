---
id: KN-TECH-d00f7b
type: technique
title: "Small-sample undercoverage of stratified percentile bootstrap intervals at five units per stratum"
tags: [bootstrap, percentile-bootstrap, stratified-bootstrap, interval-coverage, undercoverage, small-sample, calibration, slope-fit, methodology, toy-scale, pfdr]
confidence: reported
complexity: >-
  Not a cost claim. A calibration caution for an interval procedure; the
  operative quantity is the realised coverage of a nominal 95% interval when
  each stratum holds five resampled units.
applicability: >-
  Any reading of a nominal 95% stratified percentile bootstrap interval
  (units resampled with replacement within each stratum) on a design with
  five units per stratum, in particular the slope, exponent, paired-delta
  and curve-index bootstraps of EXP-PFDR-1b78f7 and EXP-PFDR-7c8bf2 (five
  curves per rung, 7 or 11 rungs), and any "interval excludes" or "interval
  above 0" reading made from them.
source_refs: [EV-PFDR-1faf10, EV-PFDR-cf6ee5, DEC-20260929-bbb3a9, DEC-20260929-1b779a, TASK-20260929-accb8e, TASK-20260929-69b7c5, EXP-PFDR-1b78f7, EXP-PFDR-7c8bf2]
proof_status: empirical_only
proof_status_note: >-
  Mixed basis, stated at the weaker level. The standard-error deflation
  factor sqrt((n-1)/n) is a derivation (validator TASK-20260929-accb8e J5 c,
  labelled derivation). The coverage figures are empirical: synthetic
  calibrations measured by two reviews.
proof_refs:
  - coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e/calibration/coverage-tables.yaml
  - coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e/validation-report.yaml
  - coordination/review/pfdr-7c8bf2-20260929/reviews/TASK-20260929-69b7c5/red-team-report.yaml
added: '2026-10-01'
superseded_by: null
---

# Small-sample undercoverage of stratified percentile bootstrap intervals at five units per stratum

## What this record is

A calibration caution about an interval procedure, produced by this program's own reviews. It is not a literature claim and not a finding about any hypothesis. Its basis, as recorded in DEC-20260929-bbb3a9 (knowledge_promotion.pending), is two independent measurements plus a derivation:

- The EXP-PFDR-7c8bf2 Stage 0 red team (TASK-20260929-69b7c5, joint J4; report sealed at dc61c5e1e) measured it first.
- The EXP-PFDR-1b78f7 validator (TASK-20260929-accb8e, joint J5) re-measured it with its own code, blind to the Stage 0 material. This meets the review plan's condition that a KN-TECH is "considered only if J5 independently confirms it".

The candidate was first named in DEC-20260929-1b779a NA-5, which deferred promotion until an independent check. DEC-20260929-bbb3a9 recorded the entry as warranted and pending a user decision on writing Markdown (NA-11). It was written on the user decision of 2026-10-01 and archived by TASK-20260929-4ab45d.

## Statement and derivation

Resampling n units with replacement within a stratum deflates the bootstrap standard error by sqrt((n-1)/n), which is 0.894 at n = 5. A nominal 95% percentile interval on a linear statistic then behaves like +-1.75 SE, with predicted coverage 0.909-0.920 (validator J5 c; labelled derivation).

EV-PFDR-1faf10 OBS-9 states the predicted range as 0.909-0.913. The 0.909-0.920 range above is the one recorded in DEC-20260929-bbb3a9's pending entry. Neither range was recomputed for this entry.

## Measured coverage of nominal 95% intervals

The values are as recorded in DEC-20260929-bbb3a9's pending entry. All four rows are the validator's measurements (TASK-20260929-accb8e J5; EV-PFDR-1faf10 OBS-9; calibration/coverage-tables.yaml).

| procedure | measured coverage |
|---|---|
| stats.bootstrap_slope (11x5 and 7x5 designs, Gaussian and t3) | 0.887-0.909 |
| stats.fit_exponent | 0.913-0.916 |
| paired delta bootstrap | 0.903-0.909 |
| ratio-and-log curve-index bootstrap (A2) | 0.864-0.875, with a one-sided false "above 0" rate of 0.070 against 0.025 |

The Stage 0 red team's earlier measurement, on the EXP-PFDR-7c8bf2 design, is in its sealed report (coordination/review/pfdr-7c8bf2-20260929/reviews/TASK-20260929-69b7c5/red-team-report.yaml, joint J4) and in EV-PFDR-cf6ee5. Its figures are not restated here, because the pending entry this record is written from does not carry them.

## Remedies

1. Monte Carlo error, which is a separate issue: seed-averaged bootstraps or >= 20000 replicates.
2. Coverage: an n/(n-1) variance correction, or t-based intervals.
3. Calibration by simulation at the design's n before any "interval excludes" reading.

DEC-20260929-bbb3a9 NA-5 (j) carries these into the design of the relation-level census: seed-averaged or >= 20000-replicate bootstraps, intervals calibrated at the design's n, and a design-evaluated A2 null slope in place of "interval above 0".

## Scope and limits

- Toy scale. The figures are synthetic calibrations of the interval procedures used by two toy-tier experiments, EXP-PFDR-1b78f7 and EXP-PFDR-7c8bf2 (log2 p <= 32). They are not observations of an engine, and no transfer to other designs or scales is asserted.
- This bootstrap procedure: the frozen stratified percentile bootstrap of those experiments and the variants in the table, on synthetic designs matching them (five curves per rung, 7 or 11 rungs). The absolute tail figures depend on residual scale.
- Five units per stratum. The derivation is stated for general n; the coverage figures are measured only at n = 5.
- Session independence of the reviews is attested; model independence is not claimed (DEC-20260929-bbb3a9 limitations).
- Bearing on the source experiment: it bounds the wording of every interval statement made on five units per rung in EXP-PFDR-1b78f7, and no decision in that run set flips because of it (EV-PFDR-1faf10 INF-7).
