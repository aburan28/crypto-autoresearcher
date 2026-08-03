# Experiment Contract: Direct Prefix Factor V1

## Hypothesis

The exact complete-addition locator can be compiled directly at central cuts
into the degree-16 and degree-8 homogeneous coordinate-ring bases of the
elliptic curve, producing exact 48- and 24-coordinate factors without
constructing the five-axis locator tensor.

Moreover, all target dependence is carried by four public scalar weights, so
the suffix advice can be separated into four target-independent component
tables.

## Null Hypotheses

1. Polynomial reduction modulo the cubic does not reproduce the frozen
   complete-addition circuit.
2. The four target components omit projective-target or scaling behavior.
3. Direct factors are correct but require `Theta(B^3)` target-independent
   suffix state and therefore do not improve the explicit central join.
4. Low factor dimension is mistaken for a zero-reporting algorithm.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: `q=953,3919,15583`;
- coordinate families: random-x, source-PRF-x, x-interval,
  rational-union;
- `A`: recorded public unknown-log progression;
- targets: one deterministic planted target and one deterministic held-out
  target per curve/family;
- cuts:
  - cut 2, prefix `A+R`, three ordered suffix points, degree 16, dimension 48;
  - cut 3, prefix `A+R+R`, two ordered suffix points, degree 8, dimension 24;
- quotient:
  `X^3=Y^2 Z-a X Z^2-b Z^3`;
- basis: all degree-`d` monomials with `X` exponent at most two;
- locator components:
  `X^2-nu Y^2`, `-2XZ`, `2nu YZ`, `Z^2`;
- target weights:
  `zq^2`, `zq*xq`, `zq*yq`, `xq^2-nu*yq^2`.

## Metrics

- polynomial operations and normal-form term counts;
- exact basis dimensions;
- prefix rows and suffix component vectors;
- component and target-specialized advice field elements and bytes;
- target-specialization multiplications;
- factor-side ranks;
- every-pair reconstruction mismatches;
- exact complete-addition locator mismatches;
- zero-set mismatches and target-component mismatches;
- construction, verification, wall time, and peak RSS;
- fitted state exponent against `q`.

## Positive Controls

- the cubic relation reduces to zero;
- symbolic complete addition evaluated at a curve point equals the frozen
  numerical complete-addition circuit;
- all four target components reconstruct the direct locator polynomial;
- every factor dot product equals the exact locator for both targets;
- every exact zero agrees with affine point equality.

## Success Criterion

The direct-factor theorem is empirically instantiated only if every cell has:

- dimensions exactly 48 and 24;
- zero polynomial, component, factor, locator, and zero-set mismatch;
- deterministic exact replay;
- complete advice and specialization accounting.

This authorizes use of the factor compiler in a later zero-index experiment.

## Algorithm Promotion Criterion

No ECDLP algorithm is promoted unless a separate zero-reporting method:

- avoids explicit `B^3` suffix generation or scanning;
- retains exact witnesses;
- keeps fixed advice/build below `q^0.5`;
- keeps target work and memory traffic near `q^0.2`;
- preserves relation rank and individual descent.

## Falsification Criterion

Any semantic mismatch falsifies the implementation. If the direct compiler
requires `Theta(B^3)` component vectors and target specialization, preserve a
correctness theorem plus an explicit-state negative; do not infer an attack
from rank 24 or 48.

## Reproduction Command

```bash
python3 src/direct_prefix_factor.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```
