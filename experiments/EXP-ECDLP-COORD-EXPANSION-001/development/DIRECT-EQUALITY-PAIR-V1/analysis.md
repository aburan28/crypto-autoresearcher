# Direct Equality Pair V1 Analysis

## Status

`RESTRICTED THEOREM` for the algebraic core; `OBSERVATION`,
`TOY-EVIDENCE`, `MODEL-BOUND`, `REVISE INTERPRETATION` for the sweep.

The exact equality predicate has a gauge-invariant projective-class
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
- hash-bound deterministic producer replay: exact, but not independent
  semantic verification.

## Intrinsic Equality Pair

For final projective point `(X,Y,Z)` and target `(xq,yq,zq)`, define

`e_x=zq X-xq Z`,

`e_y=zq Y-yq Z`.

For valid nonzero curve outputs and the tested affine targets, both residuals
vanish exactly at target equality. Under output rescaling by nonzero
`lambda`, the raw residual vector scales by `lambda`; only its projective
class and simultaneous-zero status are invariant.

The old norm locator is recovered exactly as

`h_Q=e_x^2-nu e_y^2`.

Because `nu` is a nonsquare in `F_p`, `h_Q=0` iff
`(e_x,e_y)=(0,0)`. The pair and norm therefore have the same exact zero set,
but the pair retains the two lower-degree equations.

## Direct Factor Theorem

Each equality residual is linear in the final RCB output. At cut `k`, its
degree in the prefix point is

`d_k=2^(5-k)`.

Modulo the smooth cubic, the relevant ambient coordinate-ring dimensions are:

| cut | remaining R points | residual degree | dimension per residual |
|---:|---:|---:|---:|
| 2 | 3 | 8 | 24 |
| 3 | 2 | 4 | 12 |

The target-independent suffix components are the coordinate
polynomials `X,Y,Z`. Target specialization forms the two residual vectors.

In the shared implementation, every factor product equals the numerical
residual, and every squared pair reconstructs the prior norm locator.

## Gauge Invariance

For every frozen prefix and ordered suffix tuple, the run groups permutations
internal to that suffix by their sorted tuple. Across 865,072 target-labeled
classes:

- every canonical residual pair is identical;
- every affine representative has the same canonical residual pair;
- simultaneous-zero status is identical.

Canonical residual direction is not injective: a line through the target
typically meets the cubic at other points. Therefore its equality does not
certify output-point equality. The artifact does not directly compare affine
outputs across permutations, prefix/cut reallocations, or alternate trees.

A separate read-only audit found zero affine alternate-tree mismatches over
555,804 five-tuples, 316 planted ordered witnesses, 84 incidental held-out
witnesses, and 36 infinity outputs. These checks are supplemental and are not
preserved or enforced by the official gate.

The experiment repairs the raw final-output scaling confounder for the tested
residual evaluations. It does not establish full semantic invariance across
all `S4` permutations, cross-cut allocations, the 14 binary trees, leaf or
intermediate rescaling, or target rescaling.

## Rank and State

In every sampled affine-target cell:

- `U` reaches dimension 24 at cut 2 and 12 at cut 3;
- `V_x` and `V_y` each reach 24/12;
- horizontally concatenated suffix coefficient matrices have row rank 48/24.

The pair halves each polynomial degree but retains two simultaneous
constraints. The stored specialized coefficient count and sampled
concatenated flattening rank match the old norm dimensions. This is not an
intrinsic lower bound, a count of independent equations, relation rank, or
descent evidence.

At cut 2:

| q | B | fixed `X,Y,Z` state | specialized pair state |
|---:|---:|---:|---:|
| 953 | 5 | 9,000 field elements | 6,000 |
| 3919 | 8 | 36,864 field elements | 24,576 |
| 15583 | 10 | 72,000 field elements | 48,000 |

The fixed logical coefficient payload is `3*24*B^3=72B^3`, a 2.67-fold reduction from the
four-component norm compiler's `192B^3`. The specialized pair is
`2*24*B^3=48B^3`, equal in size to the specialized norm vector.

At cut 3, fixed and specialized state are `36B^2` and `24B^2`, while the
prefix side remains `A B^2`.

These counts omit prefix/U storage, object overhead, simultaneous residency,
validation arrays, traffic, polynomial compilation, rank elimination, and
the exhaustive `Theta(A B^4)` replay. Thus the equality pair improves logical
payload constants and removes final-output scale from its projective class,
but does not change the explicit `Theta(B^3)` central side. The
`q^0.6` restatement additionally assumes `B=Theta(q^0.2)`.

## Strongest Valid Conclusion

> For valid nonzero outputs in the frozen left-associated circuit and tested
> affine targets, equality admits exact two-residual coefficient
> factorizations in ambient degree-8/4 coordinate-ring pieces of dimensions
> 24/12. Three fixed coordinate components specialize to two residual
> vectors, whose simultaneous zero set equals target equality.

Each ordered suffix has an exact factorization. Sampled canonical residual
evaluations agree under permutations internal to the suffix of the frozen
cut. Broader permutation/tree invariance is not certified.

The explicit-state boundary remains:

> Direct cut-2 logical coefficient materialization is `Theta(B^3)`; it is
> `q^(0.6+o(1))` only under `B=Theta(q^0.2)`. Cut 3 leaves
> `Theta(A B^2)` prefixes. No simultaneous-zero reporting algorithm has been
> constructed.

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

The next version must independently compare affine outputs, preserve planted
witnesses, emit authenticated factor chunks, and cover full `S4`
permutations, cross-cut allocations, all 14 binary trees, random rescaling,
infinity, doubling, inverse pairs, repeated points, and target rescaling.
