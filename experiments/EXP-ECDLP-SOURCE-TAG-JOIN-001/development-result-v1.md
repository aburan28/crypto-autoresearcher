# Development result v1: source-tagged recursive join

## Status

- `NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`: none of the tested
  selected-witness source tags produced a robust matched-null signal or useful
  fixed-curve compiler.
- `OBSERVATION`: every supported D4/D5 witness and every configured toy descent
  was correct.
- `REVISE`: small-null movement, shared-payload accounting, and route saturation
  narrow which structural gate failures can be interpreted.
- `NONCANONICAL`: one seed at 10, 12, and 14 bits. No canonical command or
  approval flag was used.

This is not a negative result for provenance generally, all-witness states,
outer-aware routing, batching, rational-map decomposition, or prime-field ECDLP.

## Evidence

- raw JSON SHA-256:
  `880d466fd5f032ae28b677664f8713950b074a87ecad3d3a079144a24e6d7fa2`;
- byte-preserving gzip SHA-256:
  `b2b274c2a64258eb0c5af00bd4eedc99319521cd461c7f9fa8e6cec4c95b9f31`;
- canonical document SHA-256:
  `7e5b417829e12a689db903eefc7ebf28e0a6724221bfaeeb9195b494a10364c3`;
- generator SHA-256:
  `9b7137ffc2fffbca05e639c9ea2e44870baa686adfc2713a80834af2a0cc59e8`;
- verifier SHA-256:
  `552bcb1c9669b9eaf7aae38942e0ca4b6305b1a73da00d768afa43b8bcf21faf`.
- verification receipt SHA-256:
  `d938cad2a704e748e1f59d41cde4736297671979b9e9f786fa9b8dd1e44031b1`;
- analysis program SHA-256:
  `0241d6a38ecd144d872ac688bb44a47d0deb2734ef1461745d0d619d6d602c95`;
- analysis output SHA-256:
  `159bdc00318f295a702ea9e97998f29eb8347a6d0127fb223360b4428ee9f924`.

The independent verifier reports `verified`: three curves, 15 factor-base
instances, 2,520 route rows, 2,160 matched nulls, and 39,475 exact factor
witnesses. Top-level promoted routing and compiler arrays are empty, as required
for a one-seed development sweep.

## Instances

| bits | p | q | B | one-trial rho operations |
|---:|---:|---:|---:|---:|
| 10 | 991 | 1,009 | 10 | 37 |
| 12 | 4,079 | 4,099 | 12 | 755 |
| 14 | 15,527 | 15,629 | 16 | 521 |

All curves have prime order, cofactor one, trace outside `{0,1}`, and `j` outside
`{0,1728}`. The rho column is one noisy arithmetic-scale trial, not a fitted
baseline.

## Functional result

All 270 candidate rows passed exact curve/support/witness replay, null
invariants, scalar separation, and the configured randomized descent. This
validates the source-record representation, both null constructors, streaming
route compiler, outer-read accounting, and full witness recovery.

Factor-base logarithms came from the private exhaustive toy audit retained from
the verified predecessor. Relation collection, matrix construction, rank, and
sparse linear algebra were not rerun and cannot be inferred from descent
correctness.

## Structural result

No candidate passed the structural gate. The table takes, independently at each
size, the best candidate's worst ratio across all eight matched nulls. Different
columns may select different candidates.

| bits | supported D4 ops | supported D5 ops | random D5 ops | total payload |
|---:|---:|---:|---:|---:|
| 10 | 0.820 | 0.981 | 0.966 | 0.986 |
| 12 | 0.904 | 0.969 | 0.986 | 0.994 |
| 14 | 0.984 | 0.989 | 0.992 | 0.989 |

The isolated D4 ordering effect weakens toward one with size and disappears
after the unchanged D5 outer scan. The best identity that stayed unsaturated at
all sizes was the `random_scalar` negative control, with D4 ratios
`1.020, 0.990, 1.004`. No fixed public coordinate identity shows a persistent
advantage.

