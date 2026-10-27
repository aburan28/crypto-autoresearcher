# Modal export adapter source preparation

2026-10-27. This adapter derives from the unchanged source-A
`protocol/export_bundle.py`, SHA-256
`2c131774e80cb1917b3121bdf380848d8c66304e585e5c718bbf45a01bc8687f`.
`export-source-A.diff` records the exact changes. Native source, original
exporter, frozen analysis, counter families, target-prefix arithmetic and
public verifier are preserved.

The new exporter names canonical backend `modal` and records actual Sandbox,
App and Image SDK identifiers from the hash-pinned provider context. It checks
the frozen source-A/source-B, adapter/build and placement bindings. One official
row remains one confirmed child invocation with 64 sequential target slots;
whole-child rusage appears once. All clocks remain `wall_valid:false`.

The seven original counter families and event/state sequences retain their
exact JSON-encoded integer arrays. Integers above 2^53 in scalar export fields
are decimal strings. They are never converted into a runtime price or added
across overlapping snapshots. Partial malformed streams are hash-checked in
full, retain their parseable rows and raw artifacts, carry explicit parse
findings, and produce excluded infrastructure outcomes. Frozen analysis keeps
its original strict parser.

`attempts:0` unattempted slots and `attempts:null` unresolved spawns stay outside
official v1 run rows, whose schema requires at least one known attempt.
Unresolved metadata explicitly retains `outcome_class:not_completed`; backend
coverage records all missing slots. No rows, rusage, target answers or counts
are invented to satisfy the planned panel. Official coverage findings remain
in the additive validation receipt.

A public verifier's passing status qualifies rows only when its input hashes
bind each original native stream or all exact native parts, using the existing
frozen analysis law. Target, witness and producer-status coverage must also
match. A stale or unrelated passing summary remains an error/exclusion with
binding findings; it cannot label current bytes verified. Raw-manifest protocol
and actual-child input-manifest pins are checked separately.

Three focused software tests use fixed text fixtures, no valid EC cohort and no
native executable. The complete 768-child text panel passes the actual official
`check-export --verify-files` command. A partial/truncated panel with unresolved
and unattempted slots passes the official JSON schema while the actual checker
reports its coverage shortfall. Tests compare every counter family against the
old exporter, verify exact large integers and one-child rusage scope, refuse a
stale passing verification label, and check original/all-part hash bindings.
Their verifier summaries are explicitly software stubs; no public equations
were evaluated and no scientific verification is claimed.

Source review before the change covered the task's `engine-notes.md` sources,
the original exporter, `protocol/analysis.py` (especially native-stream hash
binding), `verification/verify_public.py` summary construction,
`schemas/experiment-export.v1.json`, and the official
`tools/experiment_protocol.py` schema/lint/coverage checks. This is a bounded
software and representation change; it introduces no mathematical mechanism,
new experiment, performance observation, literature claim or graph change.
