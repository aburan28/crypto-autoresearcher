# Zero-run A/A fixture producer implementation

This is the five-artifact implementation package for `TASK-20261025-ad9d68`.
It is engineering support for a future approved non-cohort control only. It is
not a scientific run, readiness determination, result, or conclusion.

## Implementation

`aa_fixture_producer.py` exposes only `build_pair(left_output, right_output,
binding_manifest, legacy_boundary=None)`. It accepts the fixed public fixture
`public-prime101-default` with decimal bytes `101\n` only. Before an injected
future boundary can run, it verifies the ten frozen input source hashes, exact
configuration and limits, binding-manifest bytes, hydrated runtime payloads,
kernel, and every original Data inventory byte. Runtime payload reading first
uses the public artifact-store candidate-form interface to accept exactly one
local, regular raw or `.gz` form. It refuses absent, ambiguous, symlink, and
all `.blob.json` pointer forms before it can call `read_bytes`; therefore this
task cannot trigger `fetch`, a network read, storage upload, or retry. It
creates distinct private `runtime-cache/images` paths below two fresh output
directories.

The module has no execution CLI and has no default legacy boundary: omission of
the injected future boundary refuses. It never calls `cohort_runner.run_trial`
or `cohort_case.execute_case`.

Each document is derived from retained raw prover/checker `started.json`,
`result.json`, `serial.raw`, `qemu.stderr`, and `program.stdout` files, rather
than constructed as a ready-made A/A JSON fixture. Admission requires valid
framing, zero child exits, exactly one prime label, one complete root-101
certificate with its parsed step count, a second fresh checker framing and
acceptance, fixed identity bindings, and raw-byte hashes. The prover raw tree
must contain exactly the five `qemu_controls.vm` files plus
`certificate.cformat`; the checker tree must contain exactly its five files and
no certificate. The producer normalizes CRLF exactly as the archived
`cohort_checker.serial_parts` interface does, requires the normalized retained
`program.stdout`, and requires the prover `certificate.cformat` bytes to equal
the normalized serial-envelope certificate. It recomputes `valid_frame` from
each raw serial and requires the source-written boolean `result.vm_valid` to
match before either control can reach A/A equality. Only then does the
module load and call the archived real `cohort_checker.aa_compare` function.

Before equality, the producer writes and checks the exact `101\n` bytes at
`input/public-input.dec`, derives the certificate from the raw serial envelope,
and writes/checks it at `certificate/certificate.cformat`. It writes a checked
`custody/raw-artifact-sha256.json` for all retained prover/checker raw files.
For both the prover and the second fresh checker, it validates the public
`qemu_controls.vm` started-record interface: program/init/input/stdin hashes,
data mode, guest/host limits, initrd digest, and full fixed QEMU command with
the control's private kernel and image paths. It verifies that the private
kernel and `{initramfs_sha256}.cpio.gz` image are local regular non-symlink
files and match their recorded digests.

The A/A document retains location-independent semantic started identities.
The complete raw `started.json` records and their hashes remain in each control
directory and are validated before comparison; their private output paths are
not copied into the compared document because two intentionally fresh controls
must use different private paths and the archived `aa_compare` normalizes only
its documented incidental fields.

Any timeout, crash, missing/empty/malformed certificate, invalid framing,
checker rejection, status inconsistency, raw-artifact loss, semantic mismatch,
or reused destination raises `CONTROL_INVALID/INDETERMINATE`; the existing
control directory is retained and A/A equality is not established.

## Frozen-source and interface review

The task’s ten bound repository inputs were reviewed before implementation and
their SHA-256 values matched the handoff: the runner/checker supplied the
preserved-artifact and real `aa_compare` contract; `certificate_admission.py`
and `guest_framing.py` supplied the validity gates; `cohort_case.py` and
`qemu_controls.py` defined the future boundary that this task must not execute;
`runtime-bindings.json` and the protocol supplied fixed runtime/configuration
identities; `artifact_store.py` supplied the existing local read interface; and
the public push record supplied the unresolved access condition.

No external literature claim is made by this implementation-only task. The
repository protocol is the task-specific source review; its stated evidence gap
remains a future approved execution under the frozen conditions.

## Mock-only verification

See [test-report.txt](test-report.txt). The test injects an in-process writer
of synthetic retained raw artifacts and calls the real archived `aa_compare`.
Eight mocked tests passed in 0.051s, including a source-faithful CRLF VM serial
case, absent/mismatched raw prover certificate-file refusals, and a refusal for
a stored `vm_valid` inconsistent with raw framing. The suite also includes a pointer form whose fake
artifact-store helper recorded zero `read_bytes` calls, and table-driven
started-record/private-cache identity mutations for both controls. It records
`named_orders_executed: 0` and `legacy_program_executed: false`.
No original/legacy program, boundary, VM, QEMU, Docker, subprocess, cohort
order, storage upload, artifact-store fetch, or retry was executed.

## Unresolved access condition and limits

The public canonical-store `HeadObject` 403 from
`BATCH-08d006/artifact-store-push-v1.json` remains unresolved. This task made
no account, credential, alternate-store, pointer, upload, or retry attempt.
Existing hydrated bytes are only future input bindings. Static mocked tests do
not prove that the unexecuted real branch, runtime bytes, or any scientific
comparison is ready or produces a result.

The frozen public interface fixes the QEMU command path (`/opt/homebrew/bin/
qemu-system-i386`) but does not publish a digest for that host executable.
This implementation binds that exact path and every command argument, kernel,
initrd, payload, input, and Data identity available from the public interface;
it does not claim an unprovided QEMU executable-content hash. A future real
path missing any required public identity, private cache artifact, or retained
raw artifact refuses before A/A equality.
