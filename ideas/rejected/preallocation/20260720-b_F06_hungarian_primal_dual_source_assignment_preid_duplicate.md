# Pre-ID duplicate draft — Hungarian primal-dual source assignment

## Status and claim labels

- Prospect: 20260720-b-F06; no canonical ECDLP idea ID was allocated
- Class / risk / lane: primal_dual_assignment / conservative / conservative pre-ID screen
- State: merged_rejected_posthoc_cost_matrix_and_nonassignment_five_sum
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; an optimal assignment in a supplied matrix is not scalar recovery.

## Falsifiable hypothesis

Encode source positions and partial endpoints as a public bipartite cost matrix whose unique minimum assignment is an exact signed decomposition. Hungarian primal-dual label updates and augmenting paths would recover relations and fresh blind descents below rho and BSGS.

## Mechanism-new operation

The Hungarian method maintains dual labels, an equality graph, and augmenting paths to solve a supplied assignment problem. It counts only if the cost matrix is endpoint-derived without enumerated edges, an optimum is biconditional with exact five-source compatibility, and the augmenting path returns point-faithful occurrences. A target-tailored separating cost or solver swap is a control.

## Assumptions

1. A compact target-independent bipartite assignment formulation covers all signed and exceptional source strata.
2. Cost construction, equality graph, dual updates, augmentations, ties, restrictions, replay, rank, logs, descent, time, and memory are charged.
3. Every optimum is integral and maps to one exact five-source tuple without post-hoc selection.
4. Arbitrary restrictions preserve the formulation without rebuilding a source edge matrix.
5. The same state serves known-log and fresh scalar-blind targets without target-specific costs.

## Semantic fingerprint

public_endpoint_assignment_matrix | Hungarian_dual_labels_augmenting_paths | exact_restricted_unique_optimum | assignment_edges_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted nonemptiness and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-143_monge_transport_source_section_hypothesis.md — a public assignment cost selecting a source is the missing selector.
4. ideas/rejected/ECDLP-IDEA-382_gallai_edmonds_source_matching_decomposition_hypothesis.md — faithful matching gadgets materialize source compatibility.
5. ideas/rejected/ECDLP-IDEA-396_birkhoff_von_neumann_permutation_source_decomposition_hypothesis.md — assignment starts from a supplied support/cost matrix.

## Closest primary literature

- Kuhn, [The Hungarian method for the assignment problem](https://doi.org/10.1002/nav.3800020109), optimizes a supplied cost matrix; it does not derive an elliptic source-selecting cost.
- Tomizawa, [On some techniques useful for solution of transportation network problems](https://doi.org/10.1002/net.3230010206), supplies the at-most-n^3 additions-and-comparisons bound for an n-by-n assignment problem after the cost matrix is given.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but no compact assignment formulation.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the cost theorem, source inverse, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, matrix/constraints, cost and tie rules, restrictions, and verifier.
2. Construct target-independent matrix/state within B^(9/4+o(1)) without source-edge enumeration.
3. For R=[kappa]P, solve each exact restricted assignment and replay labelled A_i,epsilon_i using at most 5 ceil(log_2 B)+O(1) queries plus failed siblings; verify sum_i epsilon_i A_i=[kappa]P, then record sum_i epsilon_i y(A_i)=kappa.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, preserve degeneracies/failures, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge all matrix entries, constraints, dual labels, equality edges, augmentations, restrictions, replay, rank, logs, descent, scalar checks, bit complexity, and memory.

## Full rho/BSGS cost model

Let n be assignment dimension, C_cost exact entry work, Q_R restrictions, and C_inv source inversion. Tomizawa's improved dense primal-dual implementation uses at most O(n^3) additions/comparisons after the matrix is supplied, plus O(n^2 C_cost) entry work and O(n^2) represented matrix/state; compact exceptions must charge their oracle. Set a=log_N(T_matrix+n^2 C_cost), a_m=log_N(n^2+M_satellite), q=log_N(Q_R(T_Hungarian+C_inv)+T_replay), and q_m=log_N(n^2+M_dual+M_inv). With beta=1/5 and delta,delta_t,r,o,u,ell,ell_m:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), lambda,mu<=0.45, and four increasing-B one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

Five-way elliptic equality is not bipartite assignment. Faithful matrix entries or equality edges encode source compatibility; a unique target-derived optimum is a post-hoc selector. Relaxed costs can combine incompatible partial assignments, and restrictions rebuild the matrix. This merges directly with IDEAS 143/382/396.

## Proof track

Give a compact endpoint-only assignment formulation and public cost with exact all-optima/source inversion under restrictions, then close complete costs.

## Disproof track

Exhibit a fractional/incompatible assignment gadget, multiple optima with different source validity, or any cost entry derived from a known source.

## Positive and negative controls

- Positive: a supplied toy cost matrix with a unique labelled optimum.
- Negative: equal-cost incompatible assignments, post-hoc perturbed costs, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEAS 143/382/396, explicit assignment matrices, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only compact costs, exact restriction-stable optimum/source inversion, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing entry, false optimum, post-hoc tie break, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f06_cost_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f06_optimum_source_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f06_cost_analysis.md

## Interpretation boundary

This rejects the elliptic assignment encoding, not the Hungarian method. Correct optimization or one valid relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f06_cost_provenance.md; do not create it under the retired snapshot.
