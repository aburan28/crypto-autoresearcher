---
id: KN-FIND-001e68
type: internal_finding
title: "A closed-form lattice-cost estimator's primal-attack cost readout can exhibit demonstrated, reproducible, non-smooth/chaotic block-size behavior in the severely sample-starved regime m << n, with no validity-range guard warning against it -- a single headline beta figure in this regime cannot be trusted as a stable measurement without an m-sensitivity control"
tags: [instrument-design, lattice-estimator, primal_bdd, RC.MATZOV, sample-starved, reduced-dimension, m-sensitivity, chaos, negative-result, cost-model, ml-kem, medium-tier]
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
  instruments built on fpylll direct lattice reduction. This entry is about a
  completely different lane and a different tool: the reliability of a
  closed-form lattice-cost ESTIMATOR readout (primal_bdd/RC.MATZOV in the
  pinned sage-free lattice-estimator harness), not a reduction instrument, and
  a different failure mode entirely (numerical/optimizer instability at a
  reduced sample count, not a code-independence or detection-threshold
  confound). `internal_refs` carries LEDGER records only, matching the shape
  prior entries in this goal use; the sibling relationship to
  KN-FIND-5e9728 (this same batch's companion finding) is likewise recorded
  here by prose, not by internal_refs.
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-b13873/probes/m_sensitivity_sweep.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-b13873/probes/m_sensitivity_sweep_fine.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-b13873/probes/m_sensitivity_sweep.output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/probes/probe1_m2_m_sweep.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/probes/probe5_single_sample_discontinuity.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/probes/probe5_single_sample_discontinuity_output.json
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-b13873/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/reviews/TASK-20260814-c09076/red_team_report.md
added: '2026-08-14'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: DERIVATION for the mechanism, MEDIUM for the specific FIPS 203
measurement it was found in.** Not toy, not crypto-tier: nothing here is a
measured attack cost or a revision of any published security estimate.

**THIS ENTRY DOES NOT SAY THE UNDERLYING QUESTION `H-MLKEM-11aabf` ASKED IS
WRONG.** The qualitative direction (a genuine dimension reduction that drops
noisy coordinates cannot make an attacker's job harder on the retained
coordinates) is not in dispute. This entry is about why the *specific
magnitude* a closed-form cost-model estimator reports for such a reduction
cannot be trusted without a dedicated control, and how to recognize that
failure mode in advance next time.

The finding, in one sentence:

> A closed-form lattice-cost estimator's primal-attack readout (here:
> `primal_bdd` under `RC.MATZOV`) can be **demonstrably non-smooth and
> reproducibly chaotic** in the severely sample-starved regime `m << n`, with
> **no validity-range guard anywhere in its own code** to warn a caller away
> from it -- so a single headline `beta` figure built on a reduced-dimension
> construction is not, by itself, evidence of a stable security-relevant
> effect.

## 1. What was measured

`GOAL-MLKEM-005` `BATCH-a5b13c` tested `H-MLKEM-11aabf`'s C2 conjunct: whether
an honest, class-aware ciphertext-side noise model (three declared
constructions, M0/M1/M2) leaves the ciphertext-side lattice materially worse
positioned than the key-side lattice at real FIPS 203 parameters. M2's own
construction retains only the `767/3329` singleton-class coordinates at
ML-KEM-1024 and drops every doublet coordinate, producing a reduced sample
count `m = 236` against the base scheme object's own `m = n = 1024` (roughly
23% of the original). The lead producer called `primal_bdd(..., red_cost_
model=RC.MATZOV)` at this construction and got `beta(M2) = 617`, 255 bits
below `beta(M0) = beta(M1) = 872` -- directionally consistent with the
hypothesis's own prediction (M2 should read lower than M0), but roughly two
orders of magnitude beyond its stated 2-4 bit `minimum_effect`. The producer's
own writeup explicitly declined to conclude whether this magnitude was a
genuine effect or an estimator artifact.

