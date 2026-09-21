# Pre-ID duplicate draft — Rete incremental source match

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P06`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_patterns_and_partial_matches`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a production firing or valid relation is not an ECDLP result.

## Falsifiable hypothesis

An endpoint-derived Rete discrimination network shares partial tests across relation targets and
incrementally propagates only exact five-source matches. Production tokens preserve signed
occurrences, enabling complete factor logs and fresh descent with exponents at most `0.45`.

## Mechanism-new operation

Rete compiles supplied patterns into alpha/beta memories and incrementally joins matching
objects. It counts only if object tokens and pattern tests are derived from endpoints without
source enumeration and terminal tokens replay signed points. Caching previously found partial
relations in a Rete network is a control.

## Assumptions

1. Network topology/tests are target-independent and scalar-blind.
2. Alpha/beta memories fit the setup cap and do not contain explicit source tuples.
3. Token insertion, deletion, fanout, duplicate suppression, and all-negative paths are charged.
4. Terminal activation is biconditional with target equality under every restriction.
5. Activation provenance returns signs, multiplicities, and point identities for blind descent.

## Semantic fingerprint

`public_endpoint_object_tests | Rete_shared_alpha_beta_network | exact_terminal_activation | charged_signed_token_provenance | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — shared circuit state retains input/source width.
2. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — shared-state extraction needs exact endpoint source lift.
3. `ideas/rejected/ECDLP-IDEA-377_courcelle_mso_tree_automaton_source_compiler_hypothesis.md` — compiled pattern execution presupposes source input.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — partial-match joins and provenance remain charged.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact target predicate/source return frontier.

## Closest primary literature

- Forgy, [Rete: A Fast Algorithm for the Many Pattern/Many Object Pattern Match Problem](https://doi.org/10.1016/0004-3702(82)90020-0), assumes supplied patterns and objects.
- Graefe, [Volcano](https://doi.org/10.1109/69.273032), is a nearby supplied-operator execution control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not create Rete objects; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) supplies the baseline.

The shared incremental matcher is title-new here, but its information flow merges with compiled
circuits/provenance joins and remains novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, object schema, alpha/beta tests, network, update order, restrictions,
   provenance, exceptional strata, and verifier.
2. Build endpoint-only network/state within `B^(9/4+o(1))`; forbid explicit source tuples,
   pair tables, scalar residues, target caches, and post-hoc activation selectors.
3. Insert each known-log target token, propagate, replay a terminal signed occurrence tuple,
   and verify the elliptic equation.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve all factor logs, and
   charge memories, fanout, failures, duplicates, provenance, and linear algebra.
5. Reuse identical network/state for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge construction, every token edge, output, rank, factor logs, bits, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, setup/state are `N^a,N^a_m`; relation/target reciprocal densities
`N^delta,N^delta_t`; propagation/workspace `N^q,N^q_m`; rank credit `N^r`; token/proof
output `N^o`; fanout/ambiguity `N^u`; factor-log time/memory `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS controls have exponent `0.50`.

## Likely fatal obstruction

Rete alpha/beta memories are materialized partial-source matches. Building or updating them
performs the same source join; without them the network has no informative tokens. Sharing
across targets can amortize only state that is already target-independent and source-bearing.

## Proof track

Give endpoint-only object/tests with exact terminal semantics, bounded memory/fanout, signed
provenance, restriction stability, and complete sub-rho descent.

## Disproof track

Find source enumeration in one memory, a false/missed firing, unbounded token fanout, lost
provenance, target-dependent rebuild, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy objects/patterns with one labelled production firing.
- Negative: duplicate tokens, empty fibres, equal terminal labels/different sources, deletion
  order, repeated signed points, and blind targets.
- Baselines: decomposable circuits, provenance joins, P1553 R4, rho, and BSGS.
- Rete correctness is toy/model-bound evidence only.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only tokens, zero semantic errors at four sizes, bounded fanout,
  full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied partial matches, one semantic error, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p06_network_input_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p06_token_fanout_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p06_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Rete. All evidence remains toy, heuristic, model-bound, and
novelty-unverified; firing correctness is not a cryptanalytic result.

## Exactly one next executable action

1. Trace one alpha token and one beta-memory record to endpoint operations and preserve the first source-tuple dependency or unbounded token fanout.
