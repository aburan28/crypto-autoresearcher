# Pre-ID duplicate draft — Koetter–Médard network-transfer source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T12`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_network_topology_and_transfer_polynomials`.
- Class/risk/lane: representation / high-risk / high-risk top pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; feasible multicast, a nonzero determinant, decoded packets, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

Partial signed elliptic sums form packets in a compact public acyclic network whose transfer
polynomials route independent source symbols to an endpoint sink. A Koetter–Médard algebraic
network code would choose coefficients that preserve exact occurrence provenance and permit sink
decoding of relation tuples, full factor logs, and blind descents below rho.

## Mechanism-new operation

Algebraic network coding assigns local linear kernels on a supplied directed network and tests
connection feasibility through transfer matrices/determinants. It counts only if endpoint data
constructs the topology, source packets, and sink demands without enumerating partial relation
paths, and if decoded packets invert exactly to signed occurrences. Optimizing coefficients or
checking transfer rank on an explicit source network is a backend/control.

## Assumptions

1. A bounded-degree target-independent network compactly represents all valid partial sources.
2. Endpoint sink demands and transfer polynomials are public without hidden path/source advice.
3. Linear mixing preserves enough provenance for a canonical signed occurrence inverse.
4. Network construction, coefficient search, packet traffic, rank checks, decoding, and output meet both caps.
5. The same network is scalar-blind, produces full-rank relation rows, and supports 100 fresh masks.

## Semantic fingerprint

`public_partial_sum_network | algebraic_local_coding_kernels | endpoint_sink_transfer_matrix | decoded_packets_to_signed_occurrence_paths | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-223_gammoid_linkage_source_router_hypothesis.md` — linkage/path routing requires a represented source graph.
2. `ideas/rejected/ECDLP-IDEA-206_planar_network_positroid_source_router_hypothesis.md` — network coordinates consume supplied topology and source paths.
3. `ideas/rejected/ECDLP-IDEA-231_operator_scaling_shrunk_subspace_source_atomizer_hypothesis.md` — transfer-rank certificates do not recover source atoms.
4. `ideas/rejected/preallocation/20260721-d_L02_kahn_topological_source_peeling_preid_duplicate.md` — an acyclic source network still costs its vertices/arcs/provenance.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed occurrence replay remain required.

## Closest primary literature

- Koetter and Médard, [An Algebraic Approach to Network Coding](https://doi.org/10.1109/TNET.2003.818197), derives transfer-polynomial feasibility for a supplied communication network.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no compact source network or packet inverse.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the elliptic network, removes path/source materialization, supplies an
exact occurrence inverse, or completes descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, source/sink semantics, topology, local kernels, coefficient rule, transfer decoder, restrictions, masks, strata, and verifier.
- Build target-independent network/state within `B^(9/4+o(1))`, forbidding enumerated partial-sum paths, relation catalogues, and factor logs.
- For known-log endpoints, charge every vertex/edge/packet, coefficient search, determinant/rank test, transfer decode, path/occurrence lift, replay, and row verification.
- Retain failures/dependencies; collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve every factor log.
- Reuse byte-identical network/state on 100 fresh masked targets, decode/lift tuples, subtract masks, and verify scalars.
- Charge topology/state, packet traffic, ambiguity, output, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, charge setup/state `N^a,N^a_m`, reciprocal row/target densities
`N^delta,N^delta_t`, network/transfer/decode/replay `N^q,N^q_m`, rank credit
`N^r`, path/output `N^o`, ambiguity/failure `N^u`, and factor logs
`N^ell,N^ell_m`. Use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Network coding transports already supplied source packets over already supplied edges. For
elliptic relations, vertices and edges encode partial-source compatibility and therefore
materialize the missing search graph. Linear mixtures and transfer rank erase individual path and
occurrence identity; restoring backpointers recreates source-scale topology/traffic.

## Proof track

Prove a compact endpoint-derived network with exact restricted path/relation semantics, canonical
packet-to-occurrence inverse, full rank/logs, blind descent, and complete sub-rho costs.

## Disproof track

Trace topology/packets to source enumeration, exhibit equal transfer matrices with different
source paths, show mixing destroys occurrence identity, or charge state/traffic to exponent `0.50`.

## Positive and negative controls

- Positive: supplied multicast networks with known sources, sinks, and feasible linear codes.
- Negative: equal-transfer different-path networks, insufficient min-cuts, cyclic/large path graphs, mixed provenance, empty restrictions, exceptional strata, and fresh targets.
- Baselines: IDEA-223/206/231, Kahn peeling, P1553 R4, rho, and BSGS.
- Feasible transfer matrices or decoded packets remain toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public topology/transfer/inverse theorems, zero errors at four sizes/all strata, miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on source-enumerated topology, one transfer/path ambiguity, state/traffic cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t12_network_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t12_transfer_path_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t12_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not algebraic network coding. A feasible transfer,
decoded packet, or valid relation remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Draw the smallest proposed elliptic source network and label whether each vertex, edge, packet, and transfer coefficient is derivable before any partial source is enumerated.
