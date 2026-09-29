# R0 — raw/summary agreement and residual regeneration from the raw records

Task TASK-20260904-ed0e8f (red team), joint R0. Scope of this note: the tables
of `experiments/EXP-PFDR-5726af/analysis.md` sections B–K, regenerated from
`runs/*/raw-result.json` with `r0_regen.py` (output `r0_regenerated.json`).
Result: **holds** (no discrepancy found). Two honesty observations are recorded
at the end; neither is a discrepancy.

## Method (and why it is stronger than the joint asks)

`raw-result.json` carries BOTH a `metrics` block (the summariser's own output)
and a `raw` block (per-draw records). Regenerating from `metrics` would test
nothing, because `analysis.md` is generated from the same summariser. So:

1. `metrics` is never read. Only `raw.draws[*]`, `raw.null2_by_p_seed`,
   `raw.table`, `raw.mixed`, `raw.non_monomial` are read.
2. Even the per-object `d_ff` / `fall_dim_at_d_ff` fields inside `raw` are not
   trusted: every pair is re-derived from the per-layer rank profile as
   `fall_dim(D) = full_rank(D) - top_rank(D)`, `d_ff = min{D : fall_dim(D) > 0}`,
   and the recorded fields are then compared against the re-derivation.
3. `execution-report.yaml` and `analysis.md` are read only at the end, for the
   diff.

**Recorded-vs-derived mismatches: 0**, over 272 Semaev layers, 1490 NULL-1
layers, 240 NULL-2 layers, 36 mixed-block objects and 24 non-monomial readings.

## Diff against analysis.md

| analysis.md section | regenerated value | agrees |
|---|---|---|
| B, Semaev per cell (d_ff, fall_dim), all draws | (2,2,2) (5,4)×12; (2,2,3) (5,4)×12; (2,2,4) (6,10)×12; (2,2,5) (6,10)×12; (2,2,6) (7,28)×12; (3,2,4) (13,12)×2; (3,2,5) (13,12)×2 | yes |
| B, residuals against `stage0-predictions.yaml` | 0/0 at every cell, every draw | yes |
| B, NULL-3 identical across curves/targets/primes | one distinct (d_ff, fall_dim) pair per cell, and per prime | yes |
| C, NULL-2 by (p, seed) | (2,2,2) (5,1)×10; (2,2,3) (5,4)×10; (2,2,4) (6,10)×10; (2,2,5) (6,10)×10; (2,2,6) (7,28)×10; (3,2,4) (13,1)×5; (3,2,5) (13,12)×5 | yes |
| C, NULL-2 minus Semaev, P3 all-zero flag and counts | nonzero at 60/60 pairs at (2,2,2) with distinct difference (0, −3), at 10/10 pairs at (3,2,4) with (0, −11); zero at all other cells | yes |
| D, NULL-1 histograms, at/below D_null, censoring | {5:60}, {6:60}, {7:60}, {8:60}, {9:60}, {13:10}, {14:10}; below D_null 0; censored 0; no-fall-by-D_max 0 | yes |
| E, NULL-1 fall_dim at d_ff | (5,4), (6,14), (7,48), (8,165), (9,572), (13,12), (14,90) | yes |
| F, rank profiles of the first (p=4099, seed 1101, target 1 / p=65537 at m=3) draw | reproduced tuple-for-tuple, incl. generator terms 16, 49, 121, 256, 484, 4096, 29791 | yes |
| G, sol(D) covariate | N_sol per draw [2,2,2,2,2,2,2,2,1,1,2,2] at s=2..4; [2,6,2,…] at s=5 (the A-NSOL-6 draw); not computed at s=6 and m=3; d_solve None everywhere | yes |
| H, mixed-block | 36 objects, d_ff histogram {6:36}, fall_dim 14 | yes |
| H, non-monomial readings A and B | both (5, 4) on all 12 instances; `ell1_pow4_degree4_part_terms` = 0 on all | yes |
| I, H-WIL 112 cells | 112 cells, all at min(C(s,j),C(s,j+2)); meter and independent columns equal everywhere; 16 square-map cells | yes |
| J, gap D_null − d_ff | 0, 1, 1, 2, 2, 0, 1 | yes |
| K, criteria restatement | every restated integer matches the regeneration | yes |
| D-STOP-FIRST truncation | D_max_computed = 7 at (2,2,6) and 13 at (3,2,4), (3,2,5); full D_null+1 elsewhere | yes |

No table entry differs from the raw records; no residual the report calls 0 is
nonzero.

## Two honesty observations (not discrepancies)

**R0-OBS-1 (replication counting for NULL-2).** Section C's "nonzero entries
(count) 60" counts (draw, seed) PAIRS, not distinct null objects. Under
deviation D-NULL2-ONCE the block-factored null takes no curve or target input
and was computed once per (p, seed): **10 distinct objects at m = 2 and 5 at
m = 3**, reported 60 (resp. 10) times. Section K states this correctly at the
deciding cell ("10 distinct null objects"); table C does not annotate it. The
independent-object count for the P3 comparison is 10 per m = 2 cell, not 60.

**R0-OBS-2 (the H-WIL table's exponent).** All 112 cells are `e = 2`, i.e.
multiplication by `ell^2`. The m = 3 arms use `e = 4`, for which the raw table
contains no cell. This is a scope fact about the control, not an error in the
tables; it is taken up under R2.
