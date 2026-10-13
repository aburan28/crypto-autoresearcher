# Audited m=51 conductor-271 volcano collision-walk record

Date: 2026-10-13

Status: **valid for the frozen scoped inference.** The sealed analyzer accepted
all 400 jobs and all 25,600 verified planted-key solve records. All five
held-out A/A gates passed. This is a bounded source-operation experiment, not
a transfer experiment or a curve-security result.

## Outcome

The primary same-action comparison was
`floor-tau17 / crater-tau17 = +0.005763` walk-operation bit, with fixed-sample
95% CI `[-0.032170, +0.043374]`. The interval includes zero and is wholly
inside the predeclared `+/-0.10`-bit practical-equivalence band. The permitted
conclusion is therefore narrow: **no same-action sampled-level/model
association larger than 0.10 collision-work bit was resolved for this
implementation, subgroup, and exact sampled models.** It is not an estimate
of a causal conductor effect.

The ordinary-rho control was
`floor-neg / crater-neg = -0.019008` bit. Its pointwise 95% CI
`[-0.055582, +0.018144]` and Bonferroni 98.75% family interval
`[-0.065653, +0.028718]` both include zero. The four action-order comparisons
were compatible with their frozen random-map predictions: every predicted
value lies inside its applicable family interval. Compatibility is not proof
of that model.

The tested prime conductor step is real structural metadata: `f_E` changes
from 1 to 271. Here `f_pi=271*120871`, but this run covers only the
degree-271 / `f_E=271` slice. The factor-120871 descent and the bottom level
were neither constructed nor measured. These results did not resolve a
same-action walk-count difference at the frozen precision, but they do not
identify conductor as a causal variable, establish conductor-independence,
or price a degree-271 transfer.

![Measured crater/floor contrasts, per-orbit primary points, and held-out A/A
controls.](volcano_level_contrasts.png)

Figure source: [`plot_publication.py`](plot_publication.py); vector rendering:
[`volcano_level_contrasts.svg`](volcano_level_contrasts.svg). Panel A shows
fixed-exact-sample intervals: 95% for the primary and diagnostic, and
Bonferroni 98.75% for the four-member secondary family. Panel B points are
descriptive and have no frozen multiplicity-adjusted intervals. Panel C shows
fixed-exact-sample Bonferroni 99% A/A intervals. The hierarchical
orbit-resampling intervals are sensitivities and are not drawn. The separate
footer band fixes the x-label/footer overlap in the frozen presentation plot.

## Question and evidence status

| Requested distinction | Evidence in this run | Status |
|---|---|---|
| Same action at both levels | `floor-tau17 / crater-tau17` | complete for the exact sample |
| Ordinary-rho level control | `floor-neg / crater-neg` | complete for the exact sample |
| Symmetry/action-order controls | three secondary quotient contrasts plus one diagnostic | complete at the `walk_ops` level |
| Floor-orbit coverage | one fixed representative from all 16 size-17 Frobenius orbits | complete |
| Randomisation/harness drift | five held-out independent-walk A/A contrasts | all frozen gates pass |
| Explicit vertical map and dual | not exercised | not assessed |
| Fully charged endpoint-to-endpoint or endpoint-to-crater cost | not measured | not assessed |
| Larger-subgroup or NIST scaling | no scaling ladder in this study | not assessed |
| Weak-curve claim | forbidden by the protocol and unsupported by these data | not assessed |

## Exact objects and workload

The frozen objects and design are in [`PROTOCOL.md`](PROTOCOL.md),
[`spec.json`](spec.json), and [`sample.csv`](sample.csv). Work is over

`GF(2)[z] / (z^51 + z^6 + z^3 + z + 1)`

on `E_b: y^2 + x*y = x^3 + b`. The common ambient order is
`2,251,799,852,369,764`; the tested prime subgroup has order
`r=17,192,986,687` (`log2(r)=34.001101...`) and cofactor `130,972`. The
Frobenius data are

`Delta_pi = -7*(271*120871)^2`, `D_K=-7`, and `f_pi=32,756,041`.

Only the crater and the `f_E=271` slice were constructed for this run. It did
not construct or measure the separate factor-120871 descent or the bottom
`f_E=f_pi` level, so it is not a measurement of the complete conductor gap.

| sampled level | model inventory | `f_E` | `[End(E):Z[pi]] = f_pi/f_E` | native tested actions |
|---|---:|---:|---:|---|
| crater, `b=1` | 1 | 1 | 32,756,041 | negation, `tau`, `tau^17` |
| conductor-271 floor | 272 curves in 16 size-17 orbits; 16 fixed representatives tested | 271 | 120,871 | negation, `tau^17` |

