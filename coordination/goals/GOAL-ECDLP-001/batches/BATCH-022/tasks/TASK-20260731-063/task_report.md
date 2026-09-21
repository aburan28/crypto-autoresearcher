# TASK-20260731-063 — Author PA-DS-001-v2-ctrl-theater-r2

## Status

Completed (authoring). Snapshot archive is TASK-20260731-064.

## Eligibility

This Coordinator session did **not** author TASK-20260731-054
(BATCH-021 `PA-DS-001-v2-ctrl-theater-repair`). Eligible under DEC-015 /
RC-21 cycle-cap ruling for a fresh out-of-batch amend. DEC-015 does not
require idea-generator authorship.

## Inputs

- DEC-20260731-015 RC-21 non-execution; exact next_action BATCH-022
- RT-20260731-056 REVISE (RT056-B1 soft destroy; RT056-B2 equivalent-FLAG)
- RT-20260731-047 / RT047-B3 theater residuals
- EXP-DS-001 `specification.v2.yaml` (sha256 `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a`)
- Parent approval snapshot `65f3c82b` / DEC-20260731-003
- Rejected BATCH-021 freeze at `98fa35db` (immutable; not edited)

## Deliverables

- `experiments/EXP-DS-001/amendments/v2_ctrl_theater_r2.yaml` (`PA-DS-001-v2-ctrl-theater-r2`)
- `experiments/EXP-DS-001/controls/CTRL-RT056-PLANT-CLOSED-PATH.yaml`
- `experiments/EXP-DS-001/controls/CTRL-RT056-RHO-CALIB-AUDITED.yaml`
- `experiments/EXP-DS-001/controls/CTRL-RT056-NULL-SPLIT-HARD-DESTROY.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-022/QUEUE-AMEND-20260731-007.md`
- `ledger/decisions/DEC-20260731-016.yaml`
- This task report

## Co-required controls (this batch)

| Control | Residual discharged |
|---|---|
| CTRL-RT056-PLANT-CLOSED-PATH | RT056-B2 / RT047-B3 — closed `{null_gate_f2_shape}`; forbid echo entailment |
| CTRL-RT056-RHO-CALIB-AUDITED | RT038-B3 rho + RT056-M1 raw fields; ±0.15 deferred |
| CTRL-RT056-NULL-SPLIT-HARD-DESTROY | RT056-B1 — `destroy_demonstrated` iff `R_null < 0.9`; falsifiability_failed terminal |

Default cell: bits=20, B=64, m=4, seed=101.

## Deferred (named, not executed in BATCH-022 run)

- CTRL-RT025-CI-IDENTITY
- CTRL-RT025-SPARSE-P-SUCCESS

## Non-actions

- No edit to `specification.yaml` / `specification.v2.yaml` / v1 freeze blob
- No edit to rejected BATCH-021 freeze blobs
- No Executor run authorized by this task
- No full 54-cell matrix re-run
- No HEUR re-run
- No change to H-IC-001 or H-STR-002
- No STR reopen
- Unauthorized `RUN-DS-001-ctrl-theater` worktree artifacts ignored as non-binding
- EV-DS-002 / EV-DS-003 / EV-DS-004 remain immutable prior records

## Supersession

Supersedes a parallel draft that deferred amend text to idea-generator
TASK-065 / `PA-DS-001-v2-rt056-discharge`. Handoffs TASK-072/073 from that
draft are unused by this queue.
