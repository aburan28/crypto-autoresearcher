# Analysis: TYPED-TT-PREFIX-STREAMING-TRADEOFF-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The streaming evaluator retained one current `A+R0+R1` prefix state and the 25-entry `R2+R3` suffix table, while charging two point additions on each prefix transition. On all 12 diagonal rows, direct-reference arithmetic, adaptive construction, all relation targets, all supported held-out descent targets, and sealed baseline counters passed the independent verifier. Retained Python advice was `0.0815-0.1283` of the materialized advice across the rows. Fully charged point additions were `0.2040-0.2161` of the direct five-addition evaluator.

The lexicographic negative control retained direct-reference exactness but failed adaptive exactness, supported descent exactness, and sealed diagonal baseline matching. Its verifier receipt is valid as an expected negative result.

## Interpretation

This is evidence for a useful fixed-curve preprocessing tradeoff: a large materialized prefix table can be replaced by a small streaming state at the cost of additional online additions. The result is implementation- and schedule-specific. Source input points are reported separately and are not claimed to be free; the retained-advice comparison excludes those common inputs in the same way as the materialized receipt.

This does not establish an asymptotic ECDLP improvement. The experiment still uses toy curves, inherited relation witnesses, full validation, and no complete sparse linear-algebra or individual-log attack. The measured toy Pollard-rho references remain separate and the complete candidate workload is not promoted as a rho win.

## Next action

Repeat the streaming/materialized comparison across larger `A,B` sweeps, then add a matched sparse relation-matrix and target-descent cost. The key question is whether streaming advice makes the fixed-curve `S/T` frontier better without moving the work into an equally expensive online scan.
