# Pre-ID duplicate draft — Roberts–Tweedie Langevin source diffusion

## Status and claim labels

- Provisional ID: `PREID-20260723-b-S07`; no canonical ID allocated.
- Disposition: `merged_rejected_continuous_gradient_oracle_and_rounding`.
- Class/risk/lane: algorithm / high-risk / secondary pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; diffusion convergence, Metropolis correction, or a valid row is not an ECDLP result.

## Falsifiable hypothesis

A public smooth density over a continuous relaxation of signed sources has a Langevin diffusion
that reaches exact relation basins with inverse-polynomial probability. A Metropolis-adjusted
discretization and certified rounding would support full factor logs and 100 blind descents with
complete time and memory exponents at most `0.45`.

## Mechanism-new operation

Langevin Monte Carlo adds gradient drift of a supplied log density to Brownian noise; a
Metropolis-adjusted version corrects discretization bias. It counts only if endpoints compile the
log-density gradient without source information, convergence/hit bounds survive the discrete
multimodal setting, and continuous states lift exactly to signed occurrences. A source-energy
diffusion is a control.

## Assumptions

1. The endpoint log density is differentiable, exact, and has relation basins with a proved gap.
2. Gradient evaluation avoids source enumeration, target leakage, and dense source resultants.
3. Step size, precision, accept/reject cost, mixing, restarts, and hit density satisfy both caps.
4. Rounding/lifting preserves occurrence identity, signs, repeats, and exceptional strata.
5. Frozen density and tuning remain valid on fresh scalar-blind masked targets.

## Semantic fingerprint

`public_endpoint_log_density_gradient | Langevin_drift_diffusion_and_Metropolis_correction | exact_relation_basin_hit | certified_signed_occurrence_rounding | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-d_H08_simulated_annealing_source_energy_preid_duplicate.md` — a useful continuous energy has the same supplied-predicate and exact-rounding obstruction.
2. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — accept/reject sampling still needs a public density and mixing/hit theorem.
3. `ideas/rejected/preallocation/20260723-a_R09_beck_teboulle_mirror_source_descent_preid_duplicate.md` — continuous gradient geometry does not construct an integral source inverse.
4. `ideas/rejected/ECDLP-IDEA-367_amp_onsager_source_reconstruction_hypothesis.md` — approximate continuous recovery loses rare exact support and assumes an observation law.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed replay remain mandatory.

## Closest primary literature

- Roberts and Tweedie, [Exponential Convergence of Langevin Distributions and Their Discrete Approximations](https://doi.org/10.2307/3318418), analyzes Langevin diffusions and Metropolis-adjusted discretizations for a supplied target distribution.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations but no smooth sub-rho source density or exact lift.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the comparison boundary.

No checked source constructs the ECDLP gradient, proves relation-basin mixing, or supplies exact
occurrence replay and descent. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, continuous domain, log density, gradient, discretization, correction, rounding, restrictions, strata, masks, seeds, and verifier.
2. Compile target-independent density/gradient state within `B^(9/4+o(1))`, forbidding source tuples, target-trained potentials, log labels, dense resultants, and Query2P1.
3. For known-log targets, charge every gradient, diffusion step, rejection, restart, precision repair, and lift; verify signed point sums before admitting rows.
4. Retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
5. Reuse byte-identical eligible state on 100 fresh `Q+[t]P`, lift continuous hits, subtract masks, and verify each scalar.
6. Charge construction, gradients, noise, step-size bias, acceptance, mixing, density, rounding, ambiguity, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal verified densities
`N^delta,N^delta_t`; gradient/diffusion/lift work and workspace `N^q,N^q_m`;
rank credit `N^r`; output `N^o`; rejection/mixing/failure amplification `N^u`;
and factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

The diffusion is useful only with a gradient pointing toward exact source fibres. Such a gradient
encodes the missing relation predicate; a smooth surrogate has fractional modes and exponentially
small integral basins. Metropolis correction removes discretization bias, not target-density
circularity, torpid multimodal mixing, or exact occurrence loss.

## Proof track

Prove an endpoint-only smooth density/gradient, restriction-uniform relation-basin gap, subcap
convergence and hit bounds, exact all-strata rounding, full rank/logs, blind descent, and complete
exponents below `0.45`.

## Disproof track

Show a source-derived gradient, identical local derivatives with different source fibres,
fractional traps, torpid mixing, rounding ambiguity, step-size precision blowup, or complete
exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied strongly log-concave toy density with a labelled integral mode.
- Negative: separated modes, fractional modes, equal gradients/different sources, empty fibres, exceptional strata, shuffled labels, and blind targets.
- Baselines: HMC, Metropolis-Hastings, mirror descent, AMP, P1553 R4, rho, and BSGS.
- Diffusion convergence or a corrected stationary law is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public density/gradient/lift theorems, zero semantic errors at four sizes/all strata, total miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing gradient, fractional false mode, lost occurrence, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-b/s07_gradient_provenance_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-b/s07_fractional_mode_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-b/s07_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not Langevin Monte Carlo. Convergence, corrected
stationarity, or a valid tuple remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Freeze a toy smooth relaxation with one fractional and one exact relation mode, then audit whether its endpoint-only gradient distinguishes the modes without source labels.
