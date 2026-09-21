# TASK-20260908-5c0cc3 — S6 plan-origin and JSONL-bound correction

This eight-file successor implements the two source-only corrections approved by
`DEC-20260908-e58724`. It began from all eight S5 files archived at
`6bf2c6b26359c10cb816239b6a9a4729a32f0507`; every copied blob matched before
editing. The complete scientific fixtures, seeds, RNG consumption, estimators,
thresholds, counts, controls, charged-operation conventions, finalizer, streaming
architecture, and passing V/S2/S3/S4/S5 behavior remain unchanged.

All 103 handoff inputs were read at authority commit
`ede5a161aab6db8625d3ed086d52caa0a6d32bec` and matched their declared SHA-256
bindings. The published task claim is
`75687bffdda7da129df7e53032642454f113135e`. The independent review snapshot
`e3362f52cbd1b50831bffd39fb23c0295617e9a1` supplied findings S5V-01 and S5V-02;
it supplied no scientific evidence.

`verify_review_admission` still requires the complete canonical
source → plan → claim → completed release → archive → external authority →
executing-commit ancestry. The current review plan must now be present in the
reviewer's declared input and source-binding inventories. Its binding digest and
attested read digest must both equal `review_plan_sha256`, and its bytes are
resolved only at the independently verified `review_plan_commit`. Every other
declared source or historical input is resolved at
`reviewed_source_snapshot`. The implementation provides no general later-commit
fallback and does not backdate the plan into the source snapshot.

`streaming.iter_jsonl` now checks every located newline offset before converting
the record to `bytes` or calling `json.loads`. It retains the existing
no-newline oversize guard, checks the current pending record again after earlier
records are removed, and performs an explicit EOF length check before converting
or parsing an unterminated record. A record whose byte length exactly equals
`maximum_record_bytes` remains valid with or without a trailing newline. A
one-byte-over record raises `StreamingEncodingError` whether its newline is in
the first chunk, crosses the 64 KiB chunk boundary, or is absent.

The complete fixed suite contains 107 cases. Two complete invocations executed
214 cases total, all passing with zero errors and zero timeouts. The final
invocation ran from `2026-09-09T06:06:45.939734+00:00` through
`2026-09-09T06:07:31.543848+00:00`; it recorded 42.534957 seconds of internal
wall time, 5.839952 seconds of internal CPU, 45.60 seconds of external real time,
38.81 seconds of external user-plus-system CPU, and 60,112,896 bytes maximum
resident set size. Both invocations used one worker and remained below 10 seconds
per case, 1,800 aggregate executed-check wall/CPU seconds, 640 total cases, and
8 GiB observed RSS.

The suite used only fixed lower-level arithmetic, static, synthetic Git,
serialization, telemetry, custody, and temporary-artifact helpers. It did not
invoke a fixture or candidate search, scientific generator or census, null or
control panel, timing panel, Sage/PARI measurement, `future_cell`,
`run_future_pipeline`, `verify_launch_admission`, Docker/runtime launch, key,
signature, nonce, lock, run allocation, `RUN-*` record, or prospective pipeline
even in mocked form. Therefore this package reports source conformance only. It
does not report a launch, measurement, ECDLP result, performance result,
hypothesis update, or cryptanalytic conclusion.

Both test invocations opened temporary stdout and stderr paths before child
launch, used `PYTHONDONTWRITEBYTECODE=1 python3 -B`, retained exact nested
stdout/stderr and `/usr/bin/time -lp` telemetry, and yielded outer
`exec_command` sessions that were polled to terminal before the next
invocation. The regression receipt preserves every outer response, including
the intermediate polls.

One operational deviation occurred before source editing: the patch tool first
resolved the eight byte-identical S5 copies in the repository checkout instead
of this dispatched worktree. The files and resulting empty directory were
removed immediately, no test ran there, no shared tracked file was changed, and
a read-back confirmed no residual path. The copies were then recreated and
verified byte-identical in the declared worktree. This asserts nothing about the
source correction or the science.

`implementation_commit` remains null because only the Coordinator snapshot
task `TASK-20260908-69f5db` may create the implementation commit. The checkout
base used for this execution is
`f7b9eeba61b3924854f7647c0de77d53199ab30b`. A fresh independent complete
source review is still required before any admission decision.
