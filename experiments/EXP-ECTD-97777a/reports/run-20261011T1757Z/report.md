# EXP-ECTD-97777a — run observation report

This is an observations-only execution report. The supervisor created the run envelope and stopped during the child-process pre-execution hook; the producer and checker did not execute, so there are no measured census values or scientific controls to interpret and no hypothesis, experiment, or goal status transition.

## Bound execution

- Goal: `GOAL-ECTD-001`
- Experiment: `EXP-ECTD-97777a`
- Frozen plan used: `experiments/EXP-ECTD-97777a/trial-plan-v2.json`
- Successor plan SHA-256: `02fa1006428ac942c2d8d01186023e3e6487af4cf2296315335bab211750cbd7`
- Original frozen plan: `experiments/EXP-ECTD-97777a/trial-plan.json`
- Dispatch correction: `CORR-20261011-f18bdf`
- Approved by: `DEC-20261010-5396de`
- Executor task: `TASK-20261011-4b3aad`, claim epoch 1
- Run: `RUN-ECTD-63f478`
- Run directory: `experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478/`
- Code commit recorded by the supervisor: `706a4117f7c3c04342b4d1f441ff220d1d3a124c`
- Host recorded by the supervisor: Darwin, Python 3.12.8
- Started: `2026-10-11T17:57:14.730264+00:00`
- Finished: `2026-10-11T17:57:14.744183+00:00`

The worktree had unrelated untracked coordination receipts and prior SSIQ failed-run directories. No tracked source or frozen-plan file was modified for this attempt. The executor write scope was limited to the designated run and report directories.

## Exact command and controls

The supervisor recorded this producer command:

```text
python3 experiments/EXP-ECTD-97777a/implementation/run.py --run-dir experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478
```

The planned checker command was:

```text
python3 experiments/EXP-ECTD-97777a/implementation/check.py experiments/EXP-ECTD-97777a/runs/RUN-ECTD-63f478
```

The frozen protocol parameters were not reached: the fixed ordinary field is `F_89`, with `a=b=1`, the declared unordered-pair eligibility/order, and the separate permutation-label null. The requested controls were therefore not measured. The producer and checker logs are empty, and `manifest.yaml` and `raw-result.json` were not created.

## Recorded outcome

The sealed receipt reports:

| Field | Recorded value |
|---|---|
| supervisor status | `infrastructure_error` |
| return code | missing (`null`) |
| checker return code | missing (`null`) |
| detail | `Exception occurred in preexec_fn.` |
| stdout/stderr | empty |
| checker stdout/stderr | empty |
| scientific conclusion | `null` |

The stop occurred before the producer process began. The receipt is an operational record of this launch attempt, not a measurement of the affine-pair condition.

## Visual record

There are fewer than two comparable recorded values, so the accompanying SVG is a pipeline diagram rather than a numerical graph. It shows the frozen plan, supervisor envelope, pre-execution stop, and the absent producer/checker outputs. The diagram is derived only from `launch.json`, `environment.json`, `execution-receipt.json`, and the empty logs in `RUN-ECTD-63f478`.

The source data for the diagram is [`graph-data.json`](graph-data.json), and the rendered diagram is [`graph.svg`](graph.svg). The PDF embeds the same diagram.

## Artifact pointers

- [Run directory](../../runs/RUN-ECTD-63f478/)
- [Execution receipt](../../runs/RUN-ECTD-63f478/execution-receipt.json)
- [Launch envelope](../../runs/RUN-ECTD-63f478/launch.json)
- [Environment receipt](../../runs/RUN-ECTD-63f478/environment.json)
- [Dispatch correction](../../../../../../ledger/corrections/CORR-20261011-f18bdf.yaml)
- [Successor plan](../../trial-plan-v2.json)
- [Rendered PDF](report.pdf)
