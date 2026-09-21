# Typed S4 Factor Geometry V1 Result

## Status

`NEGATIVE RESULT`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The preregistered progression-specific factor-geometry hypothesis failed. The
result does not rule out nonlinear, sparse, batched, or alternate-circuit
joins.

## Exact Run

- pinned source commit: `87edb6ba427dc7e4ac699410f8e53d49a2ab036b`;
- curves: prime orders `q=953,3919,15583`;
- coordinate `R` families: random-x, source-PRF-x, x-interval, and
  rational-union;
- matched `A` variants: public unknown-log progression and public
  hash-to-curve random set;
- cuts: `[A,R]|[R,R,R]` and `[A,R,R]|[R,R]`;
- cells: 24;
- exact source tuples: 1,111,608;
- complete RCB additions: 4,446,432;
- dense controls: three per cell and cut;
- wall time: 46.51 seconds;
- maximum RSS: 95,813,632 bytes.

All source, locator, planted-witness, exact rank-factor reconstruction,
zero-set, dense-rank, dense-projective-diversity, and dense-affine-span
controls passed.

The exact rerun verifier replayed all 24 cells and 12 comparisons. Raw and
rerun normalized SHA-256 values both equal
`83594d80ccfef4aca7c9ddb6f5ab39724a9cbb84c0400cfed9ca67c1ef8c0387`.

## Factor Ranks

For cut 2, the rank is 34-35 at `q=953` and 48 at the two larger curves. For
cut 3, every cell has rank 24. Each factorization reconstructs every entry of
the exact RCB norm tensor.

These bounded ranks compactly represent the locator, but the geometry within
the rank coordinates does not collapse under progression `A`.

An independent theory review proves that these are circuit-prefix bounds, not
accidental fits. If `S_k` is the prefix point at cut `k`, the locator has
degree `2^(6-k)` in `S_k`. The degree-`d` piece of a smooth plane cubic's
homogeneous coordinate ring has dimension `3d`, giving exact bounds 48 and 24
at cuts two and three. The same argument bounds `h^e` by `48e` and `24e`,
which explains both the observed `h^2` ranks and permitted `h^8` saturation.

## Progression Fibers

At both cuts, for every curve, family, and `A` variant:

- every fixed-trailing-`R` fiber across `A` has affine rank exactly
  `|A|-1`;
- the median progression/random-A affine-rank ratio is exactly `1.0`;
- every fiber contains `|A|` projectively distinct vectors.

Thus the progression is maximally affine-independent at the tested source
sizes. No family passes the required 20-percent collapse gate.

## Projective Diversity

The progression/random-A ratios for total `U` projective-unique fraction range
from `0.971` to `1.094`; none approaches the required `0.8`.

At cut 2, projective diversity is 97.1-100 percent of the source permutation
orbit ceiling.

At cut 3, raw diversity is lower because swapping the two left-side `R`
inputs is a forced symmetry. After quotienting that symmetry, projective
diversity is still 88.6-100 percent of the source orbit ceiling.

`NEGATIVE RESULT`: the observed projective collisions are explained by source
permutations and isolated toy coincidences, not by the public progression.

## Zero Incidences

- ordered zero pairs: 4-48 per cell;
- canonical witnesses after quotienting all four `R` permutations: 1-3;
- ordered/canonical amplification: 4-24;
- matched dense-control mean zero pairs: 2.33-9.33.

The exact cells contain an intentionally planted witness. Their larger ordered
counts primarily reflect permutations of the same one to three canonical
decompositions. This is a useful constant-factor symmetry but not an exponent
gain.

The factorization does not expose the zeros: producing it already enumerates
the full tensor, and generic inner-product testing over all factor pairs costs
the same `B^5` source volume.

## Charged Diagnostic Cost

Exact factor extraction used:

- 58,948,769 field multiplications;
- 58,348,845 field subtractions;
- 1,622 field inversions;
- 351,658 row updates.

This excludes the additional dense-control dot products and source RCB
arithmetic. No index, advice structure, online query, or witness lift was
constructed.

## Strongest Valid Conclusion

`OBSERVATION`: the complete RCB norm locator on typed `[A,R,R,R,R]` sources
admits exact central ranks 24 and at most 48 on the tested cells.

`NEGATIVE RESULT`: replacing random `A` with the public group progression
does not create a 20-percent affine or projective collapse in those factors.
After source symmetries are removed, the factors retain near-maximal observed
projective diversity.

This is a negative for linear/projective factor geometry, not for all
coordinate-specific `4R` compilers.

## Next Positive Question

The remaining loopholes must use structure not measured by rank, affine span,
or projective collisions:

1. a nonlinear low-degree variety or recurrence in the factor vectors;
2. target batching that amortizes zero-inner-product searches;
3. a sparse or algebraic zero finder that operates on the RCB circuit without
   materializing its tensor;
4. a different addition tree or locator whose powering does not saturate.

An independent algorithm review also identifies an aligned many-target
special case. For `Q_t=Q0+tD`, the progression index and target index occur
only through `k=t-i`. A `D2+R` scan can therefore serve a batch in
`B^3+B(T+B)` work and `B^2+B(T+B)` memory. This can beat rho amortized per
aligned target for `B^(1/2)<T<B^(3/2)`, but it is not a one-target exponent
improvement and its relation-rank yield is untested.

Any successor must compare against generic finite-field orthogonal-vector
reporting and retain the strict end-to-end ECDLP cost gates.
