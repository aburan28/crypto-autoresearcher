# Pre-ID duplicate draft — Remez minimax endpoint indicator

## Status and claim labels

- Prospect: `20260721-b-J12`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: minimax_polynomial_approximation / representation-changing / representation pre-ID screen.
- State: merged_rejected_approximate_indicator_and_supplied_function_oracle.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an equioscillating approximant or correct toy classification is not an ECDLP result.

## Falsifiable hypothesis

Embed endpoint labels either in a compact interval or as a finite ordered node set, use Remez exchange where its continuous-domain hypotheses apply to build a minimax polynomial for the restricted-existence indicator, and recover one source from a certified exact gap with complete sub-rho costs.

## Mechanism-new operation

The native operation alternates interpolation and extremal-error exchange to obtain a best uniform approximation to a supplied function on a compact real domain. It counts only if the function oracle is endpoint-derived without source labels and the approximation has a proved gap separating exact zero/nonzero fibers with an occurrence decoder.

## Assumptions

1. Endpoint labels admit either a continuous interval embedding with a uniform exact source margin or a finite discrete embedding whose required degree/state stays within the caps.
2. Function evaluations required by Remez do not call the missing source predicate.
3. Polynomial degree, coefficient height, iterations, and extremum search fit the resource caps.
4. A positive approximant value yields an exact signed source occurrence on all strata.
5. The same approximant family supports independent relations and fresh blind targets.

## Semantic fingerprint

`public_endpoint_ordered_embedding | Remez_alternating_extremal_exchange | uniform_polynomial_restricted_indicator | extremal_certificate_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact zero sets and labelled replay are required.
2. `ideas/rejected/ECDLP-IDEA-209_simultaneous_hermite_pade_orbit_denominator_hypothesis.md` — compact approximants need supplied moment/evaluation information.
3. `ideas/rejected/ECDLP-IDEA-105_holonomic_diagonal_telescoper_hypothesis.md` — analytic compression does not locate exact source atoms.
4. `ideas/rejected/ECDLP-IDEA-387_balanced_truncation_hankel_mode_source_reduction_hypothesis.md` — approximation can erase rare modes/sources.
5. `ideas/rejected/preallocation/20260719-c_C05_aaa_barycentric_endpoint_interpolant_preid_duplicate.md` — adaptive rational approximation needs an endpoint function oracle and exact gap.

## Closest primary literature

- Remez, [Sur la détermination des polynômes d'approximation de degré donné](https://zbmath.org/?q=an%3A60.0217.02) (Communications de la Société Mathématique de Kharkov 10, 1934, 41–63), introduces the minimax approximation procedure.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply a cheap exact indicator oracle or uniform real margin.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs an exact ECDLP indicator approximant or source decoder; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, ordered embedding, function domain, restrictions, Remez initialization, charts, and verifier.
2. Evaluate the endpoint function, run exchange iterations, certify uniform error/margin, and store coefficients without source-oracle advice.
3. For known-log targets, make exact restricted decisions, self-reduce at most `5 ceil(log_2 B)+O(1)` times, recover a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified rows, retain failures/dependencies, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged target-independent state on `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge every function evaluation, extremum search, degree/coefficient growth, exchange iteration, certification, negative query, source replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge `T_oracle+K*(T_interpolate+T_extrema)+T_cert` and coefficient state in `a,a_m`; charge polynomial evaluation, restriction queries, exactness repair, and replay in `q,q_m`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Remez requires value access to the function being approximated; here that function is exact source existence. On a continuous interval, a discontinuous zero/one indicator cannot have uniform polynomial error below `1/2` across a jump, so it cannot certify exact status. On a finite discrete label set that continuity obstruction disappears, but classical continuous Remez scope changes and exact interpolation can require source-sized degree, coefficients, evaluations, and state. In both domains the function oracle and occurrence decoder remain missing; alternation points do not supply source provenance.

## Proof track

Construct an endpoint-only evaluation oracle and uniform gap, prove sub-rho degree/coefficient/iteration bounds, and derive an exact all-strata source decoder.

## Disproof track

For the continuous domain, exhibit a jump and certify the uniform-error `>=1/2` obstruction; for the discrete domain, measure exact interpolation degree/state on alternating labels. In both cases trace every function evaluation and extremum certificate for hidden source queries.

## Positive and negative controls

- Positive: smooth supplied functions with known minimax polynomials and labelled positive intervals.
- Negative: alternating zero/one labels, rare spikes, no-margin boundaries, duplicate endpoints, empty restrictions, and fresh targets.
- Baselines: AAA approximation, Hermite–Padé, dense interpolation, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only evaluations, a proved uniform exact gap, four sizes, zero false decisions, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on source-oracle evaluations, degree/coefficient overflow, any false answer, absent occurrence decoder, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j12_oracle_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j12_remez_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j12_cost_analysis.md`

## Interpretation boundary

This rejects the exact endpoint-indicator transplant, not Remez approximation. Finite behavior is toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
