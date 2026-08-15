---
id: KN-TECH-00f082
type: technique
title: "Matched-pair vs. between-shard SE ratio replicates within a fixed shard pool, not shown scale-invariant across a shard change -- and why a 3-point sizing sweep cannot tell the difference"
tags: [matched-pair-design, statistical-power, standard-error-scaling, shard-identity-confound, sizing-sweep, extrapolation, hqc, decode-blocks, methodology]
confidence: reported
complexity: not applicable; this record states a measurement-methodology caution, not a cost
applicability: "any campaign that measures a matched-pair-vs-between-shard (or generally paired-vs-unpaired) standard-error advantage at one (trial-count, shard) point and wants to extrapolate a required-trial-count formula to a much larger trial count via an assumed 1/sqrt(T) scaling law."
source_refs: [EV-HQC-3a0372, EV-HQC-dd85c1, DEC-20260809-186c86, DEC-20260809-46e85c, TASK-20260809-a79e4f, TASK-20260809-603dc5, TASK-20260809-47a5ec]
added: 2026-08-14
superseded_by: null
---

## What this record is

GOAL-HQC-001's matched-pair instrument at the V3/decode_blocks injection
point measured, then independently re-derived twice (Validator, Red Team),
a standard-error advantage of the matched-pair design over the between-shard
design that the campaign had used to size later experiments. This entry
states what replicated, what did not, and the specific reason a 3-point
sizing sweep cannot distinguish the two.

## (1) The required-trials factor replicates like-for-like

At k=m=17, the matched-pair design's paired/unpaired SE ratio measured
3.15x (pooled, stage 1, shards 5000/6000) and 2.90x-3.22x per-shard,
translating to a required-trials factor of roughly 7.7x-10.4x fewer trials
than the between-shard design needs for the same power. This corroborates
`EV-HQC-dd85c1` O6's corrected 7.74x figure, and does so as an independent
measurement on two different shards than the original probe -- not a
re-derivation of the same numbers.

## (2) The irreversibility point

A between-shard design draws its two arms from disjoint PRNG shards. Once
drawn, it cannot be re-paired after the fact into a matched-pair design
(`EV-HQC-dd85c1` O2). The choice between the two designs is therefore made
once, before any data exists -- there is no cheap fallback if the wrong one
is picked first.

## (3) The sharper, newly-measured lesson: the ratio is not shown scale-invariant across a shard change

The same SE-vs-trial-count scaling law that any required-T derivation
extrapolates through was fit at three points: T=5,000 (mean per shard,
shards 5000/6000), T=10,000 (pooled, same two shards), and T=20,000 (pooled,
fresh shards 8001/8002). The fitted exponent across all three, alpha=1.470,
falls sharply outside the physically expected 1/sqrt(T) band of [0.4, 0.6].

Decomposed into local (consecutive-point) exponents rather than one 3-point
fit, the picture sharpens: the 5,000->10,000 step -- same shards, zero new
entropy -- gives a local exponent of 0.507, essentially exact 1/sqrt(T)
consistency. The entire anomaly is concentrated in the 10,000->20,000 step,
which simultaneously introduces two brand-new shards. This is a genuine,
currently unresolved confound: **a sizing sweep that changes shard identity
at every trial-count point cannot separate "the 1/sqrt(T) scaling law is
wrong" from "this estimator's variance is shard-heterogeneous."** Both
explanations fit the same three points equally well.

The ratio and its scaling law are shown to hold, and hold cleanly, within a
fixed/similar shard pool. They have **not** been shown to hold -- and the
data show active evidence against holding -- once shard identity changes
alongside trial count.

## General lesson

Never extrapolate a design-power ratio (or any paired-vs-unpaired SE
advantage) measured at one (trial-count, shard) pair to size a much larger
experiment via an assumed scaling law, unless that law has itself been
validated in the regime being extrapolated into, with shard identity held
fixed across the validating sweep. A sizing sweep that varies both the
quantity you are trying to characterize (trial count) and a plausible
nuisance variable (shard identity) at the same time cannot attribute an
observed deviation to either one alone.

## Falsification / narrowing condition

`GOAL-HQC-001`'s own named follow-up -- repeating the T=20,000 matched-pair
extension on shards 5000 and 6000 themselves (fresh, disjoint trial ranges,
not a reconstruction) -- would resolve this directly: if the resulting SE
tracks 1/sqrt(T) from the existing (5,000; 10,000) points on those same
shards, the alpha=1.47 anomaly is a property of shards 8001/8002
specifically and this entry's scope-limited claim stands as filed. If it
collapses the same way the fresh-shard step did, the 1/sqrt(T) refutation is
real and general, and this entry must be superseded (never edited) by a
follow-up ledger archive.

## Scope labels

`EMPIRICAL`, toy-scale (HQC decode-path instrument, claim tier TOY), single
campaign, not yet independently replicated outside GOAL-HQC-001. Not a claim
about HQC's IND-CCA security, decoding-failure rate, or assumption A17.
