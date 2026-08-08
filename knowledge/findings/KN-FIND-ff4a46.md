---
id: KN-FIND-ff4a46
type: internal_finding
title: "Wording repair for KN-FIND-9d2f56: align with corrected H-PSEUDO orientation"
tags: [betti-yield, h-pseudo, wording-repair, kn-find-9d2f56, orientation-fix]
confidence: proved
evidence_level: theorem
source_refs: [DEC-20260806-08b9ed, KN-FIND-9d2f56]
internal_refs: [DEC-20260806-08b9ed, DEC-20260805-364e9e]
proof_status: derivation
added: '2026-08-06'
superseded_by: null
repair_target: KN-FIND-9d2f56
---

## Purpose

KN-FIND-9d2f56 (Betti-Yield duality) carries a title and corollary wording
that can be read as claiming H-PSEUDO is a *sufficient* condition for sub-rho
combinatorial ECDLP. The corrected H-PSEUDO orientation — confirmed by
DEC-20260806-08b9ed as consistent with H-PSEUDO-83817b — is:

- **Holding** = pseudorandom = AT-heuristic yield (the baseline).
- **Sub-rho** critical complex requires **failure** of this baseline, i.e.,
  yield strictly above the heuristic.

This record supersedes KN-FIND-9d2f56's wording without altering its
mathematical content. The theorem body (the duality between β_1 and yield) is
unchanged; only the framing is repaired.

## Repaired wording

**Title:**
> Betti-Yield duality — sub-rho chain complex requires yield above the H-PSEUDO baseline

**Finding (Theorem):** (unchanged from KN-FIND-9d2f56)

**Corollary (repaired):**
> Any combinatorial algorithm for prime-field ECDLP that achieves sub-rho
> critical complex necessarily requires a factor base S whose yield exceeds
> the H-PSEUDO baseline (the AT-heuristic yield under pseudorandomness).
> H-PSEUDO names this baseline; sub-rho requires its failure. This record
> does not claim whether such a factor base exists or whether sub-rho is
> achievable; it states only the necessary condition.

## What changes and what does not

| Element | KN-FIND-9d2f56 (current) | KN-FIND-ff4a46 (repaired) |
|---------|--------------------------|---------------------------|
| Theorem body | Duality: β_1 ≥ Ω(sqrt(N)) OR yield = o(1) | **Unchanged** |
| Orientation | "H-PSEUDO is the exact condition for sub-rho" | "Sub-rho requires failure of H-PSEUDO baseline" |
| Sub-rho claim | Ambiguous (could be read as sufficient) | Explicitly neutral: necessary condition only |
| H-PSEUDO role | "algebraic formulation of the requirement" | "names the baseline; sub-rho requires its failure" |

## Non-claims

- No claim that sub-rho combinatorial ECDLP is achievable or impossible.
- No claim that H-PSEUDO holds or fails for any specific factor base.
- No claim in either direction about the sub-rho question; this is a wording
  repair to align the record with the corrected orientation, not a resolution
  of the open question.

## Provenance

Identified as a bookkeeping defect by the BATCH-e0ccb2 review audit
(DEC-20260806-08b9ed, weighing_of_the_review). The orientation fix is
confirmed correct per DEC-20260806-08b9ed what_survives item 1.
