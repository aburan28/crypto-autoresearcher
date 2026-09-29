# TASK-20260908-e34baf — S5 spectral source architecture

This eight-file successor implements the source-only corrections approved by
`DEC-20260908-2dafc2`. It began from the six-file S4 package archived at
`2c2b45a5772894c4bd0431cb2b5da45775382328`; the six baseline blob hashes
matched before editing. The S4 producer remains failed, and nothing here
repairs or reinterprets its missing historical execution telemetry.

All 88 handoff inputs matched their declared SHA-256 values in the live tree
and at published authority commit
`ee5651080733bd636de222fc4989334081fa80f5`. The published task claim resolves
to `6a83995ef8221e737a76472aa78f714ce510fc72`. The archived independent S4 review
at `04cc7b523f957d3a7b9347d5e1084586eb1de437` supplied four source findings;
it supplied no scientific evidence.

`verify_review_admission` now applies the source-pinned canonical queue
validator to deep copies of both the claimed queue and completed authority
queue, so every task is validated and the admitted object is never mutated.
The complete review handoff is checked, inline and path-bound plans resolve to
the same precommitted plan, every plan subsection is validated, and all claimed
review-task declarations except explicit state/lease bookkeeping remain
frozen. Every handoff input digest must equal the attested read digest and the
reviewed Git blob. Exact output/release hashes and the
source → plan → claim → release → archive → authority ancestry remain binding.
Only local validator modules and dependencies whose hashes are embedded in the
reviewed source are loaded; no code is executed from an external commit.

`streaming.py` provides deterministic guarded JSON/JSON-as-YAML, JSONL, CSV,
copy, hash and readback primitives. Each encoded/read/written fragment is at
most 64 KiB. Integer mapping keys are refused instead of silently becoming
strings. Final artifacts stream directly to their staging files and are hashed
during that same pass. Large cells, fixture histories, scientific certificates,
partial certificates and diagnostics live in append-only spools. The runner
retains one current bounded cell and a compact 96-cell held-out decision reducer
in memory, rather than complete parallel histories.

`custody.py` contains the one `finalize_run` helper used by the production path
and fixed tests. It streams and verifies the payload, durably publishes it,
captures timing through that durable boundary, and then durably publishes
`runtime-custody/<run_id>/operational-completion.json`. The operational receipt
explicitly excludes its own write, rename and fsync duration and has no
self-hash. If companion publication fails after payload rename, the payload is
quarantined or marked incomplete. A cancellation, resource, infrastructure or
measurement stop retains its original type and carries every secondary custody
failure. Progress cleanup occurs only after both durable records exist.

Scientific certificates use their own append-only spool and no longer consume
one progress event per successful scalar certificate. Existing caps remain:
1,024 bytes per progress event, 256 MiB for the append log, 64 KiB for the
latest checkpoint, and a 250 ms maximum RSS polling interval between eligible
guard opportunities. Signals are checked at every existing opportunity, and
the required scientific prefix is flushed before an actual probe or stop. The
static frozen maximum is 192 cells and at most 781,824 scalar-certificate
records. `floor(256 MiB / 1,024) = 262,144` is a safe progress-event cap; none
of these values guarantees completion or reports measured performance.

Within each future cell, all seven frozen shuffle assignments, RNG counter ends
and bucket counts are now constructed and retained before occupancy is reduced.
An occupancy mismatch records seven completed assignments and zero started null
censuses, then stops. Only a valid assignment set enters the separate seven-arm
null-census loop. RNG results, charged operation conventions, estimators,
thresholds, relabel stops and scalar-certificate stops are unchanged.

The complete fixed suite contains 94 cases. Two fully retained invocations
executed 188 cases total, all passing with zero timeouts. The final invocation
ran from `2026-09-09T04:38:07.758090+00:00` through
`2026-09-09T04:38:50.091143+00:00`, reported 39.633318 seconds internal wall,
5.533481 seconds internal CPU, 42.32 seconds external real, 15.60 seconds user,
19.39 seconds system, and 61,800,448 bytes maximum external RSS. The exact
commands, initial and terminal tool results, yielded session IDs, complete
stdout JSON, full stderr/time output, all case rows and aggregate accounting are
in `regression-receipt.json`. No hard RLIMIT_AS/cgroup enforcement is claimed.

The tests used only fixed lower-level arithmetic, static inspection, mock I/O,
temporary Git histories, lazy synthetic payloads and temporary artifact roots.
They invoked the actual production finalizer. They did not invoke fixture or
candidate search, a scientific census, null/control/timing panel, Sage/PARI,
`verify_launch_admission`, `future-run`, the prospective pipeline, a real key,
signature, nonce, lock, run allocation or `RUN-*` directory.

The package remains pending Coordinator snapshot archive
`TASK-20260908-9ef3ea` and a fresh independent complete source review. It does
not claim protocol completion, measurement admission, launch admission,
scientific evidence, performance, a hypothesis conclusion or a research-state
change.
