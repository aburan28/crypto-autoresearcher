# BATCH-94168f design and dispatch archives have no verified receipts

- **Status:** `open`
- **Kind:** archival custody gap; stale scheduling. No mathematical obstruction is claimed.
- **Affected work:** [original queue](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-94168f/dispatch_queue.json); [approved, unrun EXP-ICPERF-2f2e40](../experiments/EXP-ICPERF-2f2e40/specification.yaml); [supersession decision](../ledger/decisions/DEC-20261017-661369.yaml); [GOAL-ICPERF](../ledger/goals/GOAL-ICPERF-e6b6a4/goal.yaml).
- **Next action owner:** Coordinator, future handoff TASK-20261017-0c5730.
- **Last updated:** 2026-10-17

## Problem

The 2026-09-16 BATCH-94168f design and dispatch records exist in the tree, but the two snapshot receipts required by TASK-20260916-ec9948 and TASK-20260916-8d493b are absent at their declared paths. The original eight-card queue still has every task queued. Its approved EXP-ICPERF-2f2e40 v2 is unrun and cannot be dispatched from this incomplete chain. The first task being ready is an archival obligation, not evidence that its declared archive occurred.

## Evidence and uncertainty

- **Observed:** The [original queue](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-94168f/dispatch_queue.json) SHA-256 is `268a699dc3fb02a4a9159d67ab460752e48088d421f928b74618d7f1366bc0f1`; the nine first-snapshot and four second-snapshot source files exist, while `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-94168f/archives/TASK-20260916-ec9948/snapshot-receipt.json` and `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-94168f/archives/TASK-20260916-8d493b/snapshot-receipt.json` do not. All declared producer run, reviewer and final ledger outputs are absent. A read-only live-ref audit reported no task claims and one ready old archive card; the later archival task must repeat this check before scheduling correction.
- **Derived or proved:** Source-file presence cannot substitute for the missing archive receipt, first-parent binding, record IDs and independent verifier. Old approved status is preserved as written; it does not authorize a run through this lane.
- **Suspected explanation:** Unknown. The files may have been committed through historical PRs without the declared task receipts; an exact Git ancestry inventory is still needed.
- **Missing capability:** An independently checked content-at-commit custody repair for both original archival owners, followed by current protocol/readiness review before any experiment execution.
- **What this evidence does not establish:** No scientific result, negative relation finding, baseline speed or mathematical weakness. Cancelling old queue scheduling will not resolve the missing receipts.

## What would unblock it

- [ ] TASK-20261017-0c5730 inventories all thirteen source paths and the exact historical commits, checks both expected receipt locations and any alternative receipt without assuming one, and reports all SHA-256 values.
- [ ] A prospective Coordinator correction supplies lawful content-at-commit markers and separate verified receipts under TASK-20260916-ec9948 and TASK-20260916-8d493b, or an explicit superseding archival route accepted by the dispatcher without double-owning a record. It records any original admission deviation instead of backdating claims.
- [ ] Before EXP-ICPERF-2f2e40 executes, its v2 contract, implementation, current prospective preapproval, ordinary selector, fresh lane/claim and frozen independent review plan all pass.

These checks would restore custody and execution eligibility for the exact older PDP count experiment. They would establish no complete-cost IC improvement; relation yield, useful rank, linear algebra, target and rho comparisons remain separate.

## Next discriminating step

- **Action or proof obligation:** Dispatch TASK-20261017-0c5730 in a future lawfully opened lane to produce an exact thirteen-path Git inventory and two archive-repair specifications; snapshot its four outputs under TASK-20261017-9079db.
- **Inputs and controls:** Frozen original queue, nine design paths, four dispatch-package paths, expected receipt paths, and independent Git tree/hash readback.
- **Execution limits and stop condition:** Read-only archive audit, zero scientific runs. Stop on content mismatch, a newly discovered receipt, a live old-lane claim or an archive ownership collision.
- **Outcomes and next actions:** Exact matching bytes permit a prospective archive correction; differing bytes require a new versioned provenance decision; absent reachable commits or a verifier refusal keeps this problem open.
- **Recheck trigger:** New custody receipt, new source commit, or a proposed EXP-ICPERF-2f2e40 dispatch.

## Resolution and history

2026-10-17: Scheduling supersession proposed by DEC-20261017-661369; original bytes and scientific status are preserved. Unresolved.
