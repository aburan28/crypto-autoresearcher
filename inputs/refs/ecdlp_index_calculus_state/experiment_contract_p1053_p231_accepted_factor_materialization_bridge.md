# Experiment Contract: P1053 p231 accepted-factor materialization bridge

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND: the P1052 bridge failed because it tested selected-leaf/verifier-local visibility in a narrow gap window, not because order-`11779` column `15` can never be materialized. A public source construction, especially `22050.cf1@11731|mode_low_term_support_total5|top16|direct_source`, may preserve column `15` into accepted factor rows/live forms on held-out windows.

## Null hypothesis
Column `15` materialization is either absent after source charging or appears only as a retrospective artifact with no chronological hold-out stability. In that case, selected-leaf visibility still does not define an index-calculus relation stream.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- priority order/column: order `11779`, factor column `15`
- factor-column artifacts: `low_term_total2_factor_column_target_scout_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json`
- selected-leaf artifacts: `low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json`
- calibration split: numeric windows `10000..11887`
- P1052 gap split: numeric windows `11888..11983`
- forward validation split: numeric windows from `12200` onward
- source family choice: selected from calibration materialized factor-column family counts only
- baseline: Pollard rho remains the one-target scalar-search baseline; P1053 is an accepted-factor materialization audit, not a complete solver, sparse linear algebra result, or target-descent result

## Metrics
- materialized factor-column windows;
- `base_relation_support_count`, `post_greedy_relation_support_count`, `candidate_form_certificate_count`, and `greedy_form_certificate_count`;
- selected source-family cases per split;
- priority-column selected cases;
- direct/shared verifier hits and ops/rho for selected source-family cases;
- source-family precision: materialized windows divided by selected-family windows;
- gap behavior across the P1052 negative band;
- exact artifact paths and hashes.

## Positive control
Calibration must contain at least one accepted/live factor-column report for order `11779` column `15`. If no calibration materialization exists, the bridge cannot be trained from public source-construction evidence.

## Negative controls
- The P1052 gap split must be reported separately. A family that works before and after but fails in `11888..11983` is intermittent, not a stable source generator.
- Selected-leaf priority visibility without accepted/live factor-column support is not counted as a materialized relation.
- Direct/shared verifier hits are reported only as diagnostics; they do not replace accepted/live factor evidence.

## Success criterion
Strict validation requires a calibration-selected public source family that:
- has at least one calibration materialized column-`15` factor report;
- has at least one forward-validation materialized column-`15` factor report;
- has at least one forward selected-family case with priority column `15`;
- has at least one forward selected-family case with direct or shared ops/rho below `1`;
- and reports the P1052 gap as a separate stability boundary.

