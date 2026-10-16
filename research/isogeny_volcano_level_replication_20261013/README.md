# Independent measurement at each isogeny-volcano level

Date: 2026-10-13

Status: **complete exploratory observation.** The protocol and workload were
frozen before the fresh run. The sealed analyzer accepted all 392 jobs and all
160,000 planted-key certificates.

This is an exploratory additive replication. It is not ledger evidence, a
sealed measured bound, an isogeny-transfer result, an end-to-end ECDLP speedup,
or a weak-curve verdict.

## Requested question and evidence status

- **Each sampled level:** equal-curve-weighted native negation-only counts at
  all four nodes for `m=37` and `m=41`; **verified complete**.
- **Large conductor factors:** four conditional vertical-edge contrasts and
  one factor interaction per lattice; **verified complete**.
- **Symmetry separation:** lower-level versus crater negation is primary;
  native level versus crater signed-`tau` is secondary context; **verified
  complete at the operation-count level**.
- **Uncertainty:** 50,000-replicate hierarchical bootstrap with pointwise and
  simultaneous intervals; **verified complete**.
- **Weakness:** explicit maps, subgroup preservation, recovery, and fully
  priced end-to-end costs are **not tested by this study**.

## Outcome

All six lower-level versus crater-negation point estimates were between
`-0.008978` and `+0.016988` operation-count bits. Every pointwise and
simultaneous 95% interval contained zero. The three `m=37` simultaneous 90%
ratio intervals were inside the frozen `[0.97, 1.03]` equivalence band. None
of the three `m=41` intervals was contained in that band because the intervals
were wider, so the predeclared **global equivalence result is false**. That is
an inconclusive precision outcome at `m=41`, not evidence of a level effect.

Every conditional conductor-factor edge and both factor interactions also had
a pointwise 95% interval containing zero. The fresh data therefore resolve no
large-prime-factor difference at the tested precision, but do not establish a
general conductor-independence law.

The native crater signed-`tau` context arm used 2.478--2.496 fewer counted-work
bits than the native `m=37` arms and 2.683--2.702 fewer bits than the native
`m=41` arms. This is a same-class action comparison, not a transported action,
fully priced speedup, or weak-representative result.

![Fresh per-level operation-count contrasts. Filled circles and intervals are
the fresh run; hollow diamonds are archived pilot points and are not
pooled.](volcano-level-differences.png)

Figure source: [`plot.py`](plot.py); vector rendering:
[`volcano-level-differences.svg`](volcano-level-differences.svg). The left
panels show simultaneous 95% error bars for the six-member Bonferroni family
against the shaded +/-3% band. The frozen equivalence decision instead uses
the simultaneous 90% intervals reported in the primary table below. The right
panels are native Frobenius-action context only.

## Objects and conductor gaps

The sampled nodes form conductor-factor lattices, not linear volcanoes. Write
`Z[pi] = O_(f_pi) subseteq End(E) = O_(f_E) subseteq O_K`. The final column is
the remaining index `[End(E):Z[pi]] = f_pi/f_E`; neither `f_E` nor this index is
an ECDLP-bit discount.

| study | node | `f_E` | `f_pi/f_E` | sampled curves | fresh negation-only solves |
|---|---|---:|---:|---:|---:|
| `m37` | crater | 1 | 194,399 | 1 | 5,000 |
| `m37` | floor73 | 73 | 2,663 | 74 | 74,000 |
| `m37` | floor2663 | 2,663 | 73 | 22 | 22,000 |
| `m37` | bottom | 194,399 | 1 | 30 | 30,000 |
| `m41` | crater | 1 | 703,889 | 1 | 3,000 |
| `m41` | floor409 | 409 | 1,721 | 30 | 6,000 |
| `m41` | floor1721 | 1,721 | 409 | 30 | 6,000 |
| `m41` | bottom | 703,889 | 1 | 30 | 6,000 |

The crater also has a separate signed-Frobenius context arm: 5,000 fresh
solves at `m=37` and 3,000 at `m=41`. Total frozen workload: 160,000 solves.

## Fresh results

Displayed ratios, bit effects, and interval endpoints are rounded to six
decimal places from `results.json` and `contrasts.csv`; those machine-readable
files retain the analyzer's full precision.

### Same-action level comparison: native negation only

This is the primary comparison. A ratio above one means that the named lower
node used more counted group operations than the crater under the same native
negation-only action. The six contrasts are one multiplicity family.

