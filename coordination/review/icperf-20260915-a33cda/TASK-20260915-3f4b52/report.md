# TASK-20260915-3f4b52 — Validator report, joints R1–R5 and proves-too-much object 1

Review round: REVIEW-ICPERF-20260915-a33cda (+ ADD1). Object under test:
RUN-ICPERF-a4a24b and the repaired tree `experiments/EXP-ICPERF-e21835/code/`
**at the bytes the run certifies** — bench.py `d835b1ea…`, convert.py `7166582b…`,
summary.py `353fa48d…`, binec.py `b6edbcf6…` (= commit `2bfdc65b`, the HEAD of the
Macaulay2 row). The working tree's bench.py is now `2eee0153…` (commit `e1728d8a8`,
"D6", CORR-20260916-d51133); I did **not** review that version. Every execution
below ran from a copy of the accepted bytes under `/tmp/val3f4b52/`; nothing under
`experiments/` was written (§R5.2).

This report covers my five joints only. I did not read `review-plan-r6.yaml` or
anything under `TASK-20260915-abf147/`, and I offer no whole-claim verdict.
`acceptance.json` and `acceptance-report.md` were read as the object under test;
every number below is re-derived from raw artifacts or from my own measurement,
and the few things I could not re-derive are listed in §7.

Scope of every statement here: one host (4 CPUs, 15.6 GiB, no swap, virtio
balloon), one instance (n15l5-1-S; n15l5-11-U for the SAT regression), one
Macaulay2 invocation, one Python (3.12.3). Nothing bears on index-calculus cost,
point decomposition, or the security of any curve.

Supporting artifacts: `artifacts/r1..r5/` beside this file (scripts, raw JSON,
captured stdout/stderr). Paths cited as `artifacts/…` are relative to this directory.

## 0. Verdict table

| joint | verdict | rests on | overturns a recorded prior? |
|---|---|---|---|
| R1 Macaulay2 report line | **holds** | regenerated script sha `b8c85403…` = committed run script; direct M2 exit 0, stderr empty, `RESULT gb_size=43 cpu_s=47.974 maxdeg_gb=2 is_unit=false`; regex at bench.py:579 matches; harness row 43 / 46.5714 / 2 / false | No. Coordinator's regex suspicion tested and not borne out (M2 prints reals without exponent across 4e-6 … 1.2e6). |
| R2 resident-set limit | **holds**, with two findings the plan's wording does not survive | live child `Max address space unlimited`; my 12 GiB hog killed at 8.044 GiB (SIGTERM, breached true); my 64 GiB PROT_NONE reserver survived at 394 MiB; M2 peak 6.58 GiB vs external VmHWM 6.59 GiB (0.16 %) | Partly. "does not double count … shared pages" is false: COW pages after fork ARE summed twice (demonstrated). Threads are not. ADD1-a prior confirmed and quantified: worst-case inter-poll overshoot 1.40 GiB → kill decision at up to 9.4 GiB. |
| R3 reduction | **holds** | frozen summary.py reproduces archived summary.json byte-for-byte; repaired: cells block identical (186/186 leaves); 156/156 (recovered definition), 180/180, 158/158; four distinct l=6 ratios matching reference; deletion controls: P3, P4, P5, P6 all `holds: null` + explicit `unevaluable` | **Yes, twice.** (a) 156 IS reconstructible — from `work/v3_celldiff.py` over `work/v3_reduce.json`, not from the `artifacts/v3_reduce.json` the contract cites. (b) P3's aggregation reports null-for-None, not false; the Coordinator predicted the executor would leave it false-for-null. |
| R4 environment probe | **holds** | frozen probe under an unwritten-pipe stdin: Singular blocks in `pipe_read`, one process, no children; returns at 60.06 s with `unavailable: … timed out`; repaired probe returns Singular 4.3.2 in 0.008 s | **Yes.** The 60 s timeout did not "fail" in c9590f: the process was SIGINT'd 12.9 s after launch (launch_time.txt 10:22:40.07Z, bench_stderr.log last write 10:22:52.96Z). The contract's "~4 minutes" and "timeout did not fire" have no artifact behind them. The pipe-drain hypothesis is refuted for Python 3.12 `subprocess.run`. |
| R5 scope, custody, manifest | **holds** on the measurement package; **breaks** on custody discipline during the review window and on C-BYTE at hunk granularity | frozen hashes match f8bdec; `git status --porcelain experiments/EXP-ICPERF-66fd51` empty; code hashes invariant across ecdd3bffd → 6ad48e04c → 2bfdc65b → 5fa8ffed8; every hunk maps to D1–D5 but 5 of 13 bench.py hunks map to 2–3 defects | Partly. Coordinator predicted "least informative joint"; it was not: the committed run manifest was edited in place by a concurrent session (3dc30bfcf) and restored by merge; bench.py changed (e1728d8a8) after the run and during review; epoch 1's recorded commit does not contain the code that ran. |
| proves-too-much object 1 | **discriminates** — every criterion fails on the frozen tree, A1/A4/A6 in exactly the declared way; A5 fails, but not in the way the plan declared | §6 | A5's frozen failure mode is "returns at 60 s with `unavailable`", not "does not return". |

Per-joint verdicts use the attestation vocabulary (`holds`/`breaks`/`inconclusive`);
R5 is recorded `breaks` in `attestation.yaml` because a joint stated as "the frozen
tree and the two archived run packages are byte-unchanged; every hunk attributable
to exactly one declared defect; manifest complete" is not met on its second clause
at hunk granularity, and its custody premise ("the tree holds still under review")
was violated. The measurement artifacts themselves are intact — see §R5.

## 1. Machine conditions

Read before each launch. `MemTotal 16398384 kB`; `MemAvailable` 11.08–11.21 GiB
throughout my session (the balloon had released; the acceptance run saw 6.6–6.7
GiB). `SwapTotal 0`. Load averages are recorded per measurement below; two harness
runs were taken at 1-minute load 0.83 and 0.94 (moderate on 4 CPUs) and their
**wall times are reported as unusable**; the non-timing readings from those runs
(exit codes, `/proc/<pid>/limits`, peak RSS) are load-insensitive and are used.

## 2. R1 — the Macaulay2 report line, end to end

Attack plan steps (1)–(5), each executed.

**(1) Script regeneration.** Ran the repaired `convert.py` and the frozen
`convert.py` on `inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/n15l5-1-S.in`
from `/tmp` copies of each tree.

| script | sha256 | equals committed |
|---|---|---|
| repaired regenerated | `b8c8540378dcf9f7…` | `runs/RUN-ICPERF-a4a24b/scripts/n15l5-1-S.m2` ✔ |
| frozen regenerated | `65323db0b4a780f4…` | `EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/scripts/n15l5-1-S.m2` ✔ |

