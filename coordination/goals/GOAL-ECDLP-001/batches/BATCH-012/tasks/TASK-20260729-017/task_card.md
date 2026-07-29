# TASK-20260729-017 — Snapshot archive of the contract review, and the recording of every pre-dispatch condition

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs**.

| | |
|---|---|
| **Role** | coordinator (archive — **runs alone**) |
| **Depends on** | TASK-20260729-016 |
| **Archived by** | itself |
| **Budget** | 300 s, 1 GB, `maximum_runs: 1` (zero compute) |
| **Inference** | requested policy `coordinator-orchestration-code` |

## Objective

Commit the exact TASK-20260729-016 review artifacts, record a verified
post-commit receipt, and record **in that receipt, before any run is
dispatched**, the Coordinator's approval determination on `EXP-YIELD-002` and
every pre-dispatch condition the review imposed, **verbatim**.

This card carries both BATCH-011 governance repairs:

- **D-1 route.** The frozen `experiments/EXP-YIELD-002/specification.yaml` is
  **never edited** to record approval. The approval determination is recorded
  here — pre-execution, hash-bound, committed before any run — and again as a
  formal `experiment_status_transition` in `DEC-20260729-002`. In BATCH-011 the
  transition was never recorded and had to be supplied late by a superseding
  record; that is not repeated.
- **D-2 route.** Every pre-dispatch condition is recorded here, with the number
  the reviewer gave it and the Coordinator's reading of each — adopted, adopted
  with a named narrowing, or declined with a reason. **If a condition exists and
  is not recorded here, TASK-20260729-018 does not dispatch.** In BATCH-011,
  `PC-1`, `PC-2` and `PC-4` were never separately recorded before dispatch.

## Declared commit set — exactly 3 paths

1. `.../BATCH-012/reviews/TASK-20260729-016/contract_review.yaml`
2. `.../BATCH-012/reviews/TASK-20260729-016/feasibility_check.md`
3. `.../BATCH-012/archives/TASK-20260729-017/snapshot_commit_receipt.json`

**INT-BATCH007-T applies**: this receipt's own path is declared and lands in the
immediately following commit. State that; do not backdate; invent no workaround.

## Constraints

- **Run alone.** Stage exactly the three declared paths; no extras, no
  deletions.
- Stage nothing under `experiments/`, `ledger/`, `knowledge/`, `harness/` or
  `tools/`, never `tools/validate_ledger_baseline.txt`, no AppleDouble sidecar.
- Parse `contract_review.yaml` and check it for the space-hash truncation
  defect. A verdict field silently truncated by an unquoted ` #` would
  misrepresent the reviewer — **that has already happened once in this program**.
- **Record the verdict verbatim. The receipt records the verdict; it does not
  act on it.** On PASS, record that the execution gate is met and execution is
  authorized, naming the committed records that meet it. On REVISE, record that
  execution is **not** authorized and that `RC-12`'s one-cycle route or a BATCH
  FAILURE is what follows.
- Commit message contains `TASK-20260729-017`, `TASK-20260729-016`,
  `EXP-YIELD-002`, `BATCH-012` literally.
- Every SHA-256 from Git object content at the commit. Full 40-hex
  `commit_sha` and `parent_sha`.
- The receipt states that the `INT-BATCH012-E` gate is the Coordinator's to
  enforce, that the frozen specification was not edited, and that nothing is
  durable until the post-commit verifier accepts this commit.
