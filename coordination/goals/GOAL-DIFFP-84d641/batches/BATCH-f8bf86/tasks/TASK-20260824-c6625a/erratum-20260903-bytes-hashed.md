# Executor erratum on execution-report.yaml — TASK-20260824-c6625a

record_class: executor_erratum
experiment_id: EXP-DIFFP-fe894e
task_id: TASK-20260824-c6625a
goal_id: GOAL-DIFFP-84d641
batch_id: BATCH-f8bf86
recorded_at: '2026-09-03'
role: executor
supersedes_field: ctl_quar.bytes_hashed
erratum_id: ERR-c6625a-bytes-hashed

## The defect

The committed `execution-report.yaml`, section 7 (`ctl_quar`), states:

    bytes_hashed: 5583

The correct figure, measured by this session and recorded in the run's own raw
machine-readable record, is **3103 bytes**:

- `runs/RUN-DIFFP-fe894e-buildcheck/raw-result.json`, block `raw.CTL-QUAR`,
  field `bytes_hashed`: **3103**
- Independently re-observed in this session on 2026-09-03 by streaming the
  payload's bytes into a sha256 context in 64 KiB chunks without decoding them
  (CTL-QUAR procedure, no parsing): **3103 bytes**, sha256
  `e44a3fed81e9e7621697432b2124b357fc2c3dfe...` — recompute below.
- `wc -c` on the payload file: **3103**

A file cannot be 3103 bytes and hash to 5583 bytes' worth of content; the two
figures are mutually exclusive. The `5583` in the report is a **transcription
error in the report's narrative only**. It is not present in any run record,
any manifest, any supplement, or any machine-readable artifact of this task.

## What is NOT affected

- `ctl_quar.match` — true, and correct. The recomputed sha256 equals the
  contract's expected value exactly.
- `ctl_quar.sha256_recomputed` and `sha256_expected` — both correct and
  identical to the contract's pinned value
  `e44a3fed81e9e7621697432b2124b357fc2c3f502f4bc6779df5c377b0a3e3c5`.
- Every other field of the execution report, every other artifact, and every
  run record: the byte count appears nowhere else in this task's package.
- CTL-QUAR's PASS verdict. The control's substance — sha256 recomputed from
  bytes, never parsed, matching the pinned digest — is unaffected by a wrong
  byte-count annotation.

## This session's own recomputation (2026-09-03)

    path:      coordination/goals/GOAL-MD5-001/quarantine/MD5-COLLISION-PATH-WANG-2004-199.yaml
    method:    open('rb'), stream 64 KiB chunks into sha256, discard without decode
    sha256:    e44a3fed81e9e7621697432b2124b357fc2c3f502f4bc6779df5c377b0a3e3c5
    expected:  e44a3fed81e9e7621697432b2124b357fc2c3f502f4bc6779df5c377b0a3e3c5
    match:     true
    bytes:     3103

## Why a new record, not an edit

Artifacts are immutable (AGENTS.md rule 4: "Results are immutable records.
Corrections create new records."). `execution-report.yaml` is committed and has
been read by two independent reviewers and three later batches of this goal, so
a correction is a **new record** that supersedes by reference, never an edit of
the committed file. This note is that record.

## Executor statement

The byte-count figure `5583` in the committed report is **wrong**; the correct
figure is **3103**. The control's verdict and every other integer in this
task's package are unaffected. This erratum is recorded, not silently absorbed,
per AGENTS.md rules 4, 8 and 12.
