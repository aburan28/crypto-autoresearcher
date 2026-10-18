# Approved native execution handoff

DEC-20261018-083171 approves the exact four prospectively accepted metadata-compatible successor packages. Native source archive08bf7ced7, terminal raw archive127a6a66f and approval archivec41f64db5 verify against actual Git. All four ordinary selector rows are ready; native dispatch reports all11 gates true. The native supervisor status reports one planned, unexecuted trial per new experiment.

Original invalid runs remain immutable, with no scientific interpretation or hypothesis/goal status change. These are deterministic reproductions/calibrations, not new confirmatory mathematical data. The new wrapper adds provenance and native metadata without changing the old raw bytes, fixture or algorithms. Implementation-tier route is explicit; no director runbook or model attestation is claimed.

Raw original records127a6a66f were confirmed published in origin tracking refs before report archival. Approval publication must also be confirmed before a fresh claim; the live supervisor independently enforces committed/published inputs and live published claim ownership.

Shared queue: `coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/dispatch_queue.json`. Execute serially in its priority order:

| New EXP | Executor task | Fresh RUN | Original EXP |
| --- | --- | --- | --- |
| EXP-ECDLP-3521b9 | TASK-20261018-744219 | RUN-ECDLP-03ccb4 | EXP-ECDLP-bfbe6f |
| EXP-ECDLP-087aea | TASK-20261018-e0ee60 | RUN-ECDLP-42ded6 | EXP-ECDLP-5f4f14 |
| EXP-ECDLP-11c54d | TASK-20261018-9661ac | RUN-ECDLP-d9188a | EXP-ECDLP-3c166b |
| EXP-ECDLP-5d6ec1 | TASK-20261018-f4abf9 | RUN-ECDLP-6671fe | EXP-ECDLP-20ac31 |

For each corresponding EXP/TASK (commands run from repository root):

```sh
python3 tools/newest_experiments.py --experiment EXP --json
python3 tools/research_dispatch.py coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/dispatch_queue.json --ready-only --claims refs
python3 tools/goal_lanes.py claim coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/dispatch_queue.json TASK --as executor-ideas-20261018 --ttl-minutes 10 --publish
python3 tools/experiment_execution.py run --plan experiments/EXP/trial-plan.json --owner executor-ideas-20261018 --epoch ACTUAL_RETURNED_EPOCH
python3 tools/goal_lanes.py release coordination/goals/GOAL-ECDLP-001/batches/BATCH-7ddcd6/dispatch_queue.json TASK --as executor-ideas-20261018 --outcome ACTUAL_OUTCOME --note ACTUAL_OBSERVATION --publish
```

Use the new claim's actual returned epoch, never a presumed1 or an old epoch. A release outcome is completed only for actual validated output; otherwise retain the observed failure and release failed/abandoned as appropriate. No force, old slot reuse, output overwrite, or gate bypass.

Native source-wrapper checker calls and the manifest gate determine operational validity; their acceptance is not independent scientific review or an execution proof. Preserve all observations, including a premise miss or unchanged historical matrix miss. The implementation problem remains investigating until all four fresh native outputs satisfy its stated exit conditions.

[Approval receipt](approval-archive-receipt.json), [ordinary selector readiness](gates/successors-ready.json), [native dispatch](gates/approved-dispatch.json), [original reports](../../../../../reports/ideas_execution_20261018/README.md).
