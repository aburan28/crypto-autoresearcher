# Pre-ID duplicate draft — Ukkonen suffix-tree source index

## Status and claim labels

- Prospect: `20260721-d-L07`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: representation / representation-changing / representation-changing pre-ID screen.
- State: merged_rejected_supplied_source_serialization_and_linear_size_index.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a suffix match or verified relation is not an ECDLP result.

## Falsifiable hypothesis

Serialize endpoint-derived signed source transitions into a public text, build its suffix tree online with Ukkonen suffix links, answer every restricted relation query as an exact pattern interval, replay occurrences, and complete factor logs plus blind target descent below rho and BSGS.

## Mechanism-new operation

The native operation incrementally extends an implicit suffix tree using active points, suffix links, and edge splitting while processing a supplied text once. It counts only if the text is generated from endpoint data below source traffic and pattern occurrences map exactly to signed relation tuples; indexing a supplied source serialization is a control.

## Assumptions

1. There is a canonical scalar-blind serialization of all relation-relevant source state smaller than the source deck.
2. Relation restrictions translate to contiguous or boundedly many exact suffix-tree loci.
3. Suffix links and edge labels preserve occurrence multiplicity, sign, and exceptional strata.
4. A reported text occurrence replays a complete signed tuple with charged ambiguity.
5. One target-independent text/tree serves relation collection and fresh masked targets.

## Semantic fingerprint

`public_endpoint_source_text | Ukkonen_online_suffix_tree_with_suffix_links | exact_restricted_pattern_locus | suffix_occurrence_to_signed_tuple | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restriction and signed occurrence-return frontier.
2. `ideas/rejected/preallocation/20260719-a_A06_fm_index_backward_source_unranking_preid_duplicate.md` — compressed backward search begins after a source text/BWT exists.
3. `ideas/rejected/preallocation/20260719-d_D03_suffix_array_source_interval_index_preid_duplicate.md` — suffix intervals index a supplied serialization and retain occurrence positions.
4. `ideas/rejected/preallocation/20260720-d_H01_patricia_radix_source_trie_preid_duplicate.md` — radix compaction preserves represented keys but does not create them from endpoints.
5. `ideas/rejected/preallocation/20260721-b_J07_lempel_ziv_source_phrase_dictionary_preid_duplicate.md` — adaptive parsing cannot avoid generating the source serialization first.

## Closest primary literature

- Ukkonen, [On-line construction of suffix trees](https://doi.org/10.1007/BF01206331), builds a linear-size suffix tree from a supplied string.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than a compact exact source text.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the serialization, exact restriction-to-pattern map, or occurrence-to-factor tuple lift; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional strata, alphabet/serialization, and independent point verifier.
2. Construct and certify the endpoint-derived text, suffix tree, edge labels, suffix links, and occurrence satellites without enumerating source tuples or using scalar labels.
3. For each known-log target, translate at most `5 ceil(log_2 B)+O(1)` restrictions to tree loci, replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, keep failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge serialization, tree construction, edge comparisons, restriction patterns, occurrence reporting, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge text/tree setup in `a,a_m`, restricted pattern search/replay in `q,q_m`, and reported/ambiguous occurrences in `o,u`. For `B=N^beta`, `beta=1/5`, density `delta,delta_t`, rank credit `r`, and log costs `ell,ell_m`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS are `0.50`.

## Likely fatal obstruction

Ukkonen is linear in the supplied text length, not in a smaller endpoint description. A text containing every source occurrence has source-scale length and occurrence satellites. Any shorter aggregate serialization can map distinct signed tuples to the same substrings, while arbitrary coordinate restrictions are not generally contiguous pattern queries.

## Proof track

Define an endpoint-only sub-source serialization and prove that all signed relation restrictions are exact bounded-locus pattern queries with complete occurrence replay and below-rho total costs.

## Disproof track

Trace each text symbol and occurrence pointer to source work; construct colliding serializations or nonlocal restrictions; falsify on source-sized text, false matches, lost multiplicity, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied texts with planted labelled relation patterns and contiguous restrictions.
- Negative: permuted source order, repeated substrings from distinct tuples, noncontiguous restrictions, empty patterns, and fresh targets.
- Baselines: suffix array, FM-index, PATRICIA, Lempel-Ziv, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only serialization, four increasing sizes, zero false decisions, exact multiplicity replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied/source-scale text, nonlocal restrictions, a false answer, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l07_text_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l07_ukkonen_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l07_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only suffix-tree transplant, not Ukkonen indexing for supplied text. Every finite match remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute the contract.
