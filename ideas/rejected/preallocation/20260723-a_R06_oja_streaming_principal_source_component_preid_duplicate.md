# Pre-ID duplicate draft — Oja streaming principal source component

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R06`; no canonical ID allocated.
- Disposition: `merged_rejected_streaming_covariance_aggregate`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; component convergence, a valid relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, scalar-blind endpoint samples define a covariance stream whose
leading component canonically identifies exact signed factor-base sources. Oja updates learn that
component using target-independent state, enabling full relation rank, all factor logs, and 100
fresh blind descents with complete exponents at most `0.45`.

## Mechanism-new operation

Oja's normalized Hebbian update learns the principal component of a supplied sample
distribution. It counts only if the samples are public-endpoint-derived without source labels,
the leading component is separated on every restriction, and it inverts exactly to occurrence
identities. Training on enumerated sources or post-hoc successful relations is a selector control.

## Assumptions

1. Scalar-blind public sampling exposes source covariance without enumerating source tuples.
2. A restriction-uniform spectral gap selects the true source rather than an aggregate direction.
3. Sample complexity, normalization, precision, and state fit the caps.
4. The learned component determines exact signs, repetitions, and occurrence labels.
5. Training is target-independent and frozen before 100 blind targets.

## Semantic fingerprint

`public_endpoint_sample_stream | normalized_hebbian_principal_component_update | exact_source_direction | charged_occurrence_inverse | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-b_B11_frequent_directions_source_sketch_preid_duplicate.md` — streaming covariance compression is aggregate.
2. `ideas/rejected/preallocation/20260719-b_B10_cur_skeleton_source_matrix_preid_duplicate.md` — selected rows/columns require supplied source matrix access.
3. `ideas/rejected/preallocation/20260720-a_E09_bootstrap_particle_source_filter_preid_duplicate.md` — adaptive sampling begins from a supplied state model and observations.
4. `ideas/rejected/preallocation/20260721-b_J11_adaboost_endpoint_weak_oracle_preid_duplicate.md` — training cannot turn heuristic predictors into exact source semantics.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — owns the exact endpoint predicate and replay path.

## Closest primary literature

- Oja, [Simplified Neuron Model as a Principal Component Analyzer](https://doi.org/10.1007/BF00275687), learns a principal component from a supplied sample stream.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not define the claimed source-covariance sampler.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls generic costs.

The source sampler, exact gap, and inverse are outside Oja's result; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, sampler, features, update order, learning rates, normalization, restrictions, strata, and verifier.
2. Build target-independent sampling state within `B^(9/4+o(1))`; exclude source labels, known scalar residues, and post-hoc accepted rows.
3. For each known-log target, learn/apply the frozen component, recover signed occurrences, and verify the curve sum.
4. Gather at least `max(d_FB+32,1000)` verified independent rows, rank `d_FB`, and all factor logs.
5. Apply identical frozen state to 100 fresh masked targets, recover sources, subtract masks, and verify every scalar.
6. Charge sample generation, all updates, burn-in, precision, restarts, failures, output, rank, logs, bits, and peak state.

## Full rho/BSGS cost model

With `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, sampling/query work `N^q,N^q_m`, rank credit `N^r`, output
`N^o`, ambiguity/training repetitions `N^u`, and factor-log costs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require both exponents `<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS remain `0.50`.

## Likely fatal obstruction

Covariance forgets sample identity. Different source sets can have the same leading component,
and rare sources need not affect it. Producing source-correlated samples without labels is the
original relation problem; exact inversion or restriction retraining restores the source stream.

## Proof track

Prove scalar-blind sampling, a uniform exact eigengap on all restrictions, subcap convergence,
and a deterministic occurrence inverse through full logs and blind descent.

## Disproof track

Construct equal-covariance different-source streams, a rare source outside the principal
direction, training leakage, restriction-dependent retraining, replay ambiguity, or exponent
`>=0.50`.

## Positive and negative controls

- Positive: supplied toy streams with a planted unique labelled principal source.
- Negative: equal-covariance permutations, rare singleton sources, empty fibres, shuffled
  labels, exceptional additions, and fresh blind targets.
- Baselines: Frequent Directions, bootstrap filtering, AdaBoost, P1553 R4, rho, and BSGS.
- PCA convergence is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact four-size/all-strata controls, proved source-blind sampling and gap,
  full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one covariance collision, training label, missed rare source, cap violation, or
  complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r06_sampler_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r06_equal_covariance_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r06_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Oja's rule. Learned components and valid rows remain toy,
heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Build two toy endpoint sample streams with identical covariance and different signed source support and test the frozen Oja map without labelled training data.
