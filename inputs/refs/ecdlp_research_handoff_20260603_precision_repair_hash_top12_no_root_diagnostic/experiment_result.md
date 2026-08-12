# ECFG-P285 precision repair and hash top-k12 no-root diagnostic

Status: ROOT-SAVED BASELINE PRECISION REPAIR POSITIVE / HASH TOP-K12 NO-ROOT OPS-FLOOR DIAGNOSTIC RECALL GAIN ON `1680..1687` / CLEAN FRESH `1688..1695` VALIDATION BUT NO RECALL GAIN OVER PRECISION BASELINE / REPLAY-BACKED SHARED SELECTED-PRODUCT BELOW-RHO / TOY-EVIDENCE / OPERATION-LEDGER POLLARD-RHO COMPARISON / NOT A DEPLOYABLE FASTER-THAN-RHO SOLVER.

## Code change

- Added `public_guard_topk4_precision_or_hash12_hit5_root_saved_repaired`.
- Added `public_guard_topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor`.
- Retired the P283 root-saved top-k7 branch from the active union after fresh `1672..1679` selected an unverified row.
- Repaired the older top-k4/root-saved baseline after fresh `1680..1687` selected a weak hash top-k7 charge-2/hit-3 unverified row.

## Precision base

The precision base keeps:

- low-term top-k<=4 root-saved rows only when hit-root ops>=3 and unique selected-leaf signatures>=4;
- hash/hybrid top-k<=4 root-saved rows only when hit-root ops>=4 and charge>=3;
- hash top-k<=12 root-saved rows only when hit-root ops>=5.

Prior through `1679`, the precision base selects `99` density rows, all `99` verified below rho, with zero unverified and zero verified-above-rho rows.

## Diagnostic block: 1680..1687

- Precision base: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1680_1687_hash12hit5_precision_repaired_baseline_diagnostic_no_low_prefix_probe.json`.
- Precision union: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1680_1687_hash12hit5_precision_repaired_plus_hash_top12_no_root_ops_floor_diagnostic_no_low_prefix_probe.json`.
- Precision base selects one clean row: `22050@1686`, low-term top-k4, secret `10307`, shared `102/137 = 0.74452555x`.
- Precision union selects that row plus `22050@1685`, hash top-k4, secret `10948`, shared `103/137 = 0.75182482x`.
- Replay: `low_term_total2_fixed_leaf_shared_product_timing_22050_1685_hash_topk4_repaired_hash_top12_no_root_ops_floor_diagnostic_probe.json`; direct-cover match true and public-key verification true.

## Fresh validation: 1688..1695

- Precision base: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1688_1695_hash12hit5_precision_repaired_baseline_validation_no_low_prefix_probe.json`.
- Precision union: `low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1688_1695_hash12hit5_precision_repaired_plus_hash_top12_no_root_ops_floor_validation_no_low_prefix_probe.json`.
- Both select `4` route cases, all verified below rho, zero unverified, zero verified-above-rho, and two distinct scalars: `22050@1691` secret `4361` and `22050@1694` secret `843`.
- Result: clean validation, but no fresh recall gain over the precision baseline.

## Next step

Continue with fresh `1696..1703`.  Promote only if the precision-union adds distinct fresh recall beyond the precision base with zero selected unverified rows and zero verified-above-rho rows.
