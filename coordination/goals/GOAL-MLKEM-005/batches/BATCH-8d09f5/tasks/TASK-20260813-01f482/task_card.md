# TASK-20260813-01f482 — INDEPENDENT VALIDATION

    goal / batch    GOAL-MLKEM-005 / BATCH-8d09f5
    role            validator
    policy          review-adversarial                 effort xhigh
    state           queued
    depends_on      TASK-20260813-630414, TASK-20260813-cb8943
    review_required false
    archived_by     PENDING (ledger archive)
    independent_session_required true
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## Primary target — is the injected defect exactly what PREREG-6 §2.2 declares,
## and nothing else?

Diff the lead's committed mutant file against `measure_hkz_indep.py`
yourself, independently of the lead's own reported diff — confirm
mechanically that EXACTLY ONE functional line differs (the seed-formula
index argument in the copy of `route_ii_make_A`), and that
`measure_hkz_indep.py` itself is byte-identical to its own committed state
at `3d3f5fde552f1a4783616a624f602917719701e8` (unedited). If any other line
differs, or if the original was touched, this is a CRITICAL finding.

## Second target — independently re-verify the frozen prediction

Recompute `PREREG-6` §2.3's predicted `D_route_mut` yourself, directly from
`results_relvar.json`'s own `G_REL1.hkz.L7`/`L11` per-basis arrays (never
importing the lead's or `PREREG-6`'s own numbers uncritically) and confirm
it matches (`0.0665893489077094` at `L7_b5`, `0.00948000985335451` at
`L11_b30`). Independently re-verify the `fpylll` infrastructure signal in
THIS validator's own session.

## Third target — re-derive the measured `D_route_mut`/`VERDICT_mut`, and
## check the detection mapping is applied correctly

Recompute `D_route_mut` and `VERDICT_mut` at both cells directly from the
lead's raw per-basis output, WITHOUT importing the producer's module.
Confirm the lead's report correctly reads `VERDICT_mut = "DOES NOT EXCEED"`
as DETECTED and `"EXCEEDS"` as NOT DETECTED (§2.4 point 5) — this mapping
is easy to invert by mistake and a reviewer's independent check of it is
load-bearing. Confirm `results_l7l8.json`/`results_am4.json` were not used
as a source anywhere, and that no reduction above `d = 40` occurred.

## Fourth target — the termination branch

Confirm the termination branch reported is the branch `PREREG-6` §2.6's
frozen clause actually fires from the reported numbers (`T-MUTCTRL-NODATA`
/ `-DETECTED` / `-NOT-DETECTED` / `-MIXED`, precedence and `-PARTIAL` suffix
applied correctly). Confirm the report does not, whichever branch fires,
make any claim about `hkz`'s own admissibility, `T-HKZINDEP-CONFIRMED`'s
firing, `A-1`, `ML-KEM`, or close/pause/complete `GOAL-MLKEM-005` — check
this against §2.6/§2.8/§6's FORBIDS lists line by line.

## Discipline

State which of your own claims are SINGLE-SOURCE vs REPLICATED. Record
independence as PROCEDURAL, NEVER MODEL-LEVEL, with `model_verified: false`
and its reason, host and stack MEASURED. **List every probe path
explicitly** so the ledger archive can declare it (declared gap G-1,
carried from this goal's established pattern). INDEPENDENT SESSION. COMMIT
NOTHING — your report and probes sit uncommitted (PD-4, open) until the
ledger archive commits them. Do not restate `KN-FIND-7d098b`,
`KN-FIND-9d44b4`, `KN-FIND-9b5df0`, `KN-FIND-7de6b6` or `KN-FIND-d29ece` as
new. `lam1n` is OUT OF SCOPE — do not re-open it. This batch does not
re-litigate `T-HKZINDEP-CONFIRMED`. CLAIM TIER STAYS TOY.
`knowledge/INDEX.md` must not be written, regenerated or staged. A timeout,
crash or missing dependency is INFRASTRUCTURE SIGNAL, never negative
mathematical evidence.

## Artifacts (extended per G-1 before the ledger archive stages)

    reviews/TASK-20260813-01f482/validation_report.yaml
    reviews/TASK-20260813-01f482/probes/...   (every probe you build, with output)
