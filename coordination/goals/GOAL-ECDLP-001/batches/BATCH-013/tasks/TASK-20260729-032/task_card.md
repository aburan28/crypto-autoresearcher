# TASK-20260729-032 — Snapshot archive of the frozen EXP-YIELD-003 contract

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** coordinator (archival — **runs alone**)
- **Archive kind:** snapshot; `source_task_ids: [TASK-20260729-031]`
- **Depends on:** TASK-20260729-031
- **Archived by:** itself
- **Budget:** 300 s, 1 GB, `maximum_runs: 1` (zero compute)

## Objective

Commit the exact TASK-20260729-031 artifacts and record a verified post-commit
receipt, so the pre-execution review reads an immutable, hash-bound contract
and so the resume condition and the three master seeds provably predate every
draw.

## Declared commit set — exactly 3 paths

1. `experiments/EXP-YIELD-003/specification.yaml`
2. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/tasks/TASK-20260729-031/observation_feasibility_table.md`
3. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-032/snapshot_commit_receipt.json`

**INT-BATCH007-T, now demonstrated:** an archive's own receipt cannot be
changed by the commit whose SHA it records — and marking an archive card
`completed` with its commit bound in the queue makes
`tools/research_dispatch.py` refuse the entire queue, because `verify_archive`
requires the commit to change its own receipt. Path 3 is declared here and
**lands in the immediately following commit**. State that in the receipt; do
not backdate it and do not invent a workaround.

## Exclusive write scope

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-032`

## Constraints

- **Run alone.** No other task may hold the Git index concurrently.
- Stage exactly the three declared paths. Any extra path is a scope-expanding
  commit; BATCH-010 is permanently unrenderable for declaring 7 paths against a
  195-path commit.
- Stage **nothing** under `experiments/EXP-YIELD-003/driver`, `/runs` or
  `/results` — those belong to TASK-20260729-035 and must not exist yet.
- Stage nothing under `experiments/EXP-YIELD-001` or `experiments/EXP-YIELD-002`;
  both are committed and immutable. **Verify** the EXP-YIELD-002 specification
  blob is unchanged at `f291a624610458fc7ad40b5cf174447517ce97e5` and record it.
- Stage nothing under `ledger/`, `knowledge/`, `harness/` or `tools/`, never
  `tools/validate_ledger_baseline.txt`, no other batch's queue, no macOS
  AppleDouble sidecar.
- An undeclared producer file is **neither staged nor deleted** — record it in
  the receipt for disposal by amendment.
- `yaml.safe_load` the specification before committing; check for space-hash
  truncation and for a mapping key at the indent of an open block sequence.
- **Record the three master seeds and the resume condition verbatim in the
  receipt**, so both are auditable from the receipt alone.
- Commit message contains `TASK-20260729-032`, `TASK-20260729-031`,
  `EXP-YIELD-003`, `GOAL-ECDLP-001`, `BATCH-013` literally.
- Every SHA-256 computed from Git object content at the commit, never the
  working tree. Full 40-hex `commit_sha` and `parent_sha`.

## Receipt must state

Committing the contract is **not** approving it. TASK-20260729-035 stays
blocked until TASK-20260729-033 returns PASS **and** the approval determination
is recorded in the TASK-20260729-034 receipt (INT-BATCH013-E, INT-BATCH013-F).
Nothing in BATCH-013 is durable until the dispatcher's post-commit verifier
accepts this commit.
