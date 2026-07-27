# ECFG-P286 graph edge12 root-saved top-k7 diagnostic

Status: GRAPH EDGE12 ROOT-SAVED TOP-K7 STRICT DIAGNOSTIC POSITIVE ON `1696..1703` / CLEAN FROZEN `1704..1711` ABSTENTION / REPLAY-BACKED SHARED SELECTED-PRODUCT BELOW-RHO / TOP-K16 `1711` LOOKALIKE UNPROMOTED / TOY-EVIDENCE / OPERATION-LEDGER POLLARD-RHO COMPARISON / NOT A DEPLOYABLE FASTER-THAN-RHO SOLVER.

## Code change

- Added default-off strict guard `public_guard_lowterm10_topk7_root_saved_charge3_hit4_graph_edge12_first2`.
- The guard uses only public selected-leaf/product and graph-route features:
  low-term total10 top-k7, duplicate saved ops `5`, product saved ops `1`,
  unique selected-leaf signatures at least `5`, root-saved ops `1`, charge
  `3`, hit-root ops `4`, `first_match_count = 2`, and route-edge min/max
  `12/12`.
- It does not use replay rank, scalar derivation, public-key verification, or
  below-rho labels as holdout features.

## Diagnostic block: 1696..1703

- Fresh source: `frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1696_1703_probe.json`.
- Raw strict duplicate product: `14` public selections, `5` selected
  shared-product below-rho `22050` rows, `9` unverified selections, and zero
  verified-above-rho rows.
- P285 precision base and precision union both select zero rows:
  `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1696_1703_hash12hit5_precision_repaired_baseline_validation_no_low_prefix_probe.json`
  and
  `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1696_1703_hash12hit5_precision_repaired_plus_hash_top12_no_root_ops_floor_validation_no_low_prefix_probe.json`.
- Prior route-joined strict windows through `1695` score the graph guard at
  `2/2` verified below rho, zero unverified, and zero verified-above-rho.
- With prior thresholds enabled, the graph guard selects exactly one row:
  `22050@1697`, rows `salt165/salt175`, secret `3609`, direct
  `114/137 = 0.83211679x`, shared `108/137 = 0.78832117x`.

## Replay

Timing artifact:
`low_term_total2_fixed_leaf_shared_product_timing_22050_1697_graph_edge12_root_saved_topk7_diagnostic_probe.json`.

- Status: `TIMED_SHARED_PRODUCT_SCANNER_REPRODUCES_BELOW_RHO_LEDGER`.
- Public-key verification true.
- Shared-product cover matches direct selected cover.
- Shared ledger `108/137 = 0.78832117x` rho.
- Direct replay `114/137 = 0.83211679x` rho.
- Shared/direct scan wall speedup `1.08397019`.
- Shared/direct association wall speedup `1.2691096`.

The timing numbers are local replay timings.  The rho comparison remains the
operation ledger, not a calibrated asymptotic or deployed-curve speedup.

## Frozen validation: 1704..1711

- Fresh source: `frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1704_1711_probe.json`.
- Source summary: `20` leaf-verified cases, `10` leaf-below-rho cases, best
  leaf cost `0.75182482x` rho, `14` row-verified cases, and `2`
  row-below-rho cases.
- Frozen graph guard artifact:
  `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1704_1711_graph_edge12_root_saved_topk7_validation_no_low_prefix_probe.json`.
- Result: clean abstention with zero selected rows, zero unverified rows, and
  zero verified-above-rho rows.  Prior thresholds still pass with three prior
  below-rho windows and selected precision `1.0`.

## Unpromoted candidate

Raw `1704..1711` strict product has a replay-backed `22050@1711` low-term
top-k16 row, secret `9841`, shared `113/137 = 0.82481752x`.  The exact
graph-specific slice has no prior support, and the non-graph relaxation admits
the old unverified `1273` lookalike, so the top-k16 family is not promoted.

## Next step

Continue with fresh `1712..1719`.  Promote the top-k16 family only after it
gains prior/fresh support with zero selected unverified rows and zero
verified-above-rho rows.
