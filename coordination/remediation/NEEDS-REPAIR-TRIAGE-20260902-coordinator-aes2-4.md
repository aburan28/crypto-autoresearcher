# needs_repair triage — 2026-09-02, coordinator-aes2-4 (OpenCode, standing harness)

Triage of the 13-goal `needs_repair` bucket reported by `tools/goal_portfolio_health.py`
(47 active goals: 0 ready / 34 blocked / 13 needs_repair at 2026-09-02T00:58Z).
This is a control-plane record: it diagnoses and ranks remediation; it repairs nothing,
changes no status, and rewrites no binding. All findings below were verified against the
live tree at commit bfaad725b (branch ideas-ecdlp-20260830, current with main at d4404db5d).

## Systemic observation (cited examples)

Four of the thirteen failures share one root cause: an archive task binds the goal head's
content hash at archive time, and every later legitimate head edit (the next checkpoint)
breaks the stale queue's rendering. Instances: GOAL-DIFFP-84d641 (head last changed
2026-08-28, after archive TASK-20260826-775c57), GOAL-MLKEM-005 (head changed
2026-08-31, archive TASK-20260826-70d800), GOAL-ECQ-e72c0b (same shape, archive
TASK-20260824-861144), GOAL-DREG-001 (same shape, archive TASK-20260827-0cc0e7,
dispatch_queue.v3.json; the bound head path ledger/goals/GOAL-DREG-001/goal.yaml has no
git history at that path — the head itself moved, a second-order instance of the same
drift). This is a protocol/tooling gap, not per-goal corruption: either queues should not
bind the head hash, or head edits must re-bind the queue. That is a Coordinator protocol
decision for the owning lanes, not a fix to make goal-by-goal here.

## Per-goal findings and recommended minimal fixes

