# Experiment Contract: P1036 p231 adjacent-family supply scout

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: P1035 failed because the exact frozen family had no later same-public same-window q-diverse pair. Searching adjacent repeated two-tail exact-tail/motif families while keeping the same local-factor elimination rule may expose q-diverse target-prediction pairs.

## Null hypothesis
Adjacent repeated two-tail families either have no q-diverse same-public same-window groups or have q-diverse groups whose factor vectors do not match. This is a scoped relation-supply negative, not a disproof of index calculus.

## Candidate rule
- use only `fresh_validation` forms;
- require repeated two-tail form shape: terms `[a,a,b,b]` with `a != b` and exactly two tail-support indices;
- group by same public fingerprint and same window;
- test object families:
  - exact tail expression;
  - normalized motif key;
  - exact terms plus tail support;
  - shifted gap-tail shape;
- require at least two distinct q-coefficients;
- derive a target scalar only by eliminating an exactly shared local factor vector.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scout/control window: `12440_12447`
- later validation windows: `12448_12455` through `12496_12503`
- source rank floor for expansion: `0`
- modulus/order: `11779`
- row pools: `p1029_leaf8_scout`, `leaf8_all_selectors`, `contains_leaf8`, and `all_target_rows`
- report both raw reconstructed forms and row-signature-compressed forms

## Metrics
- input row count per pool
- reconstruction error count
- repeated two-tail eligible form count
- same-public same-window object group count
- q-diverse group count
- factor-matched prediction count
- true/false toy-secret verification count
- most frequent q-diverse family descriptors

## Positive control
The scout-window section should recover at least one clean P1033/P1034-style same-window target-prediction group under the exact-tail or motif model, with zero false predictions for the original leaf-8 scout route.

## Negative control
Later-window results must not include forms from `12440_12447`. Broad scout pools are allowed to be noisy diagnostics, but they cannot be promoted as frozen rules unless a later-window zero-false rule appears.

## Success criterion
Scout success requires at least one later-window factor-matched prediction with zero false toy-secret checks in an adjacent repeated two-tail family.

## Falsification criterion
If a later-window factor-matched prediction is false, that adjacent object family is rejected for this rule. If no later q-diverse group exists, the bottleneck remains q-diverse relation generation. If q-diverse groups exist but no factor-matched pair exists, the next bottleneck is local-factor compatibility rather than row supply.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1036_p231_adjacent_family_supply_scout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1036_p231_adjacent_family_supply_scout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1036_p231_adjacent_family_supply_scout_probe.json
```

## Interpretation boundary
This is an index-calculus relation-generation scout. It may find a viable component route toward relation collection, but it is not by itself a complete faster-than-rho ECDLP algorithm. Pollard rho remains the one-target scalar-search baseline.

## Results
- timestamp: 2026-06-30T03:27:04Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1036_p231_adjacent_family_supply_scout.py --contract ecdlp_index_calculus_state/experiment_contract_p1036_p231_adjacent_family_supply_scout.md --out ecdlp_index_calculus_state/low_term_total2_p1036_p231_adjacent_family_supply_scout_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1036_p231_adjacent_family_supply_scout_probe.json`
- claim: `NEGATIVE_RESULT_P1036_ADJACENT_FAMILY_FALSE_PREDICTION`
- scout-window control:
  - `p1029_leaf8_scout`: `3` rows, `140` strict factor-matched predictions, `140` true, `0` false.
  - broader scout pools are noisy, so they remain diagnostics only: `leaf8_all_selectors` has `152` true / `576` false; `contains_leaf8` and `all_target_rows` have `216` true / `1024` false.
- later validation, raw forms:
  - `p1029_leaf8_scout`: `8` eligible entries, `0` q-diverse groups, `0` predictions.
  - `leaf8_all_selectors`: `176` eligible entries, `0` q-diverse groups, `0` predictions.
  - `contains_leaf8`: `604` eligible entries, `36` q-diverse groups, `556` predictions, `144` true, `412` false.
  - `all_target_rows`: `1588` eligible entries, `54` q-diverse groups, `3924` predictions, `752` true, `3172` false.
- later validation, compressed forms:
  - `p1029_leaf8_scout`: `8` eligible entries, `0` q-diverse groups, `0` predictions.
  - `leaf8_all_selectors`: `36` eligible entries, `0` q-diverse groups, `0` predictions.
  - `contains_leaf8`: `36` eligible entries, `0` q-diverse groups, `0` predictions.
  - `all_target_rows`: `84` eligible entries, `4` q-diverse groups, `4` predictions, `0` true, `4` false.
- compressed false witness:
  - public `[5678,559]`, window `12480_12487`;
  - family terms `[1,1,2,2]`, tail support `[2,3]`, motif gaps `[0,0,1,1]` / `[0,1]`;
  - q/rhs pairs `(10421,5756)` and `(10747,2881)`;
  - predicted scalar `6242`, source secret `10788`, toy-secret verification `false`.

## Interpretation
NEGATIVE RESULT / ADJACENT-FAMILY FALSE-PREDICTION: relaxing from the frozen leaf-8 exact-tail rule to all repeated two-tail adjacent families creates q-diverse same-public same-window supply, but the naive local-factor elimination rule is not scalar-stable. The failure survives row-signature compression, so it is not only duplicate inflation.

This does not close the index-calculus route. It identifies the missing condition: an additional public consistency guard is required before a repeated two-tail q-diverse object can be used as a target-prediction relation.

## Next concrete action
Create P1037 as a public consistency-guard scout over the P1036 q-diverse groups. Candidate guards should include same row-key/salt class, RHS-ratio or q-ratio congruence, public-coordinate residue, exact factor-vector multiplicity, and leave-one-window validation. Success requires preserving the P1033 clean scout signal while rejecting the P1036 compressed false witness before testing a new later holdout.
