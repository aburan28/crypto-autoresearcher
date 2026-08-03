# TASK-20260731-134 — Independent review (RC-28)

**Role:** reviewer (`review-adversarial`, independent session)  
**Admitted snapshot:** `0d6a1a94` (TASK-133)  
**Open decision:** DEC-20260731-037  
**Package:** PA-DS-001-v2-ctrl-sparse-p-success / CTRL-RT025-SPARSE-P-SUCCESS  
**Batch remint:** BATCH-029 (BATCH-028 = IT via DEC-035; do not launder)

## Authority

Bind review to `git show 0d6a1a94:...`:
- experiments/EXP-DS-001/amendments/v2_ctrl_sparse_p_success.yaml
- experiments/EXP-DS-001/controls/CTRL-RT025-SPARSE-P-SUCCESS.yaml
- ledger/decisions/DEC-20260731-037.yaml
- SCOPE-DECISION.md / QUEUE-AMEND-20260731-017.md

## Objective

Return **PASS** or **REVISE**. Confirm:
- `status: executable`
- `p_hat` / `p_hat_decay_observed` / `R_total_expected` / `sparse_p_success_pass|fail`
- BATCH-027/028 IT named dominated_by / deferred; no EXP-IT launder
- toy ceiling; RC-28 REVISE ⇒ non-execution

## Deliverables

- `contract_review.yaml`
- `derivation_check.md`

MAKE NO COMMIT. Approval is Coordinator TASK-135 → DEC-20260731-038.