`tau` and `tau^17` are inseparable endomorphism actions, not separable
volcano edges. Every sampled floor coefficient is in `GF(2^17)`, and the
crater is defined over `GF(2)`. The order-`r` line therefore has the same
degree-3 trace-zero context at both levels; it is not a discovered floor
advantage. The algebraic background and still-open transfer obligations are
recorded in [`TRACE_ZERO_LANE.md`](TRACE_ZERO_LANE.md).

The 4,096 A-stream target blocks pair one planted scalar across all five arms.
Within each floor orbit, offsets `64..255` supply 192 inferential blocks, for
3,072 total. Disjoint offsets `0..63` supply 64 A/A blocks per orbit, or 1,024
total. A separate B walk stream repeats those five held-out arms. Thus the
sealed workload contains `20,480` A-stream plus `5,120` B-stream records:
25,600 verified solves.

## Frozen contrasts

Displayed values are rounded to six decimals; the source decimal strings are
preserved in [`contrast_summary.csv`](contrast_summary.csv) and
[`analysis.json`](analysis.json). The estimand is always
`log2(arithmetic mean numerator walk_ops / arithmetic mean denominator
walk_ops)`, not a mean of per-target ratios.

### Primary same-action and ordinary-rho level controls

| contrast | numerator mean | denominator mean | observed bits | fixed-sample interval | hierarchical sensitivity |
|---|---:|---:|---:|---:|---:|
| primary `floor-tau17 / crater-tau17` | 69,896.649414 | 69,618.020508 | +0.005763 | 95% `[-0.032170, +0.043374]` | 95% `[-0.045718, +0.059596]` |
| secondary `floor-neg / crater-neg` | 121,282.560872 | 122,891.046875 | -0.019008 | Bonferroni 98.75% `[-0.065653, +0.028718]` | Bonferroni 98.75% `[-0.084160, +0.045691]` |

For the same-negation row, the pointwise 95% interval is
`[-0.055582, +0.018144]`. The primary fixed-sample interval retains all 16
sampled orbits exactly once; the hierarchical interval instead models an
orbit superpopulation and is a sensitivity only. Both fixed-sample intervals
include zero; the primary 95% interval is wholly inside `+/-0.10` bit.

### Symmetry/action-order controls

| ratio | observed bits | frozen prediction | residual | applicable family interval for observed | applicable interval for residual |
|---|---:|---:|---:|---:|---:|
| `floor-tau17 / crater-tau51` | +2.030601 | +2.043731 | -0.013131 | 98.75% `[+1.982463, +2.078609]` | `[-0.061269, +0.034878]` |
| `floor-tau17 / floor-neg` | -0.795077 | -0.792481 | -0.002596 | 98.75% `[-0.841369, -0.748567]` | `[-0.048888, +0.043914]` |
| `crater-tau51 / crater-neg` | -2.844685 | -2.836213 | -0.008473 | 98.75% `[-2.891296, -2.797127]` | `[-0.055083, +0.039086]` |
| diagnostic `crater-tau17 / crater-neg` | -0.819847 | -0.792481 | -0.027366 | 95% `[-0.857563, -0.781709]` | `[-0.065082, +0.010772]` |

The corresponding hierarchical sensitivity family intervals for the observed
effects are, in row order,
`[+1.971980, +2.089549]`, `[-0.851518, -0.738876]`,
`[-2.912367, -2.776217]`, and `[-0.881503, -0.757131]`. The action-order
rows deliberately change the signed action. They measure implementation-level
symmetry effects, not level effects or transported actions.

## Held-out A/A controls

All five primary A/A intervals lie inside the frozen `+/-0.15`-bit gate, so
the inferential labels were released. These gates use the fixed 16-orbit exact
sample. The hierarchical intervals are sensitivity analyses, not gate
criteria; the `crater-tau51` upper bound and `floor-tau17` lower bound extend
slightly beyond `+/-0.15`.

