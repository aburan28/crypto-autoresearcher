# Development result v1: outer-aware coordinate translator

## Status

- `NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`: reject promotion of the
  explicit source-root-product translator and configured source maps. It beats
  neither target workspace nor exact `D2+D3` online work, and no family passes
  the pre-registered continuation gate.
- `OBSERVATION`: every registered coordinate/root/identity/witness invariant
  passes on the sampled schedules, and translator advice is smaller than
  symmetry-compressed D3 in 88 of 96 evaluated target rows.
- `OBSERVATION`: D2-major batch inversion has a deterministic inversion/read
  tradeoff on exact-cardinality batches. Timing remains unattested, so this is
  not a practical timing claim.
- `NONCANONICAL`: generated 8/10/12-bit curves, two seeds, `p mod 4 = 3`. No
  canonical flag was used and `promotion_rows` is empty.

This is not a negative result for implicit product trees, modular composition,
recursive addition-law circuits, other coordinate predicates, a real shared
batch evaluator, point decomposition generally, index calculus, or ECDLP.

## Evidence

- clean source commit:
  `da4eba5a7e4d4ec574cd2a0d93f61149e6b5aaca`;
- raw JSON SHA-256:
  `8556a9e430a25ffe97b06b5508a76186784804b417ca175e05736c2332fa67f0`;
- byte-preserving gzip SHA-256:
  `63929f64b70927dff9ca31b7c39242064fc05a50be2d8c0e363cea263aec4400`;
- run-manifest SHA-256:
  `09511cbd5d78fdb01ea6a6cc52f66bed8fa4a7a5d0974551bbd68b4f6f6fe851`;
- verifier-receipt SHA-256:
  `53871d36b169c1fea2954acf1a394a557512105edfe1640448c3e80cdf1f7211`;
- analysis-program SHA-256:
  `04716c133644b393991e7e00cc3b88311e536d9a9019d22dc334d1f9a3787b42`;
- analysis-output SHA-256:
  `7c0c747aee61ab2ad1261442ac8e56cbe99d45c8c23096a3bc4ea46e74b83455`.

The wrapper reports `VERIFIED_DEVELOPMENT_RUN`, clean Git state, stable source
hashes, empty child stderr, 96.88 seconds overall, and a process-level child
high-water RSS of 1,286,520,832 bytes. RSS is not phase-isolated and does not
enter a continuation gate.

The independent receipt verifies six curves, 36 family instances, 336 factor
points, 1,536 D2 points, 5,215 D3 points, and 33,584 translator witnesses. All
24 translator family-instances are functional. There are zero continuation
rows, zero continuation families, and zero promotion rows.

## Instances

| bits | seed | p | q | B | embedding degree |
|---:|---:|---:|---:|---:|---:|
| 8 | 3317584535 | 251 | 227 | 6 | 226 |
| 8 | 2246822507 | 239 | 223 | 6 | 37 |
| 10 | 3317584535 | 991 | 1,009 | 10 | 504 |
| 10 | 2246822507 | 983 | 1,009 | 10 | 1,008 |
| 12 | 3317584535 | 4,079 | 4,099 | 12 | 1,366 |
| 12 | 2246822507 | 3,931 | 3,853 | 12 | 642 |

All fields are distinct. Every group has prime order and cofactor one; traces,
`j` invariants, and embedding degrees pass the frozen exclusions. This remains
a restricted generated-toy schedule, not a random-curve asymptotic sample.

## Compiler result

Ratios below compare target rows with the symmetry-compressed full-D3 logical
baseline and scalar exact `D2+D3`. Online means exclude rows whose exact online
weighted cost is zero; those ratios are undefined and fail closed.

| family | advice ratio | workspace ratio | online-50 numeric min / mean / max | online passes |
|---|---:|---:|---:|---:|
| x_interval | 0.486-0.708 | 12.09-21.05 | 10.37 / 207.54 / 958.85 | 0/24 |
| square_map | 0.488-0.720 | 12.50-22.04 | 10.12 / 292.09 / 1,121.93 | 0/24 |
| rational_union | 0.493-0.913 | 6.61-22.03 | 11.32 / 328.02 / 1,212.16 | 0/24 |
| random_x | 0.486-0.754 | 12.07-22.19 | 9.68 / 278.15 / 2,222.94 | 0/24 |

