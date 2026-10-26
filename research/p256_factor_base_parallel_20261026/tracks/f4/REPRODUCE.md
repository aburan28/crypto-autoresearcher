# F4 second-pass execution interface

The current files are Phase A preparation. Do not run the panel before root
releases Phase B against exact committed source, a frozen `protocol.json`,
and a real successful canonical S3 checkpoint. `run.py` enforces the shared
root release/checkpoint helper; a draft or local checkpoint preview is refused.

The intended released command, from the repository root, is:

```sh
/workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261026/tracks/f4/run.py --out research/p256_factor_base_parallel_20261026/tracks/f4/runs/run-01 --seed 2026102604 --protocol research/p256_factor_base_parallel_20261026/tracks/f4/protocol.json --release research/p256_factor_base_parallel_20261026/tracks/f4/phase-b-release.json
```

Choose a fresh attempt directory; no file in an earlier attempt is replaced.
The interpreter needs the first-pass pinned SymPy/python-flint dependencies.
Root must pin the SHA-256 of the actual executable used by this command, the
implementation commit containing all five new scripts and the runtime helper,
and the analysis hash before freezing. The program checks those observations
against Git objects before the gate. Source changes after freeze need an
additive prospective version, not a same-attempt repair or retry until green.

The source contains no top-level panel. `--help` is harmless, but Phase A
verification uses AST parsing and protocol schema checking only. The released
panel writes all raw cases, four whole-arm rows, exact graph certificates,
host/source/gate receipts, deterministic analysis and the unified export.

After a completed attempt, run the canonical export checker using the system
Python environment containing jsonschema:

```sh
python3 tools/experiment_protocol.py check-export research/p256_factor_base_parallel_20261026/tracks/f4/runs/run-01/export.json --protocol research/p256_factor_base_parallel_20261026/tracks/f4/protocol.json --verify-files
python3 tools/experiment_protocol.py flow research/p256_factor_base_parallel_20261026/tracks/f4/runs/run-01/export.json
```

If a process is stopped before four rows/export exist, preserve the partial
directory and root launcher logs. That is a `not_completed` observation,
not four invented empty mathematical results. The application writes fresh
per-case records; there is no in-place row continuation. Any restored attempt
uses new output identity, retained prior counts and invalid cross-restore clocks.

The analysis report and SVG are generated only from retained JSON/rows.
Root renders and inspects its fresh compact PDF after raw records are sealed.
The preparation report, old first-pass outputs and historical nonsplit control
remain distinct custody layers.
