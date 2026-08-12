# Experiment Contract: Typed S4 Factor Geometry V1

## Hypothesis

For the exact central rank factorizations of the complete RCB norm tensor

`h(left,right) = U(left) dot V(right)`,

the public progression `A={P0+iD}` produces invariant geometric collapse in
the `U` vectors that is absent for a matched public random unknown-log `A`.
Such collapse could be a prerequisite for a coordinate-specific
zero-inner-product index for typed `A+4R` decomposition.

## Null Hypothesis

After matching the curve, coordinate `R`, source sizes, planted target,
circuit, locator, rank field, and factorization algorithm, progression `A`
does not reduce both projective diversity and fixed-`R` fiber affine span by
at least 20 percent at cuts two and three.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: prime orders `q=953,3919,15583`;
- `R` families: random-x, source-PRF-x, x-interval, rational-union;
- `A` variants: the recorded public progression and matched public
  hash-to-curve random set;
- tensor axes: `[A,R,R,R,R]`;
- cuts:
  - cut 2: `[A,R] | [R,R,R]`;
  - cut 3: `[A,R,R] | [R,R]`;
- locator: exact complete RCB norm residual `h`;
- field: `F_p`;
- dense-vector controls: three deterministic rank-matched random factor pairs
  per cell.

## Metrics

- exact factor rank and reconstruction mismatches;
- factor digests;
- projectively distinct `U` and `V` vectors;
- projective diversity relative to the exact source permutation-orbit ceiling;
- affine-span rank of each side;
- fixed-trailing-`R` affine-span rank across the `A` axis;
- fixed-trailing-`R` projective diversity across the `A` axis;
- ordered zero incidences and left/right degree distributions;
- canonical witnesses after quotienting permutations of the four `R` indices;
- ordered-to-canonical witness amplification;
- matched dense-control incidence mean/range and theoretical `NM/p`;
- tuple, field-operation, memory, traffic, and wall-time counters.

Projective diversity and affine-span dimensions are invariant under invertible
changes of rank-factor coordinates. Coordinate sparsity is deliberately not a
promotion metric.

## Positive Controls

- rank-one, spike, and dense matrix controls from the norm-rank experiment;
- exact factor reconstruction for every tensor entry;
- every planted target has an exact zero;
- the factor dot product and recorded norm residual have identical zero sets;
- deterministic dense controls attain their generated factor rank.
- deterministic dense controls have full projective diversity and the expected
  affine-span rank.

## Negative Control

Matched random `A` removes the group progression while preserving public
unknown-log point construction. Rank-matched dense factors test whether
incidence counts differ from generic finite-field vectors.

## Success Criterion

A provisional signal requires, on all three curves and at least three of four
`R` families:

- progression/random-A projective-unique ratio `<=0.8` for `U` at both cuts;
- progression/random-A median fixed-`R` fiber affine-rank ratio `<=0.8` at
  both cuts;
- no factor, source, locator, or planted-witness mismatch;
- the collapsed progression geometry is not reproduced by dense controls.

This authorizes only a constructive zero-inner-product indexing successor.

## Falsification Criterion

The hypothesis is narrowed if ratios exceed `0.8`, change direction across
cuts or sizes, or both variants saturate the same invariant dimensions.

A negative result applies only to linear/projective geometry of these exact
rank factors and this circuit. It does not rule out nonlinear varieties,
alternate addition trees, target batching, sparse algorithms, or other
coordinate compilers.

## Cost Boundary

This run enumerates the complete tensor and all zero incidences. Enumeration
is charged and is never treated as an index.

Any promoted index must still satisfy:

- complete build, retained advice, and peak memory exponents `<1/2`;
- relation collection
  `c+u+r+max(t,w)<1/2`, with `c=1/5`;
- executed linear algebra and arbitrary-target descent exponents `<1/2`;
- at intended `t=w=1/5`, the strict penalty condition `u+r<1/10`.

Low rank alone is not an algorithm: generic zero-inner-product reporting over
`F_p^d` remains the matched barrier.

## Reproduction Command

```bash
python3 src/typed_s4_factor_geometry.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --a-variants progression random \
  --cuts 2 3 \
  --dense-controls 3
```
