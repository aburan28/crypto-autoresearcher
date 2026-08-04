# TASK-20260731-125 — Open BATCH-028 (EXP-IT-001 v3 Executor)

**Role:** coordinator  
**Decision:** DEC-20260731-035  
**Goal:** GOAL-ECDLP-001 / SG-ECDLP-002  

## Authorization binding

| Field | Value |
|---|---|
| Approval | TASK-20260731-124 / DEC-20260731-034 / APPROVED |
| Approval snapshot | `8f02ab4b7ce02dbe67a3367d559e671b1be0e556` |
| Amend freeze | `d65c5e21763fe2a920e6f546f8eec039e1bc3d8f` |
| Bound specification | `experiments/EXP-IT-001/specification.v3.yaml` only |
| Protocol amendment | PA-IT-001-v3-rc27-b5-b8 |
| `run_authorized` | true (v3 only) |

## Batch scope

Open BATCH-028 with renderable queue:

1. **TASK-127** Executor — implement + bounded toy run (IDEA-011 null; planted-path positive; matched rho/BSGS; HEUR-ISO-1)
2. **TASK-128** Snapshot archive of run package
3. **TASK-129** Validator
4. **TASK-130** Red Team
5. **TASK-131** Ledger `EV-IT-001` / `DEC-20260731-036`

Open snapshot: **TASK-126** (this open package).

## Dual-lane note

- **IT lane (this batch):** BATCH-028 Executor under DEC-035.
- **CI lane:** BATCH-026 TASK-115 left alone if still in flight; not cancelled; not archived here. DEC-031 remains reserved for CI ledger.
- Do not launder CI scopes into IT or vice versa.

## Forbid

No v1/v2 execution. No STR. No H-DS-001 / H-IC-001 / H-STR-002 edits. No push. Toy ceiling. No asymptotic support / S1_met claim from authorization alone.

## Inference

requested_policy `coordinator-orchestration-code` → resolved `cursor-grok-4.5` (`fallback_used: true`).
