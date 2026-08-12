# Implementation — Autolab ECDSA Fail: Older q=1141 higher-Toffoli score

Historical Autolab port (no re-execution).

## Provenance
- Source repo: `/Volumes/Volume/autolab`
- Source commit: `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`
- Source id: `ecdsafail-q1141-old-jul24`
- Port tool: `tools/port_autolab_experiments.py`
- Port tag: `autolab-port-20260731`

## Copied artifacts
- `source/score.json`
- `source/README.md`
- `source/results.tsv`

## Deviations from live harness execution
- Run package is an archival import of prior Autolab outputs.
- `run.code.commit` records the crypto-autoresearcher HEAD at import time;
  Autolab source commit is recorded in `inputs.parameters.source_commit`.
- Certificates are `kind: none` (not re-verified).
