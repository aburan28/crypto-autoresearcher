# Pre-ID duplicate draft — Bentley–Ottmann source-intersection sweep

## Status and claim labels

- Prospect: `20260721-c-K04`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: computational_geometry / representation-changing / pre-ID screen.
- State: merged_rejected_supplied_geometric_segments_and_order.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an intersection event or verified relation is not an ECDLP result.

## Falsifiable hypothesis

Map partial elliptic source families to planar segments so exact endpoint-compatible pairs are precisely their intersections, then apply the Bentley–Ottmann event sweep to answer restrictions and replay signed sources below rho and BSGS.

## Mechanism-new operation

The native operation maintains a sweep-line order and reports intersections of supplied planar objects output-sensitively. It counts only if segment construction, ordering, and event-to-source lift are endpoint-derived and exact over `F_p`; sweeping a supplied source segment catalogue is a control.

## Assumptions

1. A scalar-blind bounded-complexity planar embedding maps exact compatibility to segment intersection.
2. Segment count and all event coordinates fit the resource rectangle.
3. Degenerate, vertical, repeated, tangent, infinity, and empty cases are exact and occurrence-distinct.
4. Restrictions update the event queue without reconstructing the full catalogue.
5. One embedding supports relation and fresh target queries.

## Semantic fingerprint

`public_endpoint_planar_segments | Bentley_Ottmann_sweep_event_queue | exact_restricted_intersection | event_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact target-labelled existence and replay.
2. `ideas/rejected/ECDLP-IDEA-326_polynomial_partitioning_abel_jacobi_incidence_hypothesis.md` — geometry does not construct source incidence.
3. `ideas/rejected/ECDLP-IDEA-359_kakeya_nikodym_directional_source_focusing_hypothesis.md` — directional aggregates lose occurrence identity.
4. `ideas/rejected/preallocation/20260720-b_F03_fortune_voronoi_source_sweepline_preid_duplicate.md` — another sweep begins with a supplied site catalogue.
5. `ideas/rejected/preallocation/20260721-a_I06_bowyer_delaunay_source_navigator_preid_duplicate.md` — geometric navigation consumes represented sources.

## Closest primary literature

- Bentley and Ottmann, [Algorithms for reporting and counting geometric intersections](https://doi.org/10.1109/TC.1979.1675432), gives output-sensitive reporting for supplied planar objects.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not give a planar intersection representation.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source gives the elliptic-to-planar exact compiler or source lift; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, planar encoding, restrictions, degeneracy policy, and verifier.
2. Construct segments and certify compatibility iff intersection from endpoints only.
3. For each known-log target, perform exact restricted sweeps, replay one labelled tuple, and verify point equality before retaining a row.
4. Collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge segment creation, sorting, event queue, intersections, degeneracy handling, restrictions, replay, rank, logs, bit time, and memory.

## Full rho/BSGS cost model

Charge segment/event setup in `a,a_m`, restricted sweep/replay in `q,q_m`, and intersection output/ambiguity in `o,u`. With `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require the `B^(9/4)` setup/state and `B^(5/4)` fresh caps plus `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

The sweep reports intersections only after all segments are supplied. Encoding generic finite-field elliptic compatibility as planar order/intersection either enumerates source pairs, uses a DLP-compatible order, or introduces many crossings and high-degree coordinates. Quotient segments can merge different source occurrences, and exact field degeneracies defeat a generic real-plane ordering.

## Proof track

Give a public bounded-complexity planar encoding with exact all-strata intersection semantics, restriction stability, and a charged event-to-source inverse.

## Disproof track

Audit every segment and coordinate, test order dependence and degeneracies, and falsify on source enumeration, crossing/output blowup, false intersections, or lost occurrence labels.

## Positive and negative controls

- Positive: supplied labelled segment sets with planted intersections.
- Negative: dense crossing arrangements, coincident/vertical segments, duplicate endpoints, empty restrictions, and fresh targets.
- Baselines: explicit incidence scan, Fortune/Bowyer controls, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only segments, a biconditional proof, four sizes, zero false events, exact lifts, full rank, 100 blind descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied geometry, DLP ordering, any false answer, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k04_segment_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k04_sweep_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k04_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint geometry compiler, not Bentley–Ottmann. Any finite sweep remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
