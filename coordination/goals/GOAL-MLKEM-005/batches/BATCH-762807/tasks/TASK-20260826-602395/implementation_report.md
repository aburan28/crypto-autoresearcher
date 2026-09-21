# Implementation report — TASK-20260826-602395

**Goal** GOAL-MLKEM-005 · **Batch** BATCH-762807 · **Question** RQ-MLKEM-001
**Opening decision** DEC-20260824-5e222e · **Role** executor
**Claim ceiling** `instrument_repair` · **Claim tier** `toy`

This report records observations. It interprets nothing, moves no hypothesis,
writes no ledger record, and commits nothing.

---

## 0. The one-line result

`rt_ctrl_1_matched_pair_v2.py` was written as a new file; six acceptance tests
were run against it; the board is

| defect | status | evidence |
| --- | --- | --- |
| D1 STARTED stub | **PASS** | `evidence/D1_D2_sigterm_surrogate.json` |
| D2 SIGTERM flush | **PASS** | `evidence/D1_D2_sigterm_surrogate.json` |
| D3 per-tour progress | **PASS** | `evidence/D3_D4_tiny_cell.json` |
| D4 resource record | **PASS** | `evidence/D3_D4_tiny_cell.json`, `evidence/D3_D4_environment.json` |
| D5 tour count | **PASS** | `evidence/D5_tour_count.json` |
| D6 root-Hermite factor | **PASS** | `evidence/D6_root_hermite.json` |

**A passing board is not a result.** It says the instrument now records what it
always should have recorded. It says nothing about ML-KEM at any FIPS 203
parameter set, about lattice hardness, or about the obstruction RT-CTRL-1
targets. Section 8 states what the surrogates cannot show, including a residual
loss window that survives every one of these PASSes.

---

## 1. Scope compliance, stated first

* **NO d=512 REDUCTION OF ANY KIND WAS RUN, at any precision, under any label.**
* **NO mpfr_bits=100 CELL WAS RUN**, on a d=512 basis or otherwise.
* **NO 75-bit cell was re-run as a research measurement.**
* Every lattice touched by this task is **d=64, beta=20, mpfr_bits=53**
  (plus one d=32, beta=10 probe of the defect itself, §5.2). Total lattice
  compute across the whole task: **under 8 seconds of CPU**.
* The pinned predecessor
  `.../BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair.py`
  was **read and never edited**. Its sha256 was verified
  `bc0524ee432a2327bc4a5cfff5d8f5d79b590d37b2f38ea428c78af5abb25035`
  before work began **and again after all work finished** — unchanged both
  times. The precedent
  `.../BATCH-0d5018/tasks/TASK-20260815-f14d3c/stage0_d512_beta5570_precision_bisection_and_reattempt.py`
  was likewise verified at
  `58a1fdc21f45730789feeff69c6a6fd7c24bf4938be15d6e878afd246d0de485`
  and read only.
* Nothing was written outside
  `coordination/goals/GOAL-MLKEM-005/batches/BATCH-762807/tasks/TASK-20260826-602395/`.
  Nothing was committed, pushed, merged or staged. `git status --porcelain`
  after the work shows exactly the seven untracked paths of this task
  directory and nothing else.
* The v2 instrument carries a **mechanical scale guard**: `run` refuses any
  `d > --max-toy-d` (default 128) unless `--scale-run-authorisation` is given
  with a non-empty reason, which is then recorded in `environment.json`. This
  was not exercised as an acceptance test (it is a refusal, not a repaired
  defect) and is disclosed here as an addition beyond D1..D6.

---

## 2. Interpreter, environment, exact commands

**Interpreter used for everything:**

```
/tmp/claude-0/-home-user-crypto-autoresearcher/15de1654-2503-5954-afd1-67e6db6674e9/scratchpad/sagevenv/bin/python
```

Verified **by content, not by path**, before use (the predecessor's whole
failure mode was an environment difference recorded by path):

| | |
| --- | --- |
| Python | 3.11.15 |
| fpylll | 0.6.4 (`.../sagevenv/lib/python3.11/site-packages/fpylll/`) |
| numpy | 2.4.6 |
| psutil | 7.2.2 |
| host | 4 cores, 15 GiB |
| git commit at run time | `9ca07b52816ff0c960aee074fc5ea7ad43aa4ae2`, tree clean apart from this task's own new files |