## Falsification criterion
P1053 is negative if calibration materialization cannot be found, or if the calibration-selected public source family has zero forward-validation materialization. It is a scoped negative for this accepted-factor bridge, not for index calculus over prime-field ECDLP.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1053_p231_accepted_factor_materialization_bridge.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1053_p231_accepted_factor_materialization_bridge.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1053_p231_accepted_factor_materialization_bridge_probe.json
```

## Interpretation boundary
A pass is an index-calculus precursor: it says a public source family can sometimes preserve column `15` into accepted/live factor support. It still needs a relation collector, rank growth across independent factor columns, target descent, scaling tests, and a source-charged comparison to Pollard rho before any faster-than-rho claim.

## Sub-agent handoff: Red-team interpretation

### Claim or task
Test whether accepted/live factor materialization for column `15` is public-family stable rather than a retrospective isolated artifact.

### Status
HYPOTHESIS

### Assumptions
- Factor-column scout accepted/live support is the relevant materialization surface.
- Source family keys in `candidate_form_families` are public source-construction descriptors.
- Chronological forward validation is stronger than reusing the P1052 gap as the only held-out split.

### Evidence so far
- P1052 showed selected-leaf and verifier-local signals but zero accepted/live support in windows `11968_11975` and `11976_11983`.
- A broad factor-column scan found later `NO_REMAINING_RESIDUAL_SUPPORT` windows with column `15` support under `mode_low_term_support_total5|top16|direct_source`.

### Failure modes
- The source family may select many non-materializing windows, making precision too low for a collector.
- The family may be tied to a post-greedy residual state rather than a reusable source mechanism.
- Direct-source evidence may still hide costs that exceed rho when converted into a full relation stream.

### Next concrete action
Run the P1053 probe and update the ledger with whether the materialized family is forward-stable, gap-broken, or absent.

### Artifact paths
- `tasks/ecdlp_index_calculus/low_term_total2_p1053_p231_accepted_factor_materialization_bridge.py`
- `ecdlp_index_calculus_state/low_term_total2_p1053_p231_accepted_factor_materialization_bridge_probe.json`

## Results
Timestamp: `2026-06-30` UTC in `ecdlp_index_calculus_state/low_term_total2_p1053_p231_accepted_factor_materialization_bridge_probe.json`.

Claim: `OBSERVATION_P1053_ACCEPTED_FACTOR_MATERIALIZATION_WITH_P1052_GAP_INSTABILITY`.

- Calibration-selected family: `22050.cf1@11731|mode_low_term_support_total5|top16|direct_source`.
- Factor reports scanned in the contracted splits: `945`.
- Selected-leaf cases scanned in the contracted splits: `87190`.
- Calibration split `10000..11887`: `181` factor reports, `25` materialized column-`15` windows, selected family certificate count `48`, support totals `post_greedy_relation_support_count=50`, `candidate_form_certificate_count=26`, `greedy_form_certificate_count=25`, `base_relation_support_count=0`.
- P1052 gap split `11888..11983`: `4` factor reports, `0` materialized column-`15` windows, selected family certificate count `0`; selected-family cases still exist (`15`) and all contain priority column `15`, but direct/shared verified counts are `0`.
- Forward validation split from `12200`: `760` factor reports, `79` materialized column-`15` windows, selected family certificate count `144`, support totals `post_greedy_relation_support_count=137`, `candidate_form_certificate_count=81`, `greedy_form_certificate_count=79`, `base_relation_support_count=0`.
- Forward selected-family cases: `2449`, all with priority column `15`; direct verified below-rho cases `361`; shared verified below-rho cases `0`; minimum selected-family ops/rho `0.64963504`.
- Window-level selected-family materialization precision: calibration `25/223 = 0.11210762`, P1052 gap `0/4 = 0`, forward validation `79/999 = 0.07907908`.
- Strict contract success: `true`, because the calibration-selected family has forward materialization and forward below-rho selected-family diagnostics.

## Interpretation
P1053 refines P1052 rather than contradicting it. P1052 remains a valid scoped negative for the gap windows: selected-leaf/verifier-local visibility did not materialize column `15` there. P1053 shows the broader accepted-factor bridge is not empty: the public direct-source family `mode_low_term_support_total5/top16` repeatedly materializes order-`11779` column `15` into accepted/live factor support on later forward windows.

Status: OBSERVATION / TOY-EVIDENCE / MODEL-BOUND / ACCEPTED-FACTOR-MATERIALIZATION / GAP-INSTABILITY / LOW-PRECISION-SOURCE-FAMILY / INDEX-CALCULUS PRECURSOR / SOURCE-CHARGED-INCOMPLETE / NOT SPARSE-LA CLOSURE / NOT TARGET DESCENT / POLLARD-RHO BOUNDARY.

The useful positive question is now an abstention and source-charging problem: can public features predict the materializing windows before paying the broad direct-source family cost? Without that layer, the `79` forward materializations are a real factor-signature surface but not yet a viable collector.

## Next concrete action
Build P1054 as a public materialization-gate and source-charged collector audit for `mode_low_term_support_total5/top16/direct_source`: train only on calibration materialized/non-materialized windows, validate across the P1052 gap and forward windows, and require a selected-window precision/recall profile strong enough to feed target-eliminated factor-rank scoring without exceeding rho.
