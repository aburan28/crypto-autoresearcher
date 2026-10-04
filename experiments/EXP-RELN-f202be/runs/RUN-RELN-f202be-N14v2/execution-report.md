# RUN-RELN-f202be-N14v2 -- execution report

Re-analysis run under protocol amendment v1
(`experiments/EXP-RELN-f202be/amendments/v1.yaml`, version_to 2, approved by
`DEC-20260907-432a39`). Path (a) of the amendment's
`reanalysis_authorization`: full re-execution of stage2/3 for rung 14 with
the same deterministic seeds as `RUN-RELN-f202be-N14`, using
`source/run_stage2_rung_v2.py` (an exact copy of `source/run_stage2_rung.py`,
differing only in the output RUN_ID / command strings -- see
`source/SHA256SUMS_v2` and the diff noted in `implementation.md`).

- Rung: 14. Curves (seeds): 17, 24, 67 (same accepted seeds as the original
  run, loaded unmodified from `RUN-RELN-f202be-stage0/curves.json`).
- Wall clock: 40.79 s.
- Status: `completed_valid`.
- Command: `python3 source/run_stage2_rung_v2.py 14`.
- Bit-for-bit reproducibility against `RUN-RELN-f202be-N14`: **0 non-timing
  field differences** across the entire `curve_results.json` (18 object
  cells x 3 curves plus NULL/control arms); `accounting.json` byte-identical.
  See `reanalysis-provenance.json` in this directory for the full check.
- This run's own `forced_gap_within_0.1` field (per object cell, in
  `curve_results.json`) still reports the FROZEN v1 (fixed absolute 0.1)
  tolerance verdict, unchanged -- this run does not itself apply the amended
  tolerance. The amended tolerance is applied downstream in
  `RUN-RELN-f202be-stage4v2/control-verdicts.json`, computed directly from
  this run's recorded `forced_negation_gap_measured` / `_expected` / `B`
  values per cell.
- No other deviation from `source/run_stage2_rung.py`'s protocol (curve
  generation recipe, base conventions, sign conventions, predicate family,
  null-draw counts, master seed) -- this is a re-execution, not a new
  measurement design.
