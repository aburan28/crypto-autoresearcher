# Executable B1 contract

Administrative preparation only: two exact retained p4099 fixtures, sixteen
atoms and sixty-four original seed0 sources per curve, unchanged cubic law.
Historical nonzero and completed zero arms each enumerate2,293,760 descriptors
per fixture: four cells,9,175,040 collection attempts. Complete independent
arithmetic replay charges another9,175,040 attempts, separately. No native B1
or P256 scientific case was run while preparing this package.

Use the original standalone Phase B route. Root owns git, checkpoint transport
and explicit release; no additional user authorization or official scientific
status change is involved. Run these from the repository root with
`PYTHONPATH=src:.` and `/workspace/factor-base-venv/bin/python`.

1. Commit/push the final native instrumentation and this package's exact four
   administrative modules. `SOURCE_COMMIT` below is that real source commit.
2. Generate the prospective final protocol after that source commit:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b1_execution_20261029/prepare.py protocol --source-commit SOURCE_COMMIT --out research/prime_field_b1_execution_20261029/protocol.json --freeze
   ```

3. Commit/push frozen protocol; update the resume note with fixed workload,
   command, source/protocol hashes and guards. Perform actual
   `bash scripts/checkpoint.sh push` and `bash scripts/checkpoint.sh gate`.
4. Make the explicit source-bound root release:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b1_execution_20261029/prepare.py release --source-commit SOURCE_COMMIT --protocol research/prime_field_b1_execution_20261029/protocol.json --out research/prime_field_b1_execution_20261029/release.json --owner root-prime-field-b1 --authorize-root
   ```

5. Commit/push release; invoke the public run workflow on this native command:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b1_execution_20261029/supervise.py --protocol research/prime_field_b1_execution_20261029/protocol.json --release research/prime_field_b1_execution_20261029/release.json --owner root-prime-field-b1 --out FRESH_RUN_DIRECTORY
   ```

   The supervisor takes an exclusive B1 lease, records ownership/PIDs/host and
   source facts, and applies2GiB memory and21,600s wall/CPU machine watchdogs.
   The native program performs its own committed-source/interpreter/protocol/
   release checks and real canonical S3 gate, retaining `raw/admission.json`.
   No gate is bypassed. These guards protect the host; they are not a research
   spending cap or measured runtime prediction. There is no in-row resume.
6. Preserve every stopped/failed/complete prefix. Before export root may gzip
   large raw files losslessly, retaining exactly one encoding per logical file.
   The analysis reads `.json.gz` and `.jsonl.gz`, hashes final stored compressed
   bytes, and does not rewrite native records:

   ```sh
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b1_execution_20261029/analyze.py --run FRESH_RUN_DIRECTORY --protocol research/prime_field_b1_execution_20261029/protocol.json
   PYTHONPATH=src:. /workspace/factor-base-venv/bin/python tools/experiment_protocol.py check-export FRESH_RUN_DIRECTORY/export.json --protocol research/prime_field_b1_execution_20261029/protocol.json --verify-files
   ```

Keep all exported bytes hydrated at their original paths when placing large
files in artifact storage. Add a manifest with logical and stored hashes/size,
encoding and S3 receipt in a new archival record; do not alter the immutable
raw files or export. Export every stdout/stderr, exception, ownership, source,
phase/status/result/verification and admission record. Later archival manifests
are separate records. A descriptive report, diagram and inspected PDF remain
part of root's run reporting.

Each fixture/arm has one export row (four total), one physical process overall.
Whole-process CPU/RSS/wall resources appear only in `backend_record`;
collection and replay phase clocks are diagnostics, never additive independent
executions. All clocks have `wall_valid=false`. Field/group counters cover
collection only, excluding replay, integer bookkeeping, affine/kernel work,
serialization/storage and complete S. The separate arithmetic checker checks
rows, statuses/digests, projection, rank and kernel; it does not independently
check counters or serve as independent scientific review.

Collected results survive replay failure. Missing cells and missing journal
coverage remain unknown; actual stopped-prefix attempts retain journal lower
bounds. Complete collected cells remain unverified until the separate
verification file records the exact full replay. Equation differences use
normalized retained augmented rows; old-kernel syndromes are rechecked by row/
kernel products against the separately checked old kernel. Source/constraint
zero flags are checked against witness geometry and source-complete journals
against checked status blocks when journal coverage is complete.

The preview protocol is a validated draft, never authority. Final freeze and
release await root's actual committed source and canonical checkpoint.
`model-readiness.txt` retains actual resolver/probe observations: configured
coordinator identity remains unverified and its backend key is unset. No model
verification, official ledger transition, priority or speedup is claimed.
