# Pre-ID duplicate draft — Hirschberg LCS source reconstruction

## Status and claim labels

- Prospect: 20260720-b-F02; no canonical ECDLP idea ID was allocated
- Class / risk / lane: divide_conquer_sequence_alignment / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_source_strings_and_time_not_removed
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; linear-space alignment of supplied strings is not scalar recovery.

## Falsifiable hypothesis

Serialize two complementary elliptic source decks as endpoint words whose longest common subsequence encodes compatible partial sums. Hirschberg's forward/backward score split would reconstruct one exact signed source path in linear memory, enabling relations and blind descent below rho and BSGS.

## Mechanism-new operation

Hirschberg recomputes dynamic-programming rows from both ends, chooses a midpoint split, and recursively reconstructs an LCS in linear space. It counts only if the two words are endpoint-derived without a source catalogue, equality of symbols is the exact elliptic compatibility predicate, and the recovered subsequence inverts to factor occurrences. Applying it to enumerated source strings is a control.

## Assumptions

1. Target-independent words cover signed, repeated, tangent, vertical, infinity, and nonreduced strata exactly.
2. Word construction, equality tests, forward/backward passes, recursion, restrictions, replay, rank, logs, descent, time, and memory are charged.
3. An LCS has a biconditional relation to exact five-source existence rather than approximate shared features.
4. Recursive tie choices preserve occurrence labels and arbitrary restrictions.
5. The same frozen words serve fresh scalar-blind targets without target-specific serialization.

## Semantic fingerprint

public_endpoint_words | Hirschberg_forward_backward_LCS_split | exact_restricted_common_subsequence | alignment_path_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted existence and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source resolver.
3. ideas/rejected/ECDLP-IDEA-084_confluent_factor_word_rewriting_hypothesis.md — supplied word grammars do not create factor labels.
4. ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md — compact automata lose continuation-faithful ancestry.
5. ideas/rejected/preallocation/20260720-a_E08_viterbi_source_trellis_preid_duplicate.md — dynamic-programming survivors require a supplied source trellis.

## Closest primary literature

- Hirschberg, [A linear space algorithm for computing maximal common subsequences](https://doi.org/10.1145/360825.360861), saves DP memory for two supplied strings but retains quadratic comparison work.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations, not source words or an equality alphabet.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source constructs the endpoint words, exact symbol predicate, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, serialization, alphabet, equality test, split/tie rule, restrictions, and verifier.
2. Build target-independent words/state within B^(9/4+o(1)) without enumerating partial-source paths.
3. For known-log R=[kappa]P, reconstruct an exact restricted alignment and labelled A_i,epsilon_i using at most 5 ceil(log_2 B)+O(1) queries plus failed siblings; verify sum_i epsilon_i A_i=[kappa]P before recording sum_i epsilon_i y(A_i)=kappa (mod N).
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB for the actual factor-log unknowns, preserve failures/dependencies, and solve only after the rank gate.
5. Reuse unchanged words for R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge serialization, every equality/DP cell, recomputation, restrictions, ties, replay, rank, logs, descent, scalar checks, bit operations, and peak memory.

## Full rho/BSGS cost model

Let word lengths be L_1,L_2, C_eq exact symbol-comparison work, Q_R restriction queries, and C_inv inversion. Hirschberg uses Theta(L_1 L_2 C_eq) time and O(min(L_1,L_2)) score state while reconstruction recomputes rows. Set a=log_N(T_words), a_m=log_N(M_words), q=log_N(Q_R(L_1 L_2 C_eq+C_inv)+T_replay), and q_m=log_N(M_words+min(L_1,L_2)+M_inv). With beta=1/5 and delta,delta_t,r,o,u,ell,ell_m as verified-density, rank, output, ambiguity/rebuild, and log costs:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45; rho and BSGS are 0.50. Four increasing B values need one-sided 95% upper bounds.

## Likely fatal obstruction

Hirschberg removes DP storage, not the quadratic supplied-string comparison traffic. Faithful symbols or equality tests encode source incidence; coarse endpoint symbols admit alignments assembled from incompatible occurrences. Arbitrary restrictions change the strings and LCS ties lose ancestry. This merges with IDEAS 084/120 and pre-ID E08.

## Proof track

Construct endpoint-only words and an exact LCS/source theorem stable under restrictions, then close recomputation, replay, rank, and descent costs.

## Disproof track

Give equal public words with different valid sources, or show one equality test invokes Query2P1/source labels or total DP work exceeds the cap.

## Positive and negative controls

- Positive: supplied toy strings with a unique planted labelled LCS.
- Negative: equal symbols with incompatible ancestry, ambiguous LCSs, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEAS 084/120, pre-ID E08/A12, explicit sequence DP, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only words, exact restricted LCS/source inversion, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on supplied source strings, one false alignment, restriction rebuild beyond cap, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f02_word_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f02_alignment_ancestry_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f02_cost_analysis.md

## Interpretation boundary

This rejects the elliptic serialization, not Hirschberg's LCS algorithm. Linear memory or one valid alignment is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f02_word_provenance.md; do not create it under this retired pre-ID screen.
