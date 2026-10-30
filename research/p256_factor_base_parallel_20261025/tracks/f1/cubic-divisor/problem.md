# Global elimination cost after reduced cubic-divisor membership

- **Status:** open
- **Kind:** implementation/proof gap; bounded adapter resource outcomes recorded separately
- **Affected work:** TASK-20261025-13c38e, continuing TASK-20261025-cfb933
- **Next action owner:** Coordinator to assign a scoped follow-on implementation task
- **Last updated:** 2026-10-25

## Problem

The generic membership ideals can now be represented and certified as reduced on
all three coordinate strata, but no controlled global solving bound or complete
high-depth relation solver has been established for cubic-divisor membership+S4.

This updates the obstruction's state rather than repeating the original
nonreduced-terminal diagnosis: that input multiplicity issue is removed by this
new formulation under the stated separability hypotheses. It does not remove
the separate elimination-cost obligation.

## Evidence and uncertainty

- **Observed:** the fixed actual P-256 k=3 joint fixture completes, including all
  repeated strata. Twenty-one basis certificates replay by separate sparse
  arithmetic; six full query unions match exhaustive signed point triples.
- **Observed resource outcomes:** distinct k=4 positive stops during default
  Buchberger construction. Separate F5B k=4 positive and fixed-generator cases
  stop as well. Each attempt has a 30-second watchdog and 2 GiB address-space cap.
  Native logs and terminal receipts are in `attempts-01/` and `attempts-02/`.
- **Derived:** the generic cubic-divisor locus is finite reduced with C(S,3)
  geometric points. Exactly-two-equal and all-equal loci are finite reduced with
  S(S−1) and S points. This is a mathematical representation fact, not a runtime
  lower or upper bound. See [derivation.md](derivation.md).
- **Unknown cause:** the precise dominant internal work of each stopped adapter
  is unprofiled; no claim isolates degrees, fill-in, implementation constants or
  intrinsic mathematical difficulty as its cause.
- **Missing capability:** certified elimination/root extraction operating on the
  unexpanded short circuit with an explicit cost model in k and actual base size.
- **Not established:** a hardness conclusion, impossibility, speed advantage,
  asymptotic improvement, attack cost, or success distribution.

## What would unblock it

- [ ] An executable unexpanded-circuit solver completes the fixed distinct k=4
  positive and empty-generator fixtures, returning exact roots and replayable
  completeness certificates without enumerating every domain triple as its search.
- [ ] A stated total resource model includes construction, repeated strata,
  root extraction, curve lifts, unsuccessful queries and certificate generation;
  its assumptions are justified or explicitly unresolved.

These are implementation acceptance conditions for the next step, not necessary
conditions for every possible algorithm. Meeting them would still leave scaling,
independent review, official performance admission, relation independence and the
remaining ECDLP stages unresolved.

## Next discriminating step

Implement incremental elimination on the multiplication-gate circuit, retaining
its O(k) representation and avoiding immediate full expansion. Use the unchanged
k=3 completion as a positive control, the fixed k=4 positive/generator inputs as
targets, and the already solved repeated strata as controls. Declare per-process
watchdogs within the handoff memory envelope. Completion permits a deeper
correctness pass; another resource stop records only that attempt; an adapter
failure gets a separate correction. Any performance experiment needs its own
repository admission.

## Resolution and history

Unresolved. Link this progress update to the original F1 problem rather than
replacing its immutable evidence. Shared problem-index changes remain Coordinator
scope; this directory is the only authorized write scope.
