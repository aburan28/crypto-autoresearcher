# TASK-20260813-94e686 — AUTHOR PREREG-5

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           completed
    depends_on      (none)
    review_required false
    archived_by     TASK-20260813-d63082
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What it did

Wrote and froze `PREREG-5`, discharging `DEC-20260813-1aae44`'s single
`next_action` in full: a bounded successor task, as this batch's lead
measurement, that builds a GENUINELY HKZ-QUALITY (not LLL-quality)
independent `ROUTE-I''` for `hkz` ONLY (`lam1n` is explicitly out of scope —
`BATCH-6e08fe` already discharged it) at `L7`/`L9`/`L11`, at the SAME 6
currently-covered `hkz` cells, using the SAME frozen `ROUTE-P` values and the
SAME `PREREG-3` §3.3 comparison formula.

Recorded, as INFRASTRUCTURE SIGNAL only, that the dispatching session
independently confirmed `pip install fpylll` (plus its missing transitive
dependency `cysignals`) succeeds and functions correctly in its own
environment — the first such confirmation in three dedicated checks across
this campaign's history — and instructed the eventual lead to re-verify this
independently in its own session before relying on it (§1). Specified a
two-branch operational definition of "genuinely non-code-shared AND
HKZ-quality" (§2.2): Branch A, `fpylll`'s own public API used directly
(intended, primary path); Branch B, a from-scratch full HKZ implementation
if `fpylll` is unavailable in the lead's own session, bounded to `d <= 40`.
Named, as a caution only (not a constraint), the Schnorr–Euchner zig-zag
asymmetry the dispatching session found and reverted in `BATCH-6e08fe`'s
archived script — moot under Branch A. Froze a three-branch termination
clause (`T-HKZINDEP-NODATA` / `-ARTIFACT` / `-CONFIRMED`) matching
`DEC-20260813-1aae44` §11's revisit condition exactly, and operationalized
that same decision's declared boundary — the THIRD dedicated attempt at
`hkz`'s independent-verification question — as `T-HKZINDEP-NODATA` branch
(b), explicitly barring a fourth iteration absent a change in available
tooling. §2.7 re-derives, for a third time, why this does not trigger
`PREREG-2` §7.5's repair bar.

Executed with NO SHELL, using read-only file access only; every number
attributed to "this Coordinator" is a read-only observation, weaker than a
measurement, and the lead's own section 1 re-verification and section 2.3
sanity check are the batch's actual attributed measurements. The `fpylll`
installation/functional-check result in §1 was performed by the dispatching
session (which holds a shell), not this Coordinator session, and is recorded
as reported infrastructure signal for the lead to independently re-verify.

## Artifact

    tasks/TASK-20260813-94e686/prereg.md
