# Pre-ID duplicate draft — Berlekamp–Welch error-locator source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T05`; no canonical ID allocated.
- Disposition: `merged_rejected_endpoint_received_word_and_error_locator_source_oracle`.
- Class/risk/lane: algebraic_algorithm / conservative / conservative top pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a correct error locator, decoded polynomial, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-only evaluation word differs in few positions from a source-labelled relation
codeword. Berlekamp–Welch rational interpolation would recover an error locator and message
polynomial that invert to every exact signed source, enabling full-rank factor logs and 100 fresh
blind descents with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation solves `N_i=E_i y_i` for a supplied received word, then divides the numerator
by the error-locator polynomial. It counts only if the endpoint constructs source-indexed
evaluations and a sparse error promise without knowing the hidden tuple. Otherwise this is the
exact IDEA-014 endpoint-syndrome/error-locator lane or a solver substitution for IDEA-336.

## Assumptions

1. A target-independent code associates every exact signed tuple with a low-degree word.
2. Endpoint data supplies a received word within the unique-decoding radius without source advice.
3. The recovered locator/message pair lifts biconditionally to occurrence-labelled elliptic points.
4. Repetitions, signs, infinity, tangencies, and nonreduced fibres are represented exactly.
5. Word construction, linear solve, division, output, rank, logs, descent, and memory meet both caps.

## Semantic fingerprint

`public_endpoint_received_word | sparse_error_locator_rational_interpolation | decoded_source_codeword | exact_signed_point_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` — the direct public-target syndrome/error-locator owner.
2. `ideas/rejected/ECDLP-IDEA-336_guruswami_sudan_source_list_decoder_hypothesis.md` — source-indexed received evaluations remain unsupplied.
3. `ideas/rejected/ECDLP-IDEA-063_provenance_preserving_subresultant_forest_hypothesis.md` — rational polynomial backends do not construct source provenance.
4. `ideas/rejected/ECDLP-IDEA-130_folded_ag_list_recovery_source_decoder_hypothesis.md` — algebraic-code decoding after word construction is a backend change.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable existence and signed replay remain required.

## Closest primary literature

- Welch and Berlekamp, [Error correction for algebraic block codes](https://patents.google.com/patent/US4633470A/en), recovers error-locator/message data from a supplied algebraic-code word within its correction promise.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a near-codeword with occurrence-labelled errors.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the comparison boundary.

No checked source constructs the endpoint received word, proves a sparse-error promise and exact
point inverse, or completes descent. The transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, code/evaluation positions, endpoint word rule, degree/error bounds, linear solver, division/lift policy, restrictions, masks, and verifier.
- Compile target-independent state within `B^(9/4+o(1))`, forbidding source dictionaries, factor logs, and dense source evaluations.
- On known-log endpoints, charge word construction, all equations, rank defects, locator solve, polynomial division, every candidate lift, signed replay, and row verification.
- Collect at least `max(d_FB+32,1000)` verified rows, retain misses/dependencies, require rank `d_FB`, and solve every factor-base logarithm.
- Reuse identical state on 100 fresh `Q+[t]P`, decode/lift tuples, subtract masks, and verify every scalar.
- Charge setup, word size, error density, output, rank, factor solve, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal row/target densities
`N^delta,N^delta_t`; word/solve/division/lift work `N^q,N^q_m`; rank credit
`N^r`; output `N^o`; ambiguity/failure `N^u`; and factor logs
`N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Berlekamp–Welch locates errors only because the received symbols and evaluation positions are
already supplied. For ECDLP, a word agreeing with the hidden source codeword at most positions
encodes the very source information sought. Endpoint-only aggregate evaluations can be identical
for different fibres; source-faithful evaluations restore IDEA-014's missing oracle.

## Proof track

Prove endpoint-only near-codeword construction, uniform error-radius and exact all-strata point
lift, then prove full rank/logs, blind descent, and complete sub-rho costs.

## Disproof track

Exhibit equal endpoint words with different sources, show one received symbol needs a hidden
occurrence, violate the correction radius/lift, or derive a complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied Reed–Solomon words with planted correctable errors and labelled codewords.
- Negative: random endpoint words, equal-word different-source fibres, too many errors, repeated labels, exceptional charts, empty fibres, and fresh masks.
- Baselines: IDEA-014, Guruswami–Sudan, folded AG decoding, P1553 R4, rho, and BSGS.
- Correct decoding of a supplied word remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public word/lift theorems, zero errors at four sizes/all strata, miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing word symbol, radius/lift failure, false relation, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t05_received_word_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t05_equal_word_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t05_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP route, not Berlekamp–Welch decoding. Correct locator recovery,
polynomial division, or a valid row remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Define every proposed received-word coordinate for a toy curve and mark whether it is computable before any source occurrence or factor log is known.
