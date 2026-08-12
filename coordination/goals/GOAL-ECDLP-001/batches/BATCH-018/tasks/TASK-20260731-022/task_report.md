# TASK-20260731-022 — Executor report (EXP-DS-001 v2)

**Role:** executor  
**Contract:** `experiments/EXP-DS-001/specification.v2.yaml` only  
**Authorization:** snapshot `65f3c82b` / DEC-20260731-003  

## Delivered

| Run | Status | Wall (s) | Notes |
|---|---|---|---|
| RUN-DS-001-impl | completed_valid | ~0.37 | 16/64/4 seed 101 smoke; planted-bug detected; rho DL cert verified |
| RUN-DS-001-measure | completed_valid | ~1152 | Full 3×3×2×3 = 54 cells; seeds 101–103; target 200 relations |
| RUN-DS-001-heur | completed_valid | ~18 | ≥1e5 intermediates at bits 16/20/24 |

Implementation: `ds001_driver.py`, `verify_certificates.py`, `implementation.md`.  
Results: `summary.json`, `R_table.json`, `HEUR_DS_1_report.json`, `null_control_report.json`.  
Formal YAML: `execution_report.yaml`.

## Metric observations (not decisions)

- **R / R_null:** 54/54 cells `completed_valid`; median R ≈ 0.043; 43 cells `S1_eligible_on_null_axis`; **0** `F2_eligible`; R-1 observation string `S1_eligible_observation`.
- **HEUR-DS-1:** RATE and KS fail at all three adequate bit sizes; TAIL pass; `F3_trigger_observation=true`.
- **Controls:** matched rho/BSGS recorded; null spec hashes recorded; CTRL-NULL-PLANT detected on impl.

Toy-tier only. No hypothesis status change. No crypto-scale claim.

## Snapshot handoff

**TASK-20260731-023 is unblocked.** Coordinator must run the snapshot archive alone, staging exactly `declared_commit_sets.TASK-20260731-023_snapshot_paths`. Exclude `_console.log`, `_PRESNAPSHOT_REL15_audit/`, `specification*.yaml`, amendments, and FAEST/XEDN/KN-FIND-010/STR logs.

Executor does **not** perform Validator (024), Red Team (025), or ledger (026).

## Deviations

See `implementation.md` and `execution_report.yaml` (point-sum backend proxy; planted targets; pre-snapshot measure regeneration after relations=15 race).
