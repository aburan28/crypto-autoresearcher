# Red-Team Review: TYPED-TT-ADVERSARIAL-ORDER-CONTROL-V1

## Verdict

Accept as a scoped negative control. The result is useful precisely because it prevents schedule-dependent toy evidence from being presented as order-agnostic structure.

## Checks

- Both orders use the same fresh fixture and stopping rule.
- Both receipts pass independent producer rerun verification.
- Construction counters remain consistent.
- Exactness failure is visible in the raw rows and summary.
- Breakthrough and promotion flags remain false.

## Remaining concern

The controls are deterministic alternate orders, not random permutations or a formal lower bound. A source-aware randomized-order study is still open.
