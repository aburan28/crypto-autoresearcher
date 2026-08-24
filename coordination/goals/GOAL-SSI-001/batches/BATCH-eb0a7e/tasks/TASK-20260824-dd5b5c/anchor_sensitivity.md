# Anchor sensitivity — TASK-20260824-dd5b5c

## Scope

This is a comparison of two committed numerical anchors under one corrected
charging formula. It is not a security conclusion and does not choose an
anchor for any official record. The machine-readable source is
`recomputed_table.json`; it contains 240 rows, 120 for each anchor, over the
complete frozen grid.

The anchor ambiguity was already recorded in the committed closeout:
`coordination/goals/GOAL-SSI-001/batches/BATCH-5a3d0a/closeout.md:40-55`
reports the fitted-`opt` P=512 crossover as 81.6 and the `PAPER_PAIRS`
crossover as 77.7, with opposite `w=2^80` signs. The same closeout says that
row was not citation-eligible at `:56-68`. This artifact preserves that
boundary.

## Anchor definitions

| Anchor | Committed source | `(log2T_full, log2M)` values in field-size order 256, 384, 512, 576, 768 |
|---|---|---|
| `fitted_opt` | `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:per_field[*].optimal` | `(108.73088958800618, 93.27781828665178)`; `(157.87439031817553, 137.48765358816084)`; `(206.1038967394178, 181.43583267427067)`; `(229.98121023958595, 203.30702177853001)`; `(300.93543569782855, 268.68673590177326)` |
| `PAPER_PAIRS` | `experiments/EXP-WESOVOW-001/cost_model.py:60-65` | `(106.5, 92.5)`; `(157.5, 138.6)`; `(204.2, 181.3)`; `(230.9, 206.0)`; `(302.4, 272.2)` |

The corrected law used for every row is:

`log2T(w) = log2T_full_anchor + c*sqrt(log2p) + 0.5*max(0, log2M_anchor-log2w)`.

