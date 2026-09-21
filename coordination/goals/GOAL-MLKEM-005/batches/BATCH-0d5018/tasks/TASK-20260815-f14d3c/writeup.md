# TASK-20260815-f14d3c -- (d=512, beta=55) and (d=512, beta=70) per-basis precision bisection and decisive reattempt

## Provenance -- interrupted prior attempt (disclosed, not the source of this record)

This task was dispatched TWICE. The FIRST dispatch started at
`2026-08-15T14:21:53Z` and was killed by a genuine infrastructure failure:
the entire VM rebooted at `2026-08-15T17:09:32Z` (confirmed via `uptime`
showing `up 3 min` at the start of this second attempt, and by the crash
occurring approximately 2h47m into execution -- not inferred from partial
output alone). By AGENTS.md/CLAUDE.md rule 3, an infrastructure failure
(VM reboot) is never mathematical evidence, and no conclusion was drawn
from the first attempt.

The first attempt reached: Phase (a)'s bisection for `(d=512, beta=55)`
fully completed and self-consistent (determined 75 bits, matching this
second attempt's own re-derivation below), and was interrupted partway
through Phase (a)'s bisection for `(d=512, beta=70)`, before any Phase (b)
reattempt had started for either basis.

Per the task dispatch instructions, all partial artifacts from the first
attempt (`bisection_d512_beta55_results.json`, `stdout.log`, `stderr.log`,
`command.txt`, `environment.json`, `run_start_utc.txt`) were deleted from
this task's `write_scope` before this second attempt began, to avoid any
ambiguity between old and new data. This is a full, clean re-execution
from scratch -- not a resume, and not a rescoring of the first attempt's
partial data. The script surviving in the write_scope from the first
attempt, `stage0_d512_beta5570_precision_bisection_and_reattempt.py`, was
independently re-verified line-by-line against this task's own task card
(construction shape, seed formula, budget arithmetic) before being trusted
and reused unmodified for this second attempt -- see "Independent
verification of the surviving script" below.

The SECOND attempt (this record) started at `2026-08-15T17:14:00Z` and ran
to completion at `2026-08-15T23:30:29Z`, with no infrastructure
interruption. All figures reported below are from this second, complete
attempt only.

## Independent verification of the surviving script

Before trusting or reusing `stage0_d512_beta5570_precision_bisection_and_
reattempt.py`, the following checks were performed independently (not
merely assumed because the file survived the crash):

- **Seed formula**: re-computed `int(np.random.default_rng([715923, 0,
  512, beta, 0, 0]).integers(0, 2**31-1))` directly in a fresh Python
  process for `beta=55` and `beta=70`. Result: `452658293` and
  `915347894` respectively -- exact match to both the task card's expected
  seeds and the Red Team's own CTRL-1 (`probe1_d512_beta_generality.py`)
  seeds.
- **Construction shape**: diffed `worker_bisect()` and `worker_main_cell()`
  in the surviving script, structurally, against `TASK-20260815-6e4c02`'s
  own validated `worker_bisect()`/`worker_main_cell()`
  (`coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/tasks/
  TASK-20260815-6e4c02/stage0_d512_precision_bisection_and_reattempt.py`)
  and the Red Team's `probe1_d512_beta_generality.py`'s `worker()`. All
  three match: `FPLLL.set_precision(N)` called BEFORE `GSO.Mat`
  construction; `GSO.Mat(A, float_type="mpfr")` with explicitly NO
  `flags=GSO.ROW_EXPO`; `M.update_gso()`; `LLL.Reduction(M,
  flags=LLL.DEFAULT)`; bisection calls `lll_obj()` directly (not wrapped
  in `BKZReduction`); reattempt phase uses `GSO.Mat -> LLL.Reduction ->
  BKZReduction(L)` with `bkz(par, tracer=True)`.
- **Budget arithmetic**: `BISECTION_D512B_BUDGET_SECONDS=3600` (per
  basis), `PER_BASIS_FEASIBILITY_CAP_V3=14400` (per cell),
  `OVERALL_BUDGET_SECONDS=37200`, `WRITE_BUFFER_SECONDS=600` -- all match
  the task card's stated sizing (`2 x 3600s bisection + 2 x 14400s
  reattempt + 600s buffer = 37200s`).
- **Search window**: `BISECTION_LO_KNOWN_FAILING=69`,
  `BISECTION_HI_KNOWN_SUCCEEDING=100` -- matches the task card's narrowed
  `[69, 100]` window (not `[65, 100]`).
- **Scope**: script does not touch `(d=512, beta=40)`, `(d=256, beta=55)`,
  `(d=256, beta=70)`, or any ledger/status file.

No deviation from the task card's construction, seed formula, or budget
arithmetic was found. The script did not need to be rewritten and was
reused unmodified for this second, clean attempt.

## Execution summary (this attempt only)

- Started: `2026-08-15T17:14:00Z`
- Finished: `2026-08-15T23:30:29Z`
- Total script wall-clock (self-reported): `22545.08s` (~6h16m), well
  within the `37200s` (10h20m) outer budget.
- Outer wrapper: `timeout 37260 python3 stage0_d512_beta5570_precision_
  bisection_and_reattempt.py > stdout.log 2> stderr.log` (matching
  `command.txt`), not triggered (process exited on its own before the
  outer timeout).
- `stderr.log` is empty; all diagnostics are captured in-band by the
  script's own JSON records and `stdout.log`.

## Phase (a): per-basis precision bisection (isolated LLL step)

Both bases' own endpoint reproduction is `endpoint_reproduction_ok: true`
-- i.e. this second attempt independently re-confirmed 69 bits `ERROR` /
100 bits `COMPLETED` with the exact expected seeds before bisecting, per
the task card's own invalidation trigger.

### (d=512, beta=55)

- `seed_used = 452658293` (matches expected).
- Trials (mpfr_bits -> status): 69 -> ERROR, 100 -> COMPLETED, 84 ->
  COMPLETED, 76 -> COMPLETED, 72 -> ERROR, 74 -> ERROR, 75 -> COMPLETED.
- **Determined minimum adequate isolated-LLL-step precision: 75 bits**
  (genuine 1-bit-resolution bisection result, not a fallback).
- Bisection wall-clock: `2747.94s`, within the `3600s` per-basis budget.
- All isolated-step failures reproduce the same `ReductionError: b'infinite
  loop in babai'` signature seen throughout this goal's history
  (`KN-FIND-f54a82`).

### (d=512, beta=70)

- `seed_used = 915347894` (matches expected).
- Trials (mpfr_bits -> status): 69 -> ERROR, 100 -> COMPLETED, 84 ->
  COMPLETED, 76 -> COMPLETED, 72 -> ERROR, 74 -> COMPLETED, 73 ->
  COMPLETED.
- **Determined minimum adequate isolated-LLL-step precision: 73 bits**
  (genuine 1-bit-resolution bisection result, not a fallback).
- Bisection wall-clock: `2894.31s`, within the `3600s` per-basis budget.

Both bases resolved a genuine, own-basis minimum -- neither fell back to
the disclosed `FALLBACK_PRECISION_BITS=100`. The two minima differ from
each other (75 vs 73 bits) and both differ from the `(d=512, beta=40)`-
borrowed value of 69 bits that `BATCH-279acb` found inadequate for both
these bases at the isolated-step level.

## Phase (b): full-BKZ-tour reattempt at each basis's own bisected precision

### (d=512, beta=55), precision = 75 bits (bisected minimum, not fallback)

- **Status: `ERROR`** after `2502.74s` (peak RSS `141.4 MB`).
- Failure site: `bkz.py` `svp_preprocessing` -> `self.lll_obj(lll_start,
  lll_start, kappa + block_size)` -> `ReductionError: b'infinite loop in
  babai'`.
- This is the SAME failure signature (`infinite loop in babai`) as the
  isolated-step bisection failures below 75 bits, and the same pattern
  `KN-FIND-f54a82` already names at `(d=512, beta=40)`: a precision that
  clears the isolated LLL step does not necessarily clear a full BKZ tour,
  because the tour's own internal `lll_obj()` calls operate on a
  different, more-reduced row range/kappa window than the isolated-step
  harness tests. This is the recurrence the task card's item (e) explicitly
  named as out of this task's own scope to resolve (CTRL-3's costlier
  half, full-tour-level precision search), not attempted here.

