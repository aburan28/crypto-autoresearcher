# Falsification review — TASK-20260730-113 / BATCH-035

## Verdict

**CONFIRM**

Producer package TASK-20260730-111 (snapshot `2b1f64c3`) matches the expected honest MEMORY-MAP peak-byte-bound obligation schema package: disposition exactly `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, QM-MEMORY-MAP advanced to `peak_byte_bound_schema_partial` without clearance, QM-STOPPING open with `control_result: FAIL` (BATCH-034/033/032/031/018 retained), QM-ERROR `f_union_ledger_partial` retained, placeholders only, harness 8/8, `non_extrapolation: true`, zero curve compute, no CollimationSieve API invention, `retry_peak_byte_schema_partial` / `peak_liveset_partial` retained as lineage, and `peak_byte_bound` / `global_fc0_memory_bound` not instantiated.

## Snapshot binding

| Check | Result |
| --- | --- |
| Snapshot commit | `2b1f64c3a48adb3613efae76223a038fbc0a6da6` |
| Bind / HEAD | `c92927f862018913b3dc523026ac64e5b949b704` |
| Snapshot ancestor of HEAD | yes |
| Receipt parent SHA | `182c2fac3c58367d6d211007f47a03cd0448dfb5` (matches `2b1f64c3^`) |
| Exact eleven-path archive scope | yes (ten producer sources + snapshot receipt) |
| All `source_path_sha256` vs `git show 2b1f64c3` | 10/10 match |
| Archive touches CollimationSieve / BATCH-022 / ledger/ | no |
| Receipt `commit_sha` / verification | still `null` / `pending_post_commit` (non-blocking; Git checks establish durability) |

## Harness re-run

```bash
cd coordination/goals/GOAL-SSI-001/batches/BATCH-035/tasks/TASK-20260730-111
python3 -m peak_byte_bound_harness.run_harness
```

| Field | Observed |
| --- | ---: |
| tests_run | 8 |
| failures / errors | 0 / 0 |
| was_successful | true |
| ledger_status | `peak_byte_bound_schema_partial` |
| control_result | `FAIL` |
| item_count | 35 |
| family counts | 6+5+5+4+4+11 |
| status counts | wired_symbolic=24, checklist_only=2, not_instantiated=6, not_supported=2, deferred=1 |
| disposition | `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` |
| qm_memory_map | `peak_byte_bound_schema_partial` (prior `retry_peak_byte_schema_partial`) |
| qm_stopping | open |
| qm_error | `f_union_ledger_partial` |
| retry_peak_byte_schema_partial retained | true |
| peak_liveset_partial retained | true |
| no_invented_numerics | true |
| conversion_factor_invented | false |
| retry_multiplier_invented | false |
| peak_byte_bound_invented | false |
| clearance flags | all false |
| scaffold_mutated | false |
| collimation_sieve_apis_invented | 0 |

Re-run dirtied `harness_receipt.json` (timestamp / dict-key order). Restored from `git checkout 2b1f64c3 -- .../harness_receipt.json` to SHA-256 `6edcb0945066a05f34167502b4de31af8448b27af92503c5bf99cd6411b0321f`. Producer tree left clean; `__pycache__` / AppleDouble `._*` removed.

## Falsification targets

| Target | Result |
| --- | --- |
| Invented numeric widths / peak-byte bounds / conversion factors / retry multipliers / probabilities / security bits | **Not detected.** All item `numeric_width` / `conversion_factor` / `retry_multiplier` / `units` values are `null` / `not_instantiated`; `peak_byte_bound` is `unresolved` / `not_instantiated`. Global coverage keeps `retry_to_peak_byte: not_supported` and `global_fc0_memory_bound: not_supported`. Only ledger-edge cardinalities and run counters are numeric. `check_no_invented_numerics` hits=`[]`. BATCH-023 object-count lineage is explicitly not re-promoted as bytes. |
| Illicit QUERY_MEMORY or QM-MEMORY-MAP clearance | **Not detected.** `clearance: false`, `reconciled: false`, `query_memory_cleared: false` across classification / memory_map / mutation / ledger summary. |
| Illicit QM-STOPPING clearance or invented τ / joint finiteness | **Not detected.** QM-STOPPING `open`; `control_result: FAIL`; `tau_invented: false`; `joint_finiteness_established: false`; BATCH-034/033/032/031/018 FAIL reconfirmed. |
| Fake peak-byte bound completeness / PIN_COMPLETE / global FC0 memory bound | **Not detected.** `pin_complete: false`; disposition not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`; `PBB-BP-peak_byte_bound` `not_instantiated`; `PBB-BP-global-fc0-memory` `not_supported`; lifetime-trace-with-widths `deferred`; ledger_status is `*_partial`. |
| CollimationSieve@6f9188e4 API invention | **Not detected.** Archive paths exclude CollimationSieve; `apis_invented: false`; `collimation_sieve_touched: false`; status `host_gap_certified_retained_untouched`. |
| Equating ttm-v2 with BATCH-014 | **Not detected.** `equated_to_batch014: false` in classification, ledger coverage, and ttm_v2_scope. |
| Numeric security / breakthrough / goal-completion creep | **Not detected.** Mentions appear only in excluded statements / non-claims; `non_extrapolation: true`. |
| Disposition ≠ `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` when only placeholders | **Not detected.** Disposition exactly that string; evidence supports placeholder peak-byte bound obligations only. |

