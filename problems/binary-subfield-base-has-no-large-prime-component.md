# Direct proper-subfield x base has zero large-prime component on a descended binary curve

- **Status:** `open`
- **Kind:** proved conditional obstruction; remaining construction and measurement gaps
- **Affected work:** [50–63-bit elite-factor-base baseline and grid](../docs/reports/2026-10-16-elite-factor-base-baseline.md), [binary field screen](../docs/reports/2026-10-17-icperf-binary-divisor-fit.md), [full-width IC grid problem](full-width-ic-arity-grid-unmeasured.md), GOAL-ICPERF-e6b6a4
- **Next action owner:** Coordinator for the next frozen near-subfield comparison; implementation owner unassigned
- **Last updated:** 2026-10-17

## Problem

A direct base restricted to x-coordinates in `F_(2^d)` cannot contribute to a large prime subgroup of `E(F_(2^n))` when `d|n`, `d<n`, the curve descends to `F_(2^d)`, and the target prime order exceeds `2^d+1+⌊2√(2^d)⌋`. This rules out using exact subfield closure as a degree-of-regularity lever for such a subgroup on a Koblitz curve. It does not block the wider request for a near-subfield, displaced, or other full-rank elite base.

## Evidence and uncertainty

- **Observed:** The [integer record](../research/icperf_subfield_rank_gate_20261017/hasse_bounds.json) gives the exact Hasse ceiling for every proper subfield at `n=50,53,63`. The maximum ceilings are 33,566,018; 5; and 2,100,049 respectively, all below `2^(n−1)`. The existing reviewed N53 Koblitz target order 21,044,858,204,113 exceeds its actual subfield ceiling 5, as recorded in the [baseline](../docs/reports/2026-10-16-elite-factor-base-baseline.md).
- **Derived or proved:** The [proof report](../docs/reports/2026-10-17-binary-subfield-base-rank-gate.md) derives `π_q(P)=±P` from subfield x and descended coefficients, then applies `π_q²−tπ_q+[q]=0` and Hasse to bound the order of every such point. All their sums have zero projection to a prime subgroup above the ceiling.
- **Suspected explanation:** No conjecture is needed for this exact construction. Whether *near*-subfield sets retain low solver degree and full rank is unknown.
- **Missing capability:** A target-blind near-subfield or other sparse-predicate base with independently verified nonzero subgroup projection, a certified 50–63-bit curve/subgroup, and a frozen complete-cost comparison.
- **What this evidence does not establish:** It does not rule out ordinary binary curves whose coefficients do not descend to the proposed subfield, near-subfield x sets, shifted predicates, other structured bases, or any index-calculus improvement. It measures no relation yield, degree of regularity, rank growth, or ECDLP cost.

## What would unblock it

The direct subfield construction cannot satisfy the large-prime rank requirement under the stated assumptions. An alternative construction can advance the original task when it meets these checks:

- [ ] On a committed certified 50–63-bit binary curve with fixed prime target subgroup, prepare a target-blind base whose projected points are nonzero and whose projected span contains the declared target subgroup; verify the base list, projection, and rank independently. Use a direct subfield base as a zero-rank control when the curve descends.
- [ ] At equal *realized* point or orbit count, compare its membership-system support and observed solver degree against the current orbit base and random control on planted and unplanted instances; preserve misses, censoring, and failed candidates.
- [ ] For any speed claim, finish a frozen same-point end-to-end run with base-selection/setup, collection, useful rank, linear algebra, target phase, verification, memory, and matched rho, plus progress-fidelity record and independent review.

The first condition establishes that the replacement escapes this particular rank obstruction. It does not establish solver or complete-cost advantage; the latter conditions test those separately.

## Next discriminating step

- **Action or proof obligation:** Construct and independently check one near-subfield or sparse linearized-predicate base on a certified n≈53 ordinary-binary or Koblitz prime-subgroup curve before any solver timing.
- **Inputs and controls:** Fixed curve/subgroup and base seed; pure subfield zero-rank control on descended curves; equal-realized-size current orbit and random bases; holdout targets unseen during selection.
- **Execution limits and stop condition:** A Coordinator-frozen bounded protocol must specify sample counts, memory, watchdog, artifacts, checker, and stop/censor rules. Stop candidate timing if projected-rank or point-replay control fails. This record imposes no spending cap.
- **Outcomes and next actions:** Full projected rank admits a solver comparison; zero projected rank eliminates only that candidate/curve; a failed checker invalidates it; a timeout is censored. A solver-stage gain advances to complete cost, and only a reviewed complete-cost gain updates the baseline.
- **Recheck trigger:** A certified non-descended curve, an alternative base meeting the projection/rank gate, or an independent review of the conditional proof.

A planned step is not a completed experiment. Apply the existing execution, review, budget, and archival rules before acting on it.

## Resolution and history

Unresolved as a performance pathway. The direct construction's conditional rank obstruction is derived in the linked proof; the alternative construction and complete-cost comparison remain open. Completing this record or merging its PR does not establish an index-calculus improvement.