### (d=512, beta=70), precision = 73 bits (bisected minimum, not fallback)

- **Status: `NOT_COMPUTED`** -- exceeded `PER_BASIS_FEASIBILITY_CAP_V3`
  (`14400s`/4h). `subprocess_timed_out: true`, `subprocess_returncode:
  -15` (terminated by the parent's own hard wall-clock kill), peak RSS
  `142.4 MB`.
- This is the FIRST time in this goal's own recorded history that a d=512
  main-grid cell attempt has hit the feasibility cap rather than raising a
  hard `ReductionError`. The prior batch's own Red Team COST-3 explicitly
  flagged `PER_BASIS_FEASIBILITY_CAP_V3` as "adequate-and-untested-as-
  binding, not adequate-and-validated-as-binding" -- this run is the first
  evidence bearing on that flag: the cap is not merely a formality here: at
  least one cell's own reduction process ran the full 4 hours without
  either completing or raising the `ReductionError`/`infinite loop in
  babai` signature seen everywhere else in this goal. No conclusion is
  drawn about WHY (e.g. whether it would have completed at 14401s, or
  whether it was in a genuinely different, slower failure/success regime)
  -- that is explicitly NOT_COMPUTED, honestly, per the task card's own
  requirement.

Neither cell cleared its own full BKZ tour. `n_cells_completed: 0`,
`n_cells_not_computed_or_error: 2`.

## Frozen prediction / cost-model status

This is a measurement task, not a heuristic-validation or cost-model
experiment; `PREREG-8` and `EXP-MLKEM-42ea04` (claim tier TOY) remain
`review_required`/`approved_by: null`, unchanged by this task. No C1/C2 or
ML-KEM-security statement is made. `H-MLKEM-7d9bcc` stays `proposed`,
unchanged.

## Observations (measured, not interpreted)

1. Each basis has its own genuine, distinct minimum isolated-LLL-step
   precision (75 bits at beta=55, 73 bits at beta=70), both different from
   each other and both different from the beta=40-borrowed 69-bit value
   `BATCH-279acb` found inadequate.
2. At `(d=512, beta=55)`, the own-basis-bisected 75-bit precision still
   does NOT clear the full BKZ tour -- a fourth-plus recurrence of the
   isolated-step-vs-full-tour permissiveness pattern (`KN-FIND-f54a82`),
   now observed at a basis whose precision was calibrated to itself, not
   borrowed.
3. At `(d=512, beta=70)`, the own-basis-bisected 73-bit precision produced
   `NOT_COMPUTED` (budget-exhausted timeout) rather than either a
   `COMPLETED` or a hard `ReductionError` -- the first observed instance of
   this outcome class for a d=512 main-grid cell in this goal's history.
   This is reported honestly as `NOT_COMPUTED`, never as evidence in either
   direction.
4. `n_cells_completed = 0 / 2` for this task's own two cells.

## Anomalies / deviations

- **Infrastructure failure (first dispatch)**: VM reboot at
  `2026-08-15T17:09:32Z`, ~2h47m into the first attempt's execution,
  interrupting Phase (a)'s bisection for `(d=512, beta=70)`. Classified
  `infrastructure_error`. No mathematical conclusion drawn from the first
  attempt; this second, clean attempt is the sole source of this task's
  own reported figures. Disclosed here per AGENTS.md/CLAUDE.md rule 12/3
  and the executor role contract's requirement to record all deviations
  and infrastructure events.
- **Background-monitor kills during this second attempt's wait loop**:
  the executor session's own shell-level polling loops (used only to
  detect when the long-running script process exited) were repeatedly
  killed by the host session's own background-task lifecycle limit
  (observed roughly hourly) while the actual computation (`timeout 37260
  python3 ...`, PID 8148, and its worker subprocesses) continued running
  unaffected throughout. This is a monitoring-loop artifact of the
  execution session, not of the measured computation itself: the target
  process's own PID, elapsed time, and stdout/stderr were independently
  re-checked and confirmed continuously alive and undisturbed at each
  recheck. Disclosed for completeness; does not affect the recorded
  results, which come entirely from the target process's own JSON output.
- **`(d=512, beta=70)` reattempt hit the feasibility cap rather than
  erroring** -- see Phase (b) above; disclosed as a first-of-its-kind
  outcome for this goal, not smoothed over or silently treated as
  equivalent to the prior `ReductionError` pattern.

## Scope discipline (explicitly not done, per task card)

- `(d=512, beta=40)` was NOT re-attempted (already properly calibrated and
  reattempted in `BATCH-279acb`).
- `(d=256, beta=55)` and `(d=256, beta=70)` were NOT attempted or
  characterized.
- No full-tour-level precision search (CTRL-3's costlier half) was
  performed.
- No PREREG-8 Stage 1 activity was run.
- No hypothesis/experiment status was changed.
- No C1/C2 or ML-KEM-security claim is made in either direction.

## Artifacts

- `bisection_d512_beta55_results.json`
- `bisection_d512_beta70_results.json`
- `main_grid_d512_beta5570_reattempt_results.json`
- `command.txt`, `environment.json`, `stdout.log`, `stderr.log`
- `run_start_utc.txt`, `run_end_utc.txt`
- `run_manifest.yaml`
- this `writeup.md`
