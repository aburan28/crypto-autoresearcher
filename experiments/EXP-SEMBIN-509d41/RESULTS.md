# RESULTS — EXP-SEMBIN-509d41

Hypothesis: H-SEMBIN-9af7e1
Approved by: DEC-20261002-15b02c
Task: TASK-20261003-af0d91 (epoch 2; lost-completion re-claim; artifacts absent on origin/main)
Trial plan: experiments/EXP-SEMBIN-509d41/trial-plan-v1.json (Stages 0–1 only)

Stage-1 package outcome: **S1-INVARIANTS-OK**

This is the producer Stage-1 label from RUN-SEMBIN-bd538f/raw-result.json. It is **not** H-SEMBIN-9af7e1 `O-CLOSURE`: that label requires Stage 2 PREDICTIVE/INERT or Stage 2 O-IMPEDIMENT with Stage-1 intact. Stage 2 is out of scope for trial-plan-v1.json (`stage2_admitted: false`).

## Stages

| Stage | Plan id | Run id | Supervisor | Producer label |
| --- | --- | --- | --- | --- |
| 0 | stage0-topology-worksheet | RUN-SEMBIN-9000a8 | output_validated | S0-FREEZE-OK |
| 1 | stage1-reenumeration-dag-control | RUN-SEMBIN-bd538f | output_validated | S1-INVARIANTS-OK |

## Stage 0

Freeze artifacts: `stage0/preregistered-predictions.json`, `stage0/worksheet-note.md`. Master seed `20261002c94`. Twin-check not applicable (worksheet).

## Stage 1

Tree counts equal (2t-3)!! for t=3..8: 3, 15, 105, 945, 10395, 135135. `invariant_hold_all=true`. Design-figure sigma_top checks all `ok=true`. DAG known-false control: `SCOPED_REFUSAL_RECORDED`. Wall ~2.10 s (producer) / 2.22 s (receipt span).

## Claims

- break: false
- exponent_move: false
- attack: false
- amazon_bedrock: NOT SELECTED
- No Magma/Sage/AUXIN.
- No ECDLP solve. No FIPS verdict. No n>=131 transfer.
- Stage 2 HEUR-TOP cell not admitted by this plan.

## Scope

Combinatorial re-enumeration of unordered full binary merge trees t=3..8 and sigma_top tables plus DAG known-false control. Observations only.
