# Direct Prefix Factor V1 Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`VALID ALGEBRAIC PROOF SKETCH`, `REVISE CERTIFICATION`.

For the fixed five-input, left-associated RCB polynomial circuit and canonical
projective lifts, the locator admits coefficient factorizations of ambient
dimensions at most 48 and 24. The current artifact computes and hashes those
factors, then validates them by exhaustive enumeration. Its same-code replay
does not independently certify the full theorem or complete accounting.

## Exact Run

- source commit: `f4cec496`;
- curves: `q in {953,3919,15583}`;
- families: random-x, source-PRF-x, x-interval, rational-union;
- `B in {5,8,10}` and recorded `A` sizes `7,6,11`;
- cuts 2 and 3;
- planted and held-out target per cell;
- 12 family rows;
- 2,223,216 exact factor/locator pair checks;
- zero factor, component, locator, or zero-set mismatch in the shared
  implementation;
- wall time: 57.78 seconds;
- peak RSS: 59,703,296 bytes;
- same-code deterministic normalized rerun: exact;
- independent proof gate: false;
- complete accounting gate: false.

## Coordinate-Ring Construction

For a cut after prefix point `S_k`, the remaining complete additions double
degree in `S_k`. The quadratic locator therefore has degree

`d_k=2^(6-k)`.

The smooth cubic coordinate ring is reduced with

`X^3=Y^2 Z-a X Z^2-b Z^3`.

Its degree-`d` piece has basis

`X^i Y^j Z^(d-i-j), 0<=i<=2`,

of dimension `3d`. Thus:

| cut | remaining R points | degree | basis dimension |
|---:|---:|---:|---:|
| 2 | 3 | 16 | 48 |
| 3 | 2 | 8 | 24 |

The implementation symbolically executes the frozen RCB circuit with a
generic prefix point, reduces every polynomial modulo the cubic, and emits
coefficient vectors in these fixed bases.

More precisely, the run computes and hashes the vectors but does not preserve
reusable vector tables. Every component in every cell is homogeneous of the
predicted degree.

## Four-Scalar Target Dependence

For final projective output `(X,Y,Z)` and target `(xq,yq,zq)`, the locator
splits exactly into four target-independent components:

`h_Q = zq^2 (X^2-nu Y^2)
       + zq*xq (-2XZ)
       + zq*yq (2nu YZ)
       + (xq^2-nu yq^2) Z^2`.

Consequently:

- prefix basis evaluation `U` is target-independent;
- suffix advice consists of four target-independent coefficient vectors;
- one target specializes each suffix vector with four scalar weights;
- no target logarithm or factor-base logarithm is used.

All component combinations reproduce the exact frozen-circuit locator inside
the shared implementation. Arbitrarily rescaled projective targets and the
target at infinity are algebraic boundaries, not empirical controls here.

## Observed Ranks

At cut 2:

- suffix `V` rank is 48 in all 24 target cells;
- prefix `U` rank is 34 or 35 of ambient 35 at `q=953`;
- prefix `U` rank is 48 at both larger curves.

At cut 3:

- prefix and suffix ranks are 24 in every cell and target.

The larger sampled matrices therefore attain the full coordinate-ring
dimensions. These are sampled factor-matrix ranks, not intrinsic predicate
rank, relation-matrix rank, or target-descent evidence. At `q=953`, cut-2
`U` is row-capped at 35 and one cell has rank 34.

These ranks are representation-specific to the frozen RCB projective gauge.
The zero set is intrinsic, but nonzero values and factor geometry can change
under input permutation, parenthesization, or projective rescaling.

## Charged State

Advice construction avoids the `A B^4` five-axis tensor, but the validation
harness enumerates every pair and temporarily retains flattened
`factor_values` and `exact_values` arrays. The executed run therefore does
full-surface validation even though the compiler formula does not require the
tensor.

If dense component tables are materialized, cut-2 suffix payload remains:

| q | B | four-component cut-2 state | specialized cut-2 state |
|---:|---:|---:|---:|
| 953 | 5 | 24,000 field elements | 6,000 |
| 3919 | 8 | 98,304 field elements | 24,576 |
| 15583 | 10 | 192,000 field elements | 48,000 |

Symbolically these are:

- fixed component advice: `4 * 48 * B^3`;
- target-specialized factors: `48 * B^3`;
- specialization multiplications: `4 * 48 * B^3`.

With `B approximately q^0.2`, each has exponent `0.6`. Payload and
specialization time are separate resource axes; under the stated promotion
budget, this explicit implementation fails both. The observed three-point
slope is descriptive only.

Cut 3 has:

- fixed component advice `4 * 24 * B^2`;
- specialized suffix factors `24 * B^2`;
- prefix count `A B^2`.

The suffix payload is asymptotically `q^0.4`, but the explicit prefix side is
`q^0.6`, and no sublinear zero-reporting index is provided.

Missing accounting includes polynomial operation counts, specialization
additions and reductions, advice reads/writes, memory traffic, prefix-vector
storage, deep live bytes, and separate compiler versus exhaustive-validation
time.

## Strongest Valid Conclusion

The valid algebraic proof sketch for the frozen left-associated circuit is:

> The locator admits coefficient factorizations of ambient dimensions at
> most 48 and 24 at cuts 2 and 3, with target dependence carried by four
> public scalar weights.

The observed run supports that construction on the toy schedule, but the
independent proof gate remains false.

The corresponding explicit-implementation negative is:

> If dense component tables are materialized, cut-2 payload and
> specialization work remain `Theta(B^3)=q^(0.6+o(1))`; cut 3 moves the
> explicit size to the prefix side. This does not rule out streamed,
> structured, differently gauged, or alternate-tree compilers.

Interpret the recorded `direct_factor_gate=true` only as a shared-code
semantic observation. The durable gate split is:

- semantic factor observation: true;
- independent proof: false;
- complete accounting: false;
- algorithm promotion: false.

## Next Concrete Action

There are now two linked successors:

1. `GAUGE-INVARIANT-FACTOR-V2`: independently verify affine sums and normal
   forms; add planted-hit counts, infinity/doubling/inverse controls,
   rescaled targets, permutations, alternate trees, mutations, and complete
   compiler/validation/memory accounting.
2. `RANK2-NET-NORM-CIRCUIT-V1`: represent each leaf by an intrinsic
   rank-two net or divisor and test whether the four-sum divisor admits a
   target-independent iterated norm/resultant circuit below `B^2.5` state.

The gauge-invariant preflight comes first because zero-index structure must
belong to the predicate, not an arbitrary projective representative.
