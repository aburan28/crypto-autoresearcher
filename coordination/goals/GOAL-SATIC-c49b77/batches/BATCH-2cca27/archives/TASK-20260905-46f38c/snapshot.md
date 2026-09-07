# Review snapshot — TASK-20260905-46f38c

Self-neutral content binding for the TASK-20260905-5681fc review producer
artifacts: an early startup receipt (start.json) and a durable final report
(report.json) recording a POLICY REFUSAL. The serving session
(vllm/qwen3.8-27b, local backend) could not honour review-adversarial at
xhigh requested effort: the policy is unbound on the local backend
(model-bindings) and its only table resolution is anthropic:claude-opus-5
at xhigh, which is uncredentialed in this environment (ANTHROPIC_API_KEY
unset); no fallback or degradation was granted, so the reviewer correctly
refused before check 1 per the contract's own mandated path. No
receipt-integrity verdict was reached; the known-bad control was not run
(recorded, not silently omitted). This receipt's own path is self-neutral
(null hash and size before commit). It asserts no review outcome and no
scientific claim; disposition is TASK-20260905-2fadfb.

Producer claim: epoch 1, owner coordinator-satic-2, released as failed at
2026-09-05T20:43:20Z, not expired. Producer terminal window:
2026-09-05T20:19:01Z to 2026-09-05T20:29:02Z (601 s, within the 1800 s
budget); start.json written inside the 120 s early-receipt window.

Binding (sha256 of the working-tree bytes at staging time):

```json
{
  "receipt_kind": "review_snapshot_binding",
  "task_id": "TASK-20260905-46f38c",
  "source_task_ids": ["TASK-20260905-5681fc"],
  "batch_id": "BATCH-2cca27",
  "record_ids": ["TASK-20260905-5681fc"],
  "expected_parent": "a028fde7825b703c711b5246f6167baebd3dad77",
  "path_sha256": {
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/tasks/TASK-20260905-5681fc/start.json": "074d846a565d39908fa029717cf655e364604ac1cf602216871730bb2ee9b31d",
    "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/tasks/TASK-20260905-5681fc/report.json": "c5e08dcae74b9974d5f747c5c35048dd12c193c251f07c52769d096f451306a8"
  },
  "self_path": "coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/archives/TASK-20260905-46f38c/snapshot.md",
  "self_sha256": null,
  "self_size": null
}
```

Post-commit verification (parent, exact changed-path set, hash preservation,
reachability from HEAD, commit-message task and record IDs) is recorded in
the binding commit for the queue archive block.
