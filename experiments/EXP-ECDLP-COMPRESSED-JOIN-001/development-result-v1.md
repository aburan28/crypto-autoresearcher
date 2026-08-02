# Development result v1: coordinate-routed compressed join

## Status

- `RESTRICTED THEOREM`: a prime-order group has no nontrivial homomorphism into a smaller finite group, so the integer modular-routing step has no direct exact EC quotient port.
- `OBSERVATION`: the bucket router returns exact D4 and D5 witnesses and completes randomized toy descent.
- `OBSERVATION, REVISE`: an apparent x-coordinate locality signal against full-point random labels disappears against a sign-matched random x-fiber null.
- `NEGATIVE RESULT`: no tested router beats either exact materialized D4 in both advice and online work or fixed-base BSGS at equal advice.
- `TOY-EVIDENCE`, `NON-CANONICAL`: one seed at 10, 12, and 14 bits; no approval record and no canonical run.

## Evidence hashes

- raw file SHA-256: `6e195aad466b67ad2bd6181c5c8db44727858de8427965ff08709e5eb4bbd270`
- canonical JSON SHA-256: `b366c51fd3933e25d0554c4406e6fb5fc71b3ffcfd8bc4503ff1ae39d97b9e61`
- verification receipt SHA-256: `45cd8b7c8ceaf16244dd1746750061b2a7e74906bef07f0baf9cb6bec258f5ae`
- generator SHA-256: `8bf7e3ca2eb908011f3be2dc797b0d0a77ce3bc580de06bdb6acc8cb04dff10e`
- verifier SHA-256: `76deef0bb80fed8cb73bf1adb2d4ec741cb2dcd3783c198d02c2d7d468091fc4`
- fiber-null audit SHA-256: `b1434d31b63099c4de013041d43705d6ea1a4d159067bf1cd24771b5d7b989ad`
- materialized-baseline audit SHA-256: `a8d59709ce788ddff5ab5b8a714bf31bb86d8c7362846a16c27ad6c66617dc7f`

The verifier reports `verified`, three instances, nine factor-base instances, 216 router rows, 8,952 independently checked returned witnesses, and zero routing rows.

## Instances

| bits | p | q | B | rho average |
|---:|---:|---:|---:|---:|
| 10 | 991 | 1051 | 10 | 72 |
| 12 | 4051 | 4057 | 12 | 228 |
| 14 | 16267 | 16433 | 16 | 992 |

All curves have prime order, cofactor one, trace outside `{0,1}`, and `j` outside `{0,1728}`. Field selection did not use `p-1` smoothness.

## Functional result

Every tested router preserved the exact `D2+D2` support, returned verified witnesses on all scheduled supported D4 and D5 targets, and recovered all scheduled private toy challenge scalars through randomized descent. The hidden-scalar interval control exhibited narrower addition routes and remained ineligible.

This validates the route representation and witness path. Factor-base logs came from a private exhaustive toy audit standing in for the previously verified relation solver; relation collection was not rerun here.

## Initial signal and repaired null

Against a random hash of the full `(x,y)` point encoding, the x-only routers appeared to reduce route payload and candidate reads:

| router | joint 20% rows / 36 |
|---|---:|
| `x_mod` | 7 |
| `x_interval` | 5 |
| `legendre_vector` | 6 |
| `xy_linear_mod` | 0 |

That comparison was not symmetry-matched. The first three routers satisfy `h(P)=h(-P)`, while the full-point null usually separates the pair.

The repaired audit used eight deterministic public random x-fiber hashes at `r in {16,32}`. Across 54 comparisons it produced zero joint 20% rows. Median-null payload ratios tightened to:

- `x_mod`: `0.861..1.051`;
- `x_interval`: `0.943..1.096`;
- `legendre_vector`: `0.906..1.071`.

Some individual read ratios remain below `0.8`, but none combines that with a 20% payload gain on both D4 and D5. The v1 signal is therefore assigned `REVISE`, not promoted.

## Baselines

The materialized-D4 audit executes the same supported targets. Coarse routers reduce payload as low as `0.046x` materialized D4, but require `126x..12,910x` as many online group operations. No public router improves both advice and online work.

Equal-advice fixed-base BSGS is stronger still:

- sampled candidate/BSGS online ratios: `1,457x..203,334x` where the BSGS denominator is nonzero;
- three candidate advice budgets let BSGS store the entire toy group and use zero giant steps;
- candidate randomized-descent work is `12.6x..495x` the measured no-preprocessing rho average.

No router passes the preregistered gate.

## Scoped conclusion

The following candidate is rejected for promotion under this development boundary:

> Store D2 points and a ternary relation over one unary point feature, then recover D4 witnesses by scanning all route-compatible D2 bucket members.

The direct small-homomorphic-quotient port is separately blocked by the restricted theorem in `theory.md`. These results do not reject nonlinear multi-state circuits, source-tagged recursion, heavy-light witness decompositions, or batch sharing.

## Next experiment

Specify `EXP-ECDLP-SOURCE-TAG-JOIN-001`. Replace unary semantic labels with compositional D2 source states derived from factor-base fiber parameters and canonical pair witnesses. Match every candidate against random source-tag permutations preserving sign symmetry, bucket occupancy, and witness multiplicity. Require an equal-advice materialized-D4 and BSGS win before restoring relation collection.
