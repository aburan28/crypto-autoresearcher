# EXP-ECTD-07b200 — run observation report

This is an observations-only execution report. The supervisor created the run envelope and stopped in the child-process pre-execution hook; the finite first-edge producer and checker did not execute, so no scan values or controls were measured and no research state changed.

## Bound execution

- Goal: `GOAL-ECTD-001`
- Experiment: `EXP-ECTD-07b200`
- Successor plan: `experiments/EXP-ECTD-07b200/trial-plan-v2.json`
- Successor plan SHA-256: `203be1dbc5b3209f0ac32d31d7fbf4f2a2460d06d352df155b62e71fd3fc0615`
- Original plan SHA-256: `6a4e4992dcc90f0449a473877cbe6c1a2f5a715e5bb98f6f6bc73a2c2ffecd9b`
- Dispatch correction: `CORR-20261011-9bb7aa`
- Approved by: `DEC-20261010-db0e4b`
- Executor task: `TASK-20261011-358a81`, claim epoch 1
- Run: `RUN-ECTD-e5714e`
- Code commit recorded by the supervisor: `2471dd7bf185233e26a8a416dbf55593367ea8e7`
- Host: Darwin, Python 3.12.8
- Started: `2026-10-11T18:00:35.662552+00:00`
- Finished: `2026-10-11T18:00:35.680239+00:00`

No tracked source or frozen-plan file was modified for this attempt. Unrelated pre-existing untracked coordination and SSIQ files were left untouched.

## Exact command and controls

Producer:

```text
python3 experiments/EXP-ECTD-07b200/implementation/run.py --run-dir experiments/EXP-ECTD-07b200/runs/RUN-ECTD-e5714e
```

Checker:

```text
python3 experiments/EXP-ECTD-07b200/implementation/check.py experiments/EXP-ECTD-07b200/runs/RUN-ECTD-e5714e
```

The frozen protocol’s finite prime limit, coefficient ranges, all-root scan, selection order, and p=3 handling were not reached. The requested first-edge, exact point-order, quotient, group, and scaling controls were not measured. Producer and checker logs are empty; `manifest.yaml` and `raw-result.json` were not created.

## Recorded outcome

| Field | Recorded value |
|---|---|
| supervisor status | `infrastructure_error` |
| return code | missing (`null`) |
| checker return code | missing (`null`) |
| detail | `Exception occurred in preexec_fn.` |
| stdout/stderr | empty |
| checker stdout/stderr | empty |
| scientific conclusion | `null` |

The stop occurred before the producer process began. This receipt records an operational launch boundary, not the first-edge hypothesis.

## Visual record

Because zero comparable measurements were recorded, the accompanying SVG is an execution-boundary diagram rather than a numerical plot. Its source data is [`graph-data.json`](graph-data.json); it is derived from the sealed launch, environment, receipt, and empty logs for `RUN-ECTD-e5714e`.

- [Run directory](../../runs/RUN-ECTD-e5714e/)
- [Execution receipt](../../runs/RUN-ECTD-e5714e/execution-receipt.json)
- [Rendered PDF](report.pdf)
