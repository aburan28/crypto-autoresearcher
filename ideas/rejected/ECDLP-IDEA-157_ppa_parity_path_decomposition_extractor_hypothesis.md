# ECDLP-IDEA-157 — PPA parity-path decomposition extractor

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_parity_neighbor_oracle`
- Cohort: `20260718-a`
- Evidence scale: semantic and literature audit only; no experiment ran
- Contract posture: no contract; unapproved; zero runs authorized
- Scale labels: every prospective finite test is `toy`; all complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a parity proof, correct path, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For every decomposition endpoint `R`, partial factor-base decompositions admit a public implicit graph of maximum degree two with one canonical known odd vertex and whose other odd vertices encode exact signed source tuples. A target-independent predecessor/successor oracle follows a parity path to a source in complete exponent `q<1/2`; repeated known-log queries provide full-rank relations, and the same graph supports blind descent of `Q+[t]P`.

## Mechanism-new operation

The proposed operation is **public parity pairing of partial decompositions plus implicit path following to an exact source endpoint**. Invalid or nonterminal partial states are paired by a deterministic involution; the target supplies a known unpaired start; following locally computed neighbors reaches another odd vertex whose labels are a complete source tuple.

A parity certificate, honest prover, explicit decomposition graph, generic search, or post-hoc path selector is a duplicate or control. The operation is distinct only if both neighbors of every visited state are computed without enumerating completions and the terminal state inverts exactly to factor points.

The record is rejected because PPA classifies total search problems but does not make their paths short. This proposal supplies no elliptic local-pairing theorem. Natural pairings based on whether a partial state has a compatible continuation would require deciding or producing that continuation, which is the missing source oracle; a different locally computable pairing remains outside this scoped objection and must be proved rather than assumed.

## Assumptions

1. `E/F_p` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and target-independent signed factor base `F` of size `B=N^beta`.
2. Every parity-graph state has a canonical public encoding of sub-rho bit length.
3. Predecessor and successor are computed from the current state and endpoint without scalar labels, source tables, completion enumeration, or an honest prover.
4. Odd terminal vertices correspond biconditionally to exact signed source tuples, including repetitions, infinity, and exceptional charts.
5. Path length, neighbor work, failed paths, output, rank, linear algebra, blind descent, verification, and peak memory are charged.
6. Finite path measurements remain toy and extrapolated complexity remains heuristic and model-bound.

## Semantic fingerprint

`partial_elliptic_decomposition_parity_graph | public_fixed_point_free_state_pairing | canonical_unpaired_target_start | implicit_parity_path_following | exact_source_terminal | blind_masked_descent`

The load-bearing operation is a cheap local neighbor oracle with a provably sub-rho path. A parity existence proof or explicit graph traversal does not qualify.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the open source-fiber generator and transposed target-join requirement.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, where recursive addition transcripts do not compress exact source edges.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, where explicit serial-`S3` state polynomials fail complete source recovery.
4. `inputs/ledger_inventory.json` — imported `P1478`, where one transition is compact but two-transition composition becomes dense quadratic.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, which freezes the full five-term query, setup, source, rank, and descent boundary.

## Closest primary literature

- Papadimitriou, [On the complexity of the parity argument and other inefficient proofs of existence](https://doi.org/10.1016/S0022-0000(05)80063-7), defines the parity-path complexity framework; it does not provide short paths or an elliptic neighbor oracle.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring point-decomposition equations but no parity pairing or path oracle.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/BFb0052236), supplies the generic-group comparison boundary.

No cited source supplies a source-faithful locally navigable parity graph for ECDLP. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta,m`, state encoding, pairing rule, canonical start, sign conventions, and complete addition charts.
2. Define the implicit degree-two parity graph and prove every neighbor is locally computable.
3. Exhaustively verify odd-degree and source-terminal biconditionals on every tiny fixture.
4. For each known-log endpoint `R=[r]P`, follow the parity path from its canonical start to every required exact source terminal.
5. Verify each tuple directly; retain `B+sigma` independent relation rows of rank `B`.
6. Solve factor-base logarithms and verify every point logarithm independently.
7. Apply the unchanged graph to fresh `Q+[t]P`, follow all ambiguity branches, substitute factor logs, remove `t`, and verify `[x]P=Q`.
8. Charge graph construction, neighbor evaluation, path length, retained state, source output, rank, linear algebra, blind descent, and verification.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let advice/setup exponents be `a,a_m`; graph/state-constructor exponent be `c`; complete parity-path query and workspace exponents be `q,q_m`, including neighbor work and path length; inverse useful-row and target densities be `delta,delta_t`; source-output exponent be `o`; factor-log linear-algebra exponents be `ell,ell_m`; and ambiguity exponent be `u`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Explicit graph edges, completion tests, long-path state, restarts, and terminal output are included. PPA membership alone gives no bound on `q`.

## Likely fatal obstruction

The record supplies no locally computable pairing with the required source-terminal biconditional. A natural pairing that asks which partial states can be completed reinstates the source-fiber problem, but this is not a theorem against every possible pairing. Even with constant-time neighbors, the degree-two component containing the known odd start is a path, not a cycle, and it may traverse `N^(1-o(1))` distinct states before reaching its other odd endpoint. Parity guarantees that endpoint's existence, not a sub-rho route or source label.

## Proof track

Specify the state graph and involution; prove degree at most two, the odd-terminal/source biconditional, local neighbor cost, and a deterministic or expected path-length bound; then prove exact relation rank, blind descent, and `c,q,q_m,lambda,mu<=0.45`.

## Disproof track

Exhibit a state whose neighbor requires enumerating completions, a non-source odd vertex, a source mapped to even degree, a path of exponent at least `0.50`, or a reduction of the neighbor oracle to P1434’s missing source generator.

## Positive and negative controls

- Positive PPA control: a planted implicit degree-two graph with one known odd vertex, short path, and labelled terminal.
- Positive correctness control: exhaustive tiny elliptic decomposition graphs.
- Negative path control: long-line graphs with constant-time neighbors and near-full-state paths; disjoint cycles are separate pairing-sanity controls and cannot contain the known odd start.
- Mechanism control: explicit source graph construction and ordinary DFS/BFS.
- Certificate control: parity proof without terminal extraction.
- Leakage control: forbid supplied completions, scalar labels, target-selected pairings, and discarded long paths.

## Quantitative promotion and falsification gates

A fresh successor requires zero degree/parity/source errors through exhaustive 16-bit fixtures, at least 1,000 verified relations and 100 blind descents at each of two largest toy sizes, upper 95% `c,q,q_m<=0.20`, at most `N^0.20` visited states per target, and complete `lambda,mu<=0.45`. Falsify on one nonlocal neighbor, one parity/source mismatch, lower 95% path exponent at least `0.50`, or complete `lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Prospective neighbor theorem: `ideas/artifacts/ECDLP-IDEA-157/parity_neighbor_oracle_theorem.md`
- Prospective graph schema: `ideas/artifacts/ECDLP-IDEA-157/parity_graph_schema.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-157/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-157/verify_parity_paths.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-157/cost_analysis.md`

No contract, experiment, run, or prospective artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified algorithm evidence. A parity theorem establishes totality, not efficient source generation. All finite tests would be toy; all scaling claims are heuristic and model-bound; no valid path or relation is a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-157/parity_neighbor_oracle_theorem.md` formalizing whether the proposed local neighbor rule can be evaluated without solving a source-completion instance.
