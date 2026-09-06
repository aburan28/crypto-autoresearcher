# Opening snapshot — TASK-20260905-4194e7

Self-neutral content binding for the BATCH-58df35 opening scaffold: the
batch queue, the five handoffs, the launch note, and the preflight record.
This receipt's own path is self-neutral (null hash and size before commit).
It asserts no approval and no scientific claim; the approval itself is
TASK-20260905-91ca91 and the execution is TASK-20260905-f615a7, neither of
which may start before this archive verifies.

Binding (sha256 of the working-tree bytes at staging time):

```json
{
  "receipt_kind": "opening_snapshot_binding",
  "task_id": "TASK-20260905-4194e7",
  "batch_id": "BATCH-58df35",
  "record_ids": ["BATCH-58df35", "TASK-20260905-4194e7"],
  "expected_parent": "8c82d36ee332056a3c6ade08a02a888dfcaf6081",
  "path_sha256": {
    "ledger/handoffs/TASK-20260905-4194e7.yaml": "cccce87458856e059c78b180f71aa46f814527e5db7d802167af4f4eddcbb589",
    "ledger/handoffs/TASK-20260905-91ca91.yaml": "112d9107ed88c652d4d047bad70c4ffb2c37209178da86e8cb0bc2093e601cb8",
    "ledger/handoffs/TASK-20260905-f615a7.yaml": "5c44504c394daf0e218d653e9365793c43ea31190d8b90744d025f5d29a7341c",
    "ledger/handoffs/TASK-20260905-6b4607.yaml": "cd2c6c724e057ca31531268383a83e5d98a7aaec1a7022363c21251e8e5be7d0",
    "ledger/handoffs/TASK-20260905-3bcd97.yaml": "20d45d0f4de4f882eb8d02783f82efe2a298e818bc0d6ebbd9bbd874946cfef6",
    "coordination/goals/GOAL-ECRANK-002/batches/BATCH-58df35/launch.md": "816c54d7d988dcb1a2fedb521f445e2808242385d237036cc8e733c75b3597f2",
    "coordination/goals/GOAL-ECRANK-002/batches/BATCH-58df35/preflight.json": "94e93cafc3532246c4c689c150ed39653ed1724a9e86df64b615d093bc85b0f1",
    "coordination/goals/GOAL-ECRANK-002/batches/BATCH-58df35/dispatch_queue.json": "85de84fd9ece2f8f120407b8c56fca2bbe271b21eaa64e17539d808e2eb20947"
  },
  "self_path": "coordination/goals/GOAL-ECRANK-002/batches/BATCH-58df35/archives/TASK-20260905-4194e7/snapshot.md",
  "self_sha256": null,
  "self_size": null
}
```

Post-commit verification (parent, exact changed-path set, hash preservation,
reachability from HEAD, commit-message task and record IDs) is recorded in
the binding commit for the queue archive block.
