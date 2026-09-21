# Experiment Contract: Typed Five-Term Elliptic-Curve V1

## Hypothesis

On generated ordinary prime-order curves over prime fields, a public
unknown-log progression `A={P0+iD}` and a coordinate-defined transverse set
`R` support exact decompositions

`Q = P0 + iD + R_j1 + R_j2 + R_j3 + R_j4`

with constant probability. The resulting known-right-hand-side relations
reach full rank after quotienting the unavoidable one-dimensional gauge, and
the quotient solution recovers held-out target logarithms.

This experiment tests functional relation architecture. It does not test a
compressed `4R` compiler and cannot establish an exponent improvement.

## Null hypothesis

At least one of the following occurs:

- coordinate `R` loses the constant-support behavior seen in the cyclic model;
- typed relation rows have rank defects beyond the predicted gauge;
- the quotient system does not recover its diagnostic logs;
- held-out typed descent does not recover known target scalars;
- point-only witnesses disagree with the diagnostic scalar census.

## Parameters

- field/curve family: seeded, generated, ordinary, nonspecial, prime-order
  short-Weierstrass curves over `F_p`;
- sizes: 10, 12, and 14 bits for the development sweep;
- seed: 271828;
- `A,R` sizes: deterministic optimizer satisfying
  `|A|*binomial(|R|+3,4)/q >= 0.5`;
- coordinate `R`: random-x, source-PRF-x, x-interval, and rational-union;
- model control: scalar progression, explicitly attack-ineligible;
- relation shape: one `A` term and four `R` terms;
- baseline: materialized exact `4R`, plus `R`-scan with materialized `3R`;
- rho scale: `sqrt(q)` analytical reference.

## Construction Boundary

Before any subgroup scalar census is created, the program must:

1. generate `R` using public point/coordinate operations;
2. hash independent public points `P0,D`;
3. construct and freeze `A`;
4. compile point-keyed exact `3R` and `4R` witnesses;
5. collect known-right-hand-side relation rows, retaining every supported
   `A` split found by one complete `A` scan per target;
6. solve the gauge-quotiented relation system;
7. execute held-out target descent.

The subgroup census is diagnostic only and is created afterward to verify the
solution. No census value may affect construction, lookup, row selection,
rank, solving, or descent.

## Gauge

Every row has coefficient `1` on `log(P0)` and total coefficient `4` on the
`R` columns. Therefore the full matrix has the exact null vector

`(-4, 0, 1, ..., 1)`.

The attack-visible solver removes `R_0` and uses the equivalent variables

- `p0' = log(P0) + 4*log(R_0)`;
- `d = log(D)`;
- `r_j' = log(R_j)-log(R_0)` for `j>0`.

The expected quotient width is `|R|+1`. Full unquotiented rank is neither
expected nor claimed.

## Metrics

- coordinate and progression build group/field operations;
- exact `3R` and `4R` entries, transitions, bytes, and build operations;
- relation targets attempted, successful targets, candidate rows, independent
  rows, and rank;
- query additions, probes, lookups, and memory traffic proxy;
- modular linear-algebra operations;
- exact support probability;
- held-out descent successes and verified logarithms;
- analytical exponents for `|R|`, `|3R|`, `|4R|`, relation collection, and
  query work;
- all source, raw-result, command, environment, and Git hashes.

## Positive Control

Random-x is expected to behave like a random coordinate slice: near-constant
typed support, quotient rank `|R|+1`, and correct held-out descent.

## Negative Control

The scalar-progression control is expected to compress additive support. It
contains scalar metadata and is never attack-eligible. It checks that the
experiment detects structured-support collapse rather than merely replaying
the intended conclusion.

## Success Criterion

For each attack-eligible family at all three sizes:

- every returned witness verifies using points only;
- quotient rank reaches `|R|+1` within the declared target budget;
- the solved quotient variables match the post hoc diagnostic census;
- every supported held-out descent recovers its known scalar;
- exact support remains at least 0.25.

Passing this criterion supports only the typed relation architecture.

## Falsification Criterion

Any witness mismatch, inconsistent relation, incorrect quotient solution, or
incorrect held-out logarithm invalidates the run. A family is narrowed if it
misses rank or 0.25 exact support on any size. Materialized compiler cost at or
above square-root scale is a scoped negative for that compiler, not for
coordinate point decomposition generally.

## Stop Rules

- at most five families per curve;
- at most `min(q-1,64*(|R|+1))` relation targets per family;
- at most 64 held-out targets per family;
- no production keys or external targets;
- fail closed on construction overlap, identity points, witness mismatch,
  rank inconsistency, or diagnostic mismatch.

## Reproduction Command

```bash
python3 src/typed_five_ec.py \
  --bit-sizes 10 12 14 \
  --seed 271828 \
  --families random_x source_prf_x x_interval rational_union scalar_progression_control \
  --occupancy-lambda 0.5 \
  --held-out-targets 64
```
