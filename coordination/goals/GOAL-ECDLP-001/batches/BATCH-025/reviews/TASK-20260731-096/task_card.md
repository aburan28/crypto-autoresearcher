# TASK-20260731-096 — Independent review (RC-25)

**Role:** reviewer (`review-adversarial`, independent session)  
**Admitted snapshot:** `0d13ad5a` (TASK-095) — executable `-r2` PA/CTRL under **DEC-20260731-025**  
**Open decision:** DEC-20260731-025 (supersedes DEC-024 pivot for execution; restores DEC-023 intent)  
**Out of scope / do not launder:** EXP-IT-001 / H-IT-001 at 303ae797; do not review the cancelled TASK-105 path.

## Objective

Return **PASS** or **REVISE**. Confirm via `git show 0d13ad5a:...`:
- `status: executable` (not abandoned/cancelled stubs)
- `R_null >= 0.9` / `structure_gate_eligible` / `structure_direction_pass|fail`
- fresh `-r2` paths; abandoned BATCH-024 stubs not edited
- toy ceiling; no EXP-IT launder

## Cycle cap

RC-25: REVISE ⇒ BATCH-025 non-execution (no second cycle).

## Deliverables

- `contract_review.yaml`
- `derivation_check.md`

MAKE NO COMMIT. Do not approve a run (Coordinator TASK-097 does APPROVAL_DETERMINATION).
