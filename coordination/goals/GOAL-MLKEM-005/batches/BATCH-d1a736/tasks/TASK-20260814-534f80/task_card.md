# TASK-20260814-534f80 -- Corrected-construction Stage-0 re-measurement

    goal / batch    GOAL-MLKEM-005 / BATCH-d1a736
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      none (BATCH-3b9962 is closed and merged into this
                    branch's own history; DEC-20260814-4ac30a and
                    EV-MLKEM-ef0261 are already committed)
    review_required true (Validator + Red Team, review-adversarial, after
                    this task's own snapshot archive)
    budget          25200 s (7 hours), 16 GB, 1 run
    claim tier      TOY (PREREG-8's own frontmatter; unchanged by this task)

## What this task is for

Discharges `DEC-20260814-4ac30a`'s own `next_actions` in full. `BATCH-3b9962`
found `TASK-20260814-ffd791`'s Stage-0 measurement failed all 6 main-grid
cells with `fpylll.util.ReductionError('infinite loop in babai')`, and an
adversarial-review-plus-adjudication cycle reconciled why: the default
construction (`BKZReduction` built from a raw `IntegerMatrix`, which
internally builds its own GSO with `GSO.ROW_EXPO` at double precision) is
**not** fixed by raising mpfr precision alone, but the **isolated
LLL-preprocessing step** demonstrably **is** fixable once `GSO.ROW_EXPO` is
dropped and mpfr precision is raised explicitly (Red Team's own probe5,
independently reproduced twice). No session has yet measured whether the
corrected construction lets a **full BKZ tour** complete, or at what real
cost -- every attempt (Red Team's own probe6, this batch's own
`adjudicate_full_tour.py`) was time-bounded and terminated before finishing.

This task performs exactly that missing measurement, at a bounded, capped
cost.

## What it asks for

1. **Fix the construction.** Edit a fresh copy of the section-2 worker (do
   not touch `TASK-20260814-ffd791`'s own committed `stage0_feasibility.py`
   -- that run record is immutable) so that `worker_main_cell()` constructs
   `BKZReduction` from an **explicit, `GSO.ROW_EXPO`-free, mpfr-precision
   `GSO.Mat`** instead of handing it a raw `IntegerMatrix`:
   `FPLLL.set_precision(N)` called *before* construction, then
   `GSO.Mat(A, float_type="mpfr")` (no `flags=GSO.ROW_EXPO`), then
   `M.update_gso()`, then `LLL.Reduction(M, ...)`, then
   `BKZReduction(L)`. This is the exact construction
   `coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/archives/TASK-20260814-87a572/adjudication/adjudicate_precision.py`
   and `.../reviews/TASK-20260814-fe02ff/probes/probe5_precision_fix_at_cheapest_failing_d.py`
   already validate at the isolated-LLL-step level -- read both before
   writing this task's own copy.
2. **Determine the minimum adequate mpfr precision by bisection**, not an
   arbitrary choice. Bisect at the **isolated-LLL-step level only** (cheap:
   ~70-400s per trial, dominated by the outer `LLL.reduction(A)` call, not
   the mpfr step itself, which resolves in milliseconds once precision is
   adequate) at the cheapest main-grid cell (d=256, beta=40), between a
   lower bound where it still fails (53 bits, the double-precision-equivalent
   default) and an upper bound where it is known to succeed (212 bits, per
   the Red Team's own probe5). Use the SAME seed formula and instance
   (`default_rng([SEED_ROOT, 0, 256, 40, 0, 0])`, `SEED_ROOT=715923`) so the
   result is directly comparable to every other artifact in this goal. Cap
   this bisection phase at 3600s total; if it cannot complete, report
   `NOT_COMPUTED: bisection budget exhausted` honestly and fall back to
   212 bits (the last independently-validated working value) for step 3,
   disclosing that this is a fallback, not a determined minimum.
3. **Re-run the 6 main-grid cells** (`d in {256, 512}`, `beta in {40, 55,
   70}`) with the corrected construction at the bisected precision, each
   individually capped at **`PER_BASIS_FEASIBILITY_CAP_V2 = 7200 s`** (2
   hours -- roughly double PREREG-8's own original 3600s cap, a deliberate,
   disclosed escalation: this batch's own adjudication evidence
   (`ADJUDICATION.md`, `adjudicate_full_tour.py`, Red Team's own probe6)
   showed a full tour at an un-bisected, likely-oversized 212-bit precision
   ran ~684s-100s+ without completing OR erroring, so PREREG-8's own
   original 3600s double-precision-based cap is known inapplicable to this
   construction; 7200s is a first, bounded escalation, not a claim that it
   is sufficient). A cell that does not complete within 7200s is
   `NOT_COMPUTED: exceeded PER_BASIS_FEASIBILITY_CAP_V2`, not retried at a
   different parameter. If the task's own overall 25200s wall-clock cap is
   reached before all 6 cells are attempted, STOP and report the remaining
   cells as `NOT_COMPUTED: task budget exhausted before this cell was
   attempted` -- partial coverage is an honest outcome here, never papered
   over as a full sweep.
4. **Report, don't decide.** State plainly which cells completed and at what
   measured wall-clock/tours/delta, which hit the per-cell cap, and which
   were never attempted due to the overall task budget. Do not recommend
   whether Stage 1 should now be sized -- that is a separate, later
   Coordinator act, exactly as `TASK-20260814-ffd791`'s own task card
   reserved it.

## What it does not do

Does not touch `TASK-20260814-ffd791`'s own committed artifacts (immutable
run record). Does not run PREREG-8's own Stage 1 (no `>= 8`-draw grid, no
`2^20`+ target generation, no NULL-1/2/3/SENS controls). Does not change
`H-MLKEM-7d9bcc`'s status (stays `proposed`) or `EXP-MLKEM-42ea04`'s
(`review_required`, `approved_by: null` -- running this task is not
approval). Does not edit `prereg.md`, the hypothesis, or the experiment spec
-- all are frozen/filed; this is a task-level construction correction
DEC-20260814-4ac30a's own `binding_carries_restated_and_not_re_litigated`
confirms PREREG-8 section 1 point 1's own text already licenses without a
protocol amendment. Does not authorize any claim about ML-KEM security.

## Next steps after this task completes

1. A Coordinator-only snapshot archive (`TASK-20260814-cfa812`) commits this
   task's own artifacts alone, before either review reads them.
2. Independent Validator (`TASK-20260814-1ce70d`) and Red Team
   (`TASK-20260814-9cf080`) tasks (review-adversarial, xhigh effort) verify
   the bisection and the re-measurement independently.
3. A Coordinator ledger archive (`TASK-20260814-6af6d1`), carrying whatever
   `EV-*`/`DEC-*` the outcome warrants, decides -- explicitly, not by
   default -- whether and how PREREG-8's own Stage 1 can now be sized, or
   what the next escalation is if the corrected construction still cannot
   complete within any defensible cap.

## Artifact

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/tasks/TASK-20260814-534f80/task_card.md
