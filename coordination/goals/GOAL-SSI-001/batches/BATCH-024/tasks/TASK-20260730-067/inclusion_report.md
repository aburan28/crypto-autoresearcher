# TASK-20260730-067 — Path-justified F_* ⊆ F inclusions

**Goal:** GOAL-SSI-001 / BATCH-024  
**Decision / evidence:** DEC-20260730-021 / EV-SSI-023  
**Package:** FC0-EXT-PKG-SSI-001 (BATCH-022 scaffold read-only)  
**Entrypoint:** `python3 -m inclusion_harness.run_harness`  
**Compute:** zero curve / isogeny / quantum-circuit  

## What advanced beyond BATCH-023

BATCH-023 left all seven recovery_spec constituents as `scaffold_channel_wired`
with `inclusion_into_common_F: checklist_only_not_justified`.

This batch drives an executable write-scope `ScaffoldProcedure` that:

1. Runs a contrasting **success control** (no-crypto token `Verify=true`).
2. Injects a failure path per `F_*` that records the named channel, returns
   **no** `k'` with `Verify=true`, and classifies the exit as common `F`
   under the recovery_spec definition.
3. Checks those criteria in `inclusion_harness` tests (4/4).

Scaffolding stubs alone are not treated as path justification.

## Per-constituent status

| Constituent | Status | Failure-path injection |
|---|---|---|
| F_input | `path_justified_on_scaffold` | malformed `PublicInstance` |
| F_oracle | `path_justified_on_scaffold` | `cleanup_W_label` on non-live |
| F_cleanup | `path_justified_on_scaffold` | destroy before cleanup |
| F_stop | `path_justified_on_scaffold` | `note_stopping_breach` (+ τ rejected) |
| F_recovery | `path_justified_on_scaffold` | `B_post` while W/R sieve live |
| F_tail | `path_justified_on_scaffold` | `note_tail_exhaustion` |
| F_verify | `path_justified_on_scaffold` | no-crypto Verify false + fault |

Union checklist status: `path_justified_on_scaffold_all_constituents`.  
Composition status retained as **`path_justified_partial`**: scaffold path
justification without probability composition, crypto Verify, or
CollimationSieve end-to-end.

## F_sim treatment

- Write-scope-local `ScaffoldLocalSimulator` wired (`treatment_status:
  scaffold_local_wired_no_map_to_F`).
- `F_sim` absent from BATCH-022 `FailureChannel` enum (certified).
- **`maps_to_F: false`** — illicit F_sim→F implication refused.
- Complete report (`F_sim^c`) is still not Verify-success; report-only ∈ F
  by recovery_spec is **not** an F_sim→F map and does **not** clear
  QUERY_MEMORY.

## Explicit non-claims

- No QUERY_MEMORY clearance; disposition stays
  `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.
- QM-STOPPING remains **open** (no τ / joint finiteness).
- QM-ERROR advanced to `path_justified_partial` (not clearance).
- QM-MEMORY-MAP retained `peak_liveset_partial` from BATCH-023 (not
  clearance; this batch does not invent widths).
- BATCH-020 `no_admissible_pin` retained; CollimationSieve@6f9188e4
  untouched; no APIs invented.
- ttm-v2 retained as finite ideal-choice; not equated with BATCH-014.
- Closed IDEA-20260725-001/002/003 not reopened.
- No numeric security, breakthrough, or goal-completion claim.

## Artifacts

- `path_justified_inclusions.yaml`
- `f_sim_treatment.yaml`
- `inclusion_report.md`
- `mutation_status.yaml`
- `classification.yaml`
- `inclusion_harness/` (optional write-scope harness; receipt
  `inclusion_harness/harness_receipt.json`)