Unified diff (`artifacts/r1/script_diff_frozen_vs_repaired.patch`): exactly two
lines, 49–50, `gens_` → `gensG` at four occurrences. Nothing else in 33 587 bytes
changed. The RESULT line's byte format is untouched.

**(2) Direct `M2 --script`.** Repaired script, launched 06:57:41Z, loadavg
0.12/0.16/0.10, MemAvailable 11.15 GiB: exit **0**, stderr **empty** (0 bytes),
stdout exactly `RESULT gb_size=43 cpu_s=47.974 maxdeg_gb=2 is_unit=false\n`,
wall 60.36 s, children CPU 163.35 s, `ru_maxrss` 6 853 368 kB (6.54 GiB), 11
threads, child `/proc/<pid>/limits`: `Max address space unlimited`
(`artifacts/r1/m2_repaired_direct.json`).

Frozen script (control), 07:20:08Z, loadavg 0.06: exit **1**, stdout empty,
stderr `frozen_n15l5-1-S.m2:49:7:(3):[6]: error: syntax error at '='` + M2
backtrace, wall 48.01 s, CPU 164.35 s. The computation ran to completion (CPU
164 s) and the parse error fired **after** it, at the RESULT line — the D1
signature as declared (`artifacts/r1/m2_frozen_direct.{json,err}`).

**(3) Regex, character by character.** The regex as it appears in the repaired
`bench.py:579` (not as the plan quotes it — they are identical):

    RESULT gb_size=(\d+) cpu_s=([\d.]+) maxdeg_gb=(\d+) is_unit=(true|false)

`re.search` on my direct line → `('43','47.974','2','false')`; on the acceptance
row's line `RESULT gb_size=43 cpu_s=46.5472 …` → match; on EV-ICPERF-390707 C5's
line → match. The Coordinator's named suspicion — a `cpu_s` printed in a form
`[\d.]+` does not match — I tested by having M2 print reals across the range
(`artifacts/r1/rrprint.m2`, `.out`): `0.0001→.0001`, `1e-5→.00001`,
`3.975e-6→.000003975`, `1234567.891→1234570`, `2.0→2`, `0.→0`. M2's default
printing uses six significant digits and **no exponent notation** across that
range, and `[\d.]+` matches every form. Residual (not reachable here): `max {}`
on an empty basis prints `-infinity`, which `(\d+)` would reject — the zero ideal
cannot occur with field equations appended.

**(4) Harness row.** Ran the repaired `Runner`/phase-C path from a `/tmp` mirror
of the repo layout (07:05:25Z, loadavg **0.83** — wall unusable; other fields used).
Row (`artifacts/r1/harness_phaseC_repaired_results.jsonl`): `gb_size 43`,
`engine_cpu_s 46.5714`, `maxdeg_gb 2`, `unit_ideal false`,
`status consistent_proper_ideal`, `returncode 0`, `rss_limit_breached false`,
`peak_rss_kb 6898860`, 217 polls at 0.25 s. No null in any parsed field.

The acceptance's own row, read from `results_engine.jsonl` (not from
acceptance.json): `gb_size 43`, `engine_cpu_s 46.5472`, `maxdeg_gb 2`,
`unit_ideal false`, `wall_s 49.2118`, `cpu_s 165.747`, `peak_rss_kb 6941312`
(6.620 GiB), `rss_polls 197`, `loadavg1_at_start 0.0`. 197 × 0.25 s = 49.25 s ≈ wall.

**(5) Agreement.** gb_size 43 / maxdeg 2 / non-unit: my direct run, my harness
run, the acceptance row, and EV-ICPERF-390707 joint V2 run C5 (`cpu_s=47.7616`)
all agree. `engine_cpu_s` values 47.97 / 46.57 / 46.55 / 47.76 are within 3 %.
R6's independent result I have not seen (blind), so step (5)'s second half is
left to the composition.

**Timing observation (A2 envelope).** Across four M2 runs, wall = 48.0 s (load
0.06), 49.2 s (load 0.0, acceptance), 54.2 s (load 0.83), 60.4 s (load 0.12) while
children CPU = 163.3–165.7 s (±0.7 %). On this 4-CPU host with an 11-thread F4,
wall is not a stable quantity even at low load; CPU is. All four fall inside A2's
[30, 120] band; the band is wide enough to hide this and the contract says so.

**Verdict R1: holds.** The end-to-end chain the Coordinator wanted shown — regex
matched against the line the repaired converter emits through the repaired
harness, with the ROW carrying non-null values — is shown.

**Beyond the plan (R1/R5 boundary): `wall_s` for fast children is not a
measurement at the accepted commit.** The accepted poll loop (bench.py:192–209)
samples, then `time.sleep(0.25)`, so a child that exits inside an interval is
noticed at the next boundary. Side by side, frozen RUN-305ca3 vs the acceptance
run on identical instances, identical conflict counts:

| row | frozen wall_s | accepted wall_s | ratio |
|---|---|---|---|
| WDSat default n15l5-1-S (26 conflicts) | 0.0049 | 0.2515 | 51× |
| WDSat default n15l5-11-U (31257 conflicts) | 0.2153 | 0.2513 | 1.2× |
| CryptoMiniSat pure_cnf n15l5-1-S | 0.0091 | 0.2533 | 28× |
| MiniSat pure_cnf n15l5-1-S | 0.0176 | 0.2535 | 14× |
| CaDiCaL pure_cnf n15l5-1-S | 0.7172 | 0.7538 | rounds up to 3 × 0.25 |

