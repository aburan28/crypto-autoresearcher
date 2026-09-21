# Pre-ID duplicate draft — Neal slice source sampler

## Status and claim labels

- Provisional ID: `PREID-20260723-b-S05`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_density_and_level_set_oracle`.
- Class/risk/lane: algorithm / conservative / conservative pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; correct slice sampling or a verified relation is not an ECDLP result.

## Falsifiable hypothesis

There is an endpoint-only nonnegative density on signed factor-base tuples whose superlevel slices
can be sampled without enumerating the source space. Exact slice transitions would hit and replay
relations densely enough to complete factor logs and 100 fresh masked-target descents with time
and memory exponents at most `0.45`.

## Mechanism-new operation

Slice sampling augments a supplied density with a height variable and samples uniformly from the
corresponding superlevel set. It counts only if endpoints evaluate the density and delimit/sample
every slice without source membership, the chain has a proved hit bound, and accepted states
retain signed occurrence identity. Slicing an explicit source density is a control.

## Assumptions

1. Density evaluation is endpoint-only and exact, with relation fibres assigned detectable mass.
2. Stepping-out, shrinkage, or multivariate slice membership avoids source enumeration.
3. Mixing, rejected proposals, level-set geometry, restarts, and miss probability satisfy caps.
4. A sampled point has a charged exact lift to signs, repeats, and exceptional strata.
5. Frozen density/slice rules apply unchanged to known-log and fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_nonnegative_density | auxiliary_height_and_superlevel_slice_sampling | exact_relation_state_hit | certified_signed_occurrence_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — a sampler still needs an evaluable public density and mixing/hit bounds.
2. `ideas/rejected/preallocation/20260720-d_H09_gibbs_conditional_source_sampler_preid_duplicate.md` — conditional sampling assumes exact source-aware conditionals.
3. `ideas/rejected/ECDLP-IDEA-316_doob_h_transform_endpoint_source_bridge_hypothesis.md` — useful conditioning functions encode completion probability.
4. `ideas/rejected/preallocation/20260721-c_K06_jerrum_sinclair_canonical_path_source_sampler_preid_duplicate.md` — polynomial mixing on a supplied state graph does not create that graph.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — arbitrary exact restrictions and occurrence replay remain the required interface.

## Closest primary literature

- Neal, [Slice Sampling](https://doi.org/10.1214/aos/1056562461), samples from superlevel sets of a supplied unnormalized density.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no sub-rho density, slice oracle, or occurrence lift.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the matched generic baseline.

No checked source supplies the ECDLP density, slice-membership sampler, exact lift, or complete
descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, density, height law, slice construction, restrictions, lift, strata, masks, seeds, stopping rules, and verifier.
2. Compile target-independent density/slice state within `B^(9/4+o(1))`, forbidding source truth tables, target fitting, log labels, dense resultants, and Query2P1.
3. For known-log targets, charge every density call, slice expansion, rejection, shrink step, restart, and lift; verify signed point sums before admitting rows.
4. Retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse byte-identical eligible state for 100 fresh `Q+[t]P`, lift accepted states, subtract masks, and independently verify every scalar.
6. Charge setup, density/slice oracles, mixing, precision, density, replay, ambiguity, rank, logs, bit work, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal verified densities
`N^delta,N^delta_t`; density/slice/lift work and workspace `N^q,N^q_m`; rank
credit `N^r`; output `N^o`; mixing/failure amplification `N^u`; and factor-log
costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, with `0<=r<=o`. Require
`lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace
`<=B^(5/4+o(1))`. Pollard rho expected time and BSGS time/memory remain `0.50`.

## Likely fatal obstruction

Slice sampling removes proposal tuning but not the need for a useful density and exact level-set
membership. A density concentrated on relation fibres encodes the missing predicate; a smooth
proxy admits slices containing overwhelmingly many nonrelations. Exact slice boundaries or
uniform sampling over the valid source slice restore Query2P1 or source enumeration.

## Proof track

Prove an endpoint-only density and exact slice sampler, restriction-uniform relation mass,
subcap mixing/hit bounds, all-strata occurrence lift, full rank/logs, blind descent, and complete
exponents below `0.45`.

## Disproof track

Expose a source-dependent density/slice test, equal density with different source fibres,
exponentially thin valid slices, lost occurrence identity, target-trained tuning, or complete
exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied one-dimensional toy density whose labelled valid states form a wide slice.
- Negative: disconnected/thin slices, equal-density different-source fibres, empty fibres, repeated/exceptional strata, shuffled labels, and blind targets.
- Baselines: Metropolis-Hastings, Gibbs, canonical-path sampling, P1553 R4, rho, and BSGS.
- Correct stationary sampling or one hit is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact public density/slice/lift theorems, zero semantic errors at four sizes/all strata, total miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing slice oracle, false/vanishing relation slice, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-b/s05_slice_oracle_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260723-b/s05_thin_slice_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-b/s05_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not slice sampling. Correct stationarity, a wide toy
slice, or a verified tuple remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`,
and not a breakthrough.

## Exactly one next executable action

1. Freeze a toy endpoint density with one relation-bearing superlevel component and measure whether exact slice membership can be implemented without reading the source predicate.