| arm | A mean | B mean | B/A bits | fixed-sample Bonferroni 99% CI | hierarchical 99% sensitivity | gate |
|---|---:|---:|---:|---:|---:|---|
| `crater-neg` | 119,542.652344 | 120,775.493164 | +0.014802 | `[-0.074259, +0.104131]` | `[-0.096957, +0.130364]` | pass |
| `crater-tau51` | 16,815.760742 | 17,245.871094 | +0.036437 | `[-0.048191, +0.122118]` | `[-0.083065, +0.150374]` | pass |
| `crater-tau17` | 69,256.466797 | 69,675.470703 | +0.008702 | `[-0.074166, +0.092426]` | `[-0.105748, +0.125577]` | pass |
| `floor-neg` | 120,694.543945 | 119,283.780273 | -0.016963 | `[-0.104524, +0.070310]` | `[-0.147229, +0.108921]` | pass |
| `floor-tau17` | 70,057.581055 | 67,559.016602 | -0.052393 | `[-0.136468, +0.030002]` | `[-0.164949, +0.058201]` | pass |

## Per-orbit observations

Each point below uses the 192 inferential blocks attached to the named fixed
floor representative. These are descriptive/exploratory points: the frozen
protocol supplies no per-orbit confidence intervals or multiplicity
adjustment.

| orbit | exact `b` | primary `floor-tau17 / crater-tau17` bits |
|---:|---:|---:|
| 1 | 623162416261 | +0.1507931966 |
| 2 | 25640824825979 | -0.0252056902 |
| 3 | 30885819784827 | -0.0263654466 |
| 4 | 57318330399736 | +0.0106200590 |
| 5 | 67694307705004 | -0.0405102320 |
| 6 | 72881269935803 | +0.1655014433 |
| 7 | 115635957935040 | -0.0637974688 |
| 8 | 116461223646592 | +0.0213458470 |
| 9 | 116511665573478 | -0.0377513252 |
| 10 | 121360481466206 | -0.0197344347 |
| 11 | 130246110195364 | -0.0041532025 |
| 12 | 147686731444433 | +0.1054013366 |
| 13 | 213718369432541 | -0.1157022526 |
| 14 | 237711860122495 | +0.0352762381 |
| 15 | 360860333097189 | -0.0928367359 |
| 16 | 370376419722289 | +0.0417179550 |

The exact ranges for all six contrasts are:

| contrast | minimum (orbit, `b`) | maximum (orbit, `b`) |
|---|---:|---:|
| primary `floor-tau17 / crater-tau17` | -0.115702 (13, 213718369432541) | +0.165501 (6, 72881269935803) |
| `floor-neg / crater-neg` | -0.171881 (15, 360860333097189) | +0.105389 (13, 213718369432541) |
| `floor-tau17 / crater-tau51` | +1.941811 (3, 30885819784827) | +2.125624 (6, 72881269935803) |
| `floor-tau17 / floor-neg` | -0.877937 (10, 121360481466206) | -0.708363 (5, 67694307705004) |
| `crater-tau51 / crater-neg` | -2.950169 (10, 121360481466206) | -2.716883 (13, 213718369432541) |
| diagnostic `crater-tau17 / crater-neg` | -0.996209 (1, 623162416261) | -0.594998 (13, 213718369432541) |

All 96 exact orbit-by-contrast rows, their means, predictions, and residuals
are preserved in [`orbit_summary.csv`](orbit_summary.csv); all 80
orbit-by-arm distribution rows are in
[`orbit_arm_summary.csv`](orbit_arm_summary.csv).

## Operation accounting

The primary metric, `walk_ops`, counts online group additions and doublings
from collision-search start through successful and abandoned walks, including
look-ahead work, starts, and cycle escapes. Every record has 162 separately
counted target-dependent setup operations: 34 doublings plus 128 additions.
`mean total ops = mean walk_ops + 162` exactly. Quantiles are across the 3,072
inferential records per arm.

| arm | mean walk ops | SD | q05 | median | q95 | mean total ops |
|---|---:|---:|---:|---:|---:|---:|
| `crater-neg` | 122,891.046875 | 63,931.153002 | 30,241.850000 | 115,439.500000 | 237,425.550000 | 123,053.046875 |
| `crater-tau51` | 17,107.424479 | 8,863.338054 | 4,633.650000 | 15,960.000000 | 33,126.800000 | 17,269.424479 |
| `crater-tau17` | 69,618.020508 | 36,571.426218 | 17,258.700000 | 64,689.000000 | 137,298.600000 | 69,780.020508 |
| `floor-neg` | 121,282.560872 | 62,787.958935 | 34,153.700000 | 112,891.000000 | 232,938.400000 | 121,444.560872 |
| `floor-tau17` | 69,896.649414 | 35,887.774600 | 18,779.100000 | 65,973.000000 | 135,324.000000 | 70,058.649414 |

