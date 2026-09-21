# TASK-20260813-7b3039 — THE LEAD PRODUCER

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            executor
    policy          executor-implementation            effort medium
    state           not_started
    depends_on      TASK-20260813-6ad846
    review_required true
    archived_by     TASK-20260813-7ac7cd
    budget          1800 s cap, HARD 600 s measurement cap, 2 GB, 1 run
    claim tier      TOY

## What it must do, in order

**(a)** Carry `PREREG-3` §1's frozen RC-1 correction verbatim into
`report_c3lane.md` — the headline is **1,313**, not 1,416. No recomputation.

**(b)** Carry `PREREG-3` §2's frozen RC-2 correction verbatim — `P-A12a`'s
committed `OUTCOME` was, and always was, `FALSIFIED`. No recomputation, no
edit to any immutable prior artifact.

**(c)** Run `PREREG-3` §3's coverage-audited two-route measurement:
**obligation 0** (coverage audit over 27 cells — `lam1n`/`hkz`/`rawtail` x
`L7`/`L9`/`L11` x each lattice's own beta grid — reading `results_relvar.json`,
`results_l7l8.json`, `results_am4.json`, and reporting the `results_am4.json`
construction-comparability verdict explicitly either way); **obligation 1**
(per covered cell: `D_route` = max absolute route disagreement, `s_c^fib` =
already-archived fibre dispersion, verdict `EXCEEDS`/`DOES NOT EXCEED`, ties
resolved to `DOES NOT EXCEED`); **obligation 2** (aggregate `ALL-CLEAR` /
`SOME-EXCEEDS` over the covered set, with coverage fraction). Read off the
termination branch (`T-C3LANE-NODATA` / `-OBSTRUCTED` / `-OPEN`, `-PARTIAL`
suffix as required) under `PREREG-3` §3.5's frozen precedence.

## Absolute constraint

**NO REDUCTION OF ANY KIND, ANYWHERE, AT ANY LATTICE.** This task reads
already-committed files and does elementary arithmetic (max, absolute
difference, comparison) on numbers read that way. `fpylll` is never imported
or installed by this task.

## Artifacts — SEVEN PATHS

    tasks/TASK-20260813-7b3039/measure_c3lane.py
    tasks/TASK-20260813-7b3039/results_c3lane.json
    tasks/TASK-20260813-7b3039/report_c3lane.md
    tasks/TASK-20260813-7b3039/command.txt
    tasks/TASK-20260813-7b3039/stdout.log
    tasks/TASK-20260813-7b3039/stderr.log
    tasks/TASK-20260813-7b3039/run_manifest.yaml

`report_c3lane.md` must list every path this task wrote, exactly as this
goal's every prior lead producer has done, so the snapshot archive's
change-set-equality check is verifiable.
