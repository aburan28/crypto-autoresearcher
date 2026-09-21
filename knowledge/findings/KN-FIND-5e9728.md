---
id: KN-FIND-5e9728
type: internal_finding
title: "Feeding a variance-only cost instrument a single class-weighted mixture distribution for a per-coordinate-heterogeneous noise construction is mathematically forced to equal the population-average baseline it was meant to be tested against -- a protocol-design degeneracy that collapses the intended heterogeneous test before any data is measured, for any partition and any per-class distributions"
tags: [instrument-design, protocol-design, mixture-distributions, law-of-total-probability, variance-only-cost-model, noise-heterogeneity, negative-result, lattice-estimator, ml-kem, medium-tier]
confidence: derivation_plus_two_independent_reviews_via_genuinely_different_methods_on_one_model
evidence_level: derivation_plus_medium_tier_measurement
source_refs: [BATCH-a5b13c, TASK-20260814-d13724, TASK-20260814-c87a24, TASK-20260814-b13873, TASK-20260814-c09076]
internal_refs: [EV-MLKEM-159715, DEC-20260814-b0a095]
sibling_findings_narrowed: []
sibling_findings_note: >-
  This entry stands beside, and narrows neither, this goal's six existing
  KN-FIND-* entries (KN-FIND-7d098b, KN-FIND-9d44b4, KN-FIND-9b5df0,
  KN-FIND-7de6b6, KN-FIND-d29ece, KN-FIND-7ffdd0), all of which concern the
  hkz/HKZ-independence lineage's own two-route comparison/mutation-testing
  instruments built on fpylll direct lattice reduction -- a different lane and
  a different failure mode entirely (code-independence and detection-threshold
  confounds, not a mixture-distribution identity). It also stands beside, and
  narrows neither, KN-FIND-001e68 (this same batch's companion finding, about
  the reliability of the same estimator's numerical behavior at reduced sample
  counts) -- the two findings concern two independent, non-overlapping
  properties of the same pinned instrument, discovered in the same batch but
  logically unrelated to each other. `internal_refs` carries LEDGER records
  only, matching the shape prior entries in this goal use.
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-b13873/probes/independent_stage_b_readout.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-b13873/probes/independent_stage_b_readout.output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/probes/probe3_independent_census_and_m0m1_check.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/probes/probe3_independent_census_and_m0m1_check_output.json
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-b13873/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/red_team_report.md
added: '2026-08-14'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: DERIVATION for the mathematical argument, MEDIUM for the
specific FIPS 203 measurement it was found in.** Not toy, not crypto-tier.

**THIS ENTRY DOES NOT SAY WHETHER A PUBLIC PER-COORDINATE CLASS LABEL
ACTUALLY MATTERS TO ATTACKER DIFFICULTY.** `H-MLKEM-11aabf`'s own mechanism --
that the singleton/doublet label the census produces justifies a more honest,
per-coordinate noise model than the naive uniform treatment -- is not
addressed or refuted by this entry. This entry is about why one *specific way*
of testing that mechanism against a variance-only cost instrument is
guaranteed, by construction, never to distinguish it from the naive baseline,
regardless of how carefully it is executed.

The finding, in one sentence:

> When a heterogeneous-noise construction is fed to an attack/cost instrument
> as **one combined, class-weighted mixture distribution**, and the classes
> being mixed **partition the full population**, the resulting distribution is
> mathematically **forced to equal** the population-average distribution the
> naive baseline already uses -- so the two constructions can never be
> distinguished by such an instrument, no matter what the per-class
> distributions actually are.

## 1. What was measured

`GOAL-MLKEM-005` `BATCH-a5b13c` tested three declared ciphertext-side noise
models under `H-MLKEM-11aabf`'s C2 conjunct: M0 (the standard/legacy single
marginal, applied uniformly), M1 (a per-class reweighted mixture, intended to
be a more honest, class-aware treatment), and M2 (a reduced-dimension
retain-only-clean-samples construction). PREREG-7's own frozen text specified
M1 precisely: build each class's own compression-error distribution, then
"the estimator is fed a single effective distribution constructed as this
properly class-weighted mixture." The lead producer built exactly this and
found `beta(M0) = beta(M1)` exactly, bit-for-bit, at every one of the three
tested FIPS 203 parameter sets.