**The system `python3` has neither fpylll nor psutil.** Nothing was installed
and no venv was created by this task; the venv above pre-existed and was
supplied by the dispatching session (obtained per KN-TECH-14efa5, passagemath
route; KN-TECH-797223 records that recipe's container dependence).

**Commands run** (all from the task directory):

```sh
# verification of the two pinned sha256 values, before and after
sha256sum .../BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair.py
sha256sum .../BATCH-0d5018/tasks/TASK-20260815-f14d3c/stage0_d512_beta5570_precision_bisection_and_reattempt.py

# two development smoke runs of the instrument, into the scratchpad (NOT into
# the task directory, and NOT part of the evidence) -- disclosed in §9
<venv>/bin/python rt_ctrl_1_matched_pair_v2.py run --out-dir <scratch>/smoke \
    --prefix smoke --d 64 --beta 20 --mpfr-bits 53 --roles smoke
<venv>/bin/python rt_ctrl_1_matched_pair_v2.py run --out-dir <scratch>/kt \
    --prefix kt --d 64 --beta 20 --mpfr-bits 53,53,53,53,53,53 \
    --heartbeat-seconds 0.25          # SIGTERM'd at 2.0 s from the shell

# THE ACCEPTANCE SUITE -- the one command that produced every declared artifact
<venv>/bin/python acceptance_tests.py \
    > acceptance_stdout.log 2> acceptance_stderr.log
```

The acceptance suite ran **once**, exit code 0, wall clock **6.457 s**
(`real 0m6.457s`, `user 0m6.016s`, `sys 0m0.461s`). Inside it, the two D1/D2
surrogates were launched as **real subprocesses** with these exact argv:

```sh
<venv>/bin/python rt_ctrl_1_matched_pair_v2.py run \
  --out-dir artifacts/D1_D2_surrogate_S1_sigterm_failed_infrastructure \
  --prefix surrogate --d 64 --beta 20 --mpfr-bits 53,53,53,53,53,53 \
  --heartbeat-seconds 0.25                       # SIGTERM at t=2.0 s

<venv>/bin/python rt_ctrl_1_matched_pair_v2.py run \
  --out-dir artifacts/D1_D2_surrogate_S2_timeout_failed_infrastructure \
  --prefix surrogate --d 64 --beta 20 --mpfr-bits 53 \
  --heartbeat-seconds 0.25 --simulate-slow-tour-seconds 0.4 \
  --cell-timeout-seconds 1.5                     # self-timeout via SIGALRM
```

`acceptance_stderr.log` is **0 bytes**. It is **empty, not omitted**: the suite
produced no stderr output. `acceptance_stdout.log` is 7258 bytes and contains
every assertion line verbatim.

---

## 3. D1 and D2 — the STARTED stub and the signal flush

### 3.1 What was asserted and what was observed

**Surrogate kind, declared:** S1 is a **TINY LATTICE, with no sleep stub
anywhere** — six d=64/beta=20/mpfr=53 cells back to back, SIGTERM delivered
2.0 s in, so the signal lands in the middle of real fplll work rather than in a
Python `sleep`. S2 is a **declared sleep surrogate** — one d=64 cell with an
explicit 0.4 s inter-tour sleep so the instrument's own 1.5 s cell timeout
trips deterministically; every record it writes carries `surrogate: true` with
the kind. Both are routed through `rt_ctrl_1_matched_pair_v2.py` **launched as
a subprocess**; the suite re-implements no part of the stub, the handler or the
flush.

S1, observed (`evidence/D1_D2_sigterm_surrogate.json` → `S1_real_sigterm`):

| observation | value |
| --- | --- |
| return code | **143** = 128 + SIGTERM |
| total elapsed | 2.017 s |
| STARTED stubs on disk | 2 |
| `cell_final` records | 1 |
| **cells that started and never finished** | **1** |
| `KILLED_PARTIAL` records | **1** |
| `tour_start` records | 11 |
| `tour_progress` records | 10 |
| **kill landed inside a tour** | **true** (11 starts vs 10 completions) |
| unparseable journal lines | **0** |

The flushed `KILLED_PARTIAL` record carries `tours: 1`,
`tour_in_flight_index: 1`, `elapsed_seconds_at_refresh: 0.394274`,
`signal: "SIGTERM"`, `failed_infrastructure: true`, and a 15-line
`stdout_tail`.

S2, observed (`S2_instrument_cell_timeout`): return code **142** = 128 +
SIGALRM, 1.925 s, 1 STARTED stub, 3 completed tours, **1
`TIMED_OUT_PARTIAL`** record with `signal: "SIGALRM (cell timeout)"`,
`surrogate: true`, and a 6-line `stdout_tail`. This is the clause of
DEC-20260815-3e8e9c(i) that names `stdout_tail` **for a timed-out cell**,
discharged on a cell that genuinely timed out.

This is the record BATCH-f9780d's 100-bit cell did not leave.

### 3.2 The signal-safety mechanism, and its limits

**Mechanism.** The results journal is a JSON-Lines file opened **once** with
`os.open(..., O_WRONLY|O_CREAT|O_APPEND)`; the fd lives in a module-level int.
A **complete** partial record is pre-serialised to `bytes` — one per signal, so
the flushed status is the true one (`KILLED_PARTIAL` for SIGTERM/SIGINT,
`TIMED_OUT_PARTIAL` for SIGALRM) with no work in the handler — and the dict of
payloads is rebuilt and **rebound wholesale** on each refresh. Rebinding a
module-level name is atomic in CPython, so the handler reads either the old
dict or the new one, never a half-updated one. The handler does exactly:
one `os.write(fd, payload)`, one `os.fsync`, one `os.write(1, short_notice)`,
then `os._exit(128+signum)`. It **allocates nothing, opens nothing, imports
nothing, calls no json function, and touches no buffered Python stream**.
`os._exit` is deliberate: no `atexit` hook and no buffered-stream flush runs
from signal context, since a flush could deadlock if the signal landed inside a
buffered write.

**Limits, claimed no higher than the mechanism supports.**

1. **If the signal arrives mid-write.** With `O_APPEND` and a **single**
   `write()` syscall per record, the kernel appends the record whole after
   whatever bytes are already there; it cannot interleave with a partially
   written earlier line. A Python-level signal is not delivered inside the
   syscall — CPython defers to the next interpreter check — so the in-flight
   `os.write` completes first. **Observed consistently with this:** 0
   unparseable lines in both surrogate journals, and v2's own
   `rebuild-results` path re-parsed the post-kill S1 journal into an aggregate
   carrying both `STARTED` and `KILLED_PARTIAL`. `rebuild_results` nevertheless
   **retains** any unparseable line verbatim under `unparseable_lines` rather
   than dropping it, because a reader must not assume the guarantee.
2. **If the signal arrives inside an fplll C call.** CPython runs a Python
   signal handler only at an interpreter check **in the main thread**, so the
   handler does **not** run until the C call returns. At d=64 a tour is
   milliseconds and the handler fired essentially immediately — S1's kill
   landed inside tour 1 and the record was flushed. **At d=512 a single tour
   may be hours**, and there the flush is deferred for the rest of that tour. A
   SIGKILL following the SIGTERM, or a hard container stop, loses it entirely.
   SIGKILL runs nothing at all, by construction.
3. **Therefore the residual loss window is the progress made inside the
   currently running tour.** What survives regardless, because it is already on
   disk and fsync'd: the STARTED stub, every completed tour's row, every
   heartbeat, and a `tour_start` record naming **which** tour was in flight and
   **when it began** — so even a SIGKILL at d=512 yields "tour *k* began at
   *t* and had not finished by *t+Δ*", which is a lower bound on that tour's
   cost rather than the single bit "> N s".
4. **The aggregate `*_results.json` view is not signal-safe** and is never
   written from signal context. After a kill it holds the last safe-point
   state. This is directly visible in the artifacts: S1's directory contains
   `surrogate_results.json` (written after cell 1 completed, so it does **not**
   contain the kill), while **S2's directory contains no `surrogate_results.json`
   at all**, because its only cell never completed. The **journal** is the
   durable primary; `rebuild-results` regenerates the view from it.
5. **Staleness.** Elapsed time, cpu time and peak RSS in a flushed record are
   as of the last refresh. Between tours that bound is `heartbeat_seconds`.
   **Inside a tour it is not** — see §4.2. The record therefore reports
   `staleness_bound_seconds_between_tours` and leaves `staleness_bound_seconds`
   **null**, rather than stating a number the mechanism does not support.
   `tour_in_flight_index` and `tour_in_flight_started_wall_utc` are **not**
   stale: they are refreshed immediately before the tour is entered.

---

## 4. D3 and D4 — per-tour progress and the resource record

### 4.1 Observed on the tiny cell

d=64, beta=20, mpfr_bits=53, seed 1299689790, strategies sha256
`f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18`
(the content-bound copy archived in BATCH-f9780d, referenced read-only).

| observation | value |
| --- | --- |
| `tour_progress` rows in the journal | **9** (> 1) |
| rows in the final record's `tours_table` | 9 |
| tour indices | 0..8, consecutive |
| per-tour progress on stdout | 9 lines |
| unparseable journal lines | 0 |
| `cpu_times()` (psutil handle) | `{user: 1.56, system: 0.09, children_user: 0.0, children_system: 0.0}` |
| peak RSS (polled `memory_info().rss`) | **81.938 MB** |
| `resource.getrusage().ru_maxrss` cross-check | 81.645 MB |
| `stdout_tail` | 10 lines, non-empty |
| load average in `environment.json` | `[0.04931640625, 0.0830078125, 0.11962890625]` from `os.getloadavg()` |
| cell elapsed / cpu | 0.951381 s / 0.949806 s |
| pre-loop LLL / BKZ loop | 0.000378 s / 0.742096 s |

Each tour row carries: `tour_index`, `wall_utc`, elapsed since cell start, that
tour's own elapsed, cpu seconds, `clean`, `gso_r00`, `b0_norm_from_gso`,
`gso_log_det_0_d`, `delta_0_from_gso_logdet`, `root_hermite_factor`,
`root_hermite_factor_legacy_defective_formula`, `peak_rss_bytes` and
`cpu_times`. That is the tours-per-hour cost curve DEC-20260815-3e8e9c(i) named
as "exactly the quantity a Stage-1 sizing decision needs and does not have" —
present here per tour, flushed per tour, and therefore present in a killed
cell.

Two honest notes on the numbers:

* `cpu_times().user = 1.56 s` exceeds the cell's 0.95 s elapsed because
  `cpu_times()` is **process-wide**: it includes the acceptance suite's own
  imports and the D6 arithmetic test that ran before the cell. It is a
  process-level figure, not a per-cell one, and is recorded as such.
* The two RSS figures disagree slightly (81.938 vs 81.645 MB) because one is a
  polled sample of current RSS and the other is the kernel's high-water mark
  for the whole process. Both are recorded; they are **not** reconciled.

### 4.2 A measured finding: the resource sampler is starved by the GIL

`DEC-20260815-3e8e9c(i)` speaks of "the psutil handle **the polling loop
already holds**". **The pinned predecessor has no polling loop at all** — 119
lines, no psutil import. This task therefore **built** that loop; it did not
extend one. Stated because the wording could otherwise be read as implying an
existing mechanism was reused.

The loop is a Python thread, and **fplll's C calls hold the GIL**, so heartbeat
samples cannot arrive while a tour is running. Measured on the tiny cell rather
than asserted: with `heartbeat_seconds = 0.05` over a 0.951 s cell,
**9 samples were observed against 19 expected** if the thread were never
starved — a shortfall of ~53%, concentrated in exactly the intervals when a
tour is running. The instrument records `sampler_samples_observed` and
`sampler_samples_expected_if_never_starved` in every final record so the
shortfall is visible without re-deriving it.

**Consequence at scale, named here rather than left to review:** at d=512 a
signal-flushed record's peak RSS and cpu time can be **a whole tour stale**.
The mitigation implemented is the pre-tour refresh (§3.2 limit 5); the residual
is that intra-tour RSS growth is invisible to the flushed record. A run that
needs intra-tour resource resolution would need sampling from a **separate
process**, which this instrument does not do.

---

## 5. D5 — the tour count

### 5.1 The definition used, and why it is the number of tours

```
tours = the number of completed iterations of the transcribed upstream
        BKZReduction.__call__ while-loop, i.e. the number of
        bkz.tour(par, 0, -1, tracer) calls that returned.
```

That set is **exactly** the set of `("tour", i)` tracer contexts upstream
opens, because upstream opens one such context around each `self.tour(...)`
call and around nothing else. `getattr(bkz, "tours", None)` is never used.
Mechanism recorded machine-readably as `tours_mechanism:
"driving_loop_counter"` with the definition text in `tours_definition`.

### 5.2 A finding against the wording of the authorising decision

DEC-20260824-5e222e prescribes taking `tours` from `bkz.trace`. **Taken
naively that reproduces the defect it repairs**, and this task probed it live
rather than reasoning about it. Under the predecessor's exact calling
convention `bkz(par)` (d=32, beta=10, default tracer):

```
getattr(bkz,'tours',None)  -> None
hasattr(bkz,'tours')       -> False
hasattr(bkz,'trace')       -> True
bkz.trace is None          -> True
```

The reason is in the installed source:
`BKZReduction.__call__(self, params, min_row=0, max_row=-1, tracer=False)`
defaults `tracer` to **False**, and ends `try: self.trace = tracer.trace /
except AttributeError: self.trace = None`. So `bkz.trace` **exists and is
None** — an always-None read, exactly like the attribute it replaces.
Upstream's own docstring states it.

`bkz.trace` with `tracer=True` **does** give a real count, and this task uses
precisely that as its control (§5.3). But it is not usable as the instrument's
own mechanism, for a second and independent reason: **the trace exists only
after the whole call returns**, which is the case a killed cell never reaches.
Driving the loop is what makes D1, D2, D3 and D5 satisfiable at once.

This is recorded as a finding against the decision's wording. Reporting it is
not a deviation from the decision's substance — the substance is "stop reading
an attribute that is always None", and this satisfies it.

### 5.3 The equivalence control

The concern the control answers: driving the tour loop by hand could silently
change the algorithm. The loop in v2 is a line-for-line transcription of
upstream's, **retaining the pre-loop LLL and all four break tests in order**,
with only a flush added inside it.

Control: an **identically seeded, identically constructed** d=64 basis is run
through **upstream `BKZReduction.__call__`** with `tracer=True`, and its tour
count is taken as `sum(1 for child in bkz.trace.children if label == "tour")`
— the committed precedent's own method.

| | upstream `__call__` | v2 driving loop |
| --- | --- | --- |
| tour count | **9** | **9** |
| final b0 norm | **140.93615575855614** | **140.93615575855614** |

Match on both, the b0 values **bit-identical**. Trace child labels observed:
`['lll', 'tour' × 9]` — one `lll` context and nine `tour` contexts, confirming
the label predicate selects tours and nothing else.

**Two caveats on this control, stated rather than left for a reviewer.**

* **It is d=64 only.** It establishes that the loop is a faithful
  transcription at this dimension. It establishes **nothing** about d=512
  behaviour.
* **It does not reproduce the tour count quoted in the dispatch addendum.**
  The addendum recorded 26 tours and final b0 134.3540 at d=64/beta=20. This
  task measures **9 tours and b0 140.936** — because the construction differs:
  the addendum's probe used `BKZReduction(A)` on a bare matrix (fpylll's own
  `GSO.ROW_EXPO` double GSO, no strategies file), whereas this instrument
  carries the **pinned** construction forward (outer `LLL.reduction`,
  `FPLLL.set_precision` before GSO, `float_type="mpfr"`, explicitly no
  `ROW_EXPO`, content-bound strategies). **The addendum's exact numbers are not
  reproducible from the information recorded** — neither its seed nor its
  matrix construction is stated — so this task did not attempt to reproduce
  them and does not report having done so. What it shipped instead is the same
  equivalence check on the **pinned** construction with the seed recorded
  (1299689790), which is auditable end to end. If the difference matters to a
  reviewer, it is a difference of construction, not of tour counting: both
  sides of the table above use the same construction as each other.

