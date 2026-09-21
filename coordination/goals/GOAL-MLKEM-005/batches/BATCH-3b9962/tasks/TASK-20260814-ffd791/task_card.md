# TASK-20260814-ffd791 — LEAD PRODUCER, STAGE 0 ONLY

    goal / batch    GOAL-MLKEM-005 / BATCH-3b9962
    role            executor
    policy          executor-implementation            effort medium
    state           queued
    depends_on      TASK-20260814-518949 (notarization)
    review_required true (Validator + Red Team, review-adversarial, after this
                    task's own snapshot archive)
    budget          25200 s (7 hours), 16 GB, 1 run
    claim tier      TOY (PREREG-8's own frontmatter; unchanged by this task)

## What this task is for

Runs PREREG-8's own section 1 (infrastructure re-verification) and section 2
(Stage 0 feasibility benchmark) — nothing more. This is the FIRST batch in
GOAL-MLKEM-005's entire RQ-MLKEM-001 history to attempt real `fpylll` BKZ
lattice reduction, and PREREG-8's own section 6 budget is explicitly an
ESTIMATE with wide uncertainty until Stage 0 replaces it with a measured
number (section 2.1). This task performs exactly that replacement, at a
bounded, capped cost — it does NOT commit to or run PREREG-8's own Stage 1
(the full `>= 8`-draw measurement grid across up to 6 cells, section 3),
which stays a separate, later dispatch, sized from this task's own results.

## What it asks for

1. **Section 1, first, gating everything else.** Confirm `fpylll` installs
   and is callable with an explicit `block_size`; confirm the real CBD
   sampler and FIPS 203 `Compress_d`/`Decompress_d` match Table 2; confirm
   batched (BLAS/numpy) Babai reproduces exact scalar Babai on small,
   hand-checkable instances. If ANY of these fails, STOP — report
   `T-PROJNOISE-NODATA` for the whole package with the exact failure. No
   hand-rolled BKZ substitute is commissioned under any circumstance.
2. **Section 2, only if section 1 clears.** For each of the 6 `(d, beta)`
   cells (`d in {256, 512}` x `beta in {40, 55, 70}`), reduce exactly one
   basis, capped at `PER_BASIS_FEASIBILITY_CAP = 3600` s; record wall-clock,
   peak memory, tours, and the achieved root-Hermite factor `delta`. A cell
   that does not complete within the cap is `NOT_COMPUTED`, not retried at a
   different parameter. Independently, sweep the toy-floor `d in {8, 12, 16,
   20}` for `8f8f45`'s own exact-floor arm, capped at
   `TOY_FLOOR_FEASIBILITY_CAP = 900` s, selecting the largest `d` that
   completes.
3. **Report, don't decide.** State plainly which cells cleared and at what
   measured cost, or that every cell was dropped (firing
   `T-PROJNOISE-NODATA`). Recommend, but do not enact, how a later Stage-1
   dispatch should be sized from these numbers — that recommendation is
   input to a separate, later Coordinator act, not a decision this task
   makes.

## What it does not do

Does not run Stage 1 (no `>= 8`-draw grid, no `2^20`+ target generation, no
NULL-1/2/3/SENS controls). Does not change `H-MLKEM-7d9bcc`'s status (stays
`proposed`) or `EXP-MLKEM-42ea04`'s (`review_required`, `approved_by: null`
— running this task is not approval). Does not edit `prereg.md`,
`H-MLKEM-7d9bcc.yaml`, or `EXP-MLKEM-42ea04/specification.yaml` — all three
are frozen/filed. Does not authorize any claim about ML-KEM security.

## Next steps after this task completes

1. A Coordinator-only snapshot archive (new `TASK-*`, minted then) commits
   this task's own artifacts alone, before either review reads them.
2. Independent Validator and Red Team tasks (review-adversarial, xhigh
   effort) verify the section-1 checks and the Stage-0 measurements
   independently.
3. A Coordinator ledger archive, carrying whatever `EV-*`/`DEC-*` the
   outcome warrants, decides — explicitly, not by default — whether and how
   to size and dispatch PREREG-8's own Stage 1 in a subsequent batch.

## Artifact

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/tasks/TASK-20260814-ffd791/task_card.md
