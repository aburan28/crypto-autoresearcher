# Distinguished-point density tradeoff audit

## Audit basis

- Idea: `IDEA-20261006-947b64`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Governing records: `KR-RHO-7d93f6`, `KR-RHO-6239aa`, and
  `KR-RHO-cd86f5`.

## Scientific boundary

The proposal compares two distinguished-point predicates, residues divisible
by 8 and by 32, for an r-adding walk on `Z/401Z`. It measures a finite slice
of the established time/storage tradeoff. It does not propose a new walk,
change the collision-search exponent, or improve the known time-space
product.

The two predicates have different exact densities because the representative
set `{0,...,400}` contains 51 multiples of 8 and 13 multiples of 32. Those
densities must be reported directly; the labels “modulus 8” and “modulus 32”
are not themselves a theorem about a fourfold timing ratio.

## Load-bearing execution definition

“One planted logarithm” and “steps to a certified collision” do not define a
complete collision protocol. The repaired contract must specify the two
walks or target states, their initial representations, the r-adding table,
how a distinguished-point table stores coefficients, the collision event,
and the exact congruence check that recovers and verifies the planted log.
One trajectory by itself does not establish a collision against a selected
target.

Both modulus arms must use the same transition table, seed-derived target,
initial states, arithmetic implementation, and walk schedule. Only the
distinguished predicate may change. The record must retain every seed’s
termination reason, total steps for each walk, distinct table entries,
duplicate overwrites, lookups, collision reconstructions, scalar
verification, and peak memory. “Stored distinguished points” must mean a
fixed byte/accounting definition rather than only a set cardinality.

The cap rule may censor sparse walks. Paired dropping is preferable to
one-sided selection, but the report must retain all capped seeds and refuse
the ratio when fewer than the declared completion minimum finish. The lower
median convention and strict threshold comparisons must remain frozen.

## Controls and null model

The random-function control must implement the same two-walk collision and
certificate protocol, with a transition function and state representation
that are explicitly matched to the group arm. Hashing labels for a predicate
alone does not create a random-mapping baseline. If the control is intended
to test only generic thinning, state that narrower purpose and do not use it
to separate group structure from an unmatched transition process.

The first-walk hit-fraction check is a diagnostic for this finite seed. It is
not a mixing theorem, and a deviation from the exact residue density does not
by itself falsify the distinguished-point tradeoff. Likewise, a ratio above
1.6 or 1.5 on one small group is descriptive and should not be extrapolated
to cryptographic orders.

## Claim ceiling and disposition

A valid run could establish only the paired step and storage ratios for the
declared cyclic group, r-adding table, seeds, caps, predicates, and cost
ledger. It cannot establish a new time-memory curve, an exponent reduction,
or a departure from the known `T^2 S` collision-search boundary. A negative
ratio closes only this finite walk and predicate choice.

Disposition: **keep proposed as a calibration/control; do not approve it as a
new collision-search experiment as filed.** Repair the collision protocol,
the full memory/time charge, and the random-function null. If retained, use it
as a small preflight cell for the existing rho tradeoff work; otherwise leave
it unexecuted while the readiness selector has no admitted row.
