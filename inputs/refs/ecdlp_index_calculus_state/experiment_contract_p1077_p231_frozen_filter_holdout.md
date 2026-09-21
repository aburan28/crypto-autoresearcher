# Experiment Contract: P1077 P231 Frozen Filter Holdout

## Hypothesis
The P1076 public diagnostic filters identify a reusable source-shape, not only the known carrier `20696_20703:20701`. When frozen and applied to held-out validation windows excluding known positives, at least one filter should expose a new below-rho target-descent direction for column `15`, `6`, or `7`.

## Null hypothesis
The P1076 filters are local to the known blocker/carrier contrast. After excluding known positive windows `20664_20671` and `20696_20703`, the frozen filters produce no new marginal rank gain or free-column removal.

## Parameters
- field/curve family: toy prime-field ECDLP audit, target `22050.cf1@11731`, group order `11779`
- surface: P1072 top-k7 validation refs after stage-1, excluding windows `20664_20671` and `20696_20703`
- frozen filters: P1076 diagnostic filters over public salts, offsets, direct charge, and row-key tokens
- ordering: P1075 best route `window_max_direct_ops_asc__chronological`
- baseline: generic rho one normalized budget; P1076 known carrier-only charge `0.75182482` rho is excluded

## Metrics
- group operations: normalized source charge over rho
- field operations: inherited from selected-source certificates
- memory: held-out refs, windows, filter count
- relation probability: number of filters with first rank/column prefix
- rank: marginal rank gain over the P1072 stage-1 packet
- solver degree: not tested
- wall-clock: secondary

## Positive control
P1076 already established that the frozen filters route the known carrier below rho when `20696_20703` is included. P1077 excludes that window and treats it as unavailable.

## Negative control
If a filter selects held-out rows but all final marginal rank gains are zero and no free columns are removed, the filter is local rather than reusable.

## Success criterion
P1077 is positive if any frozen filter reaches a marginal rank gain or removes one of `[6,7,15]` below one rho on held-out windows excluding both known positives.

## Falsification criterion
P1077 is negative if every frozen filter has no first rank-gain prefix, no first column-`15` prefix, and final marginal rank gain `0` on the held-out surface.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1077_p231_frozen_filter_holdout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1077_p231_frozen_filter_holdout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1077_p231_frozen_filter_holdout_probe.json
```

## Claim status taxonomy
- `HYPOTHESIS`: frozen-filter holdout validation.
- `MODEL-BOUND`: toy p231/order-`11779` target-eliminated rank model.
- `TOY-EVIDENCE`: no cryptographic-scale claim.
- `NEGATIVE RESULT`: if filters fail on held-out windows.
- `TARGET-DESCENT-OPEN`: columns `[6,7]` remain open unless a held-out filter removes them.

## Results
- claim: `NEGATIVE_RESULT_P1077_FROZEN_FILTERS_NO_HELDOUT_DIRECTION`
- strict success: `false`
- filters tested: `9`
- below-rho winners: `0`
- excluded known-positive windows: `20664_20671`, `20696_20703`
- held-out surface: `22` cases across `11` windows
- outcome: every frozen filter has no first rank-gain prefix, no first column-`15` prefix, and final marginal rank gain `0`

## Interpretation
The P1076 diagnostic filters are local to the known blocker/carrier contrast. They should not be promoted as reusable public routing rules. The next useful move is to stop sorting this exhausted top-k7 column-`15` surface and instead search for a new source family or a different target-descent direction for `[6,7]`.

## Handoff: P1078 remaining-column source-family pivot

### Claim or task
Search for a new public source family or target-descent representation that can touch remaining columns `[6,7]` after the P1073/P1074 column-`15` line is exhausted.

### Status
OPEN

### Assumptions
- Toy p231/order-`11779` target-eliminated rank model.
- The current `mode_low_term_support_total5/top7` validation surface has no reusable held-out direction after known positives are removed.
- Fresh target artifacts remain unavailable in this selected-source branch.

### Evidence so far
- P1073 gives a same-target below-rho column-`15` packet.
- P1074/P1075/P1076/P1077 show disjoint routing is not validated and P1076 filters do not generalize.

### Failure modes
- Another selector/top-k family may replay column `15` rather than touch `[6,7]`.
- A row family may add rank but not remove remaining free columns.
- A successful same-target row may still fail fresh-target transfer.

### Next concrete action
Run a P1078 selector/top-k family pivot over the P1071 expanded source inventory, scoring first below-rho marginal removal of `[6,7]` over the P1073/P1074 packet and treating column `15` replay as a negative control.

### Artifact paths
- `ecdlp_index_calculus_state/low_term_total2_p1077_p231_frozen_filter_holdout_probe.json`