My standalone cryptominisat5 on the same DIMACS (load 0.04): 0.0049 / 0.0048 /
0.0045 s (`artifacts/r2/fastchild_cms_standalone.json`). CPU and conflicts are
unaffected (C-SATREG's exact conflict counts hold). Epoch 2 disclosed this as an
anomaly; CORR-20260916-d51133 records D6 as the cause and an unaccepted fix. My
position: for the row contract, every wall-based ratio among sub-0.25 s children
(P2's `wdsat_default_over_*` wall ratios, P3's `*_wall_censored` clauses on l=5)
would read ≈1 regardless of the engines. No acceptance criterion tests a fast
child's wall time, so the acceptance could not have seen this. It is a criterion
gap, not a mis-execution.

## 3. R2 — the memory limit is a resident-set limit and is not double counting

**(1) My own null objects, at the declared 8 GiB, on this host** (MemAvailable
10.9–11.1 GiB at launch, so 8 GiB resident was reachable — the acceptance host
could not have done this and did not claim to). Scripts:
`artifacts/r2/hog_resident.py` (touches 256 MiB steps to a 12 GiB target, 0.05 s
hold, prints its own `/proc/self/status` each step) and
`artifacts/r2/reserve_addrspace.py` (mmap 64 GiB `PROT_NONE|MAP_NORESERVE` in
chunks, then touches 384 MiB). Driver `artifacts/r2/drive_null.py` calls the
accepted `bench.Runner.run` unmodified (`RSS_LIMIT_GB = 8`, not patched). These
are not timing measurements; loadavg was 1.4–1.9 (my earlier M2 runs) and is recorded.

| object | tree | returncode | rss_limit_breached | peak_rss_kb | child's own last line |
|---|---|---|---|---|---|
| (i) hog 12 GiB | repaired | **−15 (SIGTERM)** | **true** | **8 434 396 (8.044 GiB)** | `touched=8192 MiB VmRSS=8398536 kB` |
| (ii) reserve 64 GiB | repaired | **0** | **false** | 403 840 (394 MiB) | `SURVIVED … VmSize=67520384 kB` |
| (i) hog | frozen | 1 | *(field absent)* | *(absent)*; highwater 6 039 124 | `OSError: [Errno 12] Cannot allocate memory` at 5.9 GiB touched |
| (ii) reserve | frozen | 3 | *(absent)* | *(absent)* | `limits: Max address space 6442450944`; `mmap reservation FAILED at chunk 0: errno=12` |

Direction (i) at magnitude: kill fired one poll after crossing, overshoot
45 788 kB (44.7 MiB) at the hog's ≈1.1 GiB/s growth. Direction (ii): 64.4 GB of
address space, 394 MiB resident, not killed. Both directions at the **declared**
8 GiB, which the acceptance run could not reach (ADD1-a).

**(2) RLIMIT_AS on a live child.** Read from `/proc/<pid>/limits` of the running
M2 child under each tree (`artifacts/r1/harness_phaseC_*_capture.json`, `watcher.limits`):

    repaired: Max address space   unlimited     unlimited     bytes
    frozen:   Max address space   6442450944    6442450944    bytes

The source grep agrees (`setrlimit` appears only in the frozen bench.py:117), but
the live readout is the check.

**(3) RSS accounting — reading and demonstration.** `pgid_rss_kb` (bench.py:81–96)
lists numeric entries of `/proc`, keeps those whose `pgrp` (field after the last
`)` in `/proc/<pid>/stat`) equals the child's session id, and sums `statm[1]`
(resident pages) × page size. `/proc` lists thread-group leaders only; threads
live under `/proc/<pid>/task/` and are **not** enumerated. Processes, not threads.

Demonstration, threads: M2 runs 11 threads in one process (`pgid_members_max 1`).
Harness `peak_rss_kb` 6 898 860 kB vs my external 0.1 s poller on the same child:
max `VmRSS` 6 899 460 kB, `VmHWM` 6 909 608 kB. Difference 0.16 %, far inside the
25 % double-counting signature. The acceptance's own row, 6.620 GiB, sits in
A3's [5.5, 7.5] band, not near double.

Demonstration, shared pages: `artifacts/r2/fork_share.py` maps 1 GiB anonymous,
touches it, forks, and reads both processes' status:

    pid 193747 (parent) VmRSS 1058268 kB  RssAnon 1051616 kB
    pid 193749 (child)  VmRSS 1054208 kB  RssAnon 1051616 kB

Physical memory used ≈1 GiB; the process-group sum is ≈2.06 GiB. **The plan's
statement "does not double count threads or shared pages" is half true.** COW
pages after `fork()` are counted once per process that maps them. The direction
is conservative (an earlier kill, never a missed one), and no engine in this
contract forks (M2, WDSat, the SAT solvers, Singular are single-process; §R4),
so no acceptance row was affected. It would matter for a forking engine or a
driver that forks workers inside the child's session, and it should be written
into the row contract as a known over-count rather than left as a claim of
correctness.

**(4) Peak is a maximum over samples, not the last sample.** M2's RSS falls
before exit: my external poller's `last_vmrss` 6 056 928 kB against `max_vmrss`
6 899 460 kB; the harness recorded `peak_rss_kb` 6 898 860 — the maximum, not the
tail. On the direct run the same pattern: sampled max 6 852 880 vs last 5 832 420.

**Beyond the plan — the two peak fields on fast children.** The poll loop samples
`pgid_rss_kb` once immediately after `Popen` and then every 0.25 s; a child that
exits inside the first interval leaves exactly one sample, taken at exec time.
The acceptance's cryptominisat5 row records `peak_rss_kb 4` (four kilobytes);
the standalone solver's `ru_maxrss` is 12 052 kB. The companion field
`max_rss_kb_children_highwater` is `getrusage(RUSAGE_CHILDREN).ru_maxrss`, which
is the driver process's cumulative high-water over **all** children it has ever
waited on — the WDSat rows carry 42 356 kB, the acceptance's direction (ii)
reserver carries direction (i)'s 2 176 560 kB. So for any child that finishes in
under 0.25 s, `peak_rss_kb` under-reads and `max_rss_kb_children_highwater`
over-reads; neither is that child's peak. Irrelevant to the 8 GiB watchdog (a
child cannot breach 8 GiB unsampled in 0.25 s unless it allocates at >32 GiB/s),
relevant to the fast-solver memory column. Not a declared defect; a limitation
the row contract should carry.

**ADD1-a — is the 8 GiB threshold established, and what is the worst-case
overshoot?** The acceptance did not test the threshold at magnitude (direction
(i) at `rss_limit_gb 2`, `outcomes.json`); I did (table above). The arithmetic is
magnitude-independent: `limit_kb = RSS_LIMIT_GB * (1 << 20)` (bench.py:177),
`total += int(statm[1]) * PAGE_KB` with Python integers, comparison `rss > limit_kb`
(bench.py:199). No 32-bit path, no unit conversion that could invert.

Overshoot, from my own fine-grained series on the acceptance M2 invocation
(`artifacts/r2/m2_series.json`: 942 samples at ≈0.05 s, peak 6 600 052 kB, load
not recorded for this run — the field is null; adjacent runs at 07:07 read
1.4–1.9, so the burst rates below are if anything **under**-estimates of a quiet
host):

| window | max RSS growth observed | where |
|---|---|---|
| 0.25 s (one poll interval) | **1 468 576 kB = 1.40 GiB** | t = 5.14→5.34 s, 1.12→2.52 GiB |
| 0.30 s (interval + poll cost) | 1.41 GiB | same burst |
| 1.0 s | 1.68 GiB | t ≈ 10.8→11.6 s |
| 5.25 s (interval + SIGTERM grace) | 3.15 GiB | t ≈ 10.8→14.7 s |

Burst rate ≈7.0 GiB/s over the worst 0.2 s; mean rate to peak 140 MiB/s. So:

- Kill decision can see up to **8 + 1.40 ≈ 9.4 GiB** resident if the burst lands
  on the limit. At the acceptance peak (6.62 GiB) headroom to 8 GiB is 1.38 GiB —
  one worst-case burst.
