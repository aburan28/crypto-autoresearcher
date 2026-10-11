# EXP-FROB-ad6a6d — run observation report

This is an observations-only execution report. The supervisor created the run envelope and stopped in the child-process pre-execution hook; the FROB producer and checker did not execute, so no field or chord-image values were measured and no research state changed.

## Bound execution

- Goal: `GOAL-FROB-6333a9`
- Experiment: `EXP-FROB-ad6a6d`
- Successor plan: `experiments/EXP-FROB-ad6a6d/trial-plan-v2.json`
- Successor plan SHA-256: `05f75ed52fec0a26c6d8e237a8ed2a732278e05a128870cc805be87e56007581`
- Dispatch correction: `CORR-20261011-954734`
- Approved by: `DEC-20261006-a7f0c6`
- Executor task: `TASK-20261011-afcf52`, claim epoch 1
- Run: `RUN-FROB-026551`
- Code commit recorded by the supervisor: `a81604effbc06c2dc4ddbb0f1177864f5c0cce89`
- Host: Darwin, Python 3.12.8
- Started: `2026-10-11T18:04:46.154727+00:00`
- Finished: `2026-10-11T18:04:46.166438+00:00`

## Exact command and controls

Producer:

```text
python3 experiments/EXP-FROB-ad6a6d/implementation/run.py --run-dir experiments/EXP-FROB-ad6a6d/runs/RUN-FROB-026551
```

Checker:

```text
python3 experiments/EXP-FROB-ad6a6d/implementation/check.py experiments/EXP-FROB-ad6a6d/runs/RUN-FROB-026551
```

The frozen F_7^3 field construction, 343-element enumeration, slope-image comparison, and declared controls were not reached. Producer and checker logs are empty; `manifest.yaml`, `raw-result.json`, and `reading.yaml` were not created.

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

The stop occurred before the producer process began. This receipt records an operational launch boundary, not a field-image observation.

## Visual record

Zero comparable measurements were recorded, so the accompanying SVG is an execution-boundary diagram rather than a numerical graph. Its source data is [`graph-data.json`](graph-data.json); it is derived from the sealed launch, environment, receipt, and empty logs for `RUN-FROB-026551`.

- [Run directory](../../runs/RUN-FROB-026551/)
- [Execution receipt](../../runs/RUN-FROB-026551/execution-receipt.json)
- [Rendered PDF](report.pdf)
