# BATCH-e26b68 Snapshot Receipt — TASK-20260806-9d5501 (archive)

**Goal:** GOAL-ECDLP-001
**Batch:** BATCH-e26b68
**Date:** 2026-08-06

## Archive content (coordinator-only snapshot commit)

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-e26b68/dispatch_queue.json`
  — dispatch queue (reviewer producer + archive task), validated by
  `tools/research_dispatch.py`.
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-e26b68/reviews/
  TASK-20260806-688acb/review_report.yaml` — independent adversarial review
  (TASK-20260806-688acb, CONCUR_WITH_OBJECTIONS), authored by the reviewer
  subagent in an independent session.
- `ledger/decisions/DEC-20260806-bba4bf.yaml` — Coordinator decision:
  accept review, correct corridor derivation to hypothesis-model window
  (empty, 64/39/39), record empirical window-cell falsification (B=16, m=3,
  N=1045; descent ratio 1.37-1.46), provenance correction, owed promotions.
- `ledger/hypotheses/H-MTBK-001.yaml` — status_history adds
  `independent_review_accepted`.
- `experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-cellgrid/manifest.yaml`
  and `RUN-MTBK-306bdb-smoke/manifest.yaml` — corrected provenance bindings
  (result.sha256 == raw artifact bytes; driver_sha256 pinned; worktree base
  commit recorded).

## Key reviewer-confirmed facts (BATCH-e26b68)

- Corridor empty at planned toy sizes **only** under the hypothesis's own
  window `beta*B^(m-1) < sqrt(N)` (bound 64/39/39 for m=3/4/5). The value
  written in AMEND-001 used `(B/2)^(m-1)` and gave 2621/160000/398000 —
  superseded.
- Cell-grid mean descent ratio 1.0546; mean relation ratio 1.4056; no m=4,5
  cell reaches 0.9*2^(m-1); the only near-sweep cells are m=3, b=0.4 relation
  channel (4.00 / 3.35).
- Empirical rescue falsification at the valid window cell (B=16, m=3, N=1045):
  descent full-check ratio 1.37-1.46 (>1).

## Provenance

- Base checked before merge: cae8537e6 (post-PR re-sync). The branch is shared
  with concurrent sessions; only the declared paths above are staged here.
- Concurrent-session files in the same tree (inputs/refs/research/ecdsafail_*,
  coordination GOAL-204b34 task cards, etc.) are NOT staged.

## Status

- Ready for ledger commit immediately following this snapshot.