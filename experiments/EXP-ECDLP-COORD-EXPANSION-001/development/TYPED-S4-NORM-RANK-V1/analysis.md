# Typed S4 Norm-Rank V1 Result

## Status

`NEGATIVE RESULT`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The preregistered progression-specific rank-reduction hypothesis failed. This
does not rule out sparse, nonlinear, target-restricted, or alternate-circuit
`4R` compilers.

## Exact Run

- pinned source commit: `eeb14eab44249f05c72885cfcdb29d44c8ce611e`;
- curves: prime orders `q=953,3919,15583`;
- coordinate `R` families: random-x, source-PRF-x, x-interval, and
  rational-union;
- matched `A` variants: public unknown-log progression and public
  hash-to-curve random set;
- cells: 24;
- exact source tuples: 1,111,608;
- complete RCB additions: 4,446,432;
- exact locator witnesses: 488;
- wall time: 34.20 seconds;
- maximum RSS: 103,628,800 bytes.

All runtime controls, RCB-to-affine replays, zero-locator equivalence checks,
and planted-witness checks passed.

The exact rerun verifier replayed all 24 cells and 12 matched comparisons. The
raw and rerun normalized SHA-256 values both equal
`72b8e22d55fa956474eeafeb3871c3b063147a8efb418ea84515e4ff6d635445`.

## Central Rank Result

The table gives the observed progression/random-A ranges. Each entry is
`cut-2 rank / cut-3 rank`; ambient dimensions are shown separately.

| q | ambient | `h` | `h^2` | `h^8` |
|---:|---:|---:|---:|---:|
| 953 | 35 / 25 | 34-35 / 24 | 34-35 / 25 | 34-35 / 25 |
| 3919 | 48 / 64 | 48 / 24 | 48 / 48 | 48 / 64 |
| 15583 | 110 / 100 | 48 / 24 | 96 / 48 | 109-110 / 100 |

The structural low ranks of `h` and `h^2` survive in the heterogeneous typed
tensor, but the early Hadamard powers grow toward the ambient dimensions.
This reproduces the earlier homogeneous norm-rank obstruction in the actual
`A+4R` source geometry.

For `h^8`, the progression/random-A ratios are:

- cut 2: `0.971-1.029`;
- cut 3: exactly `1.000`.

No family passes the required ratio `<=0.8` on any three-curve trajectory.
The positive gate is false and there are zero promoted families.

`NEGATIVE RESULT`: for this complete left-associated RCB circuit, locator, one
seed, and power schedule, replacing random `A` by the public group progression
does not reduce dense central ranks enough to support a progression-specific
compressed core.

## Exact Indicator

The exact zero indicator has much smaller ranks, but this is not a constructive
compiler signal. Its central ranks range from 2 to 10 at the tested cells,
while its progression/random-A ratios range from `0.5` to `2.33` and change
direction across families and sizes.

Each planted target has only 4-48 witnesses in a source tensor of size
4,375-110,000. A sparse tensor with few nonzero entries necessarily has low
unfolding rank. Constructing that support without enumerating the unknown
zero set is the cryptanalytic problem, so promoting indicator rank by itself
would be circular.

## Cost Boundary

This run is an exhaustive diagnostic:

- rank elimination used 260,870,005 field multiplications,
  253,588,995 subtractions, and 7,824 inversions;
- no compressed cores or witnesses were constructed;
- no arbitrary-target query was solved;
- no advice, memory, or online exponent improved.

The result is therefore not an ECDLP improvement.

## Reusable Lesson

The typed progression does not create the hoped-for dense-rank advantage. The
remaining useful object is the exact central factorization

`h(left,right) = U(left) dot V(right)`

with observed rank at most 48. A successor must test whether the `U` and `V`
vectors have constructive algebraic geometry that permits zero-inner-product
reporting below exhaustive `B^5`, rather than applying further blind Fermat
powers whose ranks saturate.

## Next Positive Question

Can the exact rank-48 central factors of the RCB norm locator be generated and
joined by a coordinate-specific orthogonal-vector index with:

- complete construction, advice, and peak memory below `q^(1/2)`;
- total target specialization and witness lift near `q^(1/5)`;
- support and independent-row penalties satisfying `u+r<1/10`;
- a proof or experiment showing that named EC-coordinate vectors are easier
  than generic vectors in `F_p^48`?

The paired negative track is to instantiate an orthogonal-vector or
structured-generic lower bound for these concrete factor vectors.
