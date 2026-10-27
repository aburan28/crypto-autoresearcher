# Prospective F3 commands

No command in the execution block has been run in Phase A. Root must first
commit/push the exact source, pin and freeze `protocol.json`, provide the
matching per-task `release.json`, and complete the real S3 checkpoint push
and gate. `run.py` calls the shared serialized gate again before any panel
arithmetic/output. No bypass option exists.

From the repository root, with a fresh output path:

```sh
python3 -B research/p256_factor_base_parallel_20261026/tracks/f3/run.py --out research/p256_factor_base_parallel_20261026/tracks/f3/runs/run-01 --seed 2026102603 --protocol research/p256_factor_base_parallel_20261026/tracks/f3/protocol.json --release research/p256_factor_base_parallel_20261026/tracks/f3/release.json
```

Then analyse retained files and export into fresh destinations:

```sh
python3 -B research/p256_factor_base_parallel_20261026/tracks/f3/analysis.py --run research/p256_factor_base_parallel_20261026/tracks/f3/runs/run-01 --out research/p256_factor_base_parallel_20261026/tracks/f3/reports/run-01
python3 -B research/p256_factor_base_parallel_20261026/tracks/f3/export.py --run research/p256_factor_base_parallel_20261026/tracks/f3/runs/run-01 --analysis research/p256_factor_base_parallel_20261026/tracks/f3/reports/run-01 --out research/p256_factor_base_parallel_20261026/tracks/f3/exports/run-01.json
python3 -B tools/experiment_protocol.py check-export research/p256_factor_base_parallel_20261026/tracks/f3/exports/run-01.json --protocol research/p256_factor_base_parallel_20261026/tracks/f3/protocol.json --verify-files
python3 -B tools/experiment_protocol.py flow research/p256_factor_base_parallel_20261026/tracks/f3/exports/run-01.json
```

Root should set actual `AUTORESEARCH_RUNTIME`, `AUTORESEARCH_SESSION_ID`
and, only when known, `AUTORESEARCH_RESOLVED_MODEL`; otherwise the process
retains null producer fields rather than inventing a model/session identity.
The actual interpreter binary hash is observed separately from source-file
hashes. Root pins all five files listed in `extensions.source_files_to_pin`.
The shared checkpoint-gate helper and curve identity implementation remain
root-owned dependencies and must be source-bound in the release.

Software preparation checks permitted before release are AST parsing,
`run.py --help`, `analysis.py --help`, `export.py --help`, and
`tools/experiment_protocol.py validate .../protocol.draft.json`. None imports
the arithmetic oracle or produces observation rows. Their actual receipts
are in `preparation-checks.json` and `preparation/`.