Canonicalisation primitives are recorded, not silently treated as free. No
field-primitive weights were frozen, so they are not converted to
group-addition equivalents.

| arm | mean canonicalisations | mean x-squares | mean y-squares | mean sign tests | mean negations |
|---|---:|---:|---:|---:|---:|
| `crater-neg` | 119,196.759115 | 0 | 0 | 119,196.759115 | 59,600.025065 |
| `crater-tau51` | 16,593.013021 | 829,650.651042 | 414,769.905924 | 16,593.013021 | 8,294.725586 |
| `crater-tau17` | 67,524.067057 | 2,295,818.279948 | 1,147,894.264974 | 67,524.067057 | 33,762.790039 |
| `floor-neg` | 117,635.792969 | 0 | 0 | 117,635.792969 | 58,823.859375 |
| `floor-tau17` | 67,794.073568 | 2,304,998.501302 | 1,152,477.198242 | 67,794.073568 | 33,900.784505 |

| arm | mean walk starts | mean cycles | mean useless collisions | mean seconds (descriptive) |
|---|---:|---:|---:|---:|
| `crater-neg` | 3,694.287760 | 2.107747 | 0.024089 | 0.088924 |
| `crater-tau51` | 514.411458 | 0.003906 | 0 | 0.026773 |
| `crater-tau17` | 2,093.953451 | 0.186523 | 0.004883 | 0.088962 |
| `floor-neg` | 3,646.767904 | 2.078451 | 0.020508 | 0.087755 |
| `floor-tau17` | 2,102.575846 | 0.182943 | 0.006510 | 0.089213 |

Mean abandoned walks were zero in every arm. Seconds are descriptive because
the host was not claimed to be isolated. Full distributions and fixed- and
hierarchical-sample mean intervals are in
[`arm_summary.csv`](arm_summary.csv).

The accounting interval excludes one-time generator/`Ust` construction and
certificates, planted-target construction, final recovery multiplication and
certificate verification, and weights for canonicaliser field primitives.
Consequently neither `walk_ops` nor total counted group operations is a fully
charged end-to-end attack cost.

## Statistical method

The frozen analyzer used 50,000 paired percentile-bootstrap draws with root
seed `202610135106`.

- The governing exact-sample bootstrap retains each of the 16 sampled orbit
  strata once and resamples the 192 paired inferential blocks within each.
- The separately reported hierarchical sensitivity resamples orbit strata and
  then paired blocks. It targets a modeled orbit superpopulation, not the
  exact sampled-orbit census.
- Primary and diagnostic intervals are pointwise 95%. The four secondary
  rows use Bonferroni 98.75% marginal intervals for 95% family coverage.
- The five A/A gates use disjoint held-out data and Bonferroni 99% marginal
  intervals for 95% family coverage.
- The primary equivalence decision requires its complete 95% interval to lie
  inside `+/-0.10` bit. Containing zero and establishing equivalence are
  separate questions.

The one chosen crater, fixed floor representatives, generator construction,
hash behavior, and implementation are bundled with level. Pairing reduces
target noise; it does not randomize conductor or identify a causal conductor
effect.

## Integrity and provenance

The run started at `2026-10-13T07:49:46.351340+00:00` and finished at
`2026-10-13T07:58:34.011824+00:00`; the 400-job interval was
`521.079691130999` seconds. Four workers were pinned to cores 0--3 on an AMD
EPYC 9V74. The clean producer revision before and after the frozen snapshot was
`929ccbcfce51d2652ecc5f647f15660a988c9aba`. The compiler was GCC 14.2.0.
The exact invocation, host record, receipts, raw outputs, and seal are inside
[`run1.tar.zst`](run1.tar.zst); replay instructions and independent audit
notes are in [`ARCHIVE.md`](ARCHIVE.md).

