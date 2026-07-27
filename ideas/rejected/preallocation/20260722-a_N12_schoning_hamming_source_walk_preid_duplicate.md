# Pre-ID duplicate draft — Schöning Hamming source walk

## Status and claim labels

- Prospect: `20260722-a-N12`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / high-risk / relative high-risk screen.
- State: `merged_rejected_supplied_kcnf_random_walk_and_exponential_restart_cost`.
- Evidence: exhaustive ledger/corpus and primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a randomized SAT guarantee or valid relation is not an ECDLP breakthrough.

## Falsifiable hypothesis

Public endpoints compile into a bounded-width `k`-CNF whose Boolean models decode exact signed factor-base relations. Schöning's restart-and-Hamming-walk algorithm would exploit a provable basin around models, returning enough occurrence-labelled relations and 100 blind descents with complete time/memory exponents below rho/BSGS.

## Mechanism-new operation

The screened operation starts from a random assignment, repeatedly chooses an unsatisfied `k`-clause and flips a random literal variable for a bounded walk, then restarts. It counts only if the `k`-CNF is endpoint-derived/compact, Boolean dimension and restart probability fit the gates, and models decode signed occurrences.

## Assumptions

1. A compact exact bounded-`k` endpoint CNF exists for every stratum and restriction.
2. The number of Boolean variables is small enough that the proven restart factor is sub-rho after conversion to `N`.
3. Clause selection and random bits are target-blind and fully charged.
4. Models preserve occurrence labels, signs, multiplicities, and point equality.
5. The same compiler/walk policy serves known-log rows and fresh masked targets.

## Semantic fingerprint

`public_endpoint_bounded_kCNF | Schoning_unsatisfied_clause_Hamming_walk | randomized_model_hit | signed_occurrence_decode | complete_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted decision/replay is not supplied by a SAT walk.
2. `ideas/rejected/ECDLP-IDEA-147_moser_tardos_relation_resampling_hypothesis.md` — random local updates require a represented constraint system and favorable structure.
3. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — a random walk on supplied source state does not create support or certify emptiness.
4. `ideas/rejected/preallocation/20260722-a_N11_walksat_noisy_source_local_search_preid_duplicate.md` — noisy SAT search inherits compiler, failure, and source-decoding costs.
5. `ideas/rejected/ECDLP-IDEA-148_isolation_weight_lowest_monomial_source_extractor_hypothesis.md` — randomization after representation cannot remove source construction.

## Closest primary literature

- Schöning, [A Probabilistic Algorithm for k-SAT and Constraint Satisfaction Problems](https://doi.org/10.1109/SFFCS.1999.814612), proves a randomized search bound for a supplied bounded-width formula; it does not compile elliptic sources or make the Boolean dimension small.
- Selman, Kautz, and Cohen, [Noise Strategies for Improving Local Search](https://cdn.aaai.org/AAAI/1994/AAAI94-051.pdf), is the heuristic local-search control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides endpoint equations but no bounded-`k` source-faithful CNF.

No checked source supplies the proposed compiler/dimension reduction/source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, `B=N^(1/5)`, factor base/decks, exceptional strata, bounded-`k` CNF, Boolean encoding, walk length/restarts, clause/literal selection, restrictions, masks, seeds, and verifier.
2. Build target-independent clauses/state within `B^(9/4+o(1))`; forbid explicit source products, target-fitted encodings, log labels, dense resultants, and Query2P1.
3. For known-log `R`, execute every preregistered walk/restart, decode actual `(A_i,epsilon_i)`, and verify `sum epsilon_i A_i=R`; retain failures.
4. Charge the proven/observed reciprocal hit density, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse byte-identical target-independent state for fresh `Q+[t]P`, decode/verify a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 blind targets.
6. Charge compiler/clauses, Boolean dimension, all steps/restarts/failures, random bits, restrictions, output, verification, density confidence, rank, factor solve, masks, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, freeze `beta=1/5`. Let setup/state be `N^a,N^a_m`; reciprocal relation/blind hit costs `N^delta,N^delta_t`; per-walk query/workspace `N^q,N^q_m`; rank credit `N^r`; output `N^o`; amplification/confidence `N^u`; factor-log costs `N^ell,N^ell_m`. Charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory are exponent `0.50`. The SAT theorem's exponential factor must be translated through the actual Boolean variable count; no restart is free.

## Likely fatal obstruction

Schöning's algorithm starts after a bounded-`k` CNF exists and its exponent is in the number of Boolean variables. Encoding five choices from `B` may use few index bits only if clauses can evaluate the elliptic relation without expanding source incidence; standard encodings instead materialize large tables/circuits. The walk cannot certify empty restrictions, and the proven restart cost can exceed rho after honest dimension conversion. This is a solver substitution, not an endpoint operation.

## Proof track

Construct a compact endpoint-only bounded-`k` CNF, prove its Boolean dimension/clauses/source decoder and mask-uniform Schöning hit bound yield complete `lambda,mu<=0.45` descent.

## Disproof track

Trace a clause to source enumeration, show CNF dimension/restart exponent reaches `0.50`, find an empty fibre indistinguishable from failure, expose an aliasing model, or violate either cap.

## Positive and negative controls

- Positive: supplied planted bounded-`k` toy CNFs with exact exhaustive basin sizes and labelled models.
- Negative: empty formulas, narrow basins, encoding aliases, target shifts, repeated strata, seed-selection traps, and blind targets.
- Baselines: WalkSAT, Moser–Tardos, Metropolis, P1553 R4, rho, and BSGS.
- Controls are toy/model-bound; a random-walk hit is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only after exact four-size semantics, frozen restart confidence, charged signed replay, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied clauses, dimension/restart exponent at least `0.50`, empty-fibre ambiguity, lost occurrence, selection leakage, or cap failure.
- A model, relation, or validator pass is not a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n12_kcnf_dimension_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n12_hamming_basin_controls.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n12_cost_analysis.md`

The prospective artifact root is not created.

## Interpretation boundary

This rejects the screened ECDLP transplant, not Schöning's SAT algorithm. Evidence remains toy, heuristic, model-bound, and novelty-unverified. No experiment, lower bound, or breakthrough is claimed.

## Exactly one next executable action

1. Write the bounded-`k` CNF dimension audit and translate the proven restart factor into the frozen `N`-exponent before any run.
