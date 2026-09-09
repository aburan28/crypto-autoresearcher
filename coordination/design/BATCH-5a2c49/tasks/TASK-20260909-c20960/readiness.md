# Tier-ladder reachability mock: readiness

## Current status

This is a BATCH-local, source-only, zero-run draft. It reserves
`H-ECDLP-ed4060` and `EXP-ECDLP-08b7f5`; it does not create canonical records.

The draft is ready only for independent review of its synthetic typed graph,
range, classification, control, and no-state-change boundary.

## What the design can test

Using only a future synthetic input constructed under the frozen interface,
the design can classify one mock route request as `RANGE_CONSTRAINED_ROUTE`,
`UNCONSTRAINED_ROUTE`, `ABSENT_ROUTE`, `NO_ROUTE`, or `INVALID_INTERFACE`.
This is an interface property. It has no authority or evidentiary bearing on
live portfolio state.

## Readiness impediments

No live goal, experiment, lane, queue, claim, priority, or ledger source was
read for this draft. Therefore their identities, graph structure, current
states, reachability, and priority ordering are all unknown here. The absence
of such reads is deliberate and does not imply that any actual route is absent
or unconstrained.

The following are required before any future live-audit work could be proposed:

1. A separately authorized source snapshot that lists exact allowed paths and
   their immutable hashes.
2. A new Coordinator decision that sets a bounded purpose and prohibits all
   state-changing output.
3. A source-bound implementation and custody plan.
4. An independent review of that plan.
5. A fresh decision and review plan before any execution.

## Authority boundary

This design cannot inspect or alter live research state. It cannot approve an
experiment, change priority, retire a branch, pause or complete a goal, create
canonical records, or execute a reachability audit. No implementation or
scientific execution is authorized.

## Evidence labels

Any future parser check or synthetic-control result would be a design or
control-plane artifact only. It would not be a cryptanalytic observation,
scientific result, portfolio verdict, or ECDLP conclusion.
