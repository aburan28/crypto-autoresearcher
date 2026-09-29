# RUN-ICPERF-a4a24b — acceptance report (EXP-ICPERF-e21835)

TASK-20260915-4f4027, executor, **epoch 2**. Machine-readable table: `acceptance.json`.
Epoch 1 (Opus binding, stopped on quota after A4/A5/A6 ran) left the artifacts committed at
`ecdd3bffd`; they are cited, not re-run. Epoch 2 (fallback binding) ran the engine side and
wrote this report. Every artifact epoch 1 wrote is untouched.

**What this report is.** A criterion-by-criterion statement of what was *measured* beside
the *pre-registered reference* from EV-ICPERF-390707, with PASS / FAIL / NOT_EVALUABLE as
the executor's comparison of the two. It is not a declaration that the instrument is
accepted: that is a Coordinator decision on independent review (contract
`success_criterion`). Where a sentence below is an inference rather than a measurement it
says so.

**Scope.** One host (4 CPU; 15.6 GiB MemTotal of which ~7 GB was available to one process
at every epoch-2 launch, because a virtio balloon held the rest; no swap). One repaired
tree (`code/`, hashes in `code/CODE_SHA256.json`). One Groebner instance (n15l5-1-S), two
SAT regression instances (n15l5-1-S, n15l5-11-U), one pure-CNF instance (n15l5-1-S), one
hash-pinned frozen reduction input. Every number is a property of a measuring instrument
on that host. **Nothing here says anything about index calculus, point-decomposition
cost, any elliptic curve, l = 6, or any prediction of H-ICPERF-2c57cc / H-ICPERF-cc4847.**

## 1. Acceptance criteria

| id | verdict | epoch | measured | pre-registered reference | artifact |
|---|---|---|---|---|---|
| A1 | **PASS** | 2 | exit 0; `RESULT gb_size=43 cpu_s=46.5472 maxdeg_gb=2 is_unit=false`; row gb_size 43 / engine_cpu_s 46.5472 / maxdeg_gb 2 / unit_ideal false | exit 0; `RESULT gb_size=43 cpu_s=47.7616 maxdeg_gb=2 is_unit=false` | `results_engine.jsonl` M2 row; `logs/m2_n15l5-1-S.out` |
| A2 | **PASS** | 2 | wall 49.21 s; child CPU 165.75 s; ratio 3.37; loadavg1 0.00 | wall in [30, 120]; CPU > wall (ref 49.97 / 170.56, 3.4) | same row |
| A3 | **PASS** | 2 | peak RSS 6,941,312 kB = **6.620 GiB** (watchdog, 197 polls @ 0.25 s); kernel ru_maxrss 6,944,112 kB = 6.623 GiB; `rss_limit_breached: false` at 8 GiB | [5.5, 7.5] GiB, not breached (ref 6.705 / 6.823 GiB) | same row |
| A4 | **PASS_WITH_DECLARED_DEVIATION** | 1 | (ii) 64 GiB PROT_NONE reservation touching 256 MiB: exit 0, not breached, at the **declared 8 GiB**. (i) killed (SIGTERM, −15) with breached true at a **SCALED 2 GiB limit / 4 GiB target** | (i) 12 GiB allocator killed under 8 GiB; (ii) survives | `watchdog_control/outcomes.json` |
| A5 | **PASS** | 1 | repaired `environment()` returned in 0.083 s, exit 0, Singular version string, 0 unavailable, under inherited-pipe stdin; frozen `ver` body hung and its 60 s timeout fired at 60.062 s | returns < 60 s with a Singular line | `logs/probe_check.json` |
| A6 | **PASS** | 1 | control: frozen code reproduces archived summary.json 517/0; repaired: four distinct l=6 ratios 10.396 / 34.472 / 67.460 / 83.500; P5 Groebner clause `evaluated:false` naming engine_cpu_s; P6 `unevaluable:["n19l6"]`, holds null; 0 disagreements with v3_reduce under every reconstructible count | 156 values agree; those four ratios; those P5/P6 reports | `summary_regression.json` |
| A7 (non-gating) | **PASS** | 2 | cryptominisat5 {conflicts 1, decisions 178, propagations 3060}; cadical {9288, 14940, 7938595}; minisat {5, 187, 2907}; 0 rows needed `stats_unavailable_reason` | counter or reason per pure-CNF row | `results_engine.jsonl` pure_cnf rows |

Per-criterion notes, measured vs inferred:

