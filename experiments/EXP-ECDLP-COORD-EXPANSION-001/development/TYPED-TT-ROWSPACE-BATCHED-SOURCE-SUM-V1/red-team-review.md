# Red-Team Review: TYPED-TT-ROWSPACE-BATCHED-SOURCE-SUM-V1

## Required objections

- A source-point cache can make a fixed-curve table lookup look like a new
  algorithm. Report cache bytes and logical bandwidth beside point additions.
- The first target builds the row space and may populate most source sums. Do
  not compare only the later online targets; include construction and target
  predicate costs for every batch width.
- The candidate changes loop order. A lower point-add count must be attributed
  to target-independent source sums, not to omitted prefix recomputation.
- Predicate evaluations remain target-specific. Count them separately and do
  not claim target work disappeared.
- A sampled reconstruction is not full support, relation generation, target
  descent, or ECDLP recovery. Keep the result model-bound and toy-scale.
- Exactness must be checked against an independently rebuilt direct oracle on
  deterministic samples; candidate self-consistency is insufficient.

## Falsification controls

- Use the target-separated cache control with the same source query indices.
- Include the `x_interval` row as a positive structural control and the three
  other public families as matched controls.
- Sweep batch widths `1,2,4,8,15`, not only the largest batch.
- Verify that the shared-cache source-sum count is independent of target width
  only when the queried source-index set is unchanged.

## Decision boundary

Even a strong source-addition saving is a fixed-curve preprocessing signal. A
future promotion would require persistent advice, online memory bandwidth,
relation rank, target descent, and a matched rho comparison.
