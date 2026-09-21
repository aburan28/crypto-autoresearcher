# RT-20260731-118 — Objections (CI-IDENTITY)

**Snapshot:** `967b78a1` (TASK-116)  
**Control:** CTRL-RT025-CI-IDENTITY @ `07232da8`  
**Approval:** `405b8422` / DEC-033  
**Prior:** EV-DS-003 / EV-DS-008 / RT-20260731-101 / DEC-029/030/033  

## Verdict

`ci_identity_pass=true` on primary cell 20/64/4/101 is **protocol success for CI measurement honesty** (cost-identity bootstrap CI contains R_point), **not** S1_met / support / asymptotic / lane death. Legacy wall-proxy CI still excludes the point — diagnostic only.

## Blocking (RT118-B1–B6)

| ID | Title |
|----|--------|
| RT118-B1 | Forbid stronger-than-toy readings from ci_identity_pass (keeps RT101-B1) |
| RT118-B2 | ci_identity_pass ≠ mechanism credit / S1_met; RT047-B2 partial cell-local discharge only |
| RT118-B3 | Unreplicated empirical_only forbids reject_scoped / lane death |
| RT118-B4 | Do not misuse legacy wall-ratio proxy CI as primary or as fail signal |
| RT118-B5 | No theater / EXP-IT / BATCH-027 launder |
| RT118-B6 | SPARSE-P-SUCCESS deferred; RT047/RT079 residuals still bind |

## Major / info

- **RT118-M1:** Optional secondary 16/128/4/102 not executed; pass is cell-local.
- **RT118-M2:** Dirty-tree / assume-unchanged driver; execution_report numeric drift vs raw-result — bind EV to snapshot hashes.
- **RT118-M3:** Narrow CI on saturated 200/200 yield may understate uncertainty; not crypto-scale.
- **RT118-I1/I2:** Package forbid hygiene OK; inference fallback recorded.

## Observed (snapshot raw-result)

| Field | Value |
|-------|-------|
| R_point | ≈0.027434 |
| cost-identity CI | [0.027246, 0.027933] — contains point |
| legacy wall-proxy CI | [0.085, 0.311] — excludes point |
| ci_identity_pass | true |
| R_null | ≈99.67 (not S1_met) |
| cells_measured | 1 |

## TASK-119 recommendation

- **DISPOSITION:** `inconclusive` (preferred) or `expand` only for SPARSE/secondary/replication scheduling  
- **NOT:** `support`  
- **H-DS-001:** keep `analyzed`  
- **Gates:** OPEN  
- **SPARSE:** deferred  
- **knowledge_promotion:** `not_warranted`  
- **Evidence / DEC:** EV-DS-009 + DEC-20260731-031  
