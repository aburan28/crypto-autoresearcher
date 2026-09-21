# Experiment Contract: P1052 p231 relation-generator constraint audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND: selected-leaf source-generation features may predict not only verifier success, but the actual factor-signature materialization needed for an index-calculus relation stream. In particular, order-`11779` column `15` may be visible before relation verification and may become an accepted factor-row motif under public constraints.

## Null hypothesis
Public selected-leaf constraints predict only verifier-local success or source-selection density, while the target column remains absent from accepted factor rows or live relation forms.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- priority order/column: order `11779`, factor column `15`
- selected-leaf artifacts: `low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json`
- factor-column artifacts: `low_term_total2_factor_column_target_scout_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json`
- audit window band: `11888_11895`, `11896_11903`, `11904_11911`, `11912_11919`, `11968_11975`, `11976_11983`
- calibration split: windows through `11912_11919`
- held-out split: windows from `11968_11975` through `11976_11983`
- baseline: Pollard rho remains the one-target scalar-search baseline; P1052 is a relation-generator constraint audit, not a complete solver or target-descent claim
- public rule catalog: priority-column hit, product-gate priority hit, top-k, selector family, selector name, support-size thresholds, and selected-support motif containment
- label classes:
  - pre-relation priority hit: selected-leaf support contains column `15`
  - verifier-local hit: direct/shared product public-key verification succeeds for a priority-hit case
  - factor-signature hit: target-column scout reports accepted factor rows or live forms touching column `15`

## Metrics
- train and validation case counts;
- priority-hit counts;
- product-gate priority-hit counts;
- direct verified priority-hit counts;
- shared-product verified priority-hit counts;
- baseline validation verified rate;
- best train-selected public rule;
- validation precision/recall for selected public rules;
- column `15` factor-target status per window;
- factor-signature materialization count;
- exact artifact paths and hashes.

## Positive control
The selected-leaf scout must report priority column visibility in both calibration and held-out windows. Without pre-relation priority visibility this audit cannot test the bridge to accepted factor signatures.

## Negative controls
The factor-column target scout must be checked independently of selected-leaf visibility. If selected leaves show column `15` but accepted factor rows/live forms do not, that is a bridge failure rather than a column-invisibility failure.

## Success criterion
Strict validation requires a train-selected public rule that:
- selects at least `8` calibration cases;
- improves shared-product verified-priority precision over calibration baseline;
- selects at least `8` held-out cases;
- improves shared-product verified-priority precision over held-out baseline;
- has at least one held-out selected case with shared-product ops/rho below `1`;
- and, critically, at least one held-out factor-column target report where column `15` has accepted factor-row support or live relation-form support.

## Falsification criterion
P1052 is negative for this relation-generator constraint if selected-leaf visibility and verifier-local hits exist, but column `15` remains absent from accepted factor rows/live forms. This is a scoped negative for this selected-leaf-to-factor-signature bridge, not for index calculus over prime-field ECDLP.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1052_p231_relation_generator_constraint_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1052_p231_relation_generator_constraint_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1052_p231_relation_generator_constraint_audit_probe.json
```

## Interpretation boundary
This audit uses existing toy p231 selected-leaf and factor-column artifacts. A pass would be an index-calculus precursor only; it would still require relation collection, sparse linear algebra, target descent, scaling tests, and charged comparison to Pollard rho.

## Sub-agent handoff: Red-team interpretation

### Claim or task
Test whether pre-relation selected-leaf column visibility actually creates accepted factor-signature support.

### Status
HYPOTHESIS

### Assumptions
- Selected-leaf term support is public source-generation evidence.
- Direct/shared product verification is post-generation verifier evidence and cannot by itself prove factor-signature materialization.
- Factor-column target reports are the relevant accepted-relation surface for column `15`.

### Evidence so far
- P1051 found no row-level low-degree invariant over public coordinates and row coefficients.
- Recent selected-leaf scouts show frequent column `15` visibility.

### Failure modes
- Public rules may predict verifier-local success while accepted factor rows still drop the target column.
- Window splits may cross policy regimes, so validation must be reported with exact window bands.
- Source-charged rho accounting remains incomplete unless rejected-row cost and accepted factor-row materialization are both charged.

### Next concrete action
Run the P1052 probe, then preserve the bridge status and next source-generation hypothesis in the ledger.

### Artifact paths
- `tasks/ecdlp_index_calculus/low_term_total2_p1052_p231_relation_generator_constraint_audit.py`
- `ecdlp_index_calculus_state/low_term_total2_p1052_p231_relation_generator_constraint_audit_probe.json`

## Results
Timestamp: `2026-06-30T06:09:05Z` in `ecdlp_index_calculus_state/low_term_total2_p1052_p231_relation_generator_constraint_audit_probe.json`.

Claim: `NEGATIVE_RESULT_P1052_SELECTED_LEAF_VERIFIER_SIGNAL_FACTOR_SIGNATURE_GAP`.

- Selected-leaf artifacts: `6`.
- Candidate public rules tested: `49`.
- Positive control: pass; selected-leaf column `15` visibility exists in calibration and held-out windows.
- Calibration split: `260` cases over windows `11888_11895`, `11896_11903`, `11904_11911`, `11912_11919`; priority hits `199`; product-gate priority hits `139`; direct verified priority hits `14` with precision `0.07035176`; shared-product verified priority hits `12` with precision `0.06030151`; shared verified below-rho selected-case hits `12`.
- Held-out split: `220` cases over windows `11968_11975`, `11976_11983`; priority hits `170`; product-gate priority hits `116`; direct verified priority hits `84` with precision `0.49411765`; shared-product verified priority hits `57` with precision `0.33529412`; shared verified below-rho selected-case hits `57`.
- Top train-selected rule `top_k_eq_4`: calibration `8/40` shared-product precision `0.2`; held-out `17/50` shared-product precision `0.34`; minimum held-out shared ops/rho `0.67883212`.
- Top selector-family rule `family_eq_hybrid`: calibration `6/52` shared-product precision `0.11538462`; held-out `18/44` shared-product precision `0.40909091`; minimum held-out shared ops/rho `0.67883212`.
- Factor-signature materialization count for order `11779` column `15`: `0`.
- Held-out factor-column target reports `11968_11975` and `11976_11983`: both `UNSEEN_IN_ROWS_AND_LIVE_FORMS`, with accepted/live support count `0`.
- Strict validation passes: `0`.

## Interpretation
P1052 found a real selected-leaf and verifier-local signal: public rules can select held-out priority cases with shared-product verified hits below the selected-case rho baseline. This is not yet an index-calculus relation generator because the same signal did not materialize column `15` in accepted factor rows or live relation forms.

Status: NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND / PRE-RELATION SELECTED-LEAF VISIBILITY / FACTOR-SIGNATURE-BRIDGE-GAP / SOURCE-CHARGED-INCOMPLETE / NOT SPARSE-LA CLOSURE / NOT TARGET DESCENT / POLLARD-RHO BOUNDARY.

The narrow negative result is that selected-leaf visibility and verifier-local success are insufficient for this column-`15` factor-signature bridge. The broader positive question remains open: find a source construction that preserves or forces the useful column into accepted factor rows/live forms before sparse linear algebra and target descent are considered.

## Next concrete action
Build P1053 as an accepted-factor materialization bridge: alter source construction or materialization so order-`11779` column `15` survives into accepted factor rows/live relation forms, not merely selected leaves. Require held-out factor-signature support, accepted/live row certificates, and source-charged rho accounting before promoting the signal.
