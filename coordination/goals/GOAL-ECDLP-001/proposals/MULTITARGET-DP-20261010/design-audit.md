# Distinguished-point multi-target calibration audit

## Audit basis

- Idea: `IDEA-20261006-6374b1`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Closest existing contract: `EXP-MTGT-d4f8cd`, which already specifies the
  shared distinguished-point baseline, same-curve multi-target ladder,
  cross-curve nulls, memory accounting, and recovery certificates.

## Overlap and scientific boundary

The proposal measures the known multi-target amortization on `Z/503Z` with
four planted targets, a fixed distinguished-point predicate, and separate
versus shared walks. Its expected ratio is a finite calibration of the
Kuhn--Struik/van Oorschot--Wiener baseline, not a new walk rule and not an
improvement below the generic multi-target frontier.

The broader `EXP-MTGT-d4f8cd` contract is the appropriate lineage for any
execution. It already requires a same-curve `M` ladder, cross-curve and
different-class nulls, fixed distinguished-point density, peak-store
accounting, collision certificates, and area-time reporting. A standalone
second experiment at `Z/503Z` would duplicate that measurement unless it is
explicitly retained as a preflight fixture for the larger contract.

## Contract gaps

“One joint r-adding walk” is not operationally precise enough to recover four
independent planted logarithms. The repaired contract must state the number
of walkers, their starting states, the target-side state carried by each
trail, the table key/value format, and the exact event that certifies one
target. A shared table may amortize storage and collision discovery, but a
single trajectory without target-labelled trails does not automatically solve
four selected targets.

The joint and separate arms must use identical partition tables, transition
semantics, distinguished-point density, initialization policy, collision
verification, and arithmetic implementation. The cost ledger must include
walk steps, distinguished-point tests, table insertion and lookup, collision
reconstruction, target initialization, scalar verification, table memory, and
any failed or duplicate collisions. Step counts alone are not a full cost
comparison.

## Statistics and censoring

Sixteen seeds and a lower median can be a reproducible calibration, but the
threshold `S/J >= 1.4` is a declared finite decision boundary, not a
confidence statement. The record must freeze the seed-to-target derivation,
the exact lower-median convention, strict versus non-strict thresholding, and
whether any seed is excluded before the comparison.

The paired cap rule is directionally correct, but dropping capped seeds can
still condition the observed distribution. The report must include every
seed's terminal reason, steps, table size, and recovered-target count, and
must refuse the ratio when the declared completion minimum is not met. No
seed may be silently replaced or dropped from only one arm.

The permuted-label control must preserve the distinguished-set cardinality
and all non-label walk parameters. Its interpretation is limited: a changed
ratio would show sensitivity to the representative predicate, while an
unchanged ratio would not prove mixing or universality. The first-walk
divisibility check is a diagnostic, not a mixing theorem and not a substitute
for an independent seed ladder.

## Claim ceiling and disposition

A valid run could establish only the exact paired step/cost ratio on the
declared cyclic group, target generator, distinguished predicate, seed set,
cap, and implementation. It cannot establish a cryptographic-scale result,
an exponent reduction, or a departure from the known multi-target
`Theta(sqrt(LN))` baseline. The permuted-label arm can falsify a labeling
artifact on this group; it cannot prove that the identity predicate is
universal.

Disposition: **keep proposed as a calibration/control; do not approve it as a
second standalone multi-target experiment.** If the broader
`EXP-MTGT-d4f8cd` contract is repaired and admitted, this `Z/503Z` cell may be
used as its smallest correctness and accounting fixture. Otherwise it should
remain an unexecuted proposed control. The current readiness selector has no
admitted row, so execution is not authorized by the repository state.

Next action: reconcile the proposal into `EXP-MTGT-d4f8cd` or a successor
contract with explicit walker/table semantics and full cost accounting, then
run the readiness command before any execution request.
