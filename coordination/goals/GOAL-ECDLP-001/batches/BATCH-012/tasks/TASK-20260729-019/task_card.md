# TASK-20260729-019 — Snapshot archive of the EXP-YIELD-002 run package

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs**.

| | |
|---|---|
| **Role** | coordinator (archive — **runs alone**) |
| **Depends on** | TASK-20260729-018 |
| **Archived by** | itself |
| **Budget** | 300 s, 1 GB, `maximum_runs: 1` (zero compute, re-runs nothing) |
| **Inference** | requested policy `coordinator-orchestration-code` |

## Objective

Commit the exact eleven run-package artifacts and record a verified post-commit
receipt, so the Validator and the Red Team read an immutable, hash-bound
package — and so **RC-A is archived under its own run id**, without which
`DEC-20260729-001` states in terms that it is not evidence.

## Declared commit set — exactly 12 paths

The eleven TASK-20260729-018 artifacts (one driver, one summary, three files in
each of three run directories) plus this archive's own receipt at
`.../BATCH-012/archives/TASK-20260729-019/snapshot_commit_receipt.json`.

**INT-BATCH007-T applies**: the receipt's own path is declared and lands in the
immediately following commit. State that; do not backdate; invent no workaround.

## Constraints

- **Run alone.** Stage exactly the twelve declared paths. Any extra path is a
  scope-expanding commit and blocks the review chain — the exact failure that
  made BATCH-010 permanently unrenderable.
- **If a run directory is missing one of its three files, do not commit and do
  not create the file.** Report the gap: a missing declared artifact is an
  evidence-integrity failure repaired by a scoped successor task, never by an
  archive that invents content.
- An undeclared Executor file is neither staged nor deleted — record it in the
  receipt for the Coordinator to dispose of by amendment.
- Machine-parse all seven JSON files (three manifests, three results,
  `summary.json`) and record the parse result per file. An unparseable manifest
  goes back to the Executor.
- **Do not re-run, re-compute, edit, normalise or reformat any run artifact.**
  Run records are immutable from the moment they are written. In particular, **do
  not adjust anything because the prediction missed.**
- Record each run's terminal status and the per-cell pass-or-miss count against
  the pre-registered prediction **as read from `summary.json`, verbatim and
  without interpretation**. The receipt reports what the package says; it does
  not decide what it means.
- Commit message contains `TASK-20260729-019`, `TASK-20260729-018`,
  `EXP-YIELD-002`, `BATCH-012` literally.
- Every SHA-256 from Git object content at the commit. Full 40-hex
  `commit_sha` and `parent_sha`.
- The receipt states that no run artifact was edited, normalised or re-run by
  this archive, and that RC-A is archived under its own run id by this commit.
