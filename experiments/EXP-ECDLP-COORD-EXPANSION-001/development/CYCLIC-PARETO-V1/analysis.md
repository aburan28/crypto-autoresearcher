# Cyclic Pareto V1 Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`NOVELTY-UNVERIFIED`.

The Stage-A joint support inequality is feasible for some unrestricted factor
bases in small prime cyclic groups. This is a positive existence result for
the finite model, not evidence of a scalable coordinate construction.

## Census

The run exhaustively enumerated 541,833 factor bases under the same
`lambda=0.5` formal-occupancy rule used by the coordinate experiment.

| q | sign policy | B | sets | median `(d2,d3,d5_new)` | qualifying | fraction |
|---:|---|---:|---:|---|---:|---:|
| 19 | canonical | 3 | 816 | `(6,9,7)` | 0 | 0 |
| 19 | complete | 4 | 36 | `(9,13.5,5.5)` | 9 | 0.25 |
| 31 | canonical | 3 | 4,060 | `(6,10,12)` | 0 | 0 |
| 31 | complete | 4 | 105 | `(9,16,10)` | 0 | 0 |
| 43 | canonical | 4 | 111,930 | `(10,19,19)` | 294 | 0.002627 |
| 43 | complete | 4 | 210 | `(9,16,14.5)` | 0 | 0 |
| 59 | canonical | 4 | 424,270 | `(10,19,27)` | 0 | 0 |
| 59 | complete | 4 | 406 | `(9,16,16.5)` | 0 | 0 |

The gate is `d2<=0.8*median(d2)`, `d3<=0.8*median(d3)`, and
`d5_new>=0.9*median(d5_new)`.

## Positive witness

For `Z/43Z`, the sign-canonical base

`F={1,4,7,38}={1,4,7,-5}`

has

`(d2,d3,d5_nonidentity,d5_new)=(8,12,20,19)`.

The thresholds are `(8,15.2,17.1)`, so the base crosses all three joint
conditions. Its metric tuple occurs for 84 enumerated bases. Two additional
qualifying metric classes occur:

- `{1,4,10,-2}` gives `(8,12,20,18)`;
- `{1,5,18,-8}` gives `(8,12,19,18)`.

The first witness is affinely equivalent over the integers to the near
progression `{-2,0,1,2}` before reduction modulo 43. That supplies a concrete
structural clue: a small-doubling set can still gain substantial new support
between depths three and five when translation and modular wraparound place
the lower-depth sumsets favorably.

## Non-scaling warning

No sign-canonical base qualifies at `q=59`. At the required coverage there,
the minimum observed `d2` is 9 while the threshold is 8; among jointly
compressed sets the maximum `d5_new` is 20 while the threshold is 24.3.

Thus V1 does not show a scalable family. The `q=43` witness may be a
finite-size wraparound resonance. Translation also changes `D5_new` because
depths one, three, and five shift by different multiples, so any follow-up
must charge how a translation is selected and test it on held-out groups.

## Restricted conclusion

The coordinate Stage-A thresholds are not intrinsically contradictory in
small cyclic groups. The failure of x intervals, square images, and the
frozen rational union is therefore representation-specific at these sizes,
not explained solely by an impossible joint support target.

## Next positive experiment

Classify the affine orbits of all 294 `q=43` witnesses, extract their integer
normal forms, and test preregistered near-progression families over larger
prime cyclic groups and generated elliptic curves. Freeze scale and
translation rules before held-out evaluation.

## Next proof experiment

For families with bounded doubling `|2F|<=K|F|`, quantify the maximum possible
new growth `|5F \ (F union 3F)|` as a function of `K`, group order, and
translation. Compare the exhaustive frontier with Freiman-type progression
models and identify exactly where modular wraparound permits catch-up growth.
