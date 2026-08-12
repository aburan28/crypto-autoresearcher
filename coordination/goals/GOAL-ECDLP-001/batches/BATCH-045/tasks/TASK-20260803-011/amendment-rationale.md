# Amendment rationale — TASK-20260803-011

**Amendment ID:** `PA-IT-001-v3-rc45-repair-5`  
**Experiment:** `EXP-IT-001` / `H-IT-001` / `GOAL-ECDLP-001`  
**Batch:** `BATCH-045`  
**Closes:** `RT-20260803-005` (DEC-20260803-001) blockers RT-044-Y1 and RT-044-M2  
**Supersedes:** `PA-IT-001-v3-rc44-repair-4`  
**Does not edit:** `specification.v3.yaml`, prior overlays, or any run artifacts.

## RT-044 closures

| Blocker | Repair | Freeze |
|---------|--------|--------|
| Y1 | R5-FIX-Y1 | Quote colon-bearing acceptance scalars; `yaml.safe_load` succeeds. |
| M2 | R5-FIX-M2 | Present `recompute_null_plant_from_ledger.py` in proposal snapshot + manifest. |

RC-44 B1–B3 (`c_smart=8`, plant bits=20, density `{20,24,28}`) and RC-43
command/certificate/comparator/Pareto wording are preserved.

## Inventor-protocol fields

- **`dominated_by`:** Pollard rho at exponent ½.
- **`sota_delta`:** three axes `not_applicable` with explicit non-solver scope (design-only task).

## Scope / non-claims

Toy tier only. No Executor admission, experiment run, or H-IT-001 transition.
The null-recompute helper is a presence/integrity artifact for M2, not a
cryptanalytic result. Reserved run IDs unused here.
