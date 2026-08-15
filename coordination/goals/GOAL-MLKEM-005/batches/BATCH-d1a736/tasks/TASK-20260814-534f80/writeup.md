# TASK-20260814-534f80 -- Corrected-construction Stage-0 re-measurement: writeup

Discharges `DEC-20260814-4ac30a`'s `next_actions` in full: fixes
`worker_main_cell()`'s construction (drops `GSO.ROW_EXPO`, raises mpfr
precision explicitly), determines the minimum adequate precision by
bisection, re-runs PREREG-8's 6 Stage-0 main-grid cells under the corrected
construction and a realistically-sized 7200s-per-cell cap, and reports the
real, measured outcome.

This writeup reports observations only. It does **not** rule on
`T-PROJNOISE-NODATA`, does **not** change `H-MLKEM-7d9bcc`'s or
`EXP-MLKEM-42ea04`'s status, and does **not** recommend a Stage-1 sizing
decision -- all reserved for the Coordinator/Validator/Red Team per this
task's own completion gate and `DEC-20260814-4ac30a`.

## 1. Construction used

Matches the exact shape `DEC-20260814-4ac30a`'s `next_actions` and this
batch's own adjudication validated at the isolated-LLL-step level, with no
deviation:

```
FPLLL.set_precision(N)                       # BEFORE GSO.Mat construction
M = GSO.Mat(A, float_type="mpfr")            # explicitly NO flags=GSO.ROW_EXPO
M.update_gso()
L = LLL.Reduction(M, flags=LLL.DEFAULT)
bkz = BKZReduction(L)
```

Verified directly against this host's fpylll 0.6.4 `bkz.py` source before
the run: `BKZReduction.__init__` branches on `isinstance(A, LLL.Reduction)`
and, when true, sets `L = A; M = L.M; self.lll_obj = L` -- it never takes the
raw-`IntegerMatrix` branch that rebuilds `GSO.Mat(A, flags=GSO.ROW_EXPO)`
internally. `worker_main_cell()` in `stage0_v2_feasibility.py` (this task's
own fresh copy; `TASK-20260814-ffd791`'s own `stage0_feasibility.py` was
never touched or imported) implements exactly this.

## 2. Bisection (Phase 1)

Isolated LLL-preprocessing-step level only (`GSO.Mat` + `LLL.Reduction` +
direct `lll_obj()` call, **not** wrapped in `BKZReduction`), at
`(d=256, beta=40)`, `seed_used=1398073216` -- confirmed bit-identical to
`TASK-20260814-ffd791`'s own reported seed at this cell and to every other
artifact in this goal using the same seed formula.

