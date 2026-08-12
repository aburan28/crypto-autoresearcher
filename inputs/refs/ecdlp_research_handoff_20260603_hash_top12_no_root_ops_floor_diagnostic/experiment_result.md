# ECFG-P284 hash top-k12 no-root ops-floor diagnostic

Status: HASH TOP-K12 NO-ROOT OPS-FLOOR DIAGNOSTIC POSITIVE ON `1648..1655` / CLEAN VALIDATION ABSTENTION ON `1656..1663` / CLEAN `1664..1671` VALIDATION BUT NO RECALL GAIN OVER BASELINE / REPLAY-BACKED SHARED SELECTED-PRODUCT BELOW-RHO / TOY-EVIDENCE / OPERATION-LEDGER POLLARD-RHO COMPARISON / NOT A DEPLOYABLE FASTER-THAN-RHO SOLVER.

## Code change

- Added `public_guard_hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75`.
- Added union guard `public_guard_topk4_or_hash12_hit5_or_hash_top12_ops_floor`.
- The branch uses only public selected-product features: hash selector, top-k<=12, hit-root ops>=3, charge `3`, root-saved ops `0`, unique selected-leaf signatures `3`, and shared ledger ops/rho at least `0.75`.

## Prior support before 1648..1655

- Prior branch support: `2` selected, `2` verified below rho, `0` unverified, `0` verified above rho.
- Prior selected rows: `22050@1192` and `22050@1623`.

## Diagnostic block: 1648..1655

- Source: `frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_1648_1655_probe.json`.
- Baseline/P282/P283 split selectors all abstain.
- New split: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1648_1655_hash_top12_ops_floor_diagnostic_no_low_prefix_probe.json`.
- Result: `SPLIT_PUBLIC_GATE_POSITIVE`.
- Selected route cases: `1`.
- Selected below rho: `1`.
- Selected unverified: `0`.
- Selected verified above rho: `0`.
- Selected case: `22050@1655`, `mode_hash_leaf_total6`, top-k `12`, secret `2449`, direct `109/137 = 0.79562044x`, shared `105/137 = 0.76642336x`.
- Replay: `low_term_total2_fixed_leaf_shared_product_timing_22050_1655_hash_topk12_hash_top12_ops_floor_diagnostic_probe.json`; direct-cover match true and public-key verification true.

## Validation blocks

- `1656..1663`: baseline, P283, and the top-k12 union all abstained cleanly with zero selected unverified and zero verified-above-rho rows.
- `1664..1671`: baseline, P283, and the top-k12 union each selected `11` route cases, all verified below rho, with zero selected unverified and zero verified-above-rho rows.  All selected rows were already caught by existing top-k4/strict branches, so the top-k12 branch did not add fresh recall.

## Next step

Continue with fresh `1672..1679`.  Promote the top-k12 branch only after it adds distinct fresh recall beyond baseline with zero selected unverified rows and zero verified-above-rho rows.
