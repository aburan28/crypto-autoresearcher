# Pre-ID duplicate draft — Cuthill-McKee bandwidth source ordering

## Status and claim labels

- Prospect: `20260721-d-L06`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: representation / representation-changing / representation-changing pre-ID screen.
- State: merged_rejected_supplied_sparsity_graph_and_ordering_only.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; reduced bandwidth, a valid sparse solve, or a relation is not an ECDLP result.

## Falsifiable hypothesis

Represent endpoint relation compatibility as a sparse symmetric matrix, apply Cuthill-McKee breadth-first degree ordering to expose a uniformly narrow band stable under restrictions, solve/replay signed occurrences inside that band, and complete factor logs plus blind descent below rho and BSGS.

## Mechanism-new operation

The native operation orders vertices by breadth-first layers while visiting low-degree neighbors first to reduce matrix bandwidth. It counts only if the sparsity graph is endpoint-derived, the band gives an exact source section, and all restriction updates remain narrow; permuting a supplied incidence matrix is a representation/backend control.

## Assumptions

1. A public endpoint compiler produces the exact sparse compatibility matrix below source scale.
2. Cuthill-McKee bandwidth remains `B^(<=5/4+o(1))` across all restrictions and targets.
3. Band entries preserve occurrence-distinct signed source provenance and exceptional strata.
4. Banded solving returns an exact tuple rather than only an aggregate or rank certificate.
5. One target-independent ordering serves known-log relations and fresh masked targets.

## Semantic fingerprint

`public_endpoint_sparse_compatibility_matrix | Cuthill_McKee_BFS_degree_ordering | restriction_stable_narrow_band | band_solution_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable target predicate and source replay frontier.
2. `ideas/rejected/preallocation/20260719-a_A08_nested_dissection_schur_source_separator_preid_duplicate.md` — sparse ordering begins with supplied source incidence and can create dense Schur state.
3. `ideas/rejected/preallocation/20260719-d_D12_multilevel_coarsened_source_partition_preid_duplicate.md` — reordered/coarsened graphs do not construct or preserve exact source fibres.
4. `ideas/rejected/preallocation/20260721-c_K11_fiduccia_mattheyses_source_partition_refinement_preid_duplicate.md` — bandwidth/cut heuristics can strand a singleton witness.
5. `ideas/rejected/ECDLP-IDEA-370_spectral_sparsification_source_router_hypothesis.md` — spectral compression does not supply exact restricted edge nonemptiness or replay.

## Closest primary literature

- Cuthill and McKee, [Reducing the bandwidth of sparse symmetric matrices](https://doi.org/10.1145/800195.805928), orders a supplied sparse symmetric matrix to reduce bandwidth.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations without the required narrow exact incidence matrix.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), gives the generic baseline.

No checked source constructs the source-free sparsity graph, proves uniform restriction bandwidth, or lifts a band solution to signed occurrences; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional strata, matrix semantics, and independent point verifier.
2. Construct and certify the endpoint-derived sparse matrix, ordering, band entries, and source satellites without source enumeration or scalar labels.
3. For each known-log target, answer at most `5 ceil(log_2 B)+O(1)` restricted band problems, replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge matrix construction, ordering, fill/bandwidth, restrictions, solving, replay, density, rank, logs, blind descent, bit time, and memory.

## Full rho/BSGS cost model

Charge sparse-matrix/order setup in `a,a_m`, restricted band solve/replay in `q,q_m`, and outputs/ambiguity in `o,u`. With `B=N^beta`, `beta=1/5`, `delta,delta_t,r,ell,ell_m` as usual, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50`.

## Likely fatal obstruction

Cuthill-McKee permutes a supplied matrix; it does not lower the information needed to build exact compatibility entries. Generic relation incidence need not have small bandwidth under any public ordering, and coordinate restrictions can destroy one favorable order. A narrow numerical or Boolean band also lacks the signed occurrence inverse unless source satellites are retained.

## Proof track

Construct the endpoint-only sparse matrix and prove a uniform band bound under every restriction together with an exact all-strata source lift and complete below-rho costs.

## Disproof track

Measure bandwidth/fill on adversarial restrictions and trace every nonzero; falsify on supplied incidence, source-sized satellites, a bandwidth/resource exponent above the cap, false lift, or total exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied banded matrices with planted labelled source paths.
- Negative: random regular incidence, adversarial permutations/restrictions, identical rows from distinct occurrences, empty fibres, and fresh targets.
- Baselines: Cuthill-McKee, nested dissection, multilevel ordering, spectral sparsification, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only matrix construction, four increasing sizes, zero false decisions, exact replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied nonzeros, unstable bandwidth, one lost occurrence, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l06_nonzero_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l06_cuthill_mckee_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l06_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only bandwidth-ordering transplant, not Cuthill-McKee on supplied sparse matrices. Every finite reduction remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
