# Opening snapshot — TASK-20260905-038574

Self-neutral content binding for the BATCH-aedb4e opening scaffold: the
batch queue, the three handoffs, the launch note, and the preflight
record. This receipt's own path is self-neutral (null hash and size before
commit). It asserts no design outcome and no scientific claim; the design
itself is TASK-20260905-82fd16 and may not start before this archive
verifies. No execution is admitted by this batch.

Binding (sha256 of the working-tree bytes at staging time):

```json
{
  "receipt_kind": "opening_snapshot_binding",
  "task_id": "TASK-20260905-038574",
  "batch_id": "BATCH-aedb4e",
  "record_ids": ["BATCH-aedb4e", "TASK-20260905-038574"],
  "expected_parent": "c8d05da9eaaf505d13d12335aa0daddeccacf23a",
  "path_sha256": {
    "ledger/handoffs/TASK-20260905-82fd16.yaml": "607ce354b723f863d09f2cb7a4d727e0e2c1b92d55d3d29a03ae3fb3582b4917",
    "ledger/handoffs/TASK-20260905-038574.yaml": "2cb4b79c04e22ea1134c8b66d016294ad48d4e7c4d99318784fcd8db7f77ffd1",
    "ledger/handoffs/TASK-20260905-efaece.yaml": "19981afedb62d4ea409e81cb1b779badf91974e6846b296a66e7fdb1ccc78071",
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-aedb4e/launch.md": "c292abb6f8508f7f37b01643b8b4fde3ff67d244c7a1173d72c33ff602116c73",
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-aedb4e/preflight.json": "d959eaf325f46d8cbd040eaadaa34c04c0327f0df6a1e76772a55d57d5e580bd",
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-aedb4e/dispatch_queue.json": "706d90c8d63cf91798f5179056cfe9aca69fa044483a8337b52095279773c539"
  },
  "self_path": "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-aedb4e/archives/TASK-20260905-038574/snapshot.md",
  "self_sha256": null,
  "self_size": null
}
```

Post-commit verification (parent, exact changed-path set, hash preservation,
reachability from HEAD, commit-message task and record IDs) is recorded in
the binding commit for the queue archive block.
