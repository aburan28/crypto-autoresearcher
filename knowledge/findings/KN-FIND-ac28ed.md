---
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
---

## Statement

The BKK K* formulas and rescue region t ∈ [1, (m+1)/2) from
KN-FIND-c7d31e verify under exact rational arithmetic, with the following
corrections to the as-committed BATCH-121 tables:

| Cell | As-committed | Exact value | Cause |
|------|-------------|-------------|-------|
| K*(standard) | 2001 | **2000** | IEEE-float ceil artifact in the evaluation of the K* formula; exact rational is 2000 |
| m=4 cell | 126 | **125** | Same IEEE-float ceil artifact |
| K*(BKK) | 96 | 96 | Correct as-committed |

The K*(BKK)=96 value is confirmed correct. The two discrepancies above are
purely representational: the underlying formulas are exact; only the
floating-point evaluation and ceiling introduced the off-by-one errors.

## Consequence for EV-SEMAEV-7f7d22

EV-SEMAEV-7f7d22 must be pre-registered against exact rational arithmetic with
the linear-algebra and memory terms included. The "provable" label on the
speedup transfer is downgraded to a model assumption: KN-FIND-c7d31e's speedup
theorem applies to the membership predicate, not to the beta transfer to the
full linear-algebra cost model.

## Provenance

Corrected from BATCH-121 documents (TASK-20260805-005) by the independent
review audit in BATCH-e0ccb2 / DEC-20260806-08b9ed adjudication item 3. The
K* formulas, rescue region, and 96-cell number all verify; only the two cells
above are corrected.

## Non-claims

- No claim about the asymptotic exponent of Semaev index calculus.
- No claim that the BKK speedup theorem (KN-FIND-c7d31e) is invalidated; it
  is confirmed with the arithmetic corrections above.
