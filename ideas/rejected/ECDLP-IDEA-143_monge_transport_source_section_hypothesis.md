# ECDLP-IDEA-143 — Monge-transport source section

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_target_separating_selector`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: prospective measurements are `toy`; costs are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an integral optimum, unique assignment, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Embed five-source decompositions in a public assignment/transport polytope and derive from the endpoint a Monge or totally unimodular cost whose unique integral optimum is an exact signed source tuple. Strong polynomial transport/assignment optimization then gives relations and blind descent without enumerating the relation fiber.

## Mechanism-new operation

The proposed operation is **endpoint-derived Monge/TU source selection**. Source positions and partial sums become transport marginals; an elliptic four-point inequality makes the cost Monge, total unimodularity ensures integrality, and a deterministic tie rule returns a canonical tuple.

Semantic audit rejects the current specification. The elliptic five-sum constraint is not a network-flow/TU constraint for an arbitrary factor base, and no public Monge inequality encodes endpoint compatibility. Constructing a target-dependent cost that uniquely favors an actual tuple is precisely the missing post-hoc selector/source section represented by IDEA-068, IDEA-104, and IDEA-125. Generic assignment optimization after candidate edges are listed is a backend.

## Assumptions

1. Public `E,<P>,N,Q,F`, `B=N^beta`, signs, repetitions, infinity, and projective addition are fixed.
2. A target-independent polytope has a compact constraint matrix, integral vertices, and a source/vertex biconditional.
3. A public endpoint-derived cost is Monge or discrete convex and uniquely selects an accepted source without inspecting candidates.
4. Polytope/cost construction does not use scalar coordinates, relation rows, or an enumerated edge set.
5. Construction, optimization, degeneracy, all optima, output, rank, factor logs, blind descent, and memory are charged.

## Semantic fingerprint

`five_source_transport_polytope | elliptic_Monge_cost | total_unimodular_integrality | public_unique_optimum | exact_vertex_to_source_inverse | blind_descent`

An explicit elliptic Monge/TU identity would be new. A chosen separating cost or supplied candidate graph is the rejected selector/backend.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the public source-fiber generator the transport graph cannot assume.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1431-CANONICAL-ROOT-PRODUCT-NO-PROMOTION`, where canonical output traversal still pays to construct every source leaf.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the complete five-source exponent boundary.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, where exact partial-source states densify beyond the gate.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-043`, where a natural Abel–Jacobi completion label performs like matched random/relabelled controls.

## Closest primary literature

- Burkard, Klinz, and Rudolf, [Perspectives of Monge properties in optimization](https://doi.org/10.1016/0166-218X(95)00103-X), characterize algorithmically useful Monge structure but do not derive it from elliptic endpoints.
- Murota, [Discrete Convex Analysis](https://doi.org/10.1137/1.9780898718508), develops M-convex/exchange optimization; fixed-target elliptic relation support need not satisfy its exchange axioms.
- Tardos, [A strongly polynomial algorithm to solve combinatorial linear programs](https://doi.org/10.1287/opre.34.2.250), makes compact integral optimization efficient once the matrix/cost are supplied, not before source incidence construction.

No checked source supplies the elliptic polytope or cost. Novelty remains unverified, and the stated selector is semantically occupied.

## Complete factor-base-to-target-descent path

1. Freeze public inputs, polytope, cost formula, tie rules, exceptional cases, and independent source verifier.
2. Construct the compact transport instance for each known-log target without enumerating relation edges.
3. Optimize, enumerate all tied optima if necessary, decode vertices to exact signed factor points, and verify elliptic addition.
4. Collect rank `B`, solve and verify factor logs.
5. Apply the same cost construction to fresh masked targets, decode candidates, subtract masks, and accept only `[x]P=Q`.
6. Charge construction, optimization, degeneracy/list output, rank, linear algebra, descent, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let polytope/cost setup be `N^a,N^a_m`, constraint/edge payload `N^c`, optimization/source-decode time and working memory `N^q,N^q_m`, inverse densities `N^delta,N^delta_t`, output `o`, ambiguity `u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
Candidate edges and tie enumeration are included. Toy solver speed is model-bound.

## Likely fatal obstruction

An arbitrary factor-base five-sum does not have the exchange/uncrossing property behind Monge and TU algorithms. Multiple decompositions prevent a public unique optimum unless the cost already distinguishes their source labels. Building the feasible edge/polytope description can be exactly the source incidence enumeration, while optimizing an aggregate relaxation can return fractional or non-source objects.

## Proof track

Exhibit an explicit compact TU matrix and endpoint-derived Monge cost, prove a source/vertex biconditional and complete `lambda,mu<=0.45` for all exceptional strata.

## Disproof track

Give a frozen factor base/target violating Monge exchange or integrality, show the cost is chosen after source inspection, or show the compact matrix contains all candidate edges. The current proposal is rejected by the absent identity and selector reduction.

## Positive and negative controls

- **Positive control:** classical Monge assignment/transport instances with supplied integral graphs and unique optima.
- **Positive control:** tiny elliptic fixtures where an oracle cost is planted, explicitly marked as a circular control.
- **Negative control:** random factor bases/targets, shuffled costs, degenerate multiple-source fibers, and aggregate LP relaxations.
- **Negative control:** enumerated candidate graphs and post-hoc separating weights.
- **End-to-end control:** rho/BSGS and blind targets with graph construction charged.

## Quantitative promotion and falsification gates

This record is rejected as a selector/backend. A new ID requires a target-blind elliptic Monge/TU theorem and complete `lambda,mu<=0.45`. One nonintegral optimum, missed source, post-hoc cost, enumerated incidence graph, or complete exponent at least `0.5` falsifies the claimed operation.

## Artifact plan

- Selector reduction: `ideas/artifacts/ECDLP-IDEA-143/monge_selector_reduction.md`
- Prospective elliptic Monge theorem: `ideas/artifacts/ECDLP-IDEA-143/elliptic_monge_identity.md`
- Frozen controls: `ideas/artifacts/ECDLP-IDEA-143/fixtures.json`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-143/cost_analysis.md`

No artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified evidence. Tests would be toy and costs heuristic/model-bound. Integral optimization correctness is not source generation or an ECDLP breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-143/monge_selector_reduction.md` exhibiting the first exchange/TU failure on exhaustive factor bases and identifying every cost term that depends on a pre-known source.
