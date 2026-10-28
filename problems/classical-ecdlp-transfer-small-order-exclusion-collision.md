# Exact-small transfer sampling collision

Status: original v1 contract infeasible; additive v2 repair specified before any cohort draw.

The frozen v1 transfer protocol for EXP-ECDLP-ef7323 requires two curves of order 17 and two of order 31, while rejecting every repeated `(p,j)` key. Its admissible order-17 keys are `(19,8)` and `(23,9)`; its order-31 keys are `(23,9)` and `(43,0)`. Four requested curves therefore have only three distinct eligible keys. The obstruction prevents complete cohort generation regardless of constructor behavior.

The evidence is the linked [integer/CM certificate](../coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-319445/sampling-v2/analytic-feasibility.json), including the exact inverse-Hasse field lists, reduced forms and prior-exclusion lookup. The CM correspondence and class-number-one j values are explicit analytic inputs; this is not a formal proof or a new curve census. An independent cohort agent checked the same arithmetic. No nonce, curve, target or candidate outcome has been generated.

The original requirement of global `(p,j)` distinctness is preserved. DEC-20261028-a4b1f7 replaces only exact order 31 with 29 in new versioned metadata. Order 29 admits p23 with j11 and p31 with discriminant -115 and two ordinary j classes, without colliding with the order-17 keys or prior exclusions. All larger strata, circuits, public multipliers, blinding, baselines, controls and stopping rules remain fixed.

Exit criteria are a fresh frozen v2 plan/protocol, exact plan-only count/source/exclusion validation, completed amendment custody and the ordinary prospective-admission checks before the single scientific invocation. Finite proposal exhaustion remains an operational incomplete sample and cannot be silently retried. Next test: zero-draw plan validation of the v2 contract; then the admitted one-VM experiment.

The frozen v1 records remain immutable and unexecuted. This correction asserts no algorithm failure, speedup, family closure or hypothesis-status change. The research mechanism graph is unchanged: this is a cohort-feasibility correction. Its dependency diagram is `v1 global (p,j) collision -> exact r29 replacement -> v2 zero-draw validation -> prospective admission -> future cohort`; no edge is a scientific result.
