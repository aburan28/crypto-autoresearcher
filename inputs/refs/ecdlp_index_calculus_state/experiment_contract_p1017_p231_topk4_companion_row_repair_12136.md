# Experiment Contract: P1017 p231 top-k4 companion-row repair

## Hypothesis
HYPOTHESIS: public companion rows with exactly the same row-key set as a frozen top-k4 anchor can restore context-safe scalar closure for intermittent top-k4 relation-supply hits on unseen windows.

## Null hypothesis
Exact row-key companion expansion either selects mostly false-positive/noisy rows, fails to produce context-safe scalar-valid groups, or produces first scalar-valid hits above the Pollard-rho baseline on unseen windows.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- diagnostic repair-control window: `12104_12111`
- validation windows: `12136_12143`, `12144_12151`, `12152_12159`, `12160_12167`, `12168_12175`
- anchor rule: `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`
- companion rule: select every builder row whose public `row_leaf_keys.row_key` set exactly equals an anchor row-key set in the same window
- baseline: Pollard rho charged as `1.0` ops-over-rho
- frozen order: `salt_gap_asc_ops`

## Metrics
- group operations: charged `source_ops_over_rho`
- field operations: inherited from source artifact ledgers
- memory: selected row count and reconstructed form count only
- relation probability: selected public-key-verified below-rho count over selected count
- rank: source rank and context-safe scalar-valid group count
- solver degree: not applicable to this component audit
- wall-clock: script runtime

## Positive control
The exact row-key companion rule must repair the P1016 `12104_12111` top-k4 relation-supply hit into a context-safe below-rho scalar hit under the frozen order.

## Negative control
Anchor-only selection is scored on the same validation windows to show whether companion expansion improves or degrades scalar closure versus P1016’s standalone top-k4 rule.

## Success criterion
Validation success requires at least one unseen validation window to have a context-safe scalar-valid group charged below `1.0` rho under the frozen order, with false-positive windows and selected cost reported.

## Falsification criterion
The hypothesis is narrowed or rejected if validation windows have no selected anchor rows, no selected public-key-verified below-rho rows, no context-safe scalar-valid groups, or first scalar-valid hits charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1017_p231_topk4_companion_row_repair_12136.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1017_p231_topk4_companion_row_repair_12136.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1017_p231_topk4_companion_row_repair_12136_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for companion-row relation scheduling. A hit is an index-calculus precursor only; it is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results

Command completed with:

```text
claim=NEGATIVE_RESULT_P1017_VALIDATION_FIRST_HIT_ABOVE_RHO control_pass=True selected=100 positives=4 precision=0.04 groups=3 success=none false_positive_windows=12144_12151,12160_12167 out=ecdlp_index_calculus_state/low_term_total2_p1017_p231_topk4_companion_row_repair_12136_probe.json
```

Key measurements:

- diagnostic control `12104_12111`: exact row-key companion expansion repaired the P1016 hit; selected `30`, positives `16`, precision `0.53333333`, context-safe scalar-valid groups `2`, first hit `0.70072993` rho.
- validation aggregate `12136_12175`: selected `100`, positives `4`, precision `0.04`, context-safe scalar-valid groups `3`, but no below-rho first hit under the frozen order.
- validation `12168_12175`: selected `40`, positives `4`, scalar-valid groups `3`, best amortized group `0.73722628` rho, but first frozen-order hit was charged `23.71532859` rho because the expansion admitted many earlier companion rows.
- anchor-only baseline selected `5`, positives `0`, scalar groups `0`; companion expansion did improve algebraic closure but overselected.
- false-positive windows: `12144_12151`, `12160_12167`.

## Interpretation

Status: `NEGATIVE RESULT` for exact row-key companion expansion as a frozen validation scheduler, with a positive closure clue.

The useful signal is narrower than the exact row-key companion rule: the validation scalar-valid row in `12168` is a cost-hybrid leaf-19 sibling of the top-k4 anchor. The next concrete action is to test a public precision guard around that sibling family, using salt bounds or row-key ordering to avoid the noisy companion mass.
