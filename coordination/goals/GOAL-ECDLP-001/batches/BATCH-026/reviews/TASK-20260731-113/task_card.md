# TASK-20260731-113 — Independent review (RC-26)

**Role:** reviewer (`review-adversarial`, independent session)  
**Admitted snapshot:** `07232da8` (TASK-112)  
**Open decision:** DEC-20260731-030  
**Package:** PA-DS-001-v2-ctrl-ci-identity / CTRL-RT025-CI-IDENTITY

## Authority

Bind review to:
- `git show 07232da8:experiments/EXP-DS-001/amendments/v2_ctrl_ci_identity.yaml`
- `git show 07232da8:experiments/EXP-DS-001/controls/CTRL-RT025-CI-IDENTITY.yaml`
- `git show 07232da8:ledger/decisions/DEC-20260731-030.yaml`
- `git show 07232da8:coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/SCOPE-DECISION.md`

Do **not** treat raced `task_report.md` IT prose in the same snapshot as authority
(see `tasks/TASK-20260731-111/REPAIR-20260731-task-report-race.md`).

## Objective

Return **PASS** or **REVISE**. Confirm `status: executable`,
`cost_identity_R` / `ci_of_cost_identity_R` / `ci_identity_pass|fail`,
toy ceiling, SPARSE deferred, no EXP-IT launder.

## Cycle cap

RC-26: REVISE ⇒ BATCH-026 non-execution.

## Deliverables

- `contract_review.yaml`
- `derivation_check.md`

MAKE NO COMMIT. Approval is Coordinator TASK-114 → DEC-20260731-033.
