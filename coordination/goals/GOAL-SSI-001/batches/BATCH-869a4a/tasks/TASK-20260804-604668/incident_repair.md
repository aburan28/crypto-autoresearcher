# BATCH-869a4a SSI incident-repair snapshot design

Date: 2026-08-04
Producer: `TASK-20260804-604668`
Classification: evidence-integrity repair design only

## Immutable commit audit

The immutable failed BATCH-d15fe0 control snapshot commit is
`c1679c48539c235364629b53cf4ae334b206d123`.

Its subject is:

```text
research: snapshot TASK-20260804-828d37 TASK-20260804-225f8c GOAL-SSI-001 BATCH-d15fe0
```

The commit correctly changed the 14 declared control-plane paths. Its first
parent and the 13 producer source hashes were verified. The dispatch verifier
nevertheless rejects it because that subject omits
`TASK-20260804-1bb7f0` and `TASK-20260804-52732e`.

Those two IDs were incorrectly included in
`TASK-20260804-828d37`'s `archive.record_ids` even though they were only
future tasks. The failure is therefore a commit-message identifier failure,
not a content, parent, or source-hash failure.

This is an evidence-integrity failure. It is not mathematical, cryptanalytic,
experimental, security, or negative evidence. BATCH-d15fe0's planned proposal
chain remains unexecuted and must not be treated as eligible.

No amendment or rewrite is prescribed for
`c1679c48539c235364629b53cf4ae334b206d123`.

## Fresh snapshot requirement

`BATCH-869a4a` creates exactly these three producer paths:

1. `coordination/goals/GOAL-SSI-001/batches/BATCH-869a4a/tasks/TASK-20260804-604668/incident_repair.md`
2. `coordination/goals/GOAL-SSI-001/batches/BATCH-869a4a/task-cards/TASK-20260804-604668.md`
3. `ledger/handoffs/TASK-20260804-604668.yaml`

The sole queued archive task, `TASK-20260804-cb3044`, must run alone and
commit exactly those three paths plus
`coordination/goals/GOAL-SSI-001/batches/BATCH-869a4a/archives/TASK-20260804-cb3044/snapshot_commit_receipt.json`.
Its commit message must contain all of:
`TASK-20260804-cb3044`, `TASK-20260804-604668`, `GOAL-SSI-001`, and
`BATCH-869a4a`.

Its `archive.record_ids` contains only `TASK-20260804-604668`,
`GOAL-SSI-001`, and `BATCH-869a4a`; it contains no future task ID.
The receipt's commit, parent, and path-hash bindings remain null or empty until
that future archive runs and the dispatcher accepts it.

## Boundary and next action

This repair batch creates no pause decision or research-state transition, and
no proposal, evidence, decision, execution, data, experiment, run, or SSI
conclusion.

After a successful repair snapshot, open a newly-ID'd fresh SSI ideation
control plane with minimal archive record IDs and do not use BATCH-d15fe0 as
authority.
