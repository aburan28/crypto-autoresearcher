# TASK-20260731-014 — Freeze H-DS-001 + EXP-DS-001

## Status

`completed` (Coordinator design freeze; no runs).

## Deliverables

| Path | Role |
|---|---|
| `ledger/hypotheses/H-DS-001.yaml` | New hypothesis from IDEA-20260731-007; status `specified` |
| `experiments/EXP-DS-001/specification.yaml` | Frozen contract at `review_required` / `approved_by: null` (D-1) |
| `ledger/goals/GOAL-ECDLP-001.yaml` | `current_batch_id: BATCH-017`, queue path, next_action |

## Design summary

- **Mechanism:** Degree-split Semaev claw membership (half-arity MITM + HEUR-DS-1).
- **Null control:** IDEA-20260731-011 structure-destruction (random multihomogeneous) frozen into protocol with planted-bug and honest-rho controls.
- **Baselines:** Matched Pollard rho (negation) + BSGS.
- **Primary metric:** R = cost_split/cost_naive; gate R_null >= 0.9 when R < 0.5.
- **Claim ceiling:** toy-tier; no crypto-scale overclaim; asymptotic promotion gates remain open.
- **Not modified:** H-IC-001 (weakened), H-STR-002 (weakened).

## Archival

Archived by `TASK-20260731-015` snapshot. Independent pre-exec review is `TASK-20260731-016`. Approval disposition is `TASK-20260731-017`. No Executor handoff until APPROVED.
