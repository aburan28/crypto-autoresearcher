# TASK-20260729-036 — Snapshot archive of the EXP-YIELD-003 run package

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** coordinator (archival — **runs alone**)
- **Archive kind:** snapshot; `source_task_ids: [TASK-20260729-035]`
- **Depends on:** TASK-20260729-035
- **Archived by:** itself
- **Budget:** 300 s, 1 GB, `maximum_runs: 1` (zero compute)

## Objective

Commit the eleven TASK-20260729-035 artifacts plus this receipt, so the run
package is immutable and hash-bound **before any review reads it** — which is
what makes RC-21A evidence at all. This program has already driven one decision
from an unarchived probe that then failed to reproduce.

## Declared commit set — exactly 12 paths

1. `experiments/EXP-YIELD-003/driver/replicate_repaired_null.py`
2. `experiments/EXP-YIELD-003/results/summary.json`
3–5. `experiments/EXP-YIELD-003/runs/RUN-YIELD-003-REPLICATE-REPAIRED/manifest.json`, `results.json`, `stdout.log`
6–8. `experiments/EXP-YIELD-003/runs/RUN-YIELD-003-HIGHPREC/manifest.json`, `results.json`, `stdout.log`
9–11. `experiments/EXP-YIELD-003/runs/RUN-YIELD-003-KNOWNANSWER/manifest.json`, `results.json`, `stdout.log`
12. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-036/snapshot_commit_receipt.json`

The three-file-per-run set is mandatory **even for a non-completed run**, which
is what makes a twelve-path declaration exact in advance rather than a guess.
Path 12 is declared here and **lands in the immediately following commit**
(INT-BATCH007-T, now demonstrated).

## Exclusive write scope

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-036`

## Constraints

- **Run alone**, and no review may read the package before this commit lands.
- Stage exactly the twelve declared paths and nothing else.
- Stage nothing under `experiments/EXP-YIELD-001` or `EXP-YIELD-002`; verify
  the EXP-YIELD-002 specification blob unchanged at
  `f291a624610458fc7ad40b5cf174447517ce97e5` and record it.
- **Do not edit** `experiments/EXP-YIELD-003/specification.yaml`. It is frozen
  and hash-bound at the TASK-20260729-032 commit and reads `review_required`
  with `approved_by: null` **by design** (INT-BATCH013-F). That null must not
  be read as evidence of non-approval and must not be repaired by an edit.
- Stage nothing under `ledger/`, `knowledge/`, `harness/`, `tools/`; never
  `tools/validate_ledger_baseline.txt`; no other batch's queue; no AppleDouble
  sidecar.
- An undeclared producer file is **neither staged nor deleted** — record it in
  the receipt for disposal by amendment.
- Machine-parse all four JSON documents before committing.
- **Quote, do not dispose.** Record the mean, sd and SEM of `z_sem` and
  `n_neg` from the package as quoted numbers. **Do not apply the resume
  condition, do not declare the shift reproduced or not reproduced, classify
  nothing** — the disposition belongs to TASK-20260729-039 after two
  independent reviews. Record verbatim what the run said about the interpreter
  build and platform, **including any statement that a different one was
  unavailable**.
- Commit message contains `TASK-20260729-036`, `TASK-20260729-035`,
  `EXP-YIELD-003`, `GOAL-ECDLP-001`, `BATCH-013` literally, and **must not
  contain the C-20 power sentence**.
- Every SHA-256 from Git object content at the commit; full 40-hex
  `commit_sha` and `parent_sha`.

## Receipt must state

That it disposes of nothing, applies no resume condition and declares no
branch; that the claim tier is **toy**; and that nothing in BATCH-013 is
durable until the dispatcher's post-commit verifier accepts this commit.
