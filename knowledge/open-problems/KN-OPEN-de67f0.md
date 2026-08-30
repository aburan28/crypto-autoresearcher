---
id: KN-OPEN-de67f0
type: open_problem
title: H-CREP-001's complete-chart intersection resultant r_R has no self-contained mathematical definition -- RT103-C1 was never discharged
tags: [ecdlp, h-crep-001, exp-crep-001, p1553, resultant, specification-gap, red-team, rt103]
confidence: unverified
status: open
source_refs: [DEC-20260830-69bbf7, DEC-20260830-680f6d, KN-OPEN-73f0f4]
added: 2026-08-30
superseded_by: null
---

## Statement

`H-CREP-001.yaml`'s entire stated mechanism is one compound sentence:
`z_R = gcd(g_I, r_R)`, where `r_R` — "the complete-chart intersection
resultant" — is characterized only as vanishing at a label exactly when
that fifth occurrence extends to a labelled pair-pair relation. No formula
for `r_R` is given anywhere in `H-CREP-001`'s own record. No named
technique, no specification of how many decks are folded together or how,
no definition of the charts, saturations, multiplicities, or strata the
sentence refers to.

**This is not a newly discovered gap.** `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-001/tasks/TASK-20260722-103/red_team_report.yaml`
— the original red-team review of this exact obligation, dated
2026-07-22 — already raised precisely this point as objection **RT103-O1**,
at severity `blocking_before_constructor_review`: "'Complete-chart
intersection resultant' is an untyped macro here... not yet scoped
tightly enough to distinguish a compact constructor from construction of
the wrong support object." The required control, **RT103-C1**, demanded a
self-contained definition of `g_I`, `r_R`, `z_R`, charts, saturations,
multiplicities, and strata, plus a proof of exact support.

`RT103-C1` was never discharged. `ledger/proposals/IDEA-20260723-001.yaml`
(H-CREP-001's own source proposal) adds no further mechanism detail.
`ledger/decisions/DEC-20260724-003.yaml` records `NO_ADMISSIBLE_CONSTRUCTION`
failing at a different requirement, without affirmatively closing
`RT103-C1`. The gap was carried silently through H-CREP-001's approval,
`EXP-CREP-001`'s freeze, and every subsequent layer of this corpus
(package docstrings, route notes, `specification.yaml`'s forbidden-payload
text) for over a month, invisible to thirteen trigger-search rounds and
two derivation rounds because none of them needed to construct `r_R`
directly — they only needed to know it was *hard to construct*, which the
underspecification did not prevent them from establishing.

## Why this surfaced now

`TASK-20260830-06afa2` (a bounded derivation task) was asked to determine
whether `r_R`'s declared `Theta(B^2)` degree reflects genuine elimination
or non-deduplicated accounting. Lacking a formula in `H-CREP-001` itself,
it reconstructed a plausible mechanism (Semaev summation polynomials) from
two sentences in the original problem statement's `mechanism_note.md`,
explicitly flagged as inference. That reconstruction is mathematically
careful (independently verified in `DEC-20260830-69bbf7`) but admits **two
equally literal, mutually exclusive readings** predicting `Theta(B^2)` and
`Theta(B^4)` respectively — and the reading that matches the pre-existing
declared figure is, if anything, the *less* literal fit to the source
text. This ambiguity is a direct symptom of `RT103-C1` never having been
discharged: there is no authoritative mechanism to check either
reconstruction against.

## The open question, precisely

**Can a self-contained, checkable mathematical definition of `r_R` be
written down** — one that specifies exactly which decks are folded, how,
with what multiplicity and saturation structure, sufficient to (a) compute
its degree unambiguously and (b) prove it has exactly the support
`H-CREP-001` claims? This is `RT103-C1`, stated in the terms this
month-long investigation has since developed.

This is explicitly **not** a question further literature search or
inference from the existing two-sentence fragment can resolve — that
fragment has now been read closely by at least three independent sessions
(`TASK-20260830-06afa2` and its two reviewing Coordinators) and is
underspecified as written. It requires either a fresh mathematical
specification from whoever can supply one, or a Coordinator decision that
the ambiguity cannot be resolved and the obligation should be scoped down,
superseded, or closed on that basis.

## Why it matters

- **If `RT103-C1` can be discharged**: the resulting definition would
  settle the `Theta(B^2)`-vs-`Theta(B^4)` question definitively, and with
  it, whether `DEC-20260830-680f6d`'s degree-mismatch reasoning (and the
  obstruction chain built on it) is about a well-defined mathematical
  object at all.
- **If it cannot be**: `H-CREP-001` may need to be recorded as
  insufficiently specified to support further degree-level analysis, which
  would itself be a significant, honest finding about this program's
  oldest continuously-active hypothesis.

## What would resolve this

A Coordinator-authored (not idea-generator-inferred) task drafting an
explicit candidate definition of `r_R` addressing every element `RT103-C1`
names, submitted for independent `validator`/`red-team` review before any
further degree-provenance or trigger-search work treats `r_R`'s properties
as established. This is the concrete next action recorded in
`ledger/goals/GOAL-ECDLP-001/goal.yaml`'s `next_action` as of 2026-08-30.

## Provenance

- `ledger/decisions/DEC-20260830-69bbf7.yaml` (kb — the closeout decision that surfaced and traced this gap)
- `ledger/decisions/DEC-20260830-680f6d.yaml` (kb — the prior finding this gap now qualifies)
- `knowledge/open-problems/KN-OPEN-73f0f4.md` (kb — the now-superseded, narrower framing of the degree question)
- `ledger/hypotheses/H-CREP-001.yaml` (retrieved — read in full by the archiving Coordinator; confirmed to lack a formula for r_R)
- `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-001/tasks/TASK-20260722-103/red_team_report.yaml` (retrieved — the original RT103-O1/RT103-C1 objection and control)
- `ledger/proposals/IDEA-20260723-001.yaml`, `ledger/decisions/DEC-20260724-003.yaml` (retrieved — confirmed no subsequent discharge of RT103-C1)
