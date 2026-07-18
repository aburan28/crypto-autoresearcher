# ECDLP-IDEA-233 — Conley connection-matrix source router

## Status and claim labels

- Class: `topological_representation`
- Risk band: `high_risk`
- Top lane: `high_risk`
- State: `merged_rejected_flow_and_morse_sets_require_source_transition_deck`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: retired `review_required` theorem preflight; unapproved and zero-run
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Conley index or connection matrix is not an ECDLP break.

## Falsifiable hypothesis

There is a scalar-blind discrete flow on a compact representation of the endpoint relation fiber
whose Morse decomposition has one canonical invariant set per exact source atom.  A Conley
connection matrix and continuation maps would recover the source-transition graph and signed point
tuples, enabling factor logs and masked descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **construct an endpoint-derived flow, compress it to a Morse decomposition,
and invert the Conley connection matrix to exact elliptic source orbits**.  It is distinct only if the
flow and Morse sets are generated without enumerating source states and the matrix has a canonical
point-labelled inverse.  Running homology software, selecting a favorable flow after seeing sources,
or retaining only a Conley index is a duplicate/control.

## Assumptions

1. Public curve, factor base, endpoint, sign, mask, and deterministic flow rules define the same source semantics without hidden scalar or source advice.
2. State complex, Morse decomposition, index filtration, connection matrix, and continuation data have sub-rho time and represented size.
3. Matrix entries and basis choices return every exact signed factor-base point, including cycles, multiplicities, and boundary states.
4. Flow construction, orbit exploration, homology, output, relation density, rank, factor logs, blind descent, verification, and memory are fully charged.

## Semantic fingerprint

`endpoint_relation_flow | implicit_morse_decomposition | conley_index_braid | connection_matrix_transition_inverse | exact_elliptic_source_orbits | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator and transposed join.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the failed coordinate-source predicate lane.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the failed arithmetic source generator lane.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry-transition boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge boundary.

## Closest primary literature

- Franzosa, [The connection matrix theory for Morse decompositions](https://doi.org/10.2307/2001142), constructs connection matrices covering homology index braids for supplied Morse decompositions.
- Franzosa and Mischaikow, [Algebraic transition matrices in the Conley index theory](https://doi.org/10.1090/S0002-9947-98-01666-3), relates connection matrices through upper-triangular transition data under specified order conditions.

Neither source constructs a scalar-blind elliptic flow or a canonical inverse from homological
connection data to finite-field point sources.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, flow, discretization, isolating neighborhoods, Morse order, matrix normalization, and verifier.
2. Construct and explore the endpoint flow and compact index filtration without enumerating its source-transition graph.
3. Compute the connection matrix, invert its transition data to every signed point-source tuple, and independently verify every elliptic sum.
4. Collect independent relation rows and solve and independently verify the complete factor-log system.
5. Apply the identical flow and matrix inverse to fresh `Q+[t]P`, preserve all candidate branches, and subtract `t`.
6. Accept only `[x]P=Q`, charging flow state, matrix traffic, source output, target replay, verification, and peak memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let flow/index setup time and memory be `N^a,N^a_m`, reciprocal relation and target
densities `N^delta,N^delta_t`, one connection-matrix evaluation and exact source inverse
`N^q,N^q_m`, independent-rank gain `N^r`, source output/ambiguity `N^o,N^u`, and
factor-log completion `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every state, orbit step, isolating cell, Morse set, basis element, matrix entry, continuation map,
source output, rejected endpoint, factor log, descent replay, and verifier call is charged.  Promotion
requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Conley and connection-matrix theory begins with a flow, invariant sets, an index filtration, and a
Morse decomposition.  Making these objects distinguish elliptic source tuples requires the same
point-labelled transition graph that is missing in P1434.  Without it, the Conley index and connection
matrix retain homology and connecting-orbit information only up to basis and continuation choices;
many point orbits share the same invariant.  Restoring a canonical basis or isolating neighborhood per
source materializes the source deck or a `B^m` state complex.

## Proof track

Construct a public sub-rho flow and index filtration, prove a canonical bijection from connection
matrix data to every point-labelled source orbit, and show complete `lambda,mu<=0.45`.

## Disproof track

Prove any source-faithful Morse decomposition factors through explicit source transitions, exhibit
distinct source flows with continuation-equivalent connection data, or show state, matrix, output,
ambiguity, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: small supplied Morse decompositions with independently known connection matrices and connecting orbits.
- Negative controls: continuation-equivalent flows with permuted source labels, homology-only summaries, IDEA-073/174/218/220, P1409/P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a scalar-blind state complex and matrix of exponent at most `0.45`, exact recall of
every source orbit, zero false sources, no explicit transition deck, full factor-log rank, 100 blind
descents at each large future toy size, and complete `lambda,mu<=0.45`.  Basis-dependent output,
continuation collisions, state materialization, or either complete exponent at least `0.50` falsifies
this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-233/conley_source_router_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-233/connection_matrix_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-233/independent_conley_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-233/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative high-risk hypothesis.  A valid isolating
neighborhood, Conley index, connection matrix, continuation theorem, source recovery on a toy flow,
or toy scalar is not a generic ECDLP improvement, crypto-scale evidence, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-233/conley_source_router_theorem.md` proving an endpoint-derived sub-rho source-faithful Morse decomposition and canonical matrix inverse or a continuation/source-state obstruction.
