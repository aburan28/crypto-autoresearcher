# TASK-20260801-141 — Open BATCH-030 / DEC-20260801-001 (gated repair/rerun of EXP-IT-001 v3)

**Role:** coordinator (`coordinator-orchestration-code`)
**State:** completed at batch open
**Decision:** DEC-20260801-001 (decision `open`; `run_authorized: false`)
**Disposition binding:** DEC-20260731-036 / EV-IT-001 / ledger `4be3195f8`
**Approval binding:** DEC-20260731-034 / `8f02ab4b`; amend freeze
PA-IT-001-v3-rc27-b5-b8 @ `d65c5e21`

## What this card does

Authors the BATCH-030 batch open as a single coordination unit:

1. `ledger/decisions/DEC-20260801-001.yaml` — Coordinator decision opening
   BATCH-030 (decision `open`, no run authorized yet, H-IT-001 unchanged).
2. `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc30-repair-1-to-7.yaml`
   — versioned repair overlay recording the seven defect fixes (FIX-1..FIX-7)
   mandated by DEC-20260731-036, with acceptance criteria. The immutable
   `specification.v3.yaml` is NOT edited; corrections create new records.
3. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/SCOPE-DECISION.md`
   — batch scope ruling, claim ceiling (toy), forbid list, single next action.
4. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/QUEUE-AMEND-20260801-001.md`
   — batch-open amendment record naming DEC-20260801-001 and RC-30.
5. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/dispatch_queue.json`
   — the full TASK-20260801-141..147 queue with the RC-30 execution gate and
   the seven admission fixes. (Coordination record; not in the archive
   declared set, per the BATCH-028 pattern.)
6. This task card.

## Deliverables (exact)

- `ledger/decisions/DEC-20260801-001.yaml`
- `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc30-repair-1-to-7.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/SCOPE-DECISION.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/QUEUE-AMEND-20260801-001.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-030/tasks/TASK-20260801-141/task_card.md`

## Constraints

- **MAKE NO COMMIT** (the orchestrator commits; TASK-20260801-142 archives).
- Every `commit_sha` / `parent_sha` / `path_sha256` written at open is
  **null** — stated in the queue notes; no hash or timing is fabricated.
- Do NOT edit: BATCH-028 queue/records, BATCH-029 (parked), ledger records
  (EV-IT-001, DEC-20260731-036, H-IT-001, GOAL-ECDLP-001), H-DS-001,
  H-IC-001, H-STR-002, `tools/`, `specification*.yaml`, existing
  implementation files, existing run artifacts.
- Do NOT write EV-IT-002 / DEC-20260801-002 (reserved for TASK-147).
- No hypothesis status changes. No promotion. No lane death. No STR. No v1/v2.
- No measurement may be asserted; the amendment and queue reference only the
  archived crash evidence and the DEC-20260731-036 defect list.

## Completion gate

- All six deliverables exist and parse (YAML/JSON valid); DEC-20260801-001
  records decision `open` with `hypothesis_status_transition.changed: false`;
  the RC-30 gate carries the seven admission fixes; the queue declares tasks
  141..147 with exclusive write scopes and dependencies.
- TASK-20260801-142 archives this card's artifacts exactly.
