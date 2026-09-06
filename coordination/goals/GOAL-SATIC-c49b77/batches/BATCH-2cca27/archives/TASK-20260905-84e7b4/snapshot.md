# Opening snapshot — TASK-20260905-84e7b4

Self-neutral content binding for the BATCH-2cca27 opening scaffold: the
approval decision DEC-20260905-ed0e18, the frozen integrity-review
contract, the batch queue, the four handoffs, the launch note, and the
preflight record. This receipt's own path is self-neutral (null hash and
size before commit). It asserts no review outcome and no scientific claim;
the review itself is TASK-20260905-5681fc and may not start before this
archive verifies.

Binding (sha256 of the working-tree bytes at staging time):

```json
{
  "receipt_kind": "opening_snapshot_binding",
  "task_id": "TASK-20260905-84e7b4",
  "batch_id": "BATCH-2cca27",
  "record_ids": ["DEC-20260905-ed0e18", "BATCH-2cca27", "TASK-20260905-84e7b4"],
  "expected_parent": "5aebb73f117e60dfad065b4af850f7b86a0193b3",
  "path_sha256": {
    "ledger/decisions/DEC-20260905-ed0e18.yaml": "a0b19ccdef10411d267639780ece5423646bdfb2b68e771b42000efb7a16db6f",
    "ledger/handoffs/TASK-20260905-84e7b4.yaml": "ed455d108866fd5cc9e82e147a2d8a3ffa1654643bba81710bd0a80f1a6948fb",
    "ledger/handoffs/TASK-20260905-5681fc.yaml": "36e8bad310a48c06e221eeceee80d2903db35df895991aa3d285af20e2ef1a06",
    "ledger/handoffs/TASK-20260905-46f38c.yaml": "a0e2c04e963fc078c5b5d6693e217980a00817de042b04808536c5d282f428fd",
    "ledger/handoffs/TASK-20260905-2fadfb.yaml": "036e597b2b015d2a36175aed8f7b204f08fad0b183a0f38db376794f3ab4c111",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/launch.md": "29619373ddd2dbf9407f96674e0cbd6f0869b86380734cc7950290790cc0419c",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/preflight.json": "48714f9404e5ef890e61179c62f26bebd2dadb13f40923656a21f9b672e91fe5",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/dispatch_queue.json": "19506a82f27c99672d560c3a339f85e412ee07581c4549f5377f5b6966bab576",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/contracts/integrity-review.json": "8589f1280cfae7891f254851c1297d2cf76a9e7a98df9948f974fa06bc815ab0"
  },
  "self_path": "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/archives/TASK-20260905-84e7b4/snapshot.md",
  "self_sha256": null,
  "self_size": null
}
```

Post-commit verification (parent, exact changed-path set, hash preservation,
reachability from HEAD, commit-message task and record IDs) is recorded in
the binding commit for the queue archive block.