The Delfs–Galbraith comparison value in the table is the committed baseline
`log2T_DG = log2p/2`, matching
`experiments/EXP-WESOVOW-001/cost_model.py:237` and the raw-result formula at
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:14`.

## Corrected crossover sensitivity

The following values are the table's corrected uncapped crossover
`log2(w*)`, with one column for each overhead scenario. `within M` records
whether the corresponding crossover is at or below that anchor's
`log2M`; it is a property of this cost-model calculation only.

| Anchor | log2p | c=0.0 | c=0.5 | c=1.0 | c=2.0 | within M for c=(0,.5,1,2) |
|---|---:|---:|---:|---:|---:|:---|
| fitted_opt | 256 | 54.739597462664 | 70.739597462664 | 86.739597462664 | 118.739597462664 | Y,Y,Y,N |
| fitted_opt | 384 | 69.236434224512 | 88.832352166777 | 108.428270109043 | 147.620105993574 | Y,Y,Y,N |
| fitted_opt | 512 | 81.643626153106 | 104.271043151076 | 126.898460149045 | 172.153294144984 | Y,Y,Y,Y |
| fitted_opt | 576 | 87.269442257702 | 111.269442257702 | 135.269442257702 | 183.269442257702 | Y,Y,Y,Y |
| fitted_opt | 768 | 102.557607297430 | 130.270420218532 | 157.983233139634 | 213.408858981839 | Y,Y,Y,Y |
| PAPER_PAIRS | 256 | 49.500000000000 | 65.500000000000 | 81.500000000000 | 113.500000000000 | Y,Y,Y,N |
| PAPER_PAIRS | 384 | 69.600000000000 | 89.195917942265 | 108.791835884531 | 147.983671769062 | Y,Y,Y,N |
| PAPER_PAIRS | 512 | 77.700000000000 | 100.327416997970 | 122.954833995939 | 168.209667991878 | Y,Y,Y,Y |
| PAPER_PAIRS | 576 | 91.800000000000 | 115.800000000000 | 139.800000000000 | 187.800000000000 | Y,Y,Y,Y |
| PAPER_PAIRS | 768 | 109.000000000000 | 136.712812921102 | 164.425625842204 | 219.851251684408 | Y,Y,Y,Y |

The values are generated from the table's formula, equivalently

`log2(w*) = log2M_anchor - 2*(log2p/2 - log2T_full_anchor - c*sqrt(log2p))`.

No anchor is silently substituted for the other.

## Selected full-grid sign sensitivity

The next two tables expose the corrected table's arithmetic at the two ends
of the declared memory grid. Each entry is `log2T_DG-log2T_corrected`; a
positive value means the corrected model's vOW row is numerically below the
baseline in this model, and a negative value means it is numerically above.

At `log2w=30`, all declared overhead scenarios are negative for both anchors:

| Anchor | log2p | c=0.0 | c=0.5 | c=1.0 | c=2.0 |
|---|---:|---:|---:|---:|---:|
| fitted_opt | 256 | -12.369798731332 | -20.369798731332 | -28.369798731332 | -44.369798731332 |
| fitted_opt | 384 | -19.618217112256 | -29.416176083389 | -39.214135054521 | -58.810052996787 |
| fitted_opt | 512 | -25.821813076553 | -37.135521575538 | -48.449230074523 | -71.076647072492 |
| fitted_opt | 576 | -28.634721128851 | -40.634721128851 | -52.634721128851 | -76.634721128851 |
| fitted_opt | 768 | -36.278803648715 | -50.135210109266 | -63.991616569817 | -91.704429490919 |
| PAPER_PAIRS | 256 | -9.750000000000 | -17.750000000000 | -25.750000000000 | -41.750000000000 |
| PAPER_PAIRS | 384 | -19.800000000000 | -29.597958971133 | -39.395917942265 | -58.991835884531 |
| PAPER_PAIRS | 512 | -23.850000000000 | -35.163708498985 | -46.477416997969 | -69.104833995939 |
| PAPER_PAIRS | 576 | -30.900000000000 | -42.900000000000 | -54.900000000000 | -78.900000000000 |
| PAPER_PAIRS | 768 | -39.500000000000 | -53.356406460551 | -67.212812921102 | -94.925625842204 |

At `log2w=80`, the same arithmetic is:

| Anchor | log2p | c=0.0 | c=0.5 | c=1.0 | c=2.0 |
|---|---:|---:|---:|---:|---:|
| fitted_opt | 256 | 12.630201268668 | 4.630201268668 | -3.369798731332 | -19.369798731332 |
| fitted_opt | 384 | 5.381782887744 | -4.416176083389 | -14.214135054521 | -33.810052996787 |
| fitted_opt | 512 | -0.821813076553 | -12.135521575538 | -23.449230074523 | -46.076647072492 |
| fitted_opt | 576 | -3.634721128851 | -15.634721128851 | -27.634721128851 | -51.634721128851 |
| fitted_opt | 768 | -11.278803648715 | -25.135210109266 | -38.991616569817 | -66.704429490919 |
| PAPER_PAIRS | 256 | 15.250000000000 | 7.250000000000 | -0.750000000000 | -16.750000000000 |
| PAPER_PAIRS | 384 | 5.200000000000 | -4.597958971133 | -14.395917942265 | -33.991835884531 |
| PAPER_PAIRS | 512 | 1.150000000000 | -10.163708498985 | -21.477416997969 | -44.104833995939 |
| PAPER_PAIRS | 576 | -5.900000000000 | -17.900000000000 | -29.900000000000 | -53.900000000000 |
| PAPER_PAIRS | 768 | -14.500000000000 | -28.356406460551 | -42.212812921102 | -69.925625842204 |

These rows show the anchor-dependent arithmetic explicitly. In particular,
the fitted and paper anchors differ in both the P=512 crossover value and the
sign at `log2w=80,c=0`; this is the already-recorded ambiguity, not a basis
for lifting its citation boundary.

## Boundary and non-interpretation

The P=512 boundary is preserved verbatim:

> The `P=512` crossover value and its `w=2^80` sign are **NOT citation-eligible**. This task does not lift that prohibition. Only a committed Coordinator decision on independently reviewed evidence can lift it.

The table is a corrected cost-model comparison on committed literals. It does
not establish a SQIsign, CSIDH, standardized-parameter, security, attack,
certificate, or asymptotic-complexity conclusion.
