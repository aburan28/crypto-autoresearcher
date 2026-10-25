# Native execution handoff: seven exact approved metadata protocols

Source1113c5bcfc373af1bdbb1d045830db59d2362ba4 was published before every actual native preapproval returned approvable:true/blockers[]. Exact accepted bytes are approved under DEC-20261018-c4352a. Original science and failed receipts remain immutable.

Queue: `coordination/goals/GOAL-ECDLP-001/batches/BATCH-e7e584/dispatch_queue.json`. Every plan has two separately allocated RUNs. Six finite packets require independent primary routes; adjacent324080 uses dependent stages, with an explicitly weak legacy label/file-presence checker and no arithmetic certification.

| EXP | TASK | RUN A / stage0 | RUN B / stage1 | Source |
| --- | --- | --- | --- | --- |
| EXP-ECDLP-c0c520 | TASK-20261018-52a40e | RUN-ECDLP-36eff6 | RUN-ECDLP-f5bde2 | EXP-ECDLP-95f69f |
| EXP-ECDLP-615fcf | TASK-20261018-5da6e5 | RUN-ECDLP-7f3a18 | RUN-ECDLP-f8d192 | EXP-ECDLP-c9110e |
| EXP-ECDLP-c64491 | TASK-20261018-f7ea72 | RUN-ECDLP-40541f | RUN-ECDLP-fce7f4 | EXP-ECDLP-d68ac9 |
| EXP-ECDLP-524b38 | TASK-20261018-f7e5bc | RUN-ECDLP-762d8c | RUN-ECDLP-b80f30 | EXP-ECDLP-efafc0 |
| EXP-ECDLP-417a94 | TASK-20261018-c7b53a | RUN-ECDLP-40d618 | RUN-ECDLP-e3586e | EXP-ECDLP-f7310e |
| EXP-ECDLP-30277c | TASK-20261018-4bb176 | RUN-ECDLP-7727d1 | RUN-ECDLP-2d3b31 | EXP-ECDLP-3365b4 |
| EXP-ECDLP-324080 | TASK-20261018-652a61 | RUN-ECDLP-0f1a90 | RUN-ECDLP-5e5d13 | EXP-ECDLP-daee4d |

After exact approval publication, for the actual native-offered EXP/TASK only:

```sh
python3 tools/newest_experiments.py --experiment EXP --json
python3 tools/research_dispatch.py coordination/goals/GOAL-ECDLP-001/batches/BATCH-e7e584/dispatch_queue.json --ready-only --claims refs
python3 tools/goal_lanes.py claim coordination/goals/GOAL-ECDLP-001/batches/BATCH-e7e584/dispatch_queue.json TASK --as executor-ideas-20261018 --ttl-minutes 10 --publish
git fetch origin refs/heads/codex/execute-ic-ideas-20261018:refs/remotes/origin/codex/execute-ic-ideas-20261018
python3 tools/experiment_execution.py run --plan experiments/EXP/trial-plan.json --owner executor-ideas-20261018 --epoch ACTUAL_RETURNED_EPOCH
python3 tools/goal_lanes.py release coordination/goals/GOAL-ECDLP-001/batches/BATCH-e7e584/dispatch_queue.json TASK --as executor-ideas-20261018 --outcome ACTUAL_OUTCOME --note ACTUAL_OBSERVATION --publish
```

One exact native run command executes both fixed planned RUNs in order. Do not alter argv, add env wrappers/interpreter flags, retry a consumed slot or force any old prediction to match. Release completed only from actual required output_validated receipts. Leave raw uncommitted for its declared isolated snapshot (29paths per finite pair;25per adjacent pair), then yield the Git hold for archive/publication and operational queue completion before the next offered task. No archive-isolation bypass. Reports follow raw publication and every PDF page must be inspected.

The adjacent O-CONTROL-FAIL/O-IMPEDIMENT labels remain observations without positive/negative hypothesis inference. Its output_validated means faithful instrument/metadata preservation only. Candidate18membership stays unauthenticated; adjacent is explicit19th. No new scientific status, mathematical certificate or generic security/performance conclusion.
