# BATCH-58df35 launch note

Execution batch for the user-confirmed RANK 2 approval gate of
GOAL-ECRANK-002: frozen contract EXP-ECRANK-76a70d (reversal-idea
experiment from IDEA-20260905-d5608c; H-ECRANK-ee6e0e specified; design
verdict DESIGN-WITH-FINDINGS under DEC-20260905-145454). The user confirmed
execution with findings 1/2/3/6 engaged. This note does not attest that
the opening archive has verified; that is TASK-20260905-4194e7.

Sequence: opening snapshot TASK-20260905-4194e7, then approval ledger
TASK-20260905-91ca91 (DEC-20260905-cebc4d approves the contract and amends
approved_by; goal head moves to this batch) -- the executor
(TASK-20260905-f615a7, executor-implementation/medium, 8 enumerated runs,
7200 s wall per run, 8 GB, counted-ops caps binding, descent/PARI/network
all zero) may start ONLY after the approval ledger verifies. Then run
snapshot TASK-20260905-6b4607 and outcome ledger TASK-20260905-3bcd97
(DEC-20260905-a5e07b, no promotion beyond servable tiers; a positive
criterion outcome stays pending required independent review).

Approval authorizes execution within the contract caps only. No C1
closure: the N1 external-witness candidate of DEC-20260905-7adca0 stays
UNPROMOTED pending review-breakthrough at max (re-probed unservable:
anthropic/openai/openrouter unusable, no backend reaches max); IMP-2
stands. Each archive requires Git verification and a PR update before
downstream use.
