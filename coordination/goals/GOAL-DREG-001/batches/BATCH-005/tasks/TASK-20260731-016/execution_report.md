# Execution report — TASK-20260731-016 (CTRL-B n=12 D=6)

## Summary

Fresh chunked CTRL-B measurement completed under write_scope
`coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/`.

| Field | Value |
| --- | --- |
| validity | `completed_valid` |
| `ctrl_b_admission_status` | `admitted` |
| `deficit_genuine_admitted` | **true** |
| `rank(null\|sem_support)` | 156520 |
| `deficit_genuine` | 156520 − 138573 = **17947** |
| expected_interval | [1931, 17947] |
| peak RSS | 6.67 GiB (under 8 GiB) |
| wall | 2298 s (under 3600 s) |

## What ran

1. Rebuilt sem/null from `(n=12,t=3,ti=0,seed=2026)`; system hashes matched CTRL-A pins.
2. Reused null adjacency pickle (sibling worktree path); column-by-column identical to
   independent in-process rebuild (`sha256=9cb27677…`).
3. Deleted exactly `null_support \\ sem_support` (16016 deg-6 columns); kept 174035.
4. Published set digests (`sha256_sorted_monomial_canonical_v1`):
   - `restricted_support_hash=8a1bf796ccb340181af0c78920e9ebc9d527743d87d6053333ed3d4cbb7bae17`
   - `deleted_set_hash=a0203e81cd0947aea405bdb7c7ae98b2ddd60c970b96b1a7d2a5caf4b5d6809b`
5. Ran `src/h012c_block_m4ri.py` `process_subchunk` over all 174035 restricted columns
   (`chunk_force=12000`, 15 units, exact-once coverage). Did **not** use unchunked
   `DREG_dff.sage`.
6. Evaluated `CTRL-B-Q-MACHINE-v1` and all protocol `admission_metrics` — all passed.

## Quarantine / claim boundary

- `raw_headline_status: quarantined_confounded` with `raw_headline_value: 17947` retained.
- Numerically, admitted `deficit_genuine` equals 17947. Per Q4 this may be cited as
  **structural only** with `structural_metric_id=deficit_genuine` from this admitted
  receipt — **not** as `deficit_vs_sr_pred` / `raw_deficit`.
- This is a **structural number for this frozen cell only**. It is **not** a `d_reg`
  theorem, **not** crypto-scale evidence, and does **not** by itself change
  `H-DREG-001` ledger status (Coordinator decision required).

## Protocol deviations

- Null adjacency pickle was read from sibling worktree
  `claude-dreg-law/.../d6-null/work/` because this worktree’s copy is absent; content
  was independently rebuilt and matched bytewise before ranking.
- Inference fallback: `executor-terra` → `cursor-grok-4.5-high-fast`
  (`AMEND-PATH-001-001`, `fallback_used: true`).

## Artifact paths (snapshot inputs for TASK-20260731-025)

- `.../TASK-20260731-016/run_manifest.yaml`
- `.../TASK-20260731-016/results.json`
- `.../TASK-20260731-016/execution_report.md`
- `.../TASK-20260731-016/stdout.log`
- `.../TASK-20260731-016/stderr.log`

Supporting (same write_scope): `ctrlb_execute.py`, `column-audit.json`,
`raw-result.json`, `chunk-coverage.log`.

```yaml
execution_report:
  experiment_id: EXP-DREG-001
  task_id: TASK-20260731-016
  implementation_commit: ac403817cde1cc15104aa62742da4ef4087a284f
  protocol_deviations:
    - null_adj_pickle_reused_from_sibling_worktree_with_independent_rebuild_match
    - inference_fallback_executor_terra_to_cursor_grok_4_5_high_fast
  runs:
    completed:
      - RUN-DREG-001-CTRLB-N12-D6-BATCH005
    invalid: []
    failed: []
  observations:
    - rank_null_restricted=156520
    - deficit_genuine=17947 admitted under CTRL-B-Q-MACHINE-v1
    - raw_17947 remains quarantined_confounded as raw_headline
  anomalies:
    - >-
      Measured deficit_genuine equals quarantined raw headline (17947); permitted
      by Q4 only when cited as deficit_genuine after admission.
  artifact_paths:
    - coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/run_manifest.yaml
    - coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/results.json
    - coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/execution_report.md
    - coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/stdout.log
    - coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/stderr.log
  executor_assessment:
    protocol_complete: true
    data_quality: good
    requires_rerun: false
```
