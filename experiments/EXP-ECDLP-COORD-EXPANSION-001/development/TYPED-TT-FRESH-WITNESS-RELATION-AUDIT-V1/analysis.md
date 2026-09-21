# Analysis: TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The source-native evaluator produced independently valid witnesses in all 12 full-control rows, and its support matched independently rebuilt typed `D4` support in every row. The full control queried exactly `100%` of the declared `A x B^4` tensor. Candidate quotient ranks ranged from `4` to `11`; some rows remained below the quotient width even after the exhaustive scan and bounded target stream.

The first-prefix negative control queried only `0.0833%-0.5714%` of the corresponding full tensor, produced valid witnesses when it found them, but failed support equality in every row and remained rank-deficient. The result therefore separates witness correctness from a viable relation-generation shortcut.

## Interpretation

This is a scoped negative result for the proposed bounded source-advice witness locator. The source coordinate predicate is not the problem in this fixture: independently checked exact witnesses exist. The missing ingredient is a sub-exhaustive method that finds enough of them while preserving support and rank. The only positive control that reproduced support was the explicit exhaustive `A x B^4` scan.

The receipt charges source advice, target construction, source queries, incremental matrix work, and solve work in separate ledgers. It does not combine source-native and typed costs into a claimed speedup.

## Next action

Search for a genuinely sub-exhaustive witness locator: collision joins over compressed prefix states, adaptive multi-prefix sampling with a held-out support test, and larger source dimensions. Any successor must report relation probability, rank, memory, target descent, and a matched rho baseline.