- **A1.** Measured: the four RESULT fields and the exit status match the reference exactly;
  engine `cpu_s` is 2.5 % under it. The emitted script `scripts/n15l5-1-S.m2` differs from
  the frozen run's script only at lines 49–50 (`gens_` → `gensG`). Inferred: nothing beyond
  "the parse error was the thing zeroing the column on this instance" — the contract's own
  falsification reading of A1.
- **A2.** Measured values inside the envelope; the band is a sanity check, not a timing claim.
- **A3.** Measured: a 6.6 GiB multi-threaded real child was polled 197 times at the declared
  8 GiB limit and not killed. **Not established:** that the watchdog fires *at* 8 GiB on a
  real engine — no real child crossed 8 GiB, and the fire path was exercised only at 2 GiB
  (A4 (i)). The 8 GiB threshold magnitude therefore remains untested on any object. Host
  context: MemAvailable at launch was 6.69 GiB; the engine's 6.94 GB peak fit under the
  ~7.02 GB single-process ceiling the headroom probe measured (§4).
- **A4.** Cited from epoch 1; not re-run. The 8 GiB threshold is untested at magnitude on
  the synthetic allocator, exactly as epoch 1 said. Epoch 2 saw the same ~6.5–7.0 GiB
  MemAvailable at every launch and did not re-run (i); the balloon deflation to 10.5 GiB
  observed *after* the M2 run (§4) was not used to re-run anything — that would have been a
  second measurement selected by a favourable host state.
- **A5.** Cited from epoch 1. The item epoch 1 recorded as UNEXPLAINED — why the frozen 60 s
  timeout returned here but not in RUN-ICPERF-c9590f — has no new measurement and stays
  unexplained.
- **A6.** Cited from epoch 1. The contract's "156" count is not reconstructible from
  `v3_reduce.json`; epoch 1 reported 180/180, 158/158 and 158-of-236-comparable with zero
  disagreements and did not adjust the reference. The 12 UNEXPLAINED leaf differences
  (P2 `ratio` absent vs present-as-null) remain UNEXPLAINED. Pointer only: `DIFFS.md` hunk
  summary.py#3 is the code site that emits that key. A reviewer adjudicates.
- **A7.** Measured on one SAT instance: 3/3 engines yield counters where the frozen instrument
  yielded 1/3 (cryptominisat5's counters are identical to the frozen run's). All three
  models verify on the curve and match the shipped certificate as a set. Nothing is said
  about UNSAT rows or other instances.

## 2. Controls

| id | verdict | epoch | what was measured |
|---|---|---|---|
| C-BYTE | **PASS_WITH_OBSERVATION** | 1 + 2 | frozen hashes = TASK-20260913-f8bdec (bench e8aad273…, binec b6edbcf6…, convert 16affe2c…, summary eaf54bd7…); repaired hashes = epoch-1 manifest (bench d835b1ea…, convert 71665821…, summary 353fa48d…); binec.py byte-identical. 19 hunks (convert 1, bench 13, summary 5), **0 attributable to no declared defect**. Observation: 5 bench.py hunks are MIXED (D2+D4+D5 docstring; D2+D4 imports; D2+D4 constants; D2+D5 `finish_dimacs_record`; D4+D2 `probe_version`/`environment`) — every *line* maps to one defect, but the *hunk* maps to more than one, so the contract's "exactly one" wording is not met at hunk granularity. Reported, not re-sliced. `code/CODE_SHA256.json`, `code/DIFFS.md`. |
| C-M2AGREE | **PASS** | 2 | gb_size 43, maxdeg_gb 2, is_unit false — identical to the two-engine agreement of EV-ICPERF-390707 joint V2. |
| C-WATCHDOG-NULL | PASS_WITH_DECLARED_DEVIATION | 1 | see A4. |
| C-SUMREG | **PASS** | 1 | see A6; `fix_boundary_cells_block_unchanged.n_moved = 0` — no median, ratio or threshold moved, so the invalidation rule did not fire. |
| C-SATREG | **PASS** | 2 | n15l5-1-S **SAT / 26**, assignment identical to RUN-ICPERF-305ca3, certificate verified on the curve; n15l5-11-U **UNSAT / 31257**. Identical to the reference; WDSat build constants equal to the frozen build's. Observation: `wall_s` 0.2515 / 0.2513 vs frozen 0.0049 / 0.2153 — the D2 poll loop quantizes wall time *up* to the 0.25 s poll interval for sub-interval children (`cpu_s` 0.0014 / 0.1939 unaffected). Not a criterion; relevant to later wall-time ratios on fast rows. |
| C-NOWRITE | **PASS** | 1 + 2 | `git status --porcelain experiments/EXP-ICPERF-66fd51` empty at epoch-1 start and at epoch-2 start and end (06:25:52Z); frozen code hashes re-verified. |
| C-PROBE | **PASS** | 1 | see A5. |
| C-LOAD | **PASS** | 1 + 2 | epoch-2 loadavg1 at launch: WDSat 0.15, pure-CNF 0.15, **M2 0.00** (< 1.0 flag, < 0.5 card precondition); MemAvailable 6,987,896 / 6,987,896 / 7,011,584 kB. No launch flagged. |