| study | lower node / crater-neg | ratio of mean ops | `log2` ratio (bits) | simultaneous 95% CI (bits) | simultaneous 90% ratio CI | inside frozen +/-3% band? |
|---|---|---:|---:|---:|---:|---|
| `m37` | floor73 | 1.002024 | +0.002917 | [-0.027519, +0.034966] | [0.982683, 1.022510] | yes |
| `m37` | floor2663 | 1.005998 | +0.008627 | [-0.027028, +0.045977] | [0.983446, 1.029838] | yes |
| `m37` | bottom | 0.993796 | -0.008978 | [-0.042598, +0.026042] | [0.973006, 1.015798] | yes |
| `m41` | floor409 | 0.999009 | -0.001430 | [-0.064901, +0.060353] | [0.959649, 1.039025] | no |
| `m41` | floor1721 | 1.011845 | +0.016988 | [-0.045113, +0.078181] | [0.972599, 1.051627] | no |
| `m41` | bottom | 1.010235 | +0.014691 | [-0.048873, +0.077866] | [0.970339, 1.051116] | no |

Global simultaneous equivalence within `[0.97, 1.03]`: **false**. All three
`m37` contrasts pass the frozen rule; all three `m41` contrasts fail it on
interval width. All six simultaneous 95% intervals include zero.

Removing the exact common target-dependent setup term changes none of the
pointwise conclusions:

| study | lower node / crater-neg | ex-setup ratio | ex-setup effect bits (pointwise 95% CI) |
|---|---|---:|---:|
| `m37` | floor73 | 1.002046 | +0.002949 [-0.020710, +0.026881] |
| `m37` | floor2663 | 1.006064 | +0.008722 [-0.018646, +0.036193] |
| `m37` | bottom | 0.993728 | -0.009077 [-0.034852, +0.016882] |
| `m41` | floor409 | 0.999009 | -0.001430 [-0.049474, +0.044967] |
| `m41` | floor1721 | 1.011847 | +0.016992 [-0.030108, +0.062563] |
| `m41` | bottom | 1.010237 | +0.014694 [-0.033223, +0.062030] |

### Per-level distributions and diagnostics

Means are equal-curve-weighted. Quantiles are across solves. Local-cap
restarts, cycles, useless collisions, and descriptive timing remain in
`level-summary.csv` rather than being collapsed into a single claim.

| study | arm | curves | verified solves | mean ops | CV | median | q05--q95 | mean / `sqrt(r)` | between-curve SD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `m37` | crater-neg | 1 | 5,000 | 14,169.384 | 0.514915 | 13,438.5 | 3,720.75--27,507.15 | 0.933079 | 0* |
| `m37` | floor73 | 74 | 74,000 | 14,198.065 | 0.515446 | 13,357.0 | 3,797.00--27,468.00 | 0.934968 | 210.769 |
| `m37` | floor2663 | 22 | 22,000 | 14,254.370 | 0.517279 | 13,358.5 | 3,779.00--27,707.00 | 0.938675 | 265.823 |
| `m37` | bottom | 30 | 30,000 | 14,081.484 | 0.515192 | 13,259.5 | 3,740.00--27,188.05 | 0.927290 | 232.380 |
| `m37` | crater-tau | 1 | 5,000 | 2,526.806 | 0.477009 | 2,393.5 | 818.95--4,683.60 | 0.166395 | 0* |
| `m41` | crater-neg | 1 | 3,000 | 679,711.961 | 0.520689 | 643,740.0 | 174,979.85--1,314,890.30 | 0.916726 | 0* |
| `m41` | floor409 | 30 | 6,000 | 679,038.566 | 0.520734 | 638,614.5 | 179,390.35--1,319,431.15 | 0.915818 | 26,628.454 |
| `m41` | floor1721 | 30 | 6,000 | 687,762.852 | 0.523548 | 645,044.0 | 174,911.30--1,333,054.75 | 0.927585 | 25,148.441 |
| `m41` | bottom | 30 | 6,000 | 686,668.633 | 0.529098 | 645,431.0 | 174,657.45--1,353,669.10 | 0.926109 | 27,556.208 |
| `m41` | crater-tau | 1 | 3,000 | 105,717.736 | 0.524878 | 99,427.5 | 25,925.20--206,454.85 | 0.142581 | 0* |

`*` The between-curve SD is zero by construction for a one-curve arm.

The remaining frozen diagnostics are below. Timing is `L0` descriptive only;
it is not a performance bound. Cycle, local-restart, and useless-collision
rates are per 1,000 walk starts.

