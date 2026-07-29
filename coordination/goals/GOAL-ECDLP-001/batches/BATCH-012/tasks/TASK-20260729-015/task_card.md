# TASK-20260729-015 — Snapshot archive of the frozen EXP-YIELD-002 contract

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs**.

| | |
|---|---|
| **Role** | coordinator (archive — **runs alone**) |
| **Depends on** | TASK-20260729-014 |
| **Archived by** | itself |
| **Budget** | 300 s, 1 GB, `maximum_runs: 1` (zero compute) |
| **Inference** | requested policy `coordinator-orchestration-code` |

## Objective

Commit the exact TASK-20260729-014 artifacts and record a verified post-commit
receipt, so the pre-execution review reads an immutable, hash-bound contract and
so the pre-registered prediction **provably predates every draw**.

## Declared commit set — exactly 3 paths

1. `experiments/EXP-YIELD-002/specification.yaml`
2. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/tasks/TASK-20260729-014/criterion_feasibility_table.md`
3. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/archives/TASK-20260729-015/snapshot_commit_receipt.json`

**INT-BATCH007-T applies.** This receipt's own path is declared and cannot be
changed by the commit whose SHA it records, so it lands in the **immediately
following commit**. State that in the receipt. Do not backdate it and do not
invent a workaround.

## Exclusive write scope

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/archives/TASK-20260729-015`

## Constraints

- **Run alone.** No other task may hold the Git index concurrently.
- Stage exactly the three declared paths. No extras, no deletions. BATCH-010 is
  permanently unrenderable for declaring 7 paths against a 195-path commit.
- Stage nothing under `experiments/EXP-YIELD-002/driver`, `/runs` or `/results`
  — they belong to TASK-20260729-018 and must not exist yet.
- Stage nothing under `experiments/EXP-YIELD-001`. **Verify** that
  `experiments/EXP-YIELD-001/specification.yaml` is unchanged at
  `82327a02bb3041af70566a3f8edfb4468dd2d52d` and record the verification; if it
  has been modified, do not commit and report an evidence-integrity failure.
- Stage nothing under `ledger/`, `knowledge/`, `harness/` or `tools/`, never
  `tools/validate_ledger_baseline.txt`, and no macOS AppleDouble sidecar file.
- Parse before committing: `yaml.safe_load` the specification **and** check for
  the space-hash truncation defect, which parses cleanly and silently discards
  the remainder of a scalar.
- **Record the pre-registered prediction verbatim in the receipt**, so it is
  auditable from the receipt alone and cannot be re-read later against the data.
- Commit message contains `TASK-20260729-015`, `TASK-20260729-014`,
  `EXP-YIELD-002`, `GOAL-ECDLP-001`, `BATCH-012` literally.
- Every SHA-256 from Git object content at the commit, never the working tree.
  Full 40-hex `commit_sha` and `parent_sha`.
- Committing the contract is **not** approving it. TASK-20260729-018 stays
  blocked until TASK-20260729-016 returns PASS (`INT-BATCH012-E`).
