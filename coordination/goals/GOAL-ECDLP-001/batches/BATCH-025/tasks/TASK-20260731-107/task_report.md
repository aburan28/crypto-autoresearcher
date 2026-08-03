# TASK-20260731-107 — EXP-IT-001 RC-25b protocol amendment (B-1–B-4)

**Goal:** GOAL-ECDLP-001  
**Batch:** BATCH-025  
**Role:** coordinator  
**Amendment:** PA-IT-001-v2-rc25b-b1-b4  
**Parent freeze:** `303ae797` (v1)  
**NOT APPROVED commit:** `7dc2b39b` (TASK-106)  
**Queue amend:** QUEUE-AMEND-20260731-014  

## Disposition

Authored one protocol_amendment package discharging RT-20260731-105 blockers
B-1–B-4. No run. No Executor authorization. H-IT-001 / H-DS-001 / H-IC-001 /
H-STR-002 untouched. Structure-null-r2 not reopened. Toy ceiling.

## Deliverables

| Path | Role |
|------|------|
| `experiments/EXP-IT-001/specification.v2.yaml` | Executable v2 contract |
| `experiments/EXP-IT-001/amendments/PA-IT-001-v2-rc25b-b1-b4.yaml` | Versioned amendment record |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/tasks/TASK-20260731-107/task_report.md` | This report |

v1 `experiments/EXP-IT-001/specification.yaml` left byte-identical to freeze
`303ae797` (sha256 `d2bd25760000539d2c4420fe0cb5279230cd6398e659e06dadf08b22c608571c`).

## Discharge summary

- **B-1:** `d=3`; `H_min` hop RV; deterministic `F_hit` tree-ball algorithm; HEUR report schema pre-search.
- **B-2:** embedding `k_max=6`; Weil-descent n∈{2,3,4} predicate; `U_IT_ORDINARY_PRIME_ORDER` density universe.
- **B-3:** composite `ell_max=floor(N^{1/2})`; `C_path=C_search+C_eval`; per-family `C_special`; pullback; ±10x on `C_eval`.
- **B-4:** `NULL-IT-ISOGENY-TRANSFER` with `R_null`, plant/rho controls, packaging hash.

## Completion gate

- [x] B-1–B-4 discharged in frozen amend package
- [x] No run
- [x] No Executor authorization
- [ ] Snapshot archive = TASK-20260731-108 (successor)

## Inference

- requested_policy: `coordinator-orchestration-code`
- resolved_model_id: `cursor-grok-4.5`
- fallback_used: true
- model_verified: false

## Next

TASK-20260731-108 snapshot of exact declared amend paths; then independent
re-review TASK-20260731-109 (do not self-review).
