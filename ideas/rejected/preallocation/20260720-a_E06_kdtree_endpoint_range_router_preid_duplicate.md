# Pre-ID duplicate draft — k-d-tree endpoint range router

## Status and claim labels

- Prospect: 20260720-a-E06; no canonical ECDLP idea ID was allocated
- Class / risk / lane: multidimensional_range_index / representation-changing / representation-changing pre-ID screen
- State: merged_rejected_supplied_source_points_and_nonfaithful_geometry
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; fast range search on represented points is not an ECDLP result.

## Falsifiable hypothesis

Map signed partial elliptic sums to target-independent low-dimensional public feature points and build a balanced k-d tree. Exact orthogonal ranges compiled from a target and source restrictions would isolate a small leaf set containing one accepting occurrence, allowing source replay, factor logs, and fresh blind descent below rho and BSGS.

## Mechanism-new operation

A k-d tree recursively partitions a supplied point set by coordinate hyperplanes and prunes cells outside a query range. It counts only if feature points are endpoint-derived without source enumeration, orthogonal ranges are biconditional with elliptic compatibility on all strata, and a leaf returns source labels. Indexing explicit partial tuples or using a post-hoc geometric selector is a control.

## Assumptions

1. A bounded-dimensional, target-independent feature map exactly separates accepting from rejecting signed sources.
2. Point construction, coordinates/precision, tree balancing, bounding boxes, range compilation, restrictions, leaves, replay, rank, logs, descent, bit time, and memory are charged.
3. Every accepting source survives pruning and every returned point has a point-faithful inverse.
4. Restricted source subsets are represented without rebuilding or storing explicit occurrence satellites.
5. One frozen tree serves known-log and fresh scalar-blind targets without target-trained coordinates.

## Semantic fingerprint

public_lowdimensional_endpoint_points | kd_tree_axis_partition | exact_restricted_orthogonal_range | leaf_point_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 freezes exact subset-stable existence.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 requires a public exact source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-344_locality_sensitive_exact_complement_filter_hypothesis.md — geometric locality does not give exact complement/source semantics.
4. ideas/rejected/ECDLP-IDEA-359_kakeya_nikodym_directional_source_focusing_hypothesis.md — directional geometry does not construct exact source incidences.
5. ideas/rejected/ECDLP-IDEA-393_mapper_cover_cluster_nerve_source_quotient_hypothesis.md — geometric covers/quotients lose occurrence ancestry.

## Closest primary literature

- Bentley, [Multidimensional binary search trees used for associative searching](https://doi.org/10.1145/361002.361007), indexes a supplied multidimensional record set; it does not construct source-faithful elliptic records.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) supplies endpoint equations but not low-dimensional exact range geometry.
- Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) supplies the baseline.

No checked primary source gives the feature theorem, exact range/source inverse, or complete descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, feature map, coordinate precision, tree construction, ranges, restrictions, and verifier.
2. Construct target-independent points/tree within B^(9/4+o(1)) without materializing source tuples.
3. For known-log R=[kappa]P, run exact restricted range queries, replay five labelled points A_i with signs epsilon_i using at most 5 ceil(log_2 B)+O(1) charged restriction queries plus misses, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; preserve failures/dependencies, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse unchanged state for fresh R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge feature/point construction, sort/build, all bounding-box visits, restrictions, false positives, replay, rank, logs, descent, verification, bit operations, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge feature-point creation, coordinate precision, tree nodes, bounding boxes, and any source satellites; q,q_m charge target-range compilation, visited cells/leaves, false positives, restriction handling, bisection, and replay. Let delta,delta_t be reciprocal verified relation/target densities, r independent-rank credit, o output, u geometric collisions/dimensional growth/rebuilds, and ell,ell_m factor-log time/state.

Let n be represented points, d dimension, k_out returned candidates, V the actually visited nodes, and C_verify one candidate/source verification. Native build is O(nd+n log n) coordinate/comparison work and state Theta(nd) plus labels. For fixed d, an orthogonal-range control may have V=O(n^(1-1/d)+k_out), but worst-case or growing d permits V=Theta(n). Set a=log_N(T_points+nd+n log n), a_m=log_N(nd+M_labels), q=log_N(Q_R(V+k_out C_verify)+T_replay), and q_m=log_N(M_query+M_output). Report n,d,V,k_out and coordinate bit precision for every restriction; do not substitute average query cost for the worst charged path.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh range/restriction/replay <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho and BSGS baselines are 0.50. Full point count, dimension/precision, worst-case visited leaves, and restriction rebuilds are charged rather than average-case hidden.
The complete fresh masked-target range/verification/replay path must also be <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion needs four increasing B values with one-sided 95% upper bounds for n,d,V,k_out, build/state, fresh, and complete exponents below the gates and zero feature/source collisions.

## Likely fatal obstruction

A k-d tree accelerates queries only after source-bearing points exist. Exact elliptic compatibility is not generally an orthogonal low-dimensional range predicate; coarse endpoint features collide on different occurrence ancestry, while faithful coordinates or satellites materialize partial tuples. Worst-case ranges can visit the full tree, and arbitrary source restrictions require rebuilt indices or labelled leaves. This merges with IDEAS 344/350/359/393.
Within this cohort it collides with E07: both index supplied ordered source records and leave construction, restrictions, and source replay unresolved.

## Proof track

Prove a bounded-dimensional endpoint-only embedding whose orthogonal ranges exactly encode all strata and restrictions, plus a point-faithful inverse and complete descent costs.

## Disproof track

Exhibit one source-bearing coordinate/satellite, two sources with identical features and different validity, or an admissible target range visiting source-scale leaves.

## Positive and negative controls

- Positive: a supplied low-dimensional point set with an axis-aligned planted accepting box and source labels.
- Negative: equal feature points with different ancestry, oblique/nonrectangular compatibility, worst-case slab queries, arbitrary restrictions, absent/exceptional targets, and blind targets.
- Baselines: IDEAS 344/350/359/393, explicit range search, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only bounded-dimensional points, exact all-strata ranges and inverse, worst-case charged replay, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing point/label, one feature collision or source-scale range, target-trained coordinates, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e06_point_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e06_equal_feature_source_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e06_cost_analysis.md

## Interpretation boundary

This rejects the proposed elliptic feature map, not k-d trees. Toy range-search correctness or average query speed is not a breakthrough.

## Exactly one next executable action

1. Write ideas/rejected/preallocation/artifacts/20260720-a/e06_point_provenance.md and derive the dimension, precision, cardinality, and source dependencies of every feature point for one complete chart.
