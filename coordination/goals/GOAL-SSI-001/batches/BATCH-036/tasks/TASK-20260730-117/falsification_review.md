# Falsification review — TASK-20260730-117 / BATCH-036

## Verdict

**CONFIRM**

Producer package TASK-20260730-115 (snapshot `5281383b`) matches the expected honest MEMORY-MAP charge-metering obligation schema package: disposition exactly `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, QM-MEMORY-MAP advanced to `charge_metering_schema_partial` without clearance, QM-STOPPING open with `control_result: FAIL` (BATCH-035/034/033/032/031/018 retained), QM-ERROR `f_union_ledger_partial` retained, placeholders only, harness 8/8, `non_extrapolation: true`, zero curve compute, no CollimationSieve API invention, `peak_byte_bound_schema_partial` / `charge_incidence_partial` retained as lineage, and numeric charge meters not instantiated.

## Snapshot binding

| Check | Result |
| --- | --- |
| Snapshot commit | `5281383b7662a9f750f3ee6f41e162f61d430311` |
| Bind / HEAD | `3ac519e1d61db88dea2227bb67c0a68f7f6eb6fa` |
| Snapshot ancestor of HEAD | yes |
| Receipt parent SHA | `86ab662b41fdee751dd0ae5567c221c40c75af25` (matches `5281383b^`) |
| Exact eleven-path archive scope | yes (ten producer sources + snapshot receipt) |
| All `source_path_sha256` vs `git show 5281383b` | 10/10 match |
| Archive touches CollimationSieve / BATCH-022 / ledger/ | no |
| Receipt `commit_sha` / verification | still `null` / `pending_post_commit` (non-blocking; Git checks establish durability) |

## Harness re-run

```bash
cd coordination/goals/GOAL-SSI-001/batches/BATCH-036/tasks/TASK-20260730-115
python3 -m charge_metering_harness.run_harness
```

| Field | Observed |
| --- | ---: |
| tests_run | 8 |
| failures / errors | 0 / 0 |
| was_successful | true |
| ledger_status | `charge_metering_schema_partial` |
| control_result | `FAIL` |
| item_count | 43 |
| family counts | 8+8+4+5+6+12 |
| status counts | wired_symbolic=32, checklist_only=1, not_instantiated=5, not_supported=4, deferred=1 |
| disposition | `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` |
| qm_memory_map | `charge_metering_schema_partial` (prior `peak_byte_bound_schema_partial`) |
| qm_stopping | open |
| qm_error | `f_union_ledger_partial` |
| peak_byte_bound_schema_partial retained | true |
| charge_incidence_partial retained | true |
| no_invented_numerics | true |
| numeric_charges_invented | false |
| peak_byte_bound_invented | false |
| clearance flags | all false |
| scaffold_mutated | false |
| collimation_sieve_apis_invented | 0 |

Re-run dirtied `harness_receipt.json` (timestamp / dict-key order). Restored from `git checkout 5281383b -- .../harness_receipt.json` to SHA-256 `d2616b243652a29a822eaae94ed50cd9d7d6faac58552e22e66a8673378b27ae`. Producer tree left clean; `__pycache__` / AppleDouble `._*` removed.

## Falsification targets

| Target | Result |
| --- | --- |
| Invented numeric charges / widths / peak-byte bounds / probabilities / security bits | **Not detected.** All item `charge_units` / `charge_accumulator` / `per_hook_charge` / `numeric_width` values are `null` / `not_instantiated`; `peak_byte_bound` is `unresolved` / `not_instantiated`. Coverage keeps `numeric_charge_meter` / `charge_meter_api` / `global_fc0_memory_bound` `not_supported`. Only ledger-edge cardinalities and run counters are numeric. `check_no_invented_numerics` hits=`[]`. |
| Illicit QUERY_MEMORY or QM-MEMORY-MAP clearance | **Not detected.** `clearance: false`, `reconciled: false`, `query_memory_cleared: false` across classification / memory_map / mutation / ledger summary. |
| Illicit QM-STOPPING clearance or invented τ / joint finiteness | **Not detected.** QM-STOPPING `open`; `control_result: FAIL`; `tau_invented: false`; `joint_finiteness_established: false`; BATCH-035/034/033/032/031/018 FAIL reconfirmed. |
| Fake metering completeness / PIN_COMPLETE | **Not detected.** `pin_complete: false`; disposition not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`; meter fields `not_instantiated` / `not_supported`; ledger_status is `*_partial`. |
| CollimationSieve@6f9188e4 API invention | **Not detected.** Archive paths exclude CollimationSieve; `apis_invented: false`; `collimation_sieve_touched: false`; status `host_gap_certified_retained_untouched`. |
| Equating ttm-v2 with BATCH-014 | **Not detected.** `equated_to_batch014: false` in classification, ledger coverage, and ttm_v2_scope. |
| Numeric security / breakthrough / goal-completion creep | **Not detected.** Mentions appear only in excluded statements / non-claims; `non_extrapolation: true`. |
| Disposition ≠ `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` when only placeholders | **Not detected.** Disposition exactly that string; evidence supports placeholder charge-metering obligations only. |

