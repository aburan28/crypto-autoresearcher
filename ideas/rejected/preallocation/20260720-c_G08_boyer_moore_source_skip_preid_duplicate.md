# Pre-ID duplicate draft — Boyer–Moore source skip

## Status and claim labels

- Prospect: 20260720-c-G08; no canonical ECDLP idea ID was allocated
- Class / risk / lane: reverse_pattern_skip_search / conservative / general pre-ID screen
- State: merged_rejected_supplied_source_text_and_pattern_encoding
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; skip-rate extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; skipping characters in a supplied text is not scalar recovery.

## Falsifiable hypothesis

Encode ordered partial-source states as a target-independent text and each restricted relation condition as a pattern. Boyer–Moore bad-character and good-suffix shifts would skip impossible alignments, replay exact signed occurrences, and support full factor-base relations and blind descent below rho and BSGS.

## Mechanism-new operation

Boyer–Moore compares a supplied pattern from right to left and shifts it using mismatch tables derived from the pattern. It counts only if the text/pattern encoding is endpoint-derived without enumerating source words, each match is exactly a source, and restrictions preserve contiguous alignments. Searching an explicit source text is a control.

## Assumptions

1. Public endpoint data compile into a target-independent text over a bounded alphabet.
2. Text/pattern construction, preprocessing, comparisons, shifts, verification, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. A match is biconditional with an exact signed source and identifies occurrences.
4. Canonical source restrictions map to substrings/pattern edits without source-sized rebuilds.
5. Fresh blind targets do not choose a scalar-leaking pattern or favourable text order.

## Semantic fingerprint

public_partial_source_text | Boyer_Moore_bad_character_good_suffix_skip | exact_restricted_pattern_match | text_alignment_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted-existence and replay frontier.
2. ideas/rejected/preallocation/20260720-b_F09_kmp_failure_link_source_matcher_preid_duplicate.md — pattern matching assumes a supplied source text.
3. ideas/rejected/preallocation/20260719-a_A12_aho_corasick_source_failure_automaton_preid_duplicate.md — multi-pattern failure links preserve supplied occurrences only.
4. ideas/rejected/preallocation/20260719-a_A06_fm_index_backward_source_unranking_preid_duplicate.md — compressed text indexing begins after text construction.
5. ideas/rejected/preallocation/20260719-d_D03_suffix_array_source_interval_index_preid_duplicate.md — suffix intervals require an explicit ordered source string.

## Closest primary literature

- Boyer and Moore, [A fast string searching algorithm](https://doi.org/10.1145/359842.359859), derives skips for a supplied pattern and text; it does not compile elliptic sources.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but no lossless source text/pattern representation.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the encoding, exact match/source theorem, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, text/pattern encoding, alphabet, shift tables, restrictions, occurrence map, and verifier.
2. Construct the target-independent text/index within B^(9/4+o(1)) without enumerating source words.
3. For known-log R, search restricted patterns and replay A_i,epsilon_i in bounded bisection; verify point equality before recording a row.
4. Collect at least max(d_FB+32,1,000) verified rows, retain comparisons/misses/dependencies, require rank d_FB, and solve factor logs.
5. Reuse unchanged text for Q+[t]P, match and replay a tuple, compute x, and verify [x]P=Q.
6. Charge text/pattern compilation, all comparisons/shifts and verification, restrictions, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Let n be text length, m pattern length, C_sym symbol construction/comparison work, C_BM(n,m) the actual complete comparison count, occ matches verified, Q_R restrictions, and C_inv replay. Do not assume sublinear average search; charge worst/observed C_BM and preprocessing O(m+|Sigma|). Set a=log_N(T_text), a_m=log_N(M_text), q=log_N(Q_R(C_BM C_sym+occ C_exact+C_inv)+T_replay), and q_m=log_N(M_text+m+|Sigma|+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds on comparisons and matches. Rho/BSGS are 0.50.

## Likely fatal obstruction

The text encodes the source catalogue or loses tuple boundaries and ancestry. Pattern skips exploit literal mismatch structure after the representation is supplied; they do not create exact endpoint/source information. Restrictions need noncontiguous coordinate subsets, not one substring. This is a solver substitution for F09/A12/A06/D03.

## Proof track

Prove a compact endpoint-only text, exact all-strata pattern/source biconditional, restriction-preserving layout, sub-gate comparison count, rank, and blind descent.

## Disproof track

Find two different source corpora with the same public text symbols but different matches, or one restriction requiring a source-sized rewritten text.

## Positive and negative controls

- Positive: supplied text with planted labelled patterns and favourable skips.
- Negative: periodic/adversarial texts, shuffled ancestry, absent patterns, noncontiguous restrictions, exceptional and blind targets.
- Baselines: naive/KMP/Aho/FM/suffix search, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only encoding, exact occurrence replay, bounded worst fresh-target comparisons, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing symbol, false match, restriction rewrite beyond cap, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g08_encoding_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-c/g08_skip_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g08_cost_analysis.md

## Interpretation boundary

This rejects the elliptic string encoding, not Boyer–Moore. A large skip or valid match is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g08_encoding_provenance.md; do not create it under this retired pre-ID screen.
