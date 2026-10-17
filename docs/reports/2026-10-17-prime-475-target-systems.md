# Common target inputs for three 475-point prime factor bases

**Status, 2026-10-17 UTC:** exact public known-answer input preparation and independent Sage replay. The [compressed full record](../../research/icperf_prime_475_target_systems_20261017/systems.json.gz), SHA-256 `4bb75b65b843a4b7ce8c0b7d8521d80a95b958f061e0ddf516639296a15fb589`, contains seven target scalars and points and all coefficients and exponents of 21 arm-by-arity systems. The [independent replay](../../research/icperf_prime_475_target_systems_20261017/sage_replay.json), SHA-256 `1180fee6058e9325db1a245906b7103f743ccc351f9dd047fe6492c913ad7955`, checked all 21 systems. These are **public correctness fixtures**. There was no algebraic solve, observed degree of regularity, natural relation, useful rank, target logarithm or end-to-end timing.

## Scope and schedule

The [certified prime-order curve](../../research/icperf_prime_fixtures_20261017/n63_seed20261017.json) has `p=9223372021248595841` and `r=9223372018953067627`. The generator is the fixture's certified witness. For each `m=2…8`, the [input generator](../../tools/icperf_prime_475_target_systems.py) derives a scalar as `1 + SHA256(domain | fixture SHA-256 | m) mod (r−1)` and multiplies the fixture generator. The domain, scalar, full point and hash are serialized. This schedule depends on the curve fixture and `m`, **not** on a base, solver output or selected relation. The scalar is public, so this schedule cannot establish unknown-scalar recovery or serve as a held-out ECDLP challenge.

Each target feeds the same-curve, equal-realized-size [896-coset](2026-10-17-prime-coset-896-search.md), [random and small-x](2026-10-17-prime-475-controls.md) bases, each of size 475. For every arm, the existing prime engine's chained-`S3` encoder builds a direct system with the same separating-form seed. The coset also has its exact quadratic membership lift. The [editable chart source](2026-10-17-prime-475-target-systems-chart.py), [SVG](2026-10-17-prime-475-target-systems.svg) and [inspected PDF](2026-10-17-prime-475-target-systems.pdf) plot the exact input monomial occurrences across arities.

## Exact serialized input sizes

All direct systems have `2m−1` variables and `2m` equations. The table counts monomial occurrences across those input equations. The random and small-x product membership polynomials have 476 and 475 nonzero terms respectively. The coset predicate has two terms but includes **421 field roots with no curve lift**, which any actual solver and point checker must account for. Its direct membership degree is 896; control direct membership degree is 475. The quadratic coset lift retains quartic `S3` equations, uses `13m−1` variables and `13m` equations, and its maximum input degree is 4.

| Summands `m` | Coset direct | Coset quadratic lift | Random direct | Small-x direct |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 16 | 60 | 964 | 962 |
| 3 | 33 | 99 | 1,455 | 1,452 |
| 4 | 50 | 138 | 1,946 | 1,942 |
| 5 | 67 | 177 | 2,437 | 2,432 |
| 6 | 84 | 216 | 2,928 | 2,922 |
| 7 | 101 | 255 | 3,419 | 3,412 |
| 8 | 118 | 294 | 3,910 | 3,902 |

The arity-eight coset lift has 103 variables and 104 equations, versus 15 and 16 in each direct arm. Sparse input support does **not** bound the Gröbner solving degree, matrix density, memory, point-extraction cost or relation probability. Direct `S8` encodes seven summands and one target; an eight-summand direct elimination needs `S9`, whereas the archived eight-summand row uses chained `S3`.

## Independent check and limits

The [Sage checker](../../tools/icperf_prime_475_target_systems_sage_verify.py) regenerated all seven scalar/point pairs with Sage curve arithmetic; checked each base point and fixed-size arm; compared every direct membership equation with the frozen coefficients; independently expanded the `S3` formula for every chain equation; and verified all eleven exponent gates and terminal coset constants in every lifted system. It checked stored support totals. The first two checker launches were stopped by the installed Sage runtime's cache-write permission under the restricted sandbox; the same immutable input replayed successfully with approved access to Sage's cache. Those launches yielded no mathematical observation. Sage emitted a version-function deprecation warning on the successful replay.

The next scientifically discriminating step is a **Coordinator-approved bounded solver protocol** with identical target points, per-cell process/RSS limits, complete failure retention and independent full-point certificates. It must compare actual solving degree/time/memory and root filtering, then natural verified relation yield, deduplicated useful rank, linear algebra, a separate unseen same-point ECDLP target, all setup including rejected base draws, and matched rho. The current `msolve` engine explicitly refuses this 63-bit `p` by default and documents arithmetic failures above its 16-bit guard; merely raising its bound is not a valid experiment. The [full-width obstruction](../../problems/full-width-ic-arity-grid-unmeasured.md) remains open.

**Graph custody:** the [canonical ECDLP frontier](../../knowledge/frontiers/ecdlp/README.md) was checked. No reviewed complete-cost or attack result changed, so its graph source and rendering remain unchanged. Provenance of the numerical statements here is `internal`: linked immutable inputs and independent Sage replay.