| study | arm | mean walk starts | cycles / 1k | local restarts / 1k | useless / 1k | mean sec / solve | aggregate ns / counted op |
|---|---|---:|---:|---:|---:|---:|---:|
| `m37` | crater-neg | 421.601800 | 0.601990 | 0 | 0.000949 | 0.007142646 | 504.090 |
| `m37` | floor73 | 422.360216 | 0.593640 | 0.000032 | 0.001056 | 0.007207290 | 507.625 |
| `m37` | floor2663 | 423.894727 | 0.580333 | 0 | 0.001287 | 0.007336559 | 514.688 |
| `m37` | bottom | 418.818133 | 0.605434 | 0 | 0.001433 | 0.007129208 | 506.282 |
| `m37` | crater-tau | 71.452400 | 0.316294 | 0 | 0 | 0.002517758 | 996.420 |
| `m41` | crater-neg | 20,433.160000 | 0.532925 | 0 | 0.038565 | 0.375741313 | 552.795 |
| `m41` | floor409 | 20,414.360167 | 0.538714 | 0 | 0.038282 | 0.377169809 | 555.447 |
| `m41` | floor1721 | 20,675.288333 | 0.545506 | 0 | 0.040378 | 0.376377932 | 547.250 |
| `m41` | bottom | 20,643.024500 | 0.536452 | 0 | 0.039360 | 0.375495268 | 546.836 |
| `m41` | crater-tau | 3,177.196333 | 0.003252 | 0 | 0.007449 | 0.121365455 | 1,148.014 |

### Does the large prime conductor factor differ?

The direct measurements are the conditional vertical edges. Each factor is
added once with the other factor absent and once with it present. The
interaction is

`log2(mu_bottom) - log2(mu_factor1) - log2(mu_factor2) + log2(mu_crater)`.

| study | factor | exact comparison | ratio | effect (bits) | pointwise 95% CI (bits) |
|---|---:|---|---:|---:|---:|
| `m37` | 73 | floor73 / crater | 1.002024 | +0.002917 | [-0.020485, +0.026585] |
| `m37` | 73 | bottom / floor2663 | 0.987871 | -0.017605 | [-0.038453, +0.003022] |
| `m37` | 2,663 | floor2663 / crater | 1.005998 | +0.008627 | [-0.018443, +0.035801] |
| `m37` | 2,663 | bottom / floor73 | 0.991789 | -0.011895 | [-0.027377, +0.003650] |
| `m37` | 73 x 2,663 | bottom x crater / (floor73 x floor2663) | 0.985876 | -0.020522 | [-0.052015, +0.010702] |
| `m41` | 409 | floor409 / crater | 0.999009 | -0.001430 | [-0.049462, +0.044956] |
| `m41` | 409 | bottom / floor1721 | 0.998409 | -0.002297 | [-0.040039, +0.036423] |
| `m41` | 1,721 | floor1721 / crater | 1.011845 | +0.016988 | [-0.030100, +0.062547] |
| `m41` | 1,721 | bottom / floor409 | 1.011237 | +0.016121 | [-0.022858, +0.055663] |
| `m41` | 409 x 1,721 | bottom x crater / (floor409 x floor1721) | 0.999399 | -0.000867 | [-0.060528, +0.061079] |

Every interval in this table contains zero. Thus no factor edge or interaction
was resolved as nonzero at pointwise 95% confidence. These contrasts answer
only whether native negation-only counts differ at the tested lattice edges.
Two lattices, non-random curve samples, and independent targets do not identify
a causal conductor-size law, establish monotonicity, or support extrapolation
to the conductor factors of a named NIST curve.

### Symmetry/action context: native level versus crater signed-`tau`

This secondary contrast intentionally answers a different question. It mixes
the ring-level change with loss of the crater's cheap native Frobenius action,
so it must not be called a conductor effect. Both total operations and the
predeclared setup-excluded sensitivity are reported.

| study | native arm / crater-tau | total ratio | total effect bits (pointwise 95% CI) | ex-setup ratio | ex-setup bits (pointwise 95% CI) |
|---|---|---:|---:|---:|---:|
| `m37` | crater-neg | 5.607627 | 2.487391 [2.454008, 2.520821] | 5.908741 | 2.562851 [2.528131, 2.597772] |
| `m37` | floor73 | 5.618978 | 2.490308 [2.463909, 2.517348] | 5.920833 | 2.565800 [2.537818, 2.594553] |
| `m37` | floor2663 | 5.641261 | 2.496018 [2.465855, 2.526040] | 5.944572 | 2.571573 [2.539883, 2.603116] |
| `m37` | bottom | 5.572840 | 2.478413 [2.449994, 2.506916] | 5.871680 | 2.553773 [2.523878, 2.583864] |
| `m41` | crater-neg | 6.429498 | 2.684706 [2.631132, 2.740854] | 6.438088 | 2.686632 [2.633020, 2.742836] |
| `m41` | floor409 | 6.423128 | 2.683276 [2.636225, 2.731547] | 6.431709 | 2.685202 [2.638105, 2.733533] |
| `m41` | floor1721 | 6.505653 | 2.701694 [2.655006, 2.748727] | 6.514363 | 2.703624 [2.656874, 2.750706] |
| `m41` | bottom | 6.495302 | 2.699397 [2.652320, 2.747287] | 6.503997 | 2.701327 [2.654196, 2.749277] |

