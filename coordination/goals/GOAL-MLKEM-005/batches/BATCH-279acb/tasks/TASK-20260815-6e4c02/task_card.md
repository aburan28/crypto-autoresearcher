# TASK-20260815-6e4c02 -- d=512 precision bisection and decisive main-grid reattempt

    goal / batch    GOAL-MLKEM-005 / BATCH-279acb
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      none (BATCH-d1a736 is closed; DEC-20260814-8ec2e5 and
                    EV-MLKEM-098182 are already committed)
    review_required true (Validator + Red Team, review-adversarial, after
                    this task's own snapshot archive -- not yet dispatched)
    budget          48000 s (13h20m), 16 GB, 1 run
    claim tier      TOY (PREREG-8's own frontmatter; unchanged by this task)
    execution       IMPLEMENTATION AND EXECUTION ARE AUTHORIZED. This is a
                    real-compute task, not a zero-run design gate.

## What this task is for

Discharges `DEC-20260814-8ec2e5`'s own `next_actions` (section 12) in full.
`BATCH-d1a736` re-measured PREREG-8's 6 Stage-0 main-grid cells under the
corrected (`GSO.ROW_EXPO`-free, mpfr) construction at a precision (65 bits)
bisected ONLY at `(d=256, beta=40)`, and found 0/6 cells cleared. Two
independent reviews reconciled that outcome: the Validator's ART-9 shows the
bisected precision is insufficient for a full tour even at the exact cell it
was calibrated on; the Red Team's OBJ-1 -- a live, seed-identical, executed
control (`probes/probe1_bisection_generality.py`) -- shows the SAME 65-bit
precision fails outright at `(d=512, beta=40)`'s own isolated-LLL-step level
(the exact operation every d=512 main-grid cell's own traceback fails on),
while 100 bits succeeds there. `DEC-20260814-8ec2e5` declines to read the
0/6 outcome as licensing `DEC-20260814-4ac30a`'s own named escalation
branches (upstream fplll bug report, alternate build/version, or a
scoped-down dimension) until this decisive, strictly-cheaper follow-up is
run: does raising precision to a value ACTUALLY BISECTED AT d=512 let the
d=512 main-grid cells' own full BKZ tours clear?

This task performs exactly that measurement, at a bounded, explicitly
justified cost.

## What it asks for

1. **(a) Determine d=512's own minimum adequate isolated-LLL-step precision
   by a GENUINE bisection** -- not a 2-point bracket -- at `(d=512,
   beta=40)`, between 65 bits (known failing) and 100 bits (known
   succeeding, per the Red Team's own OBJ-1/CTRL-1 control,
   `seed_used=2074339090`). Reuse
   `coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe1_bisection_generality.py`'s
   own harness, construction, and seed-formula shape **directly**: same
   `SEED_ROOT=715923`, same `default_rng([SEED_ROOT, 0, d, beta, 0, 0])`
   formula, same `ROW_EXPO`-free mpfr `GSO.Mat` construction
   `ADJUDICATION.md` validated (`FPLLL.set_precision(N)` before
   `GSO.Mat` construction; `GSO.Mat(A, float_type="mpfr")`, no
   `flags=GSO.ROW_EXPO`; `M.update_gso()`; `LLL.Reduction(M,
   flags=LLL.DEFAULT)`; call `lll_obj()` directly, not wrapped in
   `BKZReduction`). 1-bit-resolution binary search, both endpoints
   re-confirmed as trials before bisecting (matching
   `TASK-20260814-534f80`'s own `bisect_precision()` design). Cap this
   phase at `BISECTION_D512_BUDGET_SECONDS=3600s` total; if it cannot
   resolve, report `NOT_COMPUTED: bisection budget exhausted` honestly and
   disclose the fallback precision used for step 2 -- never presented as a
   determined minimum.
2. **(b) Re-attempt at least the three currently-ERRORing d=512 main-grid
   cells'** (`beta in {40, 55, 70}`) **own full BKZ tours** at the
   precision step 1 determines, using the exact corrected construction
   `TASK-20260814-534f80`'s own `worker_main_cell()` already validates
   (`GSO.Mat` -> `LLL.Reduction` -> `BKZReduction(L)`, reused directly, not
   reinvented). Cap each cell individually at
   **`PER_BASIS_FEASIBILITY_CAP_V3=14400s`** (4 hours) -- **explicitly NOT**
   `PER_BASIS_FEASIBILITY_CAP_V2=7200s` copied forward unexamined. This
   task's own `budget_justification` (in `dispatch_queue.json`) discloses
   the reasoning in full: `PER_BASIS_FEASIBILITY_CAP_V2` was sized against
   65-bit-precision trials, and this task's cells run at a higher,
   dimension-appropriate precision whose real per-operation cost is
   unmeasured (plausibly crossing a 64-bit mpfr limb boundary at 129 bits);
   separately, d=512 is 2x d=256's own dimension, and d=256's own measured
   full-tour costs (223.4s-626.5s before erroring, one cell exhausting the
   full 7200s cap) are the only full-tour data this goal has to scale from.
   A cell exceeding the cap is `NOT_COMPUTED: exceeded
   PER_BASIS_FEASIBILITY_CAP_V3`, never retried at a different parameter.
3. **(c) Report real per-cell wall-clock/tours/delta, or `NOT_COMPUTED`
   honestly** -- no fabricated or estimated figure presented as measured,
   for either phase.
4. **(d) Do NOT address `(d=256, beta=55)` or `(d=256, beta=70)`.** These
   remain the open question named in `EV-MLKEM-098182`'s own
   `unresolved_confounds` -- explicitly out of scope for this task, named
   here so it is not silently folded in or silently dropped. A later,
   separately-scoped follow-up addresses them.

## What it does not do

Does not touch `TASK-20260814-534f80`'s own committed
`stage0_v2_feasibility.py` or any of its artifacts (immutable run record).
Does not touch `H-MLKEM-7d9bcc.yaml`, `EXP-MLKEM-42ea04/specification.yaml`,
`EV-MLKEM-098182.yaml`, `DEC-20260814-8ec2e5.yaml`, or any file under
`BATCH-d1a736/` -- all frozen/filed, binding-carried by reference only. Does
not attempt or characterize `(d=256, beta=55)` or `(d=256, beta=70)` in any
way. Does not run PREREG-8's own Stage 1 (no `>=8`-draw grid, no `2^20`+
target generation, no NULL-1/2/3/SENS controls). Does not change
`H-MLKEM-7d9bcc`'s status (stays `proposed`) or `EXP-MLKEM-42ea04`'s
(`review_required`, `approved_by: null`). Does not make any C1/C2 statement,
in either direction -- PREREG-8 section 4.3 item 1's own `FORBIDS` clause is
honoured regardless of this task's own outcome. Does not recommend a Stage-1
sizing decision or an escalation-branch determination -- both remain a
later, separate Coordinator act. Does not authorize any claim about ML-KEM
security.

## Execution boundary

Implementation and real execution **are authorized** for this task --
`DEC-20260814-8ec2e5`'s own `next_actions` explicitly commissions it. Budget:
`maximum_runs=1` (one script, two phases, run once); `wall_clock_seconds
=48000` (13h20m: 3600s bisection + 43200s worst-case for 3 reattempted
cells at 14400s each + 600s write buffer, rounded up), backstopped by an
outer OS-level `timeout` at 48060s; `memory_gb=16`. Full sizing arithmetic
and its reasoning are in `dispatch_queue.json`'s own `budget_justification`
field for this task, not restated here to avoid drift between the two
records.

## Invalidation triggers

Any of the following invalidates this task's own result and must be
disclosed, not silently absorbed: the `(d=512, beta=40)` isolated-step
control failing to reproduce ERROR at 65 bits / COMPLETED at 100 bits with
`seed_used=2074339090`; the construction deviating from the validated
ROW_EXPO-free mpfr shape; `SEED_ROOT != 715923` or a seed-formula deviation;
a fallback precision reported as if it were a determined minimum; any C1/C2
or ML-KEM-security statement; any attempt at `(d=256, beta=55)` or `(d=256,
beta=70)`; any hypothesis/experiment status change; any Stage-1 activity;
any fabricated, estimated, or unmeasured figure presented as measured. Full
list in `dispatch_queue.json`'s own `invalidation_triggers` field for this
task.

## Next steps after this task completes

1. A Coordinator-only snapshot archive (task ID minted then, matching
   `TASK-20260814-cfa812`'s own precedent) commits this task's own
   artifacts alone, before either review reads them.
2. Independent Validator and Red Team tasks (review-adversarial, xhigh
   effort) verify the bisection and the reattempt independently.
3. A Coordinator ledger archive, carrying whatever `EV-*`/`DEC-*` the
   outcome warrants, decides -- explicitly, not by default -- whether the
   named escalation branches (upstream fplll bug report, alternate
   build/version, or a scoped-down dimension) are now ripe, or whether at
   least one cleared d=512 cell now sizes a Stage-1 dispatch and revisits
   the knowledge-promotion deferral `DEC-20260814-8ec2e5.knowledge_promotion`
   names.

## Binding carries (not re-litigated by this task)

`PREREG-8` in full; `DEC-20260814-4ac30a`; `EV-MLKEM-098182`;
`DEC-20260814-8ec2e5`; `KN-FIND-f54a82`. The exact `ROW_EXPO`-free, mpfr
construction shape both `BATCH-d1a736`'s Validator and the original
`BATCH-3b9962` adjudication validated. `SEED_ROOT=715923` and the full seed
formula, unchanged. No Branch-B hand-rolled BKZ substitute. Claim tier stays
TOY. `H-MLKEM-7d9bcc` stays `proposed` and `EXP-MLKEM-42ea04` stays
`review_required`/`approved_by: null` until this follow-up's own results are
reviewed and archived.

## Artifact

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/tasks/TASK-20260815-6e4c02/task_card.md
