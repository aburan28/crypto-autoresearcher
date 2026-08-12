# Red-team review: projective shared-sign source-state operator

## Scope

This review checks the homogeneous scaling argument, the independent verifier, and the interpretation of the three-curve result.

## Checks

- **Independent arithmetic:** the verifier reports 76 checks with no failures. It independently reconstructs every regenerated source state used by the four families on all three curves, checks both signs, and checks the affine/projective predicate relationship on two targets per family.
- **Scaling discipline:** for nonzero affine branch values, the projective branch value equals the affine value times `Z^6`; the paired product equals the affine product times `Z^12`. The factor is source-state-only and nonzero. This supports zero support and row-space rank through invertible column scaling, but it does not support using the projective values as ordinary affine predicate values.
- **Exceptional cases:** identity, equal-x, inverse-point, and generic cases are covered by unit tests and the exact fallback path. Fallback inversions remain charged.
- **Comparator provenance:** naive orbit and original affine rows are generated on the same fresh fixtures in the generator, with source hashes recorded. The independent support verifier rebuilds the class partition instead of trusting candidate class metadata.
- **Cost accounting:** projective field multiplications and inversions are lower in all 12 full cells, while point additions are essentially unchanged from naive and higher than original. Cache bytes are higher. A scalar win therefore requires an explicit weighting of field operations, inversions, point additions, and memory traffic.
- **Gate stability:** `source_prf_x` budget `44` passes on all three curves, but no other family has a three-curve accepted sub-full budget. This is a family-specific signal, not a generic factor-base result.

## Verdict

Retain as `POSITIVE TOY-EVIDENCE` and `MODEL-BOUND` for homogeneous zero-locator arithmetic. The operator merits a larger-dimension and downstream-cost successor. It does not justify a generic ECDLP, exponent, fixed-curve preprocessing-frontier, or faster-than-rho claim.

## Required successor controls

1. Publish a preregistered weighted cost table with inversion and point-add weights, plus a separate memory-bandwidth model.
2. Repeat `source_prf_x` and at least one failing family at 16-bit or larger fresh curves.
3. Charge sparse matrix rank/elimination, individual-log descent, witness lift, source-cache bandwidth, and rho in the same field-operation model.
4. Keep the homogeneous scaling invariant explicit in any successor that uses row-space reconstruction; reject any implementation that silently treats scaled values as affine values.
