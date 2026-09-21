# Implementation — Autolab binary-field BIN-EXP-007: WDSat

Historical Autolab port (no re-execution).

## Provenance
- Source repo: `/Volumes/Volume/autolab`
- Source commit: `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`
- Source id: `bin_exp007`
- Port tool: `tools/port_autolab_experiments.py`
- Port tag: `autolab-port-20260731`

## Copied artifacts
- `source/bin_exp007_result.md`
- `source/bin_exp007_wdsat.sage`
- `source/bin_exp007_wdsat.log`
- `source/bin_exp007b_extra.log`

## Deviations from live harness execution
- Run package is an archival import of prior Autolab outputs.
- `run.code.commit` records the crypto-autoresearcher HEAD at import time;
  Autolab source commit is recorded in `inputs.parameters.source_commit`.
- Certificates are `kind: none` (not re-verified).
