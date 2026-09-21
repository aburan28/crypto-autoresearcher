# Experiment Contract: P1068 P231 Gate-Repair Holdout

## Hypothesis
The P1067 source-refresh positive can be converted into a public gate repair: from the first non-P1054 column-`10` carrier, derive a rule that keeps P1054-excluded cases with the same public row-key/salt-pair signature, then validate it on later refreshed rows without verifier or rank labels.

## Null hypothesis
The P1067 carriers are not predictable by a public gate repair. Exact row-key or salt-pair replay either needs P1054-included false positives first, costs at least one rho before rank gain, or fails to recover a later column-`10` carrier.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- base packet: exact P1059 row-key prefix on window `18464_18471`
- training carrier: P1067 first refreshed carrier `20464_20471:20465`
- validation split: refreshed post-carrier rows with window start greater than `20471`
- target column: free column `10`
- public rule candidates:
  - `exact_rowkeys`
  - `p1054_excluded_and_exact_rowkeys`
  - `p1054_excluded_and_salt_min_max`
  - `p1054_excluded_and_salt_sum`
  - broad `p1054_excluded` chronological control

## Metrics
- selected validation cases per rule
- first prefix that removes free column `10`
- marginal direct-source charge over the P1059 anchor
- marginal target-eliminated rank gain over the P1059 anchor
- whether the first successful validation case is P1054-excluded

## Positive control
P1067 must identify `20464_20471:20465` as a below-rho non-P1054 carrier with marginal charge `0.71532847` rho.

## Negative control
The plain `exact_rowkeys` replay is expected to include the P1054-selected false-positive case in `20520_20527` before the later carrier; if this costs above rho, the P1054-exclusion term is justified.

## Success criterion
P1068 is positive if a P1054-excluded public rule derived from the first carrier removes column `10` on later validation rows below one rho, with no verifier/certificate/rank label in the rule.

## Falsification criterion
P1068 is negative if all P1054-excluded public rules fail to remove column `10`, or if their first column-removal prefix costs at least one rho.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1068_p231_gate_repair_holdout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1068_p231_gate_repair_holdout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1068_p231_gate_repair_holdout_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `SAME-TARGET-HOLDOUT`: validation is later same-target source rows, not a fresh target.
- `PUBLIC-GATE-REPAIR`: the rule may use P1054's public admission decision and public row-key/salt-pair features, but not verifier or rank labels.
- `POLLARD-RHO-BOUNDARY`: a below-rho marginal rank packet is not a complete ECDLP algorithm.
- `TARGET-DESCENT-BOUNDARY`: removing column `10` is rank pressure, not individual-log descent.

## Results
- timestamp: `2026-06-30T08:14:47Z`
- claim: `POSITIVE_SIGNAL_P1068_GATE_REPAIR_HOLDOUT_BELOW_RHO`
- training case: `20464_20471:20465`, direct charge `0.71532847` rho, row keys `[22050.cf1@11731:uniform:256:salt163, 22050.cf1@11731:uniform:256:salt174]`, P1054-excluded.
- validation split: `26` later refreshed windows, `85` validation cases, `1` validation rank-bearing single case.
- negative control: plain `exact_rowkeys` selects `3` validation cases and reaches column `10` only at prefix length `2`, marginal charge `1.43795621` rho, because it includes a P1054-selected false positive before the carrier.
- repaired gate: `p1054_excluded AND exact_rowkeys` selects `2` validation cases and reaches column `10` at prefix length `1`, marginal charge `0.75182482` rho.
- equivalent salt-pair gate: `p1054_excluded AND salt_min == 163 AND salt_max == 174` also reaches column `10` at prefix length `1`, marginal charge `0.75182482` rho.
- weaker controls: `p1054_excluded AND salt_sum == 337` reaches column `10` at prefix length `3`, charge `2.23357665` rho; broad `p1054_excluded` reaches at prefix length `26`, charge `18.59124095` rho.
- interpretation: P1068 converts P1067 from a source-refresh observation into a public same-target holdout gate repair. The P1054 exclusion term is doing real work by skipping a row-key false positive; the result remains a marginal rank packet, not target descent or a fresh-target transfer.
- artifact: `ecdlp_index_calculus_state/low_term_total2_p1068_p231_gate_repair_holdout_probe.json`

## Next concrete action
Build P1069 as a fresh-target or later-window transfer of the frozen `p1054_excluded AND exact_rowkeys` / salt-pair gate and attach target-descent accounting.
