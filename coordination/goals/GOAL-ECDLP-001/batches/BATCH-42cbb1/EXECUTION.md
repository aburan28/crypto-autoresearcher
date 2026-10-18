# Approved additive S3 reproduction

This fresh plan replaces only the pre-driver infrastructure failure EXP-ECDLP-3521b9 / RUN-ECDLP-03ccb4. The failed attempt stays unchanged. Native prospective preapproval accepted the exact new packet; publication and a new live claim remain required. This is in-sample metadata engineering reproduction, with no mathematical conclusion.

Queue: `coordination/goals/GOAL-ECDLP-001/batches/BATCH-42cbb1/dispatch_queue.json`. Executor task: `TASK-20261018-c32557`. New EXP: `EXP-ECDLP-4bb0ef`. New RUN: `RUN-ECDLP-25c448`. Native plan: `experiments/EXP-ECDLP-4bb0ef/trial-plan.json`.

Both frozen argv arrays already contain `env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.preloadIndex GIT_CONFIG_VALUE_0=false`. This changes only Git metadata index preloading, process-locally. Scientific source/fixture/counts and `memory_mb:256` stay fixed.

```sh
python3 tools/newest_experiments.py --experiment EXP-ECDLP-4bb0ef --json
python3 tools/research_dispatch.py coordination/goals/GOAL-ECDLP-001/batches/BATCH-42cbb1/dispatch_queue.json --ready-only --claims refs
python3 tools/goal_lanes.py claim coordination/goals/GOAL-ECDLP-001/batches/BATCH-42cbb1/dispatch_queue.json TASK-20261018-c32557 --as executor-ideas-20261018 --ttl-minutes 10 --publish
git fetch origin refs/heads/codex/execute-ic-ideas-20261018:refs/remotes/origin/codex/execute-ic-ideas-20261018
python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-4bb0ef/trial-plan.json --owner executor-ideas-20261018 --epoch ACTUAL_RETURNED_EPOCH
python3 tools/goal_lanes.py release coordination/goals/GOAL-ECDLP-001/batches/BATCH-42cbb1/dispatch_queue.json TASK-20261018-c32557 --as executor-ideas-20261018 --outcome ACTUAL_OUTCOME --note ACTUAL_OBSERVATION --publish
```

Use only the actual fresh epoch. A release is completed only after actual output_validated, otherwise failed/abandoned as appropriate. No retries or run edits. Coordinator owns the exact thirteen-path raw snapshot under `TASK-20261018-c21678`; leave raw files uncommitted until that snapshot. Reports follow raw publication and retain all original calibration readings.
