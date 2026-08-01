# TASK-20260731-026 — Ledger archive EV-DS-001, DEC-20260731-004, GOAL-ECDLP-001 checkpoint

**MIRROR ONLY.** Authoritative card is the `tasks[]` entry in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-018/dispatch_queue.json`.

- **Role:** coordinator
- **Depends on:** TASK-20260731-024, TASK-20260731-025
- **Archived by:** TASK-20260731-026
- **Write scope:** ledger/evidence/EV-DS-001.yaml, ledger/decisions/DEC-20260731-004.yaml, ledger/goals/GOAL-ECDLP-001.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-018/archives/TASK-20260731-026

## Objective

Write EV-DS-001 and DEC-20260731-004 scoped to toy cells with R-1 applied; checkpoint GOAL-ECDLP-001 with exactly one next action; commit review artifacts and ledger records together. reject_scoped on a single unreplicated empirical-only set is forbidden — use weaken + replication when applicable.
