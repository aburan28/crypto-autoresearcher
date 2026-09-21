---
id: KN-FIND-194294
type: internal_finding
title: Halving-query oracle is algebraically equivalent to the x-coordinate oracle
tags:
- halving-query
- x-oracle
- equivalence
- oracle-classification
- non-simulable
confidence: proved
evidence_level: theorem
source_refs:
- DEC-20260806-08b9ed
- DEC-20260805-364e9e
internal_refs:
- DEC-20260806-08b9ed
proof_status: derivation
added: '2026-08-06'
superseded_by: null
proof_refs: []
---

## Statement

Let O_D be the halving-query oracle: on input a point Q, it returns
x([2^{-1}]Q). Then O_D is algebraically equivalent to the x-coordinate oracle
O_x : Q ↦ x(Q). Specifically, a single halving-query O_D([2]Q) = x(Q)
recovers the target x-coordinate in one call; conversely, O_x recovers
O_D since x([2^{-1}]Q) is determined by x(Q) via the duplication formula.

## Consequence for oracle classification

O_D inherits the classification of O_x: it is NON-SIMULABLE (Tier 3) in the
GGM sense. Any sub-rho power of O_D reduces exactly to the sub-rho power of
O_x alone. The halving-query oracle does not open or close any direction that
the x-oracle alone does not already determine.

## Provenance

Corrected from BATCH-121 documents (TASK-20260805-004, TASK-20260805-005) by
the independent review audit in BATCH-e0ccb2 / DEC-20260806-08b9ed adjudication
item 1. The prior disposition (IDEA-20260805-58b638 "CLOSED as rejected —
simulable oracle, no sub-rho path") is SUPERSEDED; its premises
(GGM-simulability, barrier confirmed) are both false per the review record.

## Non-claims

- No claim that O_x (or equivalently O_D) is sub-rho-enabling or disabling.
  The x-oracle-alone sub-rho question is OPEN and is carried forward as living
  work under BATCH-122 / EV-SEMAEV-7f7d22.
- No experiment ran in this record; this is a corrected classification derived
  from the review audit.