- M2 honours SIGTERM: in `artifacts/r2/m2_sigterm.json` it died **0.151 s** after
  the signal with no further growth. Realistic worst case before death ≈ 9.4 + 1.0
  ≈ **10.4 GiB**.
- A child that ignored SIGTERM would get the 5.0 s grace before SIGKILL, in which
  the observed maximum growth is 3.15 GiB → ≈ **12.5 GiB**, on a 15.6 GiB host
  with no swap. That would OOM the guest with a hostile or stuck child.
- The acceptance's 12 GiB null object (128 MiB steps, 0.05 s hold, ≈0.7 GiB/s)
  and mine (≈1.1 GiB/s) are 6–10× gentler than M2's worst burst, so they cannot
  surface this; the Coordinator's prior is confirmed and now has a number.

Two further facts for the composition. First, the acceptance's machine
protection did not come from the instrument: `oom_score_adj = 1000` is written by
the acceptance wrapper `accept/engine_rows.py:100`, not by bench.py; a row
contract driving `bench.py main()` would have no OOM self-sacrifice unless it adds
one. Second, on the acceptance host (MemAvailable 6.6–6.7 GiB) the 8 GiB threshold
was **unreachable**, so the effective limit on the M2 row there was the kernel's,
not the watchdog's — the row passed A3 because M2's 6.62 GiB fit, not because the
watchdog bounded it.

**Verdict R2: holds** — the limit is resident-set, RLIMIT_AS is gone at runtime,
both null objects behave as declared at the declared magnitude, the peak is a
maximum, and there is no thread double-counting. Recorded against the plan's
wording: shared-page double counting exists (conservative); the poll-interval
overshoot is ≈1.4 GiB for this engine and the kill grace makes 12.5 GiB
reachable for a SIGTERM-ignoring child.

## 4. R3 — the reduction reports what it cannot evaluate, uniformly, and moves no number

**(1) Scratch run, no writes.** Copied `RUN-ICPERF-305ca3/results.jsonl` to
`/tmp/val3f4b52/r3/{frozen,repaired}/`, ran each tree's `summary.py` on its copy.
`git status --porcelain experiments/EXP-ICPERF-66fd51` before and after: empty.
Byte identity: my frozen output `0c36e5e2…` **=** archived RUN-305ca3
`summary.json`; my repaired output `c3e600d9…` **=** the acceptance's
`summary_regression/repaired/summary.json`. The reduction is deterministic and
the acceptance's inputs were the archived ones.

**(2) The 156 — ADD1-b.** The Coordinator's prior: an authoring slip, not
reconstructible. **Overturned.** The count is reproducible and I reproduced it:

- `coordination/review/icperf-20260913-66fd51/TASK-20260913-6c5729/work/v3_celldiff.py`
  (sha `cac2483e…`) counts `summary.json` `cells[*][*]` keys ending
  `_wall_s`/`_conflicts`/`_n` that have a counterpart in
  **`work/v3_reduce.json`**'s `per_cell_table`, agreeing to 1e-9 relative.
- Against the frozen summary: **156 checked, 156 match**, 24 keys with no
  counterpart, 6 unparsed. Against the repaired summary: **156/156** identically
  (`artifacts/r3/compare_out.json`, block `a_156_definition_recovered`).
- The earlier validator's report (`TASK-20260913-6c5729/report.md:188`) cites
  exactly this: "156 of 156 numeric values in summary.json's per-cell … `work/v3_celldiff.py`".

The contract (specification.yaml:118–119, 357, 472) cites
**`artifacts/v3_reduce.json`** (sha `50c39ea0…`), a *different file* with a
different layout (`cells → n15l5 → S → wdsat_default_wall_s …`) from
`work/v3_reduce.json` (sha `0a79fb54…`, `per_cell_table → "n15l5/S" → "wdsat/default" → median_wall_s`).
Both were committed together at 9181fbe1d. Under the artifacts-file layout the
definable counts are 180/180 (shared keys), 158/158 (numeric shared),
236 → 158 (validator numerics with a counterpart) — the executor's figures,
which I reproduce (`compare_out.json` block `b`). I also cross-checked the two
v3_reduce files against each other: **144 agree, 0 disagree** where my key
mapping found a counterpart; 18 engine/config pairs (cms_xor, m2_f4, singular)
I did not map. So the "uncomfortable possibility" in ADD1-b is realised in its
benign form: 156 came from a different **file** than the one the contract names,
both produced by the same validator task from the same reduction, numerically
consistent wherever both define a value. The substantive claim — the repaired
reduction agrees with the independent one wherever both compute — survives under
all four definitions. **The contract's reference is nevertheless defective**: its
number and its cited file do not go together, and neither the executor nor a
reader following the citation can reconstruct 156 from `artifacts/v3_reduce.json`.
That belongs in the composition as a contract defect to be superseded, not
edited, per ADD1-b's own rule.

**(3) Attributed diff against the frozen summary.json.** My own leaf-walker
(`artifacts/r3/compare.py`) finds the `cells` block **identical, 186/186 leaves**
— no median moved. Over the whole document: 135 leaf differences (the executor's
driver counts 125; the walkers differ on list elements), classified:

| class | n |
|---|---|
| new reporting fields (`evaluated`, `reason`, `n_clauses`, `n_evaluated`, named operands) — D3b/c | 68 + 8 + 6 + 2 |
| P2 clause cells now present as `ratio: null, evaluated: false` where frozen `P2.cells` was `{}` — D3b | 24 (12 `ratio`, 12 companions) |
| D3a loop-variable leak: three l=6 ratios corrected | 3 |
| D3b P5 Groebner clause recorded unevaluated | 6 |
| top-level `holds` true → null (P5, P6) — D3b/c | 2 |
| elements of the new `unevaluable` lists (P2: 12, P5: 3, P6: 1) | 16 |

The last row my classifier labelled `UNATTRIBUTED` mechanically (it had no rule
for list elements); on reading, all 16 are the contents of the new `unevaluable`
lists, a D3b/c reporting field. **Zero numeric values moved.** The only numbers
that differ are the three D3a corrections; n19l6/U's value is unchanged because
the leaked variable held the last cell's own value.

**ADD1-c — the 12 ABSENT-vs-null `ratio` keys.** They are
`/predictions/P2/cells/<cell>/<label>/wdsat_default_over_{m2_f4,singular}/ratio`.
Frozen `P2.cells` is `{}`: the frozen code emitted no P2 cell at all when no
Groebner row existed. The repaired code emits one cell per clause with
`ratio: null, evaluated: false, reason: "no median for m2_f4_wall_s …"`. That is
the D3b uniform rule applied to P2, and it is a **reporting-surface consequence,
not a moved number** — nothing in the frozen output existed for these keys to
have moved from. Key-iteration consumers: I searched `tools/`, both experiments,
`ledger/`, and the previous review directory for readers of `summary.json`. The
only consumers that iterate keys are (a) the acceptance's own leaf-diff
`accept/sumreg.py` — which is exactly why it reported them — and (b)
`v3_celldiff.py`, which iterates the `cells` block only (unchanged). No
production consumer in `tools/` reads these summaries. The Coordinator's "benign
and unverifiable from the JSON alone" is upheld on the first half and improved on
the second: it is verifiable, by reading the frozen code path and the consumer set.

