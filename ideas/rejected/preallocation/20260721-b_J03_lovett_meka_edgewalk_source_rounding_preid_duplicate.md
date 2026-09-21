# Pre-ID duplicate draft — Lovett–Meka edge-walk source rounding

## Status and claim labels

- Prospect: `20260721-b-J03`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: discrepancy_rounding / high-risk / high-risk pre-ID screen.
- State: merged_rejected_supplied_incidence_and_approximate_balance.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; low discrepancy or a verified row is not an ECDLP result.

## Falsifiable hypothesis

Derive endpoint-only linear discrepancy constraints for signed source occurrences and run the Lovett–Meka edge-walk to round a fractional source measure into a sparse exact restriction-stable witness family whose complete relation and descent costs beat rho and BSGS.

## Mechanism-new operation

The native operation is a constrained Gaussian edge walk that progressively fixes coordinates while controlling discrepancies of supplied sets. It counts only if the coordinate universe and constraint rows arise from endpoints without enumerating sources and rounding returns exact source occurrence labels rather than a balanced aggregate.

## Assumptions

1. Endpoint equations yield a compact fractional source vector and all discrepancy constraints below the setup cap.
2. Low discrepancy implies exact nonemptiness and not merely approximate balance.
3. Fixed coordinates map injectively to repeated signed factor-base occurrences.
4. The walk succeeds uniformly for negative restrictions and fresh targets with charged restarts.
5. Rounded rows remain independent enough for full factor-base rank.

## Semantic fingerprint

`public_endpoint_fractional_source_measure | Lovett_Meka_constrained_edge_walk | low_discrepancy_restricted_rounding | fixed_coordinate_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restrictions and source replay are mandatory.
2. `ideas/rejected/ECDLP-IDEA-349_constructive_vector_discrepancy_source_rounding_hypothesis.md` — direct operation owner for discrepancy rounding from supplied vectors.
3. `ideas/rejected/ECDLP-IDEA-137_matroid_representative_completion_kernel_hypothesis.md` — a compressed representative family assumes represented elements.
4. `ideas/rejected/ECDLP-IDEA-148_isolation_weight_lowest_monomial_source_extractor_hypothesis.md` — random isolation begins after the source family exists.
5. `ideas/rejected/preallocation/20260719-d_D06_randomized_kaczmarz_source_projection_preid_duplicate.md` — projections of supplied rows do not create source coordinates.

## Closest primary literature

- Lovett and Meka, [Constructive discrepancy minimization by walking on the edges](https://arxiv.org/abs/1203.5747), gives a randomized partial-coloring algorithm for a supplied set system.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply a low-dimensional source-incidence matrix.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source turns approximate discrepancy control into exact elliptic source existence and replay; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed occurrence universe, complete charts, restriction family, randomness, and verifier.
2. Build the fractional point and constraint matrix from public endpoints without a source table; run the edge-walk and retain all randomness, frozen coordinates, and restart costs.
3. For known-log targets, self-restrict at most `5 ceil(log_2 B)+O(1)` times, return a labelled tuple, and verify point equality before row formation.
4. Collect at least `max(d_FB+32,1000)` rows, retain failures/dependencies, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge incidence construction, covariance projections, walk steps, restarts, exactness repair, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge `T_inc+K*(T_project+T_step)+T_restart` and corresponding state in `a,a_m`; charge restricted rerounding and replay in `q,q_m`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, including randomness and output ambiguity. Require the `B^(9/4)` setup/state and `B^(5/4)` fresh caps and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

The edge-walk needs one coordinate per supplied element and one vector per supplied constraint. In this transplant those are source occurrences and restriction incidences—the missing object. Discrepancy bounds additive error in aggregate sums; they neither distinguish empty from singleton fibers nor return an exact occurrence. Exactness repair restores source enumeration or the P1553 predicate.

## Proof track

Derive a compact endpoint incidence operator, prove a discrepancy-to-exact-existence gap and occurrence lift, and bound high-probability walk, rank, and fresh-target costs.

## Disproof track

Construct rare singleton and empty fibers with identical low-discrepancy summaries; trace coordinate creation and falsify if it requires source incidence or if any rounded coordinate lacks an exact lift.

## Positive and negative controls

- Positive: supplied bounded-norm set systems with planted integral colorings and labelled coordinates.
- Negative: rare singleton fibers, zero fibers, duplicate columns, near-kernel constraints, shuffled labels, and fresh targets.
- Baselines: vector discrepancy, isolation weights, Kaczmarz, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only coordinates, a proved exact gap, four sizes, zero false answers, at least `max(d_FB+32,1000)` verified rows of full rank, 100 fresh descents, failure at most `2^-80`, both caps, and `lambda,mu<=0.45`. Falsify on supplied incidence, aggregate-only output, label loss, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j03_incidence_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j03_edgewalk_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j03_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-source use of edge-walk rounding, not constructive discrepancy minimization. Finite behavior is toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