---

## 6. D6 — the root-Hermite factor

Corrected: `(b0 / q**0.5) ** (1/d)`. The predecessor's line 78,
`b0**(1/d) / (q**0.5)**(1/1)`, is retained **only** under the key
`root_hermite_factor_legacy_defective_formula` and is never the reported
quantity.

**Closed form, derived and asserted rather than quoted:**

```
corrected / defective = (b0/q^(1/2))^(1/d) / ( b0^(1/d) / q^(1/2) )
                      = q^(-1/(2d)) · q^(1/2)
                      = q^(1/2 - 1/(2d))          -- independent of b0
```

Recomputed values (`evidence/D6_root_hermite.json`):

| quantity | recomputed here | committed figure |
| --- | --- | --- |
| distortion at (q=3329, d=512) | **57.24230824954366** | 57.242 |
| distortion at (q=3329, d=80) | **54.8456813814762** | 54.8457 |
| b0-independence, max relative deviation over b0 ∈ {1e2, 1e3, 5e3, 2.5e4, 1e6, 1.234e9} and d ∈ {64, 80, 128, 512} | ≤ **4.44e-16** | — |

**Consistency of the committed d=80 triple, recomputed from the committed
numbers themselves:** the Validator's M-6 records runner formula
`0.018481105` and standard `delta_0 = 1.0136088`. Their ratio recomputed here
is **54.84568157585816**, against the closed form **54.8456813814762** —
relative deviation **3.5e-9**, i.e. consistent to the precision at which those
two numbers were committed. This is a recomputation of the committed pair's
internal consistency; the committed numbers came from a d=80 basis this task
did not run and cannot reproduce byte-for-byte, and that limit is stated in the
evidence file too.

