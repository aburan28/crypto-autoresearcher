# AP-3 independent `2E` membership validation and binary-twist admission

**Date:** 2026-10-16 local / 2026-10-17 UTC. **Status:** implementation validation and a proof-scoped protocol obstruction. This report records observations and a mathematical implication; it makes no factor-base speed, relation-yield, or ECDLP cost claim. The [diagram](2026-10-16-icperf-ap3-membership.svg), its [editable source](2026-10-16-icperf-ap3-membership-chart.py), and the [PDF](2026-10-16-icperf-ap3-membership.pdf) accompany this report.

## Question and method

The frozen [EXP-ICPERF-42ef30 protocol](../../experiments/EXP-ICPERF-42ef30/specification.yaml) (internal provenance) requires AP-3: decide membership in `2E` without using `Tr(x_P)+Tr(a)` and cross-check at least 10,000 points per curve. For `#E=2r` with `r` odd, finite abelian group structure gives `P∈2E` exactly when `[r]P=O`. The implementation uses that scalar multiplication as its independent path, then evaluates `Tr(x_P+a)` in a separate function for the comparison. This is independent at the predicate level; both paths still use Sage field and curve arithmetic.

The [code](../../experiments/EXP-ICPERF-42ef30/code/independent_2e.py) (internal provenance) scanned polynomial-basis `x` values upward, sorted each pair of lifted `y` roots by encoded value, and checked the first 10,000 distinct affine points on each curve. Three are the shipped `a=b=1` curves at n=15,17,19. Two further curves used `a=1` and seeded nonzero `b` draws at n=17 and n=19; all draw attempts and AR-3 outcomes are in the [manifest](../../experiments/EXP-ICPERF-42ef30/tests/ap3_validation_20261016_v2/manifest.json) (internal provenance). The source SHA-256 is `05b0a6c3bebb82f5b356d114a2b52ffd3aeef32983c017ffaf1933388bbd4072`; the run records Git head `9551744186e0c6b6e9d8b91a580afb1567fbcf85`, Sage 10.10.rc0, Python 3.14.3, dirty-tree state, exact arguments, and seed 20260916.

The exact invocation was:

```sh
sage -sh -c 'env DOT_SAGE=/private/tmp/icperf-sage TMPDIR=/private/tmp python experiments/EXP-ICPERF-42ef30/code/independent_2e.py --samples-per-curve 10000 --additional-seed 20260916 --out-dir experiments/EXP-ICPERF-42ef30/tests/ap3_validation_20261016_v2'
```

The [successor summary](../../experiments/EXP-ICPERF-42ef30/tests/ap3_validation_20261016_v2/summary.json) and [execution-log receipt](../../experiments/EXP-ICPERF-42ef30/tests/ap3_validation_20261016_v2/execution_log_receipt.json) (internal provenance) hash the per-curve files, manifest, stdout, and stderr. The first check is retained separately in `ap3_validation_20261016/`; the successor adds CPU, peak-RSS and load observations. The Sage wrapper printed a path-permission warning, while the inner validation exited zero and wrote all five rows.

## Observations

| Curve `(n,a,b)` | Measured `#E` | First 10,000 points in `2E` by `[r]P` | Predicate disagreements | Validation CPU seconds |
| --- | ---: | ---: | ---: | ---: |
| `(15,1,1)` | 32,494 | 5,046 | 0 | 6.463 |
| `(17,1,1)` | 131,174 | 5,025 | 0 | 8.235 |
| `(19,1,1)` | 525,086 | 5,005 | 0 | 10.201 |
| `(17,1,107553)` | 130,974 | 4,949 | 0 | 7.940 |
| `(19,1,38918)` | 524,794 | 5,049 | 0 | 10.706 |

**Measured total:** 50,000 distinct points, zero disagreements. Per-curve wall times were 9.305, 12.204, 11.248, 10.288, and 15.170 seconds; the process peak RSS recorded in each row was 278,134,784 bytes. These times describe this correctness check on a shared host and are not an IC performance comparison. The near-half shares in the diagram describe deterministic prefixes, not random-sample estimates or confidence intervals. Every row retains a digest of the ordered points and both predicate values; any disagreement would have been listed with its exact `(x,y)` coordinates.

## Twist admission conflict

The same protocol asks C-TWIST to compare a quadratic twist on the selected slice, but AR-3 admits only `#E=2r` with `r` odd. This cannot hold for both members of a binary quadratic-twist pair. For `x≠0`, setting `z=y/x` gives `z²+z=x+a+b/x²`. Flipping the absolute trace of `a` switches whether that equation has two roots, so the two curves together have two affine points for each nonzero `x`, plus one point at `x=0` and the point at infinity on each curve. Thus `#E + #E′ = 2(q+1)`. For even `q`, an admitted `#E≡2 (mod 4)` forces `#E′≡0 (mod 4)`. This is a deduction from the curve equations; the recorded n=15,17,19 counts `(32494,33044)`, `(131174,130972)`, and `(525086,523492)` independently check those instances. The [Magma handbook](https://magma.maths.usyd.edu.au/magma/handbook/text/1557) (retrieved provenance) also describes opposite Frobenius traces for quadratic twists.

The [named problem](../../problems/binary-twist-cofactor-stage1-conflict.md) (internal provenance) states two checkable correction routes: extend the landing/count model to cofactor-four twists with independent validation, or retain AR-3 and replace the nearby-object prediction while recording the twist refusal. Only the Coordinator can change the frozen protocol. The `2E` test here is scoped to admitted cofactor-two curves; it does not supply the missing `2E/4E` criterion for the twist.

## Next checks and graph custody

AP-3's sampled cross-check is implemented on five admitted curves. AP-1's exact enumerator has no code tree or independently accepted table in the current checkout, and the twist control needs a committed correction before Stage 1 can be approved. Selected n=15/17/19 affine slices still need the per-cell WDSat admission and the full relation, rank, target and matched-rho costs. None of the 50–63-bit prime/Koblitz/ordinary-binary `m=2..8` end-to-end grid is established by this validation.

The canonical ECDLP frontier graphs were checked conceptually and left unchanged: this record adds an instrument check and a protocol obstruction, with no reviewed attack-cost or performance result to graph as a frontier edge. The diagram here remains a scoped derived view of the linked files.
