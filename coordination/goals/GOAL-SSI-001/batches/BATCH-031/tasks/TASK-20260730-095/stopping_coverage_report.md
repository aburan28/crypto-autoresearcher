# Symbolic τ-schema / stopping-coverage obligation ledger

Task `TASK-20260730-095` · batch `BATCH-031` · idea `IDEA-20260729-001`  
Convention `CSIDH-COLLIMATION-FC0-R2` · zero curve/isogeny/circuit compute  
Binding: `DEC-20260730-028` / `EV-SSI-030`

## Control result

**FAIL** — reconfirms BATCH-018 `joint_qspc_ledger.yaml` / classification
`control_result: FAIL`.

- `stopping_time.instantiation_status: not_instantiated`
- `finite_almost_surely_proved: false`
- `finite_moments_proved: false`
- `transition_kernel` / `independence_conditions` / `uniform_success_lower_bound`: null
- C2 heavy-tail mutation remains **NOT_REJECTED** / live
- QM-STOPPING remains **open**
- Disposition remains `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`

## What was produced

A checkable symbolic obligation ledger (`tau_schema_stopping_ledger.yaml`) with
24 items in three families:

| Family | Count | Role |
|--------|------:|------|
| `tau_coverage` | 8 | Required coverage slots from BATCH-018 / `stopping_liveness_control` |
| `tau_instantiation` | 8 | Type-only schema + not-supported finiteness / kernel / joint-E edges |
| `lineage_cross_link` | 8 | FAIL reconfirm, C2 live, MEMORY-MAP / Verify-exit non-clearance links |

Status counts: `wired_symbolic=11`, `checklist_only=4`, `deferred=1`,
`not_supported=8`.

Required coverage items named (not τ-instantiated):

1. recursive discards — checklist_only  
2. failed regularization — checklist_only  
3. repeated punctured-regularization attempts — checklist_only  
4. fresh-sieve recovery runs — checklist_only  
5. residual-tail entry — wired_symbolic cross-link to BATCH-030 / recovery_spec  
6. \(F_{\mathrm{stop}}\) stopping-policy breach — wired_symbolic cross-link  

Verify-relative terminal obligation is wired via recovery_spec + BATCH-029
Verify-exit lineage without inventing a cryptographic Verify body or τ.

## Lineage honesty

- **QM-MEMORY-MAP** retained at `history_uniform_tail_partial` (no clearance).
- **verify_exit_partial** retained; success-exit / \(F_{\mathrm{verify}}\) wiring ≠ stopping law.
- **QM-ERROR** retained `f_union_ledger_partial`.
- **ttm-v2** retained as finite ideal-choice only; `usable_as_global_tau=false`;
  BATCH-014 not equated.
- **BATCH-020** `no_admissible_pin` retained.
- **CollimationSieve@6f9188e4** untouched; no APIs invented.
- BATCH-022 scaffold read-only (`scaffold_mutated: false`).

## Non-claims

No numeric widths, peak-byte bounds, probabilities, security bits, τ,
transition kernels, independence conditions, jointly finite expectations,
history-uniform / summable-tail proofs, QUERY_MEMORY clearance, PIN_COMPLETE,
or crypto Verify body.

## Harness

Entrypoint: `python3 -m tau_schema_harness.run_harness`  
(from this task directory; maximum_runs: 1).
