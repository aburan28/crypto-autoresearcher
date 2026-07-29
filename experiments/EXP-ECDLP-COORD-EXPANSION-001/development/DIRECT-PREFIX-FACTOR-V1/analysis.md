# Direct Prefix Factor V1 Analysis

## Status

`RESTRICTED THEOREM`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The exact 48- and 24-coordinate factors can be generated directly from the
frozen complete-addition circuit without constructing its five-axis tensor.
This is a factor compiler, not a zero-reporting algorithm or ECDLP
improvement.

## Exact Run

- source commit: `f4cec496`;
- curves: `q in {953,3919,15583}`;
- families: random-x, source-PRF-x, x-interval, rational-union;
- `B in {5,8,10}` and recorded `A` sizes `7,6,11`;
- cuts 2 and 3;
- planted and held-out target per cell;
- 12 family rows;
- 2,223,216 exact factor/locator pair checks;
- zero factor, component, locator, or zero-set mismatch;
- wall time: 57.78 seconds;
- peak RSS: 59,703,296 bytes;
- same-code deterministic normalized rerun: exact.

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

Every component in every cell is homogeneous of exactly the predicted
degree.

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

All component combinations reproduce the exact frozen-circuit locator.

## Observed Ranks

At cut 2:

- suffix `V` rank is 48 in all 24 target cells;
- prefix `U` rank is 34 or 35 of ambient 35 at `q=953`;
- prefix `U` rank is 48 at both larger curves.

At cut 3:

- prefix and suffix ranks are 24 in every cell and target.

The larger cells therefore attain the full coordinate-ring dimensions.
Low ambient rank is not hiding a smaller linear factor in this basis.

These ranks are representation-specific to the frozen RCB projective gauge.
The zero set is intrinsic, but nonzero values and factor geometry can change
under input permutation, parenthesization, or projective rescaling.

## Charged State

The direct compiler avoids the `A B^4` five-axis tensor, but the cut-2 suffix
state remains explicit:

| q | B | four-component cut-2 state | specialized cut-2 state |
|---:|---:|---:|---:|
| 953 | 5 | 24,000 field elements | 6,000 |
| 3919 | 8 | 98,304 field elements | 24,576 |
| 15583 | 10 | 192,000 field elements | 48,000 |

Symbolically these are:

- fixed component advice: `4 * 48 * B^3`;
- target-specialized factors: `48 * B^3`;
- specialization multiplications: `4 * 48 * B^3`.

With `B approximately q^0.2`, each is `q^(0.6+o(1))`, above rho. The observed
three-point slope is 0.745 because the frozen `B` schedule itself fits 0.248.

Cut 3 has:

- fixed component advice `4 * 24 * B^2`;
- specialized suffix factors `24 * B^2`;
- prefix count `A B^2`.

The suffix state is asymptotically `q^0.4`, but the explicit prefix side is
`q^0.6`, and no sublinear zero-reporting index is provided.

## Strongest Valid Conclusion

For the frozen left-associated complete-addition circuit:

> The central low-rank theorem is constructive. Exact cut-2 and cut-3
> factors can be compiled directly in 48- and 24-dimensional cubic
> coordinate-ring bases, with all target dependence carried by four public
> scalar weights.

The corresponding explicit-state negative is:

> Direct cut-2 factor advice and target specialization remain
> `Theta(B^3)=q^(0.6+o(1))`; cut 3 moves that size to the prefix side. Rank
> factorization alone does not cross rho.

## Next Concrete Action

There are now two linked successors:

1. `GAUGE-INVARIANT-FACTOR-V2`: normalize or quotient projective scale and
   test whether intrinsic factor images retain dimensions 48/24 under
   permutations and alternate addition trees.
2. `RANK2-NET-NORM-CIRCUIT-V1`: represent each leaf by an intrinsic
   rank-two net or divisor and test whether the four-sum divisor admits a
   target-independent iterated norm/resultant circuit below `B^2.5` state.

The gauge-invariant preflight comes first because zero-index structure must
belong to the predicate, not an arbitrary projective representative.
