# RUN-RELN-f202be-stage4v2 -- execution report

Combined four-rung re-analysis under protocol amendment v1
(`experiments/EXP-RELN-f202be/amendments/v1.yaml`, version_to 2, approved by
`DEC-20260907-432a39`): the forced_negation_gap_trap_control tolerance
`|measured - expected| <= 0.1` (fixed) is replaced by
`|measured - expected| <= max(0.1, 3*(m/B)*(B^3/(4M)))`, `m = 3`, evaluated
per object cell from that cell's own recorded `B` and `M`.

Sources: rungs 14 and 16 from `RUN-RELN-f202be-N14v2` /
`RUN-RELN-f202be-N16v2` (full stage2/3 re-execution, same deterministic
seeds, confirmed bit-for-bit reproducible against the original
`RUN-RELN-f202be-N14`/`N16` -- see those runs' `reanalysis-provenance.json`);
rungs 18 and 20 from the EXISTING, UNEDITED `RUN-RELN-f202be-N18` /
`RUN-RELN-f202be-N20` (no re-execution). Command:
`python3 source/run_stage4_analysis_v2.py`. Wall clock: 0.69 s (pure
re-analysis over already-computed curve_results.json files; no enumeration).

## 1. Forced-negation-gap control under the amended tolerance

All 72 object cells (3 curves x 3 geometries x 2 B conventions x 4 rungs)
recomputed directly from `curve_results.json`'s own
`forced_negation_gap_measured` / `_expected` / `B` fields (not from the old
`forced_gap_within_0.1` boolean, which encodes only the frozen v1 tolerance).

| rung | B_1 (nominal) | worst B1-cell: abs / rel dev | worst B2-cell: abs / rel dev | amended tol @ worst B1 cell | amended tol @ worst B2 cell | old (0.1 abs) pass? | amended pass? |
|---|---|---|---|---|---|---|---|
| 14 | 48 | 0.1671 / 0.1184 | 0.1666 / 0.1303 | 0.2645 | 0.6395 | NO (15/18 cells fail at this rung; 23/72 total across rungs 14+16) | YES (0/18 cells fail) |
| 16 | 74 | 0.0946 / 0.0657 | 0.1089 / 0.0806 | 0.1753 | 0.4345 | partial (8/18 cells fail at this rung) | YES (0/18 cells fail) |
| 18 | 118 | 0.0531 / 0.0363 | 0.0716 / 0.0510 | 0.1116 | 0.2870 | YES (unchanged, floor binding) | YES (0/18 cells fail) |
| 20 | 186 | 0.0308 / 0.0208 | 0.0467 / 0.0325 | 0.1000 | 0.1901 | YES (unchanged, floor binding) | YES (0/18 cells fail) |

**Result: `forced_negation_gap_control_pass: true`, 0 of 72 cells fail, at
every rung.** Rungs 18 and 20 are confirmed INERT under the amendment (the
0.1 floor was already binding and satisfied there, exactly as the amendment
claimed -- verified here by direct recomputation, not assumed). Rungs 14 and
16, which failed 23 of 72 cells under the frozen v1 tolerance, now pass all
36 of their cells. `INV1_ok`/`INV2_ok` are true in all 72 recomputed cells
(zero accounting deviation everywhere), consistent with the amendment's
characterization that this was a tolerance miscalibration, not an
implementation defect.

**A wording note on the amendment's own validation table, recorded rather
than silently reconciled:** the amendment quotes a single worst-case
`(worst_abs, worst_rel)` pair per rung computed with the RUNG's nominal
design B_1 in the tolerance formula (e.g. `3*(3/48)=0.1875` at rung 14).
Recomputing from the raw per-cell data at rung 14 shows `worst_abs=0.1671`
matches a B_1-convention cell (B=48) while `worst_rel=0.1303` matches a
DIFFERENT cell, a B_2-convention cell (B=18) -- the amendment's single quoted
row silently mixes two different cells' numbers. This is recorded in
`implementation.md`'s addendum. It changes no pass/fail conclusion: applying
the amended formula per-cell using each cell's own recorded B (the literal
reading of the amendment text, and consistent with how the original 0.1
tolerance was already applied per-cell to both B-conventions) passes all 72
cells; applying it with the rung's nominal B_1 uniformly to every cell (the
reading implied by the amendment's own worked arithmetic) also passes all 72
cells, checked explicitly. Full per-cell table:
`control-verdicts.json.forced_negation_gap_all_cells`.

