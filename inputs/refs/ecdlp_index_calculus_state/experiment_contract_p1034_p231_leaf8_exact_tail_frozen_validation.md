# Experiment Contract: P1034 p231 leaf-8 exact-tail frozen validation

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1033 leaf `[8]` same-window fresh exact-tail/motif target-prediction signal repeats on later disjoint fresh windows when the policy is frozen.

## Null hypothesis
Later fresh windows either produce no eligible exact-tail/motif pair or produce predictions that fail toy-secret verification. No eligible-pair result is a relation-supply negative, not an algebraic disproof of the mechanism.

## Frozen policy
- leaf selector: P1029 leaf `[8]` scope
- split: `fresh_validation`
- validation windows: fresh windows strictly after `12440_12447`
- same public fingerprint
- same window
- exact-tail or motif object
- terms exactly `[8,8,11,11]`
- tail support exactly `[9,12]`
- at least two forms with distinct target coefficient `q`
- derive scalar by eliminating the shared local factor vector

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source/scout window: `12440_12447`
- validation windows: `12448_12455` through `12496_12503`
- modulus/order: `11779`
- forms: both raw reconstructed selected forms and row-signature-compressed unique forms are reported

## Metrics
- eligible form count
- eligible object group count
- prediction count
- true/false toy-secret verification counts
- no-pair opportunity count
- scout-window positive-control count

## Positive control
On the scout window `12440_12447`, the frozen exact-tail/motif policy should reproduce the P1033 signal: six pairwise predictions, all scalar `6678`, all toy-secret verified.

## Negative control
The later validation should not use forms from `12440_12447`. If the validation artifact contains signal-window predictions in the validation section, the run is invalid.

## Success criterion
Validation success requires at least one later-window prediction and zero false toy-secret verifications under the frozen policy.

## Falsification criterion
If later windows contain eligible pairs and any prediction is false, the frozen policy is falsified for this selected-data regime. If later windows contain no eligible pairs, this is a supply negative: the policy remains unvalidated and the next action is to broaden relation supply or scan more disjoint windows before judging the mechanism.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1034_p231_leaf8_exact_tail_frozen_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation_probe.json
```

## Interpretation boundary
This is a frozen validation of a toy index-calculus precursor. A supply negative does not disprove the mechanism; it says the current leaf `[8]` selected relation supply is too sparse after the scout window to validate it. Pollard rho remains the one-target baseline.

## Results
- timestamp: 2026-06-30T03:10:19Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation.py --contract ecdlp_index_calculus_state/experiment_contract_p1034_p231_leaf8_exact_tail_frozen_validation.md --out ecdlp_index_calculus_state/low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation_probe.json`
- claim: `NEGATIVE_RESULT_P1034_NO_LATER_ELIGIBLE_PAIR`
- scout-window positive control:
  - raw reconstructed forms in `12440_12447`: `18` eligible exact-tail/motif form entries, `58` predictions, `58` true, `0` false.
  - row-signature-compressed forms in `12440_12447`: `8` eligible exact-tail/motif form entries, `12` predictions, `12` true, `0` false.
  - compressed exact-tail alone reproduces the P1033 signal: `4` forms, `6` pairwise predictions, all predict scalar `6678`, all toy-secret verified.
- later frozen validation windows:
  - windows tested: `12448_12455`, `12456_12463`, `12464_12471`, `12472_12479`, `12480_12487`, `12488_12495`, `12496_12503`.
  - raw forms: `2` eligible object entries total, `2` groups, `2` no-pair groups, `0` predictions.
  - compressed forms: `2` eligible object entries total, `2` groups, `2` no-pair groups, `0` predictions.
  - the only later eligible frozen-policy form is in `12448_12455`, public `[7746,5675]`, q `7053`, rhs `7929`; it has no same-public/same-window exact-tail or motif partner.

## Interpretation
NEGATIVE RESULT / SUPPLY NEGATIVE: the frozen same-window fresh exact-tail/motif policy was not falsified by a wrong scalar; it simply had no later eligible pair to score. This preserves the P1033 mechanism as an open index-calculus precursor but shows that the current P1029 leaf `[8]` selected relation supply is too sparse after the scout window.

## Next concrete action
Create P1035 as a relation-supply expansion for the frozen exact-tail/motif policy: relax only the public row-selection route, not the exact-tail/motif target-prediction rule, to search later windows for at least two same-public same-window forms with terms `[8,8,11,11]`, tail support `[9,12]`, and distinct q-coefficients.
