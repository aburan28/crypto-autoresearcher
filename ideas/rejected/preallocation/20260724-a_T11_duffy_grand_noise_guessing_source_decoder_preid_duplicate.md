# Pre-ID duplicate draft — Duffy GRAND noise-guessing source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T11`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_noise_likelihood_and_code_membership_oracle`.
- Class/risk/lane: algorithm / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; maximum-likelihood decoding, code membership, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

Endpoint data is a noisy encoding of an exact signed-source word under a target-independent noise
law with low guesswork exponent. GRAND would guess noise patterns in likelihood order until the
corrected word passes an exact public code-membership test, then recover sources, factor logs, and
blind descents below rho.

## Mechanism-new operation

GRAND ranks supplied additive-noise sequences and queries membership of corrected words in a
supplied codebook. It counts only if endpoint data supplies a source-faithful codeword/noise model
and a compact exact membership-plus-occurrence inverse. Guessing source perturbations under a
post-hoc score or checking an explicit relation predicate is ordinary search with renamed ordering.

## Assumptions

1. Exact signed sources encode into a public additive channel model with endpoint as received word.
2. The true noise has a proved sub-rho guesswork exponent uniformly over restrictions and masks.
3. Code membership is exact, compact, source-free, and followed by a canonical occurrence inverse.
4. Abandonment, false codewords, ambiguity, output, and retries meet both caps.
5. The frozen noise law yields full-rank rows and works on 100 fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_received_codeword | target_independent_noise_likelihood_order | GRAND_membership_queries | accepted_word_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` — endpoint codeword/membership/source-lift construction is the missing lane.
2. `ideas/rejected/preallocation/20260722-a_N11_walksat_noisy_source_local_search_preid_duplicate.md` — noise-guided candidate order does not create an exact predicate.
3. `ideas/rejected/preallocation/20260722-a_N12_schoning_hamming_source_walk_contract_preid_duplicate.yaml.txt` — Hamming-neighborhood search retains supplied formula/source semantics.
4. `ideas/rejected/preallocation/20260723-b_S12_rubinstein_cross_entropy_source_sampler_preid_duplicate.md` — likelihood/score ordering is a post-hoc selector without a public compiler.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed replay remain required.

## Closest primary literature

- Duffy, Li, and Médard, [Capacity-Achieving Guessing Random Additive Noise Decoding](https://doi.org/10.1109/TIT.2019.2896110), orders supplied channel-noise guesses and tests corrected-word membership.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no additive source-code channel or low-guesswork law.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic channel model, membership/inverse, or complete descent.
Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, source code, endpoint received-word map, noise law/order, abandonment, membership/inverse, restrictions, masks, strata, and verifier.
- Build target-independent state within `B^(9/4+o(1))`, excluding relation catalogues, trained target scores, and factor logs.
- For known-log endpoints, charge received-word construction, every guessed noise, likelihood/order operation, membership query, false codeword, inverse, signed replay, and verification.
- Retain misses/dependencies; collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve every factor log.
- Reuse unchanged state on 100 fresh masks, guess/invert exact tuples, subtract masks, and verify scalars.
- Charge guesswork tails, abandonment, ambiguity, output, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, charge setup/state `N^a,N^a_m`, reciprocal row/target densities
`N^delta,N^delta_t`, guess/membership/inverse/replay `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/tail/failure `N^u`, and factor logs
`N^ell,N^ell_m`. Use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

GRAND is efficient when the physical channel supplies a concentrated noise distribution and cheap
code membership. There is no analogous public additive channel from a hidden elliptic source word
to one endpoint. Defining a likely noise requires knowing source proximity; exact membership is the
missing relation predicate, and a canonical inverse reintroduces source recovery.

## Proof track

Prove a public elliptic channel model, uniform low guesswork, compact exact membership/inverse,
full rank/logs, blind descent, and complete sub-rho costs.

## Disproof track

Exhibit equal received data/noise ordering with different sources, expose relation checking inside
membership, show heavy guesswork tails/false codewords, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied short block codes over known additive noise channels.
- Negative: flat/heavy-tailed noise, equal-received different-source fibres, false codewords, shuffled labels, empty fibres, exceptional charts, and fresh targets.
- Baselines: IDEA-014, WalkSAT/Schöning, cross-entropy, P1553 R4, rho, and BSGS.
- Maximum-likelihood native decoding remains toy/model-bound evidence for ECDLP.

## Quantitative promotion and falsification gates

- Promote only with public channel/membership/inverse theorems, zero errors at four sizes/all strata, total abandonment/miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on source-trained noise order, circular membership, one inverse ambiguity, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t11_channel_model_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t11_guesswork_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t11_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the stated ECDLP transplant, not GRAND. Correct maximum-likelihood decoding,
membership, or a valid relation remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Attempt to define a toy endpoint received-word/noise pair before choosing a hidden source and record where source-conditioned likelihood first enters.
