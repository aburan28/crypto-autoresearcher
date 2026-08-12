# ECFG-P287 graph edge-4 density validation

## Status

GRAPH EDGE4 DENSITY DIAGNOSTIC RECALL GAIN ON `1720..1727` / FROZEN FRESH
`1728..1735` VALIDATION RECALL GAIN WITH ZERO SELECTED NOISE /
REPLAY-BACKED SHARED SELECTED-PRODUCT BELOW-RHO / TARGET-`67` LOW-PREFIX
GRAPH NEGATIVE / TOY-EVIDENCE / OPERATION-LEDGER POLLARD-RHO COMPARISON /
NOT A DEPLOYABLE FASTER-THAN-RHO SOLVER.

## What Changed

`tasks/ecdlp_index_calculus/low_term_total2_fixed_leaf_guarded_target_aware_split_gate_probe.py`
now has two default-off graph-density guards:

- `public_guard_graph_edge4_density_hash12_saved2_or_topk7_root_saved`
- `public_guard_topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor_or_graph_edge4_density`

The second guard keeps the repaired precision/no-root baseline and adds three
small public graph edge-4 density slices:

- hash top-k12, saved ops `2`, charge `2`, hit-root ops `4`, route-edge min/max `4/4`
- hybrid top-k7, saved ops `1`, charge `2`, hit-root ops `3`, route-edge min/max `4/4`
- low-term total10 top-k7, saved ops `1`, charge `3`, hit-root ops `4`, route-edge min/max `4/4`

## Control And Diagnostic

Fresh `1712..1719` is the control block.  The P286 graph edge-12 strict guard
and the repaired precision selectors abstain cleanly.  The target-`67`
low-prefix top-k4/edge slices expose some below-rho rows, but prior backtests
are noisy and unverified-heavy, so that family remains negative.

On `1720..1727`, the repaired precision baseline and precision union select
only the existing `8729` scalar.  The graph-density union selects five route
cases, all verified below rho, with zero unverified and zero verified-above-rho
rows.  It adds two scalars beyond the precision baseline:

- `22050@1725`, hybrid top-k7, secret `10839`, shared `101/137 = 0.73722628x`
- `22050@1726`, hash top-k12, secret `7684`, shared `106/137 = 0.77372263x`

Timing artifacts:

- `ecdlp_index_calculus_state/low_term_total2_fixed_leaf_shared_product_timing_22050_1725_graph_edge4_hybrid_topk7_density_diagnostic_probe.json`
- `ecdlp_index_calculus_state/low_term_total2_fixed_leaf_shared_product_timing_22050_1726_graph_edge4_hash_topk12_density_diagnostic_probe.json`

Both timing replays reproduce the selected-product cover and public-key
verification.

## Fresh Validation

Fresh `1728..1735` was generated after the guard was frozen.  The source has
`5` leaf-verified cases, `4` leaf-below-rho cases, best leaf ops/rho
`0.76642336`, `4` row-verified cases, and `2` row-below-rho cases.

Raw gate summaries:

- strict shared-product gate: `3` public selections, no selected below-rho cases
- density shared-product gate: `12` public selections, `4` selected below-rho cases, `7` false positives, `1` verified-above-rho row
- target-`67` low-prefix direct gate: abstains

Frozen split validation artifact:

- `ecdlp_index_calculus_state/low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1728_1735_precision_union_plus_graph_edge4_density_validation_no_low_prefix_probe.json`

Result: `SPLIT_PUBLIC_GATE_POSITIVE`.  The frozen graph-density union selects
three route cases, all verified below rho, zero unverified, zero
verified-above-rho, and one fresh scalar:

- `22050@1733`, hash top-k4, secret `6251`, shared `114/137 = 0.83211679x`

Timing replay:

- `ecdlp_index_calculus_state/low_term_total2_fixed_leaf_shared_product_timing_22050_1733_graph_edge4_hash_topk4_density_validation_probe.json`

The replay gives direct `118/137 = 0.86131387x`, shared product `114/137 =
0.83211679x`, selected-cover match true, and public-key verification true.

A no-graph ablation with the same extra-density route but guard
`public_guard_topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor`
selects the same three fresh `1733` rows and the same scalar `6251`.  Thus the
fresh `1728..1735` result validates guarded density-route admission.  The
specifically new graph edge-4 subguard is diagnostic-positive on `1720..1727`
and needs another frozen block to become a standalone graph promotion.

## Boundary

This is not a deployable faster-than-rho ECDLP solver.  The comparison is the
repo's local operation ledger against Pollard rho on the toy/fixed benchmark,
with replay-backed scalar recovery after a public gate decision.  The 1720
block is diagnostic because the edge-4 density guard was designed after seeing
that block; the stronger result is the frozen fresh `1728..1735` validation.

## Next

Validate the frozen graph-density guard unchanged on `1736..1743`.  In
parallel, inspect the raw density below-rho rows rejected on `1728..1735` for a
public separator that does not reopen the rejected false positives.