Both endpoints were re-confirmed as trials before bisecting (never assumed):
53 bits -- `ERROR: ReductionError('infinite loop in babai')`; 212 bits --
`COMPLETED` (0.0040s isolated step). 1-bit-resolution binary search then ran
9 total trials (2 endpoint-confirmation + 7 bisection steps), each trial
dominated by the outer `LLL.reduction(A)` call (~67-70s per trial, matching
the task card's own "~70-400s per trial" expectation), for
**618.4s of the 3600s bisection budget** -- the bisection budget was **not**
exhausted.

**Determined minimum adequate mpfr precision: 65 bits**, the smallest tested
value at which the isolated LLL-preprocessing step completes on this exact
instance (64 bits: `ERROR`; 65 bits: `COMPLETED` in 0.0025s). This is a
*determined minimum*, not the disclosed 212-bit fallback -- the fallback
path was not taken. Full trial-by-trial detail (precision, outcome, elapsed
time) is in `bisection_results.json`.

## 3. Main-grid re-measurement (Phase 2)

All 6 main-grid cells were **attempted** (none skipped for overall-budget
reasons -- the overall 25200s cap was never reached; total script wall clock
was 9863.27s, about 39% of the 25200s cap). Each cell ran the corrected
construction at the bisected 65-bit precision, capped individually at
`PER_BASIS_FEASIBILITY_CAP_V2=7200s`.

| d   | beta | outcome | subprocess wall-clock | note |
|-----|------|---------|------------------------|------|
| 256 | 40   | ERROR   | 223.4s | `ValueError: math domain error` raised inside the tracer's own `tour.__exit__` -> `basis_quality()` -> `log(r_)` call, **while handling** the identical `ReductionError('infinite loop in babai')` raised by `self.lll_obj()` inside `bkz.py`'s own `svp_preprocessing` (full chained traceback in `stage0_v2_results.json`) -- the underlying condition is the same "infinite loop in babai" failure both reviews and the producer report elsewhere in this goal; the `ValueError` is a secondary exception from fpylll's own exception-handling/tracer path attempting to compute a quality metric over a basis left in a post-error state, not a distinct root cause |
| 256 | 55   | ERROR   | 626.5s | `ReductionError: 'infinite loop in babai'`, raised inside a nested `svp_preprocessing` call (deeper in the BKZ tour's own recursive preprocessing than d=256/beta=40's occurrence -- see full traceback in `stage0_v2_results.json`) |
| 256 | 70   | NOT_COMPUTED | 7200.0s (cap) | `exceeded PER_BASIS_FEASIBILITY_CAP_V2` -- ran the full 7200s cap without completing OR erroring (SIGTERM-killed by the parent at the cap, `subprocess_returncode=-15`); consistent with, and now measured well past, the Red Team's own probe6 (~684s) and this batch's own adjudication (>100s) preliminary observations that this cell "runs a long time without completing or erroring" |
| 512 | 40   | ERROR   | 386.0s | `ReductionError: 'infinite loop in babai'`, raised directly at `bkz.py:123` (`self.lll_obj()` inside `BKZReduction.__call__`, the first tour) |
| 512 | 55   | ERROR   | 395.5s | Same as 512/40: `ReductionError: 'infinite loop in babai'` at `bkz.py:123` |
| 512 | 70   | ERROR   | 413.6s | Same as 512/40: `ReductionError: 'infinite loop in babai'` at `bkz.py:123` |

**0 of 6 main-grid cells completed a full BKZ tour.** 5 cells terminated
with a definite exception (one instance of which surfaced as a secondary
`ValueError` from the tracer path while handling the same underlying
`ReductionError`); 1 cell (`d=256, beta=70`) hit the 7200s per-cell cap
without completing or erroring, exactly as its own cap discipline requires
-- it was not retried at a different parameter.

Full raw per-cell detail (seed, exact traceback, wall-clock, peak RSS,
strategies file used) is in `stage0_v2_results.json`.

## 4. What this measures, stated plainly

The corrected construction (`GSO.Mat(A, float_type="mpfr")`, no
`GSO.ROW_EXPO`, `FPLLL.set_precision(65)` called first) -- validated at the
isolated-LLL-preprocessing-step level by this batch's own adjudication and
by the Red Team's probe5 -- **does not, at the full-BKZ-tour level, clear
any of PREREG-8's 6 main-grid Stage-0 cells** at the bisected 65-bit
precision, on this host, this fpylll 0.6.4/fplll build, this seed formula.
Five cells hit the identical `'infinite loop in babai'` condition (one via a
chained secondary exception) after running substantially longer than the
double-precision default construction did (223s-626s vs. `TASK-20260814-
ffd791`'s own reported 53.7s-408.9s range for the *default*, `ROW_EXPO`-on
construction at the same cells -- **the corrected construction runs longer
before failing, it does not avoid failing**, except at `d=256, beta=70`
where it instead exhausts the 7200s cap without a definite outcome either
way). This is a real, measured, reproducible observation about this specific
construction at this specific bisected precision -- it does not by itself
determine whether a materially higher precision (e.g. the 212-bit value this
batch's earlier adjudication used, which itself only avoided the immediate
exception at the isolated-step level and was never measured to a completed
full tour either) would behave differently; that is a further, unmeasured
question this task's own scope does not answer.

## 5. Deviations and honest disclosures

- **The `ValueError: math domain error` at `d=256, beta=40`** is a different
  Python exception TYPE than the `ReductionError` reported at every other
  ERROR cell (and at every cell in `TASK-20260814-ffd791`'s own default-
  construction run). It is disclosed here in full, with its complete chained
  traceback preserved in `stage0_v2_results.json`, rather than characterized
  as identical without qualification: the traceback shows it arises from
  fpylll's own tracer path (`tour.__exit__` -> `basis_quality()`) attempting
  to compute `log()` over a GSO diagonal value that is non-positive or NaN,
  while Python was already unwinding the stack from the same underlying
  `ReductionError('infinite loop in babai')` every other cell reports
  directly. This is reported as a genuinely observed, chained-exception
  variant of the same underlying condition, not asserted to be identical
  without qualification, and not smoothed over.
- **`d=256, beta=70` neither completed nor errored within its 7200s cap.**
  This is disclosed as `NOT_COMPUTED: exceeded PER_BASIS_FEASIBILITY_CAP_V2`,
  per its own cap discipline -- it was not retried at a different beta,
  dimension, or precision.
- The 6th cell's own `seed_used` value could not be recorded in
  `run_manifest.yaml`'s per-cell seed table (the worker subprocess sets the
  seed internally via `FPLLL.set_random_seed(seed)` before writing any
  output, but was SIGTERM-killed before it ever reached `json.dump` -- its
  `seed_used` value is not recoverable from this run's own artifacts). This
  is disclosed rather than fabricated or silently omitted; the seed
  *formula* and the fact that the same formula was applied are not in
  question, only this one instance's concrete integer value.
- The overall task budget (25200s) was **not** exhausted -- all 6 cells were
  attempted, and the script finished in 9863.27s (~39% of the cap). No cell
  was skipped for "task budget exhausted before this cell was attempted"
  reasons; that branch of the task's own completion gate did not fire this
  run.
- Repository `HEAD` on this branch advanced during the run's ~2h44m
  wall-clock window (an unrelated external PR merge and its main-events
  digest commit, via the repository's own scheduled automation) -- disclosed
  in `run_manifest.yaml`; confirmed the snapshot commit
  `9010b20f68f990a13e19fc41bc445d39f63517cb` this task started from remains
  an ancestor of the branch `HEAD` at completion, and nothing in this task's
  own `write_scope` was touched by that drift.

## 6. Budget accounting

- Bisection phase: 618.4s of a 3600s budget (not exhausted).
- Main-grid phase: 6/6 cells attempted; 3253.6s of subprocess wall-clock
  summed across the 5 ERROR cells (223.4 + 626.5 + 386.0 + 395.5 + 413.6),
  plus 7200.0s for the capped NOT_COMPUTED cell = 10453.6s of subprocess
  time; total script wall-clock (including bisection, per-cell subprocess
  launch/teardown overhead, and the final results write) was 9863.27s.
- Overall task budget: 9863.27s used of the 25200s cap (~39%); 1 of 1
  permitted run performed; the outer `timeout 25260` OS-level backstop was
  never triggered.

## 7. Artifacts

All under this task's own write_scope:
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/tasks/TASK-20260814-534f80/`
-- `stage0_v2_feasibility.py`, `bisection_results.json`,
`stage0_v2_results.json`, `writeup.md` (this file), `command.txt`,
`stdout.log`, `stderr.log`, `run_manifest.yaml`, `environment.json`,
`run_start_utc.txt`, `run_end_utc.txt`.
