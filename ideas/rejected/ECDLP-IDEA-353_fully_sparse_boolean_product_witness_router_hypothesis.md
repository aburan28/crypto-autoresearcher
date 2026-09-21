# ECDLP-IDEA-353 — Fully sparse Boolean-product witness router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_sparse_matrix_backend_requires_oversized_source_incidence_and_loses_complete_provenance`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Boolean hit or one middle witness is not an ECDLP break.

## Falsifiable hypothesis

The six-list partial-sum incidence factors into public sparse Boolean matrices whose restricted fully sparse products give exact existence bits, so logarithmic bisection recovers signed factor tuples inside the campaign and fresh-target gates.

## Mechanism-new operation

The screened operation is **factor relation incidence into sparse Boolean matrices, multiply output-sparsely under source-deck restrictions, and self-reduce exact positive entries to sources**. It is distinct only if matrix construction is endpoint-derived and the factorization plus restricted decision calls needed for rank and blind descent is smaller than the original source incidence.

Minimum-interface correction: a BMM witness, all multiplicities, and complete provenance are unnecessary. A target-labelled, subset-stable exact Boolean existence bit under arbitrary dyadic deck restrictions, with `O(log B)` charged products, suffices to recover one tuple.

## Assumptions

1. Public sparse matrix factors are constructed without enumerating `B^3` or `B^4` source incidences.
2. Input and output nonzeros remain inside `B^(9/4)` setup and `B^(5/4)` query gates.
3. Restricted products preserve exact zero-versus-nonzero, so bisection recovers one complete signed tuple and repeated masked queries supply enough independent rows for rank and descent.
4. Repeated-source, singular, overlap, and infinity strata are complete.
5. Matrix construction, multiplication, witness lifting, ambiguity correction, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`six_list_partial_sum_incidence | public_sparse_boolean_factorization | fully_sparse_rectangular_product | subset_stable_exact_product_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; exact transposed value matrices retained full pair-state rank.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the exact sparse source-incidence compiler and witness router are the missing object.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; point-faithful matrix edges retain a terminal token per witness.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; exact pair/triple source batching produces cubic traffic.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; exact supplied matrix generation is a correctness control rather than a source-discovery speedup.

## Closest primary literature

- Abboud, Bringmann, Fischer, and Künnemann, [The time complexity of fully sparse matrix multiplication](https://arxiv.org/abs/2309.06317), improves multiplication as a function of explicit input/output sparsity; it does not construct source-faithful factors.
- Alon and Naor, [Derandomization, witnesses for Boolean matrix multiplication and construction of perfect hash functions](https://doi.org/10.1007/BF01940874), recovers witnesses after Boolean matrices are supplied, not all elliptic source multiplicities.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies relation equations rather than the sparse factorization.

No checked source proves the complete path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, matrix factors, target-update rule, witness lift, masks, and verifier.
2. Construct target-independent sparse matrices without source-edge materialization.
3. For known-log targets, issue restricted exact product queries, bisect to one signed tuple, and replay it directly.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Apply the identical factors to fresh `Q+[t]P` targets.
6. Bisect one witness per successful restriction, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge all nonzeros, construction, multiplication, output entries, witness tags, rank, logs, descent, verification, and memory.

## Full rho/BSGS cost model

For `B=N^(1/5)` and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,1/5+delta+q-r+o,ell,delta_t+q+o+u,1/5)`

`mu=max(a_m,q_m,1/5+o,ell_m,u)`.

Require `0<=r<=o`, setup/state at most `B^(9/4)`, fresh query at most `B^(5/4)`, and `lambda,mu<=0.45`. Rho and BSGS time exponents are `0.50`; BSGS memory is `0.50`. The cited `m^1.3459` algorithm is an upper bound, not a lower bound; applied to an explicit `B^2` input it scales as `B^2.6918`, so this particular instantiation is already non-promoting before witness lifting.

## Likely fatal obstruction

Sparse multiplication accelerates a supplied incidence product. Constructing a biconditional elliptic factorization is the missing operation, and the audited exact factors restore cubic/quartic nonzeros or the recorded full-rank boundary. One exact restricted existence bit would suffice by bisection if its matrix factors and restriction updates stayed under the gates and the resulting rows achieved rank and target coverage. No such endpoint-only factor construction or subset-stable product theorem is supplied; the known construction materializes the source incidence.

## Proof track

Construct public factors within the nonzero gates, prove subset-stable exact products plus charged bisection on every stratum, and derive rank/log/blind-descent exponents at most `0.45`.

## Disproof track

Give a family of equal Boolean products whose every public one-witness lift needs super-gate correction, or prove factor construction, multiplication, enough exact witness lifts for rank, or target descent exceed the gates.

## Positive and negative controls

- Positive: supplied sparse matrices with planted unique fully labelled witnesses.
- Negative: equal products with permuted witness tags, random full-rank incidence, repeated-middle-index ambiguity, and one-witness rank/coverage failures.
- Baselines: IDEAs 117/135/141/323, P1553-FD-R2, explicit joins, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with at most `B^(9/4)` factor nonzeros/work, at most `B^(5/4)` fresh restricted product plus bisection work, zero decision/source errors, 1,000 rows, 100 blind descents, and complete exponents at most `0.45`.
- Falsify if factor construction exceeds the setup gate, target work exceeds the query gate, one-witness lifting or rank/coverage needs source-sized provenance, or an exponent reaches `0.50`.
- A correct Boolean product or one valid tuple cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-353/sparse_factorization_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-353/provenance_loss_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-353/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-353/cost_analysis.md`

## Interpretation boundary

This rejects the source-factorization adaptation, not fully sparse matrix multiplication. All checks would be toy, heuristic, model-bound, and novelty-unverified. Matrix correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-353/sparse_factorization_obligations.md` as an endpoint-derived subset-stable exact sparse-product decision specification with every dyadic restriction and bisection call charged.
