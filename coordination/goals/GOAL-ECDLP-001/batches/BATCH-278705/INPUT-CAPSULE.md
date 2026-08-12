# BATCH-278705 input capsule

## Authoritative decision boundary

`DEC-20260803-004` closed `BATCH-046` as inconclusive for the RC-45 smoke
transfer-gate interpretation. It requires a successor with live anomalous and
null controls, fresh provenance, Pareto fields, and measure only after smoke
controls pass. It does not authorize a replay of the immutable RC-45 package.

## Immutable inputs

- `ledger/decisions/DEC-20260803-004.yaml`
- `ledger/evidence/EV-IT-008.yaml`
- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc45-repair-5.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-046/reviews/TASK-20260803-021/validation_report.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-046/reviews/TASK-20260803-022/red_team_report.yaml`

These files are read-only inputs. The author must not edit or reuse their
historical run, result, output, manifest, or provenance paths.

## Future-path requirements for the proposal

The proposed amendment must reserve fresh future paths distinct from all RC-45
paths, including at minimum:

- `RUN-IT-001-rc46-smoke` and `RUN-IT-001-rc46-measure`;
- run records beneath `experiments/EXP-IT-001/runs/RUN-IT-001-rc46-*`;
- results beneath `experiments/EXP-IT-001/results/rc46/`; and
- task-local execution provenance beneath a future, separately allocated
  successor batch.

Those paths are specifications for later work only. No such artifact is
created, run, or frozen in `BATCH-278705`.

## Prohibitions

- Do not execute Sage or any experiment.
- Do not write implementation, run, result, output, or provenance artifacts.
- Do not change hypothesis, experiment, evidence, decision, or goal status.
- Do not claim a solver result, relation, transfer, asymptotic gain, or
  cryptanalytic improvement.
