# Direct Equality Pair V1 Analysis

## Status

`RESTRICTED THEOREM`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The exact equality predicate has a gauge-invariant projective-pair
factorization of degree and component dimension one half those of the norm
locator. It gives a cleaner simultaneous-zero problem, not a simultaneous-zero
index or ECDLP improvement.

## Exact Run

- source commit: `dc768134bffdca670070a7468718702e43e0b7fe`;
- curves: `q in {953,3919,15583}`;
- four coordinate factor-base families;
- `B in {5,8,10}`;
- cuts 2 and 3;
- planted and held-out target per row;
- 12 family rows;
- 2,223,216 residual-pair factor checks;
- 865,072 prefix/canonical-suffix permutation classes;
- zero factor, norm-reconstruction, zero-set, affine-section, or permutation
  mismatch;
- wall time: 30.19 seconds;
- peak RSS: 95,092,736 bytes;
- same-code deterministic normalized rerun: exact.

## Intrinsic Equality Pair

For final projective point `(X,Y,Z)` and target `(xq,yq,zq)`, define

`e_x=zq X-xq Z`,

`e_y=zq Y-yq Z`.

Both residuals vanish exactly when the projective points are equal. Under
output rescaling by nonzero `lambda`, the pair scales by `lambda`, so its
canonical projective class is unchanged.

The old norm locator is recovered exactly as

`h_Q=e_x^2-nu e_y^2`.

Because `nu` is a nonsquare in `F_p`, `h_Q=0` iff
`(e_x,e_y)=(0,0)`. The pair and norm therefore have the same exact zero set,
but the pair retains the two lower-degree equations.

## Direct Factor Theorem

Each equality residual is linear in the final RCB output. At cut `k`, its
degree in the prefix point is

`d_k=2^(5-k)`.

Modulo the smooth cubic, the factor dimensions are:

| cut | remaining R points | residual degree | dimension per residual |
|---:|---:|---:|---:|
| 2 | 3 | 8 | 24 |
| 3 | 2 | 4 | 12 |

The target-independent suffix components are simply the coordinate
polynomials `X,Y,Z`. Target specialization forms the two residual vectors.

Every factor product equals the exact numerical residual, and every squared
pair reconstructs the prior norm locator.

## Gauge Invariance

For every prefix and every ordered suffix tuple, the run groups all suffix
permutations by their sorted tuple. Across 865,072 target-labeled classes:

- all exact outputs represent the same affine point;
- every canonical residual pair is identical;
- every affine representative has the same canonical residual pair;
- simultaneous-zero status is identical.

This repairs the active projective-gauge defect found in the raw block-product
recurrence experiment. It does not prove invariance under every alternate
addition tree, though projective point equality predicts it and should be a
separate control.

## Rank and State

In every cell:

- `U` reaches dimension 24 at cut 2 and 12 at cut 3;
- `V_x` and `V_y` each reach 24/12;
- concatenated suffix pairs reach rank 48/24.

The pair halves each polynomial degree but retains two simultaneous
constraints. The combined linear state matches the old norm dimensions.

At cut 2:

| q | B | fixed `X,Y,Z` state | specialized pair state |
|---:|---:|---:|---:|
| 953 | 5 | 9,000 field elements | 6,000 |
| 3919 | 8 | 36,864 field elements | 24,576 |
| 15583 | 10 | 72,000 field elements | 48,000 |

The fixed state is `3*24*B^3=72B^3`, a 2.67-fold reduction from the
four-component norm compiler's `192B^3`. The specialized pair is
`2*24*B^3=48B^3`, equal in size to the specialized norm vector.

At cut 3, fixed and specialized state are `36B^2` and `24B^2`, while the
prefix side remains `A B^2`.

Thus the equality pair improves constants and removes an arbitrary projective
section, but does not change the explicit `q^0.6` central side.

## Strongest Valid Conclusion

> The frozen complete-addition equality predicate admits exact,
> permutation-invariant projective-pair factors of dimensions 24 and 12 per
> residual. Three target-independent coordinate components specialize to two
> public residual vectors, and the simultaneous zero set equals target
> equality.

The explicit-state boundary remains:

> Direct cut-2 advice or specialized pair materialization is
> `Theta(B^3)=q^(0.6+o(1))`; cut 3 leaves `Theta(A B^2)` prefixes. No
> simultaneous-zero reporting algorithm has been constructed.

## Next Concrete Action

Use the intrinsic pair as the leaf object for
`RANK2-NET-NORM-CIRCUIT-V1`.

The experiment should avoid scalarizing the pair back into a gauge-dependent
sequence. It should test whether:

- rank-two net or divisor state composes the two residual constraints;
- an iterated norm/resultant circuit exploits four-sum structure below
  `B^2.5`;
- multiplication operators have low displacement rank versus matched random
  divisors;
- exact zero descent is possible without `B^3/B^4` leaf materialization.

An alternate-addition-tree pair-invariance check and a separately implemented
verifier should be included before interpreting any nonlinear compression.
