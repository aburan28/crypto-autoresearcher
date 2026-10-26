# Admission sequence

DEC-20261026-610781 authorizes only the additional owner log path
docs/session-logs/2026-10-26.md. Parent must expand the actual T-1 owner task
reservation before editing that path. No frozen handoff or source contract changed.

Actual expanded-scope receipt is present and Coordinator has recorded blocked
-> queued in the mutable dispatch queue with an additive gate receipt. Parent archives
and publishes this admission decision, new admission files and changed queue;
include exact hashes and actual commit/PR receipt without altering initial archive.
Do not rewrite initial dispatch-plan, orientation, publication-checkpoint or source files.
Generate current scheduling output under this admission directory.

Then claim the goal task (not while blocked):

```sh
python3 tools/goal_lanes.py claim coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/dispatch_queue.json TASK-20261026-589ad5 --ttl-minutes 240 --branch research/smallroot-owner-continuation-20261026 --worktree /workspace/crypto-autoresearcher --as executor-native-smallroot-ee839d
python3 tools/research_dispatch.py coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/dispatch_queue.json --ready-only --claims refs
```

Publish the actual claim and admission before native dispatch. Root maintains
Conductor lease independently; renewals are ownership protection, not research
budget. If goal max_concurrent2 is occupied, retain queued state and wait for
a lawful slot rather than take over another lane.

Executor must fully read current owner AGENTS and newest session log, and
read original native contract/card plus this additive scope decision. Append
only factual timestamped entries using the four required headings. No private
Conductor/session credentials or chat transcripts may enter either repository.
Native tool invocation must select gpt-6.1-sol/high from the published task
overlay, preserve Executor authority and report actual invocation/session
provenance. No scientific control/panel, root search or downstream review.
