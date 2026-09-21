# Experiment Contract: P1073 P231 Top-k7 Order Compression

## Hypothesis
A public ordering over the P1072 top-k7 validation split can reach the column-`15` carrier below one rho after the stage-1 column-`14` packet is promoted.

## Null hypothesis
Every tested public ordering still reaches column `15` only after at least one rho, or fails to reach it at all. The P1072 second-stage direction then remains a source-supply signal needing a better generator/order.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- baseline packet: P1072 stage-1 packet, which leaves free columns `[6,7,15]`
- candidate validation split: P1072 top-k7 validation cases after stage-1 window `20640_20647`
- target column: `15`
- policy catalog: chronological, transfer order, salt sum/min/max/span order, support-size order, priority-hit count, direct-op order, and small composite public-feature orders

## Metrics
- first prefix that removes column `15`
- charge over rho at first column-`15` prefix
- marginal rank gain at first prefix
- selected case count per policy
- full validation baseline for comparison

## Positive control
The chronological policy must reproduce P1072: first column-`15` removal at prefix length `8`, charge `6.07299272` rho.

## Negative control
No policy may use rank-gain labels, removed-column labels, direct-public-key verification, or scalar labels.

## Success criterion
P1073 is positive if any predeclared public ordering removes column `15` below one rho over the P1072 stage-1 packet.

## Falsification criterion
P1073 is negative if every tested public ordering either fails to remove column `15` or first removes it at charge `>= 1.0` rho.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1073_p231_topk7_order_compression.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1073_p231_topk7_order_compression.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1073_p231_topk7_order_compression_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `POLICY-CATALOG`: this tests a fixed local catalog, not an exhaustive search over all public orderings.
- `SINGLE-TARGET`: current selected-source artifacts contain only `22050.cf1@11731`.
- `POLLARD-RHO-BOUNDARY`: below-rho column-`15` prefixing still does not close target descent because `[6,7]` remain.
- `DIRECT-OPS-CAVEAT`: operation-count ordering is public after candidate materialization, but a full generator must charge any preordering cost.

## Next concrete action after run
If positive, freeze the winning policy and build P1074 to validate the two-stage `[14,15]` packet on a disjoint source block or fresh generated target artifacts. If negative, design a new generator for column `15` instead of reordering the current top-k7 split.

## Results
- timestamp: `2026-06-30T08:55:31Z`
- claim: `POSITIVE_SIGNAL_P1073_TOPK7_ORDER_COMPRESSES_COLUMN15_BELOW_RHO`
- policy catalog size: `18`; validation cases: `25`.
- winners below rho: `3` policies.
- best policy: `high_salt_max`, which is public and does not use direct-op ordering.
- best prefix: length `1`, case `20664_20671:20670`, row keys `[salt165,salt177]`, marginal charge `0.7810219` rho, marginal rank gain `1`, removed column `[15]`, remaining `[6,7]`.
- equivalent below-rho policies: `high_salt_span` and `high_salt_max_then_low_ops` also put the same case first at `0.7810219` rho.
- chronological P1072 control: first column-`15` prefix length `8`, charge `6.07299272` rho.
- interpretation: a simple public salt-maximum ordering compresses P1072's column-`15` second stage below rho. This creates a two-stage same-target packet removing columns `[14,15]`; columns `[6,7]`, fresh-target transfer, sparse-LA closure, and individual-log descent remain open.
- artifact: `ecdlp_index_calculus_state/low_term_total2_p1073_p231_topk7_order_compression_probe.json`

## Handoff: P1074 two-stage packet validation

### Claim or task
Freeze the P1073 two-stage policy and validate the `[14,15]` packet on a disjoint source block or newly generated target artifact.

### Status
HYPOTHESIS

### Assumptions
- Stage 1 uses the earliest top-k7 below-rho column-`14` carrier.
- Stage 2 uses `high_salt_max` over later top-k7 rows to remove column `15`.
- The current evidence is same-target and must not be promoted as fresh-target transfer.

### Evidence so far
- P1073 removes column `15` at `0.7810219` rho over the stage-1 packet.
- P1072 stage 1 removes column `14` at `0.78832117` rho over the P1069 promoted packet.
- After both stages, remaining free columns are `[6,7]`.

### Failure modes
- The salt-max ordering may be local to this same-target artifact block.
- A disjoint source block may not contain a high-salt-max carrier.
- Even if `[14,15]` validate, `[6,7]` may require a different source representation.

### Next concrete action
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1074_p231_two_stage_packet_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1074_p231_two_stage_packet_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1074_p231_two_stage_packet_validation_probe.json
```

### Artifact paths
- `ecdlp_index_calculus_state/experiment_contract_p1073_p231_topk7_order_compression.md`
- `tasks/ecdlp_index_calculus/low_term_total2_p1073_p231_topk7_order_compression.py`
- `ecdlp_index_calculus_state/low_term_total2_p1073_p231_topk7_order_compression_probe.json`
