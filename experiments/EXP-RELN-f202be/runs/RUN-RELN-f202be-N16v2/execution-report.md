# RUN-RELN-f202be-N16v2 -- execution report

Re-analysis run under protocol amendment v1
(`experiments/EXP-RELN-f202be/amendments/v1.yaml`, version_to 2, approved by
`DEC-20260907-432a39`). Path (a) of the amendment's
`reanalysis_authorization`: full re-execution of stage2/3 for rung 16 with
the same deterministic seeds as `RUN-RELN-f202be-N16`, using
`source/run_stage2_rung_v2.py` (an exact copy of `source/run_stage2_rung.py`,
differing only in the output RUN_ID / command strings -- see
`source/SHA256SUMS_v2` and the diff noted in `implementation.md`).

- Rung: 16. Curves (seeds): 39, 62, 64 (same accepted seeds as the original
  run, loaded unmodified from `RUN-RELN-f202be-stage0/curves.json`).
- Wall clock: 153.21 s.
- Status: `completed_valid`.
- Command: `python3 source/run_stage2_rung_v2.py 16`.
- Bit-for-bit reproducibility against `RUN-RELN-f202be-N16`: **0 non-timing
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
- Bose-Chowla control note (inherited from the original run, unchanged): the
  Bose-Chowla B_3-set construction requires prime q for the actual B_2 at
  this rung's curves; B_2 = 27 = 3^3 (a nontrivial prime power) for all three
  accepted curves at rung 16, so the Bose-Chowla control and its E-mirror are
  `skipped: true` here, as in the original run -- this is unrelated to the
  forced-negation-gap amendment and unaffected by it.
- No other deviation from `source/run_stage2_rung.py`'s protocol -- this is a
  re-execution, not a new measurement design.