| Goal | Verified finding | Recommended minimal fix | Owner |
|---|---|---|---|
| GOAL-ECDLP-001 | e6c1c9 queue: TASK-20260901-833888 budget wall_clock_seconds null — deliberate per the queue's own budget_amendment_note (per_task_resource_budgets amendment) but the dispatcher schema requires a positive number. RC-1 flow itself fully landed (snapshot 5d7cf2888, release 66d77efd7, ledger 164902220). | Lane owner resolves the schema/amendment conflict (give the archive task a positive nominal budget in a queue supersession) or advances the head to the B71-CRYPTO001-NEW-MECHANISM-20260902-2fb7f8 queue. | coordinator-ecdlp (LIVE — do not touch; flagged MSG-20260901-19ddae) |
| GOAL-AES-001 | Archive TASK-20260801-808 binds snapshot-receipt.json hash 7ae1d254…; file now d58e80de… (receipt last touched 2026-08-01 22:50Z). Receipt was re-bound post-archive (precedent: 8058c8731 rebind-after-fix pattern). | Verify current receipt content is the legitimate final one; then a supersession record re-binding the expected hash. Do not edit the receipt. | AES-001 lane |
| GOAL-CRYPTO-001 | Historical schema: completed producer TASK-20260731-001 appears in the archive source lists of BOTH TASK-20260731-002 (snapshot) and TASK-20260731-004 (ledger); the current dispatcher rejects double assignment. All three tasks completed. | Supersession record documenting the double assignment as a historical archive pattern; do NOT rewrite completed archive bindings (rule 15). | CRYPTO-001 lane |
| GOAL-DIFFP-84d641 | Head-bound hash drift (systemic; head edited 2026-08-28 after archive). | Head reconciliation: advance the head to the live batch, or queue supersession re-binding the current head. | DIFFP lane |
| GOAL-DREG-001 | Head-bound hash drift, second-order (bound head path has no history — head moved paths). | Same as DIFFP; note the head-path move in the reconciliation. | DREG lane |
| GOAL-FAEST-001 | Archive TASK-20260731-013 commit path-set drift: declared set missing {its own receipt, TASK-20260731-012 sources_note, KN-LIT-7637/7638}; extra {TASK-20260731-002 receipt, TASK-20260731-001 sources_note, KN-LIT-7617/7618}. Reads as the archive commit bundling a neighbouring task's artifacts (or a queue transcribing the wrong task's set). | Diagnose which path set is the legitimate final state; supersession record. No binding rewrite. | FAEST lane |
| GOAL-ICEX-001 | Archive TASK-20260731-024 commit path-set drift: missing DEC-20260731-015.yaml, extra DEC-20260731-003.yaml. | Same as FAEST. | ICEX lane |
| GOAL-MD5-001 | Whole-queue schema drift: every task's handoff.constraints is an empty list (faithful — the envelopes themselves carry empty constraints, e.g. TASK-20260822-f95c7c) and at least one task's handoff field is a string reference where the current schema expects an envelope object. Queue predates the current validator requirements; one task failed_infrastructure (87c429). | Queue supersession adding coordinator-authored constraints + normalizing the handoff references, or head reconciliation to the live batch. Envelopes stay untouched. | MD5 lane |
| GOAL-MLKEM-005 | Head-bound hash drift (systemic; head edited 2026-08-31 after archive). | Same as DIFFP. | MLKEM-005 lane |
| GOAL-SIG-001 | Archive TASK-20260725-712 commit path-set drift: missing EV-SIG-010.yaml, extra EV-SIG-007.yaml. | Same as FAEST. | SIG lane |
| GOAL-ECQ-e72c0b | Head-bound hash drift (systemic). NOTE: the ECQ lane's session (coordinator-ecq-4) released TASK-20260831-b83032 failed on 2026-09-01 with runtime exhaustion (claude weekly limit / subagent balance dead) — the lane may be orphaned; treat as available for takeover after the ECDLP/ECQ sessions' state is confirmed. | Same as DIFFP. | ECQ lane / standing harness (if orphaned) |
| GOAL-ENDO-001 | tasks[4].archive.path_sha256 for the closed batch's ledger-receipt.json is NULL (not a case issue — the value is absent); actual file hash 112e8076c6260dffa84c61a56a5f8d6227e43bcaf22d9c4b76f539d543d91eea. Batch bde652 is CLOSED (DEC-20260830-93c01b, scoped REVISE). | Supersession record re-binding the receipt hash after verifying the receipt content is the final one. No edit of the receipt. | ENDO lane |
| GOAL-MCE-001 | State-machine gap: claim-relevant producer TASK-20260809-3e30b8 completed and reviewed, but the queue requires a ledger archive after review that was never opened. | Open a small coordinator archive batch for MCE-001 (requires reading that goal's review record first). | MCE lane |

## What this record deliberately does NOT do

- Rewrites no completed archive binding, receipt, or envelope (core rules 4, 15).
- Advances no goal head or queue state (those are the owning lanes' Coordinator acts).
  Lane liveness at triage time: GOAL-ECDLP-001 confirmed live (direct message
  MSG-20260902-e9b256); GOAL-ECQ-e72c0b last active 2026-09-01T16:5xZ with a
  runtime-exhaustion release (likely orphaned); the other eleven lanes show no
  recent activity on any pushed branch.
- Does not treat the 13-goal bucket as a harness-wide integrity failure: the error shapes
  are heterogeneous (hash drift, path-set drift, schema drift, one state-machine gap, one
  live-lane conflict) and the repository's ledger otherwise validates — this is aged
  per-goal coordination debt, concentrated in batches from 2026-07-25 to 2026-08-28.

## Suggested execution order for a remediation session (ranked)

1. GOAL-ECQ-e72c0b (possibly orphaned lane; systemic-pattern fix unblocks it fastest).
2. GOAL-MCE-001 (state-machine gap; blocks any further MCE progress).
3. Systemic-pattern four (DIFFP, DREG, MLKEM-005, ECQ) via head reconciliation.
4. Path-set-drift three (FAEST, ICEX, SIG) — needs per-commit diagnosis.
5. Schema/None-binding three (MD5, ENDO, AES-001) — supersession records.
6. GOAL-CRYPTO-001 — historical pattern; lowest priority, purely render-blocking.
7. GOAL-ECDLP-001 — leave to its live lane (already flagged).
