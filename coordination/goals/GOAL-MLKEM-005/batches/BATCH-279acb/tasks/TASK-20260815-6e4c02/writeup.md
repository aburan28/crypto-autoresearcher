# TASK-20260815-6e4c02 -- d=512 precision bisection and decisive main-grid reattempt

Discharges `DEC-20260814-8ec2e5`'s own `next_actions` (section 12) in full.
Real execution, one script (`stage0_d512_precision_bisection_and_reattempt.py`),
two phases, run once (`maximum_runs=1`). Total wall-clock:
`2026-08-15T11:49:44Z` to `2026-08-15T12:59:23Z` (~4779s), well inside the
48000s budget cap, with the outer `timeout 48060` backstop never triggered.

## Phase (a): genuine bisection at (d=512, beta=40), isolated-LLL-step level

Reused `probe1_bisection_generality.py`'s own harness, construction, and
seed-formula shape directly: `SEED_ROOT=715923`,
`default_rng([715923, 0, 512, 40, 0, 0])`, the ROW_EXPO-free mpfr `GSO.Mat`
construction (`FPLLL.set_precision(N)` before `GSO.Mat` construction;
`GSO.Mat(A, float_type="mpfr")`, no `flags=GSO.ROW_EXPO`; `M.update_gso()`;
`LLL.Reduction(M, flags=LLL.DEFAULT)`; `lll_obj()` called directly, not
wrapped in `BKZReduction`).

Both endpoints were re-confirmed as trials before bisecting, matching
`TASK-20260814-534f80`'s own `bisect_precision()` design:

- 65 bits: `ERROR` (`ReductionError: infinite loop in babai`), 371.30s
  subprocess wall-clock, `seed_used=2074339090`.
- 100 bits: `COMPLETED`, 372.27s subprocess wall-clock,
  `seed_used=2074339090`.

Both reproduced the Red Team's own OBJ-1/CTRL-1 control exactly (same
outcome, same seed). No invalidation trigger fired.

The 1-bit-resolution binary search then ran 6 further trials (82, 73, 69,
67, 68 bits, plus the two endpoints already run = 8 trials total), all at
the identical seed `2074339090` (beta does not affect the isolated step's
own computation, only which basis is drawn, per `probe1`'s own design,
reused unchanged):

| mpfr_bits | status | subprocess wall-clock (s) |
|---:|---|---:|
| 65 | ERROR | 371.30 |
| 100 | COMPLETED | 372.27 |
| 82 | COMPLETED | 372.28 |
| 73 | COMPLETED | 378.80 |
| 69 | COMPLETED | 406.89 |
| 67 | ERROR | 389.90 |
| 68 | ERROR | 371.31 |

**Determined minimum adequate isolated-LLL-step precision at (d=512,
beta=40): 69 bits.** This is a genuinely determined minimum, not a
fallback: 68 bits errors, 69 bits completes; total bisection wall-clock was
2662.76s of the 3600s `BISECTION_D512_BUDGET_SECONDS` cap (budget was not
exhausted).

## Phase (b): full-BKZ-tour reattempt of the three currently-ERRORing d=512 cells

Reused `TASK-20260814-534f80`'s own `worker_main_cell()` construction shape
directly (`GSO.Mat` -> `LLL.Reduction` -> `BKZReduction(L)`), at the
phase-(a)-determined precision of 69 bits, each cell individually capped at
`PER_BASIS_FEASIBILITY_CAP_V3=14400s` (explicitly NOT
`PER_BASIS_FEASIBILITY_CAP_V2=7200s` copied forward unexamined -- see
`dispatch_queue.json`'s own `budget_justification` for the sizing
arithmetic).

| d | beta | seed_used | status | subprocess wall-clock (s) | cap reached? |
|---:|---:|---:|---|---:|---|
| 512 | 40 | 2074339090 | ERROR | 631.74 | no (4.4% of 14400s cap) |
| 512 | 55 | 452658293 | ERROR | 389.37 | no (2.7% of 14400s cap) |
| 512 | 70 | 915347894 | ERROR | 396.35 | no (2.8% of 14400s cap) |

All three seeds are bit-identical to `TASK-20260814-534f80`'s own reported
`main_grid_seeds_used` entries for the same three cells, confirming the seed
formula is unchanged.

**0 of 3 reattempted cells completed a full BKZ tour.** All three errored
with `ReductionError: infinite loop in babai`, none exceeded the cap, and no
cell was skipped for budget reasons (overall script wall-clock for phase (b)
was 4080.23s of the 48000s overall budget).

A raw, disclosed difference in failure site between the three cells (no
interpretation drawn from it here, per this task's own completion_gate and
prohibitions -- left for Validator/Red Team/Coordinator reading):

- `(d=512, beta=40)`: fails inside `svp_preprocessing`'s own `lll_obj()`
  call during the first tour's SVP-block reduction -- i.e. it gets PAST
  `BKZReduction`'s own initial `self.lll_obj()` call before failing.
- `(d=512, beta=55)` and `(d=512, beta=70)`: both fail at
  `bkz.py` line 123's `self.lll_obj()` -- the FIRST call inside
  `BKZReduction.__call__`, before any tour begins (the same failure site as
  the predecessor batch's own 65-bit run and the Red Team's own OBJ-1
  control).

Full tracebacks for all three cells are in
`main_grid_d512_reattempt_results.json`.

## (c) Every reported number is real and measured or explicitly NOT_COMPUTED

No `NOT_COMPUTED` outcome occurred anywhere in this run: both bisection
endpoints reproduced, the bisection resolved to a 1-bit-width genuine
minimum within budget, and all three reattempt cells reached a definite
`ERROR` outcome within their own 14400s cap. Every number in this writeup
and in `bisection_d512_results.json` / `main_grid_d512_reattempt_results.json`
is taken directly from this run's own executed output; nothing is estimated
or fabricated.

## (d) (d=256, beta=55) and (d=256, beta=70) were not attempted

Confirmed by direct inspection of the script and its output: `REATTEMPT_CELLS
= [(512, 40), (512, 55), (512, 70)]` only; no `d=256` cell of any kind
appears anywhere in this run's code path, logs, or results files. These
remain the open question named in `EV-MLKEM-098182`'s own
`unresolved_confounds`, explicitly out of scope for this task, and are left
for a later, separately-scoped follow-up.

## What this writeup does not do

Does not make any C1/C2 statement, in either direction. Does not recommend a
Stage-1 sizing decision or an escalation-branch determination -- both remain
a later, separate Coordinator act. Does not authorize any claim about ML-KEM
security. Does not change `H-MLKEM-7d9bcc`'s status (stays `proposed`) or
`EXP-MLKEM-42ea04`'s (`review_required`, `approved_by: null`) -- neither file
was touched by this task. Claim tier stays TOY throughout.

## Invalidation triggers checked

None fired. Full per-trigger detail is in `run_manifest.yaml`'s own
`invalidation_triggers_checked` block.

## Artifacts

- `stage0_d512_precision_bisection_and_reattempt.py` -- the script.
- `bisection_d512_results.json` -- phase (a) raw output.
- `main_grid_d512_reattempt_results.json` -- phase (b) raw output.
- `command.txt`, `stdout.log`, `stderr.log`, `run_manifest.yaml`,
  `environment.json`, `run_start_utc.txt`, `run_end_utc.txt`.
