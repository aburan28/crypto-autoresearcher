# Ledger archive — TASK-20260905-e20317

Goal `GOAL-SATIC-c49b77` · Batch `BATCH-008925` · Kind `ledger`
Source task `TASK-20260905-2c383f` · Disposition `DEC-20260905-6e8621`
Owner `coordinator-satic-c49b77-276e` · Branch `cursor/satic-c49b77-imp1-recheck-276e`

## What this archive commits

Exactly the four paths this task's `write_scope` declares:

- `ledger/decisions/DEC-20260905-6e8621.yaml` — the disposition decision
- `coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-008925/report.md` — the batch report
- `coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-008925/archives/TASK-20260905-e20317/ledger.md` — this record
- `ledger/goals/GOAL-SATIC-c49b77.yaml` — the goal checkpoint, updated additively for this lane only

Record IDs named in the commit message: `TASK-20260905-e20317`,
`TASK-20260905-2c383f`, `DEC-20260905-6e8621`.

## Binding mode

`content_first`. The source task's two artifacts
(`tasks/TASK-20260905-2c383f/startup_receipt.json` and `report.json`) were
committed by the earlier snapshot `acb081203` and restored to their
release-bound bytes by `4172dca7f`; they are immutable and this commit does not
touch them. A `commit` binding would require one commit to change the whole
six-path archive-and-source set, which is not satisfiable for a ledger archive
whose sources were snapshotted earlier — and re-touching them is precisely the
error `dd8bb7d6f` made. Content-first binds every declared artifact byte at HEAD
instead, which is the pattern CLAUDE.md prescribes ("archive receipts bind to
CONTENT first") and which 91 queue files in this repository already use. A real,
reachable commit, its declared parent, and the archival message IDs remain
mandatory and are supplied.

## Base sync

`origin/main` was fetched at the start of this task. The branch
`cursor/satic-c49b77-imp1-recheck-276e` was created from `origin/main` and the
merge base with `origin/main` is `e6059f4de`. No merge was needed and none was
performed; nothing was rebased. The three commits this disposition relies on —
`acb081203`, `4172dca7f`, `725f084ca` — are all ancestors of both HEAD and
`origin/main`, which is why the assessed artifacts are published rather than
merely local.

## Content verification performed before staging

| Path | sha256 |
|---|---|
| `tasks/TASK-20260905-2c383f/report.json` | `8763fa8ecadda9c4a6dfc4a5d73ccc285afaa026050651701ecc3d0467639403` |
| `tasks/TASK-20260905-2c383f/startup_receipt.json` | `23cf173ef680275b18c4c54304c78548ad6c80147ff14fa77cd0d5f33a3125ed` |

Both equal the `artifact_sha256` values in
`claims/TASK-20260905-2c383f.2.release.json` exactly, and both equal the bytes
at snapshot `acb081203`. The artifact disposed of here is the release-bound
artifact.

## Ledger validator

Baseline before this task's writes: 29 errors, all under `GOAL-ECRANK-002`,
`EXP-ECDLP-bbb42f` and `EXP-ECRANK-76a70d`, inherited from `main`. A grep of the
full output for `satic` and `c49b77` returns nothing. Those errors are not this
task's and were not repaired. The check after staging must add no error naming a
file written here.

## Scope discipline

- No hypothesis status changed; `active_hypothesis_ids` remains empty.
- No scientific claim; `RQ-SATIC-1ae57a` untouched.
- No approved, frozen, or historical record overwritten. Two conflicts inside
  immutable records are **named** as requiring superseding records and are not
  performed: the `findings_summary` severity split inside the bound
  `report.json`, and `IMP-3`'s clause "IMP-1 therefore stays open".
- The blocked ledger stages `TASK-20260905-e2c12f` and `TASK-20260905-86ea49`
  remain blocked. `BATCH-2cca27`'s lane, registered on branch
  `satic-reconciliation-20260905` by another session, was not touched.
- Shared goal-head fields another lane reads (`current_batch_id`,
  `dispatch_queue_path`) were deliberately **not** advanced; see the decision's
  limitations.
- The goal head was not sharded. Sharding a record whose one identifier names
  two different impediments would freeze that collision into write-once shards.
- No `dispatch_plan.*` (gitignored) and nothing under `claims/` is staged.
- Nothing was pushed; the orchestrating session pushes.

## Queue backfill

The queue's archive block for this task carries `commit_sha: null`,
`parent_sha: null` and an empty `path_sha256`, which cannot be filled inside the
commit whose sha they record. It is backfilled in a second commit alongside the
task state, which is the established pattern in this repository, and the plan is
re-rendered afterwards to confirm `completed_archive_commits_verified` passes.
