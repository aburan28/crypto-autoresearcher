# TASK-20260813-4aec9a — AUTHOR PREREG-6

    goal / batch    GOAL-MLKEM-005 / BATCH-8d09f5
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      (none)
    review_required false
    archived_by     TASK-20260813-62cd6b
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What it did

Wrote and froze `PREREG-6`, discharging `DEC-20260813-894568`'s single
`next_action` in full: a bounded successor task, as this batch's lead
measurement, that builds a MUTATION-TESTING (positive) control on the
`D_route''`/`D_route` comparison instrument itself for `hkz`, rather than a
further `ROUTE-P`-vs-`ROUTE-I'''`-style comparison (barred by
`DEC-20260813-894568` ruling_3's own independent re-derivation of the
third-attempt boundary).

Specified the exact injected defect: a one-line, off-by-one seed-index
mutation (`default_rng([1, d, k, i])` → `default_rng([1, d, k, (i+1) % 8])`)
in a COPY of `route_ii_make_A`, the seed-formula reconstruction of matrix
`A` that `PREREG-5` §2.2 point 3 licenses `ROUTE-P` and `ROUTE-I''` to
share. `measure_hkz_indep.py` itself is not edited. Named the two target
cells (`hkz/L7_b5`, `hkz/L11_b30` — bracketing dimension and predicted
margin, deliberately a small subset of `BATCH-a6fab5`'s 6 covered cells to
bound cost) and computed, BY HAND from already-archived, already-reviewed
`ROUTE-P` per-basis data (`results_relvar.json`), the frozen, pre-run
predicted `D_route_mut` at each: `0.0665893489077094` at `L7_b5` (~2.79x
`s_c^fib`) and `0.00948000985335451` at `L11_b30` (~2.48x `s_c^fib`).
Named the detection mapping explicitly (`VERDICT_mut = "DOES NOT EXCEED"`
means detected). Froze a fresh, four-branch termination clause
(`T-MUTCTRL-NODATA` / `-DETECTED` / `-NOT-DETECTED` / `-MIXED`, each
`-DETECTED`/`-NOT-DETECTED` suffixable `-PARTIAL`), not a reuse of the
`T-HKZINDEP-*` shape, per `DEC-20260813-894568`'s own instruction to design
this fresh. §2.7 re-derives, for a fifth time in this lineage, why this
does not trigger `PREREG-2` §7.5's repair bar. §2.8 and §6 state plainly
what this batch cannot do: it does not re-litigate `T-HKZINDEP-CONFIRMED`'s
own firing, does not test `hkz`'s admissibility, and its outcome either
way does not close, pause or complete `GOAL-MLKEM-005`.

Executed with NO SHELL, using read-only file access only; the frozen
prediction in §2.3 is this Coordinator's own hand arithmetic on
directly-read, already-committed numbers, explicitly weaker than a
measurement, and the lead's own independent recomputation (obligation 1
point 1) is the batch's actual attributed sanity check.

## Artifact

    tasks/TASK-20260813-4aec9a/prereg.md
