# ECFG-P283 hash top-k7 root-saved ops-floor diagnostic and 1640 validation

Status: HASH TOP-K7 ROOT-SAVED OPS-FLOOR DIAGNOSTIC POSITIVE ON `1632..1639` / CLEAN FRESH VALIDATION ON `1640..1647` BUT NO RECALL GAIN OVER BASELINE / TOP-K16 AND `67` GRAPH-ROUTE SEPARATORS NEGATIVE / REPLAY-BACKED SHARED SELECTED-PRODUCT BELOW-RHO / TOY-EVIDENCE / OPERATION-LEDGER POLLARD-RHO COMPARISON / NOT A DEPLOYABLE FASTER-THAN-RHO SOLVER.

## Code change

- Added `public_guard_hash_top7_root_saved_hit4_charge_le3_shared_ops_ge_0p75`.
- Added union guard `public_guard_topk4_or_hash12_hit5_or_hash_top7_ops_floor`.
- The new branch uses only public selector/top-k/shared-product metrics: hash selector, top-k<=7, root-saved ops>=1, hit-root ops>=4, charge<=3, and shared ledger ops/rho at least `0.75`.

## Diagnostic block: 1632..1639

- Source: `frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1632_1639_probe.json`.
- Diagnostic split: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1632_1639_hash_top7_ops_floor_diagnostic_no_low_prefix_probe.json`.
- Result: `SPLIT_PUBLIC_GATE_POSITIVE`.
- Selected route cases: `1`.
- Selected below rho: `1`.
- Selected unverified: `0`.
- Selected verified above rho: `0`.
- Selected case: `22050@1638`, `mode_hash_leaf_total6`, top-k `7`, secret `3949`, direct `108/137 = 0.78832117x`, shared `104/137 = 0.75912409x`.
- Timing replay: `low_term_total2_fixed_leaf_shared_product_timing_22050_1638_hash_topk7_hash_top7_ops_floor_diagnostic_probe.json`; direct-cover match true and public-key verification true.

## Fresh validation block: 1640..1647

- Source: `frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1640_1647_probe.json`.
- Source summary: `10` leaf-verified cases, `8` leaf-below-rho cases, best leaf ops/rho `0.72262774`, `9` row-verified cases, `1` row-below-rho case.
- Raw strict: `8` selected, `1` verified below rho, `1` verified above rho, `6` false positives.
- Raw density: `27` selected, `8` verified below rho, `2` verified above rho, `17` false positives.
- Raw `67` low-prefix: `2` selected, both unverified, so low-prefix remains disabled.

## Split comparison

- Baseline: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1640_1647_hash12hit5_strict_hit7_or_saved2_baseline_no_low_prefix_probe.json`.
- P282 union: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1640_1647_hash_top7_no_root_ops_floor_validation_no_low_prefix_probe.json`.
- P283 union: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1640_1647_hash_top7_ops_floor_validation_no_low_prefix_probe.json`.
- All three splits selected `3` route cases, all verified below rho, with zero unverified and zero verified-above-rho rows.
- Distinct selected scalars:
  - `22050@1640`, `mode_hash_leaf_total6`, top-k `7`, secret `3847`, shared `112/137 = 0.81751825x`.
  - `67@1645`, `mode_hash_leaf_total6`/hybrid top-k `4`, secret `9792`, best shared `116/125 = 0.928x`.
- Conclusion: the new branch is clean on fresh data but does not improve recall over the old/P282 selector.

## Graph-route negatives

- `22050@1641`, `mode_low_term_span_total10`, top-k `16`, secret `11680`, shared `106/137 = 0.77372263x`, is replay-backed but unpromoted.  Its compact graph-route signature matches prior unverified low-term top-k16 rows.
- `67@1646`, `mode_hybrid_support_monic_b_total6`, top-k `7`, secret `1323`, shared `0.96x`, is replay-backed but unpromoted.  The matching public shape has prior unverified density lookalikes.

## Next step

Continue with fresh `1648..1655`.  Promote only a branch that adds distinct fresh recall over the baseline with zero selected unverified rows and zero verified-above-rho rows.
