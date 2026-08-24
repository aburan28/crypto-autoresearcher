# BATCH-022 FC0-EXT-PKG-SSI-001 Verify / lifetime implementation spike

Task `TASK-20260730-059` · package `FC0-EXT-PKG-SSI-001` (frozen BATCH-021) ·
decision `DEC-20260730-019` / evidence `EV-SSI-021` · zero curve / isogeny /
quantum-circuit compute · `maximum_runs: 1` · git tip
`a3260f967caa4f1f6739795d068ad698f6bd7830`.

## Objective

Bounded implementation spike of `Verify(x,k')` and W/R/B/M_tail lifetime hooks
against frozen `FC0-EXT-PKG-SSI-001`, under the declared write scope only.
Record honest `implemented_partial | implemented_complete |
blocked_with_certificate` with checkable evidence.

## Frozen interfaces (read-only)

| Artifact | Path |
| --- | --- |
| Package | `BATCH-021/.../fc0_extension_package.yaml` |
| Verify | `BATCH-021/.../verify_interface.yaml` |
| Lifetimes | `BATCH-021/.../lifetime_hooks_interface.yaml` |
| Anchors | `recovery_spec.md`, `lifetime_trace.yaml` |

CollimationSieve@`6f9188e4` remains a negative control (`host_gap_certified`);
no APIs invented on that pin.

## What was built (write scope only)

Scaffold package under
`coordination/goals/GOAL-SSI-001/batches/BATCH-022/tasks/TASK-20260730-059/scaffold/`:

| Module | Role |
| --- | --- |
| `types.py` | Opaque roles, `CleanupResult`, `FailureChannel`, handle states |
| `verify.py` | No-crypto total `Verify(x, k_prime) -> bool` |
| `lifetime_hooks.py` | Birth/last_use/cleanup/destroy for all 12 hooks |
| `state_machine.py` | Stage live-set tracker (frozen membership checklist) |
| `test_scaffold.py` | 11 unit tests (no crypto / no curve compute) |
| `run_harness.py` + `harness_receipt.json` | Checkable coverage receipt |

Harness result: **11 tests OK**; `implemented_method_count: 48` (12 hooks × 4);
`collimation_sieve_apis_invented: 0`; numeric widths and τ invention rejected.

## Attempt outcomes (summary)

Concrete per-check records live in `lifetime_verify_attempt.yaml`.

| Target | Outcome |
| --- | --- |
| `Verify(x,k')` | `scaffolding_partial` (no crypto body) |
| `W_label` / `R_label` | `scaffolding_partial` |
| `W_sieve` / `R_sieve` | `scaffolding_partial` |
| `B_*` + `accepted_transcript` | `scaffolding_partial` |
| `M_tail` | `scaffolding_partial` (τ not invented) |
| End-to-end resource vector | `absent_under_zero_compute` |

## Implementation status

**`implemented_partial`** (see `impl_status.yaml`).

Not `implemented_complete`: zero-compute forbids crypto Verify body, numeric
widths, and an end-to-end resource vector. Not `blocked_with_certificate`: the
spike targets the in-repo frozen package (admissible scaffolding), not the
CollimationSieve pin gap from BATCH-019.

## QUERY_MEMORY blockers (honest)

| Blocker | Status after spike |
| --- | --- |
| `QM-STOPPING` | **open** (no τ / joint finiteness; scaffold rejects `invents_tau`; BATCH-018 FAIL retained) |
| `QM-MEMORY-MAP` | **scaffolding_partial_implementation_pending** — not clearance |
| `QM-ERROR` | **scaffolding_partial_implementation_pending** — not clearance |

## Disposition

`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`

Not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW` (no end-to-end resource vector).
Not `FC0_UNIFORM_ORACLE_BOUNDARY_UNRESOLVED` (this batch does not diagnose a
uniform-oracle boundary).

## Retained scope limits

- `non_extrapolation: true`
- BATCH-020 `no_admissible_pin` retained
- ttm-v2 retained as finite ideal-choice panel only; **not** equated with BATCH-014
- No numeric security, breakthrough, or goal-completion claim
- Closed IDEA-20260725-001/002/003 not reopened
- Inference: requested `executor-terra`, resolved Cursor Grok, `fallback_used: true`
- No git commit from this task

## Artifacts

1. `spike_report.md` (this file)
2. `impl_status.yaml`
3. `lifetime_verify_attempt.yaml`
4. `mutation_status.yaml`
5. `classification.yaml`
6. Scaffold (supporting checkable evidence under write scope): `scaffold/*`
