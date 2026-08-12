# Experiment Contract: P1065 P231 Relaxed High-Mean Early-Stop Compression

## Hypothesis
The P1064 relaxed high-mean source-construction band contains a small number of rank-bearing cases, and a public early-stop ordering can reach the column-`10` rank direction below one rho without spending the full `6.79562046` rho marginal relaxed-band cost.

## Null hypothesis
The P1064 relaxed-band column-`10` improvement is only visible after summing many selected cases or after using verifier/certificate oracle information. Under public ordering, the first prefix that removes column `10` still costs at least one rho.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- base packet: exact P1059 row-key prefix on window `18464_18471`
- candidate band: P1064 relaxed rule `mean_ops >= 0.75912409` on validation windows after cutoff `18023`
- target column: free column `10`
- public prefix policies: chronological, high-mean-then-transfer, latest-window-then-transfer, low-min-salt-then-transfer, low-salt-sum-then-transfer
- diagnostic oracle policies: verifier/certificate-bearing-first; these are boundaries, not algorithms

## Metrics
- marginal direct-source charge over the P1059 anchor
- marginal target-eliminated rank gain over the P1059 anchor
- first prefix that removes free column `10`
- per-case single-addition rank effect
- usable source-certificate count over the anchor
- remaining free columns after the first successful prefix

## Positive control
The full P1064 relaxed band must reproduce marginal charge `6.79562046` rho, marginal rank gain `1`, and removed free column `[10]`.

## Negative control
The exact P1063 threshold `mean_ops >= 0.78345499` must remain a no-transfer control on the validation split, with marginal rank gain `0`.

## Success criterion
P1065 is an exploratory positive if at least one public prefix policy removes column `10` with marginal charge below one rho. It is a diagnostic-only positive if only verifier/certificate-oracle ordering reaches below one rho.

## Falsification criterion
P1065 is negative if no public prefix policy removes column `10` below one rho and no individual selected case adds the missing rank direction.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1065_p231_relaxed_high_mean_early_stop.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1065_p231_relaxed_high_mean_early_stop.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1065_p231_relaxed_high_mean_early_stop_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `EXPLORATORY-POLICY-FAMILY`: the public ordering policies are tested after P1064 exposed the relaxed high-mean band; P1066 must freeze and test on a fresh split.
- `NO-VERIFIER-LABEL-PROMOTION`: verifier/certificate-bearing policies are reported only as diagnostic lower bounds.
- `POLLARD-RHO-BOUNDARY`: a below-rho marginal rank packet is not a complete ECDLP algorithm.
- `TARGET-DESCENT-BOUNDARY`: removing column `10` is rank pressure, not individual-log descent.

## Results
- timestamp: `2026-06-30T08:02:07Z`
- claim: `POSITIVE_SIGNAL_P1065_EXPLORATORY_PUBLIC_EARLY_STOP_BELOW_RHO_REQUIRES_HOLDOUT`
- record counts: `9` non-anchor candidate cases from `17` validation windows; `1` single candidate is rank-bearing over the P1059 anchor.
- positive control: the full P1064 relaxed band reproduced marginal charge `6.79562046` rho, marginal rank gain `1`, and removed free column `[10]`.
- negative control: the exact P1063 transfer control retained marginal rank gain `0`.
- rank-bearing case: `20456_20463:20457` with row keys `[22050.cf1@11731:uniform:256:salt162, 22050.cf1@11731:uniform:256:salt168]`, direct charge `0.79562044` rho, marginal rank gain `1`, removed free column `[10]`, and remaining free columns `[6,7,14,15]`.
- public prefix policies below rho: `high_mean_then_transfer`, `latest_window_then_transfer`, and `low_min_salt_then_transfer` each reach the rank-bearing case at prefix length `1` with marginal charge `0.79562044` rho.
- public prefix policies above rho or weaker: chronological ordering reaches the same case only at prefix length `6` with marginal charge `4.51824819` rho; `low_salt_sum_then_transfer` reaches it at prefix length `2` with marginal charge `1.59124088` rho.
- diagnostic oracle boundary: verifier-first and certificate-oracle orderings also reach the same case at `0.79562044` rho, but these labels are not promoted as public selectors.
- interpretation: P1065 compresses the P1064 column-`10` marginal cost from `6.79562046` rho to `0.79562044` rho under exploratory public orderings. This is a below-rho marginal rank packet and a viable next index-calculus direction, not a complete ECDLP algorithm or target descent.
- artifact: `ecdlp_index_calculus_state/low_term_total2_p1065_p231_relaxed_high_mean_early_stop_probe.json`

## Next concrete action
Build P1066 as a fresh-holdout validation of the P1065 public early-stop policy: freeze `high_mean_then_transfer` and the tie controls `latest_window_then_transfer` / `low_min_salt_then_transfer`, test on later high-mean windows or a fresh target, and require column-removal rank gain without verifier/certificate labels.
