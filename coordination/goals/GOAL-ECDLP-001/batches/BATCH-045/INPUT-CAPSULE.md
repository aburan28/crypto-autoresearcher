# BATCH-045 input capsule

## Objective

Produce one new superseding amendment record for `EXP-IT-001` v3:
`PA-IT-001-v3-rc45-repair-5` that closes `RT-044-Y1` and `RT-044-M2` under
`DEC-20260803-001`, while preserving RT-314-B1..B3 closures from RC-44.

No Executor admission or experiment run may occur under this batch.

## Authoritative inputs

- `ledger/decisions/DEC-20260803-001.yaml` and `ledger/evidence/EV-IT-006.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-044/tasks/TASK-20260803-005/`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-044/tasks/TASK-20260803-007/synthesis.md`
- `experiments/EXP-IT-001/specification.v3.yaml`
- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc44-repair-4.yaml`
- `experiments/EXP-IT-001/implementation/` (read; may add only the missing
  `recompute_null_plant_from_ledger.py`)

## Mandatory closures

1. **RT-044-Y1 — YAML parse.** Every acceptance criterion that embeds a colon
   as prose MUST be a quoted YAML string so `yaml.safe_load` succeeds. Prove
   parseability in provenance.
2. **RT-044-M2 — null recompute presence.** Author
   `experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
   and list it in `implementation_archive_manifest`. Missing file at the
   proposal snapshot ⇒ contract_invalid. Do not claim presence without the
   blob in the snapshot.
3. **Preserve RC-44 substantive freezes.** Keep `c_smart=8`, pinned
   `anomalous_plant_bits=20`, restored density abscissa `{20,24,28}`, matched
   rho restatement, and RC-43 command/certificate/comparator/Pareto wording
   unless a quoted-string fix requires a non-semantic edit.

## Deliverables (TASK-20260803-011)

- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc45-repair-5.yaml`
- `experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-045/tasks/TASK-20260803-011/amendment-rationale.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-045/tasks/TASK-20260803-011/control-matrix.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-045/tasks/TASK-20260803-011/artifact-and-cost-plan.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-045/tasks/TASK-20260803-011/provenance.yaml`