## 2. Rungs 18 and 20: confirmed unaffected

Recomputing the amended tolerance against the EXISTING, UNEDITED N18/N20
`curve_results.json` (no re-execution) shows 0 of 36 cells fail at either
rung, matching (and, since the floor is binding, numerically equal in
practice to) their original pass under the frozen v1 tolerance. Their Delta,
NULL-A band, and growth-fit contributions are untouched by this re-analysis
(same source files, same computation).

## 3. Combined four-rung classification

With the forced-gap control now passing at all four rungs (`complete_run_set:
true`, `all_blocking_controls_pass: true`), the frozen `success_criterion` /
`falsification_criterion` are evaluated for the first time on the full run
set:

- **All 36 object cells (12 per geometry x 3 geometries) are inside the
  NULL-A band (mean +/- 3 SD) at every rung on every curve**
  (`all_object_cells_in_null_a_band: true`) -- the Delta-band-inclusion half
  of the pre-committed NULL outcome holds.
- **Growth-fit slopes of `log(max(Delta - Delta_null_mean, SD_null))` vs
  `log(N)` over the four rungs, per geometry (bootstrap 95% CI, 2000
  resamples):**
  - x_interval_low: slope -0.480, CI [-0.631, -0.344] -- excludes 0 (negative)
  - x_interval_mid: slope -0.452, CI [-0.697, -0.216] -- excludes 0 (negative)
  - qr_class: slope -0.483, CI [-0.527, -0.392] -- excludes 0 (negative)

  None contains 0 (`growth_slope_contains_zero_all_geometries: false`).
- **Predicate lifts (Holm-corrected, analytic INV-3 null, 7-predicate family,
  alpha 0.05):** max Holm-corrected |z| exceeds the rejection threshold on
  24 of 36 object-cell-arm-rung combinations (mixed across rungs and
  geometries; see `predicate-lifts.json` for the full per-cell table). This
  metric uses the ANALYTIC null as a labelled substitute for the
  contract-specified NULL-A Monte Carlo null on these negation-closed arms
  (inherited deviation #3 from the original run, unchanged here -- per-draw
  NULL-A predicate sums were never retained in either run, so the
  contract-specified null cannot be built after the fact).
- **ALIVE competing-outcome literal test** (z > 3 SD on every curve at BOTH
  rungs 18 and 20, AND slope excludes 0 on the positive side): not met by any
  geometry (`alive_geometries_meeting_literal_test: []`) -- the observed
  slopes are confidently negative, not positive.

**Mechanical classification: `UNANTICIPATED_PATTERN_NOT_NULL_NOT_ALIVE`.**
The run meets the Delta-band-inclusion criterion of the pre-committed NULL
outcome but NOT its growth-slope-contains-0 criterion (slopes are confidently
negative, not zero, on all three geometries); it also does not meet the
ALIVE outcome's literal z>3-SD-with-positive-slope criterion. The frozen
`falsification_criterion` names only "interval containing both 0 and the
alive threshold" as INCONCLUSIVE/underpowered -- that is not this pattern
(the intervals confidently exclude 0 on the negative side, they are not
wide/ambiguous). This measured pattern numerically reproduces (to several
decimal places) what `RUN-RELN-f202be-stage4`'s `metrics.json` already
computed for these same Delta/growth-fit quantities before the amendment (that
run always computed the full metrics regardless of the instrument-failure
gate); this addendum changes only whether the forced-gap gate permits reading
a classification, not any underlying measured number.

**This is reported as an unanticipated observation for Coordinator/reviewer
characterization. It is explicitly NOT a NULL verdict, NOT an ALIVE verdict,
and it does NOT by itself change H-RELN-41562a's status** (remains
`proposed`), per the amendment's scope limits and the contract's
`later_review_requirements` (independent validator blind re-derivation, red
team attack on band/convention choices, review-adversarial at xhigh), which
remain owed in full before any claim-changing use.

## 4. Wall clock

0.69 s (analysis-only; no enumeration). Full session wall clock for this
addendum (re-execution of rungs 14, 16 plus this analysis): 40.79 s + 153.21 s
+ 0.69 s = approximately 195 s, well inside every stage budget.

## 5. Artifacts

`bands.json`, `metrics.json`, `predicate-lifts.json`, `control-verdicts.json`
(72-row full forced-gap table under `forced_negation_gap_all_cells`),
`classification.json`, `manifest.json`, `command.txt`, `environment.json`,
`stdout.log`, `stderr.log`.
