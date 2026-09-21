# ECDLP-IDEA-308 — Hermann–Krener nonlinear source observer

## Status and claim labels

- Class: `nonlinear_systems_representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_endpoint_output_is_not_source_observable`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a full-rank toy observability matrix, convergent supplied-state observer, valid relation, or correct transition is not an ECDLP break.

## Falsifiable hypothesis

A serial summation-polynomial chain can be treated as a finite-field nonlinear state system whose public endpoint output and Hermann–Krener observation algebra distinguish the hidden intermediate states and exact factor inputs, allowing a target-uniform nonlinear observer to generate relations and blind descents below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile successive factor additions as a nonlinear state transition, close the endpoint output under iterated Lie derivatives or finite-field observation-algebra analogues, and invert the resulting observability map with a nonlinear source observer**. This is not merely solving a dense resultant: it proposes that dynamic observation rank exposes the hidden ancestry. But the ECDLP relation fiber is deliberately many-to-one at the endpoint, and the proposed transition supplies neither a time series nor known input excitations that distinguish its hidden factor inputs. Source-labelled outputs, target-trained probes, or a full materialized state trajectory restore the missing path data. The proposal therefore merges with IDEAs 006, 070, 120, 186, and 267.

## Assumptions

1. The serial summation chain defines a target-uniform nonlinear system and observation algebra over the finite field without enumerating source inputs or paths.
2. Endpoint-derived observations and public excitations satisfy an exact finite-field analogue of the Hermann–Krener rank condition on every signed, collision, and nonreduced stratum.
3. Local observability upgrades to a canonical global biconditional inverse returning all exact factor inputs, not merely intermediate aggregate states.
4. Transition compilation, derivative or difference closure, observer construction, exceptional loci, outputs, relation rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`serial_summation_state_system | endpoint_output_map | Hermann_Krener_observation_algebra | nonlinear_exact_source_observer | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1477`, the serial three-factor forward/backward state-polynomial control whose backward recurrence becomes dense.
2. `inputs/ledger_inventory.json` — imported `P1478`, the exact one-transition norm primitive whose composition loses compact source membership.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank transposed matrix without a low-state source decoder.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the source-recoverable product whose materialization fails the cost gate.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator and transposed join.

## Closest primary literature

- Hermann and Krener, [Nonlinear controllability and observability](https://doi.org/10.1109/TAC.1977.1101601), gives differential-geometric rank conditions for nonlinear systems with specified dynamics and observation histories; it does not turn one many-to-one finite-field endpoint into labelled hidden inputs.
- Krener and Isidori, [Linearization by output injection and nonlinear observers](https://doi.org/10.1016/0167-6911(83)90037-3), studies observer construction under structural hypotheses on supplied nonlinear systems, not exact inversion of a static summation fiber.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations without a source-observable dynamical realization.

No checked source proves the required finite-field global observability, exact input reconstruction, blind target descent, or complete sub-rho cost path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, serial transition, state and input spaces, public output/probe schedule, observation algebra, observer, masks, and independent verifier.
2. For random known-log endpoints, generate the frozen observation history without enumerating hidden factor inputs or injecting source-dependent probes.
3. Run the observer, return every candidate intermediate state and exact signed factor input, and independently verify each endpoint relation.
4. Collect independent verified rows, solve the complete factor-log system, and verify every recovered factor logarithm.
5. Apply the identical system, probe schedule, and observer to fresh masked targets `Q+[t]P` without target-trained outputs, initial states, or source advice.
6. Substitute factor logs, remove masks, retain all local-chart, state, input, and sign ambiguity, and return every scalar candidate.
7. Accept only exact `[x]P=Q`, charging observation closure, state trajectories, probes, exceptional strata, outputs, failures, rows, logs, descent, verification, time, and peak memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one observation-algebra/observer/inverse attempt `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, target ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes transition and observation closure, every probe, observer solve, exact input inverse, and independent verification; `o` includes all states, branches, and input tuples returned. Rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Observability can distinguish states only through differing output histories under known dynamics and inputs. A single elliptic endpoint is shared by many valid factor paths, while the factor inputs and intermediate states are hidden and no free repeated trajectory is available. Iterating formal Lie derivatives of endpoint data does not create new information about which compatible source path occurred. If the probes expose factor-specific responses, they encode source labels; if the observer stores all compatible trajectories, its state or output is the original source-fiber enumeration.

## Proof track

Define a compact finite-field observation algebra from public endpoint data, prove an all-strata global observability and exact-input biconditional without source-labelled probes, then prove sufficient independent relation density, reusable factor logs, blind descent, and full `lambda,mu<=0.45`.

## Disproof track

Exhibit two distinct exact factor paths with identical complete public observation histories, prove the observation algebra is constant on a positive-size source fiber, or show that separating probes/trajectory state require source incidence or exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied finite nonlinear system with known inputs and a globally injective frozen observation map must reconstruct its labelled state trajectory.
- Negative: two distinct factor paths with the same endpoint and public probe history must remain ambiguous and must not be counted as successful observation.
- Baselines: explicit forward/backward path storage, dense elimination, IDEAs 006/070/120/186/267, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an independent all-strata observability/input biconditional, 1,000 verified rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if two source paths share the full public observation history, source-labelled probes are required, or charged observation/state/output reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-308/nonlinear_observability_source_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-308/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-308/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-308/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of endpoint-only Hermann–Krener source observation for the stated serial realization, not a universal impossibility theorem for nonlinear observers. A rank condition on a labelled toy system or correct transition does not provide exact factor recovery, blind scalar descent, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-308/nonlinear_observability_source_theorem.md` proving either a public all-strata exact-input observability map or an indistinguishable-path counterexample before constructing an observer.
