# RUN-SEMBIN-595308 — status: RUNNING (interim snapshot)

This package is being written by two worker processes (workerA: reproduction +
off-diagonal cells; workerB: separation cells). Files under `worker*/cells/`
are append-only (`results.jsonl`, `progress.log`) or write-once per instance.
The run is NOT complete: no `manifest.yaml` or `task-report.md` exists yet, and
nothing here is an official run record until the completing snapshot commit
adds them and this file is superseded by the manifest's `status`.
Interim commits exist only so an ephemeral container cannot lose measured cells.
relaunch 2026-09-17T07:46:15Z: msolve -u 1 (hash-table regeneration each step), mem cap 7 GB, resume skips instances whose F4 trace completed; earlier records stay in results.jsonl
relaunch 2026-09-17T07:54:35Z: msolve F4 trace on N >= 41 cells (13:4:4:4, 17:3:3:8, 21:3:3:7) deferred to a serialized heavy pass with a larger cap (msolve exponent-vector table exceeded 7 GB at N = 42 after 15 rounds, all of step degree <= 4); closure and single-level still run on them

## Attempt 2 (fresh worker directories) — started after adopting commit 49043c6ba

Attempt 1 (worker directories moved verbatim to `partial/attempt1/`) ran the
instrument at commits before 49043c6ba. That commit (Cursor Agent, reviewed and
merged here) fixes three things, one of them semantic: the single-level Macaulay
statistic (GOAL-DREG-001 style) multiplied the reduced iteration-0 basis instead
of the ORIGINAL generators, so a reduced row whose degree dropped under
cancellation received more multipliers than any generator and the row space
could exceed the degree-D Macaulay matrix. The other two are the
instrument-identity comparison (F4 rounds compared without msolve's printed
timings) and per-child peak RSS via wait4. Attempt 1's F4 traces and closure
verdicts are unaffected by the semantic fix and are kept as raw outputs; the
official measurements are attempt 2's, in `workerA/` and `workerB/`.
