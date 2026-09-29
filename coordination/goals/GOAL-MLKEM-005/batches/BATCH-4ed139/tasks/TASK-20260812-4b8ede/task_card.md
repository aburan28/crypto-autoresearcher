# TASK-20260812-4b8ede — RIDER (ii): the false-refusal control

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           executor
    policy         executor-implementation      effort medium
    state          queued
    depends_on     TASK-20260812-b581a8   (the LEAD'S SNAPSHOT — gated)
    review_required false  (archival-lifecycle flag ONLY — it governs which
                            archive kind must succeed this task, NOT whether it
                            is reviewed. Both reviews depend on it.)
    archived_by    TASK-20260812-b53c2f  (rider snapshot, runs alone, PRECEDES
                            both reviews. Queue gap G-2, closed.)
    budget         3600 s session, 4 GB, 1 run — MEASUREMENT CAPPED AT 600 s
    claim tier     TOY

## The candidate — DEFINED BY THE COORDINATOR IN PREREG-1 §§2.4 and 8.2

    X_gso_k(B) = (1/k) * sum_{j=1..k} log ||b*_j||     over the RAW basis,
                                                       frozen row order

    declared arguments: d, k, q, the raw GSO profile — AND NO BETA
    routes: RQ (QR of B^T, log|R_jj|) and RG (Cholesky of B B^T, log diagonal)

**Informative by construction:** it reads the leading k Gram–Schmidt norms,
which depend on the entries of `A`.
**Structurally refused:** it takes no beta argument, so at fixed `(d,k)` it is
constant across the beta grid and `rho = 0` exactly at G-REL1 — it fails REL-1
**by algebra**, exactly as `rdet` and `lam1n` do.

Introducing a candidate observable is a Coordinator and Idea Generator act, which
is why the wave-2 Red Team correctly declined to do it. **Do not redefine it.**

## Objective

Build the false-refusal control both waves leave owed and only wave 2 names, and
score it through (a) the gate's own committed G-REL1 code path and (b) G-VAR2 as
frozen in PREREG-1 §3.

## The two halves, both demonstrated and neither asserted

* **Informativeness**: report `X_gso_k`'s between-basis dispersion over the 8
  frozen bases at every lattice, and show it varies with `A`.
* **Refusal**: push it through the producer's committed G-REL1 scoring, report
  `rho` at every lattice at both normalizations with `s_X/|X|` beside each,
  confirm or refute `rho = 0` exactly.

`P-FR1`: refused by G-REL1 **and** admitted by G-VAR2 (`scale_degenerate` on
VAR-S because it is beta-free, PASS on VAR-F). Falsifier: either half failing.

## The result that would be worth more than the intended one

**If G-VAR2 also refuses `X_gso_k`, say so loudly.** That would mean the
degenerate-scale rule of PREREG-1 §3.2 is doing the refusing while the fibre
clause is decorative — a defect in the instrument. PREREG-1 §3.2 names
`X_gso_k` as the discriminating case in advance.

## The bound on the claim, frozen in advance

This is **ONE CONSTRUCTED INSTANCE, n = 1**. It narrows DEC-20260812-7c4a1e
C-2(b) from "the refusal side is untested in either direction" to "the refusal
side has one constructed instance of a false refusal". **IT DOES NOT MEASURE A
FALSE-REFUSAL RATE** and no rate may be reported, estimated or implied. A rate
needs a population and a sampling scheme and this batch has neither.

## Artifacts — SEVEN PATHS, AND WRITE NOTHING ELSE

    measure_falserefusal.py  results_falserefusal.json  report_falserefusal.md
    command.txt  stdout.log  stderr.log  run_manifest.yaml

`report_falserefusal.md` lists every path written.

## Bounds

Minutes of numpy; one QR and one Cholesky per basis; **no reduction at all**, so
all ten lattices are in scope. Name both could-not-fail arrangements before
running and show you are in neither. COMMIT NOTHING. CLAIM TIER TOY.
