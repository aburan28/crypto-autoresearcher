---
task_id: TASK-20260806-a4b58a
batch_id: BATCH-b3f591
goal_id: GOAL-ECDLP-001
produced_for: DEC-20260806-08b9ed item 3 / exact_next_action item B
produced_at: '2026-08-06'
status: candidate — not promoted; promotion requires Coordinator ledger decision
---

# Knowledge candidates — TASK-20260806-a4b58a

Three KN-FIND candidate records drafted per DEC-20260806-08b9ed item 3 and
exact_next_action item B. None are promoted; promotion is a Coordinator ledger
action. No committed file is edited by this task.

---

## Candidate 1: KN-FIND-194294

**Minted:** `python3 tools/allocate_id.py --check KN-FIND-194294` → free, 0 occurrences.
**Allocator note:** `--next finding` is not a registered type in `allocate_id.py`;
token minted as random 6-hex per AGENTS.md rule 14 and verified with `--check`.

```yaml
id: KN-FIND-194294
type: internal_finding
title: Halving-query oracle is algebraically equivalent to the x-coordinate oracle
tags: [halving-query, x-oracle, equivalence, oracle-classification, non-simulable]
confidence: proved
evidence_level: theorem
source_refs: [DEC-20260806-08b9ed, DEC-20260805-364e9e]
internal_refs: [DEC-20260806-08b9ed]
proof_status: derivation
added: '2026-08-06'
superseded_by: null
```

### Statement

Let O_D be the halving-query oracle: on input a point Q, it returns
x([2^{-1}]Q). Then O_D is algebraically equivalent to the x-coordinate oracle
O_x : Q ↦ x(Q). Specifically, a single halving-query O_D([2^{-1}]Q) = x(Q)
recovers the target x-coordinate in one call; conversely, O_x recovers
O_D since x([2^{-1}]Q) is determined by x(Q) via the duplication formula.

### Consequence for oracle classification

O_D inherits the classification of O_x: it is NON-SIMULABLE (Tier 3) in the
GGM sense. Any sub-rho power of O_D reduces exactly to the sub-rho power of
O_x alone. The halving-query oracle does not open or close any direction that
the x-oracle alone does not already determine.

### Provenance

Corrected from BATCH-121 documents (TASK-20260805-004, TASK-20260805-005) by
the independent review audit in BATCH-e0ccb2 / DEC-20260806-08b9ed adjudication
item 1. The prior disposition (IDEA-20260805-58b638 "CLOSED as rejected —
simulable oracle, no sub-rho path") is SUPERSEDED; its premises
(GGM-simulability, barrier confirmed) are both false per the review record.

### Non-claims

- No claim that O_x (or equivalently O_D) is sub-rho-enabling or disabling.
  The x-oracle-alone sub-rho question is OPEN and is carried forward as living
  work under BATCH-122 / EV-SEMAEV-7f7d22.
- No experiment ran in this record; this is a corrected classification derived
  from the review audit.

---

## Candidate 2: KN-FIND-ac28ed

**Minted:** `python3 tools/allocate_id.py --check KN-FIND-ac28ed` → free, 0 occurrences.

```yaml
id: KN-FIND-ac28ed
type: internal_finding
title: "Exact-arithmetic corrections to BKK K* table: K*(standard)=2000 not 2001; m=4 cell 125 not 126"
tags: [bkk, semaev, exact-arithmetic, ieee-float, bkk-speedup, bkk-corrections]
confidence: proved
evidence_level: theorem
source_refs: [DEC-20260806-08b9ed, KN-FIND-c7d31e]
internal_refs: [DEC-20260806-08b9ed, EV-SEMAEV-7f7d22]
proof_status: derivation
added: '2026-08-06'
superseded_by: null
```

### Statement

The BKK K* formulas and rescue region t ∈ [1, (m+1)/2) from
KN-FIND-c7d31e verify under exact rational arithmetic, with the following
corrections to the as-committed BATCH-121 tables:

| Cell | As-committed | Exact value | Cause |
|------|-------------|-------------|-------|
| K*(standard) | 2001 | **2000** | IEEE-float ceil artifact: 200/0.1 = 2000.0000000000005 in double precision; exact rational is 2000 |
| m=4 cell | 126 | **125** | Same IEEE-float ceil artifact |
| K*(BKK) | 96 | 96 | Correct as-committed |

The K*(BKK)=96 value is confirmed correct. The two discrepancies above are
purely representational: the underlying formulas are exact; only the
floating-point evaluation and ceiling introduced the off-by-one errors.

### Consequence for EV-SEMAEV-7f7d22

EV-SEMAEV-7f7d22 must be pre-registered against exact rational arithmetic with
the linear-algebra and memory terms included. The "provable" label on the
speedup transfer is downgraded to a model assumption: KN-FIND-c7d31e's speedup
theorem applies to the membership predicate, not to the beta transfer to the
full linear-algebra cost model.

### Provenance

Corrected from BATCH-121 documents (TASK-20260805-005) by the independent
review audit in BATCH-e0ccb2 / DEC-20260806-08b9ed adjudication item 3. The
K* formulas, rescue region, and 96-cell number all verify; only the two cells
above are corrected.

### Non-claims

- No claim about the asymptotic exponent of Semaev index calculus.
- No claim that the BKK speedup theorem (KN-FIND-c7d31e) is invalidated; it
  is confirmed with the arithmetic corrections above.

---

## Candidate 3: KN-FIND-ff4a46

**Minted:** `python3 tools/allocate_id.py --check KN-FIND-ff4a46` → free, 0 occurrences.

```yaml
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
```

### Purpose

KN-FIND-9d2f56 (Betti-Yield duality) carries a title and corollary wording
that can be read as claiming H-PSEUDO is a *sufficient* condition for sub-rho
combinatorial ECDLP. The corrected H-PSEUDO orientation — confirmed by
DEC-20260806-08b9ed as consistent with H-PSEUDO-83817b — is:

- **Holding** = pseudorandom = AT-heuristic yield (the baseline).
- **Sub-rho** critical complex requires **failure** of this baseline, i.e.,
  yield strictly above the heuristic.

This candidate supersedes KN-FIND-9d2f56's wording without altering its
mathematical content. The theorem body (the duality between β_1 and yield) is
unchanged; only the framing is repaired.

### Proposed repaired wording

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

### What changes and what does not

| Element | KN-FIND-9d2f56 (current) | KN-FIND-ff4a46 (repaired) |
|---------|--------------------------|---------------------------|
| Theorem body | Duality: β_1 ≥ Ω(sqrt(N)) OR yield = o(1) | **Unchanged** |
| Orientation | "H-PSEUDO is the exact condition for sub-rho" | "Sub-rho requires failure of H-PSEUDO baseline" |
| Sub-rho claim | Ambiguous (could be read as sufficient) | Explicitly neutral: necessary condition only |
| H-PSEUDO role | "algebraic formulation of the requirement" | "names the baseline; sub-rho requires its failure" |

### Non-claims

- No claim that sub-rho combinatorial ECDLP is achievable or impossible.
- No claim that H-PSEUDO holds or fails for any specific factor base.
- No claim in either direction about the sub-rho question; this is a wording
  repair to align the record with the corrected orientation, not a resolution
  of the open question.

### Provenance

Identified as a bookkeeping defect by the BATCH-e0ccb2 review audit
(DEC-20260806-08b9ed, weighing_of_the_review). The orientation fix is
confirmed correct per DEC-20260806-08b9ed what_survives item 1.
