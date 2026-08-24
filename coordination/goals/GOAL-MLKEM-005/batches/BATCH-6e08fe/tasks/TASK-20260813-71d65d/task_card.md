# TASK-20260813-71d65d — INDEPENDENT VALIDATION

    goal / batch    GOAL-MLKEM-005 / BATCH-6e08fe
    role            validator
    policy          review-adversarial                 effort xhigh
    state           queued
    depends_on      TASK-20260813-ea2e96, TASK-20260813-2d6b5e
    review_required false
    archived_by     PENDING (ledger archive)
    independent_session_required true
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## Primary target

**IS `ROUTE-I'` GENUINELY NON-CODE-SHARED?** Diff the lead's committed
`measure_route_reimpl.py` against `make_A`/`build_basis`/`hkz_profile` in
`measure_am4.py`, `measure_relvar.py` and `replicate_l7l8.py` (including
`BATCH-4ed139`'s copy) yourself. If the lead's basis-construction or
reduction/enumeration code is copied, adapted, or structurally paraphrased
from that lineage — even if it calls a different top-level function name —
this is a CONSTRAINT VIOLATION under `PREREG-4` §2.2 and must be reported at
full weight; it would mean this batch has not actually answered the question
it was dispatched to answer.

## Second target — re-derive, don't trust

Independently re-derive obligation 0's coverage table (§2.3: read
`results_relvar.json`'s `G_REL1` block yourself, confirm or refute the
expectation that the 3 middle-beta cells lack per-basis ground truth) and
recompute `D_route'`/`VERDICT'` at every cell the lead reports covered, from
the frozen `PREREG-4` text, WITHOUT importing the producer's module. Confirm
`results_l7l8.json`/`results_am4.json` were NOT used as a `ROUTE-P` source
anywhere in the lead's computation (§2.1's explicit exclusion).

## Third target — RC-3 and the termination branch

Confirm RC-3 was carried verbatim against
`probe_coverage_beta_mismatch_output.json`'s actual committed values. Confirm
the termination branch reported is the branch `PREREG-4` §2.6's frozen
clause actually fires from the reported numbers, precedence applied
correctly (`SOME-ARTIFACT` dominates `ALL-SURVIVE`), `-PARTIAL` suffix
applied correctly, and — if any cell fired `T-INDVERIFY-ARTIFACT` — that the
revisit condition (§2.8) is stated, not silently absorbed.

## Discipline

State which of your own claims are SINGLE-SOURCE vs REPLICATED. Record
independence as PROCEDURAL, NEVER MODEL-LEVEL, with `model_verified: false`
and its reason, host and stack MEASURED. **List every probe path explicitly**
so the ledger archive can declare it (declared gap G-1). INDEPENDENT
SESSION. COMMIT NOTHING — your report and probes sit uncommitted (PD-4,
open) until the ledger archive commits them. Do not restate `KN-FIND-7d098b`,
`KN-FIND-9d44b4` or `KN-FIND-9b5df0` as new. CLAIM TIER STAYS TOY.
`knowledge/INDEX.md` must not be written, regenerated or staged. A timeout,
crash or missing dependency in the lead's run is INFRASTRUCTURE SIGNAL, never
negative mathematical evidence.

## Artifacts (extended per G-1 before the ledger archive stages)

    reviews/TASK-20260813-71d65d/validation_report.yaml
    reviews/TASK-20260813-71d65d/probes/...   (every probe you build, with output)
