# Executable C1 contract

Administrative preparation for the unchanged seven fixed F1 cases, seed
2026102601, dimension guard 560 and stage profiling. No scientific data has
been taken by this package's preparation. The original Phase B route is
preserved: commit/push exact source and analysis; freeze/commit prospective
protocol; complete the resume note and perform a real S3 push/gate; explicitly
release root execution; then run the unchanged driver's own admission.

The coordinator subagent provides no official research-state transition or
claimed model verification. The actual adapter probe is retained in
`model-readiness.txt`; the original native gate checks an explicit root release,
not a newly invented inference-backend gate.

## Root sequence

Use `/workspace/factor-base-venv/bin/python` with `PYTHONPATH=src:.` from the
repository root. `SOURCE_COMMIT` below means the actual commit root creates
containing this directory's four Python files and all existing locked source;
it is not a fabricated future commit. Root handles all git/checkpoint actions.

1. Commit and push the exact preparation sources, including `common.py`,
   `prepare.py`, `supervise.py` and `analyze.py`. The accompanying
   `protocol.draft.json` is a validated preparation preview, not authority.
2. Generate and freeze the final prospective protocol against that source:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python \
     research/prime_field_c1_execution_20261029/prepare.py protocol \
     --source-commit SOURCE_COMMIT \
     --out research/prime_field_c1_execution_20261029/protocol.json --freeze
   ```

3. Commit/push `protocol.json`. Update `.resume/RESUME.md` with this exact panel,
   paths, command, source/protocol hash and machine guards. Run the real
   `scripts/checkpoint.sh push` followed by `gate` with supported credentials.
4. Explicitly release these exact bytes, preserving the actual checkpoint:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python \
     research/prime_field_c1_execution_20261029/prepare.py release \
     --source-commit SOURCE_COMMIT \
     --protocol research/prime_field_c1_execution_20261029/protocol.json \
     --out research/prime_field_c1_execution_20261029/release.json \
     --owner root-prime-field-c1 --authorize-root
   ```

5. Commit/push `release.json`. Start the native supervised computation:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python \
     research/prime_field_c1_execution_20261029/supervise.py \
     --protocol research/prime_field_c1_execution_20261029/protocol.json \
     --release research/prime_field_c1_execution_20261029/release.json \
     --owner root-prime-field-c1 --out FRESH_RUN_DIRECTORY
   ```

   It owns an exclusive advisory lease, records PID/host/source facts, sets
   one-process/thread environment and 2GiB/3600s memory/CPU/wall guards, and
   invokes the unchanged driver. The driver verifies the committed release,
   full source/input/interpreter hashes and frozen protocol, then calls the
   real canonical checkpoint gate. Admission is not skipped or mocked.
6. Preserve/checkpoint every outcome, including stopped or failed runs. Export
   and descriptively analyze the retained native files only:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python \
     research/prime_field_c1_execution_20261029/analyze.py \
     --run FRESH_RUN_DIRECTORY \
     --protocol research/prime_field_c1_execution_20261029/protocol.json
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python \
     tools/experiment_protocol.py check-export FRESH_RUN_DIRECTORY/export.json \
     --protocol research/prime_field_c1_execution_20261029/protocol.json --verify-files
   ```

The exporter retains two method cells over one physical panel, following the
existing protocol schema. It records physical execution count 1 explicitly.
Only the extractor cell carries the shared process's diagnostic resource
interval and native counters; the reference cell has no independent method
clock/cost. Shared object counts must not be summed. All clocks have
`wall_valid=false`, and no performance or whole-attack cost claim is admitted.

Unknown, missing and stopped cases remain unknown. Completed triple cases
require the retained finite-reference check. Every native case, stage journal,
stdout/stderr, ownership, host manifest and exception survives for reporting.
The run still needs a fresh descriptive report, diagram and inspected PDF;
independent claim review is separate. No historical F1 file or result is changed.

## Current administrative state

The draft protocol passes the repository validator. Final frozen protocol and
release must be generated **after root commits the preparation source**; they
cannot honestly bind this uncommitted code in advance. The source closure also
locks the real checkpoint script/helper, admission helper, protocol tool/schema,
export schema, interpreter digest and package versions. Root can perform the
sequence above without requesting further user authorization.
