# Pre-ID duplicate draft — DPLL source unit-branching search

## Status and claim labels

- Prospect: `20260722-a-N03`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / high-risk / secondary screen.
- State: `merged_rejected_supplied_cnf_and_exponential_branch_search`.
- Evidence: exhaustive ledger/corpus and primary-literature review only; no experiment ran.
- Contract posture: no executable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none.

## Falsifiable hypothesis

A public endpoint can be compiled into a compact CNF whose satisfying assignments are exact signed factor-base decompositions; DPLL unit propagation, pure-literal reduction, and endpoint-stable branching then find occurrence-labelled models with sufficient density for full factor logs and 100 blind descents below rho/BSGS.

## Mechanism-new operation

The screened operation alternates Boolean constraint propagation with a branch on an unassigned variable and chronological backtracking. It is distinct only if the CNF and branching variables are endpoint-derived without a source catalogue, the search tree is uniformly sub-rho, and a model decodes to actual signed occurrences.

## Assumptions

1. A compact exact all-strata endpoint CNF exists without enumerated source clauses.
2. Unit propagation plus a frozen branching rule visits sub-rho nodes for relation and blind targets.
3. No target-log or post-hoc selector informs branching.
4. Models preserve source labels, signs, multiplicity, and exceptional strata.
5. Target-independent clauses and branching policy are reusable across masked targets.

## Semantic fingerprint

`public_endpoint_relation_CNF | DPLL_unit_propagation_branching | exact_model_search | signed_occurrence_decode | complete_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted predicate and replay cannot be assumed as SAT input.
2. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — serial branching state loses source histories unless expanded.
3. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — compact compiled relation circuits need a source-faithful constructor.
4. `ideas/rejected/ECDLP-IDEA-141_unambiguous_rectangle_source_factorization_hypothesis.md` — Boolean search partitions do not remove rectangle/source width.
5. `inputs/idea_generation_20260719_batch11.md` — an adjacent proof-complexity control records resolution/DPLL certificate-width barriers for an enrichment CNF, not direct ownership of source-search DPLL.

## Closest primary literature

- Davis, Logemann, and Loveland, [A Machine Program for Theorem-Proving](https://doi.org/10.1145/368273.368557), searches a supplied formula; it does not construct the ECDLP formula or bound this search tree.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies algebraic equations but not the required CNF/source decoder.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison boundary.

The native solver is established; the endpoint compiler and sub-rho model search remain unverified and are semantically occupied.

## Complete factor-base-to-target-descent path

1. Freeze curve, `B=N^(1/5)`, factor base/decks, exceptional strata, CNF vocabulary, clause compiler, branching order, restart prohibition, restrictions, masks, and verifier.
2. Build target-independent clauses/state within `B^(9/4+o(1))`, forbidding explicit tuple tables, discrete-log labels, target-fitted advice, dense resultants, and Query2P1 calls.
3. For each known-log `R`, instantiate only endpoint literals, execute DPLL while charging every node/propagation, decode actual `(A_i,epsilon_i)`, and verify the point relation.
4. Retain failures and dependent rows; collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
5. Reuse byte-identical state/policy for fresh `R=Q+[t]P`, decode and verify a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 blind targets.
6. Charge compiler work, clause/literal storage, branch nodes, propagation, backtracking, restrictions, outputs, verification, densities, rank, linear algebra, masks, randomness, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, define setup/state `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`, ambiguity/amplification `N^u`, and factor-log costs `N^ell,N^ell_m`. Charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Promotion needs `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, online work/workspace `<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory are exponent `0.50`; no propagation or branch is free.

## Likely fatal obstruction

DPLL is a solver substitution after CNF compilation. Exact source variables or clauses expose the factor-base product, while compact encodings need the already-missing source-faithful compiler. Unit propagation is incomplete and the branch tree can enumerate the source space; successful models do not certify empty restrictions or a uniform blind-target density. Nothing in DPLL changes that information flow.

## Proof track

Prove an endpoint-only compact CNF and a frozen branch/propagation theorem bounding all restricted and blind-target search trees inside both gates, with exact occurrence decoding and full descent.

## Disproof track

Find one source-derived literal incidence, an empty fibre requiring exponential branching, target-sensitive branch advice, an undecodable model, or any complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied uniquely satisfiable bounded-width toy CNFs with labelled models.
- Negative: hard empty CNFs, encoding aliases, equal clause summaries with different source models, singleton fibres, repeated occurrences, and blind targets.
- Baselines: direct enumeration, Davis–Putnam/CDCL controls, P1553 R4, rho, and BSGS.
- All are toy/model-bound; a SAT model or verified point relation is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only after zero semantic errors at four sizes, exact restrictions, charged source decoding, full rank and logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied CNF state, a false SAT/UNSAT answer, lost source, target-fitted branch rule, cap breach, or complete exponent at least `0.50`.
- Correctness, relation validity, or a validator pass is not a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n03_cnf_branch_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n03_search_tree_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n03_cost_analysis.md`

The prospective artifact root is not created.

## Interpretation boundary

This rejects only the screened ECDLP use of DPLL. Evidence remains toy, heuristic, model-bound, and novelty-unverified. No experiment, lower bound, or breakthrough is claimed.

## Exactly one next executable action

1. Write the branch-origin audit and derive a frozen lower-bound witness for the first source-incidence clause or exhaustive branch family.
