# INCOMPLETE RUNS -- NOT VALID RECORDS, DO NOT CITE AS EVIDENCE

RUN-PMA4-001-{a,b,c,d} and the sibling
`experiments/EXP-PMA-001/implementation/` modules are the partial output of
an Executor task (dispatched for EXP-PMA-001, authorized_by
DEC-20260906-9f036a per this session's records) that was interrupted
mid-run by an account-wide HTTP 429 rate-limit ("session limit", reported
reset 5:30pm UTC 2026-09-07) on 2026-09-07 ~03:38 UTC. Per AGENTS.md rule
3, an infrastructure failure is never negative (or positive) mathematical
evidence, and per AGENTS.md rule 5, missing data stays missing and is
reported as such -- this file is that report.

**State at interruption:**
- `RUN-PMA4-001-a`, `-b`, `-c`: each has `raw-result.json`, `summary.json`,
  `stdout.log`, `stderr.log`, and its own driver script (`run_a.py` /
  `run_b.py` / `run_c.py`) -- but NO `manifest.yaml` in any of the four run
  directories, so none can be read as a bound, dispatch-authorized,
  terminal run record regardless of what its own raw-result/summary claims.
- `RUN-PMA4-001-d`: only `run_d.py` exists. No `raw-result.json`,
  `summary.json`, or logs -- this run had not finished executing (possibly
  had not started producing output) when the interruption occurred.
- No `analysis.md` or experiment-level `execution-report.yaml` exists
  anywhere under `experiments/EXP-PMA-001/`, so no aggregated
  classification or claim has been made.

**What IS present** under `implementation/` (not independently verified,
not to be relied upon until re-verified): `common.py`, `driver_core.py`,
`existence_decider.py`, `grid_data.py`, `parity_predicate.py`,
`witness_verifier.py`. (`__pycache__/` is gitignored and not committed.)

**Disposition:** a fresh Executor dispatch for EXP-PMA-001 (after the rate
limit clears) will either complete RUN-PMA4-001-d and add the missing
manifests to a/b/c, or discard and redo some or all of these runs, at that
Executor's discretion -- this directory does not bind that decision. This
marker is committed only so the working tree is honestly reflected in git
history; it is not a Coordinator snapshot archive and confers no
evidentiary status on anything under `experiments/EXP-PMA-001/runs/` or
`experiments/EXP-PMA-001/implementation/`. Do not treat any file here as a
completed run until manifests exist for all opened runs, an
execution-report.yaml exists, and this INCOMPLETE.md has been removed by
whichever task finishes or supersedes this work.
