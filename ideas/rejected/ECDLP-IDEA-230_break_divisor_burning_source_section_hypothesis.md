# ECDLP-IDEA-230 — Break-divisor burning source section

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_graph_jacobian_requires_source_incidence_deck`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: retired `review_required` theorem preflight; unapproved and zero-run
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a unique reduced divisor, break divisor, or burning certificate is not an ECDLP break.

## Falsifiable hypothesis

There is a target-independent graph model of the signed elliptic factor-base addition
correspondence whose critical group receives each public endpoint class and whose unique
break-divisor or rooted reduced-divisor representative canonically identifies every exact
factor-base source tuple.  Dhar-style burning would then provide a source section usable for
full relation collection and fresh masked-target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **endpoint-to-graph-Jacobian encoding followed by canonical
break-divisor reduction and burning-based exact source return**.  Canonical reduction would
matter only if the graph, divisor class, and inverse from break-divisor support to signed
elliptic points are constructed from the endpoint without enumerating source incidences.  A
spanning-tree enumeration, matrix-tree determinant, supplied relation graph, alternate graph
model, or post-hoc source label is a duplicate or control.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, masks, and graph construction are target-independent.
2. The graph and endpoint divisor class have sub-rho construction and represented size and do not contain one vertex, edge, rotor, or chip per source tuple.
3. The canonical representative returns all exact signed elliptic sources on every generic and boundary stratum, not merely a homologous graph divisor.
4. Graph construction, reduction, source output, relation density, rank loss, factor logs, masked descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`elliptic_addition_endpoint | implicit_critical_graph | graph_jacobian_class | canonical_break_divisor_or_q_reduced_section | burning_exact_point_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the open public algebraic source-fiber generator and transposed-target join question.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the closed concrete-coordinate source-resolving predicate hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the closed arithmetic pair/four-sum generator hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the measured lossless ancestry-edge boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition boundary.

## Closest primary literature

- An, Baker, Kuperberg, and Shokrieh, [Canonical representatives for divisor classes on tropical curves and the Matrix-Tree Theorem](https://arxiv.org/abs/1304.4259), proves uniqueness of break divisors for supplied graph or tropical-curve divisor classes.
- Luo, [Rank-determining sets of metric graphs](https://arxiv.org/abs/0906.2807), gives constructive reduced-divisor methods on a supplied metric graph.

Neither source constructs a graph-Jacobian encoding of generic elliptic addition fibers or an
endpoint-only inverse to exact point sources.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, graph compiler, sink, reduction order, tie rules, and source verifier.
2. Compile each known-log endpoint into a compact graph and divisor class without materializing its source incidences.
3. Compute the unique break or rooted reduced divisor and map its support to every exact signed factor-base tuple; verify each elliptic sum.
4. Collect independent rows, solve and independently verify all factor logs, charging duplicates and rank loss.
5. For fresh masks `t`, apply the identical compiler and burning section to `Q+[t]P`, recover every candidate scalar, and subtract `t`.
6. Accept only `x` satisfying `[x]P=Q`, charging construction, output, ambiguity, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, factor-base and target reciprocal success
densities `N^delta,N^delta_t`, one burning reduction plus exact source inverse
`N^q,N^q_m`, independent-rank gain `N^r`, source output and target ambiguity
`N^o,N^u`, and factor-log completion `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every graph vertex and edge, spanning-tree state, chip move, source output, failed
endpoint, relation row, factor log, target replay, and verifier call is charged.
Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Break-divisor uniqueness is relative to a supplied graph divisor class.  Constructing the graph
whose spanning trees or chip configurations distinguish the elliptic source tuples appears to
require exactly the point-labelled incidence edges that P1434 and the P1409/P1434 boundaries
leave missing.  If labels are removed, chip-firing retains a class and selects one canonical graph
representative, not the original elliptic preimages.  Restoring an inverse from chips or tree edges
to points reinstates the source deck, while a graph with one cell per tuple has `B^m` state.

## Proof track

Exhibit an endpoint-derived graph of sub-rho size, prove a bijection between its canonical break
divisor and all signed elliptic sources on every stratum, and establish complete
`lambda,mu<=0.45` without a source-labelled edge table.

## Disproof track

Show that any correct graph compiler factors through the explicit source-incidence graph, or
construct two endpoints/source fibers with the same public graph divisor class but different exact
sources; alternatively prove graph size, burning work, output, or ambiguity exponent at least
`0.50`.

## Positive and negative controls

- Positive control: supplied small graphs with independently enumerated critical groups, break divisors, spanning trees, and burning outputs.
- Negative controls: source-label permutations preserving the graph class, unlabeled quotient graphs, IDEA-144 reduced-divisor chip lifting, IDEA-203 matrix-tree extraction, P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires zero source-label leakage, exact recall of every signed source, no false source,
sub-rho graph size and reduction, full factor-log rank, 100 blind descents at each of two largest
future toy sizes, and complete `lambda,mu<=0.45`.  Any explicit source-edge deck, missed boundary
branch, output/state exponent at least `0.50`, or complete exponent at least `0.50` falsifies this
version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-230/endpoint_graph_section_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-230/burning_source_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-230/independent_break_divisor_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-230/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation hypothesis.  A correct critical
group, unique break divisor, spanning-tree bijection, burning replay, valid relation, or recovered toy
scalar is not a complete ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-230/endpoint_graph_section_theorem.md` proving an endpoint-only sub-rho graph/source bijection or a source-incidence factorization no-go before constructing any fixture.