**(4) Deletion-derived inputs — the control the Coordinator most wanted.**
`artifacts/r3/deletions.py` builds seven input tables from the frozen
`results.jsonl` by deleting (or, in two cases, injecting) rows, runs the
**repaired** and the **frozen** `summary.py` on each, and records per prediction
`holds`, `unevaluable`, `n_clauses/n_evaluated` (`artifacts/r3/deletions_out.json`,
per-case summaries under `artifacts/r3/deletions/`).

| case | what is made unevaluable | repaired `holds` | repaired `unevaluable` | frozen `holds` |
|---|---|---|---|---|
| P3: delete all `noncore_first` rows of n17l6/S | one P3 clause | **null** | `[n17l6/S/noncore_first_over_default_wall_censored]` (10/11 evaluated) | true |
| P3: delete all `core_order` rows | P3's first clause | **null** | `[core_order_identity]` | true |
| P4: delete all `gauss_elim` rows of n15l5/S | one P4 cell | **null** | `[n15l5/S]` (5/6) | true |
| P5: delete all cms `cnf_xor` rows of n15l5 | one P5 clause | **null** | `[n15l5/cms_xor_U_over_S_conflicts, + 3 Groebner]` (5/9) | true |
| P6: delete all null-object rows of n15l5 | one more P6 cell | **null** | `[n15l5, n19l6]` (1/3) | true |
| P6: inject one finished null row for n19l6 | none — P6 fully evaluable | **true** (3/3) | `[]` | true |
| P2+P5: inject 4 finished M2 rows for n15l5 with `engine_cpu_s` | P2 mixed 2/12, P5 7/9 | **null / null** | P2: 10 clauses; P5: `[n17l6/…, n19l6/…]` | **P2 true**, P5 true |

Every prediction with a nonempty `unevaluable` list reports `holds: null`; a
prediction whose last unevaluable clause is removed returns to a boolean; the
frozen code reports `true` throughout, including P2 `true` on 2 of 12 clauses in
the injection case — the silent-drop signature. **P3's aggregation specifically:
a None makes it null, not false.** The Coordinator predicted the executor would
fix the three named sites and leave P3 false-for-null; the executor fixed P3 (and
P4, P2) as well. Prior overturned in the executor's favour.

**(5) The four l=6 pure-CNF ratios**, recomputed by me from the rows
(`compare_out.json` block `e`), all-10 form / matched-subset form:

| cell | repaired summary | frozen summary | my all-10 | my matched-5 | reference (all-10 / matched) |
|---|---|---|---|---|---|
| n17l6/S | 10.39601237538673 | 83.50030889840438 | 10.39601237538673 | 26.070689655172412 | 10.396 / 26.071 ✔ |
| n17l6/U | 34.47183993452649 | 83.50030889840438 | 34.47183993452649 | 34.468128176414844 | 34.472 / 34.468 ✔ |
| n19l6/S | 67.46015180265655 | 83.50030889840438 | 67.46015180265655 | 327.66359447004606 | 67.460 / 327.664 ✔ |
| n19l6/U | 83.50030889840438 | 83.50030889840438 | 83.50030889840438 | 82.62897377519184 | 83.500 / 82.629 ✔ |

Four distinct values; the repaired code uses the all-10 form, as A6 states.

**Verdict R3: holds.** Both ADD1 questions answered with the Coordinator's prior
overturned on 156's origin and on P3's aggregation, and upheld on the twelve keys.

## 5. R4 — the environment probe, defect and repair, both measured

**(1) Controlled reproduction of the frozen probe.** `artifacts/r4/probe_repro.py`
launches a child that imports the **frozen** `bench` and calls `environment()`,
with the child's stdin an open pipe whose write end the launcher holds and never
writes — the inherited-stdin condition — under my own 120 s bound, snapshotting
the process tree at 5 s and 30 s (`artifacts/r4/probe_repro_frozen.json`):

- Wall **60.52 s**; child exit 0; `environment()` returned with
  `Singular: "unavailable: Command '['Singular', '--version']' timed out after 60 seconds"`,
  M2 1.22, cadical 1.7.3, cryptominisat 5.11.15, gcc 13.3.0 all present.
- Process tree at 5 s and 30 s, identical: `python3` (wchan `do_poll`) → **one**
  `Singular` (pid 189751, ppid = the python, `wchan pipe_read`, fd 0 = the pipe).
  No grandchild at any snapshot.

So the frozen probe **hangs for exactly its timeout and then returns**. It does
not hang indefinitely. The defect is real (a 60 s stall and a misreported
Singular) and it is bounded.

**(2) Is Singular a wrapper?** `/usr/bin/Singular` is an ELF x86-64 PIE, 18 584
bytes, dynamically linked against `libsingular-Singular-4.3.2.so` (`file`,
`strings`, `/proc/<pid>/maps`). Under `--version` with an unwritten pipe on stdin
(`artifacts/r4/singular_wrapper_check.json`): `exe = /usr/bin/Singular`,
`Threads 1`, `children_of_singular []`, `wchan pipe_read`, `VmRSS 8376 kB`. When I
then write `quit;` and close the pipe it exits 0 and its first stdout line is
`Singular for x86_64-Linux version 4.3.2 (4330, 64 bit) Apr  1 2024 04:44:00`.
**Single execve, no fork, no wrapper.** `Singular --version` prints its banner and
enters the interactive read loop instead of exiting; with stdin at EOF it exits.

**(3) Why the 60 s timeout "did not save" c9590f — ADD1-d.** Both the contract
(A5: "died inside it after ~4 minutes; the 60 s per-engine timeout … did not
fire") and the Coordinator's prior (descriptor-table property of the session)
are **overturned by the artifacts of c9590f itself**:

    launch_time.txt        2026-09-15T10:22:40Z   (file birth 10:22:40.072Z)
    bench_stderr.log       birth 10:22:40.072Z, last write 10:22:52.960Z
    bench_stdout.log       0 bytes, 10:22:40.072Z

The traceback — the last thing the interpreter writes — landed **12.9 s after
launch**. Its innermost frames are `subprocess.run(…, timeout=60)` →
`communicate(input, timeout=timeout)` → `_communicate` → `selector.select(timeout)`
→ `KeyboardInterrupt`. The timeout was armed (the selector was polling with a
deadline) and was interrupted by SIGINT at ~13 s, 47 s before it could fire.
Nothing "failed to time out"; nothing ran for four minutes. I found no artifact
or ledger record behind the "~4 minutes" figure (`rg` over `ledger/`, the
previous review directory and the c9590f directory: the only occurrence is
specification.yaml:451). The timestamps are original: this worktree is where
c9590f was launched, the files' birth times precede their commit (3c5a4f22,
20:46:55Z) by ten hours, and their ctimes equal their mtimes.

