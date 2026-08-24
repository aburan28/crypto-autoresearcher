# BATCH-028 routing report — TASK-20260730-083

**Role:** Executor  
**Decision / evidence:** DEC-20260730-025 / EV-SSI-027  
**Disposition:** `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`  
**QM-MEMORY-MAP:** `charge_incidence_partial` → `retry_cleanup_tail_partial` (not clearance)  
**QM-STOPPING:** open  
**QM-ERROR:** `f_union_ledger_partial` (retained)

## What was done

Under zero-compute constraints, this task builds a checkable symbolic
**retry/cleanup and residual-tail charge-routing ledger** against:

- FC0-EXT lifetime hooks on BATCH-022 `LifetimeRegistry` (cleanup modes
  `retry`/`accept`, `note_stopping_breach` → `F_stop`,
  `note_tail_exhaustion` → `F_tail`, `birth_M_tail` rejects `invents_tau`
  and `numeric_width`);
- BATCH-023 `peak_liveset_partial` stage live-set slots;
- BATCH-025 `F_stop` / `F_tail` / `F_cleanup` union membership;
- BATCH-027 `charge_incidence_partial` as retained MEMORY-MAP lineage.

Twenty-eight routes are recorded with
`route_status ∈ {wired_symbolic, checklist_only, not_supported, deferred}`:

| Family | Count |
|---|---|
| retry_cleanup | 20 |
| residual_tail | 8 |
| wired_symbolic | 17 |
| checklist_only | 7 |
| deferred | 1 |
| not_supported | 3 |

Retry/cleanup routes deepen mode-explicit cleanup → Q/S/P/C/H wiring and
symbolic peak-slot releases for attempt-local sieve objects. Residual-tail
routes wire `F_tail`/`M_tail`/`B_candidate` → H and keep `F_stop` as an
ERROR/STOPPING-lane checklist (plus scaffold τ-reject control), while
explicitly marking numeric width / E[·] under τ as `not_supported`.

## Scaffold mutation

`scaffold_mutated: false`. BATCH-022 was read-only. New work lives only
under `TASK-20260730-083/` (including `routing_harness/`).

## Non-claims (binding)

No numeric widths, peak-byte bounds, retry-to-peak conversion, probabilities,
security bits, τ, jointly finite expectations, QUERY_MEMORY clearance,
PIN_COMPLETE, CollimationSieve API invention, or BATCH-014 equation.
ttm-v2 retained as finite ideal-choice only. BATCH-020 `no_admissible_pin`
retained.

## Harness

```text
python3 -m routing_harness.run_harness
```

Single bounded run (`maximum_runs: 1`). Receipt:
`routing_harness/harness_receipt.json`.

## Interpretation limit

`retry_cleanup_tail_partial` is a symbolic MEMORY-MAP routing status. It is
not QUERY_MEMORY clearance and does not close QM-STOPPING or QM-ERROR.
