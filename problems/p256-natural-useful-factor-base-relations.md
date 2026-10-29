# Natural useful relations and full costs remain unmeasured

- **Status:** `investigating`
- **Kind:** implementation and measurement gaps; conditional distribution assumptions
- **Affected work:** [F3 labelled bases](../research/p256_factor_base_parallel_20261025/tracks/f3/report.md), [F4 divisor stitching](../research/p256_factor_base_parallel_20261025/tracks/f4/report.md), [F8 orbit control](../research/p256_factor_base_parallel_20261025/tracks/f8/report.md)
- **Next action owner:** Coordinator for separate prospective method-specific trials
- **Last updated:** 2026-10-25

## Problem

The implemented relation and compression mechanisms have exact correctness
controls, but a costed supply of useful natural relations and complete target
recovery has not been established for these prototypes.

F3 and F4 use the published P-256 group. F8 uses secp256k1 as an explicit
automorphism control, not as a transferred P-256 construction. Their outstanding
obligations differ; this record groups the common missing conclusion without
asserting a common mathematical obstruction.

## Evidence and uncertainty

- **Observed F3:** 97 Python checks and 100 separate Sage assertions passed.
  One deterministic natural case has no dependency; arranged controls have
  one zero-Q and one useful dependency. The useful control has an intentionally
  known generation witness. None is a natural-yield estimate.
- **Observed F4:** exact divisor extraction and signed cancellation replay
  cover 29 cases, including five unresolved nonrational divisors. Constructed
  one-outside and two-outside rows have ranks 5 to 4 and 4 to 1 after
  cancellation. An ordinary graph cycle can fail signed cancellation.
- **Observed F8:** eight representatives generate 48 signed orbit points;
  96 constructed rows have compressed rank 7. The known symmetry constraints
  explain the larger full-column rank. This is not 42 new independent
  pieces of information after symmetry.
- **Derived scope:** conditional laws for independent labels or uniform
  curve sections require their stated sampling assumptions. Adaptive labels,
  planted relations, anchors and repeated outside points need separate
  accounting.
- **Missing:** natural useful-relation frequency, graph collision and rank
  growth, complete resource costs, and ordinary-target attachment. One empty
  case proves neither low general yield nor impossibility.

## What would unblock it

- [ ] F3: a scalar-blind natural-instance solver with nonzero target
  coefficients and charged label construction, residual solving and failures.
- [ ] F4: a declared conditional sampling law, all-draw denominator,
  outside-point storage/collision counts, and independent rank after signed
  cancellation; engineered positives remain separate.
- [ ] F8: an ordinary relation solver with identical automorphism and orbit
  compression benefits in every comparator.
- [ ] For each method, a separately admitted complete-cost study covering
  setup, membership, root/sign recovery, failed queries, rank, linear algebra
  where needed, target attachment and memory; separate single-target and
  reusable-setup scenarios.

These are method-specific engineering/evidence gates. They do not require an
advantage as a condition for recording valid observations. A later advantage
claim requires the ordinary progress-fidelity and independent-review gates.

## Next discriminating step

Specify natural public synthetic target and base distributions for one method
at a time, retaining the existing positive, zero-information and corruption
controls. Valid execution supplies observations; implementation failure repairs
the interface; bounded null output changes only the tested scope. Recheck on a
new complete solver or admitted trial. No campaign cap or scientific status
change is introduced.

## Resolution and history

2026-10-25: opened from the three exact implementation packages. Detailed local
obligation records remain beside their sources. Unresolved.
