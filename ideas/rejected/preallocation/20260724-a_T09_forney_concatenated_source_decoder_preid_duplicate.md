# Pre-ID duplicate draft — Forney concatenated source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T09`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_inner_outer_codewords_and_decoder_composition`.
- Class/risk/lane: composition / conservative / conservative pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; inner/outer decoding, an error exponent, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

A target-independent inner representation locally exposes signed occurrence blocks while an outer
algebraic code corrects missing or ambiguous blocks. Concatenated decoding would convert endpoint
observations into exact relation tuples, full-rank factor logs, and 100 blind descents within the
complete sub-rho caps.

## Mechanism-new operation

Forney concatenation composes supplied inner and outer encoders/decoders to trade alphabet,
distance, and complexity. It counts only if endpoint data constructs inner received blocks with
exact source meaning and the outer decoder preserves occurrence provenance. Composing two decoders
after a source word is available cannot remove either decoder's missing endpoint-to-source oracle.

## Assumptions

1. Endpoint-only inner observations agree with source-labelled inner codewords at sufficient rate.
2. A compact outer word/check structure is target-independent and below the setup/state cap.
3. Inner ambiguities and erasures remain within an outer correction radius on every stratum.
4. Outer symbols invert canonically to signed occurrences, including repeats and exceptional charts.
5. Inner/outer traffic, retries, output, rank, logs, descent, and memory satisfy both caps.

## Semantic fingerprint

`public_endpoint_inner_blocks | source_preserving_inner_decode | outer_algebraic_error_correction | concatenated_symbol_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-336_guruswami_sudan_source_list_decoder_hypothesis.md` — outer list decoding still needs source-correlated received symbols.
2. `ideas/rejected/ECDLP-IDEA-130_folded_ag_list_recovery_source_decoder_hypothesis.md` — supplied algebraic-code words do not create endpoint source semantics.
3. `ideas/rejected/ECDLP-IDEA-268_multiplicity_code_hasse_jet_local_lift_hypothesis.md` — local decoder queries need a source word oracle.
4. `ideas/rejected/ECDLP-IDEA-132_high_dimensional_expander_sheaf_decoder_hypothesis.md` — local-to-global decoding begins after supplied local views.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and occurrence replay remain required.

## Closest primary literature

- Forney, [Concatenated Codes](https://mitpress.mit.edu/9780262060158/concatenated-codes/), composes inner and outer codes to obtain reliability with manageable supplied-code decoding complexity.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no source-correlated inner blocks.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies either elliptic received-word compiler, an exact occurrence inverse, or
the complete relation/log/descent path. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, inner/outer alphabets and codes, block map, decoders, ambiguity policy, restrictions, masks, strata, and verifier.
- Build target-independent encoder/check state within `B^(9/4+o(1))`, forbidding source dictionaries and factor logs.
- For known-log endpoints, charge every inner observation/decode, erasure/list, outer decode, cross-block consistency check, occurrence lift, replay, and relation verification.
- Retain failures/dependencies; collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
- Reuse byte-identical state on 100 fresh masked targets, execute both decoding layers, subtract masks, and verify scalars.
- Charge code representation, block traffic, failure amplification, output, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, charge setup/state `N^a,N^a_m`, reciprocal row/target densities
`N^delta,N^delta_t`, inner/outer decode and replay `N^q,N^q_m`, rank credit
`N^r`, list/output `N^o`, ambiguity/failure `N^u`, and factor logs
`N^ell,N^ell_m`. Use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Concatenation amplifies reliability of an already encoded message; it does not construct the
received source word. Exact inner blocks would already expose partial elliptic sources, while
aggregate blocks lose occurrence identity. Outer correction can repair supplied errors but cannot
distinguish endpoint-equivalent fibres with different hidden tuples.

## Proof track

Prove public inner observations, uniform inner/outer correction and exact all-strata occurrence
inverse, then full rank/logs, blind descent, and complete sub-rho costs.

## Disproof track

Hold inner observations fixed while changing the source fibre, expose source-bearing block data,
violate outer radius/inverse, or derive traffic/state exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied concatenated-code words with planted inner errors/erasures.
- Negative: equal-inner-data different-source fibres, adversarial block errors, outer-radius failures, repeated labels, empty fibres, exceptional charts, and fresh targets.
- Baselines: IDEA-336/130/268/132, P1553 R4, rho, and BSGS.
- A decoded concatenated word or error exponent remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public inner/outer compiler and inverse theorems, zero errors at four sizes/all strata, miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing block, inner/outer ambiguity, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t09_inner_block_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t09_concatenation_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t09_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP composition, not concatenated codes. Correct decoding, an error
exponent, or a valid relation remains `toy`, `heuristic`, `model-bound`, `novelty-unverified`, and
not a breakthrough.

## Exactly one next executable action

1. Specify one proposed endpoint-derived inner block and test whether two different exact source fibres can produce the same block sequence.
