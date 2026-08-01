# Pre-ID duplicate draft — FRT tree-metric source embedding

## Status and claim labels

- Prospect: `20260721-b-J02`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: randomized_metric_embedding / representation-changing / representation pre-ID screen.
- State: merged_rejected_supplied_metric_and_distortion.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a low-stretch embedding or verified source is not an ECDLP result.

## Falsifiable hypothesis

Derive an exact endpoint metric on source-compatible partial sums, embed it into a distribution of dominating FRT tree metrics, and use tree routing to answer every restriction and return one signed source while keeping distortion, retries, and complete cost below rho and BSGS.

## Mechanism-new operation

The native operation samples a hierarchical random partition whose induced tree metric dominates a supplied finite metric with expected logarithmic stretch. It counts only if metric points, distances, and fresh-query placement are endpoint-derived and exact source existence plus occurrence identity is invariant under the embedding; embedding a supplied source catalogue is a control.

## Assumptions

1. A source-separating public endpoint metric is computable without enumerating source tuples.
2. The FRT hierarchy has at most `B^(9/4+o(1))` state and admits restriction-stable routing.
3. Exact compatibility is a zero-distance or threshold predicate invariant under the tree distortion, while duplicate occurrences remain distinguishable.
4. A reached leaf lifts to a labelled signed occurrence across every exceptional stratum.
5. Failure probability and all resampling are charged for relation collection and fresh targets.

## Semantic fingerprint

`public_endpoint_metric | FRT_random_hierarchical_partition | dominating_tree_restricted_routing | tree_leaf_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact source-return requirement.
2. `ideas/rejected/ECDLP-IDEA-344_locality_sensitive_exact_complement_filter_hypothesis.md` — approximate metric neighborhoods do not certify exact complements.
3. `ideas/rejected/preallocation/20260719-b_B08_well_separated_pair_source_decomposition_preid_duplicate.md` — metric decomposition starts from supplied points.
4. `ideas/rejected/preallocation/20260719-c_C03_thorup_zwick_endpoint_metric_oracle_preid_duplicate.md` — approximate distance oracles lose exact witness semantics.
5. `ideas/rejected/preallocation/20260721-a_I04_johnson_lindenstrauss_exact_margin_preid_duplicate.md` — random embeddings need an unavailable exact separation margin.

## Closest primary literature

- Fakcharoenphol, Rao, and Talwar, [A tight bound on approximating arbitrary metrics by tree metrics](https://doi.org/10.1016/j.jcss.2004.04.011), assumes a supplied metric and guarantees domination with expected distortion.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives algebraic endpoint equations rather than a source-separating metric.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the ECDLP source-separating metric/catalogue, places fresh targets without rebuilding, or lifts represented metric points to occurrence-distinct sources; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional charts, randomness, and the point verifier.
2. Construct the metric and FRT hierarchy from public endpoints only; record all partitions, radii, distortion certificates, and source-free provenance.
3. For each known-log target, make at most `5 ceil(log_2 B)+O(1)` exact restrictions, route them without false negatives, lift a labelled tuple, and verify point equality before retaining a row.
4. Collect at least `max(d_FB+32,1000)` verified rows, require actual rank `d_FB`, and solve every factor log while charging failures and redraws.
5. Reuse unchanged state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge metric construction, all pair distances, hierarchy sampling, distortion repair, routing, replay, density, rank, logs, blind descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

Charge `T_metric+T_FRT+T_cert` and `M_metric+M_tree` as setup/state, and `Q_R*C_route+T_lift+T_retry` per target in `a,a_m,q,q_m`. With `beta=1/5`, charge the same complete `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Include expected stretch, high-probability redraws, and exactness repair. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50`.

## Likely fatal obstruction

For represented pairs, domination `d_T>=d` preserves metric zero versus positive distance; that is not the blocker. The blocker is constructing the source-separating metric and finite catalogue without source traffic, preserving distinct occurrence ancestry when several sources map to one metric point, and proving that distorted nearest/threshold order still represents compatibility. FRT also embeds a supplied finite point set: placing each fresh target into the same target-independent tree without rebuilding or target advice is an additional unpaid operation. Tree leaves identify represented points rather than recovering hidden factor-base sources.

## Proof track

Construct a public endpoint metric with a proved exact compatibility gap, prove FRT partitions preserve every restricted zero set and labelled lift, and derive tail bounds whose retries fit the complete cost rectangle.

## Disproof track

Show metric construction enumerates sources, construct duplicate occurrences collapsed to one metric point or a threshold/nearest-order reversal under domination, and audit whether fresh targets require rebuilding; measure false decisions, distortion tails, and lift collisions.

## Positive and negative controls

- Positive: supplied finite metrics with a certified gap and labelled nearest-source backpointers.
- Negative: near-collision metrics, rare singleton witnesses, duplicated points, empty restrictions, and fresh targets.
- Baselines: exact scan, WSPD, Thorup–Zwick, Johnson–Lindenstrauss, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with an a priori exact compatibility rule, endpoint-only metric/catalogue and fresh-query construction, zero errors across all strata, four sizes, full rank, 100 fresh blind descents, total semantic query failure at most `2^-80`, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied metric points, target-specific rebuilding, approximate-only nearest/threshold semantics, a false decision, lift failure, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j02_metric_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j02_frt_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j02_cost_analysis.md`

## Interpretation boundary

This rejects the exact endpoint-source transplant, not FRT metric embedding. Any finite result remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute the contract.
