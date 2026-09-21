# Readiness: enumerated transport-chain cost accounting screen

**Status:** BATCH-local draft. It is not an approved hypothesis, canonical
experiment, implementation task, or execution plan.

## What is defined

The design has a finite-catalogue accounting boundary. A later source-bound
catalogue must enumerate implementation records, unit schema, cost vectors,
composition rules, and chain overhead. The accounting result may only be an
`ACCOUNTED_SYNTHETIC`, `UNESTIMABLE`, or `INVALID_INTERFACE` record. Each
numerical result is bounded to the exact catalogue and exact chain serialized
in its custody manifests.

The design has three deliberately distinct controls: small-degree,
composed-chain, and deterministic random-walk selection. It also has an
unenumerated-algorithm control. No control may create a numerical cost outside
the declared implementation inventory.

## Current impediments

1. No source was read or retained. Claims about isogenies, transport costs,
   degree behavior, or lower bounds remain unread-source impediments.
2. No source snapshot, catalogue, chain, unit conversion, composition rule,
   curve, or implementation artifact exists.
3. No cost vector is an observation. The design contains no timing, memory,
   data, query, or concrete security measurement.
4. The finite catalogue cannot characterize unenumerated algorithms; this is
   a declared limitation, never a universal lower-bound argument.
5. The BATCH package has not received independent design review.

## Required gates before any future activity

1. Retain and hash primary source bytes and exact proposition locators.
2. Write a source-bound finite catalogue and composition inventory with
   immutable custody manifests.
3. Obtain independent source/design review of units, summation, controls, and
   the unenumerated-algorithm limitation.
4. Write a separate implementation-and-custody plan, then obtain independent
   implementation review.
5. Obtain a fresh Coordinator decision for any implementation or execution.

No gate is satisfied by this design alone. A validation error, timeout, or
unestimable result would be operational/custody evidence only and would not
refute any mathematical proposition.
