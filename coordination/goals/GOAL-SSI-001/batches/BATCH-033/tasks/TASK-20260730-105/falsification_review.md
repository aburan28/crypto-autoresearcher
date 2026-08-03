# Falsification review — TASK-20260730-105 / BATCH-033

## Verdict

**CONFIRM**

Producer package TASK-20260730-103 (snapshot `7da67675`) matches the expected honest MEMORY-MAP binding package: disposition exactly `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, QM-MEMORY-MAP advanced to `width_slot_binding_partial` without clearance, QM-STOPPING open with `control_result: FAIL` (BATCH-032/031/018 retained), QM-ERROR `f_union_ledger_partial` retained, placeholders only, harness 8/8, `non_extrapolation: true`, zero curve compute, no CollimationSieve API invention, and `width_schema_partial` / `charge_incidence_partial` retained as lineage.

## Snapshot binding

| Check | Result |
| --- | --- |
| Snapshot commit | `7da67675a2846e9449c1eb58c2ef84169eea4c34` |
| Bind / HEAD | `a1cc724975be3d80f5c0d64c8bff94cf593a6206` |
| Snapshot ancestor of HEAD | yes |
| Receipt parent SHA | `321e33d21c917be1d0cc2eaf2a2a223454e42212` (matches) |
| Exact eleven-path archive scope | yes |
| All `source_path_sha256` vs `git show 7da67675` | 10/10 match |
| Receipt `commit_sha` / verification | still `null` / `pending_post_commit` (non-blocking; Git checks establish durability) |

## Harness re-run

```bash
cd coordination/goals/GOAL-SSI-001/batches/BATCH-033/tasks/TASK-20260730-103
python3 -m width_slot_binding_harness.run_harness
```

| Field | Observed |
| --- | ---: |
| tests_run | 8 |
| failures / errors | 0 / 0 |
| was_successful | true |
| ledger_status | `width_slot_binding_partial` |
| control_result | `FAIL` |
| item_count | 31 |
| family counts | 12+6+4+9 |
| status counts | wired_symbolic=20, checklist_only=3, not_instantiated=4, not_supported=3, deferred=1 |
| disposition | `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` |
| qm_memory_map | `width_slot_binding_partial` (prior `width_schema_partial`) |
| qm_stopping | open |
| qm_error | `f_union_ledger_partial` |
| width_schema_partial retained | true |
| charge_incidence_partial retained | true |
| no_invented_numerics | true |
| clearance flags | all false |
| scaffold_mutated | false |
| collimation_sieve_apis_invented | 0 |

Re-run dirtied `harness_receipt.json` (timestamp / dict-key order). Restored from `git checkout 7da67675 -- .../harness_receipt.json` to SHA-256 `3b3d668ec7d6898f3f03d74e2b1f303dc0d4d40773955c8bf7f503ee75a83603`. Producer tree left clean; `__pycache__` / AppleDouble `._*` removed.

## Falsification targets

| Target | Result |
| --- | --- |
| Invented numeric widths / peak-byte bounds / probabilities / security bits | **Not detected.** All item `numeric_width` / `peak_byte_bound` values are `null` / `unresolved` / `not_instantiated`. Only ledger-edge cardinalities and run counters are numeric. `check_no_invented_numerics` hits=`[]`. |
| Illicit QUERY_MEMORY or QM-MEMORY-MAP clearance | **Not detected.** `clearance: false`, `reconciled: false`, `query_memory_cleared: false` across classification / memory_map / mutation / ledger summary. |
| Illicit QM-STOPPING clearance or invented τ / joint finiteness | **Not detected.** QM-STOPPING `open`; `control_result: FAIL`; `tau_invented: false`; `joint_finiteness_established: false`; BATCH-032/031/018 FAIL reconfirmed. |
| Fake binding completeness / PIN_COMPLETE | **Not detected.** `pin_complete: false`; disposition not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`; global FC0 memory bound `not_supported`; lifetime-trace-with-widths `deferred`; ledger_status is `*_partial`. |
| CollimationSieve@6f9188e4 API invention | **Not detected.** Archive paths exclude CollimationSieve; `apis_invented: false`; `collimation_sieve_touched: false`; status `host_gap_certified` retained. |
| Equating ttm-v2 with BATCH-014 | **Not detected.** `equated_to_batch014: false` in classification, ledger coverage, and ttm_v2_scope. |
| Numeric security / breakthrough / goal-completion creep | **Not detected.** Explicit excluded statements and `non_extrapolation: true`. |
| Disposition ≠ `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` when only placeholders | **Not detected.** Disposition exactly that string; evidence supports placeholder bindings only. |

## Residual wording debt (non-blocking / scope-expansion guards)

These are **not** grounds to REJECT or REVISE the producer package; they bind downstream EV/DEC language:

1. Do not read `width_slot_binding_partial` as MEMORY-MAP or QUERY_MEMORY clearance.
2. Do not read checklist / wired_symbolic / placeholder binding edges as numeric instantiation, charge metering, or peak-byte accounting.
3. Do not read harness 8/8 as a MEMORY-MAP mathematical proof.
4. Do not overload `artifact_commit_reference` with the CollimationSieve negative-control tip.
5. Scaffold Verify smoke and the `numeric_width: 128` reject probe are not claimed widths or crypto Verify.
6. Composite citation `fact` strings (e.g. `SLOT-W_label-Q_and_HOOK-W_label-Q_wired_symbolic`) are narrative lineage labels; prefer exact BATCH-027 edge ids in EV/DEC prose.
7. `to_hook_or_edge: QUERY_MEMORY_clearance` on BIND-PC-global-fc0-memory is a named unsupported target under `not_supported`, not clearance.

## Narrowest supported statement

Symbolic width-slot ↔ lifetime-hook / charge-incidence binding ledger (31 items; harness 8/8) advances QM-MEMORY-MAP honesty from `width_schema_partial` to `width_slot_binding_partial` with placeholders only, retains `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, keeps QM-STOPPING open under BATCH-032/031/018 FAIL, retains QM-ERROR `f_union_ledger_partial`, retains `width_schema_partial` and `charge_incidence_partial` as lineage, invents no widths/charges/peak-byte/τ/APIs/BATCH-014 equation, and claims no numeric security, breakthrough, PIN_COMPLETE, or GOAL-SSI-001 completion.

## Written paths

- `coordination/goals/GOAL-SSI-001/batches/BATCH-033/tasks/TASK-20260730-105/red_team_report.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-033/tasks/TASK-20260730-105/falsification_review.md`

## Inference

- requested_policy: `review-xhigh`
- resolved_model: Cursor Grok
- fallback_used: true
- independent_session: true
