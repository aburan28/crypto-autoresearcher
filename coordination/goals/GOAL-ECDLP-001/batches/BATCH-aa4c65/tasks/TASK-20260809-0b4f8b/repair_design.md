# Arm-A v6 successor repair design

This package is a new immutable successor to `EXP-ECDLP-e8ef62`. The prior
package, its v5 snapshot, and the fresh `TASK-20260809-7761cf` NO-GO report
remain unchanged. This task creates no implementation, run, or empirical
evidence.

## Closure map for the fresh review

| Finding | Concrete repair |
|---|---|
| `REV-7761cf-01` inconsistent paired target derivation | v6 defines one canonical byte contract in all three artifacts: `PAIR-ID-v1` length-prefixed UTF-8/u32 preimage for the raw 32-byte pair token, then `PAIR-TARGET-v1` length-prefixed UTF-8 plus the raw pair-token digest and u32 subgroup order. The target digest and `target_x=1+digest mod (n-1)) are retained and recomputed fail-closed. A frozen G01/seed 101/order 1009 vector includes both preimages, both digests, and target_x=237. |
| `REV-7761cf-02` Walsh outputs not schema-bound | v6 replaces the ambiguous `walsh_pairs_36` field with required `walsh_table_36`: exactly 36 lexicographic `(i,j)` rows, reduced exact product numerator/denominator, pair index, and sorting position. The validator recomputes all products, stable exact ordering, lower-median row 18, threshold, and effect decision; no legacy alias is accepted. |

The successor retains the already reviewed typed-map closure, exact signed-rank
permutation table, frozen coefficient-group fixture, bounded calibration, cost
accounting, controls, and toy-only claim ceiling. The next gate is the exact
snapshot followed by a fresh independent `review-adversarial` session.

