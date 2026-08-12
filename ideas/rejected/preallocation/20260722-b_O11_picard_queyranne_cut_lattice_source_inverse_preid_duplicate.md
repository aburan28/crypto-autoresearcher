# Pre-ID duplicate draft — Picard–Queyranne cut-lattice source inverse

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O11`; no canonical ID allocated.
- Disposition: `merged_rejected_without_endpoint_network_and_cut_source_bijection`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`, `theorem-gated`.
- Breakthrough claim: none; a compact cut lattice, max flow, or relation is not an ECDLP result.

## Falsifiable hypothesis

Generic elliptic endpoints construct a compact capacitated network whose Picard–Queyranne
residual preorder represents every minimum cut as a closed set, with cuts in bijection with
signed five-source target decompositions. Lattice restrictions would replay occurrences and
complete factor-base relations and blind descent inside the sub-rho caps.

## Mechanism-new operation

Picard–Queyranne contracts the residual graph of a max flow into a preorder/DAG whose closed
sets represent all minimum `(s,t)` cuts of a supplied network. It counts only if the network
is public-endpoint-derived without source edges and each closed set has an exact signed
occurrence inverse stable under restrictions.

## Assumptions

1. Network vertices, capacities, and terminals are endpoint-derived without DLP labels.
2. Minimum cuts, not arbitrary cuts, are biconditional with all target-source tuples.
3. The residual DAG is compact and preserves signs, order, multiplicities, and exceptional strata.
4. Restrictions update closed-set queries without target-specific network rebuilds.
5. One frozen construction supports known-log rows and 100 fresh scalar-blind targets.

## Semantic fingerprint

`public_elliptic_endpoint_network | Picard_Queyranne_residual_cut_lattice | exact_restricted_min_cut_family | closed_set_to_signed_occurrence_inverse | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-369_gomory_hu_cut_tree_source_router_hypothesis.md` — cut representations consume an explicit capacitated source graph.
2. `ideas/rejected/ECDLP-IDEA-404_stone_duality_source_ultrafilter_hypothesis.md` — closed-set/duality representations need an endpoint compiler and atom inverse.
3. `ideas/rejected/ECDLP-IDEA-365_submodular_flow_source_decomposition_hypothesis.md` — flow certificates do not return rare signed tuples.
4. `ideas/rejected/preallocation/20260722-b_O08_provan_shier_minimal_cut_source_listing_preid_duplicate.md` — cut listing remains downstream of source graph construction.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable source-return frontier.

## Closest primary literature

- Picard and Queyranne, [On the Structure of All Minimum Cuts in a Network and Applications](https://doi.org/10.1007/BF01581031), represents all minimum cuts of a supplied network by residual closure structure.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not construct the endpoint network or cut/source inverse.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls generic hidden-advice interpretations.

No checked source supplies the endpoint network or signed bijection. This remains a
conditional information-flow idea, novelty-unverified and rejected before allocation.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, network/capacity formulas, terminals, max-flow policy, residual contractions, restrictions, signs, strata, and verifier.
2. Build target-independent endpoint state within `B^(9/4+o(1))`; forbid source edges, target caches, pair tables, scalar residues, and dense resultants.
3. For each known-log target, derive only allowed target data, compute flow/residual DAG, query a closed set, invert it to signed occurrences, and verify the point sum.
4. Collect `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve every factor log while charging all flows, closed sets, and failures.
5. Reuse byte-identical state for 100 fresh `R=Q+[t]P` targets, recover tuples, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge network construction, capacities, max flow, residual DAG, closed-set outputs, restrictions, inversion, density, rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`.
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; every edge, flow, residual arc,
closed set, and source inverse is charged. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

The Picard–Queyranne DAG is compact only after a capacitated network and maximum flow are
supplied. A faithful network edge encodes source compatibility; minimum-cut closed sets
represent partitions, not signed five-tuples, and arbitrary deck restrictions generally
change capacities or residual structure. Equal lattices can hide different source witnesses.

## Proof track

Construct an endpoint-only network and prove a target-uniform minimum-cut/source bijection,
restriction-stable closed-set replay, no hidden scalar labels, and complete capped descent.

## Disproof track

Show one source-derived capacity, cut/source collision, tuple missing from the min-cut family,
restriction rebuild, lost occurrence, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy network whose residual lattice has one labelled cut-source tuple.
- Negative: equal cut lattices/different witnesses, multiple min cuts, empty fibres, repeated signed points, and blind targets.
- Baselines: Gomory–Hu, Provan–Shier, P1553 R4, rho, and BSGS.
- Native max-flow/cut correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only after theorem-level endpoint construction and cut/source bijection, four sizes/all strata, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on scalar/source advice, one cut/source mismatch, rebuild, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o11_endpoint_network_theorem.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o11_cut_lattice_collision_search.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o11_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This preserves a theorem-gated representation screen, not a surviving hypothesis or a
rejection of Picard–Queyranne. Evidence remains toy, heuristic, model-bound, and
novelty-unverified; no experiment, scalar recovery, lower bound, or breakthrough is claimed.

## Exactly one next executable action

1. Specify the endpoint-to-network and cut-to-signed-source maps and prove both are exact, restriction-stable, sub-rho, and scalar-label-free, or preserve the first failed property.
