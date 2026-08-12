# Experiment Contract: P1015 p231 cross-window public invariant

## Hypothesis
HYPOTHESIS: the post-P1014 active windows `12040_12047` and `12048_12055` contain a public feature invariant for builder-visible below-rho relation rows that transfers unchanged to unseen windows from `12056_12063` onward.

## Null hypothesis
Any public predicate learned from `12040_12047` and `12048_12055` either fails to hit both training windows, overselects unverified/noisy rows, or does not transfer to unseen windows with a context-safe scalar hit below Pollard rho.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- training windows: `12040_12047`, `12048_12055`
- primary validation window: `12056_12063`
- unchanged stress-sweep windows: `12064_12071`, `12072_12079`, `12080_12087`, `12088_12095`
- factor base: expanded fixed compact-leaf public row policy `fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1`
- relation shape: builder-visible source rows from the expanded source artifact
- baseline: Pollard rho charged as `1.0` ops-over-rho
- order: chosen from public order candidates using training lanes only

## Metrics
- group operations: charged `source_ops_over_rho`
- field operations: inherited from source artifact ledgers
- memory: selected row count and reconstructed form count only
- relation probability: selected public-key-verified below-rho count over selected count
- rank: source rank and context-safe scalar-valid group count
- solver degree: not applicable to this component audit
- wall-clock: script runtime

## Positive control
The selected predicate must hit at least one public-key-verified below-rho builder row in each training window.

## Negative control
The same learner must report if no cross-window predicate exists under the public feature grammar and selected-count cap.

## Success criterion
Primary success requires `12056_12063` to have at least one selected public-key-verified below-rho builder row and a first context-safe scalar-valid group charged below `1.0` rho under the frozen training-chosen order.

## Falsification criterion
The primary hypothesis is narrowed or rejected if `12056_12063` has zero selected public-key-verified rows, zero context-safe scalar-valid groups, or a first scalar-valid hit charged at or above `1.0` rho. Later-window positives are recorded as reappearance evidence, not as primary validation.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1015_p231_cross_window_public_invariant_12056.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1015_p231_cross_window_public_invariant_12056.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1015_p231_cross_window_public_invariant_12056_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for a relation-surface scheduler. A positive result would be an index-calculus precursor only; it is not sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results

Command completed with:

```text
claim=NEGATIVE_RESULT_P1015_PRIMARY_MISS_WITH_LATER_REAPPEARANCE rule=topk=4 AND selector=mode_cost_low_term_support_total2 order=salt_gap_asc_ops primary_selected=0 primary_pos=0 primary_groups=0 primary_first=None sweep_success=12064_12071 out=ecdlp_index_calculus_state/low_term_total2_p1015_p231_cross_window_public_invariant_12056_probe.json
```

Key measurements:

- learned rule: `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`.
- chosen public order: `salt_gap_asc_ops`.
- training `12040_12047`: selected `2`, positives `2`, precision `1.0`, scalar-valid groups `6`, first hit `0.70072993` rho.
- training `12048_12055`: selected `2`, positives `1`, precision `0.5`, scalar-valid groups `3`, first hit `0.70072993` rho.
- primary `12056_12063`: selected `0`, positives `0`, scalar groups `0`; primary validation failed by row absence.
- sweep `12064_12071`: selected `1`, positives `1`, precision `1.0`, scalar-valid groups `3`, first hit `0.72992701` rho, derived secret `3255`.
- sweep `12088_12095`: selected `1`, positives `0`, scalar groups `0`, showing the exact rule has sparse false-positive risk.

## Interpretation

Status: `NEGATIVE RESULT` for primary transfer to `12056_12063`, with later reappearance on `12064_12071`.

The useful refinement is that the top-k4 cost-low-term-total2 family is an intermittent relation-surface scheduler rather than a per-window invariant. The next concrete action is to freeze it unchanged and validate it as an opportunistic sparse scheduler over untouched later batches, where abstention is allowed but false-positive rate and below-rho hit charge are measured.
