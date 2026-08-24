# Falsification review — TASK-20260730-101 / BATCH-032

## Verdict

**CONFIRM**

Producer package TASK-20260730-099 (snapshot `d437b16c`) matches the expected honest MEMORY-MAP schema package: disposition exactly `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, QM-MEMORY-MAP advanced to `width_schema_partial` without clearance, QM-STOPPING open with `control_result: FAIL` (BATCH-031/018 retained), QM-ERROR `f_union_ledger_partial` retained, placeholders only, harness 8/8, `non_extrapolation: true`, zero curve compute, no CollimationSieve API invention.

## Snapshot binding

| Check | Result |
| --- | --- |
| Snapshot commit | `d437b16c25e9021b13a09fac79c04b2fcb20f6be` |
| Bind / HEAD | `91bb6d68bc05f77a191ca86f2157f7ac7df181e6` |
| Snapshot ancestor of HEAD | yes |
| Receipt parent SHA | `8a109a8087833d2c7aee67baf8a18b6f4e7d6e42` (matches) |
| Exact eleven-path archive scope | yes |
| All `source_path_sha256` vs `git show d437b16c` | 10/10 match |
| Receipt `commit_sha` / verification | still `null` / `pending_post_commit` (non-blocking; Git checks establish durability) |

## Harness re-run

```bash
cd coordination/goals/GOAL-SSI-001/batches/BATCH-032/tasks/TASK-20260730-099
python3 -m width_schema_harness.run_harness
```

| Field | Observed |
| --- | ---: |
| tests_run | 8 |
| failures / errors | 0 / 0 |
| was_successful | true |
| ledger_status | `width_schema_partial` |
| control_result | `FAIL` |
| item_count | 25 |
| family counts | 6+5+3+3+8 |
| status counts | wired_symbolic=11, checklist_only=4, not_instantiated=6, not_supported=3, deferred=1 |
| disposition | `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` |
| qm_memory_map | `width_schema_partial` (prior `history_uniform_tail_partial`) |
| qm_stopping | open |
| qm_error | `f_union_ledger_partial` |
| no_invented_numerics | true |
| clearance flags | all false |
| scaffold_mutated | false |
| collimation_sieve_apis_invented | 0 |

Re-run dirtied `harness_receipt.json` (timestamp). Restored from `git show d437b16c:.../harness_receipt.json` to SHA-256 `445249f4757364bf9fb44f7b3f2813e7059b76eba5894bb9beac1fec5953af24`. Producer tree left clean; `__pycache__` / AppleDouble `._*` removed.

## Falsification targets

| Target | Result |
| --- | --- |
| Invented numeric widths / peak-byte bounds / probabilities / security bits | **Not detected.** All item `numeric_width` / `peak_byte_bound` values are `null` / `unresolved` / `not_instantiated`. Only ledger-edge cardinalities and run counters are numeric. `check_no_invented_numerics` hits=`[]`. |
| Illicit QUERY_MEMORY or QM-MEMORY-MAP clearance | **Not detected.** `clearance: false`, `reconciled: false`, `query_memory_cleared: false` across classification / memory_map / mutation / ledger summary. |
| Illicit QM-STOPPING clearance or invented τ / joint finiteness | **Not detected.** QM-STOPPING `open`; `control_result: FAIL`; `tau_invented: false`; `joint_finiteness_established: false`; BATCH-031/018 FAIL reconfirmed. |
| Fake schema completeness / PIN_COMPLETE | **Not detected.** `pin_complete: false`; disposition not `FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW`; global FC0 memory bound `not_supported`; lifetime-trace-with-widths `deferred`. |
| CollimationSieve@6f9188e4 API invention | **Not detected.** Archive paths exclude CollimationSieve; `apis_invented: false`; `collimation_sieve_touched: false`; status `host_gap_certified`. |
| Equating ttm-v2 with BATCH-014 | **Not detected.** `equated_to_batch014: false` in classification, ledger coverage, and ttm_v2_scope. |
| Numeric security / breakthrough / goal-completion creep | **Not detected.** Explicit excluded statements and `non_extrapolation: true`. |
| Disposition ≠ `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` when only placeholders | **Not detected.** Disposition exactly that string; evidence supports schema placeholders only. |

## Residual wording debt (non-blocking / scope-expansion guards)

These are **not** grounds to REJECT or REVISE the producer package; they bind downstream EV/DEC language:

1. Do not read `width_schema_partial` as MEMORY-MAP or QUERY_MEMORY clearance.
2. Do not read checklist / wired_symbolic / placeholder slots as numeric instantiation or peak-byte accounting.
3. Do not read harness 8/8 as a MEMORY-MAP mathematical proof.
4. Do not overload `artifact_commit_reference` with the CollimationSieve negative-control tip.
5. Scaffold Verify smoke and the `numeric_width: 128` reject probe are not claimed widths or crypto Verify.

## Narrowest supported statement

Symbolic numeric-width / peak-byte obligation schema ledger (25 items; harness 8/8) advances QM-MEMORY-MAP honesty to `width_schema_partial` with placeholders only, retains `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, keeps QM-STOPPING open under BATCH-031/018 FAIL, retains QM-ERROR `f_union_ledger_partial`, invents no widths/charges/peak-byte/τ/APIs/BATCH-014 equation, and claims no numeric security, breakthrough, PIN_COMPLETE, or GOAL-SSI-001 completion.

## Written paths

- `coordination/goals/GOAL-SSI-001/batches/BATCH-032/tasks/TASK-20260730-101/red_team_report.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-032/tasks/TASK-20260730-101/falsification_review.md`

## Inference

- requested_policy: `review-xhigh`
- resolved_model: Cursor Grok
- fallback_used: true
- independent_session: true
