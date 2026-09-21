# R0 — raw/summary agreement and deficit regeneration from the raw records

TASK-20260904-0d66e3 (red team), EXP-PFDR-20ee58. Script `r0_regenerate.py`,
output `r0-regeneration.json`. The script reads only
`runs/*/raw-result.json` and the `status:` line of each `manifest.yaml`; it
imports no producer code and re-implements every table and the fit.

## What was recomputed

For all 14 runs and every draw:

- `deficit(D) = row_count - full_rank - koszul_pairwise` from each raw
  `cumulative[D]` layer record, compared with the draw's own `deficit_vector`
  and `deficit` dict;
- internal consistency of the raw record (the layer's `row_count`,
  `full_rank`, `ncols_full`, `koszul_pairwise` against the draw's `rows`,
  `rank`, `ncols`, `koszul` arrays);
- **first-principles** `rows(D)`, `ncols(D)` and `koszul(D)` from my own
  binomial formulas for the mixed ring with 3s squarefree digits and one free
  u — `#{monomials of degree ≤ t} = Σ_j C(3s, j)(t - j + 1)`, so
  `rows(D) = Σ_i #{deg ≤ D - deg f_i}`, `ncols(D) = #{deg ≤ D}`,
  `koszul(D) = #{deg ≤ D - 8}` — compared with the recorded counts;
- the per-arm deficit tables, the residual table (SEM(8) minus the median of
  the five topology-null seeds), the affine fit in exact `Fraction`
  arithmetic, the p-ladder, the curve spread, the null generator-degree
  histograms, the calibration table (both conventions), and the s = 1
  cumulative deficits;
- the headline strings of `execution-report.yaml` and `analysis.md`.

## Result

| check | outcome |
|---|---|
| runs found / status | 14 / all `completed_valid` |
| deficits recomputed from raw and equal to the recorded vectors | **870 / 870 entries** |
| distinct deficit values over the whole run set | `[0]` |
| twin draw total | **246** (matches the execution report) |
| first-principles rows / columns / koszul vs raw | all match, every draw, every D |
| `zero_product_rows` max over all draws/arms/cells | **0** |
| `deficit_series` equals `deficit_pairwise` on every draw | true |
| certificates verified on every planted draw | true; 0 failures (15 per s = 3 cell, 9 elsewhere) |
| affine fit (exact) | `alpha = 0`, `beta = 0`, `n = 72`, `rss = 0` — degenerate, zero residual variance |
| diffs against `analysis.json` (deficit tables, residuals, fit, calibration, s = 1) | **none** |
| headline strings of `execution-report.yaml` / `analysis.md` | all present as quoted |

## A5 (the analysis-script branch-rule bug)

- The raw records were **added once and never modified**:
  `git log --diff-filter=M -- 'experiments/EXP-PFDR-20ee58/runs/*/raw-result.json'`
  is empty; the whole package landed in a single commit `aaa7f5bb`. The
  specification's only later edit was the approval commit `c5742969`, which
  changed `status` / added `approval_note` and touched no prediction.
- The corrected rule is the one in the committed `analyze.py`, and it asserts
  `vec == d["deficit_vector"]` for every draw, so the shipped analysis cannot
  silently diverge from the raw layer.
- The M1 declaration follows mechanically from the raw values: every residual
  is 0 and every SEM deficit at D ∈ {5,6,7} is 0, so `all_zero` is true and the
  rule takes the M1 branch. I re-derived the same branch from the raw records
  with my own code.

## Two fidelity notes on the coded rule (no effect on this data)

1. The coded M1 test uses the **residual** `SEM(8) - median(topology(8))`, not
   `SEM(8)` itself. If the topology null had been nonzero and SEM had matched
   it, the code would declare M1 while the contract's M1 ("deficit(D) = 0 for
   all D ≤ 8 at every s, p and curve") would be false. Here the topology band is
   exactly 0, so the two coincide, and the rendered reason string does report
   the band. Worth stating so the composition does not read "M1" as literally
   "every deficit is 0" via the rule rather than via the data (it is true via
   the data — see the `[0]` row above).
2. `S_MAIN = (3, 4, 5)`, so the s = 6 cells (D ≤ 6) are outside the branch rule
   even though the contract's M1 quantifies over "every s". Their raw values are
   0, so this changes nothing, but the s = 6 cells are decoration for the branch
   declaration rather than input to it.

**R0 holds.**
