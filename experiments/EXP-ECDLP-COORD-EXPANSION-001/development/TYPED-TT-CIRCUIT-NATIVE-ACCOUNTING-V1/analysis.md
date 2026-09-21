# Analysis: TYPED-TT-CIRCUIT-NATIVE-ACCOUNTING-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The source-sum evaluator precomputed target-independent `A+R0+R1` and `R2+R3` states, then evaluated each queried tensor entry with one online point addition and the exact equality predicate. On all 12 fresh rows, every source-native value agreed with the direct affine oracle, adaptive discovery remained exact, all eight relation targets replayed exactly, and all 8 to 16 supported held-out descent targets per family replayed exactly.

Including source advice construction, charged point additions were `0.200094-0.200628` of the direct five-addition evaluator on every row. Advice retained in the Python representation ranged from approximately 44 KiB to 270 KiB; logical source-read traffic was recorded separately. Each row also includes a deterministic toy Pollard-rho reference, whose measured group-operation count is not beaten by the full relation/descent workload.

The lexicographic negative control reproduced the prior schedule failure: direct-reference arithmetic remained exact, but adaptive tensor validation failed and the sealed diagonal baseline did not match. This confirms that the source-sum compiler preserves, rather than hides, the schedule dependency.

## Interpretation

This is a genuine fixed-curve implementation improvement over the direct affine evaluator: shared source sums remove repeated additions and expose explicit advice/storage/bandwidth accounting. It is a constant-factor result in the tested regime. The retained prefix advice is cubic-scale in the source dimensions, validation remains full-tensor replay, and no relation matrix is solved by the new evaluator. It is not a generic-prime-field ECDLP breakthrough and does not beat Pollard rho as a complete attack.

## Next action

Replace explicit point-state advice with a compressed source representation or transposed circuit operator, then measure whether relation collection and supported target descent can be performed without full tensor validation or cubic retained advice.
