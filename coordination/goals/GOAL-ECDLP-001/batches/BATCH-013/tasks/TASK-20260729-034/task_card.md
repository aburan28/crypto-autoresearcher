# TASK-20260729-034 — Snapshot archive of the pre-execution review, with the approval determination recorded before any run

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** coordinator (archival — **runs alone**)
- **Archive kind:** snapshot; `source_task_ids: [TASK-20260729-033]`
- **Depends on:** TASK-20260729-033
- **Archived by:** itself
- **Budget:** 300 s, 1 GB, `maximum_runs: 1` (zero compute)

## Objective

Commit the two review artifacts **and record, in the receipt and at the moment
it is made, the Coordinator's `approval_determination` on EXP-YIELD-003
together with every pre-dispatch condition the reviewer imposed, verbatim** —
so approval strictly precedes execution in the commit graph and no later record
has to supply it post hoc. This is the D-1/D-2 prophylaxis; it worked in
BATCH-012 and is repeated exactly.

## Declared commit set — exactly 3 paths

1. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-033/contract_review.yaml`
2. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-033/independence_and_platform_note.md`
3. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-034/snapshot_commit_receipt.json`

Path 3 is declared here and **lands in the immediately following commit**
(INT-BATCH007-T, now demonstrated). State the ordering in the receipt.

## Exclusive write scope

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-034`

## Constraints

- **Run alone.** Stage exactly the three declared paths.
- **Record the determination honestly, in a field named
  `approval_determination`.** If TASK-20260729-033 returned REVISE, the
  determination is **NOT APPROVED** and the receipt states in terms that
  TASK-20260729-035 **is not authorized to run**. Never record APPROVED against
  a review that returned REVISE, and never let a later record attribute an
  APPROVED determination to a receipt that does not carry it.
- **Record every pre-dispatch condition verbatim**, numbered as the reviewer
  numbered them, with the Coordinator's disposition of each. A condition not
  recorded here does not bind the Executor, and TASK-20260729-035 does not
  dispatch (INT-BATCH013-F).
- **On REVISE, do not dispatch and do not self-authorize a cycle.** Opening the
  single permitted amendment cycle requires a recorded QUEUE-AMEND adding its
  cards, declared commit sets and budget — **and the cycle-cap ruling must be
  made by a session that did not author the amendment it authorises**
  (`execution_gate.cycle_cap_ruling_assignment`, carried from
  DEC-20260729-002). A second cycle is a **BATCH FAILURE**, and non-execution
  is never recorded as a result.
- Stage nothing under `experiments/`, `ledger/`, `knowledge/`, `harness/` or
  `tools/`; never `tools/validate_ledger_baseline.txt`; no AppleDouble sidecar.
- `yaml.safe_load` `contract_review.yaml` before committing and check for the
  space-hash truncation defect, which has already corrupted a reviewer's words
  once in this program.
- Commit message contains `TASK-20260729-034`, `TASK-20260729-033`,
  `EXP-YIELD-003`, `GOAL-ECDLP-001`, `BATCH-013` literally.
- Every SHA-256 from Git object content at the commit; full 40-hex
  `commit_sha` and `parent_sha`.
