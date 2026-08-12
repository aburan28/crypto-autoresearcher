# Pre-ID duplicate draft — Prange information-set source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T06`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_parity_check_syndrome_and_random_information_sets`.
- Class/risk/lane: algorithm / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; syndrome decoding, a low-weight vector, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

A public parity-check representation maps exact signed relation sources to low-weight error vectors
whose syndrome is computable from the endpoint. Random information-set trials would recover
occurrence positions below rho, supply full-rank factor logs, and enable fresh scalar-blind descent.

## Mechanism-new operation

Prange decoding samples an information set for a supplied code and syndrome, hoping the chosen
coordinates avoid the unknown error support. It counts only if an endpoint-to-syndrome/compiler
maps elliptic sources to low-weight errors without enumerating them and if decoded positions lift
exactly to signed occurrences. Sampling different subsets after an explicit syndrome is available
is a solver schedule, not a new ECDLP operation.

## Assumptions

1. A compact target-independent parity-check matrix indexes signed factor-base occurrences.
2. The endpoint determines an exact syndrome while every valid tuple maps to bounded Hamming weight.
3. Information-set success probability, elimination cost, and retries meet both caps.
4. Decoded support/value data preserves signs, repetitions, order, and exceptional strata.
5. The same matrix/compiler yields full-rank rows and works on 100 fresh masked targets.

## Semantic fingerprint

`public_elliptic_parity_check | endpoint_source_syndrome | random_information_set_elimination | low_weight_support_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-150_moore_syndrome_rank_metric_source_decoder_hypothesis.md` — a code syndrome decoder still needs the endpoint compiler.
2. `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` — direct endpoint-syndrome/source-lift ownership.
3. `ideas/rejected/ECDLP-IDEA-168_disjunct_pool_incidence_source_locator_hypothesis.md` — support location requires source-preserving tests.
4. `ideas/rejected/preallocation/20260722-b_O03_pinsketch_endpoint_syndrome_decoder_preid_duplicate.md` — sparse syndrome decoding does not create endpoint source semantics.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and replay remain required.

## Closest primary literature

- Prange, [The use of information sets in decoding cyclic codes](https://doi.org/10.1109/TIT.1962.1057777), samples information sets for a supplied code/syndrome decoding problem.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no low-weight code syndrome.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic parity-check/syndrome compiler, exact position lift, or
complete descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, parity-check representation, syndrome rule, weight promise, information-set sampler, elimination, restrictions, masks, and verifier.
- Build target-independent matrix/state within `B^(9/4+o(1))`, excluding relation catalogues and factor logs.
- For known-log endpoints, charge syndrome construction, every sampled set, rank test, elimination, retry, decoded vector, signed replay, and relation verification.
- Retain misses/dependencies; collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve every factor log.
- Reuse byte-identical state on 100 fresh masked targets, decode/replay tuples, subtract masks, and independently verify scalars.
- Charge success probability, matrix traffic, failure amplification, output, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, charge setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, syndrome/ISD/elimination/replay `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/retries `N^u`, and factor-log solve
`N^ell,N^ell_m`. Use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Information-set decoding begins after a parity-check matrix and syndrome encode the hidden error
support. Public elliptic endpoints do not provide such a low-weight linearization. Constructing it
is IDEA-014's missing operation; once supplied, Prange only changes how the explicit syndrome
problem is searched and typically retains exponential subset trials.

## Proof track

Prove a compact endpoint syndrome map with a uniform low-weight biconditional, exact all-strata
support lift, subcap ISD probability/cost, full rank/logs, and blind descent.

## Disproof track

Expose source enumeration in one matrix/syndrome entry, show equal syndromes with different
supports, violate low weight, or derive trial/elimination/memory exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied random linear codes with planted correctable low-weight errors.
- Negative: equal-syndrome different-source fibres, high-weight sources, singular sets, shuffled labels, empty restrictions, exceptional charts, and fresh targets.
- Baselines: IDEA-014/150, PinSketch, P1553 R4, rho, and BSGS.
- Decoding a supplied syndrome remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public syndrome/lift theorems, zero errors at four sizes/all strata, miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on source-bearing syndrome data, one support ambiguity, trial/cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t06_syndrome_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t06_support_collision_fixtures.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t06_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the declared ECDLP transplant, not information-set decoding. A decoded low-weight
vector or valid relation remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and not
a breakthrough.

## Exactly one next executable action

1. Write the proposed parity-check and endpoint-syndrome equations for the smallest nontrivial toy factor base and audit every source-dependent term.
