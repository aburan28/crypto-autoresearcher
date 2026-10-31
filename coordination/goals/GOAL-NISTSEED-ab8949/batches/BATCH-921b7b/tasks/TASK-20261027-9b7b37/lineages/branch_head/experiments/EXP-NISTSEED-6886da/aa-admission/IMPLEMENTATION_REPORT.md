# Actual-output follow-up, 27 October 2026

The first real public101 A/A pair exposed a total-time footer that the original semantic filter retained. The producer now omits only explicitly parsed elapsed-time fields and retains normalized checker step index, discriminant and acceptance values. Four retained output fixtures reproduce the mismatch; a changed checker result and an unknown time-like event remain distinguishable. All six mocked/fixture methods, including the JSON schema checks, pass. The corrected producer also replays two retained actual controls successfully without starting a new VM.

The separate full-cohort investigation is in `research/nist_seed_ecpp_full_cohort_20261027/REPORT.txt`. Its frozen source commit is4c7298e5212f523642c782483cd28f4bd5000d66, before this producer correction. The complete evidence archive preserves that snapshot, all original failures and both full-cohort format diagnostics. It does not identify the historical selection criterion. Earlier source-only task/archive statements below describe their original dated scope.

# TASK-20261025-ad9d68 corrected-v3 source-only implementation report

`named_orders_executed: 0`
`legacy_program_executed: false`
`VM calls: 0`
`storage attempts: 0`

## Observed input availability

The earlier candidate observed that the four uncompressed payload paths were
absent and therefore refused before the deferred boundary. That prior absence
is retained as an observation. It is now cleared: the root operator
materialized the exact public uncompressed bytes from existing `.gz` inputs,
read-only, with size/hash verification recorded in
`runtime-payload-materialization-v2.json`. This task reread the four paths and
observed the runtime-bindings sizes and SHA-256 values match. It performed no
decompression, network, storage, or execution operation.

## Raw helper-identity gate

Before an explicit future boundary may run, `binding()` rehashes the ten source
bindings, four payloads, kernel, and complete original Data inventory. The
producer then derives expected prover/checker initramfs bytes via the frozen
`qemu_controls.image()` pure byte-construction function: full Data and 300
seconds for the prover; no Data and 30 seconds for the checker; empty stdin for
both. It validates each retained `started.json` against the exact frozen helper
command vector, private cache kernel, private image path/digest, program/init/
input/stdin hashes, data mode, limits, and nonempty UTC field. It also validates
finite nonnegative elapsed status, helper `vm_valid`, exact raw framing,
certificate custody/root/grammar, every checker row, and raw result hashes.

Raw file custody hashes remain outside the semantic A/A documents, so different
allowed elapsed/UTC/private-path material retains different custody hashes while
the archived comparator normalizes its documented incidental fields only.

The deferred default boundary remains source only. When later explicitly called,
it uses unchanged `qemu_controls.vm`, a distinct private cache/images directory
per control, fixed101, full original prover arguments, and a second fresh
checker VM only when a prover certificate exists. No code path invoked it here.

## Retained review history and current test observation

The initial v1 five-test pass is retained. `aa-candidate-review-v1` found the
elapsed raw-digest, unchecked second checker-row, and duplicate-exit defects;
v2 corrected them. `aa-candidate-review-v2` then found that helper-format
command/data-mode/initramfs/stdin identities were not gated. The current
mock-only test receipt is in `test-report.txt`: actual `binding()` succeeds,
pure source reconstruction creates mock cache images, and command, mode, stdin,
initramfs, payload/init hash, limits, result status, labels, rejection, framing,
certificate, raw custody, cache, destination, and runtime input mutations are
refused at their intended stages.

The complete cohort experiment remains unapproved. This source/test work makes
no scientific readiness assertion or scientific conclusion.

## Schema repair

Outer `aa-v3-independent-checks.json` exercised 21 synthetic full-pipeline
mock scenarios with the expected outcomes; these are not the curve cohort and
no program executed. Its producer binding remains
`d481423ee4562c345d575f1dbd8f57a1dd5184e2c599c813a2f91154e790ef18`.
The separate `aa-schema-validation-v1.json` found eight Draft 2020-12 schema
errors because nested trace, status, and runtime objects declared strict
additional-property behavior without declaring their actual properties.

`aa_fixture_schema.json` now describes the complete `build_pair` result,
strict A/A result, both eight-key semantic documents, separate raw custody,
trace event rows, status fields, parsed certificate-step array, and fixed
runtime configuration. The optional `jsonschema` test dependency is required
for the recorded schema test and is supplied only by the task-local
`schema-check-venv`; no global dependency or configuration was changed. The
source producer was not altered during this schema repair.

## Sources read

The committed handoff; `runtime-bindings.json`; materialized payload hashes;
frozen `qemu_controls.py`, `certificate_admission.py`, `guest_framing.py`, and
`cohort_case.py`; retained public prime-101 helper artifacts; and archived
`cohort_checker.aa_compare` were inspected. The canonical storage HTTP 403
remains unresolved and was not retried.

## Nonrecursive SHA-256 values

| File | SHA-256 |
| --- | --- |
| `aa_fixture_producer.py` | `d481423ee4562c345d575f1dbd8f57a1dd5184e2c599c813a2f91154e790ef18` |
| `test_aa_fixture_producer.py` | `e0dc3abcd3519e54f3cc8d00ee34da4d595b6714c9827a26f648fcb33a21ccc9` |
| `aa_fixture_schema.json` | `c8f4f81ef3a092b3ea9360d568802b0b7e346245d02cae7e4f7a01e4af3d3087` |
| `test-report.txt` | `2af104d75aa50ae09562ff7c02e5ec924b0ce42f6dc1ea20e016d198cde2eecb` |

This report has no self-hash.