The setup-excluded sensitivity subtracts exactly 155 operations at `m=37` and
167 at `m=41`. The `ops` counter does not price field operations used by orbit
canonicalisation, curve/generator precomputation, final verification, or any
isogeny map. These rows are therefore operation-count context, not a fully
priced speedup or transfer result.

## Archived pilot context (not pooled)

The historical point estimates below motivated the fresh replication. They
are observations from different seed namespaces and archived runs, not fresh
outcomes and not inputs to the new bootstrap.

| study | lower node | archived lower/crater-neg ratio | archived effect (bits) | fresh minus archived (bits) |
|---|---|---:|---:|---:|
| `m37` | floor73 | 0.997670 | -0.003365 | +0.006283 |
| `m37` | floor2663 | 0.992785 | -0.010446 | +0.019074 |
| `m37` | bottom | 0.994579 | -0.007843 | -0.001135 |
| `m41` | floor409 | 1.001240 | +0.001788 | -0.003218 |
| `m41` | floor1721 | 1.004482 | +0.006451 | +0.010536 |
| `m41` | bottom | 0.998343 | -0.002392 | +0.017083 |

Archived sources:

- `research/isogeny_volcano_rho_20261005/results.json`, SHA-256
  `2eb7caee726587c6d5450c81afee5275f2d39c96edef3514443e05d145e2f452`;
- `research/isogeny_volcano_rho_m41_20261006/results.json`, SHA-256
  `11c53edde3011a0ef81cbab0e7a62390cb20d1be07ed83814bba4f4219dc9235`.

## Statistical method and limitations

The primary estimand is the ratio of equal-curve-weighted mean `ops`, not the
mean of per-solve ratios. The frozen analysis uses 50,000 fixed-seed
three-stage empirical bootstrap replicates: curves, process chunks within
selected curves, and solves within selected chunks. The one-curve crater arms
resample chunks and then solves. The implementation uses exactly 4,096
fixed-seed solve-resampled means per chunk as an empirical reservoir, with a
2,000,000-cell memory cap.

Pointwise 95% intervals describe individual contrasts. Bonferroni simultaneous
95% intervals cover the frozen family of six primary level contrasts.
Bonferroni simultaneous 90% intervals implement the frozen +/-3% equivalence
rule. Equivalence inside that margin is not equality, and a confidence
interval containing one is not evidence of equivalence.

The curve samples were fixed historically, but targets are independent rather
than paired across curves because the legacy solver shares one PRNG stream for
curve setup, target generation, and walk randomness. This design can test
reproducibility and quantify node-level differences in this implementation; it
cannot causally attribute a difference to conductor alone.

## Weakness claim boundary

This study can support only statements about measured source-operation counts
on these proxy classes. It does not provide an explicit isogeny map or dual,
subgroup-preservation certificate, endpoint action, scalar recovery path,
map-evaluation cost, or complete cold-start/amortised cost. Consequently:

- a conductor gap alone is not evidence of ECDLP weakness;
- a lower operation count at one sampled node would be a lead requiring
  replication and complete pricing, not a weak-curve assertion;
- a native crater signed-`tau` advantage does not establish that the action is
  cheaply transported to a lower representative;
- a bounded null result supports only **no weakness found in scope**, never
  absence of a weak representative or transfer in general.

The labels **weak representative exists**, **source-transfer-weak**, or
**class-weak** remain unavailable unless their separate map, subgroup,
recovery, and total-cost obligations are discharged.

## Evidence and provenance

All repository paths and commit identifiers cited in this report have
provenance `internal`; no recalled or unverified external source supports a
result claim here.

Frozen at commit `f10e03e3d8b0e584d23202deb391c5e7b06026cf`.
`FROZEN.sha256` seals the protocol, specification, runner, analyzer, and plot
source. The producer worktree was clean at that commit before both binaries
were built with GCC 14.2.0 using `-O2 -march=native`. Binary SHA-256 values
were `15ae904dc8f3313b1902c57bb6acd2e7e19d12f824148f2ee74e58cac6b2fa2d`
for `m37` and
`a2c80bdc011d8e8c157b46d91c2dd9a2b768f242bfa239da49d26c1457467c76`
for `m41`.

