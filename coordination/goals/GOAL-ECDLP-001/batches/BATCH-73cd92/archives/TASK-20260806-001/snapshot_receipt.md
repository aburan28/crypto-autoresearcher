# BATCH-73cd92 Snapshot Receipt — TASK-20260806-001

**Goal:** GOAL-ECDLP-001
**Batch:** BATCH-73cd92
**Date:** 2026-08-06

## Content

- `experiments/EXP-MTBK-306bdb/amendments/AMEND-001.yaml` — corridor-emptiness
  + geometric-model correction of the EXP-MTBK protocol (v0 -> v1).
- `experiments/EXP-MTBK-306bdb/code/run_mtbk_dataset.py` — corrected v1
  cell-grid driver (recursive m, adaptive target counts).
- `experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-cellgrid/*` — 36-cell
  grid run (curves {1,5}, b in {0.4,0.5,0.6}, m in {3,4,5}, seeds {1,2}).
- `experiments/EXP-MTBK-306bdb/analysis.md` — corrected v1 analysis.
- `ledger/decisions/DEC-20260806-26c0e8.yaml` — approve AMEND-001, supersede
  the rescue-window prediction, keep H-MTBK-001 proposed.
- `ledger/hypotheses/H-MTBK-001.yaml` — YAML syntax correction (A3 quoting);
  substantive content unchanged.

## Key numbers (BATCH-73cd92)

- Corridor-empty bounds: N<64 (m=3), N<39 (m=4), N<39 (m=5); numerically
  confirmed over N in {64,1e3,1e5,5.2e4,1e9}.
- 36-cell grid: descent ratio mean ~1.05 (m-invariant); relation ratio
  ~1.41; only tiny-B m=3 cells approach the sweep factor 4x. Both far below
  2^(m-1).

## Provenance

- Given the shared worktree and a concurrent session's uncommitted
  EXP-MTBK changes (b={0.6,0.7} spec + full-pipeline execution report), this
  batch stages ONLY the files above. The parallel artifacts are left untouched
  for the owning session and are intentionally NOT staged here.

## Read state

- Base checked: 089ff715 (pre-merge current). The branch previously carried
  BATCH-120..124 as 465395808; HEAD has since advanced through other goal
  batches (SSI/HAWK) in the shared tree.