## 2. How the confound was diagnosed -- two methods, converging within a single batch

Both reviews, working independently and via **genuinely different,
non-overlapping methods**, built an `m`-sensitivity sweep bracketing the
producer's own `reduced_m = 236` and found the same picture:

- **A coarse-then-fine sweep** (the Validator): from `m = 1024` down to
  `m = 220`, `beta` moves smoothly and monotonically down from 855 to roughly
  350, then becomes non-monotone and chaotic below `m ~ 350` (966 at `m=300`,
  876 at `m=260`, 617 at `m=236`, 759 at `m=220`) before total optimizer
  failure sets in.
- **Five separate probes including a single-unit-step scan** (the Red Team):
  a 34-point coarse sweep (`m` 10 to 3000) plus a fine, step-2 scan around the
  boundary the coarse sweep found, plus a dedicated single-unit-step scan
  (`m = 233..239`) isolating the sharpest possible signal.

**Both independently found the identical sharp result**: `beta(m=236) = 617`,
`beta(m=237) = 908` (or 905, depending on the exact construction variant
tested) -- a swing of roughly 290 core-SVP bits for a change of exactly one
sample out of 1024 (0.1% of `n`). Both confirmed this is fully deterministic
and reproducible (re-run five times at `m=236`, the value never varies), not
measurement noise. Below roughly `m = 218-220`, `primal_bdd` itself returns no
finite-cost configuration at all (`rop = +inf`) -- total optimizer failure,
not merely a small or unreliable number. Above roughly `m = 240-250`, the
function becomes smooth and monotone again, eventually saturating at the
base-object value (855) as `m` approaches 1024.

**The mechanism was independently source-verified, not merely observed.**
The estimator's own `primal_usvp`/`primal_bdd` call path applies a
Bai-Galbraith embedding-enlargement construction that floors its internal
`d`-optimizer's search grid at `d >= n` regardless of how small `m` is,
producing a cramped, locally non-convex search landscape whenever `m << n` --
exactly the shape that would produce total failure below a threshold, a
chaotic band immediately above it, and smoothing out once the search range is
no longer degenerate. A direct grep of the estimator's own source confirms no
`InsufficientSamplesError`-style validity guard exists for this specific
attack path tied to `m` relative to `n` (unlike this same estimator's
`lwe_dual.py`, `lwe_guess.py`, and `lwe_bkw.py` modules, which do raise such a
guard for their own success conditions) -- the instrument silently returns a
number from deep inside the chaotic band with no warning to the caller.

## 3. Why this generalizes beyond this goal, and beyond the prior six findings' family

The general shape: any research use of this or a structurally similar
closed-form lattice-cost estimator that constructs a reduced-dimension
(sample-starved, `m << n`) instance and cites its headline `beta`/cost figure
must first run and report an `m`-sensitivity/smoothness control bracketing
the constructed `m`, because a single headline number in this regime cannot
be trusted as a stable measurement of the underlying object without one --
**the magnitude, not merely the direction, of an effect can be dominated by
instrument artifact.** This is a general lesson about closed-form
lattice-cost-estimator reliability under reduced-dimension constructions,
directly relevant to any future hypothesis, in this campaign or another,
proposing to drop or reduce samples and read a `beta` figure off this same
class of estimator. It is unrelated in mechanism, tool, and failure mode to
this goal's six prior findings, all of which concern a direct fpylll
reduction instrument's own two-route comparison or mutation-testing design,
not a closed-form cost-model readout's own numerical behavior.

## 5. What remains open

Whether the pinned estimator's non-smooth `m << n` behavior is specific to
this particular construction (Kyber1024's own base object, this specific
`Xe`/`Xs` choice) or a more general property of the Bai-Galbraith embedding
trick at other `n`/`m` ratios and other base schemes remains untested; neither
review built a control at a different base scheme or dimension within
budget. A concrete, cheap follow-up (~5-10 minutes, same instrument, no new
dependency) is named by the Red Team but not commissioned by this finding.
