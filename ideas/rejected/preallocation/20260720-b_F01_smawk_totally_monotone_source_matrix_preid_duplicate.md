# Pre-ID duplicate draft — SMAWK totally-monotone source matrix

## Status and claim labels

- Prospect: 20260720-b-F01; no canonical ECDLP idea ID was allocated
- Class / risk / lane: totally_monotone_matrix_search / conservative / conservative pre-ID screen
- State: merged_rejected_missing_public_monge_matrix_and_source_cell_oracle
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; finding row minima in a supplied matrix is not an ECDLP result.

## Falsifiable hypothesis

Arrange pair-pair versus singleton compatibility costs as a public totally monotone matrix. SMAWK row-minimum search would identify exact accepting cells using submatrix pruning, replay signed factor-base occurrences, collect full-rank relations, and support fresh blind descent below rho and BSGS.

## Mechanism-new operation

SMAWK deletes columns and recurses on alternating rows to find row extrema of a supplied totally monotone matrix in linear oracle calls. It counts only if elliptic endpoints induce the matrix and total monotonicity before sources are known, every cell is computable without Query2P1, and an extremum is biconditional with an exact source. Applying SMAWK after enumerating a compatibility matrix is a control.

## Assumptions

1. Public endpoint rows and columns define a total order and an all-strata totally monotone cost matrix.
2. Matrix dimensions, cell evaluation, column reduction, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. A row extremum distinguishes empty from singleton support exactly and preserves occurrence ancestry.
4. Arbitrary dyadic source restrictions preserve total monotonicity without rebuilding source cells.
5. One target-independent matrix family serves known-log and fresh scalar-blind targets without a post-hoc cost.

## Semantic fingerprint

public_pair_singleton_orders | SMAWK_total_monotone_row_minima | exact_restricted_accepting_extremum | matrix_cell_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 is the exact restricted-existence residual.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 requires a public source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-143_monge_transport_source_section_hypothesis.md — the missing elliptic Monge/TU identity and post-hoc selector owner.
4. ideas/rejected/ECDLP-IDEA-353_fully_sparse_boolean_product_witness_router_hypothesis.md — a matrix witness backend still needs endpoint-derived factors.
5. ideas/rejected/ECDLP-IDEA-373_adaptive_tensor_cross_source_interpolant_hypothesis.md — exact entry probes are the missing predicate.

## Closest primary literature

- Aggarwal, Klawe, Moran, Shor, and Wilber, [Geometric applications of a matrix-searching algorithm](https://doi.org/10.1145/10515.10546), assumes a supplied totally monotone matrix and value oracle; it does not derive either from elliptic endpoints.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations but no totally monotone source matrix.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic Monge identity, exact cell oracle, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, exceptional charts, row/column orders, cost rule, restriction rule, and verifier.
2. Construct the target-independent matrix oracle/state within B^(9/4+o(1)) without materializing pair/singleton source cells.
3. For known-log R=[kappa]P, use exact restricted minima to replay labelled A_i and signs epsilon_i in at most 5 ceil(log_2 B)+O(1) restriction queries plus failed siblings; first verify sum_i epsilon_i A_i=[kappa]P, then record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown logs y(A).
4. Let d_FB be the actual distinct factor-log dimension after identifications and normalization; retain failures/dependencies, collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, and only then solve.
5. Reuse unchanged state for fresh R=Q+[t]P, replay a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge matrix construction, every cell probe/comparison, reductions, restriction rebuilds, replay, rank, logs, blind descent, scalar checks, bit complexity, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let n,m be matrix dimensions, C_cell and M_cell the exact cell-oracle time/state, Q_R all restriction queries, and C_inv replay work. SMAWK uses O(n+m) cell comparisons for one supplied totally monotone matrix; restrictions may require new matrices. Set a=log_N(T_orders+T_oracle_build), a_m=log_N(M_orders+M_oracle), q=log_N(Q_R((n+m)C_cell+C_inv)+T_replay), and q_m=log_N(M_oracle+n+m+M_inv). Let delta,delta_t be reciprocal verified-hit densities, r independent-rank credit, o output, u ties/monotonicity failures/rebuilds, and ell,ell_m factor-log time/state.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), the complete fresh matrix/restriction/replay path <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. Four increasing B values need one-sided 95% upper bounds below every gate.

## Likely fatal obstruction

Generic elliptic five-sum compatibility has no supplied Monge quadrangle inequality or public total order. A 0/1 cell oracle already answers restricted source existence; a cost selecting a true cell is post-hoc source advice. Coarse endpoint costs admit false minima, while faithful cells materialize pair/singleton incidence. This merges with IDEAS 143/353/373.

## Proof track

Prove an endpoint-only total-monotonicity identity, exact all-strata cell/source biconditional stable under restrictions, point-faithful inversion, and the complete bounds.

## Disproof track

Exhibit one 2x2 elliptic submatrix violating total monotonicity or two source systems with identical public costs and different accepting cells.

## Positive and negative controls

- Positive: a supplied Monge matrix with planted unique minima and independently known source labels.
- Negative: shuffled labels, equal-cost incompatible cells, empty/singleton restrictions, exceptional targets, and fresh blind targets.
- Baselines: IDEAS 143/353/373, explicit compatibility matrices, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only matrix construction, exact restriction-stable minima/source inversion, rank d_FB over at least max(d_FB+32,1,000) rows, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing cell oracle, monotonicity violation, false extremum, restriction rebuild beyond cap, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f01_total_monotonicity_counterexample.md
- ideas/rejected/preallocation/artifacts/20260720-b/f01_matrix_source_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f01_cost_analysis.md

## Interpretation boundary

This rejects the proposed elliptic matrix, not SMAWK. Correct row minima or one relation are not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f01_total_monotonicity_counterexample.md; do not create it under this retired pre-ID screen.
