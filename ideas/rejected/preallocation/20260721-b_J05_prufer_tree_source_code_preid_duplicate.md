# Pre-ID duplicate draft — Prüfer tree source code

## Status and claim labels

- Prospect: `20260721-b-J05`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: bijective_tree_encoding / representation-changing / representation pre-ID screen.
- State: merged_rejected_supplied_tree_and_label_sequence.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a bijective code or decoded tree is not an ECDLP result.

## Falsifiable hypothesis

Construct an endpoint-derived labelled tree whose leaves are signed source occurrences, encode it by a Prüfer sequence, and use prefix restrictions on that sequence to decide exact source existence and unrank one factor-base tuple below rho and BSGS.

## Mechanism-new operation

The native operation bijects a supplied labelled tree on `n` vertices with a length-`n-2` label sequence by repeated leaf deletion. It counts only if the tree is constructed from endpoints without source enumeration and every sequence symbol retains exact source ancestry; recoding a supplied source tree is a control.

## Assumptions

1. Public endpoints determine a source-complete labelled tree of sub-rho size.
2. Restrictions become prefix or alphabet restrictions without expanding the tree.
3. Repeated endpoints remain distinct occurrence labels through encode/decode.
4. A decoded branch yields one exact signed factor-base tuple on all strata.
5. The same tree supports independent relation rows and fresh blind targets.

## Semantic fingerprint

`public_endpoint_source_tree | Pruefer_leaf_deletion_sequence | restricted_sequence_nonemptiness | decoded_tree_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — source-complete restricted return frontier.
2. `ideas/rejected/ECDLP-IDEA-203_matrix_tree_arborescence_source_extractor_hypothesis.md` — tree enumeration assumes supplied incidence.
3. `ideas/rejected/ECDLP-IDEA-235_tutte_activity_source_unranking_hypothesis.md` — activity words encode a represented graph structure.
4. `ideas/rejected/preallocation/20260719-d_D05_wilson_cycle_popping_source_tree_preid_duplicate.md` — generated trees retain supplied graph edges.
5. `ideas/rejected/preallocation/20260721-a_I10_prim_minimum_source_skeleton_preid_duplicate.md` — a spanning tree is a lossy skeleton of supplied source incidence.

## Closest primary literature

- Prüfer, [Neuer Beweis eines Satzes über Permutationen](https://books.google.com/books?id=H7suAQAAIAAJ), gives the labelled-tree sequence bijection (Archiv der Mathematik und Physik 27, 1918, 142–144).
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not construct a source-complete labelled tree.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the endpoint tree or restriction-stable elliptic source decoder; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, occurrence labels, signed decks, restrictions, exceptional charts, and verifier.
2. Construct the source tree and Prüfer code from endpoints without a source catalogue; certify encode/decode and restriction semantics.
3. For each known-log target, use at most `5 ceil(log_2 B)+O(1)` exact restrictions, decode one occurrence-labelled source tuple, and verify point equality before retaining a row.
4. Collect at least `max(d_FB+32,1000)` verified rows, retain dependencies and failures, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged state on `Q+[t]P`, decode a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge tree construction, every edge/label, code generation, restricted decoding, negative queries, replay, density, rank, logs, descent, bit time, and peak memory.

## Full rho/BSGS cost model

Charge `T_tree+T_encode` and `M_tree+M_code` in `a,a_m`; charge restricted sequence search plus decoding in `q,q_m`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, including output and ambiguity. Require setup/state at most `B^(9/4+o(1))`, fresh work/workspace at most `B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Prüfer coding is length-preserving up to two symbols and applies only after the labelled tree is supplied. Any tree containing every exact source path must already encode source incidence, while a smaller spanning or canonical tree can discard valid restricted witnesses. Sequence prefixes are properties of arbitrary vertex labels, not endpoint-stable source restrictions.

## Proof track

Construct a compact endpoint tree, prove completeness under every restriction and exact occurrence decoding, and bound code queries plus blind descent.

## Disproof track

Trace every tree edge and label to source traffic; construct restrictions whose sole witness was deleted by a skeleton, and test duplicates, empty fibers, and shuffled codes.

## Positive and negative controls

- Positive: supplied labelled trees with known Prüfer codes and planted restricted subtrees.
- Negative: non-tree compatibility graphs, duplicate endpoint labels, deleted-witness skeletons, empty restrictions, and shuffled decode maps.
- Baselines: explicit tree traversal, Wilson, Prim, matrix-tree, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only tree construction, exact restriction stability, four sizes, zero false answers, full-rank verified relations, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied tree edges, incomplete coverage, label ambiguity, any false answer, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j05_tree_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j05_pruefer_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j05_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-to-tree compiler, not Prüfer coding. Finite results remain toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
