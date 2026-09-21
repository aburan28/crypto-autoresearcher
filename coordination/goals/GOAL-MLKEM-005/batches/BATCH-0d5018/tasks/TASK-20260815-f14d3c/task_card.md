# TASK-20260815-f14d3c -- (d=512, beta=55) and (d=512, beta=70) per-basis precision bisection and decisive reattempt

    goal / batch    GOAL-MLKEM-005 / BATCH-0d5018
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      none (BATCH-279acb is closed; DEC-20260815-201633 and
                    EV-MLKEM-e4189c are already committed)
    review_required true (Validator + Red Team, review-adversarial, after
                    this task's own snapshot archive -- not yet dispatched)
    budget          37200 s (10h20m), 16 GB, 1 run
    claim tier      TOY (PREREG-8's own frontmatter; unchanged by this task)
    execution       IMPLEMENTATION AND EXECUTION ARE AUTHORIZED. This is a
                    real-compute task, not a zero-run design gate.

## What this task is for

Discharges `DEC-20260815-201633`'s own `next_actions` (section 12) in full.
`BATCH-279acb` bisected a precision at `(d=512, beta=40)` only, applied it
unchanged to the other two currently-ERRORing d=512 main-grid cells, and
found 0/3 cells cleared. Two independent reviews reconciled that outcome:
only `(d=512, beta=40)` was ever tested at its own correctly-calibrated
precision; `(d=512, beta=55)` and `(d=512, beta=70)` were tested only at
that basis's own borrowed, now-shown-inadequate 69-bit value. The Red
Team's own OBJ-1 (`TASK-20260815-85e02a`, `probes/probe1_d512_beta_generality.py`)
independently, live executed the identical isolated-LLL-step harness at
both other bases and DECISIVELY FALSIFIED "69 bits generalizes within
d=512": at BOTH `(d=512, beta=55, seed=452658293)` and `(d=512, beta=70,
seed=915347894)`, 69 bits -- `ERROR`; 100 bits -- `COMPLETED`, bracketing
each basis's own true minimum to `(69, 100]`. `DEC-20260815-201633` declines
to read that narrower 0/3 outcome as licensing `DEC-20260814-4ac30a`'s own
named escalation branches (upstream fplll bug report, alternate
build/version, or a scoped-down dimension) until this decisive, narrower,
cheaper follow-up is run: does EACH of those two cells clear its own full
BKZ tour once precision is bisected AT ITS OWN BASIS, not borrowed from a
different one?

This task performs exactly that measurement, at a bounded, explicitly
justified cost, for both bases separately.

## What it asks for

1. **(a) Determine EACH basis's own minimum adequate isolated-LLL-step
   precision by a GENUINE, SEPARATE 1-bit-resolution bisection** -- not a
   2-point bracket, which the Red Team's own CTRL-1 (`probe1_d512_beta_
   generality.py`) already supplies as a `(69, 100]`-bit bracket at BOTH
   bases -- at `(d=512, beta=55)` AND, SEPARATELY, at `(d=512, beta=70)`.
   **Search window is `[69, 100]`, not `[65, 100]`**: the Red Team's own
   CTRL-1 already confirms 69 bits `ERROR`s and 100 bits `COMPLETED`s at
   the isolated-step level for BOTH bases (`seed_used=452658293` at
   beta=55, `seed_used=915347894` at beta=70), so re-testing anything
   below 69 bits would repeat a measurement CTRL-1 already made and is
   explicitly not required -- this narrows the search window from the
   predecessor's 35-bit-wide `[65,100]` to a 31-bit-wide `[69,100]`, one
   fewer bisection step needed per basis (`ceil(log2(31))=5` vs.
   `ceil(log2(35))=6`). Reuse `probes/probe1_d512_beta_generality.py`'s own
   harness, construction, and seed-formula shape **directly**: same
   `SEED_ROOT=715923`, same `default_rng([SEED_ROOT, 0, d, beta, 0, 0])`
   formula, same `ROW_EXPO`-free mpfr `GSO.Mat` construction
   `ADJUDICATION.md` validated (`FPLLL.set_precision(N)` before `GSO.Mat`
   construction; `GSO.Mat(A, float_type="mpfr")`, no `flags=GSO.ROW_EXPO`;
   `M.update_gso()`; `LLL.Reduction(M, flags=LLL.DEFAULT)`; call
   `lll_obj()` directly, not wrapped in `BKZReduction`). 1-bit-resolution
   binary search PER BASIS, both endpoints (69 bits known failing, 100 bits
   known succeeding, per CTRL-1) re-confirmed as trials before bisecting,
   matching `TASK-20260815-6e4c02`'s own `bisect_precision_d512()` design
   (reused directly, not reinvented). Cap EACH basis's own bisection at
   `BISECTION_D512B_BUDGET_SECONDS=3600s` total (unchanged from
   `TASK-20260815-6e4c02`'s own precedent, comfortably above the ~2770s
   worst case at this narrower window -- see `dispatch_queue.json`'s own
   `budget_justification`); if either cannot resolve, report `NOT_COMPUTED:
   bisection budget exhausted` for THAT basis honestly and disclose the
   fallback precision used for its own reattempt -- never presented as a
   determined minimum.
2. **(b) Re-attempt EACH of those two cells' own full BKZ tour at ITS OWN
   newly-bisected precision** (not the beta=40-borrowed 69 bits), using the
   exact corrected construction `TASK-20260815-6e4c02`'s own
   `worker_main_cell()` already validates (`GSO.Mat` -> `LLL.Reduction` ->
   `BKZReduction(L)`, reused directly, not reinvented). Cap each cell
   individually at **`PER_BASIS_FEASIBILITY_CAP_V3=14400s`** (4 hours) --
   REUSED, EXPLICITLY DISCLOSED, NOT SILENTLY COPIED FORWARD: the prior
   batch's own Red Team COST-3 found this cap "adequate-and-untested-as-
   binding, not adequate-and-validated-as-binding" (no cell has yet hit it;
   every failure to date has been a hard `ReductionError` exception, not a
   timeout). This task's own `dispatch_queue.json` `budget_justification`
   states this choice explicitly rather than copying it forward silently, as
   this task's own next_action requires. A cell exceeding the cap is
   `NOT_COMPUTED: exceeded PER_BASIS_FEASIBILITY_CAP_V3`, never retried at a
   different parameter.
3. **(c) Do NOT re-attempt `(d=512, beta=40)`.** Already properly
   calibrated and reattempted in `BATCH-279acb` (0/1, a deeper failure
   site, a fourth recurrence of `KN-FIND-f54a82`'s own pattern) -- not to be
   silently repeated without a new, stated reason. None is stated here.
4. **(d) Report real per-cell wall-clock/tours/delta, or `NOT_COMPUTED`
   honestly** -- no fabricated or estimated figure presented as measured,
   for either phase, at either basis.
5. **(e) This task does NOT resolve the Red Team's own CTRL-3 caveat.**
   Even a properly, individually calibrated ISOLATED-STEP precision is not
   guaranteed to clear the full tour: `OBJ-2`/`KN-FIND-f54a82`'s own
   isolated-step-vs-full-tour permissiveness pattern already recurred a
   FOURTH time at `(d=512, beta=40)` itself in `BATCH-279acb`, at its own
   correctly-bisected precision. A fully decisive control would eventually
   need to bisect precision AT THE FULL-TOUR LEVEL directly (running
   `bkz(par, tracer=True)` itself at increasing precision until it
   completes or the cap is reached, for each cell) -- named here explicitly
   as a further, more expensive, LATER step this task does NOT attempt, not
   this follow-up's own job.
6. **(f) Do NOT address `(d=256, beta=55)` or `(d=256, beta=70)`.** Still
   the open question named in `EV-MLKEM-098182`'s own `unresolved_confounds`
   -- still out of scope, left for a later, separately-scoped follow-up.

## What it does not do

Does not touch `TASK-20260815-6e4c02`'s own committed
`stage0_d512_precision_bisection_and_reattempt.py` or any of its artifacts
(immutable run record). Does not touch `H-MLKEM-7d9bcc.yaml`,
`EXP-MLKEM-42ea04/specification.yaml`, `EV-MLKEM-e4189c.yaml`,
`DEC-20260815-201633.yaml`, `EV-MLKEM-098182.yaml`, `DEC-20260814-8ec2e5.yaml`,
`KN-FIND-ead2ac.md`, `KN-FIND-f54a82.md`, or any file under `BATCH-279acb/`
or `BATCH-d1a736/` -- all frozen/filed, binding-carried by reference only.
Does not attempt or characterize `(d=256, beta=55)` or `(d=256, beta=70)` in
any way. Does not run PREREG-8's own Stage 1 (no `>=8`-draw grid, no
`2^20`+ target generation, no NULL-1/2/3/SENS controls). Does not change
`H-MLKEM-7d9bcc`'s status (stays `proposed`) or `EXP-MLKEM-42ea04`'s
(`review_required`, `approved_by: null`). Does not make any C1/C2 statement,
in either direction -- PREREG-8 section 4.3 item 1's own `FORBIDS` clause is
honoured regardless of this task's own outcome. Does not perform a
full-tour-level precision search (CTRL-3's costlier half) -- named
explicitly above as a further, later step. Does not recommend a Stage-1
sizing decision or an escalation-branch determination -- both remain a
later, separate Coordinator act. Does not authorize any claim about ML-KEM
security.

## Execution boundary

Implementation and real execution **are authorized** for this task --
`DEC-20260815-201633`'s own `next_actions` explicitly commissions it.
Budget: `maximum_runs=1` (one script, two bases, each with its own
bisection-then-reattempt phase pair, run once); `wall_clock_seconds=37200`
(10h20m: 2 x 3600s per-basis bisection + 2 x 14400s per-cell reattempt +
600s write buffer, rounded up), backstopped by an outer OS-level `timeout`
at 37260s; `memory_gb=16` (unchanged -- same construction, same dimension,
peak RSS observed to date at d=512 is ~140MB). Full sizing arithmetic and
its reasoning are in `dispatch_queue.json`'s own `budget_justification`
field for this task, not restated here to avoid drift between the two
records.

## Invalidation triggers

Any of the following invalidates this task's own result and must be
disclosed, not silently absorbed: the `(d=512, beta=55)` isolated-step
control failing to reproduce `ERROR` at 69 bits / `COMPLETED` at 100 bits
with `seed_used=452658293`; the `(d=512, beta=70)` isolated-step control
failing to reproduce `ERROR` at 69 bits / `COMPLETED` at 100 bits with
`seed_used=915347894`; the construction deviating from the validated
`ROW_EXPO`-free mpfr shape at either basis; `SEED_ROOT != 715923` or a
seed-formula deviation; a fallback precision reported as if it were a
determined minimum, at either basis; any C1/C2 or ML-KEM-security statement;
`(d=512, beta=40)` re-attempted without a new, stated reason; any attempt at
`(d=256, beta=55)` or `(d=256, beta=70)`; a full-tour-level precision search
performed (CTRL-3's costlier half, explicitly out of this task's own scope);
any hypothesis/experiment status change; any Stage-1 activity; any
fabricated, estimated, or unmeasured figure presented as measured. Full list
in `dispatch_queue.json`'s own `invalidation_triggers` field for this task.

## Next steps after this task completes

1. A Coordinator-only snapshot archive (`TASK-20260815-02b01b`, matching
   `TASK-20260815-af296c`'s own precedent) commits this task's own artifacts
   alone, before either review reads them.
2. Independent Validator (`TASK-20260815-57bc79`) and Red Team
   (`TASK-20260815-19c716`) tasks (review-adversarial, xhigh effort) verify
   each basis's own bisection and reattempt independently.
3. A Coordinator ledger archive (`TASK-20260815-fa0ead`, pre-bound to
   minted/verified `EV-MLKEM-6edf0e` / `DEC-20260815-3e8e9c`), carrying
   whatever `EV-*`/`DEC-*` the outcome warrants, decides -- explicitly, not
   by default -- whether either or both cells cleared, whether the named
   escalation branches (upstream fplll bug report, alternate build/version,
   or a scoped-down dimension) are now ripe, or whether a cleared cell now
   sizes a Stage-1 dispatch.

## Binding carries (not re-litigated by this task)

`PREREG-8` in full; `DEC-20260814-4ac30a`; `DEC-20260814-8ec2e5`;
`EV-MLKEM-e4189c`; `DEC-20260815-201633`; `KN-FIND-ead2ac`;
`KN-FIND-f54a82`. The exact `ROW_EXPO`-free, mpfr construction shape every
prior batch in this goal's history has validated. `SEED_ROOT=715923` and the
full seed formula, unchanged. No Branch-B hand-rolled BKZ substitute. Claim
tier stays TOY. `H-MLKEM-7d9bcc` stays `proposed` and `EXP-MLKEM-42ea04`
stays `review_required`/`approved_by: null` until this follow-up's own
results are reviewed and archived.

## Artifact

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/TASK-20260815-f14d3c/task_card.md
