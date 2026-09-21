# BATCH-46254b control-plane refresh — 2026-08-20

Coordination record for the refresh commit (B1) that makes the dispatch queue
match the verified state of the batch. Not evidence; asserts nothing about MD5.

## What the refresh records

- **TASK-20260810-26d0d5 → completed.** BCP-1 authored at f5087686e (2026-08-13)
  and repaired at d5fc2117d (2026-08-13), both in origin/main. BCP-1.yaml
  sha256 c3e92028f4c2f5e4a314aa3dafb965d7a36c0a93f179c9f0b5ca41bdd2a80c6d
  verified at HEAD.
- **TASK-20260810-927ab5 → completed.** Snapshot receipt committed at 48372c5d2
  (first parent f9745bb37), binding fixed at d8b91866a, both on this branch
  (PR #485). The queue's archive block was filled for content_first
  verification: commit 48372c5d2, path_sha256 covering BCP-1.yaml
  (c3e92028...) and the receipt (469cc57c... at HEAD).
  - RECORDED DISCREPANCY: the receipt's verification note claims the commit
    message names RQ-MDFIVE-6870c1 and DEC-20260810-9942ea; the actual message
    of 48372c5d2 names GOAL-MD5-001, BATCH-46254b and TASK-20260810-927ab5
    only. The queue's archive.record_ids is therefore declared as exactly the
    identifiers the bound commit's message names. The receipt is immutable and
    unedited.
- **TASK-20260810-3e0793 → completed.** Implementation pin + test-vector report
  committed at 421932986 (2026-08-19, this branch, PR #485). Test vectors:
  partial pass only; open item recorded in the report.
- **TASK-20260810-fc23ce → cancelled.** Its commit-mode binding was impossible
  by construction (three declared files committed inside a 24-path commit,
  230038427, now in origin/main). Superseded per DEC-20260819-8e16cc.
- **TASK-20260819-bec8eb → completed.** Its deliverable, the reattestation
  record, is committed by this refresh commit; hash stable at this commit.
- **TASK-20260819-f98fc0 → queued, single ready task.** content_first snapshot
  archive of the reattestation record; runs alone; after its receipt verifies,
  TASK-20260810-bde128 and TASK-20260810-b9d956 run concurrently
  (max_concurrent 2).

## Dispatch attempt record (B1 archival commit)

The B1 archival commit was first dispatched 2026-08-20 to a `coordinator`
subagent (requested policy coordinator-orchestration-code; resolved model
vllm/qwen3.8-27b). The subagent REFUSED to execute: its tool surface in this
runtime carries no command-execution tool, and it refused rather than
fabricate commit SHAs or verifier output (correct behavior under SC-1 and the
no-fabrication rule). The commit was therefore performed by the coordinating
session itself — the only surface in this runtime with a shell — under the
identical declared scope (the ten paths below, no others), the identical
post-commit verification steps, and this record documenting the substitution.
No review independence is affected: this is a coordinator archival act, not a
review, and it ran with no other agents in flight.

## Historical note: throwaway test commits

The prior session (2026-08-19) tested the reattestation + content_first
mechanism on throwaway branches: commits 20548ed3d ("B1
reattestation+reconciled queue") and 4f585c265 ("B2 ffc125 content_first
receipt final") on throwaway/aes-md5-full2, and 27d7e3236 / bf1c1c3e5 on
throwaway/aes-md5-fv3, all referencing the never-issued TASK-20260819-ffc125 /
TASK-20260819-aa8e1d. None of them is reachable from this branch; they are
dangling test artifacts and are superseded by this refresh, which uses the
actually-issued tasks (bec8eb / f98fc0) recorded in DEC-20260819-8e16cc.

## Scope of this commit (ten paths, staged individually)

1. ledger/decisions/DEC-20260819-8e16cc.yaml (repaired draft: YAML indentation
   fault fixed; ffc125 references replaced by the issued tasks; draft_repair_note added)
2. ledger/handoffs/TASK-20260819-bec8eb.yaml
3. ledger/handoffs/TASK-20260819-f98fc0.yaml
4. coordination/goals/GOAL-MD5-001/batches/BATCH-46254b/reattestation/BATCH-46254b-opening-reattestation.yaml
5. coordination/goals/GOAL-MD5-001/batches/BATCH-46254b/task-cards/TASK-20260819-bec8eb.md
6. coordination/goals/GOAL-MD5-001/batches/BATCH-46254b/task-cards/TASK-20260819-f98fc0.md
7. coordination/goals/GOAL-MD5-001/batches/BATCH-46254b/review-plan/review-plan-b9d956.yaml
8. coordination/goals/GOAL-MD5-001/batches/BATCH-46254b/dispatch_queue.json
9. ledger/goals/GOAL-MD5-001.yaml (next_action + updated_at)
10. coordination/goals/GOAL-MD5-001/batches/BATCH-46254b/control-plane-refresh-20260820.md (this file)

Claim ceiling unchanged: protocol_freeze_implementation_pin_and_literature_acquisition_only.
No scientific status, claim, approval, promotion, attestation or review verdict
changed. Amazon Bedrock was not selected, configured, probed, contacted or used.
