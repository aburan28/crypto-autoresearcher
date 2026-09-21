# Pre-ID duplicate draft — Tutte randomized source matching

## Status and claim labels

- Prospect: 20260720-d-H06; no canonical ECDLP idea ID was allocated
- Class / risk / lane: skew_determinant_matching_decision / high_risk / high-risk pre-ID screen
- State: merged_rejected_supplied_compatibility_graph_and_self_reduction_cost
- Evidence: complete live ledger/corpus and checked primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; correctness, a relation, or native algorithm performance is not an ECDLP result.

## Falsifiable hypothesis

Encode compatibility in a skew Tutte matrix; randomized nonzero determinant tests plus self-reduction would decide restrictions, recover labelled matchings/relations, complete logs, and descend blind targets below rho/BSGS.

## Mechanism-new operation

The Tutte determinant decides perfect matching for a supplied graph; Lovasz-style independent random evaluation is one-sided, while Mucha-Sankowski/Harvey algebraic algorithms or a charged deletion reduction recover a matching. It counts only if edges are endpoint-derived and matching is biconditional with a five-way relation; explicit determinants are controls.

## Assumptions

1. A compact graph has a perfect matching exactly when a signed relation exists.
2. Edges are endpoint-derived; evaluation points come from recorded independent uniform seeds in a predeclared finite field and are never endpoint-derived.
3. Restrictions, adaptive error, and self-reduction are fully charged.
4. Recovered matchings lift to exact signed occurrences.
5. Matrix build, trials, replay, rank, logs, descent, bits, and memory are charged.

## Semantic fingerprint

public_endpoint_compatibility_graph | Tutte_random_skew_determinant | exact_restricted_matching | self_reduced_matching_to_signed_occurrences | logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — live uncommitted P1553 R4 exact restricted common-factor frontier.
2. ideas/ECDLP-IDEA-050_spinor_matchgate_addition_transform_hypothesis.md — the active Pfaffian/matchgate owner already requires a public source-faithful signature and exact self-reduction.
3. ideas/rejected/preallocation/20260719-b_B04_edmonds_blossom_source_matching_preid_duplicate.md — matching needs a graph.
4. ideas/rejected/ECDLP-IDEA-345_linear_matroid_parity_source_packing_hypothesis.md — algebraic packing assumes a ground set/oracle.
5. ideas/rejected/ECDLP-IDEA-382_gallai_edmonds_source_matching_decomposition_hypothesis.md — decomposition does not create edges.

## Closest primary literature

- Tutte, [The Factorization of Linear Graphs](https://doi.org/10.1112/jlms/s1-22.2.107), gives the represented-graph factorization foundation, not the later randomized numerical test or recovery algorithm.
- Lovasz, [On determinants, matchings, and random algorithms](https://www.researchgate.net/publication/221150072_On_determinants_matchings_and_random_algorithms), gives the randomized determinant test on a supplied graph.
- Mucha and Sankowski, [Maximum Matchings via Gaussian Elimination](https://doi.org/10.1109/FOCS.2004.40), and Harvey, [Algebraic Algorithms for Matching and Matroid Problems](https://doi.org/10.1137/070684008), give randomized algebraic recovery routes on supplied represented graphs.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not this source compiler.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required elliptic endpoint-to-source operation; ECDLP novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, exceptional charts, native state, restriction grammar, and independent point verifier.
2. Construct target-independent state from public endpoints within B^(9/4+o(1)) without enumerating source tuples or invoking Query2P1.
3. For R=[kappa]P, use exact restricted existence and charged replay to return labelled A_i and signs epsilon_i in at most 5 ceil(log_2 B)+O(1) positive/negative queries; verify sum_i epsilon_i A_i=[kappa]P before recording sum_i epsilon_i y(A_i)=kappa in unknown logs.
4. Let d_FB be the actual distinct factor-log dimension; retain failures/dependencies, collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, replay a tuple, compute x=sum_i epsilon_i log_P(A_i)-t mod N, and independently verify [x]P=Q.
6. Charge construction, restrictions, failed queries, replay, relation density, rank, log solve, descent, scalar verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For v vertices/e edges over a declared field F_s, one determinant trial costs O(v^omega) and O(v^2) state. Let A be the total adaptive decisions and choose t fresh independent seeds so A(v/s)^t<=2^-80. Charge either a fully instantiated O(v^omega) Mucha-Sankowski/Harvey recovery or the conservative O(e v^omega) deletion reduction as T_rec: a=log_N(T_graph+t v^omega), a_m=log_N(M_graph+v^2), q=log_N(Q_R t(v^omega+T_rec)+C_lift+T_replay), q_m=log_N(v^2+e+M_lift). Field operations, seed generation/storage, inverse updates, failed trials, and exact point replay are included.

For B=N^beta, beta=1/5, let delta,delta_t be reciprocal verified-hit densities, r independent-rank credit, o output, u ambiguity/rebuild/error overhead, and ell,ell_m factor-log time/state:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/advice/state <=B^(9/4+o(1)), complete fresh work/workspace <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. Four increasing B values require one-sided 95% upper bounds below empirical gates.

## Likely fatal obstruction

The graph is the missing source-incidence object; coarse graphs admit false matchings and faithful graphs materialize the predicate. Nonvanishing alone is relation-only until recovery is charged.

## Proof track

Prove endpoint graph/matching biconditional, restriction stability, adaptive error, subcap recovery, and full costs.

## Disproof track

Find a false/missing matching, source-bearing edge, or recovery cost above the cap.

## Positive and negative controls

- Positive: supplied graphs with unique labelled perfect matchings.
- Negative: near-perfect/no-perfect graphs, shuffled edges, false-zero trials, blind targets.
- Baselines: blossom/Hungarian/matroid parity, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

Promote only with an endpoint-only exact restricted operation, exact occurrence lift, a frozen field F_s and independent recorded seeds satisfying A(v/s)^t<=2^-80, a fully instantiated recovery route, rank d_FB over at least max(d_FB+32,1,000) verified rows, 100 fresh blind descents, both caps, and lambda,mu<=0.45. Falsify on source-bearing edge, endpoint-derived/correlated randomness, false/missing matching, recovery overflow, error above 2^-80, cap failure, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-d/h06_graph_matching_biconditional_audit.md
- ideas/rejected/preallocation/artifacts/20260720-d/h06_determinant_controls.json
- ideas/rejected/preallocation/artifacts/20260720-d/h06_cost_analysis.md

## Interpretation boundary

This rejects the compatibility graph/recovery path, not the Tutte criterion. A toy success remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-d/h06_graph_matching_biconditional_audit.md; do not create it under this retired pre-ID screen.
