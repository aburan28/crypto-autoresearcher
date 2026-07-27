# Pre-ID duplicate draft — WalkSAT noisy source-local search

## Status and claim labels

- Prospect: `20260722-a-N11`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / high-risk / secondary screen.
- State: `merged_rejected_supplied_cnf_heuristic_local_search_without_empty_certificate`.
- Evidence: exhaustive ledger/corpus and primary-literature review only; no experiment ran.
- Labels: all finite controls are toy; success-rate extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a local-search hit or relation is not an ECDLP result.

## Falsifiable hypothesis

An endpoint-derived CNF for signed relations has a landscape in which WalkSAT's mixture of greedy low-break flips and random unsatisfied-clause flips reaches occurrence-labelled models with a uniform probability large enough to collect full-rank rows and solve 100 blind targets below rho/BSGS.

## Mechanism-new operation

The screened operation selects an unsatisfied clause and flips either a variable minimizing newly broken clauses or a random variable, with restarts/noise. It counts only if clauses/variables are endpoint-derived without source catalogues, success probabilities are proven rather than post-hoc, and models replay signed occurrences.

## Assumptions

1. A compact exact all-strata endpoint CNF exists.
2. The frozen noise/restart policy has a uniform lower-bounded hit probability on known-log and blind targets.
3. Clause-violation/break scores are DLP-free and fully charged.
4. Reached models decode occurrence labels/signs without aliases.
5. Failure statistics and restarts are retained; no post-hoc selector is used.

## Semantic fingerprint

`public_endpoint_relation_CNF | WalkSAT_noisy_clause_flip | heuristic_model_hit | signed_occurrence_decode | relation_campaign_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence/replay cannot be inferred from heuristic hits.
2. `ideas/rejected/ECDLP-IDEA-147_moser_tardos_relation_resampling_hypothesis.md` — randomized local resampling assumes represented constraints and a favorable event structure.
3. `ideas/rejected/preallocation/20260720-d_H08_simulated_annealing_source_energy_preid_duplicate.md` — noisy local optimization on a supplied landscape lacks an exact source compiler.
4. `ideas/rejected/preallocation/20260722-a_N03_dpll_source_unit_branching_preid_duplicate.md` — complete CNF search already exposes compiler and source-decoding costs.
5. `ideas/rejected/ECDLP-IDEA-148_isolation_weight_lowest_monomial_source_extractor_hypothesis.md` — randomized isolation/search starts after the source family is represented.

## Closest primary literature

- Selman, Kautz, and Cohen, [Noise Strategies for Improving Local Search](https://cdn.aaai.org/AAAI/1994/AAAI94-051.pdf), studies mixed random-walk/greedy search for supplied SAT instances; it gives no elliptic compiler or uniform guarantee here.
- Davis, Logemann, and Loveland, [A Machine Program for Theorem-Proving](https://doi.org/10.1145/368273.368557), is the complete-search control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not furnish the CNF or landscape theorem.

No checked source constructs the proposed ECDLP landscape or descent guarantee; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, `B=N^(1/5)`, factor base/decks, exceptional strata, CNF, initialization, noise, restart/step budgets, score updates, restrictions, masks, seeds, and verifier.
2. Build target-independent clauses/state within `B^(9/4+o(1))`; forbid explicit source products, target-fitted tuning, log labels, dense resultants, and Query2P1.
3. For known-log `R`, run all preregistered seeds including failures, decode candidate `(A_i,epsilon_i)`, and verify the point relation before retaining a row.
4. Estimate/charge reciprocal hit density, collect at least `max(d_FB+32,1000)` verified rows, retain dependencies, require rank `d_FB`, and solve all factor logs.
5. Reuse byte-identical state/policy for fresh `R=Q+[t]P`, decode/verify a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 blind targets without selection leakage.
6. Charge compiler work, clauses/literals, score maintenance, all flips/restarts/failures, output, verification, density confidence, rank, factor solve, masks, randomness, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, define setup/state `N^a,N^a_m`, reciprocal hit costs `N^delta,N^delta_t`, query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`, amplification/confidence `N^u`, factor-log costs `N^ell,N^ell_m`. Charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, online work/workspace `<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory are exponent `0.50`; failed restarts and statistical confidence are charged.

## Likely fatal obstruction

WalkSAT searches an explicit CNF and offers no certificate for an empty restricted fibre. Its empirical landscape can change across targets; noise tuning or reporting only successful seeds is post-hoc selection. A compact CNF/source decoder is already the missing operation, and absent a uniform hit theorem the complete reciprocal density can be rho-scale or worse. Thus it merges with stochastic solver/annealing controls.

## Proof track

Construct the endpoint CNF and prove a mask-uniform hitting bound for the frozen WalkSAT chain, exact source decoding, full-rank relation density, and complete sub-rho costs including failures.

## Disproof track

Find a source-derived clause, a target family with exponentially small hit probability, an empty fibre indistinguishable from timeout, a lost occurrence, selection leakage, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied planted toy CNFs with frozen seeds and exact exhaustive hit probabilities.
- Negative: empty formulas, deceptive local minima, target shifts, seed-selection traps, aliasing models, repeated strata, and blind targets.
- Baselines: simulated annealing, Moser–Tardos, DPLL, P1553 R4, rho, and BSGS.
- Controls are toy/model-bound; a hit is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only after zero semantic errors at four sizes, preregistered confidence bounds, charged source replay, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one supplied clause catalogue, empty-fibre ambiguity, selection leakage, lost source, cap breach, or complete exponent at least `0.50`.
- A correct model or point relation is not a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n11_landscape_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n11_preregistered_hit_controls.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n11_cost_analysis.md`

The prospective artifact root is not created.

## Interpretation boundary

This rejects the screened ECDLP transplant, not WalkSAT. Claims remain toy, heuristic, model-bound, and novelty-unverified. No experiment or breakthrough is claimed.

## Exactly one next executable action

1. Write the landscape-origin audit and freeze a seed-complete toy protocol that reports every failure before measuring any hit rate.
