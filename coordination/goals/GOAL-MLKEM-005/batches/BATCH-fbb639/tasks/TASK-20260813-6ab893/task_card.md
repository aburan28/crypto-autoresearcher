# TASK-20260813-6ab893 — Red-team the two-route measurement

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            red-team
    policy          review-adversarial                 effort xhigh
    state           not_started
    depends_on      TASK-20260813-7b3039, TASK-20260813-7ac7cd
    review_required false
    archived_by     the ledger archive (id pending, G-5)
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Attack the measurement at its declared weak points: whether the `L7`
`ROUTE-I` (`BATCH-4ed139`'s P-L1 rider) is genuinely a **second** route or
shares code with the primary pipeline in a way that would make the comparison
vacuous; whether `results_am4.json` is correctly included or excluded for
`L9`/`L11`; whether the `rawtail` `ROUTE-W` proxy is ever silently folded into
the substantive tally instead of reported and excluded; whether the
termination clause's precedence (a single `SOME-EXCEEDS` cell dominates
`ALL-CLEAR`) was applied correctly. Builds at least one probe, including a
calibration control using a candidate with a genuinely near-zero true route
disagreement (e.g. `rdet`, in `A-1`'s own scope) to show what a disagreement
"floor" looks like.

## Deliverables

    reviews/TASK-20260813-6ab893/red_team_report.md
    reviews/TASK-20260813-6ab893/probes/*  (every probe listed explicitly in
                                             the report — declared gap G-1)

## Independent session, commits nothing

Report and probes sit uncommitted across a dispatch window (`PD-4`, open)
until the ledger archive commits them.
