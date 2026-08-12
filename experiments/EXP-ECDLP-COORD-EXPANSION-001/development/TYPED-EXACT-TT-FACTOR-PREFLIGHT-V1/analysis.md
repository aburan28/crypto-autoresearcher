# Analysis: TYPED-EXACT-TT-FACTOR-PREFLIGHT-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The exact finite-field TT factorization reconstructed all 12 frozen locator tensors with zero mismatches. Every row had a strictly smaller exact core payload than the unrounded direct-sum/Kronecker schedule.

The exact internal TT ranks were:

| Curve | Factor-base families | Exact ranks | Tensor entries | Exact core entries | Raw/exact payload |
|---|---|---:|---:|---:|---:|
| q=953, B=5 | all four | `[1,7,30..35,14..15,5,1]` | 4,375 | 3,574--4,299 | `3.29e115`--`3.95e115` |
| q=3,919, B=8 | all four | `[1,6,48,36,8,1]` | 24,576 | 18,532 | `1.22e115` |
| q=15,583, B=10 | all four | `[1,11,110,55,10,1]` | 110,000 | 78,321 | `3.61e114` |

The raw baseline was replayed from the committed RCB shape schedule and had internal bonds of approximately `9.70e58`. The raw schedule is therefore an extremely loose upper bound on exact TT rank for these toy tensors. The exact ranks are instead close to the ambient unfolding limits at the middle cuts: for example, the B=10 rows reach ranks 110 and 55. This means the representation can be compressed enormously relative to naive closure, but the remaining exact ranks do not yet suggest a low-rank relation compiler.

The producer enumerated 4,375, 24,576, or 110,000 tensor entries per row and charged affine group operations, modular elimination operations, memory, and wall time. The full sweep took approximately 15.1 seconds and used approximately 64 MiB peak RSS on this host.

## Interpretation

This is a positive result for the narrow hypothesis that raw TT bond growth is not a lower bound on exact toy locator-tensor representation size. It identifies exact TT factorization as a viable implementation primitive for subsequent common-basis or cross-compression work.

It is not evidence of a faster ECDLP algorithm. The construction is enumerative, uses one target at a time, does not build relations, does not solve the relation matrix, does not perform target descent, and does not amortize the factorization cost. It also uses direct affine addition to construct the locator values; the RCB shape comparison is structural rather than a claim that the factorized cores are generated non-enumeratively from the RCB circuit.

## Next action

Build a non-enumerative candidate compiler that samples or contracts the RCB circuit into a shared basis, then verifies the resulting cores against the exact tensor on B=5, 8, and 10 controls. The acceptance bar must include charged sampling/contraction work, core storage, target count, reconstruction success, and comparison with the exact ranks above.
