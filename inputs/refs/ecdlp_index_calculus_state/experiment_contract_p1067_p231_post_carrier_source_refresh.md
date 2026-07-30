# Experiment Contract: P1067 P231 Post-Carrier Source Refresh

## Hypothesis
The P1066 failure is caused by the P1054 gate being too narrow after the P1065 carrier. If we refresh the source surface by admitting all post-carrier joined source rows, not only P1054-selected rows, a public ordering can find another column-`10` rank direction below one rho.

## Null hypothesis
Rows outside the P1054 gate do not add target-eliminated rank over the P1059 anchor, or any rank-bearing case appears only after broad above-rho spend.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- base packet: exact P1059 row-key prefix on window `18464_18471`
- excluded carrier: P1065 rank-bearing case window `20456_20463`, transfer `20457`
- refreshed holdout split: all joined forward-validation rows with source cases and window start greater than `20463`, regardless of the P1054 selected rule
- P1054-only control: P1066's post-carrier selected rows `[20520_20527,20608_20615,20648_20655]`
- target column: free column `10`
- public policies: chronological, `high_mean_then_transfer`, `latest_window_then_transfer`, `low_min_salt_then_transfer`, `low_salt_sum_then_transfer`

## Metrics
- number of refreshed post-carrier windows and cases
- number of refreshed rows excluded by P1054
- per-case marginal rank gain and removed free columns over the P1059 anchor
- first prefix under each public policy that removes column `10`
- marginal direct-source charge over the P1059 anchor
- whether the first rank-bearing case is outside P1054

## Positive control
P1065 must still identify `20456_20463:20457` as a below-rho carrier, and P1066 must remain negative on the P1054-only post-carrier control.

## Negative control
The P1054-only post-carrier control must have `0` rank-bearing single cases and `0` column-`10` removals.

## Success criterion
P1067 is positive if the refreshed post-carrier row surface contains a non-P1054 rank-bearing case that removes column `10` below one rho under a public policy.

## Falsification criterion
P1067 is negative if all refreshed post-carrier rows leave the P1059 anchor free columns unchanged, or if the first column-`10` removal under every public policy costs at least one rho.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1067_p231_post_carrier_source_refresh.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1067_p231_post_carrier_source_refresh.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `SOURCE-REFRESH`: this changes the source row admission surface after P1066; it is not an independent fresh target.
- `P1054-GATE-BOUNDARY`: this tests whether P1054 excluded useful rows after the carrier.
- `POLLARD-RHO-BOUNDARY`: a below-rho marginal rank packet is not a complete ECDLP algorithm.
- `TARGET-DESCENT-BOUNDARY`: removing column `10` is rank pressure, not individual-log descent.

## Results
- timestamp: `2026-06-30T08:08:59Z`
- claim: `POSITIVE_SIGNAL_P1067_SOURCE_REFRESH_NON_P1054_BELOW_RHO_COLUMN10`
- refreshed surface: `27` post-carrier windows with source cases, `88` candidate cases, window range `[20464_20471,20800_20807]`.
- P1054 control: `3` P1054-selected holdout windows and `0` P1054 rank-bearing cases, matching the P1066 negative boundary.
- source-refresh signal: `2` non-P1054 rank-bearing single cases, both below rho and both removing free column `[10]`.
- best case: `20464_20471:20465` with row keys `[22050.cf1@11731:uniform:256:salt163, 22050.cf1@11731:uniform:256:salt174]`, direct charge `0.71532847` rho, marginal rank gain `1`, removed free column `[10]`, and remaining free columns `[6,7,14,15]`.
- second case: `20632_20639:20636` with the same row keys, direct charge `0.75182482` rho, marginal rank gain `1`, and removed free column `[10]`.
- public policy result: chronological ordering reaches the best case at prefix length `1` with marginal charge `0.71532847` rho. `high_mean_then_transfer`, `latest_window_then_transfer`, `low_min_salt_then_transfer`, and `low_salt_sum_then_transfer` all find a rank carrier only after above-rho prefixes; their de-duplicated marginal charges are `19.81751832`, `38.35766439`, `7.14598543`, and `24.2919709` rho respectively.
- interpretation: P1067 shows the P1066 failure was a gate/admission failure, not absence of later rank carriers in the source bank. This is a same-target source-refresh positive, not a fresh-target validation or target descent.
- artifact: `ecdlp_index_calculus_state/low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json`

## Next concrete action
Build P1068 as a frozen gate-repair validation: learn a public rule that admits the refreshed rank-bearing row while rejecting broad noisy rows, then test on later windows or a fresh same-family target.
