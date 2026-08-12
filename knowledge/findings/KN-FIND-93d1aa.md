---
id: KN-FIND-93d1aa
type: internal_finding
title: Toy-scale BKK rescue of an infinite crossover K* is falsified at the one live window cell (B=16, m=3, N=1045)
tags: [ecdlp, multi-target, bkk, rescue-window, falsified, toy-scale]
confidence: measured
evidence_level: reproduced_experiment
source_refs: [BATCH-e26b68, TASK-20260806-688acb, EXP-MTBK-306bdb]
internal_refs: [DEC-20260806-bba4bf, RUN-MTBK-306bdb-cellgrid]
review_refs:
  - coordination/goals/GOAL-ECDLP-001/batches/BATCH-e26b68/reviews/TASK-20260806-688acb/review_report.yaml
proof_status: empirical_only
proof_refs:
  - experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-cellgrid/raw-result.json
  - experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-cellgrid/result.json
added: '2026-08-06'
superseded_by: null
---

## Finding (empirical falsification of the toy rescue)

Under the corrected rescue-window model (hypothesis window
`beta*B^(m-1) < sqrt(N)`, i.e. t_std < (m+1)/2), the rescue-window corridor
is EMPTY at all planned toy sizes (bounds 64/39/39 for m=3/4/5), so no
"BKK rescues an infinite K*" cell can exist by the corridor argument alone.
But even under the looser written window, the one cell that DOES fall inside
it is empirically non-rescuing:

- **Live window cell**: N=1045 (p=1009), m=3, B=16 (b=0.4). Sweep-model
  t_std = B^(2)/sqrt(N) = 7.92 >= 1 (std K* infinite), t_bkk =
  (2/4)·B^(2)... < 1 (BKK K* nominally finite).
- **Measured**: descent full-check ratio 1.3716 / 1.4568 for seeds 1/2, i.e.
  >1 (baseline displaced, no descent rescue); relation full-check ratio
  4.00 = exactly the sweep domain ratio (not a rescue, just the domain
  factor in the harvest channel).

### Falsified claims

- "BKK sparse check rescues a finite K* where the standard run has infinite
  K* at toy scale" — falsified for the naive ordered-enumeration descent.
- The AMEND-001 written `(B/2)^(m-1)` corridor bound (2621/160000/398000
  era) as a claim of emptiness — superseded (see DEC-20260806-bba4bf).

### Surviving structure

The BKK factorization still delivers the relation/collection domain ratio
(4.00 at m=3/B=16) — that channel is real; it is the descent channel's
geometric budget (KN-FIND-7b19c2) that removes the rescue.

## Test boundary/unchanged

Toy naive enumeration. Not a statement about full-sweep/memorized-relation
variants, Pollard rho, or the index theorem itself (KN-FIND-982fdf remains
correct as a full-sweep order-statistics statement). FR-2 (N=27, m=3, B=3)
is the pre-registered cheapest decisive probe of the maximal corrected cell;
this record is scoped to the data already measured.