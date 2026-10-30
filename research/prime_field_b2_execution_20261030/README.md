# B2 matched subset/cover execution contract

Five fixed membership-selected ties, two arms each: baseline h0 and the selected
nonzero shift on the same active atom subset. Both arms use the completed-zero
policy and restrict constraints and residual endpoints to that same subset.
Original16native atoms,15projected unknown columns, public anchors,64seed0
sources and full historical preprocessing rows remain unchanged. No candidate
is selected by relation yield.

The size15pair has1,863,680 branches per arm; four size14pairs have1,490,944
per arm. Total:15,654,912 collection attempts and the same number of separately
charged independent replay attempts. No sampling, source replacement or early
rank stop. This package's preparation ran administrative software fixtures
only, with no scientific B2/B1/P256 trial.

Root owns git, checkpoint transport and explicit release. Use the public run
skill for execution. From the repository root, first commit/push final native
core/check/driver, inputs and these administrative modules. SOURCE_COMMIT below
must be that actual source commit, not a future placeholder.

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b2_execution_20261030/prepare.py protocol --source-commit SOURCE_COMMIT --out research/prime_field_b2_execution_20261030/protocol.json --freeze
```

Commit/push frozen protocol, update resume with command/source/protocol hashes
and guards, then perform real `bash scripts/checkpoint.sh push` and `gate`.
Explicitly release those exact bytes under standing user authorization:

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b2_execution_20261030/prepare.py release --source-commit SOURCE_COMMIT --protocol research/prime_field_b2_execution_20261030/protocol.json --out research/prime_field_b2_execution_20261030/release.json --owner root-prime-field-b2 --authorize-root
```

Commit/push release. Launch one supervised native process:

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b2_execution_20261030/supervise.py --protocol research/prime_field_b2_execution_20261030/protocol.json --release research/prime_field_b2_execution_20261030/release.json --owner root-prime-field-b2 --out FRESH_RUN_DIRECTORY
```

The supervisor owns an exclusive lease and records source/host/ownership/PIDs.
2GiB memory and21,600s wall/CPU watchdogs protect the host; these are not
measured runtime predictions or research spending caps. Native admission binds
committed source/input/interpreter/frozen protocol/release and calls the actual
canonical S3 gate. No override or mock is supplied; there is no in-row resume.

Preserve every stopped/failed prefix. Root may losslessly gzip raw files before
export, with exactly one encoding retained per logical path. Export final bytes:

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_b2_execution_20261030/analyze.py --run FRESH_RUN_DIRECTORY --protocol research/prime_field_b2_execution_20261030/protocol.json
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python tools/experiment_protocol.py check-export FRESH_RUN_DIRECTORY/export.json --protocol research/prime_field_b2_execution_20261030/protocol.json --verify-files
```

Ten disjoint arm/candidate rows share one physical process. Whole-process
resources appear once in backend_record; collection/replay phase clocks are
components, not extra costs. All clocks have wall_valid=false. Native counters
cover partial collection work only; replay, affine/kernel/elimination,
preprocessing, integer bookkeeping and storage costs are incomplete. No
Delta-per-cost, complete S, wall-time advantage or attack-cost claim follows.

Unknown cells retain null counts and stopped journals provide attempt lower
bounds. Complete collected rows survive failed replay and remain unverified
until the separate checker file passes. Analysis independently projects new
rows, normalizes their affine equations, and multiplies them by the old kernel.
It checks accepted source/constraint-zero flags against cover geometry, source
completion records against checked status blocks, and rank-progress/syndrome
journals against retained accepted rows when journal coverage is complete.
Combined rank minus preprocessing rank measures additional information on
unchanged columns; a larger row pool is not itself a gain.

The independent arithmetic checker validates complete row/status/rank/kernel
and auxiliary constraints. It does not audit field counters or constitute
independent scientific review. Final source/input provenance is embedded in
inputs.json, with source artifact hashes; all exact source dependencies are
locked by release. Model readiness remains honestly unverified. No official
scientific record or state transition is created here.

Every raw/status/verification/admission/phase/exception/log file is hashed in
export. Keep hydrated bytes at original paths if storing large artifacts;
subsequent storage manifests/receipts are separate immutable records. Root's
run reporting still needs its descriptive report, diagram and inspected PDF.
