# ECDLP-IDEA-336 — Guruswami–Sudan source list decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_list_decoder_requires_received_source_evaluations_and_returns_aggregate_codewords`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a decoding radius, interpolating polynomial, valid relation, or toy codeword is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-derived evaluations form a received word close to source-indexed low-degree codewords, allowing Guruswami–Sudan interpolation and factorization to return all exact signed factor tuples within the P1553 bounds.

## Mechanism-new operation

The screened operation is **encode source tuples as low-degree functions, derive a received word from the endpoint, perform multiplicity interpolation, factor the bivariate interpolant, and decode candidate source codewords**. This merges with IDEAs 014, 063, 098, 130, 136, 150, 268, and 281: a list decoder assumes evaluations correlated with an existing codeword. Constructing source-indexed evaluations from the endpoint is the missing source oracle; interpolation/factorization is then a backend.

## Assumptions

1. A target-independent algebraic code represents exact signed tuples with distance sufficient for list decoding.
2. Endpoint-only computation supplies a received word agreeing with each hidden source codeword beyond the decoding radius.
3. The output list is bounded and maps biconditionally to every source stratum.
4. Evaluation construction, interpolation, factorization, list output, rank, factor logs, descent, verification, and memory are charged.
5. The same encoding and received-word rule apply to fresh masked targets.

## Semantic fingerprint

`signed_source_codeword_encoding | endpoint_derived_received_word | multiplicity_interpolation | codeword_factor_list_to_exact_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-P1425-EXACT-PHASE-LIFT-CONTROL`, the exact finite-field interpolation control.
2. `inputs/ledger_inventory.json` — imported `ECFG-P1427-EXACT-RIEMANN-ROCH-COMPILER-CONTROL`, the full-rank coefficient and multipoint-evaluation control.
3. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the batched source generator hypothesis.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE2-TRANSLATED-CIRCUIT-TRADEOFF`, the compact endpoint circuit versus source-output boundary.

## Closest primary literature

- Guruswami and Sudan, [Improved decoding of Reed-Solomon and algebraic-geometry codes](https://doi.org/10.1109/18.782097), list-decodes from a supplied received word with sufficient agreement.
- Shokrollahi and Wasserman, [List decoding of algebraic geometric codes](https://doi.org/10.1109/18.748993), interpolates and factors over supplied function-field evaluations.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations, not received source evaluations.

No checked source constructs the received word or proves bounded exact lists and full ECDLP descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, coloured decks, code, evaluation set, received-word rule, multiplicities, list policy, source policy, masks, and verifier.
2. For known-log endpoints, construct the received word without source tuples, list-decode, map every codeword to exact points, and verify relations.
3. Collect at least `B=N^(1/5)` independent rows, solve every factor log, and independently verify them.
4. Apply the identical encoder/decoder to fresh scalar-blind masked targets.
5. Substitute logs, remove masks, retain the full list, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

Let setup and memory be `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, received-word/interpolation work excluding list output `N^q,N^q_m`, verified rank `N^r`, list output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All evaluations, multiplicities, interpolation coefficients, factorization, codeword list entries, point decoding, and verification are charged; `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

List decoding recovers a codeword because correlated received symbols are supplied. An endpoint existence equation does not provide source-indexed evaluations. Deriving them answers the source-completion problem, while generic interpolation or factorization after that step is a solver substitution.

## Proof track

Construct endpoint-only received symbols, prove agreement and bounded exact lists on all strata, then prove relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Show any received symbol evaluates a source-dependent coordinate, exhibit two fibres with the same endpoint word but different tuples, or charge interpolation/list state beyond the gates.

## Positive and negative controls

- Positive: supplied noisy Reed-Solomon and AG-code words within radius must decode to all planted codewords.
- Negative: endpoint-only random words and equal-word/different-source fixtures must not yield preferred elliptic points.
- Baselines: IDEAs 014/063/098/130/136/150/268/281, dense interpolation, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only word construction, exact all-strata decoding, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if a source evaluation is input, list size/state reaches `B^3`, one stratum is missed, or either exponent reaches `0.50`.
- Fast decoding of supplied codewords is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-336/received_word_source_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-336/agreement_and_list_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-336/word_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-336/cost_analysis.md`

## Interpretation boundary

This rejects the declared endpoint-to-list-decoding route, not list decoding generally. A decoded planted word or correct relation is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-336/received_word_source_input_receipt.md` defining every proposed received symbol and proving whether it is computable without a hidden factor or completion query.
