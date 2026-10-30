# Solver on the elliptic component of the same-field quartic Jacobian

- **Status:** open (local implementation/theory obligation; no official research state)
- **Kind:** implementation gap and missing solver/cost proof
- **Affected work:** TASK-20261025-7144c5, F7; `report.md`, `checks.json`
- **Next action owner:** Coordinator to assign a prospective implementation handoff
- **Last updated:** 2026-10-25

## Problem

A costed DLP algorithm on the injected P-256 order-r component of J_C has not been supplied. The explicit cover C: u⁴=x³−3x+b over Fp and π(x,u)=(x,u²) supplies pullback/norm correspondence and smooth plane-quartic geometry, but neither full plane-quartic divisor arithmetic nor a target-component relation solver is implemented here.

The original task's explicit map/genus/subgroup screen is fulfilled. The missing capability blocks only downstream solver or cost claims. It does not block construction, imply nonexistence, or give negative evidence about every cover. The same source r≈p is retained; the ambient Jacobian has dimension three. A full-Jacobian algorithm in another subgroup/field regime is insufficient evidence.

## Evidence and uncertainty

- **Observed:** seven nonhyperelliptic fibre checks and seven genus-two fibre checks, including Frobenius-stable nonsplit supports; successful exact Sage receipts and commands are retained.
- **Derived:** π_*π*=[2], gcd(2,r)=1 and source-factor Frobenius compatibility prove subgroup injection and scalar recovery. The quartic Prym polynomial has form T⁴+A T²+p²; A is unknown. Its order and extra r-multiplicity are not measured.
- **Suspected explanation:** no causal explanation is proposed for solver difficulty; no relation solver has run.
- **Missing capability:** arbitrary-class plane-quartic arithmetic/norm routines; complete relation/rank/individual-log method for the elliptic image; paired total-cost validation.
- **Does not establish:** a speed gain, impossibility, full r-primary decomposition or broad cover classification.

## What would unblock it

- [ ] Implement arbitrary-class pullback/norm and divisor arithmetic on this exact curve, with principal-divisor identities, exceptional cases and [2] composition checks.
- [ ] Supply a solver formulation that handles both transported inputs, proves or measures useful relation rank modulo r, includes individual logarithm and verifies the recovered scalar on E.
- [ ] Under a new prospective task/protocol, price the complete process against the same-source baseline with setup, failures, memory, recovery and fixed-target preprocessing accounted for.

The first item establishes executable correspondence support; it alone does not meet the second or third. Computing A would refine the ambient group, without meeting the solver conditions.

## Next discriminating step

Implement and certify arbitrary-class arithmetic and norm for the displayed quartic, with its explicit source fibres as positive controls, a coordinate-isomorphic source control, zero/principal divisor controls and out-of-image classes. Keep the handoff's one-process/2GiB resource envelope for initial implementation validation. A success enables a separately specified solver test; a bounded implementation failure records its precise case; an infrastructure failure asserts nothing about the mathematics. Recheck when that implementation or an independently justified image-specific solver becomes available.

## Resolution and history

2026-10-25: constructed the explicit same-field cover and exact subgroup correspondence. Solver/cost obligation remains unresolved. This file follows the repository problem template inside the assigned write scope; registration in a shared problem index, if needed, belongs to the Coordinator's exclusive archival/synthesis scope.
