# Pre-ID duplicate draft — Cover-tree endpoint metric router

## Status and claim labels

- Prospect: `20260721-b-J09`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: exact_metric_index / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_point_catalogue_and_expansion_constant.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; fast nearest-neighbor lookup or a verified tuple is not an ECDLP result.

## Falsifiable hypothesis

Map partial source sums to a public exact metric of bounded expansion constant, build a cover tree, and route each restricted endpoint query to an exact compatible source occurrence within the fresh-target cap.

## Mechanism-new operation

The native operation maintains nested metric covers with separation and covering invariants, yielding exact nearest-neighbor search for a supplied point set when its expansion constant is small. It counts only if the metric catalogue is endpoint-derived without source enumeration and nearestness is equivalent to exact source compatibility.

## Assumptions

1. Public endpoints yield a source-separating exact metric and point set without listing sources.
2. The relevant expansion constant `c` is uniformly subpolynomial in `B`.
3. Exact zero/nearest distance distinguishes empty, singleton, duplicate, and exceptional fibers.
4. Tree nodes retain labelled signed occurrence backpointers.
5. The same index supports known-log relations and fresh masked targets.

## Semantic fingerprint

`public_endpoint_metric_catalogue | cover_tree_nested_nets | exact_restricted_nearest_query | nearest_node_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and replay frontier.
2. `ideas/rejected/ECDLP-IDEA-344_locality_sensitive_exact_complement_filter_hypothesis.md` — metric filters lack an exact generic gap.
3. `ideas/rejected/preallocation/20260720-a_E06_kdtree_endpoint_range_router_preid_duplicate.md` — spatial indexes require supplied points.
4. `ideas/rejected/preallocation/20260720-c_G06_rtree_spatial_source_hierarchy_preid_duplicate.md` — hierarchical boxes preserve a supplied catalogue.
5. `ideas/rejected/preallocation/20260719-b_B08_well_separated_pair_source_decomposition_preid_duplicate.md` — metric hierarchy and separation start after point materialization.

## Closest primary literature

- Beygelzimer, Kakade, and Langford, [Cover trees for nearest neighbor](https://doi.org/10.1145/1143844.1143857), introduces an exact index for a supplied finite metric set and claims expansion-constant-dependent bounds; the proof gaps are addressed by the next control.
- Elkin and Kurlin, [Counterexamples expose gaps in the original cover-tree complexity analysis](https://arxiv.org/abs/2208.09447), shows the historical complexity claims cannot be used as proved worst-case bounds without repair.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not provide a source point catalogue or bounded-expansion metric.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the ECDLP metric catalogue, proves bounded expansion, or supplies source backpointers; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, metric, restrictions, exceptional charts, occurrence labels, and verifier.
2. Construct the metric points and cover tree from public endpoints only; certify nesting, covering, separation, expansion, and source-free provenance.
3. For each known-log target, issue exact restricted queries, self-reduce at most `5 ceil(log_2 B)+O(1)` times, return a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified rows, retain failures/dependencies, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged tree for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge every metric point/distance and use the original `O(c^6 S log S)` construction and `O(c^12 log S)` query expressions only as optimistic historical controls, replacing them by any corrected proved bounds; also charge exactness repair, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Put full point construction and cover-tree build in `a,a_m`, and exact restricted queries plus replay in `q,q_m`; do not hide `c` or catalogue size `S`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Cover trees index supplied metric points; generating the partial-sum/source catalogue pays the missing traffic. Generic elliptic endpoint features have no proved bounded expansion or exact compatibility gap. Even an exact nearest point is only a supplied partial sum unless occurrence backpointers recreate all source ancestry. The original 2006 `c`-dependent complexity claims have known proof gaps/counterexamples, so they cannot establish the required exponents; treating them optimistically still leaves the catalogue obstruction.

## Proof track

Construct an endpoint-only metric catalogue implicitly, prove bounded expansion and an exact zero-distance source criterion, and bound all queries and lifts.

## Disproof track

Measure catalogue generation and expansion under random and adversarial endpoints; construct feature collisions and duplicate endpoints with different sources and audit every backpointer.

## Positive and negative controls

- Positive: supplied low-expansion metrics with labelled exact nearest neighbors.
- Negative: high-expansion sets, metric collisions, duplicate endpoints, empty restrictions, rare witnesses, and fresh targets.
- Baselines: exact scan, k-d/R-trees, WSPD, LSH, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only construction, proved subpolynomial `c`, four sizes, zero false decisions, complete labelled lifts, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied points, polynomial `c`, absent exact gap, label loss, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j09_metric_catalogue_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j09_cover_tree_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j09_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint metric-catalogue compiler, not cover trees. Finite results remain toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