The pipe-drain hypothesis (kill direct child, then block draining a pipe a
grandchild holds) I also tested directly, because it is written into D4's fix
rationale and the repaired docstring: a frozen-style
`subprocess.run(capture_output=True, timeout=4)` against
`artifacts/r4/forking_engine2.sh` (child never exits; grandchild `sleep 300`
holds the stdout pipe) **returned at 4.006 s** with `TimeoutExpired`
(`artifacts/r4/frozen_probe_forking_out.json`). On Python 3.12.3
`/usr/lib/python3.12/subprocess.py:551–564`, the POSIX timeout path is
`process.kill(); process.wait(); raise` — it does not re-enter `communicate()`,
so a surviving grandchild cannot block it. The grandchild is leaked, not waited
on. The hypothesis is refuted on this interpreter.

**(4) Repaired probe under the identical launch**
(`artifacts/r4/probe_repro_repaired.json`): wall **0.50 s** for the whole
`environment()` (`took_s 0.046`), `Singular: "Singular for x86_64-Linux version
4.3.2 (4330, 64 bit) Apr  1 2024 04:44:00"`, per-engine seconds
`gcc 0.002, M2 0.032, Singular 0.008, cryptominisat5 0.002, cadical 0.002`.
The acceptance's `logs/probe_check.json` shows the same shape. C-PROBE and A5 met
with two orders of magnitude to spare.

**(5) Sufficient for a forking engine?** Tested against two synthetic forking
engines with the accepted `probe_version` (`artifacts/r4/forking_probe_out.json`,
bench sha `d835b1ea…` confirmed in the artifact):

- `forking_engine.sh` (prints a version line, forks `sleep 300` that holds stdout,
  then blocks on `read`): returned `forking-engine version 0.0` in **0.002 s** —
  `stdin=DEVNULL` gave the `read` EOF, output went to a temp file so the
  grandchild's hold blocks nothing. **But the grandchild survived** (pid 194496
  still running afterwards): `kill_group` runs only on the timeout path
  (bench.py:651–652); a child that exits normally leaves any forked descendant
  orphaned in its session. The docstring's "a forked grandchild cannot outlive
  the timeout" is true as written and narrower than it reads.
- `forking_engine2.sh` (never exits; grandchild `sleep 300`): returned
  `unavailable: no exit within 3s; process group killed` at 3.002 s, and the
  grandchild was killed with the group.

So: bounded return for forking and non-forking engines alike (the requirement A5
states); process hygiene only on the timeout path. For this host's engines,
inherited stdin was the whole story and DEVNULL alone would have been the whole
fix — exactly what the Coordinator said would change its mind.

**Verdict R4: holds.** Mechanism measured on both sides; the contract's account
of c9590f corrected.

## 6. Proves-too-much object 1 — the acceptance procedure on the unrepaired tree

Every criterion run against `experiments/EXP-ICPERF-66fd51/code/` (frozen
hashes verified §R5.1), from `/tmp` copies. Required: each **fails**, in its own
defect's way.

