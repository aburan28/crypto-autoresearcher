# Pre-ID duplicate draft — Pritchard ABC source posterior

## Status and claim labels

- Provisional ID: `PREID-20260723-b-S09`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_simulator_summary_and_approximate_acceptance`.
- Class/risk/lane: algorithm / high-risk / secondary pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; posterior concentration, a simulation match, or a valid tuple is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-only simulator of signed source summaries has a sufficient statistic and tolerance
schedule for which approximate Bayesian computation concentrates on exact elliptic-relation
sources with inverse-polynomial acceptance. Accepted simulations would replay occurrences for full
factor logs and 100 blind descents with complete time and memory exponents at most `0.45`.

## Mechanism-new operation

Approximate Bayesian computation draws parameters from a supplied prior, runs a supplied
simulator, and accepts when simulated summaries are close to observed summaries. It counts only
if endpoints provide a sub-rho source simulator and an exact sufficient summary whose zero
tolerance gives signed occurrence replay. Simulating explicit source tuples and post-selecting
near endpoint matches is a control.

## Assumptions

1. The simulator is endpoint-derived and does not enumerate or sample from a source catalogue.
2. The summary is sufficient for exact signed-source identity across every exceptional stratum.
3. Tolerance, acceptance density, simulations, adaptation, and false-match probability satisfy caps.
4. Accepted latent states include occurrence labels rather than aggregate summaries only.
5. Frozen prior/simulator/summary/tolerance rules work on fresh scalar-blind masked targets.

## Semantic fingerprint

`public_endpoint_generative_source_simulator | summary_distance_rejection_ABC | exact_zero_tolerance_relation_acceptance | latent_signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-a_E09_bootstrap_particle_source_filter_preid_duplicate.md` — simulation/filtering assumes a state transition and observation model carrying source semantics.
2. `ideas/rejected/preallocation/20260720-d_H10_em_latent_source_mixture_preid_duplicate.md` — latent-variable inference consumes a supplied model and can merge sources.
3. `ideas/rejected/ECDLP-IDEA-367_amp_onsager_source_reconstruction_hypothesis.md` — approximate inference assumes a tractable generative observation law and loses exact support.
4. `ideas/rejected/preallocation/20260723-a_R04_hutchinson_trace_source_estimator_preid_duplicate.md` — matching aggregate summaries does not identify exact occurrences.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted source semantics and replay remain the required owner.

## Closest primary literature

- Pritchard, Seielstad, Perez-Lezaun, and Feldman, [Population Growth of Human Y Chromosomes: A Study of Y Chromosome Microsatellites](https://doi.org/10.1093/oxfordjournals.molbev.a026091), performs likelihood-free rejection using simulations and summary matching for a supplied demographic model.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no sub-rho source simulator or exact sufficient statistic.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the ECDLP simulator, sufficient summary, exact acceptance inverse, or
complete descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, prior, simulator, summary, metric, tolerance schedule, restrictions, lift, strata, masks, seeds, and verifier.
2. Compile target-independent simulator/summary state within `B^(9/4+o(1))`, forbidding source-product generation, target fitting, scalar logs, dense resultants, and Query2P1.
3. For known-log targets, charge every simulation, summary, rejection, adaptation, tolerance reduction, restart, and latent lift; verify signed point sums before rows.
4. Retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse byte-identical eligible state for 100 fresh `Q+[t]P`, replay accepted latent sources, subtract masks, and independently verify every scalar.
6. Charge construction, simulator cost, acceptance density, summaries, precision, false matches, replay, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal verified acceptance
densities `N^delta,N^delta_t`; simulation/summary/lift work and workspace
`N^q,N^q_m`; rank credit `N^r`; output `N^o`; tolerance/false-match/failure
amplification `N^u`; and factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

ABC avoids a likelihood only by assuming a simulator. A simulator emitting relation-correlated
signed sources is already the missing source generator; a generic source simulator has relation
acceptance equal to brute-force density. Nonzero tolerance admits false relations, while zero
tolerance and sufficient summaries return to exact endpoint membership and occurrence replay.

## Proof track

Prove an endpoint-only sub-rho simulator, exact restriction-sufficient summary, inverse-polynomial
zero-tolerance acceptance, all-strata replay, full rank/logs, blind descent, and complete costs.

## Disproof track

Show source enumeration in the simulator, equal summaries with different fibres, a false accepted
relation, vanishing zero-tolerance density, target-trained summaries, or complete exponent at
least `0.50`.

## Positive and negative controls

- Positive: a supplied finite generative toy model with a sufficient labelled summary.
- Negative: equal summaries/different sources, nonzero-tolerance false matches, empty fibres, rare relations, shuffled labels, exceptional strata, and blind targets.
- Baselines: particle filtering, EM, AMP, trace summaries, P1553 R4, rho, and BSGS.
- Posterior concentration or approximate calibration is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact public simulator/summary/lift theorems, zero false accepts at four sizes/all strata, total miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing simulation, insufficient summary, false accept, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-b/s09_simulator_provenance_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-b/s09_summary_collision_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-b/s09_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not approximate Bayesian computation. A calibrated
posterior, close simulation, or verified tuple remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Enumerate the smallest two signed-source fibres with the same frozen ABC summary but different exact relation status, and record the simulator inputs needed to separate them.
