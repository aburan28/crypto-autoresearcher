# BATCH-031 input capsule

## Why this batch
DEC-20260802-446a54 (BATCH-028) closed OPEN-BATCH023-A as attempted_and_inconclusive with disposition refine.
Red team RT411037-B1/B2 block any HEUR-DS-1 support reading while thr_TAIL=0 (LPF=2 saturated) and the object is an FB census.

## Exactly one next action (from goal)
Open a successor batch that repairs RT411037-B1 and RT411037-B2 before any HEUR-DS-1 claim.

## Batch-031 design
Contract-gate only: freeze EXP-SMTH-9d04ba with non-LPF2-saturated tail + thr_TAIL>0 integrity gate and B2 non-promotion language; snapshot; independent RT+Val; ledger authorize/refuse execute.
No measurement in this batch.

## Non-goals
No STR/DEP reopen. No goal completion. Toy tier only.
