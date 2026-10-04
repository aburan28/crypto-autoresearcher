# Ledger archive — TASK-20260907-9b71ea

Goal `GOAL-SATIC-c49b77` · Batch `BATCH-127c82` · Kind `ledger`
Source tasks `TASK-20260907-6fbd6d`, `TASK-20260907-c3d2d8` · Disposition `DEC-20260907-6c6137`
Owner `coordinator-satic-c49b77-276e` · Branch `cursor/satic-c49b77-imp1-recheck-276e`

## What this archive commits

Exactly the six paths of this task's artifact ∪ source set:

- `ledger/decisions/DEC-20260907-6c6137.yaml` — the disposition decision
- `ledger/goals/GOAL-SATIC-c49b77.yaml` — additive BATCH-127c82 checkpoint
- `coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/archives/TASK-20260907-9b71ea/ledger.md` — this record
- `coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-6fbd6d/startup_receipt.json` — Validator startup receipt
- `coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-6fbd6d/report.json` — Validator report
- `coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-c3d2d8/disposition.json` — disposition worksheet

Record IDs named in the commit message: `TASK-20260907-9b71ea`,
`DEC-20260907-6c6137`, `GOAL-SATIC-c49b77`, `BATCH-127c82`.

## Binding mode

`commit`, self-neutral on this receipt. `commit_sha` and this file's own digest
are null before the commit: a value here would have to hash itself. The queue
`dispatch_queue.json` is outside this task's `write_scope` and is not staged.
If the queue archive block cannot live in this commit (self-hash), `commit_sha`,
parent, and the six path hashes are recorded after the commit for the
orchestrating session to backfill.

## Base sync

`origin/main` was fetched at the start of this task. Merge-base with
`origin/main` is `d48709b077ee0fd371700921d4be66795747ac03`, which equals
`origin/main`. The branch is already up to date (18 commits ahead, 0 behind);
no merge was needed and none was performed. Nothing was rebased. Expected
parent of this ledger commit is current HEAD
`e08a645eebc786c0fa0a060974af3bebe141e1c7` (the live claim for this task).
The merge digest over `d48709b..origin/main` is empty (no records, no goal
transitions). BATCH-008925 remains another session's open lane on
`satic-reconciliation-20260905`; the goal head was edited additively only.

## What the decision records (from the worksheet; rulings not changed)

- Four instrument verdicts by the frozen formula: A `partially_sensitive`,
  B `sensitive`, C `insensitive`, D `invalid`.
- A-T4/T5: formula detect=false AND otherwise-channel DispatchError recorded;
  predicate not relaxed.
- Validator J1–J4 all `holds` in a one-reviewer round.
- IMP-3 first condition SATISFIED, second UNTOUCHED, so IMP-3 does not clear.
- Nested IMP-1 stays cleared; top-level IMP-1 stays partially cleared; IMP-2
  out of scope. DEC-20260905-6e8621's disposition is not rewritten.
- Neither completion criterion met.
- No attestation that was not obtained; `model_verified` false.
- `knowledge_promotion`: not_warranted — a sensitivity measurement of a
  verification procedure is not a SATIC finding.

## Scope discipline

- No hypothesis status changed; `active_hypothesis_ids` remains empty.
- GOAL-SATIC-c49b77 stays `active`. `paused` and `blocked` are refused.
- No existing impediment text was changed.
- The two defects named for supersession are carried forward by reference
  and are not repaired.
- The goal head was not sharded.
- Shared fields `current_batch_id` and `dispatch_queue_path` still name
  BATCH-1a527c and were not advanced.
- `dispatch_plan.json` / `dispatch_plan.md` are gitignored and are never staged.
- Nothing under `claims/` is staged.
- The queue is outside write_scope and is not staged in this commit.

## Inference provenance

Requested policy `coordinator-orchestration-code`; configured binding
`coordinator-orchestration-code -> anthropic:claude-opus-5 (effort=high)`,
resolved by `python3 -m orchestration.adapter resolve --role coordinator
--policy coordinator-orchestration-code`; runtime a Cursor Cloud Agent session
self-reporting Cursor Grok 4.6 (`cursor:grok-4.6`); both the configured
binding and the runtime identity are recorded; the requested policy was not
substituted; `fallback_used` false; `degraded_requirements` empty;
`bedrock_used` false. **`model_verified` is false** — this session did not
run `doctor --probe`. A configured binding is not verification.

Binding (sha256 of the working-tree bytes at staging time; this file self-neutral):

```json
{
  "receipt_kind": "ledger_archive_binding",
  "task_id": "TASK-20260907-9b71ea",
  "source_task_ids": ["TASK-20260907-6fbd6d", "TASK-20260907-c3d2d8"],
  "goal_id": "GOAL-SATIC-c49b77",
  "batch_id": "BATCH-127c82",
  "record_ids": [
    "GOAL-SATIC-c49b77",
    "BATCH-127c82",
    "DEC-20260907-6c6137",
    "TASK-20260907-39511d",
    "TASK-20260907-6fbd6d",
    "TASK-20260907-c3d2d8",
    "TASK-20260907-9b71ea"
  ],
  "binding_mode": "commit",
  "commit_sha": null,
  "expected_parent": "e08a645eebc786c0fa0a060974af3bebe141e1c7",
  "path_sha256": {
    "ledger/decisions/DEC-20260907-6c6137.yaml": "7e89a86c9750b96422db4faf09efa9a1656c38548ddb8359bb8c109b9df51587",
    "ledger/goals/GOAL-SATIC-c49b77.yaml": "421d03a56f94d80e4b22d43865963927525d0781ecfc4ef788c1497954fa5297",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-6fbd6d/startup_receipt.json": "ee5558a1920ca7421d07c419331e630396277a63df3beb99e11aa575488f834e",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-6fbd6d/report.json": "2a27ea9f10614d004b5dcef5bef14d58b18a14adc26e8ab7af43b2e3356be6bb",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-c3d2d8/disposition.json": "4e78eb5c79ce4ab33db55ce5e85913e46a787b0abacf501e3cc4dac7def4ff64"
  },
  "self_path": "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/archives/TASK-20260907-9b71ea/ledger.md",
  "self_sha256": null,
  "self_size": null,
  "queue_not_staged": "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/dispatch_queue.json"
}
```
