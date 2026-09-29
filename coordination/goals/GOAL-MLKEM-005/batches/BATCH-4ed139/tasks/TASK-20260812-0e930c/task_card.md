# TASK-20260812-0e930c — RIDER (iii): fpylll-equipped L7/L8 replication

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           executor
    policy         executor-implementation      effort medium
    state          queued
    depends_on     TASK-20260812-b581a8   (the LEAD'S SNAPSHOT — gated)
    review_required false  (archival-lifecycle flag ONLY — it governs which
                            archive kind must succeed this task, NOT whether it
                            is reviewed. Both reviews depend on it.)
    archived_by    TASK-20260812-b53c2f  (rider snapshot, runs alone, PRECEDES
                            both reviews. An INFRASTRUCTURE outcome here is
                            still archived, and archived as one.)
    budget         3600 s session, 4 GB, 1 run — 1200 s CAP INCLUDING THE INSTALL
    claim tier     TOY

## Objective

Install fpylll pinned at **0.6.4** and re-measure the **L7/L8 arm** — the 8
frozen bases at `d = 20`, the frozen beta grid `{5, 10, 15}`, HKZ through the
frozen pipeline — reproducing the committed per-basis `hkz` and `lam1n` values of
`results_relvar.json` and reporting the max absolute deviation.

`P-L1`: reproduces to 6 decimals. Falsifier: max absolute deviation above 1e-6.

## THE FRAMING IS FROZEN AND GOES IN THE REPORT'S OWN OPENING

This **RESTORES THE COVERAGE WAVE 2 LOST** and is **NEVER** to be presented as
resolving a doubt, **there being none to resolve**. fpylll's absence in both
wave-2 sessions is **INFRASTRUCTURE SIGNAL** and was never evidence against
`lam1n`, `hkz`, the 48 reductions or their reported max `hkz_violation` of 0.0.

The honest position it improves on, from DEC-20260812-7c4a1e: the
reduction-dependent quantities currently have **one re-execution** (wave 1,
through the producer's own code on the producer's own machine, which cannot catch
a specification error) and **zero independent re-implementations** in either
wave.

## AM-9, applied and stated

**fpylll's `k` counts the q-scaled rows, NOT the identity block.** Show the row
count you passed and why.

## Environment — record it in full

Platform, python, numpy, scipy, fpylll. This is exactly what the BATCH-cbe023
Red Team's environment record lacked, and it is why the **"genuinely
cross-platform"** reading of the L7/L8 agreement is **NOT CITABLE**. Report
whether this run differs from the producer's `python 3.11.15 / numpy 2.4.6 /
scipy 1.17.1` stack **as measured**, and make no cross-platform claim unless the
environments actually differ and both are recorded. The citable form is a
**PORTABILITY** result across three textually distinct implementations.

## If the install fails or the reduction times out

**INFRASTRUCTURE SIGNAL.** Emit all seven artifacts declaring the failure with
its exact error, claim nothing, and do not report a deviation that was never
measured. It is not a negative result about anything.

## Artifacts — SEVEN PATHS, AND WRITE NOTHING ELSE IN THE REPOSITORY

    replicate_l7l8.py  results_l7l8.json  report_l7l8.md
    command.txt  stdout.log  stderr.log  run_manifest.yaml

`report_l7l8.md` lists every path written. **The fpylll install goes OUTSIDE the
repository** (a virtualenv under a scratch path); record the exact install
command and the resolved version in `command.txt` and in the manifest.

## Bounds

One install plus about 20 s of reduction at `d = 20`. `d <= 40` throughout; no
new reduction beyond the frozen HKZ pipeline; L1/L2 and L4/L5 are out of scope.
COMMIT NOTHING. Install nothing into the repository. CLAIM TIER TOY.
