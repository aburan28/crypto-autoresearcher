# Experiment Contract: P1037 p231 public consistency-guard scout

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: P1036 showed that adjacent repeated two-tail families create q-diverse same-public same-window supply, but naive local-factor elimination is not scalar-stable. A public consistency guard over group size, q-count, salt/row-key diversity, and term/tail gaps may preserve the clean P1033/P1036 scout signal while rejecting the compressed P1036 false witness.

## Null hypothesis
No public guard in the finite catalog both preserves a clean scout-window signal and rejects the compressed later false witness. This would keep the next bottleneck at representation design rather than guard selection.

## Guard catalog
The scout tests only public metadata:
- pair salt and row-key diversity;
- salt-gap thresholds;
- group form count and q-count thresholds;
- repeated-term gap and tail-width thresholds;
- exact-tail/motif/object model restrictions;
- q/rhs difference thresholds;
- fixed combinations of these primitives.

The guard catalog must not use `source_secret` or `toy_secret_verified` when selecting pairs.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scout/control window: `12440_12447`
- later validation windows: `12448_12455` through `12496_12503`
- source rank floor: `0`
- modulus/order: `11779`
- row pools: `p1029_leaf8_scout`, `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- primary false-witness context: `all_target_rows_later_compressed`
- primary clean control: `p1029_leaf8_scout_scout_compressed`

## Metrics
- prediction count selected by each guard;
- true/false toy-secret verification count after selection;
- clean-control preservation;
- compressed false-witness rejection;
- later compressed signal count after guard;
- raw diagnostic false count after guard.

## Positive control
At least one guard should preserve the P1033/P1036 scout-window compressed clean signal with nonzero true predictions and zero false predictions.

## Negative control
The primary false-witness context is P1036 `all_target_rows_later_compressed`, which contains the `[1,1,2,2]` / tail `[2,3]` compressed false prediction. A successful guard must reject this context or select it with zero false predictions.

## Success criterion
Primary success requires a public guard with:
- nonzero true predictions and zero false predictions in `p1029_leaf8_scout_scout_compressed`;
- zero false predictions in `all_target_rows_later_compressed`;
- and, for a stronger relation-generation signal, at least one later compressed prediction with zero false predictions.

## Falsification criterion
If every guard that preserves the clean control also selects a false prediction in the compressed later context, this finite public guard catalog fails. If guards reject the false witness but leave no later compressed predictions, this is a useful consistency-filter result, not a new relation-generation positive.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1037_p231_public_consistency_guard_scout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1037_p231_public_consistency_guard_scout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1037_p231_public_consistency_guard_scout_probe.json
```

## Interpretation boundary
This experiment tests guardability of a relation-generation component. It does not prove a complete faster-than-rho ECDLP algorithm, sparse linear algebra closure, or target descent. Pollard rho remains the one-target scalar-search baseline.

## Results
- timestamp: 2026-06-30T03:35:27Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1037_p231_public_consistency_guard_scout.py --contract ecdlp_index_calculus_state/experiment_contract_p1037_p231_public_consistency_guard_scout.md --out ecdlp_index_calculus_state/low_term_total2_p1037_p231_public_consistency_guard_scout_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1037_p231_public_consistency_guard_scout_probe.json`
- claim: `P1037_PUBLIC_GUARD_REJECTS_COMPRESSED_FALSE_WITNESS_NO_LATER_SIGNAL`
- event reconstruction:
  - `p1029_leaf8_scout_scout_compressed`: `24` prediction events from `3` rows / `5` unique forms / `0` reconstruction errors.
  - `all_target_rows_later_compressed`: `4` prediction events from `638` rows / `21` unique forms / `0` reconstruction errors.
  - raw diagnostic contexts remain duplicate-sensitive: `all_target_rows_later_raw` has `3924` prediction events before guarding.
- guard catalog summary:
  - `33` guards preserve the compressed clean control.
  - `27` guards preserve the compressed clean control and reject the compressed false witness.
  - `0` guards produce a later compressed zero-false positive signal.
- strongest false-witness rejectors:
  - `term_gap_ge_3`: `24` clean-control true, `0` clean-control false, `0` primary later compressed predictions, `0` later raw false predictions.
  - `tail_width_ge_3`: same counts.
  - `group_salt_count_ge_3`: same counts.
  - `group_forms_ge_4_and_term_gap_ge_3`: same counts.
  - `group_q_ge_4_and_tail_width_ge_3`: same counts.
  - `term_gap_ge_3_q_delta_ge_500`: same counts.
- rejected compressed false witness:
  - public `[5678,559]`, window `12480_12487`;
  - family terms `[1,1,2,2]`, tail support `[2,3]`, term gap `1`, tail width `1`;
  - q/rhs pairs `(10421,5756)` and `(10747,2881)`;
  - predicted scalar `6242`, source secret `10788`, toy-secret verification `false`.
- preserved clean control:
  - public `[11476,7416]`, window `12440_12447`;
  - family terms `[8,8,11,11]`, tail support `[9,12]`, term gap `3`, tail width `3`;
  - predicted scalar `6678` across exact-tail/motif/terms-tail/gap-tail object models with zero false predictions.

## Interpretation
OBSERVATION / CONSISTENCY-FILTER RESULT: public structural guards can reject the P1036 compressed false witness while preserving the P1033/P1036 clean scout signal. The simplest useful guard is `term_gap_ge_3` or equivalently `tail_width_ge_3` for the current evidence.

This is not yet a new later relation-generation positive because the guard abstains on the later compressed relation supply. The next useful work is to generate or locate later q-diverse repeated two-tail groups satisfying term gap at least `3` / tail width at least `3`, then rerun the same strict factor-vector elimination.

## Next concrete action
Create P1038 as a guarded structural-family supply search: pre-register `term_gap_ge_3 OR tail_width_ge_3` as the public consistency guard, scan later/fresh row pools for same-public same-window q-diverse repeated two-tail groups satisfying the guard, and report whether any factor-matched predictions survive with zero false toy-secret checks.
