# Experiment Contract: Four-Sum Divisor Barrier V1

## Hypothesis

For coordinate factor bases of size `B approximately q^0.2`, the reduced
four-sum divisor has `Theta(B^4)` distinct support. Therefore any explicit
coordinate algebra, dense multiplication operator, or dense rational
function vanishing on every support point has dimension or pole degree
`Omega(B^4)`, above rho.

This is an explicit-divisor barrier only. A succinct resultant, arithmetic
circuit, or structured quotient may evade it.

## Null Hypotheses

1. Coordinate four-sum support collapses below `B^2.5`.
2. The canonical four-tuple census disagrees with exact `D2+D2` support.
3. The conclusion is caused by an incorrect multiset or permutation count.
4. A known compressible scalar progression fails to show small divisor
   support as a positive control.

## Parameters

- immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves `q=953,3919,15583`;
- random-x, source-PRF-x, x-interval, rational-union;
- scalar-progression positive control;
- canonical multiset sums of sizes 2, 3, and 4;
- exact affine curve addition;
- reduced point support and x-coordinate support;
- `D2+D2` support reconstructed from all unique `D2` points.

## Metrics

- canonical tuple counts;
- unique point and x-fibre support;
- collision multiplicities and entropy;
- direct-D4 versus D2+D2 support mismatch;
- support divided by `B^2.5` and `sqrt(q)`;
- minimum pole degree for a dense vanishing function;
- explicit coordinate-algebra dimension;
- dense final coefficient count;
- pair-attempt counts, group additions, bytes, wall time, and RSS;
- fitted support exponents against `q`.

## Restricted Theorem

If a nonzero rational function on a smooth projective curve vanishes at
`m` distinct rational points, its pole divisor has degree at least `m`,
because a principal divisor has degree zero.

For a reduced split divisor with `m` support points, its coordinate algebra
has dimension `m`. Thus explicit dense divisor/norm representations require
`Omega(m)` field elements. This does not lower-bound arithmetic-circuit size.

## Positive Control

The scalar-progression factor base should have four-sum support `O(B)`, well
below coordinate-family support and the canonical tuple count.

## Success Criterion

An explicit-divisor barrier signal requires all four coordinate families on
all three curves to satisfy:

- exact agreement between direct canonical D4 and D2+D2 support;
- D4 support greater than `B^2.5`;
- D4 support greater than `sqrt(q)`;
- zero semantic mismatch;
- scalar-progression support materially smaller.

## Falsification Criterion

Any support mismatch falsifies the implementation. Support below `B^2.5`
promotes that family to a divisor-compression successor. A barrier signal
does not rule out succinct circuits, nonreduced schemes, multiplicity
compression, target batching, or alternate divisors.

## Reproduction Command

```bash
python3 src/four_sum_divisor_barrier.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --positive-control scalar_progression_control
```
