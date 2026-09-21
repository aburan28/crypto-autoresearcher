# Experiment Contract: P1014 p231 frozen raw-visibility rule validation

## Hypothesis
HYPOTHESIS: the P1013 public rule `transfer_index % 8 == 2`, `top_k == 12`, selected leaves contain `90`, and selector total suffix at least `2` transfers unchanged to unseen expanded-source windows as a public relation-surface predictor.

## Null hypothesis
On unseen windows, the frozen rule either selects no public-key-verified below-rho builder rows, selects only unverified rows, or fails context-safe scalar reconstruction below the Pollard-rho baseline.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- primary validation window: `12032_12039`
- unchanged stress-sweep windows: `12040_12047`, `12048_12055`
- diagnostic control: `12024_12031`, used only to verify P1013 reproduction
- factor base: expanded fixed compact-leaf public row policy `fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1`
- relation shape: two-row selected stress-leaf rows with leaf `90`, top-k `12`, transfer offset `2`
- baseline: Pollard rho charged as `1.0` ops-over-rho
- frozen order: `ops_asc_transfer`

## Metrics
- group operations: charged `source_ops_over_rho`
- field operations: inherited from source artifact ledgers
- memory: selected row count and reconstructed form count only
- relation probability: selected public-key-verified below-rho count over selected count
- rank: source rank and context-safe scalar-valid group count
- solver degree: not applicable to this component audit
- wall-clock: script runtime

## Positive control
The frozen rule and frozen order must reproduce the P1013 diagnostic result on `12024_12031`: six selected public-key-verified below-rho rows and a first scalar-valid hit below rho.

## Negative control
The same transfer offset/top-k/two-row shape without leaf `90` must not produce a context-safe below-rho scalar hit on each validation window.

## Success criterion
Primary success requires `12032_12039` to have at least one selected public-key-verified below-rho builder row and a first context-safe scalar-valid group charged below `1.0` rho under the frozen `ops_asc_transfer` order.

## Falsification criterion
The primary hypothesis is narrowed or rejected if `12032_12039` has zero selected public-key-verified rows, zero context-safe scalar-valid groups, or a first scalar-valid hit charged at or above `1.0` rho. Later-window sweep positives are recorded as reappearance evidence, not as primary validation.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1014_p231_frozen_raw_visibility_rule_12032.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1014_p231_frozen_raw_visibility_rule_12032.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1014_p231_frozen_raw_visibility_rule_12032_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for a relation-surface scheduler. It is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results

Command completed with:

```text
claim=NEGATIVE_RESULT_P1014_PRIMARY_SELECTS_NO_ROWS control_pass=True primary_selected=0 primary_pos=0 primary_groups=0 primary_first=None sweep_success=none out=ecdlp_index_calculus_state/low_term_total2_p1014_p231_frozen_raw_visibility_rule_12032_probe.json
```

Key measurements:

- diagnostic control `12024_12031`: control passed; selected `6`, positives `6`, context-safe scalar-valid groups `3`, first frozen-order hit `0.70072993` rho.
- primary `12032_12039`: selected `0`, positives `0`, scalar groups `0`; raw source summary still had `161` source-replay below-rho rows but the frozen candidate family had `0`.
- sweep `12040_12047`: selected `6`, positives `0`, scalar groups `0`; source summary had `39` public-key-verified stress-leaf below-rho rows, so the frozen leaf-90/offset-2 rule missed the active public-positive family.
- sweep `12048_12055`: selected `0`, positives `0`, scalar groups `0`; source summary had `27` public-key-verified stress-leaf below-rho rows.
- negative controls did not produce below-rho scalar-valid groups.

## Interpretation

Status: `NEGATIVE RESULT` for the exact frozen P1013 rule, not for raw-source visibility or prime-field index-calculus approaches generally.

The failure mode is specific: the P1013 offset/top-k/leaf-90 family was not a stable public invariant. The next concrete action is to learn a public cross-window invariant from the post-P1014 active public-positive windows `12040_12047` and `12048_12055`, then freeze it before scoring unseen windows from `12056_12063` onward.