## Residual wording debt (non-blocking / scope-expansion guards)

These are **not** grounds to REJECT or REVISE the producer package; they bind downstream EV/DEC language:

1. Do not read `peak_byte_bound_schema_partial` as MEMORY-MAP or QUERY_MEMORY clearance.
2. Do not read checklist / wired_symbolic / placeholder bound edges as instantiated peak-byte bounds, conversion factors, or retry multipliers.
3. Do not read harness 8/8 as a MEMORY-MAP mathematical proof or a global FC0 memory bound.
4. Do not overload `artifact_commit_reference` with the CollimationSieve negative-control tip.
5. The scaffold `numeric_width: 128` reject probe is not a claimed width, peak-byte bound, or conversion factor.
6. `to_bound_surface: QUERY_MEMORY_clearance` on `PBB-BP-global-fc0-memory` is a named unsupported target under `not_supported`, not clearance.
7. Some harness receipt honesty flags are hardcoded literals; rely on YAML/Git checks already performed, not the receipt alone.
8. Naming `protocol_id: CSIDH-COLLIMATION-FC0-R2` is convention wiring only; units remain `not_instantiated` and no numeric bound is attached.

## Lineage spot-checks

- BATCH-034 CONV-CF-conversion_factor / CONV-CF-retry_multiplier / CONV-CF-retry-to-peak-path exist.
- BATCH-033 BIND-LH-W/R/B/M_tail-birth and BIND-PC-peak-byte exist.
- BATCH-023 retains `peak_rule.definition: max_over_named_stage_live_sets_not_sum` and `peak_byte_bound: unresolved`.
- `retry_peak_byte_schema_partial` and `peak_liveset_partial` retained as lineage under advancement.

## Narrowest supported statement

Symbolic peak-byte bound obligation schema ledger (35 items; harness 8/8) advances QM-MEMORY-MAP honesty from `retry_peak_byte_schema_partial` to `peak_byte_bound_schema_partial` with placeholders only under an explicit protocol declaration (protocol_id / units / accounting_rule max-not-sum), retains `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, keeps QM-STOPPING open under BATCH-034/033/032/031/018 FAIL, retains QM-ERROR `f_union_ledger_partial`, retains `retry_peak_byte_schema_partial` and `peak_liveset_partial` as lineage, invents no widths/conversion factors/retry multipliers/peak-byte/τ/APIs/BATCH-014 equation, does not instantiate `peak_byte_bound` or `global_fc0_memory_bound`, and claims no numeric security, breakthrough, PIN_COMPLETE, or GOAL-SSI-001 completion.

## Written paths

- `coordination/goals/GOAL-SSI-001/batches/BATCH-035/tasks/TASK-20260730-113/red_team_report.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-035/tasks/TASK-20260730-113/falsification_review.md`

## Inference

- requested_policy: `review-xhigh`
- resolved_model: Cursor Grok
- fallback_used: true
- independent_session: true
