# Development result v1: fixed-curve five-term compiler

## Status

- `OBSERVATION`: the materialized `4+1` workflow reaches relation rank and individual descent on the tested ordinary and random toy bases.
- `NEGATIVE RESULT`: no coordinate row passes the dual-null and same-advice BSGS routing gate in this one-seed development sweep.
- `TOY-EVIDENCE`: 12, 14, and 16-bit generated groups only.
- `NON-CANONICAL`: the run has no approval record and does not satisfy the frozen three-seed protocol.

## Frozen bytes for this development artifact

- raw result SHA-256: `fc1a92521e2a2a10b7f56ac18a9ba144ae5b6aa6b9127a1375c95a336acd6b7e`
- generator SHA-256: `f06f56bc659d0ef66c3ad19bf4b97e51a4af8bb9a376030830d1ae3323a9bd76`
- verifier SHA-256: `145641c26f1edb7dab73ff9f3dd99c64de9df57ff7685cf0c61c834e1af99b7c`
- verifier status: `verified`, `development_only: true`, 3 instances, 36 rows, 0 routing rows.

## Instances

| bits | p | q | B | signed five-term classes | rho average group ops |
|---:|---:|---:|---:|---:|---:|
| 12 | 3863 | 3793 | 12 | 2668 | 412 |
| 14 | 16363 | 16333 | 16 | 10128 | 924 |
| 16 | 64403 | 64663 | 22 | 46530 | 1580 |

All curves have prime order, trace outside `{0,1}`, and `j` outside `{0,1728}`. The field prime was selected before and independently of the reported factorization of `p-1`.

## Functional result

Every one of the 30 non-control rows (`x_interval`, `square_map`, `rational_union`, `random_x`, and `random_scalar`, each at witness caps 1 and 4) reached rank `B`, reproduced every solved factor-base point from its recovered logarithm, and verified all four randomized individual-log challenges.

All six scalar-progression rows failed the complete functional gate because their exact five-term support shrank too far for the frozen descent budget. This is the intended compression-positive, expansion-negative control behavior.

This establishes a complete toy relation pipeline. It does not establish an efficient ECDLP algorithm.

## Routing result

No coordinate row passed.

- Candidate preprocessing-score ratios versus random-x ranged from `0.8851` to `1.1764`.
- Ratios versus random-scalar ranged from `0.8308` to `1.1039`.
- The routing threshold is at most `0.8` against both controls while retaining support and functional correctness.
- The configuration contains one seed, while aggregate routing requires two passing seeds at every size.

The exploratory total group-operation slopes were:

| family | witness cap 1 | witness cap 4 |
|---|---:|---:|
| x_interval | 0.6867 | 0.6867 |
| square_map | 0.7117 | 0.7115 |
| rational_union | 0.6691 | 0.6700 |

The corresponding charged `F_p` multiplication slopes ranged from `0.6566` to `0.7086`, and advice-bit slopes ranged from `0.8739` to `0.8995`. These three points are too small for asymptotic inference, but none is a sub-`0.5` signal.

## Fixed-curve interpretation

The compiler has low sampled online cost after preprocessing and therefore crosses ordinary no-preprocessing rho after only a small number of repeated toy targets in a group-operation-only calculation. That observation is not a generic-frontier win.

At the same full advice-bit budget, executed fixed-base BSGS solved the identical challenges using `16.3x` to `36.7x` fewer sampled-average online group operations. Comparing deterministic worst-case bounds widened the ratio to `367x` through `595x`. No coordinate row beat BSGS, and BSGS is itself weaker than the tight generic random-walk preprocessing frontier in relevant regimes.

## Scoped negative

The following candidate is rejected for promotion under this development boundary:

> Materialize every distinct four-sum point with one or four raw index witnesses, then scan one factor-base point online.

This does not reject coordinate-specific fixed-curve preprocessing as a class. It rejects the naive materialized `D4` representation and the tested witness policies on one seed at 12-16 bits.

## Necessary improvement

With `B` near `q^(1/5)`, the current online scan has exponent about `0.2`. To lie near `S*T^2 = q` at that online exponent, advice must be near `q^0.6`; a random-like materialized four-sum table is near `q^0.8` before encoding overhead. The observed advice slopes near `0.88-0.90` are consistent with the wrong side of this gap.

A successor therefore needs one of the following, not another hash-table tuning pass:

1. a coordinate-predictable membership representation for `4F` with witness recovery and advice near or below `q^0.6`;
2. an application-specific 3SUM-indexing compiler transferred to EC addition without storing all source keys;
3. a batch query algorithm whose shared online work changes the amortized exponent, not only the constant;
4. an algebraic recursive circuit that generates witnesses without generic Groebner elimination and still beats same-advice BSGS.

## Next experiment

Specify `EXP-ECDLP-COMPRESSED-JOIN-001`: hold the verified relation/rank/descent layer fixed, replace only the materialized `D4` dictionary with a compressed coordinate join, and require a same-advice BSGS win before any multi-seed escalation.