## Residual wording debt (non-blocking / scope-expansion guards)

These are **not** grounds to REJECT or REVISE the producer package; they bind downstream EV/DEC language:

1. Do not read `charge_metering_schema_partial` as MEMORY-MAP or QUERY_MEMORY clearance.
2. Do not read checklist / wired_symbolic / placeholder metering edges as instantiated charge meters, widths, or peak-byte bounds.
3. Do not read harness 8/8 as a MEMORY-MAP mathematical proof or a numeric charge-metering implementation.
4. Do not overload `artifact_commit_reference` with the CollimationSieve negative-control tip.
5. The scaffold `numeric_width: 128` reject probe is not a claimed width or charge.
6. `to_meter_surface` / clearance-target naming on `CM-PBB-global-fc0` (`QUERY_MEMORY_clearance`) is a named unsupported target under `not_supported`, not clearance.
7. Some harness receipt honesty flags are hardcoded literals; rely on YAML/Git checks already performed, not the receipt alone.
8. Naming `protocol_id: CSIDH-COLLIMATION-FC0-R2` is convention wiring only; units / meters remain uninstantiated.

## Lineage spot-checks

- BATCH-027 `HOOK-W_label-Q` / `HOOK-R_label-Q` / `HOOK-W_sieve-S` / `HOOK-R_sieve-S` / `HOOK-B_recovery-C` / `HOOK-M_tail-H` / `HOOK-accepted_transcript-P` exist; `HOOK-charge-meter` is `not_supported`.
- BATCH-035 `PBB-BP-peak_byte_bound` / `PBB-PD-protocol_id` / `PBB-PD-units` / `PBB-PD-accounting-rule-max-not-sum` / `PBB-BP-global-fc0-memory` exist.
- BATCH-033 `BIND-LH-W/R/B/M_tail-birth` exist.
- `peak_byte_bound_schema_partial` and `charge_incidence_partial` retained as lineage under advancement.

## Narrowest supported statement

Symbolic charge-metering obligation schema ledger (43 items; harness 8/8) advances QM-MEMORY-MAP honesty from `peak_byte_bound_schema_partial` to `charge_metering_schema_partial` with placeholders only on lifetime hooks, retains `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, keeps QM-STOPPING open under BATCH-035/034/033/032/031/018 FAIL, retains QM-ERROR `f_union_ledger_partial`, retains `peak_byte_bound_schema_partial` and `charge_incidence_partial` as lineage, invents no charges/widths/peak-byte/τ/APIs/BATCH-014 equation, does not instantiate numeric charge meters, and claims no numeric security, breakthrough, PIN_COMPLETE, or GOAL-SSI-001 completion.

## Written paths

- `coordination/goals/GOAL-SSI-001/batches/BATCH-036/tasks/TASK-20260730-117/red_team_report.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-036/tasks/TASK-20260730-117/falsification_review.md`

## Inference

- requested_policy: `review-xhigh`
- resolved_model: Cursor Grok
- fallback_used: true
- independent_session: true

## Harness re-run status

- Re-run: OK (8/8)
- Producer `harness_receipt.json` restored: yes (SHA-256 `d2616b243652a29a822eaae94ed50cd9d7d6faac58552e22e66a8673378b27ae`)
