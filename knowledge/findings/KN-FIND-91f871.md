---
id: KN-FIND-91f871
type: internal_finding
title: "Rank candidate Q(t) families by measured height envelope, not by generic rank: buying generic rank buys a steeper height law"
tags: [height-envelope, shioda-tate, piecewise-height-law, family-selection, gate, nagao-1994, mestre-1982, icarm, naive-height, rank-12]
confidence: derivation_must_not_be_stronger_than_EV-ECQ-cbc837
evidence_level: derivation_plus_one_measured_family
source_refs: [RUN-ECQNAG-f88f54-001, RUN-ECQNAG-f88f54-002, RUN-ECQNAG-f88f54-003, RUN-ECQNAG-f88f54-004, RUN-ECQNAG-f88f54-005, RUN-ECQNAG-f88f54-006, RUN-ECQNAG-f88f54-009, RUN-ECQNAG-f88f54-012, GOAL-ECQ-002]
internal_refs: [RQ-ECQ-80f23c, H-ECQ-a609f8, H-ECQ-8b600d, H-ECQ-0ed5c8, EV-ECQ-cbc837, DEC-20260823-839fc6]
proof_status: derivation
proof_status_note: >-
  Must not be stated stronger than EV-ECQ-cbc837, whose proof_status is
  `derivation`.
proof_refs:
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-72505a/validation_report.md
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-eaf799/redteam_report.md
review_refs:
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-72505a/verdict.yaml
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-eaf799/objections.yaml
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/archives/TASK-20260823-452f5f/receipt.yaml
added: '2026-08-24'
superseded_by: null
---

# Rank families by measured envelope, not by generic rank

## Scope (verbatim, binding)

> The slope law and the 1.2(r+2) bound are claimed for minimal Weierstrass
> models of elliptic surfaces over P^1; the O(1) term is UNMEASURED outside
> the one family measured here; the 109.505 figure is claimed for the
> transcribed NAGAO-1994 surface and nowhere else; and nothing in this
> finding bears on rank >= 31 over Q, which remains an open world record.

## Statement

For an elliptic surface of degree d over P^1, a minimal Weierstrass model
has deg a4 <= 4d and deg a6 <= 6d, so the fibre's naive height satisfies
h(E_t) = 12d log|t| + O(1); Shioda-Tate caps generic Mordell-Weil rank at
10d - 2, so a family of generic rank r has d >= ceil((r+2)/10) and hence an
asymptotic height slope of at least 1.2(r+2). The small-parameter lever
therefore exhausts inside a bounded region of small-Weil-height parameters,
and inside that region the fibre height is set by the family's own O(1)
constant rather than by the parameter. THE OPERATIONAL CONSEQUENCE IS A
CHEAP GATE: candidate families are ranked by the MEASURED lower envelope of
minimal-model naive height over the crossover band -- about two seconds and
1e5 fibres per family -- rather than by generic rank, because at fixed d the
constant varies enormously between families.

## Worked instance

The transcribed NAGAO-1994 quartic: d = 2, predicted slope 24 against a
measured 24.14, flat arm h = 119.42 + 0.062 log|t| below the crossover at
|t| ~ 89, lower envelope 109.5051651866501 at t = +-62 over 141221 fibres,
against Mestre 1982's 79.329 at the same rank 12. The gate would have
rejected the family before a batch was spent on it.

## How this finding is used

This is the gate that BATCH-8b08ef (H-ECQ-0ed5c8, EXP-ECQ-0e0cbb) applies:
the squarefree-discriminant pre-filter selects candidate families, and their
envelopes are measured, not inferred from generic rank. The batch-3
refinement (KN-FIND-e1b836) identifies WHICH family property the O(1)
constant tracks in the construction of Mestre: the reducible-finite-fibre
count, selected for by the pre-filter. BATCH-8b08ef's producer applied the
gate and reached BRANCH C (coverage is the result; no cell taken), so the
gate's operational consequence stands but the lever it was meant to drive
remains unproven at full coverage.
