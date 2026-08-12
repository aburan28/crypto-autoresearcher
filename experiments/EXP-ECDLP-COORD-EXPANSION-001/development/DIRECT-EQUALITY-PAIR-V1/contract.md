# Experiment Contract: Direct Equality Pair V1

## Hypothesis

Replacing the quadratic norm locator by its two projective equality residuals

`e_x=zq X-xq Z`, `e_y=zq Y-yq Z`

gives an intrinsic simultaneous-zero predicate with direct central factors of
dimensions 24 and 12, half the degree of the norm factors. The projective
residual pair is invariant under output rescaling, tuple permutation, and
choice of affine representative.

## Null Hypotheses

1. Direct polynomial factors do not reproduce both numerical residuals.
2. The simultaneous zero set differs from exact target equality.
3. Different RCB orderings preserve the point but change the projective
   residual pair.
4. The lower dimensions still require explicit `Theta(B^3)` suffix state and
   do not supply a simultaneous-zero index.

## Parameters

- immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves `q=953,3919,15583`;
- random-x, source-PRF-x, x-interval, rational-union;
- recorded public progression `A`;
- planted and held-out target per family;
- cut 2: degree 8, dimension 24, three ordered suffix points;
- cut 3: degree 4, dimension 12, two ordered suffix points;
- coordinate-ring relation
  `X^3=Y^2 Z-a X Z^2-b Z^3`;
- target-independent suffix components `X,Y,Z`;
- target-specialized factor pair `(e_x,e_y)`.

## Metrics

- basis dimensions and polynomial degrees;
- prefix and suffix counts;
- `U`, `V_x`, and `V_y` ranks;
- three-component fixed advice and two-vector specialized advice;
- every-pair residual, norm-reconstruction, and zero-set mismatches;
- projective-pair mismatches across all suffix permutations;
- mismatches against the canonical affine representative;
- operations, bytes, wall time, and peak RSS.

## Positive Controls

- projective residual pairs are unchanged by arbitrary common nonzero scale;
- `(e_x,e_y)=(0,0)` iff the exact complete-addition output equals the target;
- `e_x^2-nu e_y^2` equals the prior exact norm locator;
- all ordered suffix permutations have the same canonical residual pair;
- the affine representative has the same canonical pair.

## Success Criterion

Every cell must have dimensions 24/12 and zero factor, norm, zero-set,
permutation, and affine-section mismatches under deterministic exact replay.

Passing constructs a gauge-invariant factor oracle only.

## Algorithm Promotion Criterion

A separate simultaneous-zero index must avoid explicit `B^3` suffix
generation/scanning, preserve witnesses, and meet the charged sub-rho
relation, rank, memory, and descent gates.

## Falsification Criterion

Any semantic or invariance mismatch falsifies the compiler. If the exact pair
still requires `Theta(B^3)` state, preserve the lower-degree theorem and the
explicit-state negative separately.

## Reproduction Command

```bash
python3 src/direct_equality_pair.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```