**Real-basis cross-check, free from the tiny cell** (d=64, a genuinely reduced
basis, this task's own seed):

| | |
| --- | --- |
| b0 | 140.93615575855614 |
| corrected root-Hermite | **1.01405240364132** |
| predecessor's defective formula | **0.01872498928065514** |
| measured ratio | **54.15503253125713** |
| closed form q^(1/2 − 1/128) | **54.15503253125713** — identical |

The corrected q-ary value also agrees with the GSO-log-determinant definition
computed independently on the same basis: `delta_0_from_gso_logdet =
1.0140524036413219` vs `1.01405240364132`, agreeing to ~1e-15.

### 6.1 An incidental observation about the cited precedent's GSO formula

Recorded because it was measured, not because it was sought, and **it does not
change D6's verdict**. The precedent TASK-20260815-f14d3c computes

```python
det_l_pow_1_over_d = np.exp(float(log_det) / d)
delta_0 = (first_vec_norm / det_l_pow_1_over_d) ** (1.0 / d)
```

In the installed fpylll 0.6.4, `M.get_log_det(0, d)` returns the log
determinant of the **Gram** matrix, i.e. `2·log vol`. Measured on this
construction at d=64:

```
get_log_det(0,64)     = 519.0673432047867
exp(logdet / (2·64))  = 57.69748694699989      q**0.5 = 57.697486947006624
exp(logdet / 64)      = 3328.999999999223      q      = 3329
```

So `exp(log_det/d)` is `vol^(2/d)`, not `vol^(1/d)`. The v2 instrument uses
`exp(log_det/(2d))` for its reported `delta_0_from_gso_logdet` and records the
precedent's literal form beside it under
`delta_0_from_gso_logdet_precedent_literal_form`, each labelled. **This is an
observation about a committed artifact, not a change to it**, and it is
mentioned here so that a reviewer comparing v2 against the precedent is not
surprised. It is outside the D1..D6 contract and this task takes no position on
what, if anything, should be done about it.

---

## 7. Files written

All paths absolute under
`/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-762807/tasks/TASK-20260826-602395/`.

**The twelve declared artifacts — all twelve exist:**

1. `rt_ctrl_1_matched_pair_v2.py`
2. `acceptance_tests.py`
3. `acceptance_results.json`
4. `acceptance_stdout.log` (7258 bytes)
5. `acceptance_stderr.log` (**0 bytes — empty, not omitted**)
6. `evidence/D1_D2_sigterm_surrogate.json`
7. `evidence/D1_D2_sigterm_surrogate_stdout.log`
8. `evidence/D3_D4_tiny_cell.json`
9. `evidence/D3_D4_environment.json`
10. `evidence/D5_tour_count.json`
11. `evidence/D6_root_hermite.json`
12. `implementation_report.md` (this file)

No declared artifact carries `NOT_REACHED`: every test ran.

**Artifacts produced but NOT on the declared list, disclosed here and named to
the snapshot task TASK-20260826-9e9d53 rather than silently added:**

* `artifacts/D1_D2_surrogate_S1_sigterm_failed_infrastructure/` —
  `surrogate_results.jsonl`, `surrogate_results.json`, `surrogate_rebuilt.json`,
  `surrogate_environment.json`, `surrogate_stdout.log`
* `artifacts/D1_D2_surrogate_S2_timeout_failed_infrastructure/` —
  `surrogate_results.jsonl`, `surrogate_environment.json`,
  `surrogate_stdout.log` (**no** `surrogate_results.json`, for the reason in
  §3.2 limit 4)
* `artifacts/D3_D4_D5_tiny_cell/` — `tiny_results.jsonl`, `tiny_results.json`,
  `tiny_environment.json`, `tiny_stdout.log`
* `__pycache__/` — Python bytecode cache, created by importing the instrument
  from the suite. It is matched by the repository's root `.gitignore`
  (`__pycache__/`) and will not be staged. Nothing was deleted.

**DEC-20260815-3e8e9c condition (v), discharged with the LITERAL label.** Both
surrogate executions were deliberately terminated, and every artifact of both
is preserved under directory names carrying the literal token
`failed_infrastructure`, with the same literal label carried **inside** each
flushed record as `failed_infrastructure: true` and as
`label: "failed_infrastructure"` in the evidence file. **Nothing was deleted.**
BATCH-f9780d discharged this condition in substance without the literal label
(its Validator's C-4 records the deviation); that deviation is not carried a
second time.

---

## 8. What these surrogates CANNOT show

Declared here, not discovered at review. KN-FIND-f54a82 binds the analogous
point for isolated-step probes and is why this section exists.

1. **A d=64 tour is milliseconds; a d=512, mpfr=100 tour may be hours.**
   Nothing in this suite exercises per-tour flush cost, file-handle lifetime,
   RSS growth or journal size against a tour of that length.
2. **Handler latency inside a long C call is untested at scale.** S1 shows the
   handler firing when SIGTERM lands during fplll work — but fplll work that
   returns to the interpreter within milliseconds. At d=512 the flush is
   deferred until the in-flight tour returns. **This is the residual loss
   window this design leaves, and it is the honest answer to "what would a
   d=512 run do that the toy cannot show":** a SIGTERM immediately followed by
   SIGKILL, or a hard container stop, mid-tour at d=512 would leave the STARTED
   stub, the completed tours, and the `tour_start` record for the in-flight
   tour — **but not** that tour's own partial state, and not an up-to-date RSS
   or cpu figure. What is recoverable in that case is a **lower bound**
   ("tour *k* began at *t* and had not completed by the kill"), not the tour's
   cost.
3. **Flush overhead is unbounded by this evidence.** Each tour writes one
   `tour_start` and one `tour_progress` line and issues two `fsync`s. At d=64
   that is negligible against a 0.1 s tour, and this suite does **not** measure
   it. At d=512 it should be negligible against an hours-long tour by the same
   argument — **but that is an argument, not a measurement**, and it is
   labelled as such.
4. **The tours table grows without bound** in memory and in the pre-serialised
   payload: every flushed record embeds the full `tours_table`. At 9 tours this
   is invisible. A cell with thousands of tours would make each refresh's
   `json.dumps` progressively more expensive, and the payload progressively
   larger. **No cap is implemented and none was tested.** Named as a known
   scale-only failure mode.
5. **`stdout_tail` is capped at 24 lines** (`STDOUT_TAIL_LINES`). For a
   long-running cell that cap could truncate away the only interesting part.
   The full stdout is separately retained in `<prefix>_stdout.log`, so the tail
   is a convenience inside the record and not the only copy — but the *record*
   carries only the last 24 lines.
6. **Nothing here bears on the mathematics.** Not on ML-KEM at any FIPS 203
   parameter set, not on lattice hardness, not on precision response at tour
   level, not on the obstruction RT-CTRL-1 targets. **An instrument that can
   now record an outcome has not observed one.**

---

## 9. Deviations, and everything else that must not be dropped

* **DEV-1 — two development smoke runs of the instrument were executed before
  the acceptance suite**, into the scratchpad (`<scratch>/smoke`,
  `<scratch>/kt`), not into the task directory. Their commands are in §2. The
  first ended in `status: "ERROR"` — `FileNotFoundError` on the strategies
  path, from a wrong repo-root depth in the module — which was fixed before the
  suite ran; the error was *recorded by the instrument rather than raised*,
  which is itself the D1/D2 behaviour working. The second was the first real
  SIGTERM test and behaved as S1 later did. These are development runs, not
  acceptance evidence, and no figure in this report or in any evidence file
  comes from them. They are disclosed rather than omitted.
* **DEV-2 — the instrument was edited between those smoke runs and the
  acceptance suite** (repo-root depth; per-signal payloads; the pre-tour
  payload refresh; the corrected GSO log-det handling of §6.1; the honest
  staleness fields). The acceptance suite ran **once**, against the final file,
  and every number in this report comes from that single execution.
* **DEV-3 — the acceptance suite's D3/D4/D5 tiny cell runs in-process with
  `arm_signals=False`**, so it does not replace the suite's own signal
  handlers. The arming path is therefore exercised **only** by the D1/D2
  subprocess surrogates — which is where it belongs, since only a real
  subprocess can be really killed. Disclosed because it means "the tiny cell
  passed" says nothing about the handler.
* **DEV-4 — no `EXP-*` contract, no `RUN-*` identifier, no run directory and no
  manifest were created.** batch.yaml PD-4 pre-declares this shape and
  `charged_runs_authorised: 0`. The reproduction-package layout of
  `docs/evidence-and-reproducibility.md` therefore does **not** apply to this
  task, and its absence is a declared property of the contract rather than an
  omission by this executor. `maximum_runs: 1` in the handoff is the
  dispatcher's minimum positive integer (PD-1) and was **not** consumed:
  **zero charged experiment runs were performed.**
* **No test was retuned, no assertion weakened, no threshold moved.** Every
  assertion in `acceptance_tests.py` was written before the suite was run and
  passed on the first and only suite execution. Nothing was rerun until it went
  green.
* **No infrastructure failure occurred during the acceptance suite** (exit 0,
  empty stderr). AGENTS.md rule 3 was therefore not invoked; the suite
  nevertheless carries explicit NOT_REACHED branches for every test, and they
  are unused.
* **Budget.** Declared 1800 s wall clock, 2 GB memory, `maximum_runs: 1`
  (0 charged). Actual compute: 6.457 s for the suite plus two smoke runs of
  ~2 s each. Peak RSS observed 81.9 MB, far under the 2 GB cap. No cap was
  approached and none was exceeded.

---

## 10. Certificate statement

**`certificate.kind: none`**, stated explicitly per
`docs/claims-and-verification.md`. This task claims **no** discrete-log solve
and **no** factor-base relation, so no solution certificate is required and
none is emitted. What the acceptance suite verifies is the **instrument's
recording behaviour**, and each of the six checks is an observation of an
artifact on disk written by the instrument itself, re-read and re-parsed by the
suite. The nearest thing to independent re-verification here is the D5
**equivalence control**, which re-derives the tour count through upstream
`BKZReduction.__call__` — code this task did not write — and obtains 9 = 9 with
a bit-identical b0.

## 11. Inference provenance and rule 12

| field | value |
| --- | --- |
| `requested_policy` | `executor-implementation` |
| `reasoning_effort` | `medium` (bound by `.claude/agents/executor.md`, derived from `orchestration/roles.yaml` → `model-policies.yaml`) |
| `fallback_used` | `false` |
| `fallback_allowed` | `false` |
| `degraded_allowed` | `false` |
| `model_verified` | **`false`** |
| `model_verified_reason` | No adapter probe receipt exists for this session and `AUTORESEARCH_POLICY` / `AUTORESEARCH_BACKEND` are unset. Recorded as unverified rather than asserted. |
| `independent_session` | `true`, **procedurally only** |

**Rule 12 status: UNMET AND UNWAIVED, INHERITED.** Under this harness every
policy alias resolves to one model, so this producer, both reviewers and the
closing Coordinator are expected to resolve to the same model. **Agreement
between them is correlated same-model judgement and is not independent
corroboration.** Independence in this batch is procedural — fresh sessions,
disjoint write scopes, sibling blindness — and never model-level.

## 12. Toy-scale and transfer statement

Every measurement in this report was taken at **d=64, beta=20, mpfr_bits=53**
(one probe at d=32, beta=10), on a single 4-core host, with fpylll 0.6.4 and
the content-bound strategies file
`f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18`. **Claim
tier: `toy`. Claim ceiling: `instrument_repair`.**

**No result here transfers to d=512, to mpfr_bits=100, to any other lattice
dimension or precision, or to any cryptographic parameter set, and none is
offered as transferring.** Nothing in this package states or implies anything
about ML-KEM at any FIPS 203 parameter set. The six PASSes say that the
successor instrument writes a STARTED stub before a cell, flushes a partial
record on a real signal, emits and flushes per-tour progress, records resources
machine-readably, counts tours by a stated mechanism that agrees with upstream
at d=64, and computes the root-Hermite factor by the standard definition. **A
passing acceptance board does not authorise the 100-bit re-run**; approval is a
frozen contract at a declared path plus a committed Coordinator decision, and
neither exists for that cell. Whether the instrument is fit to carry the next
capped run is for the two reviewers' `admissibility_ruling` blocks and
TASK-20260826-70d800, not for this report.
