# Experiment Contract: P1035 p231 leaf-8 exact-tail supply expansion

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: P1034 failed because the P1029 leaf `[8]` selected route was too sparse. Relaxing only the public row-selection route while keeping the P1033/P1034 exact-tail/motif target-prediction rule frozen may expose later same-public same-window eligible pairs.

## Null hypothesis
Even broader later-window row pools contain no eligible pair under the frozen exact-tail/motif rule. This is a relation-supply negative, not a false prediction or an algebraic disproof.

## Frozen target-prediction rule
- same public fingerprint;
- same window;
- exact-tail or motif object;
- terms exactly `[8,8,11,11]`;
- tail support exactly `[9,12]`;
- at least two forms with distinct q-coefficients;
- derive scalar by eliminating the shared local factor vector.

## Row-supply pools
- `p1029_leaf8_scout`: original P1029 scout predicate for exact leaf `[8]`.
- `leaf8_all_selectors`: any row whose `unique_leaf_indices` is exactly `[8]`.
- `contains_leaf8`: any row whose `unique_leaf_indices` contains `8`.
- `all_target_rows`: every target row in the later fresh windows.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scout/control window: `12440_12447`
- later validation windows: `12448_12455` through `12496_12503`
- source rank floor for expansion: `0`
- modulus/order: `11779`
- report both raw reconstructed forms and row-signature-compressed forms

## Metrics
- input row count per pool
- reconstruction error count
- form count and unique form count
- eligible frozen-policy form count
- object group count
- no-pair group count
- prediction count
- true/false toy-secret verification count
- scout-window control reproduction

## Positive control
At least one expanded pool must reproduce the P1033/P1034 scout-window signal on `12440_12447`: predicted scalar `6678`, zero false predictions.

## Negative control
No later-window result may use forms from `12440_12447`. If the later section contains scout-window forms, the run is invalid.

## Success criterion
Supply-expansion success requires at least one later-window eligible pair under the frozen rule. A stronger validation success requires at least one later-window prediction and zero false predictions.

## Falsification criterion
If any later-window prediction is false, the frozen exact-tail/motif rule is falsified for that row-supply pool. If no pool contains an eligible later-window pair, this is a scoped supply negative and the next step should broaden source generation or search adjacent exact-tail/motif families under a new contract.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1035_p231_leaf8_exact_tail_supply_expansion.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion_probe.json
```

## Interpretation boundary
This is an index-calculus relation-supply experiment. It does not change the target-prediction rule after seeing later windows. A supply negative does not prove the mechanism impossible; it identifies the next bottleneck as relation generation.

## Results
- timestamp: 2026-06-30T03:17:27Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion.py --contract ecdlp_index_calculus_state/experiment_contract_p1035_p231_leaf8_exact_tail_supply_expansion.md --out ecdlp_index_calculus_state/low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion_probe.json`
- claim: `NEGATIVE_RESULT_P1035_RELAXED_SUPPLY_NO_ELIGIBLE_PAIR`
- scout-window control:
  - `p1029_leaf8_scout`: `3` scout rows, `70` predictions, `70` true, `0` false.
  - broader scout pools are noisy: `leaf8_all_selectors` gives `76` true and `288` false; `contains_leaf8` and `all_target_rows` each give `108` true and `512` false. Therefore the original P1029 route remains the only clean scout control.
- later validation pools:
  - `p1029_leaf8_scout`: `1` later row, `4` eligible exact-tail/motif entries, `0` predictions.
  - `leaf8_all_selectors`: `192` later rows, `48` eligible entries, `0` predictions.
  - `contains_leaf8`: `282` later rows, `70` eligible entries, `0` predictions.
  - `all_target_rows`: `638` later rows, `66` eligible entries, `0` predictions.
- reason for no prediction:
  - later raw pools contain eligible same-public/same-window groups, but every such group has only one distinct q-coefficient.
  - examples include `leaf8_all_selectors` raw groups: `12472_12479` public `[1263,1661]`, `8` forms, q `[3914]`; `12456_12463` public `[1897,5063]`, `4` forms, q `[11108]`; `12448_12455` public `[8404,4042]`, `4` forms, q `[7053]`.
  - compressed pools reduce these to one form per group, also no pair.

## Interpretation
NEGATIVE RESULT / SUPPLY NEGATIVE: relaxing the row-selection route from the P1029 leaf `[8]` scout all the way to all target rows still does not produce a later same-public/same-window exact-tail or motif pair with distinct q-coefficients. The frozen target-prediction rule was not falsified by any wrong scalar; it simply had no later pair to evaluate.

This narrows the next engineering requirement: relation generation must create q-diversity inside the same exact-tail/motif object. More of the same selected rows is insufficient if each object group is single-q.

## Next concrete action
Create P1036 as an adjacent-family supply scout: keep the same-public same-window local-factor elimination method, but search nearby exact-tail/motif families such as terms `[9,9,11,11]` / tail `[10,12]`, tail gaps `[0,2]` or `[0,3]`, and repeated-term two-tail motifs for groups with at least two distinct q-coefficients. Score toy-secret prediction truth/false counts before proposing any frozen rule.
