# Native execution handoff for two approved three-output reproductions

Source archive ac7675823a379fde6fb3a2b872bfa6ea5aaa0d60 contains the exact new helper and review_required packets. Both actual published-source preapproval reports accepted the exact final bytes under DEC-20261018-ca4056. Approval publication, ordinary selector readiness and fresh published native claims remain mandatory. Original failures stay invalid; no scientific status is promoted.

Queue: `coordination/goals/GOAL-ECDLP-001/batches/BATCH-5b3b39/dispatch_queue.json`.

| EXP | TASK | RUN | Original |
| --- | --- | --- | --- |
| EXP-ECDLP-ee406e | TASK-20261018-eeb8cc | RUN-ECDLP-4110e6 | EXP-ECDLP-f34097 |
| EXP-ECDLP-5c8854 | TASK-20261018-39dae2 | RUN-ECDLP-67ed93 | EXP-ECDLP-903c48 |

For each corresponding EXP/TASK, serially:

```sh
python3 tools/newest_experiments.py --experiment EXP --json
python3 tools/research_dispatch.py coordination/goals/GOAL-ECDLP-001/batches/BATCH-5b3b39/dispatch_queue.json --ready-only --claims refs
python3 tools/goal_lanes.py claim coordination/goals/GOAL-ECDLP-001/batches/BATCH-5b3b39/dispatch_queue.json TASK --as executor-ideas-20261018 --ttl-minutes 10 --publish
git fetch origin refs/heads/codex/execute-ic-ideas-20261018:refs/remotes/origin/codex/execute-ic-ideas-20261018
python3 tools/experiment_execution.py run --plan experiments/EXP/trial-plan.json --owner executor-ideas-20261018 --epoch ACTUAL_RETURNED_EPOCH
python3 tools/goal_lanes.py release coordination/goals/GOAL-ECDLP-001/batches/BATCH-5b3b39/dispatch_queue.json TASK --as executor-ideas-20261018 --outcome ACTUAL_OUTCOME --note ACTUAL_OBSERVATION --publish
```

Use actual fresh epochs. Release completed only after actual native output_validated, otherwise retain/release the actual failure. Both exact plan command arrays already contain the process-local Git setting and actual Python executable. Do not edit source, plan, frozen outputs or retry a consumed slot.

Leave each13-file raw tree uncommitted for its declared Coordinator exact14-path snapshot, then reports follow raw publication. Each fresh timed legacy result/RESULTS/manifest is retained exactly as newly produced; do not compare fresh timing bytes for equality to a separate old run. This is metadata engineering reproduction only.
