# TASK-20260730-071 — Symbolic F-union / operational-error composition ledger

**Goal:** GOAL-SSI-001 / BATCH-025  
**Decision / evidence:** DEC-20260730-022 / EV-SSI-024  
**Package:** FC0-EXT-PKG-SSI-001 (BATCH-022 scaffold read-only)  
**Entrypoint:** `python3 -m composition_ledger_harness.run_harness`  
**Compute:** zero curve / isogeny / quantum-circuit  
**Harness:** 7/7 tests OK (`composition_ledger_harness/harness_receipt.json`)

## What advanced beyond BATCH-024

BATCH-024 left all seven recovery_spec constituents as
`path_justified_on_scaffold` with `composition_status=path_justified_partial`
and honest `F_sim` (`maps_to_F=false`).

This batch constructs a checkable **symbolic F-union ledger**:

1. Defines `U = F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ F_recovery ∪ F_tail ∪ F_verify`.
2. Records explicit membership rules R1–R5 (set inclusion into common `F`,
   Verify=true success exit, channel-fire ⇒ F, F_sim not mapped).
3. Records **operational-error composition** as symbolic set-union under the
   recovery_spec common-event definition — checklist / set-theoretic only.
4. Retains F_sim honesty (`maps_to_F=false`).

No probabilities, numeric error bounds, security bits, or τ are invented.

## F-union status

| Item | Status |
|---|---|
| Union expression | `U ⊆ F` (seven constituents) |
| Membership rules | R1–R5 recorded and harness-checked |
| Success exit | Verify=true only |
| F_sim | `maps_to_F=false` retained; not a union member |
| `composition_status` | **`f_union_ledger_partial`** |

## Composition structure summary

- **Kind:** `symbolic_set_union_under_common_event_F`
- **Not:** probability sum, numeric union bound, security-bit reduction, or
  independent Bernoulli product
- **Rule:** any fired `F_*` without Verify=true ⇒ operational failure ∈ F;
  overlaps permitted; no independence claim
- **Checklist C1–C7:** all passed in harness (names, prior path justification,
  membership, success exit, no probabilities, F_sim honesty, no τ)

## Disposition and QM blockers

- **Disposition:** `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`
- **QM-STOPPING:** open (no τ / joint finiteness)
- **QM-ERROR:** advanced to `f_union_ledger_partial` (not clearance)
- **QM-MEMORY-MAP:** retained `peak_liveset_partial` (not clearance)
- **BATCH-020:** `no_admissible_pin` retained
- **ttm-v2:** retained as finite ideal-choice; not equated with BATCH-014
- CollimationSieve@6f9188e4 untouched; no APIs invented
- Closed IDEA-20260725-001/002/003 not reopened
- No numeric security, breakthrough, or goal-completion claim

## Artifacts

- `f_union_ledger.yaml`
- `operational_error_composition.yaml`
- `composition_ledger_report.md`
- `mutation_status.yaml`
- `classification.yaml`
- `composition_ledger_harness/` (optional write-scope harness; receipt
  `composition_ledger_harness/harness_receipt.json`)