No target passes workspace, online, or preprocessing-amortization gates. Of 96
target rows, 82 weight-50 ratios are defined and 14 zero-denominator ratios fail
closed. Advice
alone passes 24/24 rows for `x_interval`, `square_map`, and `random_x`, and 16/24
for `rational_union`; advice compression does not compensate for explicit live
polynomial state or evaluation work.

The eligible `x_interval` versus `random_x` same-map comparison has weight-50
ratios `0.916-1.102` and density ratios `1.000-1.003`. Support is never worse,
but no row reaches the required `0.8` ratio. Square and Mobius families remain
map-confounded diagnostics and cannot satisfy the coordinate-specific null gate.

## Trend result

All slopes are exploratory log-log fits over six toy instances.

| family | online slopes, weights 10-100 | D3 advice slope | density slope | explicit-H slope | trend gate |
|---|---:|---:|---:|---:|---:|
| x_interval | 0.892-0.937 | 0.791 | +0.00382 | 0.530 | fail |
| square_map | 0.871-0.919 | 0.785 | +0.00283 | 0.530 | fail |
| rational_union | 0.843-0.888 | 0.895 | +0.00181 | 0.484 | fail |
| random_x | 0.872-0.921 | 0.814 | +0.00104 | 0.485 | fail |

Combined-G maximum-degree slope is `0.243` for every family; term-count slopes
are `0.459-0.462`. Degree, term-count, and explicit-H slopes are below D3
materialization for every family. `rational_union` also has online-operation
slopes below its D3 slope, but its absolute online ratios are still at least
`11.32x`, its density slope is positive, and it lacks a same-map randomized
null. These are representation diagnostics, not continuation evidence.

## Batch result

| scale | exact rows | deterministic operation passes | mean inversion ratio | mean D2-read ratio | mean multiplication ratio |
|---|---:|---:|---:|---:|---:|
| B | 144 | 142 | 0.328 | 0.274 | 1.672 |
| 16B | 124 | 124 | 0.0238 | 0.0212 | 1.976 |

Twenty additional `16B` rows were support-clamped and correctly excluded from
signals. Eighteen family/kind/scale groups pass the conjunctive deterministic
operation/read gate. No group passes a practical timing gate because timing is
unattested. This is a constant-factor inversion/bandwidth tradeoff, not a lower
complement-test exponent.

## Scoped conclusion

Reject this exact candidate for promotion:

> Materialize accepted source-root products into `G_Q`, evaluate a complete D2
> root product into explicit `H_Q mod M2`, extract roots, and recover witnesses.

The finite-coordinate logic is exact, but the representation densifies into a
large simultaneously live polynomial state and performs far more online field
work than exact `D2+D3`. The eligible identity-map coordinate predicate behaves
like its matched random-x control. More tuning of the same explicit root-product
loop is therefore a weak next bet.

## Next positive question

The useful unresolved question moves before `G_Q`/`H_Q` materialization:

> Do recursive S3 transition states on actual elliptic-coordinate factor bases
> admit a target-independent, composable quotient with fewer than `0.8|D2_x|`
> classes and exact signed witness lifting, or do those state sets expand like
> the same-map random control?

This directly tests the compressed recursive-circuit and structured-group
barrier lead. A positive result supplies an implicit compiler primitive; a
negative result yields coordinate-specific expansion evidence rather than
another solver-tuning failure.

### Next concrete action

Write, but do not execute,
`EXP-ECDLP-RECURSIVE-S3-QUOTIENT-001/contract.md`. Its minimal barrier test must
recover exact compatibility roots and signed witnesses without materializing
any `Theta(|D2_x|)` target-specific coefficient vector, under the same advice,
workspace, online-work, and identity-map or map-matched randomized controls.
