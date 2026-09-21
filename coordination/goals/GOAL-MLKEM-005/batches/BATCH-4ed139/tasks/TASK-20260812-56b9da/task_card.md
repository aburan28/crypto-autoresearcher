# TASK-20260812-56b9da — THE LEAD PRODUCER: implement, validate and score G-VAR2

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           executor
    policy         executor-implementation      effort medium
    state          queued
    depends_on     TASK-20260812-1ed548  (the notarizing commit MUST exist first)
    review_required true
    archived_by    TASK-20260812-b581a8
    budget         5400 s session, 4 GB, 1 run — MEASUREMENT CAPPED AT 600 s
    claim tier     TOY

## The three obligations, verbatim from the goal's single next_action

**(a) IMPLEMENT G-VAR2 per AM-16 (a)(b)(c)** — scaled between-basis dispersion
measured against the candidate's OWN between-cell range at fixed (d, k),
reported as a per-cell **PROFILE** and never as an all-cells Boolean, with every
candidate scored through **at least two declared arithmetic routes** and the
route recorded beside each value.

**(b) VALIDATE IT AGAINST BOTH FIXTURES per AM-17(b)** — the six arithmetic
routes of `probe_nullroute.py` in family **F0** (all six routes to `X_null` and
to `rdet` REFUSED; `lam1n` / `hkz` / `rawtail` ADMITTED, target behaviour
declared in its own committed output in advance) **AND** the nearby family
**F1** of `probe_gvar_family.py` (`X_null` and `rdet` REFUSED there too) — with
the **fibre clause** of AM-17(c) written into the criterion and the family
declared as part of it per AM-17(d).

**(c) SCORE V_evade** (`X_null + 1e-9 * A[0,0]/q`) through the same criterion and
report whether the pre-registered prediction of DEC-20260812-7c4a1e holds —
that a scaled criterion REFUSES V_evade, its between-basis float sd of 3.91e-10
being negligible against a between-cell range of order 1 — or is falsified.

## The specification is PREREG-1, not this card

Everything above is frozen in
`tasks/TASK-20260812-34b86c/prereg.md`: the criterion (§3), the degenerate-scale
rule with both readings (§3.2), the fibre clause (§3.3), `tau_var = 1e-3` and its
basis (§3.4), the two fixtures' declared target behaviour (§4), the V_evade
prediction and its AM-15(a) classification (§5), the graded MUST-PASS guard and
the VOID row (§6.1), the could-not-fail arrangements in both directions
(§6.2–6.4), the three-way termination clause (§7), the prediction register (§9)
and the outcome rows (§10). **Do not re-derive any of it and do not amend it.**

## Artifacts — SEVEN PATHS, AND WRITE NOTHING ELSE IN THE REPOSITORY

    tasks/TASK-20260812-56b9da/measure_gvar2.py
    tasks/TASK-20260812-56b9da/results_gvar2.json
    tasks/TASK-20260812-56b9da/report_gvar2.md
    tasks/TASK-20260812-56b9da/command.txt
    tasks/TASK-20260812-56b9da/stdout.log
    tasks/TASK-20260812-56b9da/stderr.log
    tasks/TASK-20260812-56b9da/run_manifest.yaml

`report_gvar2.md` must **LIST EVERY PATH THIS TASK WROTE** inside the
repository. An undeclared committed file and a declared uncommitted file are the
two halves of defect D3 and both are terminal for an archive.

## Bounds

Seconds to low minutes. `d <= 40` for anything reduction-dependent. **No new
reduction beyond the frozen HKZ pipeline.** At `d in {100, 140}` the
reduction-dependent candidates are available only through route RC (committed
values) — a declared coverage limit, not a result.

## The single thing not to get wrong

**Read the termination branch off R2-OUT-1 and R2-OUT-2 under R2-OUT-V's
precedence, and nowhere else.** Name the branch, quote the PREREG-1 clause it
fires under, state what it licenses and forbids. Do not argue for a different
branch. Do not report a branch the numbers do not fire. If fpylll is absent or
anything times out or crashes, that is INFRASTRUCTURE SIGNAL, it forces the
`T-PARTIAL` suffix of PREREG-1 §7.4, and it is **never** a fixture failure.

## Binding carries

PREREG-1 §§11 and 11.1 in full, including the corrected citable range **4.87x to
31.03x** and the eleven non-citable phrases. CLAIM TIER TOY.
`knowledge/INDEX.md` is not written, regenerated or staged. COMMIT NOTHING.
