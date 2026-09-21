# Experiment Contract: P1013 p231 raw-source visibility rescue

## Hypothesis
HYPOTHESIS: raw source-replay below-rho stress-leaf rows from `12016_12023` expose a public feature family that predicts builder-visible, public-key-verified below-rho relation rows on `12024_12031`.

## Null hypothesis
The raw source-replay rows are only materializer-local artifacts: any public family derived from them either selects no builder-visible public-key-verified rows, selects mostly unverified rows, or fails context-safe scalar reconstruction above the Pollard-rho baseline.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- sizes: window `12016_12023` for raw-source feature extraction; window `12024_12031` for diagnostic holdout scoring
- seeds: encoded in source artifacts and transfer indices
- factor base: expanded fixed compact-leaf public row policy `fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1`
- relation shape: two-row selected stress-leaf rows with leaf `90`, top-k `12`, transfer offset `2`
- baseline: Pollard rho charged as `1.0` ops-over-rho

## Metrics
- group operations: charged `source_ops_over_rho`
- field operations: inherited from source artifact ledgers
- memory: selected row count and reconstructed form count only
- relation probability: selected public-key-verified below-rho count over selected count
- rank: source rank and context-safe scalar-valid group count
- solver degree: not applicable to this component audit
- wall-clock: script runtime

## Positive control
The public rule must cover raw `12016_12023` rows with `source_verified=true` and `below_rho=true`, showing that the rule is grounded in the raw source-replay signal.

## Negative control
The same transfer offset/top-k/two-row shape without leaf `90` should not produce a context-safe below-rho scalar hit on `12024_12031`.

## Success criterion
On `12024_12031`, the rule selects at least one public-key-verified below-rho builder row and the first context-safe scalar-valid group is charged below `1.0` rho under a public order.

## Falsification criterion
The hypothesis is narrowed or rejected if the rule has zero selected public-key-verified rows, zero context-safe scalar-valid groups, or the first scalar-valid hit is charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1013_p231_raw_source_visibility_rescue_12024.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1013_p231_raw_source_visibility_rescue_12024.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1013_p231_raw_source_visibility_rescue_12024_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` and a diagnostic rescue audit, not a clean frozen validation and not a full faster-than-rho ECDLP algorithm. A positive result only justifies freezing the public rule unchanged for the next unseen window and integrating it into a broader index-calculus relation-collection track.

## Results

Command completed with:

```text
claim=P1013_DIAGNOSTIC_RAW_SOURCE_VISIBILITY_RESCUE_BELOW_RHO selected=6 positives=6 precision=1.0 groups=3 best_charge=0.70072993 negative_selected=4 out=ecdlp_index_calculus_state/low_term_total2_p1013_p231_raw_source_visibility_rescue_12024_probe.json
```

Key measurements:

- raw `12016_12023`: `132` source-replay below-rho rows, all public-key unverified; candidate rule covers `6` source-replay below-rho raw rows.
- builder `12016_12023`: `0` public-key-verified stress positives, confirming the materializer-visibility mismatch.
- builder `12024_12031`: candidate selects `6/77` rows, all `6` are public-key-verified below rho; precision `1.0`, recall `1.0` over builder-visible stress positives.
- context-safe reconstruction: `3` scalar-valid groups, best first hit `0.70072993` rho, derived secret `3029`.
- negative control: selected `4` rows, `0` public-key-verified positives, `0` context-safe scalar-valid groups.

## Interpretation

Status: `OBSERVATION` / `TOY-EVIDENCE` / `DIAGNOSTIC`.

The raw source-replay feature family `transfer_index % 8 == 2`, `top_k == 12`, leaf `90`, and selector total suffix at least `2` is a viable index-calculus surface predictor on this diagnostic pair of windows. This is not a full ECDLP algorithm and not a clean prospective validation because `12024_12031` was inspected during triage. The next concrete action is to freeze this exact public rule unchanged on the next unseen expanded-source window, starting with `12032_12039` if available.
