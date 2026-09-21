# Arm-A successor repair design

This package is a new immutable successor to `EXP-ECDLP-a76937`. The prior
package and its fresh `TASK-20260809-cff774` NO-GO report remain unchanged.
This task creates no implementation, run, or empirical evidence.

## Closure map for the fresh review

| Finding | Concrete repair |
|---|---|
| `REV-cff774-01` automorphism/stabilizer ambiguity | v3 manifests require `automorphism_order`, duplicate-free complete `generated_group_maps`, `group_order_certificate`, the complete positive-divisor `allowed_stabilizer_sizes`, and the exact replay equation `orbit_size * stabilizer_size = automorphism_order`. |
| `REV-cff774-02` source/random pairing and calibrations | Target derivation uses `pair_id`/group seed/field bits only; source and random controls share the resulting pair token, target, partition seed, and stopping rule. Eight calibration rows have explicit seeds, family predicates, expected detector labels, and exclusion dispositions. |
| `REV-cff774-03` charged-work overlap | `COST-ECDLP-5ec1c5-v2` uses one exclusive field/scalar/event counter source, expands point/map internals into field wrappers, charges hash/serialization/memory/setup explicitly, and marks point/certificate counters diagnostic-only. |
| `REV-cff774-04` unattainable test | Held-out groups increase from four to eight; the exact two-sided sign-permutation minimum is `2/256`, making `p <= .05` attainable. All eight groups must be valid, removing the contradictory partial-validity rule. |
| `REV-cff774-05` incomplete collision fixture | The fixture retains duplicate and quotient-equivalent negatives and adds `(a1,b1)=(12,7)`, `(a2,b2)=(39,9)`, denominator `2`, and expected recovered `x=37`. |

The successor remains finite toy-scale and carries no exponent or
cryptographic-scale claim. The next gate is the exact snapshot followed by a
fresh independent `review-adversarial` session.
