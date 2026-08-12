# Pre-ID duplicate draft — Fiduccia–Mattheyses source-partition refinement

## Status and claim labels

- Prospect: `20260721-c-K11`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: hypergraph_partition_heuristic / conservative / pre-ID screen.
- State: merged_rejected_supplied_source_hypergraph_and_heuristic_cut.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a low-cut partition or relation is not an ECDLP result.

## Falsifiable hypothesis

Construct an endpoint-derived source hypergraph, apply Fiduccia–Mattheyses gain buckets and single-vertex moves to isolate target-compatible source blocks, and use recursive exact partitions to replay occurrences below rho and BSGS.

## Mechanism-new operation

The native operation iteratively moves vertices between blocks using gain buckets for a supplied hypergraph cut objective. It counts only if vertices, nets, gains, and exact restriction labels are endpoint-derived and heuristic refinement preserves all witnesses; refining a supplied source hypergraph is a control.

## Assumptions

1. A sparse public hypergraph represents exact source compatibility without enumerating tuples.
2. A cut objective has a proved exact-witness margin, not merely empirical locality.
3. Gain updates and recursive restrictions fit the resource caps.
4. Refined blocks retain signed occurrence backpointers on all strata.
5. The partition is target-independent and reusable for fresh targets.

## Semantic fingerprint

`public_endpoint_source_hypergraph | Fiduccia_Mattheyses_gain_bucket_moves | exact_restricted_block_refinement | block_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted source-return frontier.
2. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — the hypergraph and codegrees are missing inputs.
3. `ideas/rejected/ECDLP-IDEA-348_frieze_kannan_cut_decomposition_source_router_hypothesis.md` — cut summaries lose rare source edges.
4. `ideas/rejected/ECDLP-IDEA-370_spectral_sparsification_source_router_hypothesis.md` — approximate cut/energy preservation can delete singleton relations.
5. `ideas/rejected/preallocation/20260719-d_D12_multilevel_coarsened_source_partition_preid_duplicate.md` — partition refinement consumes the supplied source graph.

## Closest primary literature

- Fiduccia and Mattheyses, [A linear-time heuristic for improving network partitions](https://doi.org/10.1145/800263.809204), gives gain-bucket refinement for a supplied network/hypergraph.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply the source hypergraph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the endpoint hypergraph or proves exact witness-preserving cuts; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, hypergraph/net semantics, gain policy, restrictions, charts, and verifier.
2. Construct vertices/nets and certify their endpoint-only origin.
3. For known-log targets, refine blocks, answer exact restrictions, replay a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged partition state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph construction, all nets, gain updates, passes, restarts, restrictions, replay, density, rank, logs, bit time, and memory.

## Full rho/BSGS cost model

Charge hypergraph/partition setup in `a,a_m`, restricted moves/replay in `q,q_m`, and restarts/output in `o,u`. With `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, and charge heuristic failures. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, exact semantic failure `<=2^-80`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Fiduccia–Mattheyses is a heuristic on an explicit hypergraph. Its nets are precisely the source incidence being sought, and cut gain measures aggregate locality rather than exact target-labelled existence. A sequence of improving moves can strand or coarsen a unique witness while still improving the cut, so exact self-reduction needs a separate oracle.

## Proof track

Construct the hypergraph publicly, prove an exact witness-margin invariant for every move/restriction, and bound all passes and replay costs.

## Disproof track

Audit net construction, create unique witnesses crossing low-gain cuts, vary seeds/ties, and falsify on supplied incidence, heuristic-only convergence, lost labels, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied labelled hypergraphs with a cut objective exactly aligned to planted sources.
- Negative: unique cross-cut witnesses, local minima, dense nets, duplicate endpoints, empty restrictions, and fresh targets.
- Baselines: multilevel coarsening, Frieze–Kannan, spectral sparsification, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only nets, exact invariant, four sizes, zero false decisions, exact lifts, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on source nets, any lost witness, heuristic-only evidence, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k11_net_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k11_partition_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k11_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-source partition transplant, not the Fiduccia–Mattheyses heuristic. Any finite cut remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
