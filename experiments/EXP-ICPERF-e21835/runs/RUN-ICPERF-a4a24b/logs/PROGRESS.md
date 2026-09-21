# RUN-ICPERF-a4a24b — executor progress log (append-only)

TASK-20260915-4f4027, EXP-ICPERF-e21835, executor (`executor-implementation`).
Written incrementally so an interrupted session is recoverable. Times are UTC.

## S0 — orientation (2026-09-15T22:26Z .. 22:35Z)

- Read the frozen contract `experiments/EXP-ICPERF-e21835/specification.yaml`
  in full: `status: approved`, `approved_by: coordinator`,
  `approval_basis: DEC-20260915-428a17`. Authority confirmed.
- Read the task card TASK-20260915-4f4027 in
  `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-a33cda/dispatch_queue.json`
  (write_scope = code/ + runs/RUN-ICPERF-a4a24b/ only; maximum_runs 1).
- Did NOT read `coordination/review/icperf-20260915-a33cda/` (reviewers' material,
  contains the Coordinator's expected values). Confirmed by not listing it.
- Read: EV-ICPERF-390707 inputs via the two validator reports' artifacts
  (`v3_reduce.py`, `v3_reduce.json`, `m2_reportfix.diff`), the frozen four files,
  and `RUN-ICPERF-c9590f/ABORTED.md` + `bench_stderr.log`.
- Host at S0: `uptime` load average 0.00 0.03 0.06; 4 CPUs; 15 GiB total,
  ~6 GiB available. `git rev-parse HEAD` = 1fc65075ccb87ccba82c342a2f2af15e926acee9
  (branch cursor/semaev-2015-audit-program-5b8b; f4f2dfa80 snapshot is an ancestor).
- C-BYTE part 1 (frozen tree hashes vs TASK-20260913-f8bdec snapshot-receipt.json):
  MATCH on all four files
  (bench e8aad273…, binec b6edbcf6…, convert 16affe2c…, summary eaf54bd7…).
- `git status --porcelain experiments/EXP-ICPERF-66fd51` → empty (C-NOWRITE, start).

## S1 — repaired tree created (2026-09-15T22:35Z)

- Copied the four frozen files byte-identically to
  `experiments/EXP-ICPERF-e21835/code/`; sha256 verified equal before any edit.
- Created `runs/RUN-ICPERF-a4a24b/{logs,watchdog_control,accept}/`.
- `accept/` holds the acceptance driver scripts (they are not part of the
  instrument tree, so they live under the run directory, not under code/,
  which C-BYTE audits file-by-file against the frozen tree).

## S2 — discrepancies noted while reading (recorded, not resolved by me)

- D-1 (prompt vs contract): the dispatch prompt says the contract is committed
  at f4f2dfa80; HEAD at S0 is 1fc65075c because two later commits (queue update,
  bus publish) landed on the branch. f4f2dfa80 is an ancestor, so the frozen
  contract bytes are the ones read. No conflict with the contract.
- D-2 (contract A6 reference count): the contract's C-SUMREG/A6 reference is
  "156 per-cell numeric values" agreeing with `v3_reduce.json`. That count is not
  reconstructible from `v3_reduce.json`: the counts available there are 236
  (all numeric values in its own `cells` block), 180 (keys shared with the frozen
  `summary.json` cells block), and 158 (shared keys whose frozen value is a
  non-null number). `grep -rn 156` over the review directory and
  EV-ICPERF-390707 finds no provenance for 156. Handled by reporting every
  reconstructible count with its explicit definition beside the reference, and
  never by adjusting the frozen reference.

## S3 — repairs written (2026-09-15T22:36Z .. 22:40Z)

- convert.py: D1 (`gens_` -> `gensG` at all three occurrences; RESULT byte format
  unchanged).
- bench.py: D2 (RLIMIT_AS removed; `pgid_rss_kb` / `kill_group` added; `Runner.run`
  rewritten on Popen + start_new_session + 0.25 s RSS polling at 8 GiB, recording
  peak_rss_kb / rss_limit_gb / rss_limit_breached / rss_poll_interval_s / rss_polls;
  `budget_stop_rss_limit` status at the four status sites), D4 (`probe_version`,
  temp files instead of pipes, DEVNULL stdin, process-group kill, 10 s per engine,
  per-engine probe seconds recorded), D5 (per-engine `SOLVER_STAT_PATTERNS`,
  `parse_solver_stats`, `stats_unavailable_reason`, cadical loses `-q`, minisat gets
  `-verb=1`).
- summary.py: D3 (`evaluated`/`unevaluated`/`compose` helpers; `L` bound inside the
  P3 loop; unevaluated clauses made visible in P2, P3, P4, P5, P6 with reasons; a
  nonempty `unevaluable` list forces top-level `holds: null`). No median, ratio,
  threshold, inclusion rule or `finished` definition touched.
- binec.py: untouched, byte-identical.
- Driver scripts (not part of the instrument) under runs/RUN-ICPERF-a4a24b/accept/,
  null objects under watchdog_control/.

## S4 — probe invocation (D4 / A5 / C-PROBE) 2026-09-15T22:40:41Z .. 22:41:41Z

- C-LOAD at launch: loadavg1 0.00; MemAvailable 7,023,220 kB.
- Both children launched with stdin = the read end of an open pipe never written to
  and never closed (the RUN-ICPERF-c9590f configuration).
- REPAIRED `environment()`: returned in **0.083 s**, exit 0. Singular =
  "Singular for x86_64-Linux version 4.3.2 (4330, 64 bit) Apr  1 2024 04:44:00".
  No engine `unavailable:`. Per-engine probe seconds: gcc 0.004, M2 0.064,
  Singular 0.008, cryptominisat5 0.004, cadical 0.002. environment.json written.
- FROZEN `ver` body, verbatim, same launch: **did hang**, and its 60 s timeout DID
  fire here — returned at 60.062 s with
  `unavailable: Command '['Singular', '--version']' timed out after 60 seconds`.
  So the inherited-stdin hang reproduces, but why the same 60 s timeout did not
  return in RUN-ICPERF-c9590f is NOT explained by this measurement. Recorded as
  unexplained (contract A5 permits either).
- Artifacts: logs/probe_check.json, logs/probe_repaired.{out,err},
  logs/probe_frozen_control.{out,err}, environment.json.

## S5 — HOST CONDITION affecting C-WATCHDOG-NULL and A3 (recorded before running)

- MemAvailable is ~7.0 GB of a 16.0 GB MemTotal, with SwapTotal 0. The contract
  budgets "10 GB for the whole task ... on a 15 GB host" and C-WATCHDOG-NULL
  direction (i) asks for a process that makes **12 GiB** resident under the declared
  8 GiB watchdog. Neither 12 GiB nor 8 GiB of resident memory can be reached with
  ~7.0 GB available and no swap: the kernel OOM killer would fire before the
  watchdog could, which would measure the OOM killer and not the watchdog, and
  risks killing unrelated host processes (machine protection).
- Deviation taken, recorded here and in the manifest: direction (i) is exercised at
  a SCALED limit (watchdog 2 GiB, allocator target 4 GiB, 128 MiB steps) — same
  mechanism, same polling interval, same kill path, reachable memory. Direction (ii)
  is exercised at the DECLARED 8 GiB limit, since it touches only 256 MiB.
- RLIMIT_AS is set nowhere, including in the null objects, so the claim that
  RLIMIT_AS would kill direction (ii) is cited from EV-ICPERF-390707 and is not
  re-measured here.
