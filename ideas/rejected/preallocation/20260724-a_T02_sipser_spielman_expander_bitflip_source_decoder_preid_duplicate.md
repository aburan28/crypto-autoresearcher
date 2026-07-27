# Pre-ID duplicate draft — Sipser–Spielman expander bit-flip source decoder

## Status and claim labels

- Provisional ID: `PREID-20260724-a-T02`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_expander_tanner_graph_and_local_syndrome`.
- Class/risk/lane: graph_algorithm / conservative / conservative pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; expansion, local correction, or a verified relation is not an ECDLP break.

## Falsifiable hypothesis

Public endpoint data induces a bounded-degree expanding Tanner graph whose violated local checks
identify erroneous source-occurrence bits. Sipser–Spielman bit flipping would recover exact signed
relations, full-rank factor logs, and blind descents below the rho/BSGS boundary.

## Mechanism-new operation

The native operation repeatedly flips variables that violate enough checks in a supplied expander
code. It counts only if endpoint data constructs the bounded-degree source graph and exact local
syndromes without relation enumeration, and if decoded bits lift biconditionally to occurrence
labels. Bit flipping on an explicit addition/incidence graph is a control already inside the
supplied-local-view boundary of IDEA-132.

## Assumptions

1. A scalar-blind endpoint compiler emits a bounded-degree Tanner graph without source-sized state.
2. Source-valid words are separated by quantified expansion and a restriction-stable decoding radius.
3. Local checks are exact on repetitions, signs, infinity, tangencies, and empty fibres.
4. Flips retain occurrence provenance and return complete signed tuples rather than aggregate bits.
5. Graph construction, decoding, misses, rank, logs, descent, and memory satisfy both caps.

## Semantic fingerprint

`public_endpoint_Tanner_graph | source_preserving_expansion | violated_check_bit_flips | exact_occurrence_word_lift | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-132_high_dimensional_expander_sheaf_decoder_hypothesis.md` — the supplied local-view/expansion decoder owner.
2. `ideas/rejected/ECDLP-IDEA-168_disjunct_pool_incidence_source_locator_hypothesis.md` — incidence tests need a compact source-preserving constructor.
3. `ideas/rejected/preallocation/20260722-a_N09_sum_product_source_messages_preid_duplicate.md` — sparse factor-graph messages start from supplied checks.
4. `ideas/rejected/preallocation/20260721-d_L02_kahn_topological_source_peeling_preid_duplicate.md` — local peeling assumes source arcs and indegrees.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed replay remain required.

## Closest primary literature

- Sipser and Spielman, [Expander Codes](https://doi.org/10.1109/18.556667), gives efficient decoding for codes built from supplied expanding graphs and local constraints.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but no compact Tanner graph with source-labelled local views.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison.

No checked source constructs the endpoint graph, local syndromes, exact source lift, or full
descent. The ECDLP claim remains novelty-unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, decks, graph constructor, checks, flip threshold/order, restrictions, masks, strata, and verifier.
- Build target-independent graph/state within `B^(9/4+o(1))`, excluding enumerated relation edges and factor logs.
- For known-log endpoints, charge graph access, check evaluation, every flip/round/restart, occurrence replay, and independent row verification.
- Collect at least `max(d_FB+32,1000)` verified rows, retain dependencies/failures, require rank `d_FB`, and solve all factor logs.
- Reuse unchanged state for 100 fresh scalar-blind masks, decode/replay tuples, subtract masks, and verify scalars.
- Charge expansion certification, state, failure density, output, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, graph/check/flip/replay cost `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, and factor-log cost
`N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Expansion decoding saves work only after the code graph and local checks are supplied. Exact checks
over hidden relation sources are the missing incidence representation; compact checks lose
occurrence identity, while explicit checks restore source-sized graph state. Local satisfaction also
need not imply a globally extendible elliptic tuple.

## Proof track

Prove a compact endpoint graph, source-preserving expansion, exact local-to-global decoding on all
strata, full rank/logs, blind descent, and both complete exponents below `0.45`.

## Disproof track

Trace one edge/check to source enumeration, exhibit locally consistent nonextendible words or equal
syndromes with different sources, or charge graph/state/rounds to exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied expander codes with planted correctable bit errors.
- Negative: nonexpanding graphs, locally consistent dead ends, equal-syndrome fibres, repeated occurrences, empty restrictions, and fresh targets.
- Baselines: IDEA-132, sum-product, Kahn peeling, P1553 R4, rho, and BSGS.
- A certified expander or corrected supplied word remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with a public graph/check theorem, zero errors over four sizes/all strata, miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on a supplied source graph, one local/global mismatch, lost label, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-a/t02_graph_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260724-a/t02_local_global_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260724-a/t02_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects only the declared ECDLP graph transplant, not expander codes. Expansion, successful
bit flipping, or a valid relation remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Build the smallest endpoint-equivalent pair whose supplied local check syndromes agree but whose exact signed relation fibres differ.
