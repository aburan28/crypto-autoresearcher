# Pre-ID duplicate draft — Kahn topological source peeling

## Status and claim labels

- Prospect: `20260721-d-L02`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: graph_algorithm / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_dag_and_source_indegree_state.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a topological order or verified relation is not an ECDLP result.

## Falsifiable hypothesis

Compile signed relation completions into a public acyclic dependency graph, use Kahn zero-indegree peeling under restrictions to expose an exact source path, replay its occurrences, and complete factor logs plus blind target descent below rho and BSGS.

## Mechanism-new operation

The native operation repeatedly removes zero-indegree vertices while decrementing successor indegrees, producing an order or a cycle certificate. It counts only if the DAG, indegrees, and predecessor provenance are endpoint-derived and peeling is biconditional with restricted relation existence; peeling a supplied source dependency graph is a control.

## Assumptions

1. Endpoint data induces an acyclic dependency graph without enumerating partial source assignments.
2. Zero indegree is equivalent to a valid extendable source state, not merely local consistency.
3. Restrictions update indegrees without scanning all source arcs or deleting a unique witness.
4. A terminal peeled chain returns one signed occurrence-distinct relation tuple.
5. The same compiled DAG supports relation collection and fresh scalar-blind descent.

## Semantic fingerprint

`public_endpoint_dependency_DAG | Kahn_zero_indegree_peeling | exact_restricted_terminal_reachability | peel_chain_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed occurrence replay frontier.
2. `ideas/rejected/preallocation/20260721-a_I09_tarjan_scc_source_quotient_preid_duplicate.md` — SCC processing assumes supplied compatibility arcs and can lose source paths.
3. `ideas/rejected/preallocation/20260721-a_I11_savitch_recursive_source_reachability_preid_duplicate.md` — low-space reachability does not remove graph construction or path traffic.
4. `ideas/rejected/ECDLP-IDEA-352_implicit_dominator_tree_source_router_hypothesis.md` — implicit DAG summaries remain source-incidence representations.
5. `ideas/rejected/ECDLP-IDEA-364_reingold_universal_exploration_source_router_hypothesis.md` — traversal sequences process a represented graph rather than create endpoint adjacency.

## Closest primary literature

- Kahn, [Topological sorting of large networks](https://doi.org/10.1145/368996.369025), gives zero-indegree deletion for a supplied directed network.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations without a compact acyclic source dependency graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), gives the generic baseline.

No checked source constructs the required endpoint DAG, exact restricted peeling semantics, or occurrence lift; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional charts, DAG semantics, and the independent point verifier.
2. Build and certify endpoint-derived vertices, arcs, indegrees, and provenance without source enumeration, scalar labels, or a supplied relation catalogue.
3. For each known-log target, impose at most `5 ceil(log_2 B)+O(1)` restrictions, peel zero-indegree states, replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. Use actual `d_FB`, keep failures and dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, obtain a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge DAG construction, indegree updates, restrictions, provenance, density, rank, logs, target descent, bit time, and memory.

## Full rho/BSGS cost model

Charge DAG setup/state in `a,a_m`, restricted peeling and replay in `q,q_m`, and emitted/ambiguous chains in `o,u`. With `B=N^beta`, `beta=1/5`, `delta,delta_t,r,ell,ell_m` as density, target-density, rank-credit, and log exponents, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain exponent `0.50`.

## Likely fatal obstruction

Kahn peeling begins with the complete arc and indegree representation. Relation extensions are cyclic and source-distinct in general; making them acyclic needs an explicit assignment order whose vertices and arcs are the source search tree. Local zero indegree does not certify global completion, and exact provenance restores the state that peeling was meant to compress.

## Proof track

Exhibit a public endpoint-derived DAG with a complete path/relation biconditional, restriction-stable indegrees, and exact provenance, then prove full setup/query/rank/descent exponents below the gates.

## Disproof track

Trace every indegree and arc to its origin; falsify on source enumeration, cycle-breaking advice, local-consistency false positives, witness deletion, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied DAGs with planted labelled terminal chains.
- Negative: cyclic partial-sum graphs, locally consistent dead ends, duplicate occurrences, empty restrictions, and fresh targets.
- Baselines: explicit Kahn peeling, Tarjan SCC, Savitch reachability, Reingold traversal, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only DAG construction, four increasing sizes, zero semantic errors, exact all-strata replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both resource caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on a supplied DAG, any cycle-breaking oracle, false answer, lost occurrence, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l02_dag_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l02_kahn_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l02_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only Kahn-peeling transplant, not topological sorting. Every finite peel remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
