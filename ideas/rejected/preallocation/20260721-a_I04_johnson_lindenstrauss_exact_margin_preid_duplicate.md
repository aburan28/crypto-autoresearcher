# Pre-ID duplicate draft — Johnson–Lindenstrauss exact-margin source embedding

## Status and claim labels

- Prospect: `20260721-a-I04`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: randomized_embedding / representation_changing / representation-changing pre-ID screen.
- State: scoped_rejected_approximate_metric_and_supplied_source_vectors.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; distance preservation, a collision, or a toy scalar is not a breakthrough.

## Falsifiable hypothesis

Map endpoint/source feature vectors through a public Johnson–Lindenstrauss projection with a proved separation margin, then answer exact restricted existence and replay one signed tuple below rho/BSGS.

## Mechanism-new operation

JL random projection preserves pairwise Euclidean distances approximately in logarithmic dimension. It counts only if public endpoint features have an a priori exact gap and the projected cell lifts to every signed occurrence; projecting a supplied source vector catalogue is a representation control.

## Assumptions

1. Endpoint-only features exist before source enumeration.
2. Equal and unequal source completions have a public gap larger than worst-case distortion.
3. Projection randomness and failure probability are independent, recorded, and charged.
4. Projected buckets preserve all duplicates, signs, restrictions, and exceptional strata.
5. One target-independent map supports factor logs and fresh blind descent.

## Semantic fingerprint

`public_endpoint_features | Johnson_Lindenstrauss_random_projection | exact_gap_restricted_membership | projected_cell_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-344_locality_sensitive_exact_complement_filter_hypothesis.md` — approximate locality lacks an exact elliptic gap.
2. `ideas/rejected/ECDLP-IDEA-349_constructive_vector_discrepancy_source_rounding_hypothesis.md` — vectors are supplied source state and rounding loses labels.
3. `ideas/rejected/preallocation/20260719-b_B10_cur_skeleton_source_matrix_preid_duplicate.md` — projection begins after a source matrix exists.
4. `ideas/rejected/preallocation/20260719-b_B11_frequent_directions_source_sketch_preid_duplicate.md` — low-dimensional sketches preserve norms, not exact occurrences.
5. `ideas/rejected/preallocation/20260720-d_H11_dbscan_density_source_cluster_preid_duplicate.md` — metric neighborhoods are not exact equality witnesses.

## Closest primary literature

- Johnson and Lindenstrauss, [Extensions of Lipschitz mappings into a Hilbert space](https://doi.org/10.1090/conm/026/737400), proves approximate finite-set distance preservation, not exact source inversion.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives algebraic endpoint equations rather than a separated Euclidean embedding.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source proves the proposed exact elliptic margin; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, feature map, public projection distribution, restrictions, exceptional charts, and verifier.
2. Construct endpoint features, projection, and duplicate-preserving bucket state without enumerating source tuples or invoking `Query2P1`.
3. For known-log targets, use exact projected gap decisions and restricted self-reduction to replay signed points, verify their sum, and record valid rows.
4. For actual `d_FB`, retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged state for `Q+[t]P`, replay, compute `x`, and verify `[x]P=Q`.
6. Charge feature construction, random bits, projection, bucket traffic, failure amplification, restrictions, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Let `a,a_m` include feature/projection/bucket setup and `q,q_m` include restricted queries, exact fallback, and replay. With `B=N^(1/5)`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `beta=1/5`, `0<=r<=o`.

Projection failure amplification and collision verification are in `u`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`, versus rho/BSGS `0.50`.

## Likely fatal obstruction

JL preserves approximate distances for supplied vectors. The elliptic relation predicate is exact and has no known endpoint-derived Euclidean separation; near collisions can be arbitrarily close under any ad hoc feature map. Exact verification filters false positives only after candidates exist, while storing source vectors/buckets is the missing source table.

## Proof track

Construct an endpoint-only feature map with a proved polynomial exact gap, bounded projection dimension, duplicate-preserving inversion, and complete restriction/descent costs.

## Disproof track

Produce unequal tuples with vanishing/small feature gap or trace every stored vector to source state; falsify if exact fallback or candidate traffic reaches the source deck.

## Positive and negative controls

- Positive: supplied separated Euclidean vectors with planted duplicates and exact backpointers.
- Negative: arbitrarily close unequal vectors, feature collisions, shuffled backpointers, empty restrictions, and fresh blind targets.
- Baselines: unprojected features, LSH/sketch owners, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require a proved exact gap, recorded failure at most `2^-80`, zero false decisions, exact lifts, four increasing sizes, rank `d_FB` from at least `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on no gap, supplied vectors, lost duplicates, false answers, cap failure, or a complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i04_exact_margin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i04_projection_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i04_cost_analysis.md`

## Interpretation boundary

This rejects the exact-margin transplant, not JL. Any toy separation remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute the contract.
