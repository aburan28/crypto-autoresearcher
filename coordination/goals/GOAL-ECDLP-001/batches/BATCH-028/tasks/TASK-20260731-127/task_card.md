# TASK-20260731-127 — Execute bounded toy EXP-IT-001 v3

**Role:** executor (`executor-implementation`)  
**Admitted after:** TASK-126 open snapshot verifies  
**Approval binding:** TASK-124 / DEC-20260731-034 / `8f02ab4b`  
**Batch open:** DEC-20260731-035  
**Amend freeze:** `d65c5e21` (PA-IT-001-v3-rc27-b5-b8)

## Authorized contract

- **Only** `experiments/EXP-IT-001/specification.v3.yaml`
- Run id: `RUN-IT-001-bounded-toy`
- Claim ceiling: **toy** (20/24/28-bit). No crypto-scale. No asymptotic support.

## Required arms / controls

1. HEUR-ISO-1 density freeze + F_hit / KS / TAIL reporting (`HEUR_ISO_1_report.json`)
2. Charged transfer gate (`transfer_gate_report.json`) with cost ledger labels
3. Planted-path positive control (CTRL-PLANTED-PATH-POS)
4. Matched Pollard rho + matched BSGS baselines
5. IDEA-20260731-011 null object (`NULL-IT-ISOGENY-TRANSFER`) + CTRL-NULL-IT-PLANT
6. Concrete cost table

## Deliverables (exact)

- `experiments/EXP-IT-001/runs/RUN-IT-001-bounded-toy/manifest.json`
- `experiments/EXP-IT-001/runs/RUN-IT-001-bounded-toy/raw-result.json`
- `experiments/EXP-IT-001/results/summary.json`
- `experiments/EXP-IT-001/results/HEUR_ISO_1_report.json`
- `experiments/EXP-IT-001/results/transfer_gate_report.json`
- `experiments/EXP-IT-001/results/concrete_cost_table.json`
- `experiments/EXP-IT-001/results/null_it_isogeny_transfer_report.json`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-028/tasks/TASK-20260731-127/execution_report.yaml`

## Constraints

- MAKE NO COMMIT (TASK-128 archives).
- Do not execute v1/v2. Do not edit `approved_by` in v3 blob.
- Do not touch EXP-DS-001 / BATCH-026 / H-DS-001 / H-IC-001 / H-STR-002.
- No STR. Honest `failed_infrastructure` / resource stop OK (not math negative).
- Inference: requested `executor-implementation` → fallback `cursor-grok-4.5`; record `fallback_used`.
