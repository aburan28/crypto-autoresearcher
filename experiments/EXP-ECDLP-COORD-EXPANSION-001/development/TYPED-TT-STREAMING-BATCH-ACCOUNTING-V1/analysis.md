# Analysis: TYPED-TT-STREAMING-BATCH-ACCOUNTING-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The diagonal producer passed all five batch schedules on all 12 fresh rows. The full batch replayed all eight relation targets and every held-out target supported by both existing toy descent paths. Direct-reference arithmetic, relation binding, relation replay, supported descent replay, and the prefix-reuse counter all passed.

The streamed advice retained `0.0824-0.1337` of the materialized Python advice. Charged point-add ratios including advice construction and adaptive construction were:

| Batch | Target composition | Charged ratio range |
|---|---|---:|
| `balanced_1` | 2 targets | `0.202130-0.208992` |
| `balanced_2` | 4 targets | `0.201078-0.204627` |
| `balanced_4` | 8 targets | `0.200542-0.202348` |
| `balanced_8` | 16 targets | `0.200272-0.201183` |
| `full` | all relation plus supported descent targets | `0.200182-0.201183` |

Prefix recomputation was exactly one pass over the prefix fibers for every batch, so the target count was removed from that part of the online work. The improvement is a modest amortization effect, not a new exponent. The lexicographic receipt retained direct-reference exactness but failed balanced and full exactness, relation replay, and supported descent as expected.

## Interpretation

This is a valid fixed-curve many-target scheduling improvement for the source evaluator. It shows that advice reuse can be exposed by changing the loop order, but the measured gain is small relative to the existing source-sum constant factor. The source inputs are reported separately, and the relation matrix, sparse linear algebra, and individual-log cost are still inherited from the fixture rather than newly solved by this experiment.

## Next action

Implement a complete downstream ledger: independently rebuild the typed relation matrix, charge sparse elimination and target coefficient recovery, and compare the resulting many-target schedule with materialized D4 and matched rho under the same field-operation model. Then repeat the batch experiment on genuinely larger source dimensions.
