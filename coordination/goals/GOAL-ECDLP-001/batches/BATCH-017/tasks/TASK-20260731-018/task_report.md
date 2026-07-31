# TASK-20260731-018 — Author EXP-DS-001 v2 (PA-DS-001-v1-to-v2)

## Status

Completed (authoring). Snapshot archive is TASK-20260731-019.

## Inputs

- RT-20260731-016 REVISE (B-1, B-2 blocking; M-1..M-4 major)
- TASK-20260731-017 receipt: `APPROVAL_DETERMINATION: NOT APPROVED`
- Immutable v1 at commit `df613af684f6b878378b6e7696d1ce3ef8975a4c`
  (`sha256 c1792bf1733e56f631b04585f50272c9a3342302459daa62a64d1e5fdc4c3889`)

## Deliverables

- `experiments/EXP-DS-001/specification.v1-frozen-df613af6.yaml` (byte-identical to v1)
- `experiments/EXP-DS-001/specification.v2.yaml`
- `experiments/EXP-DS-001/amendments/v1_to_v2.yaml` (`PA-DS-001-v1-to-v2`)

## Discharges

| ID | Disposition |
|---|---|
| B-1 | `heur_ds_1_decision_rule` with D/u freeze, rate band c=8, KS threshold, quantitative TAIL; degree-CDF vs rho forbidden |
| B-2 | F2 = R < 0.5 ∧ R_null < 0.9 (aligned with S1 gate) |
| M-1 | `cost_identities` frozen |
| M-2 | `prediction_not_met_inconclusive_partial` |
| M-3 | `rho_calib_ratio_*` rename |
| M-4 | claw key, smoothness abort, multidegree vectors |

## Non-actions

- No edit to `experiments/EXP-DS-001/specification.yaml` (v1)
- No Executor run
- No change to H-IC-001 or H-STR-002 statuses
- H-DS-001 status remains `specified`; thresholds deferred to EXP-DS-001 v2
