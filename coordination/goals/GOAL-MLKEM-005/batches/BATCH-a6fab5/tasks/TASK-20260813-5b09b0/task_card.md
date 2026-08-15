# TASK-20260813-5b09b0 — INDEPENDENT RED TEAM

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    role            red-team
    policy          review-adversarial                 effort xhigh
    state           queued
    depends_on      TASK-20260813-c0ec71, TASK-20260813-861a58
    review_required false
    archived_by     PENDING (ledger archive)
    independent_session_required true
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## Primary target — attack the independence AND fidelity claims, don't take
## either on faith

This batch exists because `BATCH-6e08fe`'s independent route turned out to
be independent but NOT fidelity-matched. Do not repeat that failure at one
remove by trusting this batch's own claim to have fixed it. **BUILD, don't
propose**: (a) diff the lead's reduction/enumeration code against the barred
lineage AND against `BATCH-6e08fe`'s own `measure_route_reimpl.py` — report a
CRITICAL finding if either is transcribed; (b) if Branch A (fpylll) was
declared, independently confirm the actual API sequence used genuinely
performs BKZ at `block_size = d` (not LLL under a different name) by reading
the fpylll calls directly and, if budget allows, running a small
independent smoke test of your own; if Branch B was declared, confirm the
committed code genuinely implements BKZ, not merely LLL relabeled.

## Second target — independently re-verify the fpylll infrastructure signal

Attempt the identical `pip install fpylll` (+ `cysignals` if needed) /
`import fpylll` sequence `PREREG-5` §1 describes, IN THIS RED TEAM'S OWN
SESSION, and report your own result plainly — a third independent data point
on this environment fact, regardless of what the lead found.

## Third target — the coverage and ROUTE-P exclusion discipline

Confirm, by reading the lead's script and results directly, that
`results_l7l8.json` and `results_am4.json` were NEVER used as a source of
`ROUTE-P` values, and that genuine `ROUTE-P` per-basis ground truth exists at
all 6 named cells.

## Fourth target — the termination clause, the revisit condition, and the
## third-attempt boundary

Check the termination-branch precedence was applied correctly. If
`T-HKZINDEP-ARTIFACT` fired at any cell, confirm the revisit condition
(`PREREG-5` §2.8) is stated with the exact cell(s) named. If
`T-HKZINDEP-NODATA` branch (b) fired, confirm the declared third-attempt
boundary is stated explicitly and that the report does not smuggle in a
recommendation for a fourth iteration without a change in available tooling.

## Built control, not proposed

At least one null or nearby-object control, BUILT — e.g. if Branch A
(fpylll) is available in this session, independently recompute `rdet` (in
`A-1`'s scope, algebraically forced to zero true dispersion) using fpylll's
own API at one matched cell, to calibrate what a genuinely HKZ-quality
independent route's residual floor looks like on a candidate with a KNOWN
answer, before trusting the residual floor reported for `hkz`.

## Discipline

State the cheapest falsification of every headline with its cost. Where a
measurement goes against your own thesis, report it at the same weight as
your objections. INDEPENDENT SESSION. COMMIT NOTHING. Do not restate
`KN-FIND-7d098b`, `KN-FIND-9d44b4`, `KN-FIND-9b5df0` or `KN-FIND-7de6b6` as
new. `lam1n` is OUT OF SCOPE for this batch — do not re-open it. CLAIM TIER
STAYS TOY. `knowledge/INDEX.md` must not be written, regenerated or staged.
A timeout, crash or missing dependency is INFRASTRUCTURE SIGNAL, never
negative mathematical evidence.

## Artifacts (extended per G-1 before the ledger archive stages)

    reviews/TASK-20260813-5b09b0/red_team_report.md
    reviews/TASK-20260813-5b09b0/probes/...   (at least one BUILT, re-executable probe)
