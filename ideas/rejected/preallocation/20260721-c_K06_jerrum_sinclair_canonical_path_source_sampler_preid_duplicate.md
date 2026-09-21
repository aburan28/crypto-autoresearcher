# Pre-ID duplicate draft — Jerrum–Sinclair canonical-path source sampler

## Status and claim labels

- Prospect: `20260721-c-K06`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: markov_chain_sampling / high-risk / pre-ID screen.
- State: merged_rejected_supplied_state_graph_and_approximate_sampling.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; rapid mixing or a sampled relation is not an ECDLP result.

## Falsifiable hypothesis

Define an endpoint-derived Markov chain on partial signed decompositions, prove rapid mixing by low-congestion canonical paths, and sample exact restricted sources often enough for full-rank relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

The native operation bounds conductance by routing canonical paths through a supplied state-transition graph. It counts only if states/transitions and canonical paths are endpoint-derived without sources, the chain detects empty restrictions exactly, and sampled states replay labelled occurrences; mixing a supplied witness graph is a control.

## Assumptions

1. A compact irreducible source chain is constructible without enumerating source tuples.
2. Canonical path congestion and mixing time fit the resource rectangle uniformly under restrictions.
3. The chain has no false-positive state and handles empty fibres exactly.
4. Stationary mass of useful independent rows is not exponentially small.
5. Frozen transitions support fresh masked targets and exact occurrence replay.

## Semantic fingerprint

`public_endpoint_source_chain | Jerrum_Sinclair_canonical_path_congestion | exact_restricted_sampling | state_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact empty/singleton restrictions and replay.
2. `ideas/rejected/ECDLP-IDEA-081_toric_markov_fiber_walk_hypothesis.md` — a fibre walk presupposes represented moves/states.
3. `ideas/rejected/ECDLP-IDEA-104_lorentzian_relation_measure_sampler_hypothesis.md` — sampling aggregate measures does not return exact sources cheaply.
4. `ideas/rejected/ECDLP-IDEA-302_propp_wilson_coupling_source_sampler_hypothesis.md` — exact sampling still requires a source-bearing chain.
5. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — MCMC proposals and target densities are supplied source objects.

## Closest primary literature

- Jerrum and Sinclair, [Approximating the permanent](https://doi.org/10.1137/0218077), uses a Markov chain and canonical-path/conductance analysis on a represented matching state space.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not provide the state graph or proposal kernel.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the exact ECDLP chain, canonical routes, empty-fibre decision, or source lift; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, state encoding, transition kernel, seeds, restrictions, charts, and verifier.
2. Construct states and moves from endpoints only; prove detailed balance, irreducibility, congestion, and source-free provenance.
3. For known-log targets, make exact restricted decisions, mix with charged burn-in, sample/replay a tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs.
5. Freeze the chain before `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge state construction, transitions, congestion proof obligations, burn-in, autocorrelation, failures, density, replay, rank, logs, bit time, and memory.

## Full rho/BSGS cost model

Charge chain setup/state in `a,a_m`, mixing/query/replay in `q,q_m`, and effective-sample/ambiguity costs in `o,u`. With `beta=1/5`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, including inverse stationary mass plus integrated autocorrelation. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, semantic failure at most `2^-80`, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Canonical paths analyze a chain whose states and transitions are already known. Exact relation states are the missing source fibre, and local moves preserving an endpoint require source tuples or expensive constrained solves. Approximate sampling cannot certify emptiness, rare useful states can have negligible stationary mass, and a mixed aggregate state does not automatically retain occurrence provenance.

## Proof track

Construct the chain publicly, prove exact state semantics, rapid mixing and useful mass uniformly under restrictions, and give a charged labelled replay.

## Disproof track

Audit state/move origins, exhibit bottlenecks or exponentially rare sources, test empty restrictions, and falsify on circular proposals, approximate-only decisions, or missing replay.

## Positive and negative controls

- Positive: supplied rapidly mixing labelled matching chains with known stationary mass.
- Negative: disconnected fibres, narrow bottlenecks, rare singleton states, empty restrictions, duplicate endpoints, and fresh targets.
- Baselines: direct sampling, Metropolis–Hastings, CFTP, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only chain construction, a proved polynomial congestion bound within the caps, exact emptiness, four sizes, full rank, 100 fresh descents, failure `<=2^-80`, and `lambda,mu<=0.45`. Falsify on supplied states, a bottleneck, false emptiness, missing occurrence lift, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k06_chain_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k06_mixing_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k06_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-chain transplant, not canonical-path MCMC analysis. Any finite mixing trace is toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
