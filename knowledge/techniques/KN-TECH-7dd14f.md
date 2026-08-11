---
id: KN-TECH-7dd14f
type: technique
title: "Matched-pair vs. between-shard comparison design: the power deficit replicates across four independent measurements, with a corrected required-trials factor and an irreversibility point"
tags: [methodology, experiment-design, matched-pair, between-shard, jackknife, comparison-design, power, hqc, decoding-correlation, real-sampler, replication, pre-registration, toy-scale]
confidence: measured
complexity: "No added asymptotic cost to the estimator itself; the matched-pair design costs one extra decode pass per trial (generate the batch's bits once, decode twice) against the between-shard design's single decode pass, in exchange for a ~5.0x-7.7x reduction in the trial count required to reach a fixed target power at this campaign's load-bearing cell (k=m=17)."
applicability: "Any two-arm real-vs-defected (or treatment-vs-control) comparison over a shared random generation process, where the underlying draw can be routed deterministically through both arms -- i.e. the generation is a pure function of a committed seed/shard index and the decode/measurement step does not mutate its input. Demonstrated here for one nonlinear joint-moment estimator (log2_A_k) over one real decoder (HQC PS-R3's decode_blocks); the underlying argument (pairing removes shared sampling variance that an unpaired quadrature-SE calculation cannot) is general to comparison-design statistics, not specific to this estimator."
source_refs: [EV-HQC-3a0372, EV-HQC-dd85c1, DEC-20260809-186c86, DEC-20260809-46e85c, DEC-20260806-9a4551]
added: 2026-08-11
superseded_by: null
---

## The lesson

A between-shard (unpaired) comparison design can look statistically clean —
committed, reproducible, mechanically sound — while being several-fold less
powered than a matched-pair (paired) design available for free on the same
underlying random draws. This program first observed the gap as a single,
unreplicated measurement (`EV-HQC-dd85c1` O8: one source, one shard, one
uncommitted scratch script, ratio 2.78x at `k=17`). `DEC-20260809-46e85c` held
promotion of this lesson pending a concrete, binding release condition: file
the entry stating whichever framing stage 1's own replication measured,
because "a design-power figure that does not replicate across shards is the
more valuable lesson" if it failed to hold up. **It held up.**

## What replicated, and how

`TASK-20260809-a79e4f` measured the paired-vs-unpaired SE ratio at the
load-bearing cell `k=m=17` four independent ways, against the original
single-source figure:

| measurement | shards | T | ratio (unpaired SE / paired SE) |
|---|---|---|---|
| original (`EV-HQC-dd85c1` O8) | 424242 | 5,000 | 2.78x |
| this batch, shard 5000 | 5000 | 5,000 | 2.902x |
| this batch, shard 6000 | 6000 | 5,000 | 3.224x |
| this batch, stage-1 pooled | 5000+6000 | 10,000 | 3.117x |
| this batch, stage-2 pooled | 8000-8003 | 20,000 | 3.769x |

All four new measurements land within the same order of magnitude and
direction as the original 2.78x. Both an independent Validator (own
from-scratch driver, different chunk size) and an independent Red Team
(full re-execution of the actual committed script on a third machine/OS/
Python/numpy combination, plus a from-scratch jackknife reimplementation
not calling any of the producer's code) reproduced every one of these
figures exactly. **This is a genuine, non-exact-digit replication, and
should be read that way**: a ratio of two quantities each carrying its own
sampling variance should *not* reproduce to the literal decimal, and a
match that close would itself be the suspicious outcome. The general
finding — matched-pair design gives several-fold tighter SEs than a
between-shard design on this estimator, robustly across four independent
samples now, not one — is corroborated by data an executor other than the
original probe's author generated.

## The corrected required-trials factor

The campaign's first pass at converting this SE-ratio into a required-trials
factor overstated it: a deliverable's "roughly 5-18x" headline crossed
different `delta` and `z` values between the matched-pair and between-shard
cells being compared (dividing the smallest matched-pair required-trials
cell by the *largest* between-shard cell). At fixed `delta` and fixed `z`,
the required-trials ratio is exactly `(SE_unpaired / SE_paired)^2`,
independent of both: **the defensible, like-for-like figure at the
load-bearing cell `k=m=17` is 5.0x to 7.7x**, not 5-18x. The direction is
unchanged and remains substantial; only the top-end magnitude was
overstated, by about 2.4x (`DEC-20260809-46e85c` O6).

## The irreversibility point

A between-shard design draws its two arms from disjoint PRNG streams keyed
per shard index (in this program's harness: `sha_key(ps_id, "T", shard,
MASTER_SEED)`). Once trials are drawn this way, **no matched pair can be
recovered after the fact** — not by better serialization, not by any
post-hoc reanalysis of the committed data. This program verified this
concretely: a matched-pair "reanalysis" of an already-collected
between-shard pilot dataset was found structurally impossible on the
pilot's own committed data for exactly this reason (`EV-HQC-dd85c1` O2).
**The choice between a paired and an unpaired design is therefore made
once, before the first trial is drawn — not a parameter that can be
revised after seeing early results, and not a gap that better data
retention closes.** Where a matched-pair design is available at comparable
or lower cost (as it is here: one extra decode pass per trial, sharing one
generation pass), it should be the default, not a fallback reached only
after an underpowered between-shard result forces a redesign.

## What this lesson does *not* yet license — a caveat carried explicitly

This SAME batch's data, at the SAME cell, independently falsified a
DIFFERENT and separable assumption on its own pre-registered terms: the
campaign's required-T derivation assumes the matched-pair jackknife SE
scales as `1/sqrt(T)` (a fitted exponent of 0.5), and the measured exponent
(0.3186, independently reproduced exactly by two reviewers) falls outside
the pre-registered `[0.4, 0.6]` consistency band (`DEC-20260809-186c86`).
**The corrected 5.0x-7.7x power-deficit factor above is a validated
statement about the SE RATIO at the trial counts actually measured
(T=5,000-20,000 per arm), not yet a validated statement about how that
factor extrapolates to a full-scale required-T figure**, because the
scaling relationship it would need to be plugged into is itself now an open
question pending a dedicated scaling-characterization task. Treat the two
findings as separable: the paired-design-is-more-powerful lesson (this
entry) replicates cleanly; the specific 1/sqrt(T) scaling law it was
originally sized against does not, on this batch's own first empirical
test of it.

## Falsification

A future two-arm comparison over a shared generation process on this or a
similarly-structured estimator, where the matched-pair and between-shard
SEs at the same trial count are statistically indistinguishable (ratio ≈
1, within sampling noise), would refute the general applicability claim
above — it would mean the within-pair correlation this design exploits is
specific to this estimator/decoder combination rather than a property of
pairing shared draws more generally.

## Scope labels

`TOY, HARD CEILING`. Measured only for PS-R3 (`n=7187, n_e=56, N=7168,
m=17`), the V3 (last-block-window-read-early) defect class, the
`decode_blocks` injection point, and the `log2_A_k` joint-moment
estimator, at T=5,000-20,000 trials per arm. This is a
design-methodology lesson about comparison statistics under this program's
harness, generalizable within that scope; it is **not** a statement about
HQC's IND-CCA security, its decoding-failure rate, assumption A17 or A5,
or any standardized parameter set, and no such extrapolation is licensed.
