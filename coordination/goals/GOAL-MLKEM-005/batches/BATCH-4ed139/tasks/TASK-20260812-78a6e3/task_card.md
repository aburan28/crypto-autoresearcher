# TASK-20260812-78a6e3 — RIDER (i): the C-1 resolving tabulation

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           executor
    policy         executor-implementation      effort medium
    state          queued
    depends_on     TASK-20260812-b581a8   (the LEAD'S SNAPSHOT — gated so this
                                           cannot displace the lead)
    review_required false  (archival-lifecycle flag ONLY — it governs which
                            archive kind must succeed this task, NOT whether it
                            is reviewed. Both reviews depend on it, and the
                            Validator must RE-DERIVE this tabulation
                            INDEPENDENTLY.)
    archived_by    TASK-20260812-b53c2f  (rider snapshot, runs alone, PRECEDES
                            both reviews — so this task's artifacts are read
                            COMMITTED. Queue gap G-2, closed.)
    budget         3600 s session, 2 GB, 1 run — MEASUREMENT CAPPED AT 120 s
    claim tier     TOY

## Objective

Settle a **direct numeric contradiction** between the two review waves'
validators, who re-derived the same quantity from the same immutable file and
reported incompatible answers.

    wave 1 (TASK-20260809-3f1dc4 F-1): "15 of the 19 G-REL2 cells fall BELOW
      the stated lower bound of 6x" — thirteen at exactly 5.71x, one at 4.97x.
    wave 2 (TASK-20260812-da8c3b F-1): "TWO entries fall below 6x" out of all
      29 X_null G-REL entries, at 0.486626 (4.87x) and 0.496557 (4.97x),
      "at the mean-over-8 reading".

## The work

Tabulate the **19 G-REL2** and **10 G-REL1** `X_null` criterion values out of the
committed `results_relvar.json` under **all three declared readings** — legacy
`i = 0`, count of passing bases, mean over 8 — and publish the **multiset with
the reading beside each**.

Per reading report: min with its location, max with its location, and the count
below 6x **separately over the 19 G-REL2 cells, over the 10 G-REL1 lattices, and
over all 29 entries** — the two waves counted over different denominators and
that may be the whole explanation. Report whether any entry sits at exactly
5.71x. Note before looking that `1 - k/(d-k) = 0.5714...` for `(d,k) = (100,30)`,
so that value is **structurally available** in this family and wave 1's figure is
not obviously a typo.

## Artifacts — SEVEN PATHS, AND WRITE NOTHING ELSE

    tabulate_c1res.py  results_c1res.json  report_c1res.md
    command.txt  stdout.log  stderr.log  run_manifest.yaml

`report_c1res.md` lists every path written.

## What this rider resolves and what it does not

It resolves a **CITATION BLOCK**, not a dispute about competence. Do not declare
either validator wrong beyond what the tabulation shows. Until the Coordinator
rules on this tabulation in the batch decision, **NEITHER COUNT IS CITABLE** —
and **"a factor of 6 to 31" remains FALSE and uncitable regardless**. The
corrected range **4.87x to 31.03x** and the minimum **0.486626** at G-REL2
L1/L2 beta 15 are agreed, two-wave replicated and binding; re-derive them and
confirm or contradict, and if contradicted say so plainly.

## Bounds

Seconds of Python on a committed file, pinned by sha256 and **never edited**.
No reduction, no fpylll, no basis rebuild. COMMIT NOTHING.
