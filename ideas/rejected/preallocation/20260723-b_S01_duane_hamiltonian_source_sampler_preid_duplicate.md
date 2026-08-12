# Pre-ID duplicate draft — Duane Hamiltonian source sampler

## Status and claim labels

- Provisional ID: `PREID-20260723-b-S01`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_energy_gradient_and_continuous_relaxation`.
- Class/risk/lane: algorithm / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; acceptance, mixing, or a verified relation is not an ECDLP break.

## Falsifiable hypothesis

A public differentiable relaxation of signed factor-base tuples has a Hamiltonian flow whose
typical trajectories reach exact elliptic-relation fibres with inverse-polynomial probability.
Metropolis correction and an exact lift would then supply full-rank relations and 100 fresh
masked-target descents with complete time and memory exponents at most `0.45`.

## Mechanism-new operation

Hybrid/Hamiltonian Monte Carlo augments a supplied target density with momentum, integrates
Hamiltonian dynamics using its gradient, and applies an accept/reject correction. It counts here
only if endpoints compile the potential and gradient without source enumeration, the continuous
trajectory has a charged exact lift to signed occurrences, and restriction queries remain exact.
Running HMC on an explicit source energy is a control, not a new ECDLP operation.

## Assumptions

1. A target-independent endpoint relaxation has exact relation minima separated by a proved gap.
2. Potential and gradient evaluations avoid source tables, dense resultants, and hidden completion.
3. Mixing, integrator error, rejection, restarts, and relation-hit probability satisfy both caps.
4. Rounding/lifting preserves signs, multiplicities, and every exceptional elliptic stratum.
5. The frozen state is scalar-blind and reusable on fresh masks without target-trained tuning.

## Semantic fingerprint

`public_endpoint_continuous_potential | Hamiltonian_momentum_flow_and_acceptance | exact_relation_basin_hit | certified_rounding_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — any accept/reject chain needs a public target-density ratio and a proved hit bound.
2. `ideas/rejected/preallocation/20260720-d_H08_simulated_annealing_source_energy_preid_duplicate.md` — a useful source energy already contains the missing relation predicate.
3. `ideas/rejected/preallocation/20260723-a_R09_beck_teboulle_mirror_source_descent_preid_duplicate.md` — continuous geometry and gradients do not supply an exact source inverse.
4. `ideas/rejected/ECDLP-IDEA-367_amp_onsager_source_reconstruction_hypothesis.md` — continuous reconstruction assumes a tractable observation law and loses exact occurrence semantics.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable existence and signed replay remain the live owner.

## Closest primary literature

- Duane, Kennedy, Pendleton, and Roweth, [Hybrid Monte Carlo](https://doi.org/10.1016/0370-2693(87)91197-X), uses molecular-dynamics trajectories and a Metropolis correction for a supplied differentiable action.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no sub-rho differentiable source relaxation or lift.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the comparison boundary.

No checked source supplies the endpoint potential, gradient, exact rounding theorem, or full
descent. The ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, factor base, continuous domain, potential, metric, integrator, rounding, restrictions, strata, masks, seeds, and independent verifier.
2. Compile target-independent potential/gradient state within `B^(9/4+o(1))`, forbidding source-labelled tuples, scalar logs, target fitting, and Query2P1.
3. For known-log targets, charge every trajectory, gradient call, rejection, restart, and lift; admit a row only after replaying signed points and verifying the elliptic sum.
4. Retain failures and dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor-base logarithms.
5. Reuse byte-identical eligible state on 100 fresh `R=Q+[t]P`, lift signed tuples, subtract masks, and independently verify every recovered scalar.
6. Charge setup, gradients, integration precision, acceptance, mixing, density, lifting, ambiguity, rank, factor solve, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal relation and target
densities `N^delta,N^delta_t`; trajectories, gradients, and lift cost/workspace
`N^q,N^q_m`; rank credit `N^r`; output `N^o`; ambiguity, rejection, and failure
amplification `N^u`; factor-log solve `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, with `0<=r<=o`. Require
`lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace
`<=B^(5/4+o(1))`. Pollard rho remains expected-time exponent `0.50`; BSGS remains
time/memory exponent `0.50`.

## Likely fatal obstruction

HMC accelerates sampling only after a differentiable target action is supplied. An action whose
gradient guides trajectories toward exact elliptic source fibres either evaluates the missing
source predicate or is a heuristic relaxation with no exact gap. Continuous rounding merges
distinct signs and exceptional strata; making it exact restores source-scale state or search.

## Proof track

Prove an endpoint-only potential/gradient compiler, restriction-uniform energy gap, subcap mixing
and hit bounds, exact all-strata lift, full-rank relation collection, blind descent, and complete
cost exponents below `0.45`.

## Disproof track

Exhibit equal public potentials with different source fibres, a gradient term derived from source
incidence, a fractional minimum with no relation, rounding ambiguity, torpid mixing, or a complete
exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied smooth toy energy with one planted labelled integral minimum.
- Negative: flat/multimodal actions, equal-energy different-source fibres, fractional minima, empty fibres, exceptional strata, shuffled labels, and fresh blind targets.
- Baselines: Metropolis-Hastings, annealing, mirror descent, P1553 R4, rho, and BSGS.
- Numerical convergence, high acceptance, or one valid tuple remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors across four sizes/all strata, a proved public compiler and exact lift, total miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing gradient, false relation basin, ambiguous lift, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-b/s01_potential_provenance_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-b/s01_rounding_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260723-b/s01_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not Hamiltonian Monte Carlo. Correct dynamics,
acceptance, or a verified relation remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Construct the smallest toy pair with identical endpoint-derived relaxed potential data but different exact signed-source fibres, and record whether any source-free rounding rule distinguishes them.
