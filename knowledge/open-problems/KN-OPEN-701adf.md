---
id: KN-OPEN-701adf
type: open_problem
title: H-CREP-001's r_R has a candidate mathematical definition under two competing readings, but neither reading supplies a construction meeting H-CREP-001's own exponent caps
tags: [ecdlp, h-crep-001, exp-crep-001, p1553, resultant, specification-gap, red-team, rt103, construction-cost]
confidence: unverified
status: open
source_refs: [KN-OPEN-de67f0, DEC-20260830-d7b846]
added: 2026-08-30
superseded_by: null
---

## Statement

A Coordinator-authored draft (`TASK-20260830-351be7`) supplied the first
self-contained candidate mathematical definition of `H-CREP-001`'s `r_R`
since `RT103-O1`/`RT103-C1` was raised on 2026-07-22, choosing the
two-pairs/`Theta(B^4)` reading over the corpus-declared-matching
one-pair/`Theta(B^2)` reading. Independent validator (`TASK-20260830-495939`)
and red-team (`TASK-20260830-031380`) review found genuine, unconditional
progress on part of `RT103-C1` (`g_I`, `z_R`, occurrence maps,
multiplicities, and the forward direction of the support biconditional are
all independently re-verified, not restated) but did NOT discharge
`RT103-C1` as a whole: the reading choice survives on only two of three
claimed independent textual legs (red-team's proves-too-much Object 3
shows the third leg equally supports the rejected reading), the converse
direction of the biconditional remains conditional on an unformalized
heuristic and verified on only one instance, and a new, more decisive
obstruction (OBJ-5) was surfaced: **neither reading's `r_R`, if
materialized directly, meets `H-CREP-001`'s own declared exponent caps**
(`fresh_target_online_exponent_cap_in_B: 1.25`,
`preprocessing_exponent_cap_in_B: 2.25`) -- direct materialization costs at
least `B^2` (one-pair) or `B^4` (two-pairs) field elements online, far over
cap under either reading.

## Why this supersedes KN-OPEN-de67f0

`KN-OPEN-de67f0` asked whether a self-contained definition of `r_R` could
be written down at all. That question is now substantially answered: yes,
at least two internally-consistent candidate definitions exist, and one
has survived a full adversarial review round on its definitional content.
The open question has shifted: it is no longer primarily "can `r_R` be
defined" but "can `r_R` (or `z_R` directly) be *constructed* within
`H-CREP-001`'s own budget" -- a question orthogonal to which reading is
textually correct, since both readings currently fail it by a wide margin.

## The open question, precisely

Does a compact or implicit representation of `z_R = gcd(g_I, r_R)` exist --
avoiding full materialization of the degree-`B^2` or degree-`B^4`
intermediate object `r_R` -- that fits within `H-CREP-001`'s stated
exponent caps, under EITHER the one-pair or two-pairs reading? If the
honest answer is no under both readings, this is itself a significant
finding about `H-CREP-001`'s construction obligation, independent of ever
resolving the reading ambiguity.

Separately, and lower priority per `DEC-20260830-d7b846`'s `next_actions`:
is the one-pair-vs-two-pairs reading ambiguity resolvable at all from the
existing two-sentence source, or is it genuine textual underdetermination
requiring an external specification? Two derivation rounds, one drafting
round, and one adversarial review round have now engaged this fragment;
further inference from the identical source is judged unlikely to add
information (`DEC-20260830-d7b846`).

## What would resolve this

A bounded, non-batch, zero-experiment Coordinator-authored task assessing
whether a compact/implicit representation of `z_R` can be constructed
within cap under either reading, submitted for independent review before
further work treats `r_R`'s construction cost as either resolved or
unresolvable.

## Provenance

- `knowledge/open-problems/KN-OPEN-de67f0.md` (kb — the superseded, narrower framing)
- `ledger/decisions/DEC-20260830-d7b846.yaml` (kb — this round's closeout decision)
- `coordination/goals/GOAL-ECDLP-001/proposals/B71-RCREP-DEFINITION-REVIEW-20260830-495939/tasks/TASK-20260830-031380/redteam-report.yaml` (kb — OBJ-5)
- `coordination/goals/GOAL-ECDLP-001/proposals/B71-RCREP-DEFINITION-REVIEW-20260830-495939/tasks/TASK-20260830-495939/validator-report.yaml` (kb — independent re-verification of the forward-direction proof and the tangent-stratum overclaim)
- `ledger/hypotheses/H-CREP-001.yaml` (retrieved — the declared exponent caps this obstruction is measured against)
