# TASK-20260813-28eb06 — Red-team ROUTE-I2

    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            red-team
    policy          review-adversarial     independent_session_required
    state           queued
    depends_on      TASK-20260813-415c21, TASK-20260813-5d1920
    review_required false
    archived_by     PENDING (ledger archive, TASK-20260813-fe3dec)
    budget          3600 s, 2 GB, 1 run
    claim tier      TOY

## What this task must do

Attack `PREREG-4`'s part (b) where it is weakest: whether the claimed
algorithmic difference is genuine or superficial; whether `ROUTE-I2`'s
basis is bit-identical to the frozen `F0` construction `ROUTE-P` consumed;
whether every reduction/enumeration diagnostic was honestly reported,
including unfavourable ones; and whether the termination clause's
precedence (a single `UNDERMINES`-firing cell dominates `CONFIRMS`) was
applied correctly. **Build** checks, don't merely propose them.

## Primary targets, in order

1. A structural/AST-level (not merely literal-string-import) check for
   shared code between `measure_route_i2.py` and the three named prior
   files.
2. A basis-fidelity check via a derivable invariant (max entry bound,
   block structure, or the closed-form `(d-k)*log(q)` determinant check)
   that does not require importing the producer's code.
3. Confirm no basis with a flagged breakdown diagnostic was silently
   counted as if it succeeded.
4. Confirm the termination clause's precedence was applied correctly.
5. Confirm the `RC-3` carry matches your own committed probe output exactly.
6. **Build** at least one null/nearby-object control (e.g. run `ROUTE-I2`'s
   own pipeline twice on the same basis, or on a degenerate basis with a
   known closed-form profile, to calibrate its own noise floor before
   trusting its comparison against `ROUTE-P`).

## Deliverables

    reviews/TASK-20260813-28eb06/red_team_report.md
    reviews/TASK-20260813-28eb06/probes/*   (at least one built, re-executable probe)

**List every probe path explicitly in the report** — declared gap `G-1`.

## Constraints

Independent session. Commit nothing. Do not restate
`KN-FIND-9b5df0`/`KN-FIND-7d098b`/`KN-FIND-9d44b4` as new. No reduction
above `d = 40` anywhere. Claim tier stays TOY. Where a measurement goes
against your own thesis, report it at the same weight as your objections.