Four exploratory supported-D5 slopes fell below `0.5`; all four were
`random_scalar` controls, and their matched null slopes occupied the same range.
Those three-point slopes are diagnostics, not exponent evidence.

## Compiler result

No candidate passed any mandatory exact-D2, partial-D4, or decomposition-envelope
comparison. Even the cheapest candidate at each size had the following ratios:

| bits | query `S*T^2` / exact D2 | D5 ops / partial D4 | D5 ops / full D4 | descent ops / rho |
|---:|---:|---:|---:|---:|
| 10 | 1,819 | 16.3 | 104 | 6.24 |
| 12 | 11,605 | 34.9 | 831 | 5.60 |
| 14 | 34,882 | 101.1 | 4,947 | 84.7 |

The minima may come from different rows. The worsening exact-D2, partial-D4,
and full-D4 ratios corroborate the restricted same-outer-schedule theorem: this
inner router still scans every factor and then performs nonnegative inner work.
The measurements do not extend that theorem to outer routing, batches, or other
cost models.

## Interpretation repairs

1. **Null movement.** At 10 bits, two source-null permutations moved only
   `2/5` fibers. Zero of the 90 candidate rows met both movement and saturation
   prerequisites. At 12 and 14 bits, 62 and 42 rows did. The 10-bit gate count is
   therefore not a candidate rejection; its per-metric ratios remain descriptive.
2. **Shared payload.** Candidate and null total advice both contain the same
   factor/D2 scaffold. For tag count four, even deleting every candidate route
   leaves a worst-null total-payload lower bound of `0.939..0.977`; those 90 rows
   could not meet a `0.8` total-payload gate. A successor must gate incremental
   route information structurally and retain total advice only for compiler
   comparisons.
3. **Saturation.** Route-universe saturation rose from 21/90 to 28/90 to 48/90.
   Fixed small tag alphabets increasingly erase route geometry.
4. **BSGS sampling.** One toy BSGS challenge required zero online additions in
   54 ten-bit and 24 fourteen-bit rows. That makes some average-envelope ratios
   undefined. Exact-D2, partial-D4, full-D4, BSGS worst-case, and rho negatives
   remain independently available.
5. **Statistics.** Worst-of-eight-null thresholds are conservative promotion
   rules, not calibrated significance tests. The valid statement is no robust
   20% gain, not statistical indistinguishability.

## Scoped conclusion

Reject this exact candidate for promotion:

> Bind one selected factor-pair provenance to each semantic D2 point, route the
> D2+D2 inverse join by a small source tag, and retain the same D5 outer scan.

The experiment mostly relabeled nearly injective factor-pair sums. It did not
test nontrivial source-aligned additive collisions, all-witness relational states,
an outer-factor predicate, or shared work across targets.

## Next experiments

1. **Exact outer `2+3` floor.** Build exact D2 and D3 dictionaries, query D5 as
   `D2 + D3`, and measure full/partial advice plus batches `K in {1,B,16B}`.
   This is generic MITM with heuristic space `q^(3/5)` and time `q^(2/5)`, not an
   ECDLP exponent claim; it is the mandatory outer-aware comparator.
2. **Source-domain resultant census.** Substitute actual `x=phi_b(t)` source
   maps into the Semaev/addition-law correspondence and eliminate the outer
   factor algebraically. Stop if degree, coefficient count, or template storage
   approaches full D3.
3. **Bounded-source solver preflight.** Only if planted controls and the degree
   census survive, test pair-symmetric small-root/hybrid solving of all five
   source parameters. Require exact leaves and signs, not x-only roots.

Any successor must resample ineffective nulls, scale its state alphabet away
from saturation, replicate one identity on at least two seeds, and report
offline field operations, advice bytes, memory traffic, online work, supported
targets, success probability, rank, linear algebra, and individual descent.
