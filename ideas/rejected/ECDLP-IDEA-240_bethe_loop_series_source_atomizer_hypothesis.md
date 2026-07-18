# ECDLP-IDEA-240 — Bethe loop-series source atomizer

## Status and claim labels

- Class: `statistical_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_factor_graph_encodes_sources_and_exact_loop_sum_restores_search`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; belief propagation, an exact loop expansion, or a marginal is not an ECDLP break.

## Falsifiable hypothesis

Each signed elliptic factor-base endpoint admits a compact source-blind factor graph whose Bethe
fixed point plus exact generalized-loop corrections yields integral one-point marginals that
canonically expose every factor point.  Exact marginal self-reduction would then support relation
collection and fresh masked-target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **endpoint factor-graph compilation, belief-propagation fixed-point
construction, exact generalized-loop-series correction, and integral marginal-to-source return**.
Approximate BP, a supplied source-valued graph, tensor-network contraction, matchgate/Pfaffian
specialization, solver substitution, or post-hoc marginal selector is a duplicate or control.

## Assumptions

1. `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, masks, variables, factors, and graph compiler are target-independent.
2. The graph has sub-rho represented size and can be compiled without one state, factor, or edge per signed source tuple.
3. A canonical BP fixed point exists, the exact loop correction is computable below rho, and corrected marginals return all exact points on generic and boundary strata.
4. Factor construction, messages, loops, source output, ambiguity, rank loss, factor logs, descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`elliptic_endpoint_factor_graph | canonical_bethe_bp_fixed_point | exact_generalized_loop_series | integral_source_point_marginals | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the open endpoint source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the failed concrete-coordinate source predicate.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the failed arithmetic pair/four-sum generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the measured source-ancestry edge boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition boundary.

## Closest primary literature

- Chertkov and Chernyak, [Loop Calculus in Statistical Physics and Information Science](https://arxiv.org/abs/cond-mat/0601487), gives an exact finite loop expansion around a belief-propagation contribution for supplied finite graphical models.
- Chertkov and Chernyak, [Loop series for discrete statistical models on graphs](https://arxiv.org/abs/cond-mat/0603189), derives loop corrections indexed by generalized loops of a supplied factor graph.

Neither source constructs a compact source-blind elliptic-addition graph, bounds its loop family
below rho, or makes exact marginals a canonical inverse to point-labelled sources.  Novelty remains
unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, factor graph, gauge, BP initialization/fixed-point rule, loop family, marginal self-reduction, and verifier.
2. Compile a compact factor graph for each known-log endpoint without enumerating point sources or source-valued transitions.
3. Compute the canonical BP messages and every required loop correction, derive exact integral marginals, self-reduce to every signed point tuple, and verify elliptic sums.
4. Collect independent relation rows, solve all factor logs, and independently verify rank and logs.
5. Apply the identical compiler, loop expansion, and marginal self-reduction to fresh `Q+[t]P`, preserve all ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging graph state, messages, loop enumeration, source output, failed endpoints, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let graph/message setup time and memory be `N^a,N^a_m`, reciprocal relation and target
densities `N^delta,N^delta_t`, one exact loop/marginal/source inverse `N^q,N^q_m`,
independent-rank gain `N^r`, source output and ambiguity `N^o,N^u`, and factor-log
completion `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Variables, domains, factors, messages, fixed-point retries, generalized loops, loop weights, exact
precision, marginals, self-reduction branches, relation rows, factor logs, target retries, and
verification are charged.  Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

A factor graph capable of distinguishing exact elliptic source points needs source-valued variable
domains and addition constraints, reproducing the missing incidence/source deck.  Removing labels
leaves aggregate counts or nonintegral marginals.  The exact loop identity is finite but may contain
exponentially many generalized loops; summing them in a generic loopy addition graph is the original
counting/contraction problem.  Multiple BP fixed points and gauge choices also defeat a canonical
point inverse without adding source labels.

## Proof track

Construct a compact source-blind graph with a canonical fixed point, prove polynomial/sub-rho exact
loop summation and integral all-source self-reduction, and establish complete
`lambda,mu<=0.45`.

## Disproof track

Prove exact factors require explicit source domains, exhibit equal corrected aggregates with different
point fibres, or show graph size, generalized-loop count, self-reduction output, ambiguity, or either
complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: small supplied factor graphs where exhaustive enumeration independently verifies BP, loop corrections, partition function, and marginals.
- Negative controls: tree graphs, graph-label permutations, approximate BP, matchgate/Pfaffian cases, IDEA-079/102/104/135, P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-blind graph of exponent at most `0.45`, canonical exact messages and
loop corrections, integral exact recall with zero false points, full factor-log rank, 100 blind descents
at each of two largest future toy sizes, and complete `lambda,mu<=0.45`.  Explicit source domains,
uncontrolled fixed-point dependence, loop/output exponent at least `0.50`, or complete exponent at
least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-240/bethe_loop_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-240/factor_graph_loop_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-240/independent_loop_series_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-240/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation hypothesis.  Correct BP
messages, an exact loop identity, an exact partition function, valid relation, or recovered toy scalar
is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-240/bethe_loop_source_theorem.md` proving a compact source-blind graph with sub-rho exact loop marginals or a factor/loop-count source-search no-go.
