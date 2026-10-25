# PR 2397 legacy adapter correction

This additive correction preserves the original pinned adapter, all five frozen
plans that bind it, and every historical attempt. It supplies a prospective v2
adapter and synthetic regression controls. The v2 source is not approved for
execution by any current experiment packet; `execution_authorized` remains
false in the [proposed binding](proposed-source-binding.json). Coordinator
allocation, prospective source binding, approval and native admission are still
required before any use in a new experiment.

The original adapter at `tools/legacy_trial_manifest.py`, SHA256
`973bc4e18a12e548ec1659d686bef65350126e6646639f38ef941d5bc84575b9`, has two
reproduced defects. A synthetic failed child writes a third binary file; only
the two declared files survive, and removal of the temporary directory loses
the extra bytes. A separate synthetic case changes the adapter wall time to
-5 seconds and its finish timestamp to precede its start, then regenerates the
corresponding envelope; the original checker accepts that inconsistent timing.
These cases establish missing preservation and validation checks. They do not
establish that any retained historical run lost extra output or has bad timing.

The new `tools/legacy_trial_manifest_v2.py` preserves unexpected regular files
in the failure receipt using their bytes and SHA256, records links without
following them, and refuses successful acceptance when undeclared outputs exist.
It checks nonnegative finite adapter timing and ordered timezone-aware intervals
for both child phases inside the adapter interval. It also checks runtime and
exact artifact coverage, canonical scalar types, integer return codes, new
specification identity, and existing dangling output links. Malformed legacy
YAML remains a failed attempt with the available original bytes retained.
If output reading or copying fails, the scratch directory remains and the failure
receipt records its location. If receipt persistence fails, stderr records the
retained location. Cleanup happens only after preserved bytes and the receipt
are persisted; two injected read/write failures cover this path.
Its receipt schema is versioned; no historical receipt is converted.

The frozen three-output `legacy_stage0_manifest.py` has the same cleanup-on-I/O-
failure problem. A separate prospective `legacy_stage0_manifest_v2.py` applies
that preservation fix, with its own [source binding](proposed-stage0-source-binding.json).
All 25 synthetic controls pass, including the two injected read/write failures.
Neither of its two approved plans is rebound. Together the two prospective
suites pass 48 tests and 29 subtests. The staged tar adapter already preserves
a verified complete archive before cleanup; snapshot failure retains its workspace.

All 23 v2 tests use synthetic metadata producers and temporary repositories.
The original three-adapter suite independently passed 45 tests and 29 subtests.
The separate worksheet metadata/arithmetic software suite passed 22 tests and
failed one Linux-specific fixture assumption: `/bin/sh` and `/usr/bin/sh` do
not resolve to the same executable on this macOS host. That result is recorded
as a local validation limit; it does not establish a runtime invocation defect.

The retained packet's 41 native receipts have 448 matching artifact hashes.
Its 43 plan documents have 402 matching source/specification bindings, representing
142 distinct path/hash pairs. Recorded statuses remain 32 `output_validated`,
7 `invalid_output`, and 2 `infrastructure_error`. These are integrity checks,
not a fresh scientific execution or an independent mathematical certification.
The historical report `EXP-ECDLP-3521b9/reports/run-20261018T0450Z/metrics.json`
contains absence prose rather than JSON; its bytes remain historical evidence,
and the corresponding `report-data.json` records missing metrics as null.

The review also checked 47 completed archive records against Git: all 1,880
path hashes, exact changed-path sets, recorded parents and HEAD ancestry match.
All 255 selected copied-report fields and original-byte comparisons match
the canonical retained records. Native queue validation with its repository
verifier passes 29 of 30 saved queues. The sole refusal is the preserved,
rejected duplicate-ownership proposal in `BATCH-7ddcd6/first-successor-failure`;
its later distinct preservation queue passes. This does not turn the rejected
proposal into an accepted queue.

Six additive schema records under `schema/` now supply missing metadata from
the retained native receipts, commands, environment and frozen specifications.
The exact original/replacement hashes are registered in the existing run
supersession registry. All six retain `status: invalid_output`, `result.valid:
false`, and null scientific conclusions. Unknown dirty state and numeric seed
remain null. The four records that omitted canonical `run.id` use the existing
explicit null-id provenance mechanism, binding the original `run.run_id`, native
receipt and directory identity. No parser or schema rule is relaxed.
The six routed records pass existing schema and hash/identity checks; all 60
original-manifest schema errors are resolved additively. Historical full-ledger
counts remain historical observations rather than a statement of current CI.

The [problem record](../../../problems/legacy-adapter-output-preservation.md) tracks
the remaining prospective binding obligation. The CI scope gate now runs after
its scope producer and accepts either explicit boolean ledger decision.
Current-head CI remains a separate merge gate.
No hypothesis, goal, original protocol, or scientific status is promoted here.
