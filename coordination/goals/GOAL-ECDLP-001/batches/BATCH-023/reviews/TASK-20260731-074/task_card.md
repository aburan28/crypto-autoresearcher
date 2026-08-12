# TASK-20260731-074 — Independent review (ADMITTED)

**Status:** ready (admitted)  
**Role:** reviewer  
**Policy:** review-adversarial (independent session)  
**Snapshot:** `f41fd196e1cf0345c903b68d4326b311e5ea573b` (TASK-20260731-073)  
**RC-23:** one cycle; REVISE ⇒ BATCH-023 non-execution  

## Objective

Return PASS or REVISE on `PA-DS-001-v2-ctrl-plant-contrast` / `CTRL-PLANT-CONTRASTIVE-F2`.

Confirm contrastive plant credit requires plant-OFF `null_gate_f2_shape` false AND plant-ON true; forbids F2-on-F2 detection credit; no full matrix; no immutable freeze edits.

## Inputs

- Snapshot `f41fd196e1cf0345c903b68d4326b311e5ea573b`
- `experiments/EXP-DS-001/amendments/v2_ctrl_plant_contrast.yaml`
- `experiments/EXP-DS-001/controls/CTRL-PLANT-CONTRASTIVE-F2.yaml`
- `ledger/decisions/DEC-20260731-018.yaml`
- RT-20260731-070 / DEC-20260731-017 / EV-DS-006

## Deliverables

- `contract_review.yaml`
- `derivation_check.md`

## Constraints

- Independent session; MAKE NO COMMIT
- Toy claim ceiling; do not alter H-IC-001 / H-STR-002
- Do not launder BATCH-021 theater WIP
