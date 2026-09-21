# R0 — regeneration of the ladder, fits, band, NULL-3, F5 and iteration-count tables from the raw records

Red Team, TASK-20260904-3a2ff5. Scripts `r0_regenerate.py`, `r0_controls.py`,
`r0r1_fits.py`; outputs `r0_regenerated_ladder.json`, `r0_controls.json`,
`r0r1_fits.json`. Only `experiments/EXP-PFDR-cbdefb/runs/*/raw-result.json` was read as
input; `analysis.md`, `analysis.json` and `execution-report.yaml` were read only to diff
against. No package file was modified.

## Diffs

| regenerated object | comparison | differences |
|---|---|---|
| ladder table, 15 cells x 5 arms = 75 rows x 17 fields (n, degenerate, d_ff and d_lf histograms after the count-1 rule, d_lf uncensored, raw closure pairs, right_censored, no_fall_in_window, single_fall, count-1 entries, saturated count-1 entries, min iteration count, closure = graded d_ff, certificate routes, engines, cross-checked, cross-check agreement) | `analysis.json ladder.table` | **0** |
| d_lf primary fit s = 2..5, per draw | `analysis.json fits.d_lf_primary` / analysis.md section D | slope 0.4000, CI [0.38202515, 0.41797485], residual variance 0.05021, n = 480 -- **identical** |
| per-prime fits (n = 160) | analysis.md section D | [0.36858, 0.43142] -- **identical** |
| null band table (offsets, uncensored counts, censored, no-fall), 30 rows | `analysis.json controls.null_band` | **0** |
| F5 controlled-null flags | `analysis.json controls.F5_same_pair_at_every_cell` | **0** (null1 false, null2 false, noncurve TRUE) |
| falls with iteration count 1, per cell and arm | `analysis.json controls.falls_with_iteration_count_1` | **0** |
| NULL-3 minus Semaev, d_ff and d_lf | analysis.md section F | **0** (difference 0 at s = 3, 4, 5; undefined at s = 2 where NULL-3 is a single monomial) |
| Semaev censored draws in any fit | -- | **0 of 600**; every s = 5 Semaev draw is certified (route C1+C2) |

## Independent reconstruction of the object (not merely of the arithmetic)

`ptm_objects.py` rebuilds S~ = S_3(ell_1, ell_2, x_R) from the formula in the review plan
with the meter's ring arithmetic (no producer code in the construction) for the declared
instance p = 4099, a = 3245, b = 455, x_R = 1960, and measures it with the frozen
closure at D_max = 7:

  s = 2 -> (d_ff, d_lf) = (5, 5); s = 3 -> (5, 5); s = 4 -> (6, 6), all certified,
  single fall.

These match the package cell values and P3's frozen prediction. (This is an
independent-construction cross-check by the Red Team, not the blinded re-derivation,
which belongs to the sibling task.)

## The count-1 rule

Contract invalidation rule 3 says "a claimed fall with closure iteration count 1
invalidates that fall entry". Regenerating the rule from the raw histories:

- count-1 fall entries occur at s = 1 ONLY, on every arm that has a root: 120 Semaev,
  120 non-curve, 165 of 600 NULL-1. `count1_only_at_s1 = True`; the per-cell counts
  match `analysis.json` exactly.
- no fall at any s >= 2 on any arm at any cell has iteration count 1.
- The rule was applied to fall ENTRIES (not whole systems) exactly as written, with raw
  values shown beside the rule-applied ones, and the s = 1 level is outside the primary
  fit by the pre-declared range. The secondary fit s = 1..5 is therefore numerically
  identical to the primary (n = 480 in both) -- as reported.

What the tell actually detects is in `proves-too-much-table.md` (object 4): at s = 1 the
count-1 condition is a perfect detector of "this system has a solution", not of a
non-iterating closure.

RESULT FOR R0: HOLDS. Every table entry, slope, interval and label regenerates from the
raw records with zero differences, no censored draw entered a fit, and the count-1 rule
was applied as the contract states and only at s = 1.
