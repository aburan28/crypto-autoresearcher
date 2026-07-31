# Pre-ID duplicate draft — Goemans–Williamson source rounding

## Status and claim labels

- Prospect: `20260721-c-K08`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: semidefinite_rounding / high-risk / high-risk pre-ID screen.
- State: merged_rejected_supplied_conflict_sdp_and_approximation_gap.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an SDP value, cut, or verified relation is not an ECDLP result.

## Falsifiable hypothesis

Derive a compact endpoint conflict SDP whose integral optima are exact signed source tuples, use Goemans–Williamson random-hyperplane rounding plus exact repair to answer every restriction, and complete descent below rho and BSGS.

## Mechanism-new operation

The native operation solves a supplied vector relaxation and rounds vectors by a random hyperplane with an approximation guarantee. It counts only if the SDP is endpoint-derived, its integrality gap is zero on all source restrictions, and rounding plus repair returns exact occurrences with negligible charged failure; rounding a supplied conflict graph is a control.

## Assumptions

1. A polynomial-size SDP encodes the exact five-source fibre without a source dictionary.
2. Every feasible optimum has a uniformly bounded exact margin and zero integrality gap.
3. Random rounding plus repair preserves rare singleton and empty semantics.
4. Integral labels lift to signed factor-base occurrences on all strata.
5. The relaxation is target-independent and reusable for fresh masked targets.

## Semantic fingerprint

`public_endpoint_source_SDP | Goemans_Williamson_random_hyperplane_rounding | exact_restricted_integral_repair | cut_labels_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted predicate and source replay.
2. `ideas/rejected/ECDLP-IDEA-328_sos_pseudoexpectation_source_rounding_hypothesis.md` — relaxations do not create exact source sections.
3. `ideas/rejected/ECDLP-IDEA-335_lovasz_theta_source_rounding_hypothesis.md` — graph SDP bounds consume the source conflict graph.
4. `ideas/rejected/ECDLP-IDEA-349_constructive_vector_discrepancy_source_rounding_hypothesis.md` — approximate rounding loses exact occurrence identity.
5. `ideas/rejected/preallocation/20260719-d_D04_alpha_expansion_source_labeling_preid_duplicate.md` — approximation moves start from supplied labels/energy.

## Closest primary literature

- Goemans and Williamson, [Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming](https://doi.org/10.1145/227683.227684), proves approximation via random-hyperplane rounding for supplied instances.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not provide the compact exact SDP.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source gives the exact ECDLP SDP, zero-gap theorem, or occurrence repair; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, SDP variables/constraints, rounding seeds, restrictions, charts, and verifier.
2. Construct the relaxation from endpoints only and prove integral/source biconditionality.
3. For each known-log target, solve exact restricted relaxations, round/repair, replay a tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve all factor logs.
5. Freeze the formulation and randomness policy before `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge matrix construction, precision, SDP solve, rounding attempts, repair, false solutions, density, replay, rank, logs, bit time, and peak memory.

## Full rho/BSGS cost model

Charge formulation/solve state in `a,a_m`, each restricted solve/round/repair in `q,q_m`, and retries/solutions in `o,u`. With `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; include bit precision and worst-case gap. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, failure `<=2^-80`, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Goemans–Williamson guarantees only an approximate cut on a supplied graph. Exact elliptic source recovery needs a source-incidence formulation, zero integrality gap, and exact rare-event repair. The graph/constraints are the missing source object; approximate objective value cannot distinguish zero from a singleton fibre, and repair invokes the original constrained-source oracle.

## Proof track

Derive the SDP publicly, prove zero integrality gap and uniform exact margin under all restrictions, and give a charged occurrence-preserving rounding/repair theorem.

## Disproof track

Audit constraint origins, construct fractional optima and singleton gaps, test rounding tails and repair circularity, and falsify on any source-supplied matrix or approximate-only guarantee.

## Positive and negative controls

- Positive: supplied integral conflict SDPs with planted labelled cuts and exact repair.
- Negative: integrality-gap instances, rare singleton cuts, zero-margin collisions, empty restrictions, and fresh targets.
- Baselines: Lovasz theta, SOS, discrepancy/alpha-expansion controls, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only formulation, zero-gap/margin theorem, zero errors over four sizes, failure `<=2^-80`, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied incidence, a fractional gap, circular repair, false answer, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k08_sdp_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k08_rounding_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k08_cost_analysis.md`

## Interpretation boundary

This rejects the exact endpoint-source SDP transplant, not Goemans–Williamson approximation. Any finite rounded tuple remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute the contract.
