# Pre-ID duplicate draft — Skip-list source order index

## Status and claim labels

- Prospect: 20260720-a-E07; no canonical ECDLP idea ID was allocated
- Class / risk / lane: randomized_order_index / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_ordered_sources_and_restriction_rebuild
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; logarithmic expected dictionary search is not scalar recovery.

## Falsifiable hypothesis

Order public partial-sum keys and assign target-independent random skip-list heights. A target/restriction query would traverse towers to the predecessor interval containing an exact compatible endpoint and replay one signed source occurrence, enabling relations, factor logs, and fresh blind descent below rho and BSGS.

## Mechanism-new operation

A skip list randomly promotes nodes into linked levels so predecessor/range queries take expected logarithmic time on a supplied ordered dictionary. It counts only if nodes and keys are endpoint-derived without source enumeration, a predecessor interval is exact source existence, and source restrictions are supported without relinking explicit occurrences. Replacing a balanced tree over a supplied source catalogue is a control.

## Assumptions

1. A target-independent total order makes all accepting signed sources contiguous and exact on every chart.
2. Node/key construction, random heights, forward pointers, range traversal, restrictions, misses, replay, rank, logs, descent, randomness, bit time, and memory are charged.
3. Equal endpoint keys retain distinct point-faithful ancestry without source-sized satellites.
4. Arbitrary dyadic source restrictions can be applied without rebuilding towers or scanning base-level nodes.
5. One frozen list serves known-log and fresh scalar-blind targets without target-specific ordering.

## Semantic fingerprint

public_ordered_endpoint_nodes | skiplist_random_towers | exact_restricted_predecessor_interval | base_node_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted target-label existence.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source-resolving circuit.
3. inputs/ledger_inventory_20260719.json — ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY charges labelled dictionary records.
4. ideas/rejected/ECDLP-IDEA-350_translation_catalog_fractional_cascading_source_router_hypothesis.md — fast search begins after a source catalogue exists.
5. ideas/rejected/ECDLP-IDEA-371_jez_recompression_source_grammar_hypothesis.md — compressed ordering/grammar state loses occurrence provenance or retains the source language.

## Closest primary literature

- Pugh, [Skip lists: a probabilistic alternative to balanced trees](https://doi.org/10.1145/78973.78977), indexes supplied ordered keys with randomized levels; it does not construct relation keys.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies equations but no ordered source dictionary.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies exact endpoint-only order construction, occurrence replay, or complete descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, key order, height seeds, list construction, restrictions, and verifier.
2. Build target-independent towers within B^(9/4+o(1)) without source-product nodes.
3. For known-log R=[kappa]P, query exact restricted predecessor intervals, replay labelled points A_i with signs epsilon_i by at most 5 ceil(log_2 B)+O(1) charged restriction queries plus misses, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; preserve dependencies/failures, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse unchanged list for fresh R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge all node/key creation, pointers, traversals, equality buckets, restrictions/relinks, replay, rank, logs, descent, bit operations, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge ordered nodes, keys, random tower heights, forward pointers, and equality/source satellites; q,q_m charge target-key compilation, all pointer traversals, misses, restrictions, bisection, and replay. Let delta,delta_t be reciprocal verified relation/target densities, r independent-rank credit, o output, u height tails/equal-key ambiguity/relinks, and ell,ell_m factor-log time/state.

Let n be supplied base nodes, H total tower nodes/pointers, Q_R restriction/predecessor queries, C_search the realized traversal length, and C_relink the work needed to enforce a restriction. Native build/state is Theta(n+H), expected search is O(log n), and a high-probability rather than expectation-only tail must be frozen. Set a=log_N(T_nodes+n+H), a_m=log_N(n+H+M_satellite), q=log_N(Q_R(C_search+C_relink)+T_replay), and q_m=log_N(M_query+M_persistent). A target-key order and a dyadic source-deck restriction are distinct coordinates; if exact restrictions require Theta(n) relinking/scanning or extra persistent labelled indexes, that cost/state is explicit.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require state <=B^(9/4+o(1)), fresh traversal/restriction/replay <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. The base-level dictionary cardinality, collision buckets, high-probability rather than expected costs, and all restriction relinks are charged.
Each fresh masked-target predecessor/restriction/replay path must independently be <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion requires four increasing B values with a simultaneous one-sided 95% upper bound on traversal/relink/build/state/complete exponents and an explicit high-probability tower-height tail.

## Likely fatal obstruction

Skip lists improve navigation only after ordered nodes are supplied. Those nodes are the missing source catalogue; endpoint aggregation creates equal-key buckets without occurrence identity. Arbitrary source restrictions delete base nodes and invalidate forward pointers, so exact support requires per-restriction relinking or a labelled persistent dictionary. This merges with IDEAS 120/350/371/374.

## Proof track

Construct ordered nodes endpoint-only, prove exact interval/source biconditional stable under restrictions and high-probability sub-gate traversal, then close replay and descent.

## Disproof track

Expose one source-bearing node or equality satellite, give equal ordered endpoint keys with different valid sources, or show a restriction forces base-level scan/rebuild.

## Positive and negative controls

- Positive: a supplied ordered dictionary with unique planted labelled key and redundant towers.
- Negative: equal endpoint keys with distinct ancestry, adversarial tower heights, deletion-heavy restrictions, absent/exceptional targets, and blind targets.
- Baselines: IDEAS 120/350/371/374, binary search over explicit tuples, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only nodes, exact restriction-stable intervals and source inverse, high-probability full costs, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source node, one equal-key/source collision, one source-scale relink/scan, target-trained order, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e07_node_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e07_equal_key_restriction_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e07_cost_analysis.md

## Interpretation boundary

This rejects the transplant, not skip lists. Expected dictionary performance or one found explicit tuple is not a breakthrough.

## Exactly one next executable action

1. Write ideas/rejected/preallocation/artifacts/20260720-a/e07_node_provenance.md and classify every base node, equality bucket, and forward pointer by its source dependence.
