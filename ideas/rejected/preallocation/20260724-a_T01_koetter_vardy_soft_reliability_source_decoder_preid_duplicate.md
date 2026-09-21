# Pre-ID duplicate draft — Koetter–Vardy soft-reliability source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T01`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_reliability_matrix_and_list_decoder_backend`.
- Class/risk/lane: algorithm / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a correct multiplicity assignment, decoded codeword, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Public endpoint data yields a source-free reliability matrix over signed factor-base positions.
Koetter–Vardy multiplicity assignment and interpolation would then recover every exact relation
source with bounded list size, enough full-rank rows, and 100 fresh blind descents while complete
time and memory exponents remain at most `0.45`.

## Mechanism-new operation

The native operation converts supplied symbol reliabilities into interpolation multiplicities,
then applies algebraic soft-decision list decoding. It counts as an ECDLP operation only if the
endpoint compiles calibrated source-symbol reliabilities without enumerating sources, consulting
factor logs, or evaluating the missing restricted-source predicate. Supplying a reliability matrix
to IDEA-336's list decoder is a decoder-front-end substitution, not a new source-return mechanism.

## Assumptions

1. Endpoint-only observables determine calibrated probabilities for occurrence-labelled symbols.
2. Multiplicity assignment preserves signs, repetitions, ordering, and exceptional elliptic strata.
3. The interpolation list contains all and only exact source tuples with charged bounded output.
4. Reliability construction, interpolation, factorization, replay, rank, factor logs, and descent satisfy both caps.
5. Frozen reliabilities remain scalar-blind and reusable on fresh masked targets.

## Semantic fingerprint

`public_endpoint_symbol_reliabilities | Koetter_Vardy_multiplicity_assignment | soft_list_interpolation | exact_signed_occurrence_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-336_guruswami_sudan_source_list_decoder_hypothesis.md` — the supplied received-word/list-decoder owner.
2. `ideas/rejected/ECDLP-IDEA-268_multiplicity_code_hasse_jet_local_lift_hypothesis.md` — multiplicity data still needs a public source-sensitive oracle.
3. `ideas/rejected/ECDLP-IDEA-014_elliptic_code_error_locator_descent_hypothesis.md` — endpoint-to-code-syndrome construction is already the missing operation.
4. `ideas/rejected/preallocation/20260723-b_S12_rubinstein_cross_entropy_source_sampler_preid_duplicate.md` — post-hoc scores or probabilities cannot create exact source semantics.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable existence and signed replay remain the live frontier.

## Closest primary literature

- Koetter and Vardy, [Algebraic Soft-Decision Decoding of Reed–Solomon Codes](https://doi.org/10.1109/TIT.2003.819332), assigns interpolation multiplicities from a supplied reliability matrix.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not symbol reliabilities or an exact source lift.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic-group baseline.

No checked source supplies the ECDLP reliability compiler, all-strata occurrence inverse, or
complete descent. The transplant remains novelty-unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, signed decks, reliability rule, multiplicity budget, interpolation order, list policy, restrictions, masks, and verifier.
- Compile target-independent state within `B^(9/4+o(1))`, forbidding source tables, target fitting, dense resultants, and factor logs.
- On known-log endpoints, charge reliability computation, multiplicities, interpolation, factorization, every list branch, signed replay, and independent relation verification.
- Retain failures and dependencies; collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor-base logarithm.
- Reuse byte-identical eligible state on 100 fresh `Q+[t]P` targets, replay tuples, subtract masks, and verify every scalar.
- Charge setup, state, densities, ambiguity, rank, factor solve, bit work, and peak memory end to end.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal relation and target
densities `N^delta,N^delta_t`; reliability/decoding/replay work and workspace
`N^q,N^q_m`; rank credit `N^r`; output `N^o`; ambiguity/failure `N^u`; and
factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, with `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Pollard rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Soft-decision decoding improves a decoder after a reliability channel is supplied. For hidden
elliptic sources, an accurate reliability entry already answers which occurrence can extend to a
relation. Proxy reliabilities can agree while exact source fibres differ; exact calibration restores
Query2P1, source enumeration, or target-trained advice.

## Proof track

Prove an endpoint-only calibrated reliability compiler, restriction-uniform exact list theorem,
all-strata occurrence lift, full rank/log recovery, blind descent, and complete sub-rho costs.

## Disproof track

Hold the public reliability matrix fixed while changing the exact source fibre, expose any
source-labelled training/input, or derive unbounded list/state or a complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied Reed–Solomon words with calibrated reliabilities and planted errors.
- Negative: equal-reliability different-source fibres, shuffled labels, empty fibres, repeated points, exceptional charts, and fresh blind targets.
- Baselines: Guruswami–Sudan, multiplicity-code decoding, IDEA-014, P1553 R4, rho, and BSGS.
- Better decoding score or one valid tuple remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors across four sizes/all strata, a proved public compiler and exact lift, miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing reliability entry, missed/false source, post-hoc calibration, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t01_reliability_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t01_equal_matrix_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t01_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not Koetter–Vardy decoding. Correct multiplicity
assignment, interpolation, or a valid row remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Construct a smallest pair of signed-source fibres with identical frozen endpoint-derived reliability matrices and test whether their exact extendible occurrences differ.
