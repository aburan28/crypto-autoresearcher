# Deferred-lane minimum-viable-batch cost gate: readiness

## Current state

This is a **BATCH-local draft** for `H-ECDLP-a8ad36` and
`EXP-ECDLP-0cad85`. It has not created canonical records. It is zero-run:
implementation authorization is false, scientific execution authorization is
false, and the maximum scientific run count is zero.

## What the draft defines

The draft separates seven inputs that a future source-bound cost observation
would need: source identity, cost, comparable baseline, parameter range,
count, ratio, calibration, and consumer. It also defines the conservative
outputs `INVALID_INTERFACE`, `UNESTIMABLE`, `NO_CONSUMER`, and `COMPARABLE`.
The first three prevent a missing input from turning into an inferred estimate.

`COMPARABLE`, if a future independently reviewed implementation ever emits it,
would mean only that the specified accounting fields were typed and
cross-consistent for that disclosed record. It would not rank work, approve an
experiment, retire a lane, infer a resource allocation, or say anything about
ECDLP hardness or an attack.

## Readiness blockers

- No live lane, goal, queue, claim, priority, cost, or consumer was read.
- No primary source or retained repository record was read or hash-bound.
- No real baseline, calibration record, range, count, cost, or ratio exists in
  this BATCH artifact.
- No validator implementation or synthetic control fixture exists.
- No implementation-admission decision, independent design review, execution
  decision, or independent result review exists.

These are not negative evidence about any research lane. They make every live
cost question **unestimable from this draft**.

## Preconditions for a later admission decision

1. Bind an exact source snapshot and retain every relevant source object with
   byte hashes and locators.
2. Define the allowed accounting boundary and common units from those sources.
3. Implement and independently review the static validator plus synthetic
   controls; do not use it on live data yet.
4. Obtain a fresh Coordinator decision that names the exact future write scope,
   evidence boundary, consumer contract, and no-state-change condition.
5. Independently review any resulting receipt before treating it as a cost
   observation. A receipt remains an accounting artifact, not a scientific or
   cryptanalytic conclusion.

## Non-results

This draft does not contain a cost estimate, a minimum batch, a live comparison,
a calibration, a consumer, a priority, a retirement decision, a canonical
record, an experiment run, or an ECDLP claim.
