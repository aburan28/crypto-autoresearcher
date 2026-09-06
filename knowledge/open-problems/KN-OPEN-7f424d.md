---
id: KN-OPEN-7f424d
type: open_problem
title: Does an interleaved, modulus-reduced combination rule exist for a second deck pair in H-CREP-001's complete-chart intersection system?
tags: [ecdlp, h-crep-001, exp-crep-001, telescoping, resultant, remainder-tree, p1553, decomposition]
confidence: unverified
status: open
source_refs: [DEC-20260830-6f28e0, DEC-20260830-04169a]
added: 2026-08-30
superseded_by: KN-OPEN-73f0f4
---

## Statement

Across all eight frozen `EXP-CREP-001` routes for `H-CREP-001`'s P1553
`r_R mod g_I` remainder-transducer problem, exactly one deck pair (decks 0
and 1) has a dedicated compact pairwise combination object: the
`pair-product generator`, an ordered pair over `decks[0] x decks[1]`
(size B^2), with a genuinely additive/telescoping combination rule
(label-matching set union, cost `O(|S1|+|S2|)`). This object alone never
determines the target quantity `z_R`.

The step that does fold in the remaining information -- `build_chart_index`,
which bundles decks 2, 3, and 4's raw occurrence lists -- has **no stated
pairwise decomposition anywhere in the frozen record**. It is declared only
as a whole-set cost, and the subsequent `materialize_resultant_coefficients`
step is a single, non-decomposed atomic edge (identical across every
non-oracle route via the shared `build_expansion_route()` builder) at
cost/output exponent 3. This absent decomposition is what mechanically
forces the verifier's own max-aggregation rule (`check_representation.py`'s
`check_V6`) to a Theta(B^3) online-cost floor for all eight routes,
independently verified line-by-line against the source in
`DEC-20260830-6f28e0`.

## The open question

**Can an interleaved, `g_I`-reduced combination rule be constructed for a
second deck pair** (for example decks 2 and 3), analogous in kind to the
existing decks-0/1 pair-product generator but folding in the remaining
strata, **and if so, is its combination cost additive/telescoping (like
the decks-0/1 case) or multiplicative** (a Bezout-type growth, which would
not help)?

This is genuinely undetermined by anything currently in `H-CREP-001.yaml`
or the eight frozen `EXP-CREP-001` route packages -- not because it was
tried and failed, but because no route in the frozen set ever attempts a
decomposition beyond the one already-present decks-0/1 pairing. The
question is precisely the residual gap named in `TASK-20260830-e30c67`'s
`derivation-report.yaml` (`named_missing_specification`,
`forward_guidance_open_directions`) and confirmed independently absent from
the source by the archiving Coordinator in `DEC-20260830-6f28e0`.

## Why it matters

- **If such a rule exists and telescopes**: it would be the first
  candidate public constructor for `r_R mod g_I` this goal has found since
  opening -- a genuine typed trigger, dischargeable against the amended
  pre-admission gate (`preadmission_gate_g2_g8_wording_amendment_20260830`
  on `ledger/goals/GOAL-ECDLP-001/goal.yaml`).
- **If it provably cannot exist** (with a derivation as rigorous as
  `DEC-20260830-6f28e0`'s, not an assertion): it would extend the
  code-verified obstruction from "the eight as-built routes" to a genuine
  structural argument about the complete-chart intersection system itself,
  which no prior round (including the immediately preceding gate/framing
  review's failed dichotomy attempt) has achieved.
- **If it is simply unresolved after a genuine attempt**: the honest
  outcome is a second `partial_derivation_gap_named` result, still useful
  for narrowing where future effort should go.

## What would resolve this

A bounded, zero-to-low-compute, non-batch analytical task, following the
same method as `TASK-20260830-e30c67`: write down the frozen instance
model's decks-2/3 occurrence structure explicitly (as `generate_instances.py`
defines it), attempt to construct an interleaved combination rule by hand
on a small concrete case (e.g. `B=2`), and check a degenerate/boundary case
before generalizing. This is the concrete next action recorded in
`ledger/goals/GOAL-ECDLP-001/goal.yaml`'s `next_action` as of 2026-08-30.

## Provenance

- `coordination/goals/GOAL-ECDLP-001/proposals/B71-PAIRPRODUCT-TELESCOPING-DERIVATION-20260830-e30c67/tasks/TASK-20260830-e30c67/derivation-report.yaml` (kb — originating derivation)
- `ledger/decisions/DEC-20260830-6f28e0.yaml` (kb — independent source-code verification and scope correction)
- `ledger/decisions/DEC-20260830-04169a.yaml` (kb — prior gate/framing review that named the need for this derivation)
- `experiments/EXP-CREP-001/instances/generate_instances.py`, `experiments/EXP-CREP-001/verifier/check_representation.py`, `experiments/EXP-CREP-001/packages/build_packages.py` (retrieved — directly opened and read by the archiving Coordinator)
