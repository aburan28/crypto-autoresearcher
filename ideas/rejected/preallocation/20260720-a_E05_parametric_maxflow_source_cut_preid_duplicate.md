# Pre-ID duplicate draft — Parametric max-flow source cut

## Status and claim labels

- Prospect: 20260720-a-E05; no canonical ECDLP idea ID was allocated
- Class / risk / lane: exact_parametric_graph_cut / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_capacity_graph_and_cut_oracle
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; an exact flow or nested-cut sequence is not an ECDLP result.

## Falsifiable hypothesis

Encode signed source compatibility in a capacitated graph whose source/sink capacities vary monotonically with a public target parameter. A fast parametric maximum-flow computation would expose nested minimum cuts; a cut transition would exactly mark restricted target nonemptiness and identify one signed source tuple for relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

Gallo–Grigoriadis–Tarjan parametric flow reuses flow state for a one-parameter class in which nonterminal arc capacities are fixed while capacities out of the source and into the sink vary monotonically in the prescribed directions, yielding nested minimum cuts. It counts only if graph/capacities obey that class and are endpoint-derived without source edges, cut membership is biconditional with source existence under every restriction, and a transition replays occurrences. Running parametric flow on an explicit relation graph or using Query2P1 as the separation/capacity oracle is a control.

## Assumptions

1. A target-independent capacitated graph encodes all signed and exceptional elliptic source strata exactly.
2. Vertices, arcs, capacity functions, breakpoints, flow residuals, restrictions, cut extraction, replay, rank, logs, descent, bit time, and memory are charged.
3. Cut nesting survives arbitrary dyadic source restrictions and does not merge incompatible occurrences.
4. A cut transition identifies point-faithful signed source labels, not only aggregate feasibility.
5. One frozen graph serves known-log and fresh scalar-blind targets without target-specific edge construction or an external exact separator.

## Semantic fingerprint

public_monotone_capacity_network | parametric_maxflow_nested_mincuts | exact_restricted_cut_transition_bit | cut_boundary_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 is the exact restricted-existence residual.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 requires a public source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-365_submodular_flow_source_decomposition_hypothesis.md — a flow oracle/ground set presupposes source incidence.
4. ideas/rejected/ECDLP-IDEA-369_gomory_hu_cut_tree_source_router_hypothesis.md — cuts summarize a supplied graph and do not retain valid source paths.
5. ideas/rejected/ECDLP-IDEA-381_megiddo_cole_parametric_source_search_hypothesis.md — parametric search accelerates an already supplied decision predicate.

## Closest primary literature

- Gallo, Grigoriadis, and Tarjan, [A fast parametric maximum flow algorithm and applications](https://doi.org/10.1137/0218003), treats a prescribed one-parameter class with fixed nonterminal capacities and monotone terminal-incident capacities on a supplied network; it does not construct that network.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations but not a source-capacity network.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), gives the baseline.

No checked primary source supplies the endpoint network, exact source inverse, or complete descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, exceptional charts, graph/capacity constructor, parameter order, breakpoint rule, restrictions, and verifier.
2. Construct target-independent network/residual state within B^(9/4+o(1)) without materializing source arcs.
3. For known-log R=[kappa]P, locate an exact cut transition in each restricted problem, replay labelled points A_i with signs epsilon_i using at most 5 ceil(log_2 B)+O(1) charged restriction queries plus negative siblings, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; retain dependencies/failures, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse unchanged state for fresh R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge graph construction, all parametric breakpoints, relabel/push work, every restriction and cut, replay, rank, logs, descent, scalar checks, bit complexity, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge vertex/arc/capacity construction and target-independent residual state; q,q_m charge target parameter compilation, all breakpoints, pushes/relabels, restricted max-flow calls, negative cuts, bisection, and replay. Let delta,delta_t be reciprocal verified transition densities, r independent-rank credit, o output, u nonunique cuts/breakpoints/rebuilds, and ell,ell_m factor-log time/state.

Let n,m be network vertices/arcs, T_MF(n,m) and M_MF(n,m) the frozen max-flow time/state bounds, Q_R the total restriction calls, and C_inv the cut-to-source inversion work. The admitted GGT class processes its nested one-parameter cuts within a constant-factor max-flow bound on one supplied network; arbitrary source restrictions generally make new networks. Thus a=log_N(T_network+n+m), a_m=log_N(M_network+M_MF), q=log_N(Q_R(T_network+T_MF+C_inv)+T_replay), and q_m=log_N(M_network+M_MF+M_inv). Q_R includes every negative sibling in the at most 5 ceil(log_2 B)+O(1) replay tree, and capacity precision/breakpoint output are included.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh parametric flow/restriction/replay <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. The complete network, capacity precision, every breakpoint, and any restriction rebuild are charged.
Separately require the complete fresh masked-target Q_R-flow/cut-inversion/replay path <=N^(0.25+o(1))=B^(5/4+o(1)). At four increasing B values, one-sided 95% upper bounds for n,m,T_MF, rebuilds, inversion, state, and complete exponents must remain below the gates.

## Likely fatal obstruction

Parametric flow accelerates a supplied monotone network. Constructing exact arcs or a capacity whose minimum cut flips precisely when a signed source exists is Query2P1 in graph form. Coarse endpoint aggregation permits a cut assembled from incompatible source fragments, while source-labelled arcs materialize the catalogue. Restrictions generally change the network rather than only the parameter. This merges with IDEAS 365/369/381 and pre-ID D07.

## Proof track

Construct the network endpoint-only, prove an all-strata cut-transition/source biconditional stable under restrictions, give a point-faithful cut inverse, and close the complete costs.

## Disproof track

Expose one source-bearing arc/capacity or external separator, or give two source systems with the same capacity network and different restricted existence/source tuples.

## Positive and negative controls

- Positive: a supplied monotone network whose planted source-labelled path produces a unique cut breakpoint.
- Negative: identical aggregate capacities with incompatible source colors, nonunique cuts, restriction rebuilds, absent and exceptional targets, and fresh blind targets.
- Baselines: IDEAS 365/369/381, pre-ID D07, ordinary max-flow on explicit incidence graphs, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only network construction, exact restriction-stable cut/source biconditional, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source arc/oracle, one aggregate-cut/source mismatch, target-specific rebuild, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e05_network_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e05_equal_cut_source_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e05_cost_analysis.md

## Interpretation boundary

This rejects the ECDLP encoding, not parametric maximum flow. Correct cuts, solver speed, or one valid relation are not a breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-a/e05_network_provenance.md; do not create it under the retired snapshot.
