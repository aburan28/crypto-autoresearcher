# TASK-20260908-4cacf0 — S4 spectral source, admission, and custody repair

This six-file successor is authorized by `DEC-20260908-afe5b9` and starts as
an exact copy of the `TASK-20260908-a58827` package at snapshot
`44a9e000bb8a4a8e77eff58817f44726b62ba72e`. The initial six blob comparisons
matched exactly. All 70 declared input bindings matched both the live bytes
and the published authority commit
`7b36178fe6c0cc92242071bf42cb4e81c5aa0cc9`; the published task claim resolves
to `703ce4e36485c8b8d89211147790914dc46a6b75`.

The repair preserves every frozen scientific fixture, seed, RNG construction,
count, cost reduction, threshold, and control. It changes the future runner's
source-level operational custody and only exercises lower-level fixed,
synthetic, mock, and temporary-Git conformance cases. It creates no scientific
fixture or candidate, collision census, null/control/timing panel, Sage/PARI
measurement, prospective pipeline invocation, key, signature, nonce, lock,
run allocation, or `RUN-*` directory.

`verify_review_admission` now requires the canonical dispatch-queue schema and
the complete nested validator handoff, source bindings, review plan, exact
source reads, queue-relative write-once claim/release records, source-pinned
dispatch/lane validators, and a standard `review_attestation.verdict: holds`.
It enforces the strict review-plan → claim → completed-release → archive →
external-authority lifecycle, exact release hashes for every reviewer output,
and an archive receipt separate from reviewer output hashes.

Diagnostic rows now name actual start and end samples plus
`process_group_rss_boundary_sample_max_bytes`; they never label a two-boundary
maximum as a continuous peak. Successful coordinate/null diagnostics are
serialized only from their canonical cell row. Interrupted diagnostics alone
enter the partial stream. Unavailable telemetry remains an
`InfrastructureStop` with a retained interruption row.

Construction, hashing, writes, and verification use chunks no larger than
64 KiB with guarded checkpoints. Cancellation and resource stops retain their
typed classifications through publication. Future-run timing reaches durable
payload publication, then a separate `progress/operational-completion.json`
receipt is written and fsynced outside that measured boundary; it makes no
self-inclusive timing or self-hash claim. The progress tree remains on typed
construction or publication failure.

Progress has an append-only, at-most-1024-byte event log and one atomically
replaced compact latest checkpoint. The event log is capped at 256 MiB and the
latest checkpoint at 64 KiB; a cap breach is a retained `ResourceStop`. The
safe cap is `floor(256 MiB / 1024) = 262,144` events. This is linear in
retained events and replaces the predecessor's all-history rewrite. The guard
records requests, actual RSS polls, event count, and bytes; its 250 ms cadence
is a sampling policy, not a real-time scheduling guarantee. The frozen maximum
panel has 192 cells (`4 × (8 exploratory + 8 held-out) × 3`); the cap provides
a safe operational stop rather than an unsupported completion estimate.

After the seventh shuffle assignment, occupancy is reduced and retained before
any relabel work; an occupancy failure emits `partial_invalid_cell` and stops.
The exact relabel result is likewise retained and checked before constant-O,
mutated-verifier, or Cayley work. These are source conformance repairs, not
new observations.

The final fixed suite contains 79 cases and passes. The receipt retains the
known failed/debugging attempt and a separate wrapper-interrupted invocation
whose per-case telemetry was not available; it reports a conservative maximum
of 237 cases against the 640-case ceiling. Requested 8 GiB `RLIMIT_AS`
installation failed on this host, so no hard memory-limit success is claimed.

The package remains pending Coordinator archive `TASK-20260908-5abf3c` and a
fresh independent source review. It does not claim implementation approval,
measurement admission, launch admission, a scientific result, or a hypothesis
conclusion.
