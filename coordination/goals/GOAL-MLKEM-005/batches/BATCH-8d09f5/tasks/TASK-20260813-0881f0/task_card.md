# TASK-20260813-0881f0 — INDEPENDENT RED TEAM

    goal / batch    GOAL-MLKEM-005 / BATCH-8d09f5
    role            red-team
    policy          review-adversarial                 effort xhigh
    state           queued
    depends_on      TASK-20260813-630414, TASK-20260813-cb8943
    review_required false
    archived_by     PENDING (ledger archive)
    independent_session_required true
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## Primary target — attack whether the mutation is exactly what it claims to
## be, don't take it on faith

This batch exists because `BATCH-a6fab5`'s two reviews independently found
the `D_route`/`D_route''` mechanism has near-zero DEMONSTRATED power against
a shared-code defect. Its own claim to fix that is itself a claim to be
attacked, not trusted. **BUILD, don't propose**: (a) diff the lead's
committed mutant file against `measure_hkz_indep.py` yourself and confirm
EXACTLY ONE functional line differs — report a CRITICAL finding if more
than one line differs, if the change is not the declared seed-index
off-by-one, or if `measure_hkz_indep.py` itself was touched; (b) if budget
allows, independently RE-RUN the mutant's own logic (or an equivalent
reimplementation) at least once, from scratch, to confirm the reported
`D_route_mut`/`VERDICT_mut` at at least one cell is reproducible and not an
artifact of the lead's own script alone.

## Second target — independently re-verify the fpylll infrastructure signal

Attempt the identical `pip install fpylll` / `import fpylll` sequence
`PREREG-6` §1 describes, IN THIS RED TEAM'S OWN SESSION, and report your own
result plainly — a data point on this environment fact, regardless of what
the lead found.

## Third target — attack the frozen prediction (`PREREG-6` §2.3) and
## `HEURISTIC-M1`

Recompute the predicted `D_route_mut` yourself directly from
`results_relvar.json`'s own per-basis arrays. Separately, assess whether
`HEURISTIC-M1` (the mutant's shifted-seed reduction converges as reliably
as `BATCH-a6fab5`'s own unmutated route) held in practice — did every
matched basis of the mutant's own run actually converge, or did any fail
and get silently treated as if it hadn't? If the measured `D_route_mut`
diverges substantially from the frozen prediction, determine whether this
is better explained by a convergence failure (`HEURISTIC-M1` not holding)
or by the instrument genuinely behaving differently than predicted, and
report which, with reasoning — do not let the two be conflated.

## Fourth target — the termination clause and the detection mapping

Check the termination-branch precedence was applied correctly. Independently
verify the detection mapping (`VERDICT_mut = "DOES NOT EXCEED"` = DETECTED)
was applied the right way round in the lead's own report — this is the
single easiest place for this batch to silently invert its own headline.
Confirm the report's FORBIDS compliance (§2.6/§2.8/§6): no claim about
`hkz`'s admissibility, no re-litigation of `T-HKZINDEP-CONFIRMED`, no
`ML-KEM`/FIPS-203/cost claim, no goal-status claim.

## Built control, not proposed

At least one built control distinguishing "the mutation genuinely changed
the measured lattice" from "the mutation had no real effect and the large
`D_route_mut` comes from somewhere else" — e.g., independently verify that
the mutant's basis at slot `i` is bit-identical (or converges to the same
value) as an UNMUTATED `route_ii_make_A(d, k, q, (i+1) % 8)` would produce,
confirming the mutation does exactly what §2.2 claims and nothing more.

## Discipline

State the cheapest falsification of every headline with its cost. Where a
measurement goes against your own thesis, report it at the same weight as
your objections. INDEPENDENT SESSION. COMMIT NOTHING. Do not restate
`KN-FIND-7d098b`, `KN-FIND-9d44b4`, `KN-FIND-9b5df0`, `KN-FIND-7de6b6` or
`KN-FIND-d29ece` as new. `lam1n` is OUT OF SCOPE — do not re-open it. This
batch does not re-litigate `T-HKZINDEP-CONFIRMED`. CLAIM TIER STAYS TOY.
`knowledge/INDEX.md` must not be written, regenerated or staged. A timeout,
crash or missing dependency is INFRASTRUCTURE SIGNAL, never negative
mathematical evidence.

## Artifacts (extended per G-1 before the ledger archive stages)

    reviews/TASK-20260813-0881f0/red_team_report.md
    reviews/TASK-20260813-0881f0/probes/...   (at least one BUILT, re-executable probe)
