# Falsification review — TASK-20260730-109 / BATCH-034

## Verdict

**CONFIRM**

Producer package TASK-20260730-107 (snapshot `deb1c18b`) matches the expected honest MEMORY-MAP conversion-schema package: disposition exactly `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, QM-MEMORY-MAP advanced to `retry_peak_byte_schema_partial` without clearance, QM-STOPPING open with `control_result: FAIL` (BATCH-033/032/031/018 retained), QM-ERROR `f_union_ledger_partial` retained, placeholders only, harness 8/8, `non_extrapolation: true`, zero curve compute, no CollimationSieve API invention, `width_slot_binding_partial` / `peak_liveset_partial` retained as lineage, and `retry_to_peak_byte` / `conversion_factor` / `peak_byte_bound` not instantiated.

## Snapshot binding

| Check | Result |
| --- | --- |
| Snapshot commit | `deb1c18b4b21ab9344255b46bc8fcb38d4d65023` |
| Bind / HEAD | `0abd6cc3b9ced0b73e0a45d8f37de7f314e0379f` |
| Snapshot ancestor of HEAD | yes |
| Receipt parent SHA | `1c7c4b9b6e6755e5de12d5e935912aa04c8378bb` (matches) |
| Exact eleven-path archive scope | yes |
| All `source_path_sha256` vs `git show deb1c18b` | 10/10 match |
| Receipt `commit_sha` / verification | still `null` / `pending_post_commit` (non-blocking; Git checks establish durability) |

## Harness re-run

```bash
cd coordination/goals/GOAL-SSI-001/batches/BATCH-034/tasks/TASK-20260730-107
python3 -m retry_peak_byte_harness.run_harness
```

| Field | Observed |
| --- | ---: |
| tests_run | 8 |
| failures / errors | 0 / 0 |
| was_successful | true |
| ledger_status | `retry_peak_byte_schema_partial` |
| control_result | `FAIL` |
| item_count | 34 |
| family counts | 6+6+6+6+10 |
| status counts | wired_symbolic=21, checklist_only=4, not_instantiated=5, not_supported=3, deferred=1 |
| disposition | `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` |
| qm_memory_map | `retry_peak_byte_schema_partial` (prior `width_slot_binding_partial`) |
| qm_stopping | open |
| qm_error | `f_union_ledger_partial` |
| width_slot_binding_partial retained | true |
| peak_liveset_partial retained | true |
| no_invented_numerics | true |
| conversion_factor_invented | false |
| retry_multiplier_invented | false |
| peak_byte_bound_invented | false |
| clearance flags | all false |
| scaffold_mutated | false |
| collimation_sieve_apis_invented | 0 |

Re-run dirtied `harness_receipt.json` (timestamp / dict-key order). Restored from `git checkout deb1c18b -- .../harness_receipt.json` to SHA-256 `168221d7d9511f2396b690cd387a61f99bf60fe103373815ed5d5a5222e9f291`. Producer tree left clean; `__pycache__` / AppleDouble `._*` removed.

## Falsification targets

| Target | Result |
| --- | --- |
| Invented numeric widths / peak-byte bounds / conversion factors / retry multipliers / probabilities / security bits | **Not detected.** All item `numeric_width` / `conversion_factor` / `retry_multiplier` values are `null` / `not_instantiated`; `peak_byte_bound` is `unresolved` / `not_instantiated`. Global coverage keeps `retry_to_peak_byte: not_supported`. Only ledger-edge cardinalities and run counters are numeric. `check_no_invented_numerics` hits=`[]`. |
| Illicit QUERY_MEMORY or QM-MEMORY-MAP clearance | **Not detected.** `clearance: false`, `reconciled: false`, `query_memory_cleared: false` across classification / memory_map / mutation / ledger summary. |
| Illicit QM-STOPPING clearance or invented τ / joint finiteness | **Not detected.** QM-STOPPING `open`; `control_result: FAIL`; `tau_invented: false`; `joint_finiteness_established: false`; BATCH-033/032/031/018 FAIL reconfirmed. |
| Fake conversion completeness / PIN_COMPLETE | **Not detected.** `pin_complete: false`; disposition not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`; global FC0 memory bound `not_supported`; lifetime-trace-with-widths `deferred`; ledger_status is `*_partial`. |
| CollimationSieve@6f9188e4 API invention | **Not detected.** Archive paths exclude CollimationSieve; `apis_invented: false`; `collimation_sieve_touched: false`; status `host_gap_certified` retained. |
| Equating ttm-v2 with BATCH-014 | **Not detected.** `equated_to_batch014: false` in classification, ledger coverage, and ttm_v2_scope. |
| Numeric security / breakthrough / goal-completion creep | **Not detected.** Explicit excluded statements and `non_extrapolation: true`. |
| Disposition ≠ `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` when only placeholders | **Not detected.** Disposition exactly that string; evidence supports placeholder conversion obligations only. |

## Residual wording debt (non-blocking / scope-expansion guards)

These are **not** grounds to REJECT or REVISE the producer package; they bind downstream EV/DEC language:

1. Do not read `retry_peak_byte_schema_partial` as MEMORY-MAP or QUERY_MEMORY clearance.
2. Do not read checklist / wired_symbolic / placeholder conversion edges as numeric conversion factors, retry multipliers, or peak-byte accounting.
3. Do not read harness 8/8 as a MEMORY-MAP mathematical proof.
4. Do not overload `artifact_commit_reference` with the CollimationSieve negative-control tip.
5. The scaffold `numeric_width: 128` reject probe is not a claimed width or conversion factor.
6. `to_conversion_surface: QUERY_MEMORY_clearance` on CONV-CF-global-fc0-memory is a named unsupported target under `not_supported`, not clearance.
7. Some harness receipt honesty flags are hardcoded literals; rely on YAML/Git checks already performed, not the receipt alone.

## Lineage spot-checks

- BATCH-028 route ids cited by CONV-RR-* exist.
- BATCH-033 BIND-LH-W/R/B/M_tail-birth, BIND-PC-peak-byte, BIND-PC-retry-to-peak exist.
- BATCH-023 retains `peak_rule.definition: max_over_named_stage_live_sets_not_sum` and `peak_byte_bound: unresolved`.

## Narrowest supported statement

Symbolic retry-to-peak-byte conversion obligation schema ledger (34 items; harness 8/8) advances QM-MEMORY-MAP honesty from `width_slot_binding_partial` to `retry_peak_byte_schema_partial` with placeholders only, retains `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, keeps QM-STOPPING open under BATCH-033/032/031/018 FAIL, retains QM-ERROR `f_union_ledger_partial`, retains `width_slot_binding_partial` and `peak_liveset_partial` as lineage, invents no widths/conversion factors/retry multipliers/peak-byte/τ/APIs/BATCH-014 equation, and claims no numeric security, breakthrough, PIN_COMPLETE, or GOAL-SSI-001 completion.

## Written paths

- `coordination/goals/GOAL-SSI-001/batches/BATCH-034/tasks/TASK-20260730-109/red_team_report.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-034/tasks/TASK-20260730-109/falsification_review.md`

## Inference

- requested_policy: `review-xhigh`
- resolved_model: Cursor Grok
- fallback_used: true
- independent_session: true
