# Analysis: Source-Aware Pair-Sum-X Selector

## Status

`MIXED`, `TOY-EVIDENCE`, `MODEL-BOUND`; the strict two-curve replication gate
is negative for the primary selector.

## Result

The fixed target-independent selector `pair_sum_x_ascending` orders the
`B^2` suffix pairs by the affine x-coordinate of the source-only point
`R_j + R_k`, with infinity last and deterministic tie breaking.

On seed `271828`, curve
`recursive-toy-p15667-a10428-b3105-q15583`, the `source_prf_x` family passes
the strict 64/100 gate: projected support is exact, all held-out supported
targets are covered, the candidate rank is `11/11`, and predicted entries fall
from `1,650,000` to `1,056,000`. No other family on that curve passes the
strict gate.

On seed `161803`, curve
`recursive-toy-p15683-a13370-b621-q15749`, no family passes the strict gate.
The source-aware order therefore does not replicate as a two-curve result.
Support-only and rank-only partial signals remain visible and are retained in
the raw receipt, but they are not accepted relation-locator results.

Both curves pass the full-budget exact replay and direct witness checks. The
matched rho control solves every target with `211,901` total group operations.
The independent verifier regenerates both fixtures and passes every selector
hash, source hash, digest, support, witness, curve, and rho certificate.

Selector construction is explicit: each family/curve computes 100 source pair
sums, costing 100 group operations, 90 point additions, 10 doublings, 100
inversions, and 310 field multiplications in this toy configuration. These
costs are reported separately from the locator's repeated advice build; no
selector-preprocessing cost is hidden.

## Interpretation

The one-curve `source_prf_x` signal shows that source-only pair-sum geometry can
change which suffix columns carry the observed support. The fresh p15683
failure prevents promotion to a reproducible fixed-curve improvement. This is
not evidence that source-aware selection is useless in general, and it does
not address non-enumerative circuit contraction, target-independent row-space
construction, or a different source invariant.

The next useful experiment is a predeclared selector that uses a compositional
source invariant rather than a single affine coordinate, such as a
source-pair orbit/diagonal class or a bounded combination of x and y features,
with the same two-curve held-out protocol. It must be tested as a fixed rule,
not selected from the target support.

## Implementation evidence

Runs `RUN-TT-SOURCE-AWARE-001`, `002`, and `004` are preserved
`failed_implementation` receipts for seed mapping, selector metadata, and a
missing verifier rho helper. They produced no mathematical result. The valid
generator is `RUN-TT-SOURCE-AWARE-003`; the valid independent verifier is
`RUN-TT-SOURCE-AWARE-005`.

