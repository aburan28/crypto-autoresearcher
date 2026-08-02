# Analysis: TYPED-TT-SOURCE-AWARE-SKELETON-PREFLIGHT-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The structured prefix-fiber constructor reached the sealed exact cut-3 ranks on all 12 rows after examining only the first rank-many diagonal/lexicographic prefix fibers. It then reconstructed all eight relation targets and the first held-out target exactly.

Construction query ratios versus a full five-source tensor were:

- B=5: `0.080-0.086`;
- B=8: `0.09375`;
- B=10: `0.050`.

Target specialization through selected suffix columns was `0.55-0.60` of a full cut-3 tensor. The actual base-oracle unique-query counters exactly matched the recorded construction query counts on every row. The full validation run took approximately 47.9 seconds and used approximately 55 MiB peak RSS.

## Interpretation

This is the strongest current representation-level positive signal in the campaign. It shows that the exact cut-3 source-prefix skeleton can be discovered from a small number of complete suffix fibers, rather than from the full base tensor, on the frozen toy curves and coordinate families.

The result is still not an ECDLP improvement. The rank budget comes from the sealed exact oracle; the prefix order is a simple pilot-guided structured order; full tensor evaluation remains in the validation phase; and no persistent-advice bytes, memory bandwidth, relation matrix, individual-log descent, or rho comparison has been charged. The construction also reuses direct affine oracle evaluation rather than deriving the skeleton from the RCB circuit itself.

## Next action

Bind the source-aware skeleton to the existing typed relation and held-out descent path. Repeat on fresh ordinary prime-field curves and target batches, then replace the pilot rank budget with an adaptive stopping rule and compare the complete fixed-curve offline/online cost against optimized rho and materialized D4 baselines.
