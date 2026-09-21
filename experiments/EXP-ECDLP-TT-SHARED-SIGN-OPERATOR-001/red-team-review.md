# Red-team review: shared-sign source-state operator

## Scope

This review checks whether the paired affine primitive, its receipts, and its interpretation support more than a scoped toy signal.

## Checks

- **Independent verification:** `RUN-TT-SHARED-SIGN-OPERATOR-003` is clean and `completed_valid`. It regenerates the fixtures and orbit partition, checks lifted witnesses, verifies the operator source hash, and checks matched rho certificates.
- **Exceptional arithmetic:** equal-x and identity cases are explicit branches. The generator records paired calls, shared inversions, fallbacks, and identity cases; the verifier checks that the accounting partitions every source call.
- **Comparator provenance:** the naive orbit and original full-predicate rows come from the committed preceding quotient receipt, not a reimplemented hand-written comparator. Its raw-result hash is `8bcb199d601393e4ea962dbf77750d10b4382c3fcb6fc8e1d79311f66bb806fc`.
- **Cost accounting:** the paired operator approximately halves source-state inversions relative to the naive quotient. It leaves the point-add count near the naive quotient and therefore cannot be described as a scalar total-cost win without an explicit inversion/addition weighting model.
- **Gate stability:** `source_prf_x` passes budgets `32,44` on the first curve and `44` on the second; budget `32` fails on the second curve and all other families fail. This is mixed cross-curve evidence.
- **Scope:** no cryptographic-size sweep, full factor-base construction, sparse matrix solve, individual-log descent, or deployment-relevant target recovery is present.

## Verdict

Retain as `POSITIVE TOY-EVIDENCE` and `MODEL-BOUND` source-state arithmetic. The evidence justifies a fresh projective/differential operator experiment. It does not justify a generic ECDLP, exponent, fixed-curve preprocessing-frontier, or faster-than-rho claim.

## Required successor controls

1. Repeat the source operator on a third fresh ordinary curve with an untouched seed.
2. Report field multiplications, inversions, point additions, cache bytes, bandwidth, lift work, relation rank, held-out support, descent, and rho in one table.
3. Include a weighted-cost sensitivity table so an inversion saving cannot be mistaken for a total-cost saving.
4. Keep one family and one budget that fail as negative controls; do not tune the selector after seeing the held-out result.
