# Analysis: TYPED-TT-ROWSPACE-WITNESS-LOCATOR-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

Across 12 rows, the per-target mode and the fixed-curve reuse mode both emitted independently valid witnesses and matched the typed-D4 support set for every target. The adaptive row-space ranks were `15` at `p=947`, `35-36` at `p=4027`, and `55` at `p=16267`. Each row processed `B+1` fresh targets.

The reuse mode reduced source-side unique queries and point additions by `7.6%-13.9%` and `7.5%-13.3%`, respectively, relative to rebuilding the basis for each target. Retained streaming advice was `7.8%-16.2%` of the materialized D4 builder footprint. These are genuine fixed-curve representation signals with exact support and witness checks.

The limiting cost is explicit: reconstructed suffix entries equal `100%` of the `A x B^4` tensor in both modes. After all ledgers are separated, candidate group work is approximately `53x-258x` the materialized-D4 baseline on these toy rows. The candidate therefore does not pass a net fixed-curve attack gate, and no exponent claim follows.

## Interpretation

The target-independent cut-3 row space is a useful structural observation. It suggests that target dependence may be confined to a low-dimensional coefficient vector while the source-side basis remains stable. That could matter for many-target standardized curves if a later operator can locate zeros without scanning every suffix column.

The current experiment does not provide that later operator. It replaces repeated point additions with field reconstruction but retains the full suffix enumeration, so the central decomposition bottleneck remains.

## Next action

1. Derive a target-parametric transposed operator that computes only candidate zero columns from the reused basis.
2. Test source-derived randomized bases and held-out target families on larger source dimensions.
3. Compare complete offline advice, relation rank, individual descent, and memory bandwidth against materialized D4 and matched rho before considering promotion.
