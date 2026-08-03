# Asymmetric Layers V1 Analysis

## Status

`POSITIVE SIGNAL`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`NOVELTY-UNVERIFIED`.

Position-specific layers can combine a small pair image with stable
five-term coverage. This is the first positive mechanism in this experiment
family that persists across increasing cyclic-group sizes.

It is not yet a coordinate construction or an ECDLP improvement. The
materialized transverse triple layer is much larger than the rho-scale
frontier permits.

## Construction

Relations have the typed form

`A + A + R + R + R = Q`,

where:

- `A` is an arithmetic progression;
- `R` is a disjoint random transverse set;
- `|A|` and `|R|` minimize total columns subject to
  `(2|A|-1)*binomial(|R|+2,3)/q >= 0.5`.

The compiler materializes `2A` and `3R`, then scans `2A` against a `3R`
membership table.

## Exact results

| q | `|A|` | `|R|` | columns | `|2A|` | `|3R|` | success | `T_perm` |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 251 | 4 | 4 | 8 | 7 | 20 | 0.464 | 5.49 |
| 503 | 3 | 6 | 9 | 5 | 55 | 0.448 | 4.01 |
| 1009 | 4 | 7 | 11 | 7 | 82 | 0.443 | 5.52 |
| 2003 | 5 | 8 | 13 | 9 | 118 | 0.420 | 7.16 |
| 4001 | 4 | 11 | 15 | 7 | 279 | 0.407 | 5.69 |
| 8009 | 5 | 13 | 18 | 9 | 448 | 0.405 | 7.23 |
| 16001 | 8 | 14 | 22 | 15 | 554 | 0.413 | 11.85 |
| 32003 | 9 | 17 | 26 | 17 | 957 | 0.410 | 13.46 |

Coverage remains near the random-sum prediction for occupancy 0.5. The
materialized pair layer stays tiny, and the random-permutation online scan
remains far below `sqrt(q)` at these sizes.

## Scaling

Exploratory fitted exponents over eight group sizes are:

- columns: `0.247`;
- pair support and online scan: `0.210` and `0.211`;
- triple support: `0.767`;
- support-mass advice: `0.724`;
- compiler transitions: `0.747`;
- nonidentity five-term support: `0.974`.

The design target predicts the cleaner asymptotic profile

- columns: `q^(1/4)`;
- pair scan: `q^(1/4)`;
- materialized triple advice/build: `q^(3/4)`;
- constant success probability.

## Cost boundary

The observed support-mass and online exponents give

`S*T^2 approximately q^(0.724+2*0.211)=q^1.146`,

above the generic fixed-preprocessing frontier. The theoretical materialized
profile is `q^(3/4)*q^(1/2)=q^(5/4)`.

For relation collection, roughly `q^(1/4)` columns require the same order of
independent rows. At `q^(1/4)` query work per row, collection reaches
`q^(1/2)` before linear algebra. Sparse linear algebra on `q^(1/4)` columns
also sits near `q^(1/2)`.

Therefore this is a viable index-calculus *architecture*, not yet a
faster-than-rho algorithm. It has no asymptotic slack until at least:

1. triple-membership advice/build is reduced below `q^(1/2)`;
2. relation collection or matrix solving gains strict slack below `q^(1/2)`;
3. the scalar layers are replaced by public coordinate-defined sets with
   unknown logs and charged construction.

## Concrete research target

Build a coordinate-specific representation of `3R` supporting exact
membership and witness lift with:

- fixed advice and construction `q^(1/2-epsilon)`;
- online work no worse than the `2A` scan, `q^(1/4+o(1))`;
- exact constant target coverage;
- typed relation rows over `A union R`;
- batch relation collection and rank tests;
- no subgroup-log oracle in construction or query.

Recursive S3 addition-law circuits, compressed algebraic joins, and
fixed-curve batch decomposition are directly relevant to this target.

## Failure modes

- Materializing `3R` keeps preprocessing at `q^(3/4)`.
- Replacing membership by scanning one `R` leaf against `2R` gives
  rho-scale or worse total work.
- `q^(1/4)` columns put ordinary sparse linear algebra at the square-root
  boundary.
- Scalar-defined layers reveal logs and are evaluator-only toys.
- Support does not establish independent relation rows or target descent.

## Next experiment

Replace random scalar `R` with a coordinate-defined transverse set and compare
three exact membership representations:

1. materialized `3R`;
2. `R` scan plus materialized `2R`;
3. recursive S3 circuit or algebraic codec with witness lift.

Run many-target relation collection, measure rank and matrix cost, and retain
the full fixed-curve offline/online/storage accounting.
