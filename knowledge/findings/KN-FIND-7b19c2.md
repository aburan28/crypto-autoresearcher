---
id: KN-FIND-7b19c2
type: internal_finding
title: Geometric first-success descent model — per-target cost ~ N/B for naive ordered enumeration, both std and BKK enumerators
tags: [ecdlp, multi-target, semaev, index-calculus, toy-scale, measured]
confidence: measured
evidence_level: reproduced_experiment
source_refs: [BATCH-73cd92, BATCH-e26b68, TASK-20260806-688acb]
internal_refs: [DEC-20260806-26c0e8, DEC-20260806-bba4bf, EXP-MTBK-306bdb, RUN-MTBK-306bdb-cellgrid]
review_refs:
  - coordination/goals/GOAL-ECDLP-001/batches/BATCH-e26b68/reviews/TASK-20260806-688acb/review_report.yaml
proof_status: empirical_only
proof_refs:
  - experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-cellgrid/raw-result.json
  - experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-cellgrid/result.json
added: '2026-08-06'
superseded_by: null
---

## Finding (geometric-descent, toy scope)

For naive ordered enumeration in a factor-base descent (index-calculus with
threshold factor base), the per-target first-success cost is approximately
**N/B** use-group ops, for BOTH the standard enumerator and the BKK
sparse-check enumerator, at toy scale.

### Measured evidence (RUN-ED_200b, 36 cells)

- Mean full-check **descent** ratio (std/bkk) across the 36-cell corrected
  grid: **1.0546** (essentially 1.0-1.1); no m=4,5 cell reaches 0.9·2^(m-1).
- Mean **relation** ratio: **~1.41** overall (b.size). Only the m=3, b=0.4
  relation channel reaches the sweep-domain factor (4.00 at B=16; 3.35 at
  B=13); these are the small-B cells where domain cardinality dominates.
- Probe (unarchived, recorded with caveat in AMEND-001): 12 targets on
  p=52721, B=230 gave mean std 149 / bkk 123 per-target checks vs
  N/B ≈ 228 predicted by the geometric model, and vs B^2 = 52900 predicted by
  the sweep model.
- Implication: the exponential variable-sort index theorem (KN-FIND-982fdf,
  sweeps) is a full-sweep statement; the empirically-dominating first-success
  budget is geometric, NOT domain cardinality.

## Test boundary

- **Affected:** the toy naive-enumeration multi-target index-cal depth/cost
  model (descend channel); any claim that BKK multiplies the exponent-1/2
  baseline by (m+1)/2 in this channel.
- **Unaffected**: the group-algebra factorization theorem itself
  (KN-FIND-c7d31e), the C_t-minimality oracle theorem (KN-FIND-982fdf), the
  full-sweep (memorized relation table) variant in which sweep cardinality IS
  the budget, and all Pollard-rho claims.

## Status

Review-surviving (TASK-20260806-688acb F2, CONCUR on the ratio numbers).
Promoted scope: descent channel, toy naive enumeration.