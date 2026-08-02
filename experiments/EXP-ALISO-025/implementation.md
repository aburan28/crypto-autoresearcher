# Implementation — Autolab isogeny: p1243_parity_repaired_kani_probe

Historical Autolab port (no re-execution).

## Provenance
- Source repo: `/Volumes/Volume/autolab`
- Source commit: `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`
- Source id: `p1243_parity_repaired_kani_probe`
- Port tool: `tools/port_autolab_experiments.py`
- Port tag: `autolab-port-20260731`

## Copied artifacts
- `source/p1243_parity_repaired_kani_probe_result.json`
- `source/p1243_parity_repaired_kani_probe.py`

## Deviations from live harness execution
- Run package is an archival import of prior Autolab outputs.
- `run.code.commit` records the crypto-autoresearcher HEAD at import time;
  Autolab source commit is recorded in `inputs.parameters.source_commit`.
- Certificates are `kind: none` (not re-verified).
