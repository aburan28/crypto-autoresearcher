# TASK-20260813-968dc8 — INDEPENDENT VALIDATION

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    role            validator
    policy          review-adversarial                 effort xhigh
    state           queued
    depends_on      TASK-20260813-c0ec71, TASK-20260813-861a58
    review_required false
    archived_by     PENDING (ledger archive)
    independent_session_required true
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## Primary target

**IS `ROUTE-I''` GENUINELY NON-CODE-SHARED, AND IS IT GENUINELY HKZ-QUALITY?**
Two separate questions, both load-bearing. Independence: diff the lead's
committed reduction/enumeration code against `make_A`/`build_basis`/
`hkz_profile` in `measure_am4.py`/`measure_relvar.py`/`replicate_l7l8.py`
(including `BATCH-4ed139`'s copy) AND against `BATCH-6e08fe`'s own
`measure_route_reimpl.py` reduction/enumeration code — `PREREG-5` §2.2 point
1 bars copying either lineage this time. Fidelity: if Branch A was declared
(`fpylll`), confirm the actual API calls used genuinely implement
BKZ(block=`d`) + explicit HKZ sweep + independent per-index enumeration, not
merely LLL under a different name. If Branch B was declared, confirm the
from-scratch implementation genuinely performs BKZ (not merely LLL) at
`block_size = d`.

## Second target — the fpylll re-verification and branch choice

Independently re-verify, in THIS validator's own session, whether `fpylll`
is available (attempt the identical install/import sequence `PREREG-5` §1
describes) and report your own result plainly, regardless of which branch
the lead declared. If your own environment disagrees with the lead's
declared branch choice, this is a finding to report, not silently absorbed.

## Third target — re-derive, don't trust

Independently confirm genuine `ROUTE-P` per-basis ground truth exists at all
6 named cells (read `results_relvar.json`'s `G_REL1.hkz` block yourself) and
recompute `D_route''`/`VERDICT''` at every cell the lead reports covered,
WITHOUT importing the producer's module. Confirm `results_l7l8.json`/
`results_am4.json` were NOT used as a `ROUTE-P` source anywhere in the
lead's computation.

## Fourth target — the termination branch and the third-attempt boundary

Confirm the termination branch reported is the branch `PREREG-5` §2.6's
frozen clause actually fires from the reported numbers, precedence applied
correctly, `-PARTIAL` suffix applied correctly. If `T-HKZINDEP-ARTIFACT`
fired at any cell, confirm the revisit condition (§2.8) is stated with the
exact cell(s) named. If `T-HKZINDEP-NODATA` branch (b) fired, confirm the
declared third-attempt boundary is stated explicitly and that no fourth
attempt is implicitly proposed anywhere in the lead's report.

## Discipline

State which of your own claims are SINGLE-SOURCE vs REPLICATED. Record
independence as PROCEDURAL, NEVER MODEL-LEVEL, with `model_verified: false`
and its reason, host and stack MEASURED. **List every probe path explicitly**
so the ledger archive can declare it (declared gap G-1, carried from this
goal's established pattern). INDEPENDENT SESSION. COMMIT NOTHING — your
report and probes sit uncommitted (PD-4, open) until the ledger archive
commits them. Do not restate `KN-FIND-7d098b`, `KN-FIND-9d44b4`,
`KN-FIND-9b5df0` or `KN-FIND-7de6b6` as new. `lam1n` is OUT OF SCOPE for this
batch — do not re-open it. CLAIM TIER STAYS TOY. `knowledge/INDEX.md` must
not be written, regenerated or staged. A timeout, crash or missing
dependency in the lead's run is INFRASTRUCTURE SIGNAL, never negative
mathematical evidence.

## Artifacts (extended per G-1 before the ledger archive stages)

    reviews/TASK-20260813-968dc8/validation_report.yaml
    reviews/TASK-20260813-968dc8/probes/...   (every probe you build, with output)
