# TASK-20260908-a58827 — S3 spectral source-conformance repair

This six-file package is the immutable repair successor authorized by
`DEC-20260908-fd696a`. It starts from the byte-identical six-file source package
at `TASK-20260908-111152` / snapshot `1cf7cc7004bd058eb92b81d65f05e89f6aff71d0`.
All V-01 through V-08 and S2-01 through S2-08 behavior remains in the copied
driver and fixed regression suite. This task changes source definitions and
fixed synthetic/mock conformance checks only. It creates no run allocation,
key, signature, lock, `RUN-*` directory, future-run invocation, fixture
selection, candidate search, census, control panel, timing panel, or ECDLP
measurement.

S3-01 makes future review admission bind the actual completed validator task in
the external authority queue. The verifier requires that task's nested
`review-adversarial` / `xhigh` handoff, exact declared output set, archived
output hashes, standard PASS attestation, one plan-owned joint, and source
read hashes. Claim ownership is read from the queue-relative write-once
`goal_lanes.py` claim/release blobs and their Git commits. The control-plane
claim owner/session/epoch is checked against those blobs; independent native
reviewer provenance remains the separate inference envelope.

S3-02 treats the `runs/` parent-directory fsync as part of quarantine
durability. A failed parent fsync records `parent_directory_fsync_failed`,
sets `state: quarantine_parent_fsync_failed`, and leaves
`quarantine_complete: false`. A failed failure-receipt write retains the prior
S2 distinction: even when a move succeeds, the absent durable receipt leaves
the state `unretained`.

S3-03 records each failed scalar certificate, then records a
`partial_invalid_cell` record and raises `MeasurementInvalidStop` before any
later collision start, arm, control, or cell can run. S3-04 wraps coordinate
and null collision censuses in `measured_diagnostic`, which writes one completed
or interrupted row with actual process-group RSS start/end/peak observations.
Unavailable telemetry is an `InfrastructureStop`; no memory value is invented.

S3-05 supplies durable progress callbacks before bounded guard probes in
subgroup enumeration, collision starts and steps, coordinate partitioning,
constant-O control work, artifact assembly, and publication. The future path
keeps cancellation handlers installed through guarded artifact construction and
publication. Publication failures still route through the typed custody receipt.

The final regression suite has 58 fixed static/synthetic/mock cases. It uses
temporary synthetic Git graphs and temporary artifact directories only. It
passed on its final attempt. Earlier failed attempts and their telemetry are
retained verbatim in `regression-receipt.json`; they are implementation-test
history, not mathematical observations.

This package is pending Coordinator snapshot task `TASK-20260908-cbd974` and a
fresh independent complete source review. It does not assert implementation
approval, launch admission, measurement readiness, a scientific result, or a
hypothesis conclusion.