| artifact | SHA-256 |
|---|---|
| frozen-input commitment `FROZEN.sha256` | `149a9028aeda673dd833fb699543b9c7f6d7ed59dff17e5f1d18d96a505508d9` |
| complete archive `run1.tar.zst` | `eaad213c09f70c4c3cc330af20286328e51ab079545abaf5b80feba1b0027505` |
| sealed-tree `MANIFEST.sha256` inside archive | `1318653f04d8c1a8b79d6cd646d0f1a410fe78c5e13c9db2d1700006b7a04d1d` |
| normalized raw records inside archive | `0f3099774d4530538763723a735e2244586ab40bfb8589dda9c32cc6413705f8` |
| solver binary inside archive | `4db25d2113bc39cce71e24b317b4c3ded69a7e177a23f86c4dbb2277bafdb3e0` |
| `analysis.json` | `9087c623b85ab0da7dc483deb7d3153eeae1ded8f87c5283b912d36c5e7feee6` |
| `arm_summary.csv` | `1dfd292827c456e1ddbefeddd13b69cdaabbfe98705cd85d86aa1daae573470b` |
| `contrast_summary.csv` | `4bae750a075b408c02d942fd81e65b176926f34cd53d78dd119d4ee10066ba96` |
| `orbit_summary.csv` | `e1c29093a1e8523badb901c45698d52844b58538297038066ae0738ed555df51` |
| `orbit_arm_summary.csv` | `3aed1593abea428fc4dba87d02f25c78c0d343ceae34a28821a2d29f62c344e6` |
| `aa_summary.csv` | `3bcd30cf1178edb8ab04ef21a93d5a2389f7b2b40d0b1adc494a35edeb646d29` |
| publication plot source `plot_publication.py` | `6de756bc56e57db179cf3ab5379b7bce51b9b88c0e411cef3d941db365cff388` |
| publication SVG | `246c602e3666042243563da36a8fee5e47acfd9f27cfc440071523cd42b41252` |
| publication PNG | `e85d7fe220173f316227af6b0bb3dbbd1d5a0e4b2dd882ed0946a60297db2ea7` |

The archive holds 400 raw files, 400 job receipts, 35 self-test certificates,
and a 424-entry file seal. The analyzer independently rechecked the frozen
commitment, exact file sets, plan, commands, receipt bindings, raw rows,
counter identities, scalars, stream namespaces, orbit assignment, binary,
session, and complete seal before issuing
`VALID_FOR_SCOPED_INFERENCE`.

## Reproduce without changing the evidence record

From the repository root, extract to a new empty directory, verify the sealed
tree, and direct reanalysis to a separate new output directory:

```sh
study_dir=research/isogeny_volcano_m51_rho_20261013
replay_root=/tmp/isogeny-volcano-m51-rho-replay
replay_out=/tmp/isogeny-volcano-m51-analysis-replay
test ! -e "$replay_root"
test ! -e "$replay_out"
mkdir "$replay_root"
tar --zstd -xf "$study_dir/run1.tar.zst" -C "$replay_root"
(cd "$replay_root" && sha256sum --strict -c MANIFEST.sha256)
python3 "$study_dir/analyze.py" \
  --run-root "$replay_root" \
  --output-dir "$replay_out"
MPLCONFIGDIR=/tmp/m51-volcano-replay-mpl \
  python3 "$study_dir/plot_publication.py" \
  --input-dir "$replay_out" \
  --output-prefix /tmp/m51-volcano-replay
```

Build a byte-reproducible landscape PDF with the installed Pandoc/pdfTeX
toolchain. The trailer ID is derived from the report source rather than time:

```sh
report_source=research/isogeny_volcano_m51_rho_20261013/README.md
report_sha256=$(sha256sum "$report_source" | awk '{print $1}')
report_id=${report_sha256:0:32}
SOURCE_DATE_EPOCH=1791849600 \
FORCE_SOURCE_DATE=1 \
pandoc "$report_source" \
  --from=gfm --standalone --pdf-engine=pdflatex \
  --resource-path=research/isogeny_volcano_m51_rho_20261013 \
  -V documentclass=extarticle -V fontsize=8pt \
  -V geometry:landscape -V geometry:margin=0.45in -V colorlinks=true \
  -V "header-includes=\\pdftrailerid{<${report_id}><${report_id}>}" \
  -o research/isogeny_volcano_m51_rho_20261013/report.pdf
```

## Claim boundary

This record supports only bounded statements about collision-walk operation
counts for this prime subgroup, implementation, exact crater, fixed set of 16
floor representatives, generator construction, hash behavior, and accounting
interval. It does **not** establish:

- a causal effect of the conductor or the degree-271 vertical edge;
- an explicit isogeny/dual, subgroup-preserving DLP transfer, or recovery path;
- fully priced canonicalisation, map evaluation, one-time transfer, or
  end-to-end attack cost;
- scaling to larger subgroups or any NIST P-, B-, K-, or sect113r1 curve;
- a security-bit reduction or a weak curve.

The next transfer claim would require explicit maps and duals, subgroup and
scalar-recovery certificates, and complete cold-start and amortised cost
against the best same-subgroup control. These data do not substitute for any
of those gates.
