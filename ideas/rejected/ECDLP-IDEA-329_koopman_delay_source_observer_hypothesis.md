# ECDLP-IDEA-329 — Koopman delay-coordinate source observer

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_delay_observables_require_a_source_trajectory_and_endpoint_map_is_many_to_one`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Koopman eigenfunction, delay embedding, valid relation, or toy trajectory reconstruction is not an ECDLP break.

## Falsifiable hypothesis

The serial elliptic addition process admits a compact public observable family whose Koopman-delay coordinates embed each hidden signed source trajectory and permit exact endpoint-to-source inversion within the P1553 bounds.

## Mechanism-new operation

The screened operation is **treat sequential factor addition as dynamics, lift public observables linearly under a Koopman operator, form delay coordinates from the endpoint, and invert the embedded trajectory to factor points**. This merges with IDEAs 056, 070, 120, 267, and 308: Koopman theory starts from a known transformation or flow, while delay reconstruction requires time-series observations along one trajectory. An ECDLP endpoint is only a many-to-one terminal observation with no supplied ancestry, so constructing the missing delay sequence is the source router.

## Assumptions

1. A target-independent finite observable dictionary closes under elliptic additions without pair-state materialization.
2. Endpoint data determine enough delays without observing or guessing hidden intermediate sums.
3. Delay coordinates embed all signed and repeated source trajectories and invert canonically.
4. Dictionary construction, Koopman action, delays, inversion, output, rank, factor logs, descent, verification, and memory are charged.
5. The same observables invert fresh masked targets.

## Semantic fingerprint

`serial_elliptic_dynamics | finite_Koopman_observable_closure | endpoint_derived_delay_embedding | exact_source_trajectory_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1477`, the serial forward/backward endpoint-state representation.
2. `inputs/ledger_inventory.json` — imported `P1478`, the compact one-transition identity and dense composition control.
3. `inputs/ledger_inventory.json` — imported `ECFG-H680`, the recursive source-resolving circuit hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the canonical ancestry-edge noncompression boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the exact differential-state noncompression control.

## Closest primary literature

- Koopman, [Hamiltonian systems and transformation in Hilbert space](https://doi.org/10.1073/pnas.17.5.315), represents observables of a supplied transformation or dynamical flow by a linear operator.
- Takens, [Detecting strange attractors in turbulence](https://doi.org/10.1007/BFb0091924), obtains delay-coordinate reconstruction from observed time-series values under embedding hypotheses; it does not create those observations from one terminal value.
- Hermann and Krener, [Nonlinear controllability and observability](https://doi.org/10.1109/TAC.1977.1101601), characterizes observability from supplied input-output dynamics; it does not create missing source observations.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies terminal endpoint equations, not a hidden addition trajectory.

No checked source supplies endpoint-derived delays, exact source inversion, or the complete sub-rho path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, coloured factor decks, addition order, observable dictionary, delay convention, masks, and verifier.
2. From each known-log endpoint alone, derive delay coordinates, recover every exact factor trajectory, and verify the relation.
3. Collect at least `B` independent rows, solve all factor logs, and independently verify them.
4. Apply the identical observable/delay inverse to fresh masked targets with no trajectory advice.
5. Substitute factor logs, remove masks, retain ambiguity, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, observable propagation/inversion excluding emission `N^q,N^q_m`, verified rank `N^r`, source output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`, define

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every observable coefficient, hidden-delay constructor, spectral solve, trajectory branch, and verification is charged, with `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Koopman linearity acts on a known dynamical map; delay reconstruction separately consumes observations along a trajectory. The endpoint forgets the ordered factor inputs and intermediate sums. Delay vectors cannot be computed from a single terminal state unless an inverse/ancestry oracle is already available; a source-faithful observable dictionary restores pair or path state.

## Proof track

Construct a compact endpoint-derived delay system, prove injectivity and exact inversion on all strata, and then prove relation rank, factor-log completion, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Exhibit two valid source trajectories with the same endpoint and all public endpoint-derived observables, or prove that computing one distinguishing delay solves the missing transition/source problem.

## Positive and negative controls

- Positive: fully observed toy dynamics with a known embedding must reconstruct planted trajectories.
- Negative: source-permuted or ancestry-colliding trajectories with the same endpoint must not be distinguished without charged intermediate observations.
- Baselines: IDEAs 056/070/120/267/308, explicit path enumeration, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only after endpoint-only delay and inversion theorems, exact all-strata recall, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if any delay uses a hidden intermediate, dictionary state reaches `B^3`, two trajectories collide, or either complete exponent reaches `0.50`.
- Reconstruction from supplied trajectories is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-329/endpoint_delay_observability_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-329/trajectory_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-329/independent_observer_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-329/cost_analysis.md`

## Interpretation boundary

This rejects the specified endpoint-only Koopman-delay route, not Koopman methods generally. A valid observable model or toy trajectory is not source-complete ECDLP evidence or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-329/endpoint_delay_observability_receipt.md` proving whether any nonconstant delay is computable from the terminal endpoint without importing an intermediate source state.
