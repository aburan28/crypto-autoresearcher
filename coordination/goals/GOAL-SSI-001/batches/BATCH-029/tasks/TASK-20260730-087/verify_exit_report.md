# Verify-exit / F_verify obligation ledger report (TASK-20260730-087)

## Summary

Zero-compute Executor package for GOAL-SSI-001 BATCH-029 under
DEC-20260730-026 / EV-SSI-028. Constructs a checkable symbolic
Verify-relative success-exit and F_verify obligation/charge-routing ledger
against recovery_spec (BATCH-013), path-justified F_verify (BATCH-024),
F_union membership (BATCH-025), and retry/cleanup / H-side lineage
(BATCH-027/028). Advances QM-MEMORY-MAP from `retry_cleanup_tail_partial`
to `verify_exit_partial` without QUERY_MEMORY clearance.

## Observations (no conclusions)

- **24 ledger items**: success_exit=7, f_verify_membership=6,
  charge_routing=11.
- **Status counts**: wired_symbolic=17, checklist_only=1, deferred=1,
  not_supported=5 (identity 17+1+1+5=24).
- Success-exit wiring retains recovery_spec rule that only
  `Verify(x,k')=true` is success; report-only / unverified / exhausted
  residual remain failures.
- F_verify retained as BATCH-025 union member with BATCH-024
  path-justified false/fault scaffold paths; F_sim `maps_to_F=false`
  honesty retained.
- Charge-routing edges wire B_candidate→H, Verify outcomes→success /
  F_verify, and post-Verify cleanup of B_candidate/M_tail/B_recovery to
  H/C without numeric metering.
- Explicit `not_supported` / `deferred` for crypto Verify body, numeric
  widths, E[·] under τ, and F_verify probability charges.
- Disposition: `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.
- QM-STOPPING: open. QM-ERROR: `f_union_ledger_partial` retained.
- BATCH-020 `no_admissible_pin` retained; CollimationSieve@6f9188e4
  untouched; ttm-v2 retained as finite ideal-choice only (not equated to
  BATCH-014).
- BATCH-022 scaffold read-only (`scaffold_mutated: false`).

## Harness

```text
python3 -m verify_exit_harness.run_harness
```

Receipt: `verify_exit_harness/harness_receipt.json` (written on run).

## Non-claims

No numeric widths, peak-byte bounds, probabilities, security bits, τ,
joint finiteness, crypto Verify body, QUERY_MEMORY clearance,
PIN_COMPLETE, CollimationSieve API invention, or BATCH-014 equation.

## Artifact paths

- `verify_exit_obligation_ledger.yaml`
- `memory_map_status.yaml`
- `verify_exit_report.md`
- `mutation_status.yaml`
- `classification.yaml`
- `verify_exit_harness/` (harness + receipt)