## 2. How the identity was diagnosed -- two methods, converging within a single batch

Both reviews, working independently and via **genuinely different,
non-overlapping methods** (a symbolic probability derivation plus a
from-scratch numerical re-implementation, in each case never importing the
producer's own code), confirmed and explained the identity:

**Symbolically**: for independent random variables `Xe` (the base CBD noise)
and a mixture `D` of class-conditional distributions `D_1, ..., D_k` with
weights `p_1, ..., p_k`, the law of total probability gives
`Law(Xe + D) = sum_i p_i * Law(Xe + D_i)` -- a direct consequence of summing
an independent variable into each branch of a mixture, requiring no further
assumption about what the per-class distributions actually are. Because the
fibre-size classes M1 conditions on **partition** the full population exactly,
M0's own population-average distribution *is*, by definition, that same
law-of-total-probability mixture over those same classes. Given PREREG-7's own
instruction to feed the estimator "a single effective distribution," M1 cannot
produce a number different from M0 -- this is forced by the specification
itself, not an artifact of how carefully it was executed.

**Numerically**: both reviews independently built the exact per-class pmf and
the exact `CBD(eta1)` pmf via binomial convolution (not variance shortcuts)
and confirmed the total variance is bit-identical between M0 and M1 at every
parameter set -- and, crucially, **at two structurally different partitions of
the same population** (`d_u=10`'s 767×3/257×4 split at ML-KEM-512/768, and
`d_u=11`'s 767×1/1281×2 split at ML-KEM-1024). The identity held both times,
which is exactly what the algebraic argument predicts and a coincidence-based
account would not.

**The practical bite of the argument depends on the instrument's own cost
path being moment-only.** Both reviews confirmed (one by direct source grep,
the other by spot-checking it functionally with a different noise-object
constructor) that the pinned estimator's `primal_bdd` call graph consumes only
`Xe.stddev` -- never a full probability mass function or a higher moment --
for this cost path. An estimator that consumed the full per-coordinate pmf
might, in principle, distinguish M0 from M1 even though their *marginal*
mixture is identical; this specific, pinned, variance-only instrument cannot.

## 3. Why this generalizes beyond this goal, and beyond the prior six findings' family

The general shape: when a hypothesis-testing protocol specifies a "per-class
noise reweighting" or heterogeneous-noise construction as *partition the
population by a public/known label, build each class's own distribution, then
feed the instrument one combined effective distribution*, that construction is
**mathematically guaranteed** to collapse to the population-average baseline
whenever the classes partition the full population and the instrument's own
noise-consuming code path is moment-only -- regardless of class sizes,
probabilities, or per-class distributions, and regardless of the specific
partition. The resulting agreement between the "heterogeneous" and "baseline"
readouts is therefore not evidence that heterogeneity does not matter; it is a
design artifact of how the heterogeneous model was fed to the instrument. To
actually test whether a public per-coordinate class label matters to attacker
difficulty against a moment-only cost instrument, the construction must either
change *which samples/equations* the instrument sees (a genuine dimension
reduction or selective retention, not a re-mixed marginal) or must use or
build an instrument that consumes more than the first two moments of a
per-coordinate-varying noise model. This is a general protocol-design lesson
for any future hypothesis, in this campaign or another, proposing to test
per-coordinate or per-class noise heterogeneity against a moment-only cost
instrument by mixing then feeding one combined distribution -- directly
actionable and preventable in a way none of this goal's prior findings
describe.

## 4. What remains open

Whether a genuinely different attack construction (e.g. a row-rescaling or
whitening technique that treats coordinates heterogeneously rather than
mixing them into one marginal) or an instrument extension consuming more than
the first two moments would show a material, testable M1-style effect remains
fully open. Neither is commissioned by this finding; both are named as
licensed candidates for a future, separately-specified protocol.