The run began at `2026-10-13T06:10:25.597160+00:00` and completed at
`2026-10-13T06:53:06.059611+00:00` on an AMD EPYC 9V74 host, using four
workers pinned to CPUs 0--3. The runner recorded 392/392 completed jobs,
160,000/160,000 verified solves, and no error. The analyzer verified the exact
file sets and receipts, found zero duplicate rows, and accepted every planted
certificate. The `m37` raw tree contains 272 files with SHA-256
`bae5bbe0f77da5c376a43f18a9641e27bc3d95488e8f1a86bb8c62cac64075f8`;
the `m41` tree contains 120 files with SHA-256
`0096c753b7e96a5977318482c87455ee9d3166c381b46dcad9644e5f73b54226`.

| artifact | SHA-256 |
|---|---|
| `run1.tar.zst` | `37d8abf2d12d51eed53ef013f05bbf8a17028ee51c60355cf1e2f2994fa63eb7` |
| `results.json` | `cc52d06c8e04769ceed6e194abbef651f0c6cee330670452c5e98027451ea372` |
| `level-summary.csv` | `61370aff72167634f9f3c0e9e667183ecef5abc18530ad8b831f6bef96e34757` |
| `contrasts.csv` | `09e1a2b20e24efecee2906b7058f4447a5ea063992310eb662fce0c989c01681` |
| `volcano-level-differences.svg` | `6a2790432ca1f8ee30f249723e4d5031eedf94c4d02d250be58ac45339699812` |
| `volcano-level-differences.png` | `0d677b680140d6197f68f26a7a52f144236f1a6fd51dfa9fae180dec3d4a3f71` |

The plan, receipt, and session hashes recorded inside `results.json` are,
respectively,
`d54036bdcc762f8c56434755be7a786a7756fdf5ff75b9406bb77b0cb88de2f1`,
`9bbd38db211cdd496f1fc0993940a4d97d522e1e84adfdfdee57670eff726804`,
and `76947b5b4e310768534783d465dde37e3ea2cc891443dd7bcd96b70db3d9ad8e`.

[`ATTEMPTS.md`](ATTEMPTS.md) preserves the launch and archive history. A
clean-room extraction was byte-equal to the live run tree. Analysis of a
relocated extraction was intentionally rejected because absolute output paths
are part of the frozen receipts; reproducible reanalysis must recreate the
recorded run-root path. This is an archive portability limitation, not a
failed planted-key certificate.

Primary frozen sources are [`PROTOCOL.md`](PROTOCOL.md),
[`spec.json`](spec.json), [`run_replication.py`](run_replication.py),
[`analyze.py`](analyze.py), and [`plot.py`](plot.py).

## Reproduce

The frozen analyzer is path-bound. From the repository root, recreate the
recorded run root if it is not already present, then analyze and plot:

```sh
study_dir=research/isogeny_volcano_level_replication_20261013
run_root=/tmp/isogeny-volcano-level-replication-20261013-run1
if [ ! -d "$run_root" ]; then
  mkdir "$run_root"
  tar --zstd -xf "$study_dir/run1.tar.zst" -C "$run_root"
fi
python3 research/isogeny_volcano_level_replication_20261013/analyze.py \
  --run-root "$run_root" \
  --output-dir "$study_dir"
MPLCONFIGDIR=/tmp/matplotlib-volcano-level \
  python3 research/isogeny_volcano_level_replication_20261013/plot.py
```

Build a byte-reproducible PDF with the installed Pandoc 3.1.11.1 and pdfTeX
toolchain. The trailer ID is derived from the report source rather than from
wall-clock state:

```sh
report_source=research/isogeny_volcano_level_replication_20261013/README.md
report_sha256=$(sha256sum "$report_source" | awk '{print $1}')
report_id=${report_sha256:0:32}
SOURCE_DATE_EPOCH=1791849600 \
FORCE_SOURCE_DATE=1 \
pandoc "$report_source" \
  --from=gfm --standalone --pdf-engine=pdflatex \
  --resource-path=research/isogeny_volcano_level_replication_20261013 \
  -V documentclass=extarticle -V fontsize=9pt \
  -V geometry:landscape -V geometry:margin=0.55in -V colorlinks=true \
  -V "header-includes=\\pdftrailerid{<${report_id}><${report_id}>}" \
  -o research/isogeny_volcano_level_replication_20261013/report.pdf
```

Validate the rendered file and extract its text for inspection:

```sh
pdfinfo research/isogeny_volcano_level_replication_20261013/report.pdf
pdftotext -layout \
  research/isogeny_volcano_level_replication_20261013/report.pdf -
```
