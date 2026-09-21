# Pre-ID duplicate draft — Jeannerod–Neiger Popov source approximant

## Status and claim labels

- Provisional ID: `PREID-20260724-b-U11`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_interpolation_vectors_and_approximant_basis`.
- Class/risk/lane: algorithm / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a Popov basis, short relation, or valid elliptic row is not an ECDLP break.

## Falsifiable hypothesis

Endpoint evaluations yield a low-order polynomial-matrix interpolation instance whose shifted-Popov
minimal approximant basis contains canonical sparse vectors encoding exact signed sources. Fast
approximant-basis computation would recover full relation rank and blind descent with both complete
exponents at most `0.45`.

## Mechanism-new operation

The native operation computes minimal polynomial relations among supplied vector sequences and
normalizes them in shifted Popov form with compact output. ECDLP novelty requires a public,
source-free interpolation-vector compiler and an approximant-vector to exact occurrence inverse.
Changing the interpolation or linear-algebra backend after source-sensitive samples exist is duplicate.

## Assumptions

1. Endpoint-only samples define the interpolation vectors without source enumeration.
2. A public shift makes desired source relations uniquely minimal.
3. Popov normalization preserves signs, repetitions, exceptional strata, and point labels.
4. Sample generation, basis computation, factoring, replay, logs, and descent satisfy both caps.
5. The shift/order is frozen before targets and independent of hidden scalars.

## Semantic fingerprint

`public_endpoint_vector_samples | shifted_Popov_minimal_approximant_basis | canonical_short_polynomial_relation | exact_signed_source_lift | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-078_sparse_source_enumerator_interpolation_hypothesis.md` — interpolation begins after the missing evaluator exists.
2. `ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md` — supplied moments plus a short decoder are occupied.
3. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — matrix generator/minimal-basis backends do not create source semantics.
4. `ideas/deferred/ECDLP-IDEA-133_target_local_nonlinear_apolar_flat_extension_hypothesis.md` — flat/minimal relations still need exact atom/source inversion.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted decision and signed replay remain the gate.

## Closest primary literature

- Jeannerod, Neiger, Schost, and Villard, [Fast computation of minimal interpolation bases in Popov form](https://arxiv.org/abs/1602.00651), starts from supplied interpolation vectors.
- Massey, [shift-register synthesis](https://doi.org/10.1109/TIT.1969.1054260), is the scalar recurrence predecessor.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide low-order source-sensitive vector samples.

No checked source provides the ECDLP sample compiler or occurrence lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, vector sampler, order, shift, basis normalization, restrictions, masks, and verifier.
- Build target-independent state under `B^(9/4+o(1))` without source moments, factor logs, dense resultants, or target fitting.
- Charge every sample coordinate, polynomial-matrix product, recursive basis step, normalization, factor branch, and signed replay.
- Verify at least `max(d_FB+32,1000)` independent rows, rank `d_FB`, and all factor-base logarithms.
- Reuse byte-identical eligible state on 100 fresh masked targets, subtract masks, and verify scalars.
- Charge polynomial degree/state, output, ambiguity, failure, bit work, and peak memory.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state are `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, sampling/basis/replay work `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, and logs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Approximant-basis algorithms reveal relations among supplied samples; they do not construct
source-sensitive samples. Aggregate endpoint vectors can share the same Popov basis across
different occurrence fibres. Choosing a shift that singles out the desired support is post-hoc
advice unless derived without exact source knowledge.

## Proof track

Prove endpoint-only low-order sampling, a target-independent shift theorem, unique all-strata
approximant-to-source inversion, full rank/log/descent, and complete sub-rho costs.

## Disproof track

Hold the interpolation instance/Popov basis fixed while varying exact fibres, expose source-derived
samples or tuned shifts, or show degree/state/replay or complete exponent reaches `0.50`.

## Positive and negative controls

- Positive: supplied polynomial-vector sequences with planted short relations and labelled atoms.
- Negative: equal-approximant different-source fibres, dense/random sequences, adversarial shifts, repeated/tangent/infinity strata, and fresh targets.
- Baselines: IDEAs 053/056/078/133, P1553 R4, rho, and BSGS.
- Correct Popov normalization or a short relation is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only with exact sampler/shift/lift theorems, zero errors, failure at most `2^-80`, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-bearing sample, post-hoc shift, equal-basis source collision, cap breach, missed/false occurrence, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-b/u11_sample_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-b/u11_equal_popov_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-b/u11_polynomial_matrix_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not Popov approximant bases. Correct normalization, a short
relation, or a valid elliptic row remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Construct two smallest endpoint vector-sample families with the same shifted-Popov basis and test whether their exact signed source fibres differ.
