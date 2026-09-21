# Charge-incidence ledger report — TASK-20260730-079 / BATCH-027

## Objective

Construct a checkable symbolic stage↔resource charge-incidence ledger linking
`peak_liveset_partial` stage live-set slots and FC0-EXT lifetime hooks to
Q/S/P/C(+H) resource-vector fields (BATCH-023/026), advancing QM-MEMORY-MAP
beyond `resource_vector_partial` without inventing numeric widths/charges or
claiming QUERY_MEMORY clearance. Keep QM-STOPPING open.

## Method (zero compute)

Read-only against:

- BATCH-022 scaffold: `STAGE_LIVE_SETS`, `StageLiveSetTracker`, `LifetimeRegistry`
- BATCH-021 frozen `lifetime_hooks_interface.yaml` (12 hooks)
- BATCH-023 `peak_live_set_accounting.yaml` (`peak_liveset_partial`)
- BATCH-026 `qspc_resource_vector_ledger.yaml` (`resource_vector_partial`)

Wrote incidence edges under the TASK-20260730-079 write scope only. No curve,
isogeny, simulator, or quantum-circuit execution. CollimationSieve@6f9188e4
untouched (no API invention).

## Observations

1. **Stage-slot incidence.** Fifteen edges map named live-set slots
   (`W_label`, `R_label`, `W_sieve`, `R_sieve`, `B_sieve`,
   `accepted_transcript`, `B_post`, `B_recovery`, `M_tail`, `B_candidate`,
   `B_input`, `B_attempt`, plus an explicit `not_supported` numeric-width
   catch-all) to Q/S/P/C(+H) with statuses in
   `{wired_symbolic, checklist_only, not_supported, deferred}`.

2. **Lifetime-hook incidence.** Thirteen edges map FC0-EXT hook families on
   `LifetimeRegistry` to the same fields. Primary wirings:
   - Q ← `W_label`, `R_label`
   - S ← `W_sieve`, `R_sieve` (plus checklist `B_sieve`)
   - P ← `accepted_transcript`, `B_post`
   - C ← `B_recovery` (plus checklist `B_input`/`B_attempt`/`B_post`)
   - H ← `M_tail`, `B_candidate`

3. **Deferred / not supported.** `R_sieve→Q` deferred (no invented Q/S split).
   Numeric charge metering and numeric-width incidence are `not_supported`.

4. **Counts (ledger edges only).** wired_symbolic=18, checklist_only=7,
   deferred=1, not_supported=2; 15+13=28=18+7+1+2.

5. **Scaffold mutation.** `scaffold_mutated: false`; BATCH-022 not modified.

## Statuses

| Lane | Status |
|------|--------|
| Disposition | `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` |
| QM-MEMORY-MAP | `charge_incidence_partial` (prior: `resource_vector_partial`) |
| QM-STOPPING | `open` |
| QM-ERROR | `f_union_ledger_partial` (retained) |
| QUERY_MEMORY | unreconciled / not cleared |
| BATCH-020 pin | `no_admissible_pin` retained |
| ttm-v2 | finite ideal-choice; not equated to BATCH-014 |

## Non-claims

No numeric widths, numeric charges, peak-byte bounds, probabilities, security
bits, τ, jointly finite E[·], QUERY_MEMORY clearance, PIN_COMPLETE, or
CollimationSieve API invention.

## Harness

```text
python3 -m charge_incidence_harness.run_harness
```

Receipt: `charge_incidence_harness/harness_receipt.json`.

## Idea-status suggestion

`confirm_charge_incidence_partial_query_memory_open`