| criterion | frozen outcome | declared failure mode | as declared? |
|---|---|---|---|
| A1 direct M2 | exit 1, stdout empty, `syntax error at '='` at 49:7 after 164 CPU-s | parse error after the computation | **yes** |
| A1 through frozen harness | exit −6 (SIGABRT) at 11.2 s, `std::bad_alloc`, VmHWM 2.70 GiB, RLIMIT_AS 6 GiB on the live child; row `status infrastructure_exit_-6`, no gb_size | (D2 masks D1 — the contract's own account) | **yes**, and it shows why D1 was invisible in RUN-305ca3 |
| A4 (i) hog | exit 1 with `OSError [Errno 12]` at 5.9 GiB, no `rss_limit_breached` field | *(criterion undefined for the frozen row shape; fails)* | fails, by RLIMIT_AS |
| A4 (ii) reserver | exit 3, `mmap … FAILED at chunk 0: errno=12`, `Max address space 6442450944` | killed by RLIMIT_AS | **yes** |
| A5 probe | returns at **60.52 s** with Singular `unavailable: … timed out after 60 seconds` | "not returning" | **fails, but not as declared**: bounded at 60 s, Singular not a version string, 60.06 s > 60 s |
| A6 four l=6 ratios | all four `83.50030889840438` | the single repeated value | **yes** |
| A6 P5 Groebner clause | `P5.cells` has 6 entries, none Groebner; `holds: true` | no record of the skipped clause | **yes** |
| A6 P6 | `n19l6.holds null`, top-level `holds: true` | n19l6 dropped, true | **yes** |
| A6 156 / cells | frozen summary reproduces archived summary.json byte-for-byte; 156/156 against v3 | *(not a discriminator)* | **passes on frozen — by design** |

Two things to record. First, **A6's numeric-agreement clause passes on the
unrepaired tree**, necessarily: it is C-SUMREG's *control* ("reporting only,
moves no number"), designed to hold on both trees, and it does. It discriminates
nothing by itself and must not be counted as evidence *for* the repair; the
discriminating parts of A6 are the three reporting signatures, which all flip.
Second, **A5 discriminates but the plan mis-described the frozen failure**: the
unrepaired probe is bounded at 60 s per engine and returns; the criterion fails
on the Singular string and (barely) on the 60 s bound, not on "not returning".
The contract's A5 reference should be corrected in the composition.

No criterion that should fail passes. The acceptance is interpretable.

## 7. R5 — scope, custody and manifest completeness

**(1) Frozen hashes** vs TASK-20260913-f8bdec `path_sha256` (BATCH-51e2aa
dispatch_queue.json): bench.py `e8aad273…` ✔, binec.py `b6edbcf6…` ✔, convert.py
`16affe2c…` ✔, summary.py `eaf54bd7…` ✔ (`artifacts/r5/hash_table.json`).

**(2) `git status --porcelain experiments/EXP-ICPERF-66fd51`**: empty, at the
start and end of my session (`artifacts/r5/git_status_porcelain_66fd51.txt`, 0
bytes). Both archived `summary.json` files unchanged (RUN-305ca3's hash
`0c36e5e2…` equals my scratch reproduction). C-NOWRITE holds; the Coordinator's
one stated suspicion for this joint did not materialise.

**(3) My own diff and hunk attribution** (`artifacts/r5/diff_*.patch`, taken
against the accepted bytes — applying my bench.py patch to the frozen file yields
`d835b1ea…`, confirmed): convert.py 1 hunk (D1), summary.py 5 hunks (D3),
bench.py 13 hunks, binec.py 0. Total 19, matching CODE_SHA256.json. Every hunk
contains only lines I can assign to D1–D5; **none is attributable to no defect**.
But five bench.py hunks (#1 header/docstring, #2 constants, #3 Runner docstring
and setup, #8 the row-finishing block, #12 `probe_version`/`environment`) carry
lines from two or three defects each — D2+D4+D5 in the constants block, D2+D5 in
the row finisher, D2+D4 where the watchdog's `kill_group` is reused by the probe.
C-BYTE's pass condition reads "every diff hunk attributable to **exactly one** of
D1–D5". At hunk granularity that is **not met** for 5 of 19; at line granularity
it is met for every line. My call, since the plan makes it mine: the contract's
purpose — no undeclared change — is satisfied and the scope violation the
stopping rule guards against did not occur; the literal wording is not satisfied,
and the composition should say which reading it adopts rather than let the
producer's "0 unattributable" stand for "exactly one". A shared-constants block
cannot be made single-defect without splitting one file edit into artificial
hunks, so I would adopt the line reading and record the deviation.

**(4) CODE_SHA256.json** (`experiments/EXP-ICPERF-e21835/code/`, sha
`825ed6d0…`): every `frozen_sha256` and `repaired_sha256` matches the file it
names **at commit 2bfdc65b / 5fa8ffed8**; binec.py byte-identical ✔. Against the
current worktree, bench.py does **not** match (`2eee0153…`): that is D6
(CORR-20260916-d51133) and is expected, not an integrity failure of the run.
Also recorded: CODE_SHA256.json says `diff_hunks` per file but the same five
mixed hunks appear under two or three defect ids in `hunks_per_defect` — the
file discloses the mixing; it does not resolve the C-BYTE reading.

**(5) HEAD advanced during the run — invariance verified.** Code-file hashes at
every commit I could reach: `ecdd3bffd`, `6ad48e04c`, `2bfdc65b` (HEAD at the M2
row and the probe), `5fa8ffed8` — all four files identical at all four
(`hash_table.json`). At `e1728d8a8` and HEAD, bench.py differs (D6). The M2 row
ran on the accepted bytes.

**(6) Manifest completeness against AGENTS.md "Artifact policy"**, read from
`manifest.yaml` (epoch 1, Coordinator-authored), `manifest-epoch2.yaml`
(executor) and `manifest_v2.yaml` (Coordinator, 07:17, supersedes by reference):

| field | present | where / note |
|---|---|---|
| exact command | epoch 2: yes; epoch 1: **not recorded by the producer** | `manifest_v2.yaml` argues the three drivers are argument-free, so committed bytes determine the command; `command.txt` lists them. Honest, and a reconstruction, not a record. |
| git commit + dirty state | yes | epoch 1 `1fc65075`, epoch 2 `2bfdc65b`, `dirty_tree: true` with reason |
| environment / versions | yes | `environment.json`, `environment-epoch2.json` (probe repaired, Singular named) |
| seeds | n/a, stated | contract: deterministic engines; null objects record their schedule |
| requested policy / resolved model / effort / fallback | yes | epoch 1 `claude-opus-5-thinking`, quota; epoch 2 fallback true with reason and the `inference_amendment` |
| stdout/stderr per invocation | yes | `logs/*.out|err`; top-level `stdout.log`/`stderr.log` are companions that say they are not captured streams |
| raw results | yes | `results.jsonl`, `results_engine.jsonl`, `watchdog_control/outcomes.json`, `summary_regression.json` |
| validity status + reason | epoch 1 `valid: null` with reason; epoch 2 states per-criterion outcomes | |
| timestamps, resources | yes | per row: wall, cpu, peak_rss_kb, polls, loadavg |
| `rss_limit_gb`, `rss_poll_interval_s` | yes, on every row | direction (i) records `rss_limit_gb 2`, `declared_limit_gb 8`, `scaling_reason` — the deviation is on the row itself |

Nothing required is missing. One defect I confirm and one I add:
CORR-20260916-b35a05 (epoch-1 `hypothesis_id: H-ICPERF-2c57cc` where the
contract says null) is correctly described. Added: **epoch 1's recorded commit
`1fc65075` does not contain the code tree** — `experiments/EXP-ICPERF-e21835/`
at that commit holds only `specification.yaml`; the four code files were first
committed at `ecdd3bffd`, after epoch 1 ran. A reader checking out epoch 1's
`git_commit` does not get the bytes that produced A4/A5/A6; only the per-file
sha256 in `manifest.yaml` (which match `ecdd3bffd`) pin them. CORR-d51133's
"`code.commit` is what made this recoverable" is true for epoch 2 and false for
epoch 1. Minor: CORR-d51133 says "49.2 s wall against a 2.0 s poll interval";
the accepted interval is 0.25 s (197 polls).

**(7) Custody during the review window — ADD1-e and beyond it.** ADD1-e's four
questions, then what I observed happening while I held the claim.

*(1) Does the Coordinator-authored manifest assert anything the artifacts do
not carry?* I checked every per-criterion verdict in `manifest.yaml` against
the raw artifact it names: A4 against `outcomes.json` (direction (i) at 2 GiB,
(ii) at 8 GiB — both as the manifest states), A5 against `probe_check.json`, A6
against `summary_regression.json`; A1–A3/A7 `NOT_EVALUABLE` because no M2 row
existed at epoch 1 — true (`results_engine.jsonl` is an epoch-2 file, absent at
`ecdd3bffd`). I found no assertion beyond the artifacts. The authorship
objection stands as the Coordinator itself framed it: the party that dispatched
the work wrote the producer's record. Defensible given the alternative (durable
artifacts vs. none) and correctly labelled; still a custody compromise, and the
label `PASS_WITH_DECLARED_DEVIATION` is **not** in the contract's vocabulary
(`metrics.primary`: PASS / FAIL / NOT_EVALUABLE). Under that vocabulary A4 at
epoch 1 is, strictly, NOT_EVALUABLE on direction (i) at the declared magnitude
and PASS on direction (ii); the manifest's label is more informative and less
disciplined, exactly as the Coordinator anticipated. I would keep the label in
prose and record the contract-vocabulary verdict beside it.

*(2) Did epoch 2 modify anything committed at `ecdd3bffd`?* `git diff --name-status
ecdd3bffd 5fa8ffed8 -- experiments/EXP-ICPERF-e21835/` shows **additions only**
(52 files, 0 modifications, 0 deletions); the four code files, `manifest.yaml`,
`results.jsonl`, `outcomes.json`, `probe_check.json`, `summary_regression.json`,
`environment.json` are hash-identical at both commits. **Epoch 2 modified nothing.**

*(3) Supersession by reference?* `manifest-epoch2.yaml` names `manifest.yaml`,
pins its sha `8a4f1c0c…`, and adds; both remain readable. `manifest_v2.yaml` does
the same for both. Yes.

*(4) Is the recorded interruption cause the real one?* Not verifiable from
artifacts: the run directory carries nothing that distinguishes a quota stop
from a host timeout (last artifact write 22:44Z, discovery 05:55Z). The manifest
says so, records the wrong first inference, and states why the distinction
matters (different remedies). That is honest, not tidy. I can add only that the
epoch-2 `inference_amendment` and fallback are consistent with a quota cause.

*Beyond ADD1-e — what moved while the review was in flight.* My task was
claimed at `a6eef3eab`. After that, in this branch's history:

- **`3dc30bfcf` (07:02:52Z, a concurrent session) edited the committed, archived
  `manifest.yaml` in place** (+17 lines: `code.commit`, `code.command`), moving
  its hash to `23327c0f…` — a binding field of the completed archive
  TASK-20260915-7da7f1. The values added were accurate; the mechanism broke an
  archive. The merge `a8c9c32f6` (07:25:25Z) restored the bytes to `8a4f1c0c…`
  and records why. Net effect on the tree: none; on the record: a committed run
  manifest was mutable for 23 minutes during its own review.
- **`e1728d8a8` (07:09:13Z) changed `bench.py`** — the instrument under
  certification — after the run and during the review (D6, CORR-d51133). I
  verified my copy under test is the accepted `d835b1ea…`, and I did not review
  the D6 bytes. CORR-d51133's guidance to reviewers is correct; I add that the
  guidance arrived at 07:3x, after my measurements had been taken against a copy
  I had already hashed — the copy protected me, not the record.
- Six files were **added** to the run directory after the 7da7f1 snapshot
  (`command.txt`, `stdout.log`, `stderr.log`, `raw-result.json`,
  `manifest_v2.yaml`, `accept/compose_companions.py`), by two sessions in
  conflict, resolved by a third version at the merge. All are additive
  companions; the measurement artifacts are untouched (hash table). But the run
  directory a reviewer was told is "committed and immutable" gained six files and
  a rewritten-then-restored manifest while the review ran.

None of this changes a measurement. All of it is what R5 exists to notice, and the
Coordinator's expectation that this joint would be "the least informative" is not
borne out.

**Verdict R5: breaks**, narrowly and specifically — on C-BYTE's literal
one-defect-per-hunk clause (5/19 mixed) and on the tree-holds-still premise
(manifest edited in place and restored; instrument changed post-run). The
measurement package, the frozen tree, the two archived run packages, the code
hashes at the certifying commit, and the manifest's factual content all check.
The composition can treat the C-BYTE clause as satisfied at line granularity
with a recorded deviation; it cannot treat the custody window as clean.

## 8. Things I could not verify, and what each costs

- **R6's independent basis.** Blind by construction; R1 step (5)'s second half
  is open. Cost: R1's agreement is between two repairs of one converter and two
  engines reading that converter's output, as the plan says.
- **The interruption cause of epoch 1.** No artifact distinguishes quota from
  timeout. Cost: none to any measurement; the remedy chosen (re-dispatch on a
  different binding) was the right one for either cause.
- **M2 series load.** `m2_series.json` and `m2_sigterm.json` did not record
  loadavg (field null). Cost: the 1.40 GiB/0.25 s burst is a lower bound on a
  quiet host's; the overshoot arithmetic is if anything optimistic.
- **Behaviour above 8 GiB with a SIGTERM-ignoring child.** Computed (12.5 GiB),
  not measured; measuring it risks the guest. Cost: the number is arithmetic on
  observed growth, not an observation.
- **The "~4 minutes" in the contract.** I could not find its source; I can only
  show the artifacts say 12.9 s.

## 9. Disagreements, stated plainly

With the **contract**: (a) A5's reference account of c9590f is wrong on two
facts — it died at 12.9 s, not ~4 min, and the timeout was interrupted, not
inoperative; (b) A6/C-SUMREG's "156" is defined by a file other than the one the
contract cites; (c) D4's pipe-drain rationale does not describe Python 3.12's
`subprocess.run`; (d) C-BYTE's "exactly one defect per hunk" is not achievable
for a shared-constants block and should say "every line" or accept mixed hunks
explicitly.

With the **Coordinator's priors**: R3 — 156 is reconstructible (prior: authoring
slip); P3 aggregates None→null (prior: executor leaves false-for-null). R4 — the
c9590f difference is the interrupt time, not the descriptor table; the
pipe-drain mechanism does not exist on this interpreter. R5 — not the least
informative joint. R2 — the plan's "does not double count shared pages" is false
for COW after fork (conservative direction). Upheld: R1 regex worry (tested, not
borne out — as the Coordinator half-expected), ADD1-a (poll interval is the
residual risk; now 1.40 GiB), ADD1-c (benign), ADD1-e (manifest accurate,
authorship objectionable, `PASS_WITH_DECLARED_DEVIATION` outside the vocabulary).

