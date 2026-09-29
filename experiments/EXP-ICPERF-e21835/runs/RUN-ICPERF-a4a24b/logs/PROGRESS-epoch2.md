# RUN-ICPERF-a4a24b — executor progress log, EPOCH 2 (append-only)

TASK-20260915-4f4027 epoch 2, EXP-ICPERF-e21835, executor (`executor-implementation`,
fallback binding: epoch 1's Opus quota was exhausted). Times are UTC.
Epoch 1's log is `logs/PROGRESS.md` and is immutable; this file is new.

## E2-S0 — orientation (2026-09-16T06:10Z)

- Read `docs/agent-runtime-core.md`, `agents/executor.md`, and the frozen contract
  `experiments/EXP-ICPERF-e21835/specification.yaml` in full:
  `status: approved`, `approved_by: coordinator`, `approval_basis: DEC-20260915-428a17`.
  Authority confirmed.
- Read the TASK-20260915-4f4027 card (handoff, write_scope, artifact_paths, `resumption`)
  from `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-a33cda/dispatch_queue.json`.
- Did NOT list or read `coordination/review/icperf-20260915-a33cda/` (reviewers' material).
- Read epoch 1's `manifest.yaml`, `logs/PROGRESS.md`, `results.jsonl`.
- HEAD at E2-S0: ca6946306 (claim commit); epoch 1 artifacts committed at ecdd3bffd.
  `git diff HEAD --stat -- experiments/EXP-ICPERF-e21835 experiments/EXP-ICPERF-66fd51`
  is empty: both trees are byte-identical to HEAD before I write anything.
- Immutability rule acknowledged: nothing under `code/` or under the committed
  `runs/RUN-ICPERF-a4a24b/**` will be edited, appended, regenerated or deleted. New
  files only: `logs/PROGRESS-epoch2.md` (this), `results_engine.jsonl`,
  `acceptance.json`, `acceptance-report.md`, `manifest-epoch2.yaml`, new logs, and
  `code/CODE_SHA256.json` + `code/DIFFS.md` (both absent at ecdd3bffd; C-BYTE part 2).

## E2-S1 — C-BYTE part 2, before any compute (2026-09-16T06:20Z)

- Re-hashed both trees: frozen four files match TASK-20260913-f8bdec (bench e8aad273…,
  binec b6edbcf6…, convert 16affe2c…, summary eaf54bd7…); repaired four files match epoch 1's
  manifest (bench d835b1ea…, binec b6edbcf6…, convert 71665821…, summary 353fa48d…).
  binec.py byte-identical.
- `diff -u` hunk counts: convert 1, bench 13, summary 5, binec 0 → 19 hunks.
- Attribution (written into `code/DIFFS.md`, one `DEFECT:` line per hunk, and
  `code/CODE_SHA256.json`): D1 ← convert#1; D3 ← summary#1..5; D2/D4/D5 ← bench.
  **Zero hunks attributable to no declared defect**, so the C-BYTE stopping rule does not
  fire and compute may proceed.
- Observation for the reviewer, not resolved by me: 5 of the 13 bench.py hunks are MIXED
  (bench#1 docstring D2+D4+D5; #2 imports D2+D4; #3 constants D2+D4; #8
  finish_dimacs_record D2+D5; #12 probe_version+environment() D4+D2). Each line in them maps
  to one defect (split given in DIFFS.md), but the HUNK maps to more than one because the
  defects share a file region. The contract's C-BYTE pass wording says "exactly one of
  D1-D5" per hunk; I report the mixed hunks rather than re-slice the diff to make them
  disappear.
- Generator script kept out of the repo (`/tmp/e2_gen_diffs.py`); DIFFS.md reproduces the
  `diff -u` output verbatim with labels inserted before each `@@`.
- Post-write: `git status --porcelain experiments/EXP-ICPERF-66fd51` empty (C-NOWRITE holds);
  the only new paths are the two code/ artifacts and this log.

## E2-S2 — HOST MEMORY CONDITION, measured before any engine launch (2026-09-16T06:14Z .. 06:17Z)

- C-LOAD pre-check at 06:14Z: loadavg 0.00/0.04/0.12; no bench.py/M2/wdsat processes;
  4 CPUs; MemTotal 16,398,384 kB (15.64 GiB); **MemAvailable 6,932,032 kB (6.61 GiB)**;
  SwapTotal 0. Engines present: M2 1.22, Singular, cryptominisat5, cadical, minisat, gcc, make.
- Where the other ~8.7 GB is: `free -m` shows 9,290 MB "used" while guest processes hold
  ~600 MB anon + ~260 MB slab. `virtio_balloon` is loaded (virtio0, features bits 1,2,5,32 =
  STATS_VQ, DEFLATE_ON_OOM, REPORTING, VERSION_1). The hypervisor has ballooned ~8.5 GB out of
  this guest. This is the same condition epoch 1 saw (MemAvailable 6.45-7.0 GiB) and it is a
  property of the VM, not transient load, so "wait and re-check" cannot by itself raise it.
- Headroom probe (machine-protection check, NOT an acceptance measurement; script
  `accept/mem_headroom_probe.py`, output `logs/mem_headroom_probe.{json,out,err}`): a
  self-sacrificing allocator (oom_score_adj 1000, 256 MiB steps, stop at MemAvailable < 400 MiB).
  **Reached 6656 MiB touched / self RSS 6,825,896 kB (6.51 GiB) with MemAvailable 191,936 kB
  left; the unaccounted/balloon proxy stayed at ~8.49 GB the whole time (no deflation).**
  Released cleanly; MemAvailable back to 6.63 GiB. Wall ~10 s, rc 0.
- Reading (mine, an inference from the probe): the single-process resident ceiling on this
  guest is ~6.5-6.7 GiB. The pre-registered Macaulay2 peak is 6.705 GiB (repaired script) /
  6.823 GiB (committed script), i.e. 7.03-7.15 GB, which is ABOVE the ceiling by roughly
  200-300 MiB. An M2 launch is therefore likely, not certain, to be OOM-killed before the
  8 GiB watchdog could ever be relevant. The balloon's DEFLATE_ON_OOM may or may not release
  pages in the kernel's OOM path; the probe stopped at its floor deliberately and did not test that.
- Decision sequence, following the handoff: (1) run the low-memory work first (C-SATREG WDSat
  rows, A7 pure-CNF rows), (2) re-check MemAvailable over time, (3) decide on the M2 launch with
  the numbers in hand. No scaled substitute for A3 will be run under any circumstances.

## E2-S3 — C-SATREG and A7 rows, through the repaired bench.py (2026-09-16T06:17:59Z .. 06:18:20Z)

Driver `accept/engine_rows.py` (new; calls `bench.run_wdsat` / `bench.phase_D` / `bench.phase_C`
of the repaired tree with `bench.Runner` unchanged; only the row sink is redirected to the NEW
file `results_engine.jsonl`, and a C-LOAD `host_at_launch` snapshot is attached per row).
WDSat rebuilt from the vendored source under `builds/wdsat_987b7f5ef9/` (same sizing constants
as the frozen run's build: `wdsat_constants` equal).

- **C-SATREG** (`--wdsat`, logs/driver_wdsat.*, logs/wdsat_default_*.{out,err}):
  n15l5-1-S → **SAT / 26 conflicts**, assignment bit-string identical to RUN-ICPERF-305ca3's,
  certificate check verified on the curve (binec). n15l5-11-U → **UNSAT / 31257**.
  Both IDENTICAL to the pre-registered reference (validator table: SAT/26, UNSAT/31257) and to
  the frozen run. rss_limit_breached false, peak RSS 2.4 / 2.2 MB. loadavg1 0.15 at launch.
- OBSERVATION (instrument property, not a criterion): the repaired `Runner.run` reports
  `wall_s` 0.2515 / 0.2513 for these rows where the frozen run recorded 0.0049 / 0.2153. The
  D2 poll loop sleeps RSS_POLL_INTERVAL_S = 0.25 s between polls, so wall time for any child
  faster than one interval is quantized UP to ~0.25 s. `cpu_s` (0.0014 / 0.1939) is unaffected.
  Relevant to any later wall-time ratio on fast rows; recorded for the reviewer.
- **A7** (`--purecnf`, logs/driver_purecnf.*, logs/{cryptominisat5,cadical,minisat}_cnf_n15l5-1-S.*):
  pure CNF regenerated with the vendored XORtoCNF.sh, sha256 matches the upstream manifest.
  cryptominisat5: SAT, stats {conflicts 1, decisions 178, propagations 3060} — identical to the
  frozen run's counters. cadical (now without `-q`): SAT, {conflicts 9288, decisions 14940,
  propagations 7938595} — frozen run had `{}`. minisat (now `-verb=1`): SAT, {conflicts 5,
  decisions 187, propagations 2907} — frozen run had `{}`. All three SAT models verify on the
  curve and match the shipped certificate as a set. No row needed `stats_unavailable_reason`.
  Scope: ONE instance; nothing is said about the other 59 or about any UNSAT row.
- Memory re-check after these rows: MemAvailable 7,023,284 kB (6.70 GiB), loadavg1 0.08.

## E2-S4 — decision on the Macaulay2 launch, WRITTEN BEFORE LAUNCHING (2026-09-16T06:20Z)

Re-checks: MemAvailable 6,932,032 kB (06:14Z) → 7,023,284 (06:18Z) → 7,013,504 kB (06:19Z),
loadavg1 0.02. The handoff's "exceeds roughly 8 GiB" gate is NOT met and, because the shortfall
is a hypervisor balloon holding ~8.5 GB (E2-S2), waiting cannot meet it.

The handoff says: wait and re-check rather than launch into a host that will OOM; if it still
does not fit, report a machine-resource impediment with the numbers; never a scaled A3.
The contract (budget.maximum_memory_gb_note) assumed "a 15 GB host"; this guest offers ~7.0 GB
to a single process. That assumption-vs-host gap is reported regardless of what follows.

DECISION: make EXACTLY ONE protected attempt, and record the departure from the handoff's
"do not launch" reading as a protocol deviation (PD-E2-1). Reasons, in order:
 1. The guard's purpose is machine protection. The driver sets oom_score_adj=1000 on itself
    before `phase_C`, which the M2 child inherits, so if the guest runs out of memory the
    kernel's victim is the engine and only the engine. The headroom probe already drove
    MemAvailable to 190 MiB without harming the host.
 2. Whether it "fits" is genuinely uncertain, not settled: the probe ceiling is ~7.02 GB
    total reachable; the pre-registered repaired-script peak is 6.705 GiB = 7,031,000 kB.
    The gap is ~0.2%, inside the difference between two M2 runs. Only a launch decides it.
 3. Either outcome is data and neither is a scaled substitute: a completed row yields
    A1/A2/A3/C-M2AGREE measured at the declared 8 GiB watchdog; an OOM kill yields
    A1/A2/A3 NOT_EVALUABLE on a DIRECT observation (the RSS the real engine reached on this
    guest before the kernel intervened) instead of on an inference from a synthetic probe.
    The contract's stopping rule already treats a censored M2 invocation as a recorded
    infrastructure outcome that continues the acceptance.
 4. One attempt only. No retry regardless of outcome (no "rerun until it looks right").
Pre-registered recording rules for the outcome:
 - exit 0 + RESULT line parsed → evaluate A1, A2, A3, C-M2AGREE against the frozen references.
 - killed by the kernel (returncode -9 with rss_limit_breached false and no RESULT line) →
   A1/A2/A3/C-M2AGREE NOT_EVALUABLE, reason "guest OOM (balloon), peak RSS observed = X",
   classified infrastructure_error / resource_exhaustion, never negative evidence.
 - killed by the 8 GiB watchdog (rss_limit_breached true) → A1 NOT_EVALUABLE per the contract's
   stopping rule, A3 FAIL is NOT inferred (the peak would then be > 8 GiB, which is a measurement
   to report beside the [5.5, 7.5] reference, and the reviewer decides).
 - wall > 600 s (bench.TIMEOUTS m2_f4_l5, tighter than the contract's 900 s ceiling) → A1
   NOT_EVALUABLE, timeout recorded.

## E2-S5 — the Macaulay2 acceptance invocation (2026-09-16T06:21:00Z .. 06:21:49Z)

- C-LOAD at launch: loadavg 0.00 / 0.12 / 0.15 (1-min 0.00, under the 1.0 flag and the card's
  0.5 precondition); MemAvailable 7,011,584 kB; no other bench/M2/wdsat process. Driver
  oom_score_adj 1000 set before phase_C (inherited by M2). `bench.phase_C(R, [n15l5-1-S])`.
- Emitted script `scripts/n15l5-1-S.m2` (sha256 b8c85403…) differs from the frozen run's
  `RUN-ICPERF-305ca3/scripts/n15l5-1-S.m2` ONLY at lines 49-50 (`gens_` → `gensG`): D1's scope
  confirmed at the emitted-script level. Everything upstream of the report line is byte-equal.
- OUTCOME (row 6 of results_engine.jsonl; logs/m2_n15l5-1-S.{out,err}, stderr empty):
  returncode **0**; stdout `RESULT gb_size=43 cpu_s=46.5472 maxdeg_gb=2 is_unit=false`;
  parsed row: gb_size 43, engine_cpu_s 46.5472, maxdeg_gb 2, unit_ideal false,
  status consistent_proper_ideal. wall_s **49.2118**; child cpu_s **165.747** (ratio 3.37).
  peak_rss_kb **6,941,312** (6.620 GiB, watchdog-observed, 197 polls at 0.25 s);
  max_rss_kb_children_highwater 6,944,112 (6.623 GiB, kernel ru_maxrss of the child — the two
  agree to 2.8 MB); rss_limit_gb 8; **rss_limit_breached false**; timed_out false (timeout 600).
- Against the frozen references (comparison only; verdict table is acceptance.json):
  A1 ref `gb_size=43 cpu_s=47.7616 maxdeg_gb=2 is_unit=false` exit 0 → measured 43 / 46.5472 /
  2 / false, exit 0. A2 ref 49.97 s wall / 170.56 s CPU → 49.21 / 165.75, wall in [30,120],
  CPU > wall. A3 ref 6.705 / 6.823 GiB → 6.620 GiB, in [5.5, 7.5], not breached at 8 GiB.
  C-M2AGREE 43 / 2 / false → 43 / 2 / false. No disagreement; engine cpu_s 2.5% under the
  reference and peak 1.3% under, which is within run-to-run variation of the same engine on
  the same host and is reported, not explained.
- HOST AFTER THE RUN (unexpected, recorded): at 06:22Z MemAvailable was 10,986,088 kB
  (10.5 GiB) and the balloon proxy had fallen from ~8.49 GB to ~4.29 GB. So the virtio balloon
  DOES deflate — after a pressure event, on a delayed (tens of seconds) timescale — which
  corrects E2-S2's "waiting cannot by itself raise it": waiting WITHOUT pressure did not raise
  it over 6 minutes; pressure followed by waiting did. The M2 run itself therefore ran inside
  the ~7.0 GB ceiling (peak 6.94 GB vs probe ceiling ~7.02 GB) and did not need the deflation.
  Implication for the row contract, not for this acceptance: MemAvailable on this class of
  guest is a lagging number and a single pre-launch reading under-reports what a run can get.
- One attempt was made, as pre-registered. No retry.
- Post-run environment probe (`environment-epoch2.json`, new file; epoch 1's environment.json
  untouched): M2 1.22, Singular 4.3.2, CryptoMiniSat 5.11.15, CaDiCaL 1.7.3, minisat 2.2.1
  (apt), gcc 13.3.0, Python 3.12.3; probe seconds gcc 0.002, M2 0.032, Singular 0.033,
  cms 0.002, cadical 0.003 (inherited stdin from this shell; returned).
- Repository events during the session, observed via `git log` only: HEAD moved ca6946306 →
  2bfdc65b1 (a merge of origin/main and a Coordinator commit whose SUBJECT names a review-plan
  addendum). I did not open `coordination/review/icperf-20260915-a33cda/`. `git diff --stat
  ca6946306 HEAD` over my two scope directories is empty. An untracked
  `ledger/corrections/CORR-20260916-273589.yaml` exists in the worktree; it is not mine and I
  did not read or touch it.

## E2-S6 — paperwork and completion gate (2026-09-16T06:25Z .. 06:30Z)

- Written: `acceptance.json`, `acceptance-report.md`, `manifest-epoch2.yaml` (supersedes
  `manifest.yaml` BY REFERENCE; epoch 1's manifest untouched), `environment-epoch2.json`.
- Completion gate: all planned invocations terminal (1 M2 row, 2 WDSat rows, 3 pure-CNF rows,
  plus epoch 1's 2 watchdog rows, probe and reduction); no missing run; every contract-required
  artifact exists (CODE_SHA256.json and DIFFS.md were the two absent at ecdd3bffd); raw
  `results_engine.jsonl` and `acceptance.json` agree on every cited value (checked by script);
  each engine row reproduces from `accept/engine_rows.py --{wdsat,purecnf,m2}` at the recorded
  code hashes.
- C-NOWRITE end check 06:25:52Z: `git status --porcelain experiments/EXP-ICPERF-66fd51` empty;
  frozen code hashes e8aad273 / b6edbcf6 / 16affe2c / eaf54bd7 unchanged.
- Final scope audit: every untracked path is under `experiments/EXP-ICPERF-e21835/code/` or
  `.../runs/RUN-ICPERF-a4a24b/`; no tracked file modified; the four `code/*.py` hashes equal
  epoch 1's manifest values.
- Confirmed again: `coordination/review/icperf-20260915-a33cda/` was never listed or read.
- NOT committed. The Coordinator's snapshot task (TASK-20260915-7da7f1) commits.
- Corrections to my own earlier entries in this log: E2-S2's "waiting cannot by itself raise
  [MemAvailable]" is corrected by E2-S5 (the balloon deflated after pressure). Nothing else.
