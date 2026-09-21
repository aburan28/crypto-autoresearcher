# ECDLP-IDEA-395 — Karger–Stein random-contraction source router

## Status and claim labels

- Class: `randomized_graph_contraction`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_random_contraction_requires_explicit_source_edges_and_min_cuts_do_not_encode_exact_relations`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; finding a toy minimum cut or preserving a planted path is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible weighted graph over partial elliptic states admits a Karger–Stein-style recursive random contraction that preserves at least one exact five-deck source route with sufficient probability, then exposes and canonically replays that route under restrictions for complete blind descent below the frozen gates.

## Mechanism-new operation

The screened operation is **sample weighted edges, recursively contract the partial-source graph, branch at the Karger–Stein stopping scale, recover a surviving minimum-cut certificate, and replay it as occurrence-labelled factor points**. It is distinct from generic graph routing only if both the edge sampler and the cut-to-source lift are endpoint-only and avoid source-incidence materialization.

## Assumptions

1. Exact five-deck relations induce a cut/route statistic separated from all nonsources by a target-uniform gap.
2. Endpoint data supplies exact weighted-edge sampling without listing source-labelled edges or tuples.
3. Recursive contraction preserves a useful source certificate with inverse-polynomial probability after all signed-stratum restrictions.
4. A surviving cut canonically lifts to one occurrence-labelled factor tuple rather than only a partition.
5. Graph construction, edge sampling, contraction branches, repetitions, output, rank, factor logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_weighted_partial_source_graph | Karger_Stein_recursive_random_contraction | source_preserving_cut_event | cut_certificate_replay | exact_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless source ancestry cannot be hidden as contracted graph input.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the compact exact source-resolving graph remains the missing object.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; endpoint-only target-uniform source generation remains unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; an explicit contraction edge stream already pays source incidence.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; generating source paths from pair advice restores cubic work.

## Closest primary literature

- Karger and Stein, [A New Approach to the Minimum Cut Problem](https://doi.org/10.1145/234533.234534), recursively contracts a supplied graph to preserve a minimum cut with analyzable probability.
- Gomory and Hu, [Multi-Terminal Network Flows](https://doi.org/10.1137/0109047), is a deterministic cut-routing control that also assumes explicit capacities.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relation equations but no graph, edge sampler, or cut-to-tuple theorem.

No checked source constructs the proposed source-free graph or proves that an elliptic relation is a contraction-stable cut; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, graph vertices, capacities, exact edge sampler, contraction branching/repetition schedule, replay rule, restrictions, masks, and verifier.
2. Build target-independent graph/sampler state within `B^(9/4+o(1))` without materializing source-labelled edges.
3. For known-log targets, run recursive contractions to the frozen stopping scale, recover a qualifying cut, replay one occurrence-labelled five-point tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charging failed repetitions, false cuts, ambiguity, and dependent rows; solve and verify factor logs.
5. Apply the unchanged sampler, contraction, and replay to fresh scalar-blind `Q+[t]P`, charging every restriction and target rebuild.
6. Substitute factor logs, remove `t`, retain all ambiguity branches, and verify `[x]P=Q`.
7. Charge graph/sampler construction, random bits, all contraction branches and repetitions, cut recovery, replay, output, rank, factor logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query including all success amplification at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Random contraction is efficient only after graph edges and weights are available. An edge between compatible elliptic partial states is the source-incidence object whose construction already exceeds the gate. Minimum cuts return vertex partitions, not rare five-way sum witnesses, and contractions deliberately discard internal edge identities needed for point replay. Success amplification cannot repair a missing gap theorem. This merges with IDEAs 203, 352, 369, 370, and 380 unless an endpoint-only edge sampler and cut/source biconditional are proved.

## Proof track

Construct a subgate exact edge sampler, prove a quantitative cut gap for every stratum, prove contraction survival plus canonical occurrence replay, and derive complete amplified `lambda,mu<=0.45` bounds.

## Disproof track

Show that sampling one edge evaluates source incidence, exhibit exact sources and nonsources with identical cut statistics, or measure contraction/repetition/replay costs above the gates.

## Positive and negative controls

- Positive: explicit weighted graphs with planted minimum cuts and labelled source paths must match exact min-cut values and replay the planted labels.
- Negative: same-cut/different-label graphs, relabelled edges, low cuts unrelated to sources, all signed strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 203/352/369/370/380, explicit Karger–Stein input graphs, random edge deletion, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only edge sampling, a cut/source biconditional, per-query amplified failure at most `2^-40`, `1,000` independent rows, `100` blind descents, frozen caps, and `lambda,mu<=0.45`.
- Falsify on one explicit source edge, one same-cut/different-source collision, one replay failure, amplification above cap, or either exponent at least `0.50`.
- A correct toy contraction or minimum cut is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-395/contraction_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-395/cut_source_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-395/contraction_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-395/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic random-contraction router, not Karger–Stein. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a correct cut is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-395/contraction_source_obligations.md` and classify whether each sampled edge in the smallest proposed graph can be generated without knowing either endpoint's source ancestry.
