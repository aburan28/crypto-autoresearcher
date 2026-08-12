# Pre-ID duplicate draft — Luby MIS source peeling

## Status and claim labels

- Prospect: `20260721-c-K05`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: randomized_parallel_graph / conservative / pre-ID screen.
- State: merged_rejected_supplied_conflict_graph_and_random_coverage.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an independent set or relation is not an ECDLP result.

## Falsifiable hypothesis

Construct an endpoint-derived conflict graph on partial signed sources, use Luby's randomized maximal-independent-set rounds to peel nonconflicting candidates, and preserve an exact restricted witness plus replay path below rho and BSGS.

## Mechanism-new operation

The native operation chooses local random priorities and removes selected vertices plus neighbours in parallel. It counts only if graph vertices/edges are constructed without source enumeration and maximality preserves every nonempty restricted source fibre; MIS on a supplied conflict graph is a control.

## Assumptions

1. A sparse public conflict graph represents source compatibility without tuple enumeration.
2. Each nonempty restriction retains at least one source through every randomized peel.
3. Failure probability, repetitions, and rare singleton restrictions are charged.
4. Selected vertices lift to signed occurrences on all exceptional strata.
5. Frozen random state serves relation and fresh masked targets.

## Semantic fingerprint

`public_endpoint_conflict_graph | Luby_random_priority_MIS_rounds | exact_restricted_witness_survival | selected_vertex_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restrictions and replay frontier.
2. `ideas/rejected/ECDLP-IDEA-147_moser_tardos_relation_resampling_hypothesis.md` — randomized resampling needs represented bad events and witnesses.
3. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — source hypergraph construction remains unpaid.
4. `ideas/rejected/ECDLP-IDEA-361_robust_sunflower_core_source_router_hypothesis.md` — approximate combinatorial thinning can delete rare exact sources.
5. `ideas/rejected/ECDLP-IDEA-368_pippenger_spencer_nibble_source_packing_hypothesis.md` — semirandom packing assumes sampleable source edges.

## Closest primary literature

- Luby, [A simple parallel algorithm for the maximal independent set problem](https://courses.csail.mit.edu/6.852/08/papers/Luby.pdf), proves randomized local MIS rounds for a supplied graph.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply the conflict graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the ECDLP conflict graph or proves exact witness survival/replay; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, source decks, graph semantics, random seeds, restrictions, charts, and verifier.
2. Construct conflict vertices/edges from endpoints only and preregister the witness-survival invariant.
3. For known-log targets, run exact restricted peeling with charged restarts, replay one labelled tuple, and verify point equality.
4. Retain all failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse frozen state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph construction, priority generation, rounds, deletions, retries, replay, density, rank, logs, blind descent, bit time, and memory.

## Full rho/BSGS cost model

Use `a,a_m` for graph/state, `q,q_m` for restricted rounds/replay, and `o,u` for output and restart ambiguity. With `beta=1/5`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, including failure tails. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Luby's algorithm consumes an explicit graph and returns a maximal independent set, not a witness for a rare target-labelled fibre. Conflict edges are source incidence; quotienting them loses occurrence labels. Random peeling may remove the sole useful source while still producing a valid MIS, and repetitions cannot turn maximality into exact restricted existence without a separate oracle.

## Proof track

Derive the graph publicly, prove every restricted nonempty fibre survives each round with negligible charged failure and exact replay, and bound all restarts.

## Disproof track

Trace edge construction and build singleton fibres removed by competing vertices; falsify on supplied incidence, nonzero false-negative probability, lost labels, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied graphs whose every maximal independent set contains a planted labelled source.
- Negative: unique-source conflicts, dense graphs, rare positives, duplicate endpoints, empty restrictions, and fresh targets.
- Baselines: explicit MIS, Moser–Tardos, nibble/container controls, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only graph construction, exact survival theorem, failure at most `2^-80`, four sizes, zero false decisions, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on source edges, a deleted unique witness, missing replay, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k05_conflict_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k05_mis_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k05_cost_analysis.md`

## Interpretation boundary

This rejects the exact endpoint-source transplant, not Luby MIS. Any finite peel remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
