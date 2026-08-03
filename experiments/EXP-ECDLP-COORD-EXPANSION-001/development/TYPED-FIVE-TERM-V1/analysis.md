# Typed Five-Term V1 Analysis

## Status

`POSITIVE SIGNAL`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`NOVELTY-UNVERIFIED`.

The typed five-term shape

`A + R + R + R + R = Q`

preserves constant support coverage while keeping the explicit `A` scan and
the relation-column dimension near `q^(1/5)`.

This is a viable classical index-calculus architecture to optimize. It is not
yet a coordinate construction, a compressed relation compiler, or a
faster-than-rho algorithm.

## Mechanism

`A={P0+iD}` is intended to be a public group progression generated from two
unknown-log public points. Although it contains about `q^(1/5)` points, its
logs are represented by only two unknowns:

`log(P0+iD)=log(P0)+i*log(D)`.

`R` is intended to be a coordinate-defined transverse factor base of about
`q^(1/5)` points with one log unknown per point.

The exact query scans `A` and tests whether `Q-A_i` lies in `4R`.

## Exact cyclic results

| q | `|A|` | `|R|` | log unknowns | `|4R|` | success | `T_perm` |
|---:|---:|---:|---:|---:|---:|---:|
| 251 | 4 | 4 | 6 | 35 | 0.448 | 3.25 |
| 503 | 4 | 5 | 7 | 69 | 0.456 | 3.24 |
| 1009 | 5 | 6 | 8 | 124 | 0.506 | 3.89 |
| 2003 | 8 | 6 | 8 | 125 | 0.399 | 6.45 |
| 4001 | 7 | 8 | 10 | 319 | 0.440 | 5.55 |
| 8009 | 9 | 9 | 11 | 487 | 0.436 | 7.10 |
| 16001 | 12 | 10 | 12 | 704 | 0.420 | 9.48 |
| 32003 | 12 | 12 | 14 | 1,343 | 0.408 | 9.57 |

The size optimizer minimizes the larger of the relation-collection proxy
`|A|*|R|` and the linear-algebra proxy `|R|^2`, subject to

`|A|*binomial(|R|+3,4)/q >= 0.5`.

Asymptotically it balances `|A|` and `|R|`, giving both
`Theta(q^(1/5))`.

## Scaling

Exploratory fitted exponents are:

- A scan: `0.251`;
- transverse size: `0.218`;
- log unknowns: `0.169`;
- relation-collection proxy: `0.419`;
- linear-algebra proxy: `0.337`;
- materialized `4R`: `0.726`;
- D4 compiler transitions: `0.733`;
- final support: `0.976`.

Discrete sizes and additive constants depress several finite-size slopes. The
intended asymptotic profile is:

- scan and log columns: `q^(1/5)`;
- relation collection and ordinary sparse linear algebra: `q^(2/5)`;
- materialized D4 advice/build: `q^(4/5)`;
- constant decomposition probability.

## Breakthrough condition

Materializing `4R` destroys the attack: with `T=q^(1/5)`, its
`S*T^2` scale is `q^(6/5)`.

A credible exponent-breaking successor needs:

1. public coordinate-defined `R` with unknown logs;
2. exact `4R` membership and witness lift with fixed advice/build
   `q^(1/2-epsilon)`;
3. online specialization no worse than `q^(1/5+o(1))`;
4. about `q^(1/5)` independent typed relation rows;
5. rank, filtering, and linear algebra below `q^(1/2-epsilon')`;
6. held-out target descent;
7. full fixed-curve preprocessing, bytes, bandwidth, and success accounting.

The `q^(1/2)` advice threshold is an end-to-end attack budget, not a result
already achieved. It is also below the generic preprocessing requirement for
`T=q^(1/5)`, so any successful compiler must exploit actual elliptic-coordinate
structure rather than only generic group operations.

## Why this is especially relevant

This architecture converts the broad five-term research bet into one sharply
defined subproblem:

> Compile exact witness-bearing membership in the fourfold sum of a
> `q^(1/5)` coordinate factor base using less than square-root fixed-curve
> preprocessing.

Recursive S4 addition-law circuits, algebraic joins, fixed-curve advice, and
batch point decomposition all target this object directly.

## Failure modes

- A scalar-defined progression would reveal logs; `P0` and `D` must be
  independently generated public points with unknown logs.
- The R points must be coordinate-generated without subgroup-log selection.
- Generic MITM for `4R` remains square-root scale or worse.
- Constant support does not imply independent relation rows.
- Standard matrix solving is favorable only if the typed coefficient matrix
  actually reaches rank with the predicted column count.
- A fixed-curve precomputation win must state supported targets and
  amortization explicitly.

## Next experiment

Implement the typed construction on generated toy elliptic curves:

- hash two independent points for `P0,D`;
- construct `A={P0+iD}`;
- construct coordinate `R` from random-x, x-interval, and rational-map
  families;
- build exact materialized `4R` only as an audit baseline;
- collect known-RHS typed relations;
- measure rank and held-out descent;
- compare materialized D4, `R`-scan plus D3, and recursive S4 membership.
