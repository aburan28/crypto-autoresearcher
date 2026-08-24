# TASK-20260813-451a6d — Independent validation

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            validator
    policy          review-adversarial                 effort xhigh
    state           not_started
    depends_on      TASK-20260813-7b3039, TASK-20260813-7ac7cd
    review_required false
    archived_by     the ledger archive (id pending, G-5)
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Independently re-derive the coverage audit (which of the 27 cells have a
genuine `ROUTE-I`), the per-cell `D_route`/`s_c^fib` comparison, the aggregate
verdict, and the termination branch — from `PREREG-3`'s frozen text, reading
the same committed corpus files itself, **without importing the producer's
module**. Runs its own verdict on `results_am4.json`'s construction
comparability. Confirms RC-1/RC-2 were carried verbatim and that no reduction
was performed anywhere. Runs the git-plumbing change-set-equality check on
both archive commits of this batch, exactly as this goal's every prior
validation has.

## Deliverables

    reviews/TASK-20260813-451a6d/validation_report.yaml
    reviews/TASK-20260813-451a6d/probes/*  (every probe listed explicitly in
                                             the report — declared gap G-1)

## Independent session, commits nothing

Report and probes sit uncommitted across a dispatch window (`PD-4`, open and
inherited) until the ledger archive commits them.