## 3. Protocol deviations (epoch 2)

- **PD-E2-1 — M2 launched below the handoff's ~8 GiB MemAvailable gate.** MemAvailable was
  6.61–6.70 GiB at every re-check over ~7 minutes because a hypervisor balloon held ~8.5 GB;
  waiting without pressure did not move it. Decision and outcome rules were written in
  `logs/PROGRESS-epoch2.md` E2-S4 *before* the launch: the gate's purpose (machine
  protection) was met by `oom_score_adj 1000` on the driver, inherited by the engine, so the
  only possible OOM victim was the engine; fit was uncertain (~0.2 % gap between the probe
  ceiling and the reference peak); one attempt only; no scaled substitute under any outcome.
  The engine fit and completed. This departs from the handoff's guidance, not from the frozen
  contract.
- **PD-E2-2 — instrument timeout 600 s, contract ceiling 900 s.** `bench.TIMEOUTS["m2_f4_l5"]`
  is 600 s in the immutable repaired tree; 600 < 900 so the ceiling was respected. The row
  took 49 s.
- **PD-E2-3 — headroom probe not in the contract.** `accept/mem_headroom_probe.py` touched
  6.5 GiB and released it, to measure the guest's ceiling rather than guess it. Retained as
  `logs/mem_headroom_probe.{json,out,err}`; offered as evidence for no criterion.

## 4. Host observations (recorded, not interpreted beyond what is stated)

- `virtio_balloon` (features STATS_VQ, DEFLATE_ON_OOM, REPORTING) held ~8.49 GB of the
  16.4 GB guest at every epoch-2 launch; `free` showed 9.3 GB "used" against ~0.6 GB of
  process memory. The headroom probe reached 6,825,896 kB resident with 191,936 kB
  MemAvailable left and the balloon proxy flat → single-process ceiling ≈ 7.02 GB.
- The M2 row peaked at 6.94 GB observed, under that ceiling, and completed.
- At 06:22:32Z, after the M2 run, MemAvailable was 10,986,088 kB and the balloon proxy
  4.29 GB: the balloon deflated ~4.2 GB within about a minute of the pressure event. My
  E2-S2 log line that waiting "cannot by itself raise it" was too strong and is corrected
  in E2-S5: waiting *without* pressure did not raise it; pressure followed by waiting did.
  For the row contract this means a single pre-launch MemAvailable reading on this guest
  class under-reports what a run can obtain.
- Contract vs host: `budget.maximum_memory_gb_note` assumes "a 15 GB host". This guest
  offered ~7 GB to a single process at launch. The assumption did not hold; the row fit anyway.

## 5. Disagreements with pre-registered references or with epoch 1

- None on any pass/fail-bearing value. Numeric differences from the A1/A2/A3 references
  (engine cpu_s −2.5 %, wall −1.5 %, peak RSS −1.3 %) are reported as measured, not
  adjusted and not explained.
- No disagreement with any epoch-1 measurement; epoch 2 re-measured none of them.

## 6. What was not measured

- The 8 GiB watchdog firing on a real engine (no real child crossed 8 GiB), and on a
  synthetic allocator at magnitude (A4 (i) ran at 2 GiB). The threshold's *value* is
  untested; its *mechanism* (poll, sum over process group, kill group) is tested at 2 GiB
  and its *non-firing* below the limit is tested at 6.6 GiB on a real engine.
- A5's unexplained item; A7 beyond one SAT instance; anything Singular computes.

## 7. Failure classification

No failure occurred in epoch 2. Epoch 1's stop was a billing-quota event on the runtime and
belongs to no class in the executor taxonomy that touches the science; it is recorded in
epoch 1's manifest and in `manifest-epoch2.yaml`.

## 8. Discipline confirmations

- `coordination/review/icperf-20260915-a33cda/` was neither listed nor read in epoch 2 (a
  Coordinator commit subject naming a review-plan addendum was seen in `git log` only).
- No file committed at `ecdd3bffd` under `code/` or `runs/RUN-ICPERF-a4a24b/` was edited,
  appended to, regenerated or deleted; the four `.py` hashes were re-verified after every
  write. All epoch-2 outputs are new files.
- One Macaulay2 attempt was made. All raw outputs, including the headroom probe, are retained.
