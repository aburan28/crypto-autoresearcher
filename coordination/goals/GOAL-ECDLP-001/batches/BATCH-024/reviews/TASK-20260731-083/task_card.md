# TASK-20260731-083 — Independent review (RC-24)

**Role:** reviewer (`review-adversarial`, independent session)  
**Admitted snapshot:** `32165e30` (TASK-082)  
**Package:** PA-DS-001-v2-ctrl-structure-null / CTRL-NULL-OBJECT-STRUCTURE-DIRECTION  
**Open decision:** DEC-20260731-020  

## Objective

Return **PASS** or **REVISE** on the structure-null addendum. Confirm:
- structure credit requires `R_null ≥ 0.9` (or rising ladder toward 1) while `R` advantageous under null-object packaging;
- plant-contrast / `planted_bug_detected` must not be renamed as `structure_gate`;
- honest `structure_direction_fail` is allowed (not infrastructure; not lane death);
- deferred CI-IDENTITY / SPARSE named; no edit to prior freezes; toy ceiling.

## Cycle cap

RC-24: REVISE ⇒ BATCH-024 non-execution (no second cycle).

## Deliverables

- `contract_review.yaml`
- `derivation_check.md`

MAKE NO COMMIT. Do not author repairs. Do not alter H-IC-001 / H-STR-002.
