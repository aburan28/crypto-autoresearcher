# Producer snapshot — TASK-20260907-e7cc96

Self-neutral content binding for TASK-20260907-39511d's known-bad-control run
package. This receipt freezes seven files as delivered, before any reviewer
opens any of them. It binds BYTES, not a result. It asserts nothing about
whether any instrument flagged a planted defect, whether any cell was
insensitive, whether the package is complete or defective, or whether the
frozen predicate's verdict will stand review. Independent review follows this
freeze. Any later record citing this snapshot as evidence of a sensitivity
outcome is misciting it.

**What is frozen.** The producer directory contains exactly the seven declared
paths and no other file. They are committed as found in the working tree. No
producer file was edited, completed, improved, or re-run at archive time. A
defect in the package, if any, is committed and routed to the reviewer.

**Scope, asserted here and not to be widened later.** This lane measures the
sensitivity of an archive-receipt verification procedure and nothing else. It
asserts NOTHING scientific about SATIC, summation polynomials, Semaev
polynomials, SAT encodings, solvers, or the ECDLP. Neither of
GOAL-SATIC-c49b77's completion criteria is met and this archive moves neither.
No hypothesis status changes. DEC-20260905-6e8621's impediment disposition
stands exactly as given.

**The mutation never entered the repository.** The corrupted copies live under
`/tmp/satic-kbc-BATCH-127c82/`, verified outside the checkout by git itself
(`git check-ignore -v /tmp` → `fatal: /tmp: '/tmp' is outside repository at
'/workspace'`). Nothing under that scratch root is staged. The producer's
declared `write_scope` contains only paths beneath its own task directory: no
receipt, no queue, no archive and no ledger path appears in it. This commit
adds only this archive receipt beside those seven files.

**Base checked before this commit.** `origin/main` was fetched at the start of
this task. Merge-base with `origin/main` is
`d48709b077ee0fd371700921d4be66795747ac03`, which equals `origin/main`. The
branch is already up to date; no merge was needed and none was performed.
Nothing was rebased. Expected parent of this snapshot is current HEAD
`c3a5be95d03895528c4e04519654a92edcc94f80` (the live claim for this task).
This receipt's own path is self-neutral (null hash, null size, null
`commit_sha` before commit); a value here would have to hash itself.

**Queue not staged.** `dispatch_queue.json` is outside this task's
`write_scope` and is not a source artifact of this archive (it was bound by
TASK-20260907-814b9f). Including it would add an undeclared extra path to a
`binding_mode: commit` archive whose expected set is the seven producer files
plus this receipt. The queue's archive block for TASK-20260907-e7cc96 therefore
stays `commit_sha: null` / empty `path_sha256` in this commit. Backfill of that
block is left to a later queue update, the same two-commit reason as
`4feb619f1` / `c94a71b47` except that here the queue is not in scope so the
second commit is not this task's.

**Not in the declared set, and why.**
`dispatch_plan.json` and `dispatch_plan.md` are gitignored generated artifacts
and are never staged. Nothing under `claims/` is staged. Nothing under
`/tmp/satic-kbc-BATCH-127c82/` is staged. No other archive receipt is staged.

Binding (sha256 of the working-tree bytes at staging time):

```json
{
  "receipt_kind": "producer_snapshot_binding",
  "task_id": "TASK-20260907-e7cc96",
  "source_task_ids": ["TASK-20260907-39511d"],
  "goal_id": "GOAL-SATIC-c49b77",
  "batch_id": "BATCH-127c82",
  "record_ids": [
    "GOAL-SATIC-c49b77",
    "BATCH-127c82",
    "TASK-20260907-39511d",
    "TASK-20260907-e7cc96"
  ],
  "binding_mode": "commit",
  "commit_sha": null,
  "expected_parent": "c3a5be95d03895528c4e04519654a92edcc94f80",
  "path_sha256": {
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-39511d/start.json": "3dc95e6e718945d47e9290f0fa90389168d97fd5dec162bf6274eb39885df37c",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-39511d/procedure.py": "f6771281581c96812fc7afae4eeeb57f65f27a17c340d410db6fd1d1cda6e96c",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-39511d/procedure_null.py": "e477db4938976b434092106032b3d43f7d84e16d9bc61d88e39f949533f8e2bf",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-39511d/procedure_promiscuous.py": "344c29605b90a2ec48978d46f5dc102170868f8b6fd14621822ff4c713c134e7",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-39511d/trials.json": "b218b42daa4dced0602b4d4e1504e305f89f1a90760ec2e5e030d71e6ec4bec2",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-39511d/commands.md": "19947c1837673d9a68a26c47788d2fb29dd4e0595f317bd737c190e41bd9fd26",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/tasks/TASK-20260907-39511d/report.json": "bb48ddb5afaa56ce2aeb894cb29b6a9243a12865da1340ccb9a42b8c9c964e68"
  },
  "self_path": "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/archives/TASK-20260907-e7cc96/snapshot.md",
  "self_sha256": null,
  "self_size": null,
  "scratch_root_not_staged": "/tmp/satic-kbc-BATCH-127c82/",
  "queue_not_staged": "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-127c82/dispatch_queue.json"
}
```

**Inference provenance.** Requested policy `coordinator-orchestration-code`;
configured binding `coordinator-orchestration-code -> anthropic:claude-opus-5
(effort=high)`, resolved by `python3 -m orchestration.adapter resolve --role
coordinator`; runtime a Cursor Cloud Agent session self-reporting Cursor Grok
4.6 (`cursor:grok-4.6`); both the configured binding and the runtime identity
are recorded; the requested policy was not substituted; `fallback_used` false;
`degraded_requirements` empty; `bedrock_used` false. **`model_verified` is
false** — this session did not run `doctor --probe`. A configured binding is
not verification and is not treated as one here.
