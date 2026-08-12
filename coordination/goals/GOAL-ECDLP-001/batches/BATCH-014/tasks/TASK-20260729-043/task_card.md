# TASK-20260729-043 — Snapshot archive of the pre-execution review, carrying the approval determination

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** coordinator (archival task — **runs alone**)
- **Depends on:** TASK-20260729-042
- **Archive kind:** snapshot; `source_task_ids: [TASK-20260729-042]`
- **Budget:** 300 s, 1 GB, `maximum_runs: 1` (zero compute)

## Objective

Commit the exact TASK-20260729-042 review artifacts **and record, in the same
receipt and at the moment it is made, the Coordinator's APPROVAL DETERMINATION
on EXP-STR-004 together with every pre-dispatch condition the reviewer imposed,
verbatim** — so the determination is pre-execution and hash-bound and cannot be
reconstructed afterwards.

## Declared commit set — exactly 3 paths

```
coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/reviews/TASK-20260729-042/contract_review.yaml
coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/reviews/TASK-20260729-042/derivation_check.md
coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/archives/TASK-20260729-043/snapshot_commit_receipt.json
```

## The approval determination — INT-BATCH014-F

- Write `APPROVAL_DETERMINATION` as an explicit field: **APPROVED** or **NOT
  APPROVED**, with the reviewer's verdict quoted, **every pre-dispatch condition
  recorded verbatim and numbered**, and the sha256 of both review artifacts.
- **If the reviewer named conditions and this receipt does not record them,
  TASK-20260729-044 does not dispatch.**
- A receipt that records NOT APPROVED is recorded as NOT APPROVED. No later
  record may attribute an APPROVED determination to a receipt that does not
  carry it.

## The D-1 prophylaxis

**Do not edit `experiments/EXP-STR-004/specification.yaml`.** It is frozen at
`status: review_required` with `approved_by: null` **by design**, and that null
**must not be read as evidence of non-approval**.

## On REVISE — RC-14 / INT-BATCH014-E

No run is authorized. Either **exactly one** versioned `protocol_amendment`
cycle is opened by a recorded QUEUE-AMEND, snapshot-committed and independently
re-reviewed by a non-originating session before execution — with the cycle-cap
ruling assigned to a session that **did not author** the amendment — or the
batch records the non-execution as a **BATCH FAILURE** and records it as such.

## Hazards

Check for a stale `.git/index.lock` before staging and record what you found; a
zero-byte lock with no live git process is **reported, and stops the card** —
never deleted silently. An unfinished git verification is reported as
unfinished, never as PASS and never as FAIL. No AppleDouble sidecar. Nothing
under `ledger/`, `knowledge/`, `harness/`, `tools/` or `experiments/`.

This receipt lands in the immediately following commit (INT-BATCH007-T).
