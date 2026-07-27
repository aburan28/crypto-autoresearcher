# Experiment Contract: P1054 p231 public materialization gate

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND: P1053 found that `22050.cf1@11731|mode_low_term_support_total5|top16|direct_source` can materialize order-`11779` column `15` into accepted/live factor support, but broad use of that family has low window precision. A public source-window gate over family density, salt spread, transfer span, and operation estimates may select materializing windows more efficiently than the broad family baseline.

## Null hypothesis
Calibration source-window features either overfit or do not improve forward materialization precision. In that case the P1053 bridge remains a real accepted-factor surface but not yet a usable collector.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- priority order/column: order `11779`, factor column `15`
- source family: `target=22050.cf1@11731`, `selector=mode_low_term_support_total5`, `top_k=16`
- factor-column artifacts: `low_term_total2_factor_column_target_scout_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json`
- selected-leaf artifacts: `low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json`
- calibration split: numeric windows `10000..11887`
- P1052 gap split: numeric windows `11888..11983`
- forward validation split: numeric windows from `12200` onward
- allowed selector features: source-family case count, priority-column case count, unique salt count, salt span/min/max, transfer span, and direct-source operation estimates
- excluded selector features: accepted/live factor label, direct/shared public-key verification label, scalar-valid label, secret, and any forward materialization outcome
- baseline: Pollard rho remains the one-target scalar-search baseline; P1054 is a materialization gate, not a complete solver or target-descent claim

## Metrics
- calibration and forward broad materialization precision over labeled factor windows;
- calibration-selected public rule expression;
- selected windows, materialized windows, precision, and recall per split;
- P1052 gap false-positive count;
- diagnostic direct/shared verification counts, not used for gate selection;
- source-family selected case counts and operation estimate ranges;
- exact artifact paths and hashes or aggregate digest.

## Positive control
The broad source family must reproduce the P1053 positive surface: at least one calibration and one forward materialized window.

## Negative controls
- The P1052 gap split is evaluated separately. A rule that selects gap windows with no materialization is a false-positive boundary.
- Rules are selected using calibration labels only.
- Direct/shared verification labels are diagnostics only; they cannot be part of the selected public gate.

## Success criterion
Strict P1054 gate success requires a calibration-selected source-only rule that:
- selects at least `10` calibration windows;
- materializes at least `3` calibration windows;
- has calibration precision at least `2x` the broad calibration labeled-window baseline;
- selects at least `10` forward windows;
- materializes at least `5` forward windows;
- has forward precision greater than the broad forward labeled-window baseline;
- and reports P1052 gap selection explicitly.

This is still a collector precursor. It does not claim faster-than-rho ECDLP unless later source-charged collection, factor-rank growth, and target descent are successful.

## Falsification criterion
P1054 is negative if no calibration-selected source-only rule satisfies the calibration gate, or if the selected rule does not improve forward materialization precision over the broad labeled-window baseline.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1054_p231_public_materialization_gate.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1054_p231_public_materialization_gate.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1054_p231_public_materialization_gate_probe.json
```

## Interpretation boundary
A P1054 pass means public source-window features improve the materialization gate for the P1053 direct-source bridge. It still needs a source-charged relation collector, accepted row export, target-eliminated factor-rank scoring, sparse linear algebra, target descent, and scaling tests before any faster-than-rho claim.

## Sub-agent handoff: Red-team interpretation

### Claim or task
Test whether public source-window features predict accepted/live column-`15` materialization better than the broad P1053 family baseline.

### Status
HYPOTHESIS

### Assumptions
- Selected-leaf source-window summaries are public before factor materialization.
- Operation estimates can be used for ordering/gating, but direct/shared verification labels cannot.
- Chronological forward windows are the primary validation surface.

### Evidence so far
- P1053 found `25` calibration and `79` forward materialized windows for the direct-source family.
- P1053 also found zero materialization in the P1052 gap.

### Failure modes
- Calibration gates may select a narrow salt/transfer artifact that does not forward-transfer.
- A gate may improve precision but lose too much recall to feed factor-rank scoring.
- Source charge may still exceed rho when exported into a full accepted-row collector.

### Next concrete action
Run the P1054 probe and record whether the selected public gate is forward-stable, gap-clean, and strong enough to justify a P1055 source-charged collector.

### Artifact paths
- `tasks/ecdlp_index_calculus/low_term_total2_p1054_p231_public_materialization_gate.py`
- `ecdlp_index_calculus_state/low_term_total2_p1054_p231_public_materialization_gate_probe.json`

## Results
Timestamp: `2026-06-30` UTC in `ecdlp_index_calculus_state/low_term_total2_p1054_p231_public_materialization_gate_probe.json`.

Claim: `POSITIVE_SIGNAL_P1054_PUBLIC_MATERIALIZATION_GATE_LOW_RECALL`.

- Input artifact count: `4007`; the probe records an aggregate input artifact digest.
- Selected public rule: `(transfer_span >= 6) AND (mean_ops >= 0.72992701)`.
- Rule source: calibration-only selection over public source-window features; accepted/live materialization labels were used only in calibration, and direct/shared verifier labels were excluded from the gate.
- Calibration baseline over labeled factor windows: `25/181 = 0.13812155`; broad source-family baseline: `25/173 = 0.14450867`.
- Calibration selected by rule: `10` windows; materialized `6`; precision `0.6`; recall `0.24`; support totals `post_greedy_relation_support_count=14`, `candidate_form_certificate_count=7`, `greedy_form_certificate_count=6`.
- P1052 gap selected by rule: `0` windows; materialized `0`; this keeps the gap as a clean abstention under the selected gate.
- Forward baseline over labeled factor windows: `79/760 = 0.10394737`; broad source-family baseline: `79/725 = 0.10896552`.
- Forward selected by rule: `50` windows; materialized `13`; precision `0.26`; recall `0.16455696`; support totals `post_greedy_relation_support_count=33`, `candidate_form_certificate_count=14`, `greedy_form_certificate_count=13`.
- Forward diagnostic direct-verified below-rho cases among selected windows: `46`. This is not part of the selected gate.

## Interpretation
P1054 turns the P1053 accepted-factor bridge from an unfiltered low-precision surface into a public, forward-validating materialization gate. The selected source-only rule improves forward labeled-window precision by about `2.50x` over the broad labeled baseline and about `2.39x` over the broad source-family baseline.

Status: POSITIVE SIGNAL / TOY-EVIDENCE / MODEL-BOUND / PUBLIC-MATERIALIZATION-GATE / LOW-RECALL / ACCEPTED-FACTOR-MATERIALIZATION / INDEX-CALCULUS PRECURSOR / SOURCE-CHARGED-INCOMPLETE / NOT SPARSE-LA CLOSURE / NOT TARGET DESCENT / POLLARD-RHO BOUNDARY.

The low recall is the main limitation: `13/79` forward materialized windows are recovered. This is enough to justify an accepted-row exporter and rank-scoring audit, but not enough to claim a complete collector or any faster-than-rho ECDLP algorithm.

## Next concrete action
Build P1055 as a source-charged accepted-row collector and factor-rank scoring audit for the P1054 gate: export accepted/live column-`15` rows selected by the public gate, charge the selected source windows against rho, and test whether they add target-eliminated factor-rank dimensions beyond the existing order-`11779` bank.
