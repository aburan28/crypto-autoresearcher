# Pre-ID duplicate draft — R-tree spatial source hierarchy

## Status and claim labels

- Prospect: 20260720-c-G06; no canonical ECDLP idea ID was allocated
- Class / risk / lane: spatial_bounding_rectangle_index / representation-changing / representation-changing pre-ID screen
- State: merged_rejected_supplied_geometric_source_objects_and_overlap_worst_case
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: finite controls are toy; geometric selectivity is heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; a selective spatial query on a supplied object set is not ECDLP progress.

## Falsifiable hypothesis

Embed pair endpoints and singleton complements as public low-dimensional geometric objects. An R-tree hierarchy of bounding rectangles would prune incompatible source regions, return exact signed occurrences under restrictions, and support relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

An R-tree dynamically groups supplied spatial objects into overlapping minimum-bounding rectangles and searches only rectangles intersecting a query region. It counts only if the embedding/query geometry is endpoint-derived, rectangle intersection is sound and complete for exact elliptic relations, overlap remains below the cap, and leaves replay occurrences. Indexing an explicit source point cloud is a control.

## Assumptions

1. A public fixed-dimensional embedding maps every relevant source object and fresh target query without scalar hints.
2. Object generation, rectangle construction/splits, overlap, node visits, restrictions, exact checks, replay, rank, logs, descent, bit time, and memory are charged.
3. Query intersections have a proved all-strata biconditional or every false positive is charged.
4. Canonical source restrictions preserve the same hierarchy with bounded updates.
5. The embedding and layout are target-independent and stable for blind targets.

## Semantic fingerprint

public_endpoint_spatial_objects | Rtree_bounding_rectangle_hierarchy | exact_restricted_intersection_query | leaf_object_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted source frontier.
2. ideas/rejected/preallocation/20260720-a_E06_kdtree_endpoint_range_router_preid_duplicate.md — range pruning begins from a supplied point catalogue.
3. ideas/rejected/preallocation/20260719-b_B08_well_separated_pair_source_decomposition_preid_duplicate.md — geometric decomposition assumes explicit sites.
4. ideas/rejected/preallocation/20260720-b_F03_fortune_voronoi_source_sweepline_preid_duplicate.md — spatial cells preserve only supplied site provenance.
5. ideas/rejected/preallocation/20260719-c_C10_clarkson_shor_source_cutting_preid_duplicate.md — cuttings accelerate supplied range spaces, not source compilation.

## Closest primary literature

- Guttman, [R-trees: a dynamic index structure for spatial searching](https://doi.org/10.1145/602259.602266), assumes supplied spatial objects and provides no worst-case sublinear guarantee under arbitrary overlap.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies algebraic endpoint constraints but no selective Euclidean rectangle embedding.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the embedding, overlap theorem, exact source inverse, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, embedding, object and rectangle formats, split heuristic, query/restriction geometry, provenance, and verifier.
2. Construct the target-independent spatial objects and R-tree within B^(9/4+o(1)) without enumerating relation tuples.
3. For known-log R, query and exactly verify candidates, replay A_i,epsilon_i under bounded restrictions, verify point equality, and record an unknown-log row.
4. Collect at least max(d_FB+32,1,000) verified rows, retain all false positives/misses/dependencies, require rank d_FB, then solve logs.
5. Reuse unchanged hierarchy for Q+[t]P, recover a tuple, compute x, and verify [x]P=Q.
6. Charge embedding/object construction, all bounding boxes, overlap visits, false positives, restrictions, replay, rank, logs, blind descent, bit time, and peak state.

## Full rho/BSGS cost model

Let n be indexed objects, H tree height, V_R rectangle nodes and L_R leaves visited by a complete query, C_box intersection work, C_exact exact elliptic check, Q_R restrictions, and C_inv replay. Native R-tree query cost is data-dependent and worst-case Theta(n); use the measured full V_R,L_R rather than assuming logarithmic time. Set a=log_N(T_embed+T_build), a_m=log_N(M_objects+M_tree), q=log_N(Q_R(V_R C_box+L_R C_exact+C_inv)+T_replay), and q_m=log_N(M_tree+L_R+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% upper bounds on overlap and cost. Rho/BSGS are 0.50.

## Likely fatal obstruction

The spatial objects already contain source incidence. Elliptic equality is algebraic and generically gives no low-dimensional rectangle separation; bounding boxes overlap, while exact leaves reintroduce the catalogue. Query selectivity on tuned samples is post-hoc and has no exact absence semantics. This merges with E06/B08/F03/C10.

## Proof track

Prove an endpoint-only fixed-dimensional embedding, exact query/source biconditional, restriction-stable overlap bound, provenance, rank, and blind descent.

## Disproof track

Construct targets for which every bounding rectangle intersects, or two source systems with identical spatial objects but different valid tuples.

## Positive and negative controls

- Positive: supplied low-overlap spatial objects with planted labelled intersections.
- Negative: adversarial overlapping rectangles, shuffled labels, empty/singleton restrictions, exceptional and blind targets.
- Baselines: E06/B08/F03/C10, full scan, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only embedding, exact replay, proved overlap/query caps, rank d_FB, 100 blind descents, and lambda,mu<=0.45.
- Falsify on one supplied source object, false-negative box pruning, worst-case full scan, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g06_embedding_overlap_audit.md
- ideas/rejected/preallocation/artifacts/20260720-c/g06_spatial_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g06_cost_analysis.md

## Interpretation boundary

This rejects the proposed elliptic spatial representation, not R-trees. A selective toy query or correct leaf hit is not a breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g06_embedding_overlap_audit.md; do not create it under the retired snapshot.
