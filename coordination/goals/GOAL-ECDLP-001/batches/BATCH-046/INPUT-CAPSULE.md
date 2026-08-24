# BATCH-046 input capsule — Executor

## Bound contract

- `experiments/EXP-IT-001/specification.v3.yaml` (immutable)
- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc45-repair-5.yaml`
  (frozen at proposal snapshot `16f7b7bf8`; do not edit)
- Binding entrypoint:
  `experiments/EXP-IT-001/implementation/run_bounded_toy.py`

## Exact commands (frozen)

Smoke:
```
sage experiments/EXP-IT-001/implementation/run_bounded_toy.py --amendment experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc45-repair-5.yaml --run-id RUN-IT-001-rc45-smoke --mode smoke --seed 2026080304
```

Measure (if smoke package is snapshot-admissible and wall remains):
```
sage experiments/EXP-IT-001/implementation/run_bounded_toy.py --amendment experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc45-repair-5.yaml --run-id RUN-IT-001-rc45-measure --mode measure --seeds 2026080304,2026080305,2026080306
```

## Executor deliverables

Under `experiments/EXP-IT-001/runs/<run-id>/` and `results/` plus
`coordination/.../tasks/TASK-20260803-019/execution_report.yaml`.
Observations only — no support/reject conclusions.