With the **executor**: (a) the repaired `probe_version` docstring claims process-
group hygiene that exists only on the timeout path; (b) `peak_rss_kb` and
`max_rss_kb_children_highwater` are both presented as per-row peaks and neither
is one for a child under 0.25 s — the row should say so or the field should be
sampled at exit; (c) `wall_s` at the accepted commit is a poll-boundary
quantity for fast children — disclosed by epoch 2 as an anomaly, but an anomaly
that would have zeroed the wall-ratio predictions of the row contract if run on
the accepted bytes, and no acceptance criterion could see it.

With **CORR-20260916-d51133**: `code.commit` recovers epoch 2's bytes, not epoch
1's; the poll interval is 0.25 s, not 2.0 s.

## 10. Citations and provenance (AGENTS.md rule 9)

All `internal`, read by this session: the files named above under
`experiments/EXP-ICPERF-e21835/`, `experiments/EXP-ICPERF-66fd51/` (read-only),
`coordination/review/icperf-20260915-a33cda/{review-plan.yaml,
review-plan-addendum-1.yaml}`, `coordination/review/icperf-20260913-66fd51/TASK-20260913-6c5729/`
(report, `work/`, `artifacts/`), `ledger/corrections/CORR-20260916-b35a05.yaml`,
`CORR-20260915-654160.yaml`, `CORR-20260916-d51133.yaml`, the BATCH-a33cda and
BATCH-51e2aa dispatch queues, `/usr/lib/python3.12/subprocess.py`. External
facts (`file`, `strings`, `/proc`) observed directly on this host. No recalled
citation is relied on.
