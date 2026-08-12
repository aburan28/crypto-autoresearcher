# Experiment Contract: P1072 P231 Top-k7 Split Validation

## Hypothesis
The P1071-expanded family `mode_low_term_support_total5/top7` supports a chronological two-stage descent: after the earliest top-k7 carrier removes column `14`, later top-k7 rows add a second independent direction and remove column `15` over the updated packet.

## Null hypothesis
The P1071 top-k7 family only looks good as an oracle full-family batch. Once the earliest column-`14` hit is promoted, later top-k7 rows either add no new rank, fail to remove column `15`, or require above-rho charge before any new direction appears.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- promoted packet: P1059 anchor, P1067 training carrier, and P1068 validation carrier
- frozen family: `selector=mode_low_term_support_total5`, `top_k=7`, `source=direct_source`
- stage-1 training carrier: earliest P1071 top-k7 single hit that removes any promoted-packet free column below rho
- validation split: top-k7 rows with window start greater than the stage-1 carrier window end
- target columns after stage 1: updated free columns, expected `[6,7,15]`

## Metrics
- stage-1 carrier charge, rank gain, and removed column
- validation case count and window count
- first validation prefix with marginal rank gain over stage 1
- first validation prefix that removes column `15`
- full validation-family marginal rank and free-column removals
- charge over rho for every promoted-prefix event

## Positive control
P1071 best single hit must reproduce column-`14` removal below one rho using `mode_low_term_support_total5/top7`.

## Negative control
The P1070/P1068 same-rowkey replay direction is not used for stage-2 validation; validation is only top-k7 rows after the stage-1 window.

## Success criterion
P1072 is positive if the frozen top-k7 validation split removes column `15` or adds marginal rank over the stage-1 packet below one rho.

## Falsification criterion
P1072 is negative if later top-k7 rows add no rank and remove no free columns over the stage-1 packet, even as a full validation batch.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1072_p231_topk7_split_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1072_p231_topk7_split_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1072_p231_topk7_split_validation_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `CHRONOLOGICAL-SPLIT`: stage-2 validation uses only windows after the stage-1 carrier.
- `SINGLE-TARGET`: current selected-source artifacts contain only `22050.cf1@11731`.
- `POLLARD-RHO-BOUNDARY`: a two-stage rank signal is not a complete faster-than-rho ECDLP algorithm.
- `TARGET-DESCENT-BOUNDARY`: even removing columns `[14,15]` still leaves `[6,7]` unresolved.

## Next concrete action after run
If positive below rho, freeze the two-stage packet and search for columns `[6,7]`. If only above-rho, build a public prefix/ordering compression for top-k7 column-`15` validation. If negative, the full-family P1071 rank gain was a non-chronological batch effect and needs a different source schedule.

## Results
- timestamp: `2026-06-30T08:50:48Z`
- claim: `OBSERVATION_P1072_TOPK7_STAGE2_EXISTS_ABOVE_RHO`
- frozen family: `mode_low_term_support_total5/top7`.
- stage-1 carrier: `20640_20647:20642`, row keys `[salt164,salt168]`, direct charge `0.78832117` rho, direct-public-key verified, marginal rank gain `1`, removed column `[14]`, remaining `[6,7,15]`.
- stage-1 below-rho candidates: `4`.
- validation split: `25` later top-k7 cases over `13` windows.
- first column-`15` validation prefix: length `8`, last case `20664_20671:20670`, marginal charge `6.07299272` rho, marginal rank gain `1`, removed column `[15]`, remaining `[6,7]`.
- full validation family: marginal charge `19.0145986` rho, marginal rank gain `1`, removed column `[15]`, remaining `[6,7]`.
- strict success below rho: `false`; weak source-supply success: `true`.
- interpretation: P1072 validates a chronological second-stage source direction for column `15`, but not an efficient below-rho order. The next problem is public prefix compression for the top-k7 validation split, not discovery of another pool.
- artifact: `ecdlp_index_calculus_state/low_term_total2_p1072_p231_topk7_split_validation_probe.json`

## Handoff: P1073 top-k7 ordering compression

### Claim or task
Find a public ordering over the P1072 validation refs that reaches the column-`15` carrier before one rho.

### Status
HYPOTHESIS

### Assumptions
- Ordering may use public row-key salts, transfer index, selected support, priority-hit count, and measured direct operation count.
- Ordering must not use rank gain, removed-column labels, direct-public-key verification, or scalar labels.
- Success remains same-target toy evidence until fresh-target artifacts exist.

### Evidence so far
- Chronological validation reaches column `15` only at prefix length `8`, charge `6.07299272` rho.
- The target prefix case `20664_20671:20670` has direct charge `0.7810219` rho, so below-rho compression is possible if a public order can place it first.

### Failure modes
- A policy may overfit P1072 validation if chosen after inspecting rank labels.
- Direct operation count may not be free in a real generator and must be charged honestly.
- A below-rho first hit still leaves `[6,7]` unresolved.

### Next concrete action
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1073_p231_topk7_order_compression.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1073_p231_topk7_order_compression.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1073_p231_topk7_order_compression_probe.json
```

### Artifact paths
- `ecdlp_index_calculus_state/experiment_contract_p1072_p231_topk7_split_validation.md`
- `tasks/ecdlp_index_calculus/low_term_total2_p1072_p231_topk7_split_validation.py`
- `ecdlp_index_calculus_state/low_term_total2_p1072_p231_topk7_split_validation_probe.json`
