# Experiment Contract: P1016 p231 frozen top-k4 sparse scheduler

## Hypothesis
HYPOTHESIS: the P1015 top-k4 public rule `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`, with frozen order `salt_gap_asc_ops`, acts as an opportunistic sparse relation-surface scheduler on untouched later windows.

## Null hypothesis
On untouched later windows, the frozen top-k4 rule either never selects rows, selects only unverified/noisy rows, or fails to produce a context-safe scalar-valid hit below the Pollard-rho baseline.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- control window: `12064_12071`, used only to verify the P1015 reappearance line
- validation batch: `12096_12103`, `12104_12111`, `12112_12119`, `12120_12127`, `12128_12135`
- factor base: expanded fixed compact-leaf public row policy `fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1`
- relation shape: builder-visible source rows selected by the frozen top-k4 rule
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
The rule and order must reproduce the `12064_12071` P1015 below-rho reappearance.

## Negative control
Untouched validation windows where the rule selects rows but no public-key-verified below-rho row are counted as false-positive windows and included in the batch precision.

## Success criterion
Batch success requires at least one untouched validation window to have a selected public-key-verified below-rho builder row and a first context-safe scalar-valid group charged below `1.0` rho under `salt_gap_asc_ops`.

## Falsification criterion
The sparse-scheduler hypothesis is narrowed or rejected if the validation batch has no selected rows, no selected public-key-verified rows, no context-safe scalar-valid groups, or first scalar-valid hits charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1016_p231_frozen_topk4_sparse_scheduler_12096.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1016_p231_frozen_topk4_sparse_scheduler_12096.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1016_p231_frozen_topk4_sparse_scheduler_12096_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for sparse relation scheduling. A hit is an index-calculus precursor only; it is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results

Command completed with:

```text
claim=NEGATIVE_RESULT_P1016_BATCH_NO_CONTEXT_SAFE_SCALAR_GROUP control_pass=True selected=6 positives=1 precision=0.16666667 success=none false_positive_windows=12112_12119,12120_12127 out=ecdlp_index_calculus_state/low_term_total2_p1016_p231_frozen_topk4_sparse_scheduler_12096_probe.json
```

Key measurements:

- control `12064_12071`: reproduced P1015; selected `1`, positive `1`, scalar-valid groups `3`, first hit `0.72992701` rho.
- validation aggregate over `12096_12135`: selected `6`, positive `1`, batch precision `0.16666667`, selected cost `4.05839418` rho, context-safe scalar-valid groups `0`.
- `12104_12111`: selected `2`, positives `1`, precision `0.5`, but scalar-valid groups `0`; the positive row was transfer `12105`, salt gap `11`, leaf tuple `[90]`, rank `2`, ops `0.77372263` rho.
- false-positive windows: `12112_12119` selected `3/0`, `12120_12127` selected `1/0`.
- abstention windows: `12096_12103`, `12128_12135`.

## Interpretation

Status: `NEGATIVE RESULT` for the exact frozen top-k4 sparse scheduler as a scalar-recovery rule on the untouched batch.

The result still preserves a positive relation-supply clue: `12104_12111` has a selected public-key-verified below-rho row, but the singleton top-k4 selector does not provide enough compatible forms for context-safe scalar derivation. The next concrete action is a companion-row repair: use public sibling selectors sharing the same row-key/leaf-90 surface around the top-k4 hit, then validate whether rank closure returns without reopening the false positives seen on `12112` and `12120`.
