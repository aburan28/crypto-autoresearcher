# Implementation — Autolab prime-field: round020_solvegate

Historical Autolab port (no re-execution).

## Provenance
- Source repo: `/Volumes/Volume/autolab`
- Source commit: `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`
- Source id: `round020_solvegate`
- Port tool: `tools/port_autolab_experiments.py`
- Port tag: `autolab-port-20260731`

## Copied artifacts
- `source/round020_solvegate_result.json`
- `source/round020_results.md`
- `source/round020_solvegate_contract.md`
- `source/round020_solvegate_ic_vs_rho.sage`
- `source/round020_solvegate_ic_vs_rho.sage.py`
- `source/round020_solvegate.log`

## Deviations from live harness execution
- Run package is an archival import of prior Autolab outputs.
- `run.code.commit` records the crypto-autoresearcher HEAD at import time;
  Autolab source commit is recorded in `inputs.parameters.source_commit`.
- Certificates are `kind: none` (not re-verified).
