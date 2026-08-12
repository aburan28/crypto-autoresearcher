# Pre-ID duplicate draft — Needleman-Wunsch source alignment

## Status and claim labels

- Prospect: `20260721-d-L09`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: dynamic_programming / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_sequences_and_dense_alignment_grid.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an optimal alignment, valid path, or relation is not an ECDLP result.

## Falsifiable hypothesis

Encode two endpoint-derived partial-source streams so valid decompositions are their optimal global alignments, use Needleman-Wunsch dynamic programming under restrictions to recover exact signed occurrences, and complete factor logs plus blind target descent below rho and BSGS.

## Mechanism-new operation

The native operation fills a two-dimensional score grid from diagonal, insertion, and deletion predecessors and backtraces an optimal global alignment. It counts only if both sequences and scores are endpoint-derived, optimality is biconditional with relation existence, and the grid/backtrace fit the cost caps; aligning supplied source sequences is a control.

## Assumptions

1. Public endpoint data generates two compact streams without enumerating source assignments.
2. A target-independent exact scoring rule makes valid relations precisely the optimal alignments with a public gap.
3. Restrictions update the alignment problem without dense recomputation or source advice.
4. Every accepted backtrace returns occurrence-distinct signed factors on all exceptional strata.
5. The same state serves known-log relations and fresh scalar-blind target descent.

## Semantic fingerprint

`public_endpoint_partial_source_sequences | Needleman_Wunsch_global_alignment_DP | exact_restricted_optimal_alignment | backtrace_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restriction, replay, rank, and descent frontier.
2. `ideas/rejected/preallocation/20260720-b_F02_hirschberg_lcs_source_reconstruction_preid_duplicate.md` — low-space alignment reconstruction retains supplied strings and quadratic time.
3. `ideas/rejected/preallocation/20260721-c_K07_bcjr_endpoint_trellis_source_decoder_preid_duplicate.md` — dynamic-programming marginals start from a supplied trellis and can merge sources.
4. `ideas/rejected/preallocation/20260720-a_E08_viterbi_source_trellis_preid_duplicate.md` — an optimal trellis path needs the represented state graph and scoring model.
5. `ideas/rejected/ECDLP-IDEA-371_jez_recompression_source_grammar_hypothesis.md` — compressed word equations still need a source-faithful endpoint grammar.

## Closest primary literature

- Needleman and Wunsch, [A general method applicable to the search for similarities in the amino acid sequence of two proteins](https://doi.org/10.1016/0022-2836(70)90057-4), computes an optimal alignment for two supplied sequences.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than compact aligned source streams.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the sequences/scoring gap or an exact alignment-to-factor lift from ECDLP endpoints; the transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional strata, alphabet/scores, and independent point verifier.
2. Construct and certify the endpoint-derived sequences, score rule, sparse DP state if claimed, and occurrence backpointers without source enumeration or scalar labels.
3. For each known-log target, make at most `5 ceil(log_2 B)+O(1)` restrictions, backtrace `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge sequence construction, grid cells, score comparisons, restrictions, backtrace, density, rank, logs, blind descent, bit time, and memory.

## Full rho/BSGS cost model

Charge sequence/DP setup in `a,a_m`, restricted alignment/replay in `q,q_m`, and output/ambiguity in `o,u`. With `B=N^beta`, `beta=1/5`, `delta,delta_t,r,ell,ell_m` as usual, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50`.

## Likely fatal obstruction

Needleman-Wunsch requires both source sequences and a dense product grid. There is no known scalar-blind local score whose global optimum is exactly an elliptic five-source relation; many partial alignments share scores but have different endpoint sums. A score that encodes those sums or a backtrace table restores the source state, and low-memory variants do not remove quadratic work.

## Proof track

Construct the endpoint-only sequences and exact public score-gap theorem, then give restriction-stable sparse DP and all-strata backtrace with complete below-rho exponents.

## Disproof track

Search for optimal nonrelation alignments and suboptimal valid relations, and audit sequence/grid origin; falsify on a semantic mismatch, supplied sequences, dense traffic, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied sequence pairs with planted uniquely optimal labelled alignments.
- Negative: score ties, valid nonoptimal paths, optimal nonrelations, empty restrictions, duplicate occurrences, and fresh targets.
- Baselines: Needleman-Wunsch, Hirschberg, Viterbi, BCJR, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only sequence construction, four increasing sizes, zero score/relation errors, exact replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on one semantic mismatch, dense source grid beyond cap, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l09_score_biconditional_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l09_alignment_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l09_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only alignment transplant, not Needleman-Wunsch on supplied sequences. Every finite alignment remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
