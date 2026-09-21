# TASK-20260813-7930a6 — INDEPENDENT RED TEAM

    goal / batch    GOAL-MLKEM-005 / BATCH-6e08fe
    role            red-team
    policy          review-adversarial                 effort xhigh
    state           queued
    depends_on      TASK-20260813-ea2e96, TASK-20260813-2d6b5e
    review_required false
    archived_by     PENDING (ledger archive)
    independent_session_required true
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## Primary target — attack the independence claim itself, don't take it on faith

This whole batch exists because the LAST batch's "independent route" turned
out not to be independent. Do not repeat that failure by trusting this
batch's own claim of independence. **BUILD, don't propose**: pick at least
one function in the lead's committed `measure_route_reimpl.py` and show,
line by line, either that it could not plausibly derive from `make_A`/
`build_basis`/`hkz_profile` (report the diff), or that it in fact does
(report that as a CRITICAL finding — this batch would then have reproduced
its own predecessor's defect).

## Second target — the ROUTE-P exclusion discipline

Confirm, by reading the lead's script and `results_route_reimpl.json`
directly, that `results_l7l8.json` and `results_am4.json` were NEVER used as
a source of `ROUTE-P` values (`PREREG-4` §2.1 bars both explicitly, since
both are `ROUTE-I`-family code-shared artifacts under F-1/RT-1) — only
`results_relvar.json`'s own `G_REL1` per-basis array.

## Third target — the coverage claim

Independently determine which of the 18 cells genuinely have `ROUTE-P`
per-basis ground truth in `results_relvar.json`'s `G_REL1` block (build a
probe rather than trust the lead's obligation-0 table), specifically
checking whether any middle-beta cell (`L7 b10`, `L9 b15`, `L11 b20`) has
per-basis data this Coordinator's and the lead's own reads may have missed.

## Fourth target — the termination clause and the revisit condition

Check the termination-branch precedence was applied correctly and that, if
`T-INDVERIFY-ARTIFACT` fired at any cell, the revisit condition (`PREREG-4`
§2.8) is stated with the exact cell(s) named, not diluted into a vague
caveat.

## Built control, not proposed

At least one null or nearby-object control, BUILT: e.g. independently
recompute `rdet` (in `A-1`'s scope, algebraically forced to zero dispersion)
at one matched cell using the lead's own declared implementation choice, to
calibrate what a genuinely independent route's residual floor looks like on
a candidate with a KNOWN answer, before trusting the residual floor reported
for `lam1n`/`hkz`.

## Discipline

State the cheapest falsification of every headline with its cost. Where a
measurement goes against your own thesis, report it at the same weight as
your objections. INDEPENDENT SESSION. COMMIT NOTHING. Do not restate
`KN-FIND-7d098b`, `KN-FIND-9d44b4` or `KN-FIND-9b5df0` as new. CLAIM TIER
STAYS TOY. `knowledge/INDEX.md` must not be written, regenerated or staged.
A timeout, crash or missing dependency is INFRASTRUCTURE SIGNAL, never
negative mathematical evidence.

## Artifacts (extended per G-1 before the ledger archive stages)

    reviews/TASK-20260813-7930a6/red_team_report.md
    reviews/TASK-20260813-7930a6/probes/...   (at least one BUILT, re-executable probe)
