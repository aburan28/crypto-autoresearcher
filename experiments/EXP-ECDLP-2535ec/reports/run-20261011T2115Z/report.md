# EXP-ECDLP-2535ec run report

This is an observation-only report for `RUN-ECDLP-b2d284`. It records the
supervisor path and its sealed infrastructure receipt; it does not assign
evidence strength, change the hypothesis or experiment state, or interpret a
scientific outcome.

## Scope and custody

- Goal: `GOAL-ECDLP-001`; question: `RQ-ECDLP-002`; hypothesis:
  `H-ECDLP-bd1572`; experiment: `EXP-ECDLP-2535ec`.
- Successor plan:
  `experiments/EXP-ECDLP-2535ec/trial-plan-v2.json`, SHA-256
  `2e9841e4fc754b4b5898bc1a1794eabd54d9ff468b2b188cfee3a90e689f74ae`.
- Correction: `CORR-20261011-d20976`; queue:
  `BATCH-1adefe`; executor task: `TASK-20261011-a71042`.
- Claim: owner `executor-ecdlp-2535ec`, epoch `1`; the claim was released as
  failed infrastructure after the sealed receipt was committed.
- Run-record commit: `111d82295f`; branch:
  `codex/run-csidh-7886f6-20261011`.
- The worktree had unrelated pre-existing untracked artifacts. The run commit
  staged only `experiments/EXP-ECDLP-2535ec/runs/RUN-ECDLP-b2d284/`.

## Requested command and trial accounting

Exact supervisor command:

```text
PYTHONPATH=. python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-2535ec/trial-plan-v2.json --owner executor-ecdlp-2535ec --epoch 1
```

The supervisor recorded the producer command as:

```text
python3 experiments/EXP-ECDLP-2535ec/implementation/run.py --d 3 4 5 --bits 30 40 --A 150 300 --Bs 512 2048 --seeds 1 2 3 --out <run_dir>
```

One trial was requested, zero completed, one failed at infrastructure setup,
and zero timed out. The supervisor loaded the plan, admitted the claim, and
created the run receipt. It then recorded `status: infrastructure_error` with
detail `Exception occurred in preexec_fn.` while installing the declared
address-space guard. The producer did not start; the checker did not start.

The recorded host was Darwin with Python 3.12.8. CPU time, hostname, and a
runtime lock hash were not present in the sealed environment record, so they
are missing rather than inferred. The first local invocation was rejected by
the linked-worktree Git lock permission boundary before supervisor admission;
the elevated retry reached the supervisor and produced the sealed receipt.

## Measurements and controls

No measurement rows, sample counts, arm yields, controls, manifest, or
`raw-result.json` were emitted. Consequently this report contains no
quantitative comparison or uncertainty calculation. The declared experiment
parameters remained in the recorded command: `d={3,4,5}`, `bits={30,40}`,
`A={150,300}`, `B_s={512,2048}`, and seeds `{1,2,3}`. These are requested
parameters, not measured values.

The visual beside this report is a pipeline diagram rather than a quantitative
plot because the run produced fewer than two comparable values. Its editable
data are in `graph-data.json`; its rendered diagram is `graph.svg`. The
diagram records the queue, claim, supervisor, pre-execution guard, producer,
checker, and output states directly from
`runs/RUN-ECDLP-b2d284/execution-receipt.json` and the sealed launch receipt.

## Artifacts

- [pipeline diagram](graph.svg)
- [diagram data](graph-data.json)
- [execution receipt](../../runs/RUN-ECDLP-b2d284/execution-receipt.json)
- [launch receipt](../../runs/RUN-ECDLP-b2d284/launch.json)
- [environment](../../runs/RUN-ECDLP-b2d284/environment.json)
- [command](../../runs/RUN-ECDLP-b2d284/command.txt)
- [supervisor stderr](../../runs/RUN-ECDLP-b2d284/stderr.log)

The run is operationally incomplete, and the report records that boundary as
the observation. Any scientific interpretation belongs to a later independent
review/archive task.
