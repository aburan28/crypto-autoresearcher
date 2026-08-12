# Pre-ID duplicate draft — Pomerance quadratic-sieve source collector

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V08`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_smooth_values_and_relation_only_parity_certificate`.
- Class/risk/lane: algorithm / conservative / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; smooth values, a null vector, or a valid relation are not an ECDLP break.

## Falsifiable hypothesis

An endpoint-derived quadratic polynomial has smooth values exactly at indices
encoding signed factor-base tuples. Sieving those values and solving the exponent
parity matrix would return exact occurrences, full factor-base logs, and 100 blind
descents with complete time and memory exponents `<=0.45`.

## Mechanism-new operation

The quadratic sieve evaluates a supplied polynomial near a square root of a supplied
integer, sieves values for small-prime divisibility, and finds a parity dependency.
It is ECDLP-new only if endpoints compile the polynomial and index-to-tuple inverse
without enumerating source tuples or building an explicit large-prime table.

## Assumptions

1. A compact public quadratic polynomial represents every restricted source fibre.
2. Smooth indices lift bijectively to signed occurrences across all strata.
3. Parity linear algebra preserves multiplicity and point labels needed for replay.
4. Sieving, factoring, dependency solving, replay, logs, and descent meet both caps.
5. Polynomial choice and interval are frozen before source outcomes and fresh targets.

## Semantic fingerprint

`public_endpoint_quadratic_polynomial | smooth_value_interval_sieve | exponent_parity_dependency | exact_index_to_signed_tuple_lift | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — smooth factors still require charged source provenance.
2. `ideas/rejected/ECDLP-IDEA-063_provenance_preserving_subresultant_forest_hypothesis.md` — product/remainder sieving begins after source polynomials exist.
3. `ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md` — aggregate exponent data lose exact occurrences.
4. `ideas/rejected/ECDLP-IDEA-280_exterior_algebra_multilinear_monomial_source_sieve_hypothesis.md` — sieve certificates do not create a source compiler.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable source replay remains the frontier.

## Closest primary literature

- Pomerance, [The quadratic sieve factoring algorithm](https://doi.org/10.1007/3-540-39757-4_17), starts from a supplied integer/polynomial and returns congruences of squares.
- Morrison and Brillhart, [A method of factoring and the factorization of F7](https://doi.org/10.2307/2005475), is the continued-fraction predecessor.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not construct the required quadratic index-to-source bijection.

No checked source supplies the endpoint compiler or exact occurrence lift. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, signed decks, polynomial compiler, sieve interval/base, large-prime policy, restrictions, masks, and verifier.
- Build target-independent state within `B^(9/4+o(1))`, excluding enumerated tuple indices, explicit large-prime tables, target fitting, and logs.
- Charge polynomial evaluation, sieve updates, trial divisions, partial merges, parity rows, nullspace, source replay, and every failure.
- Verify `max(d_FB+32,1000)` independent elliptic rows, rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical eligible state on 100 fresh masked targets, subtract masks, and verify scalars.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, sieve/replay work `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity/failure `N^u`, log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`;
rho/BSGS remain `0.50`.

## Likely fatal obstruction

Quadratic sieving accelerates smoothness detection after a scalar-indexed polynomial
exists. A point-faithful index is already a source catalogue or scalar labelling.
The parity matrix forgets even multiplicities and returns a relation-only square
certificate; restoring exact signed tuples and arbitrary restrictions recreates the
missing source predicate.

## Proof track

Prove endpoint-only polynomial/index compilation, exact all-strata index-to-source
inversion, charged smoothness and partial merges, full rank/logs, blind descent, and
both cost caps.

## Disproof track

Expose a source/scalar-labelled index, freeze sieve/parity output while changing
fibres, show large-prime provenance is explicit, or reach exponent `0.50`.

## Positive and negative controls

- Positive: supplied quadratic-sieve polynomials with planted labelled smooth indices.
- Negative: equal parity matrices/different sources, repeated primes, false partial merges, empty fibres, post-hoc intervals, and fresh targets.
- Baselines: IDEAS 053/063/117/280, CFRAC, P1553 R4, rho, and BSGS.
- Smoothness or a correct null vector remains relation-only evidence.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/inverse, zero provenance errors, charged relation density, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one scalar/source index, parity-source collision, explicit large-prime table, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v08_sieve_index_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v08_parity_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v08_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not the quadratic sieve. Correct smooth values,
dependencies, factors, relations, or validator passes remain `toy`, `heuristic`,
`model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Trace every datum needed to map one sieved smooth index back to a signed elliptic tuple and mark the first source-bearing step.
