# EXP-MLKEM-004 implementation notes

Executor task: `TASK-20260724-919`. Observations only.

## Repairs relative to EXP-MLKEM-003

- Added harness-side `CTRL-SYNTHETIC-BASELINE-INVISIBLE` (`synthetic_control.py`).
- Redefined outcome precedence so `generator_hardening_insufficient` fires only when the synthetic control is missed by G2/G3; wolfSSL defect rediscovery is not marginal information.
- Second implementation selection constrained to fixed-bound hand-written vector tails; BoringSSL rejected; PQClean preferred when buildable; liboqs-style verify is not load-bearing.
- Exact argv in every `command.txt`; build wall-clock in `/tmp/exp-mlkem-004/pre-run/build_timing_receipt.json`.
- Anchor grade cites the file actually validated against.

## Scope

No key recovery, oracle construction, exploitation path, disclosure, or deployed-system interaction occurred. Library comparison logic was not modified.
