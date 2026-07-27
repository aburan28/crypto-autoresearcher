# Pre-ID duplicate draft — Leapfrog Triejoin source intersection

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P04`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_tries_and_join_relations`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; worst-case-optimal join execution or a relation is not an ECDLP result.

## Falsifiable hypothesis

Endpoint-derived tries for projected relation coordinates support Leapfrog Triejoin seeks that
intersect five source roles without materializing the Cartesian product. Exact leaves replay
signed occurrences and complete relation collection plus blind descent below exponent `0.45`.

## Mechanism-new operation

Leapfrog Triejoin cyclically seeks sorted trie iterators to their common value and recursively
binds query variables. It counts only if the tries are compact endpoint-derived objects rather
than source tables and if leaf bindings return exact signed point occurrences. Re-encoding
materialized pair/source relations as tries is a control.

## Assumptions

1. Trie nodes and projections are public, scalar-blind, and target-independent.
2. Total trie size fits `B^(9/4+o(1))` without hidden source incidence.
3. Iterator seeks, projection cardinalities, output, and restriction rebuilds are charged.
4. Common bindings are biconditional with elliptic target equality on every stratum.
5. Leaf paths replay signs, multiplicities, and point labels for fresh descent.

## Semantic fingerprint

`public_endpoint_projection_tries | leapfrog_multiway_seek_intersection | exact_common_binding | charged_leaf_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-325_insideout_faq_source_join_hypothesis.md` — existing multiway-join backend owner.
2. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — relation width and provenance construction remain charged.
3. `ideas/rejected/preallocation/20260720-d_H01_patricia_radix_source_trie_preid_duplicate.md` — a trie over supplied source keys is not a new operation.
4. `ideas/rejected/ECDLP-IDEA-377_courcelle_mso_tree_automaton_source_compiler_hypothesis.md` — compact tree execution still needs a source compiler.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — endpoint-labelled exact existence/replay frontier.

## Closest primary literature

- Veldhuizen, [Leapfrog Triejoin](https://arxiv.org/abs/1210.0481), proves worst-case optimality up to logarithmic factors for supplied trie-indexed relations.
- Ngo et al., [Worst-Case Optimal Join Algorithms](https://doi.org/10.1145/2213556.2213565), is the nearby general multiway-join result.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not construct the input tries; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) is the control.

The execution primitive is title-new here, but the information flow is the occupied
InsideOut/provenance/trie lane. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, query hypergraph, variable order, trie projections, restrictions,
   signed leaf schema, and verifier.
2. Build endpoint-only tries within `B^(9/4+o(1))`; forbid explicit source tuples, pair sums,
   target-labelled caches, scalar residues, and dense resultants.
3. For each known-log target, run restricted Leapfrog seeks, replay one signed leaf tuple, and
   verify the elliptic sum.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve every factor log, and
   charge trie construction, seeks, intermediate bindings, output, failures, and linear algebra.
5. Reuse identical tries for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge projection widths, index state, bit complexity, rank, logs, descent, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state are `N^a,N^a_m`; relation/target reciprocal densities are
`N^delta,N^delta_t`; seek/query/workspace are `N^q,N^q_m`; rank credit is `N^r`; output
is `N^o`; ambiguity is `N^u`; factor-log time/memory are `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and all trie
construction/output charged. Rho and BSGS controls have exponent `0.50`.

## Likely fatal obstruction

Trie projections are source-bearing relations. Constructing them either enumerates pair/higher
partial sums or materializes the same quotient-algebra payload. Worst-case optimality is relative
to input plus output size and does not remove this construction floor.

## Proof track

Construct compact endpoint-only tries, prove exact all-strata binding semantics and signed
inverse, and derive full setup/query/memory exponents below both controls.

## Disproof track

Trace one trie node to source enumeration, find a binding collision/miss, super-cap projection,
large output, lost sign, restriction rebuild, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy trie relations with one labelled five-way join tuple.
- Negative: identical projections/different sources, empty joins, dense outputs, repeated points,
  variable-order permutations, and blind targets.
- Baselines: InsideOut, Patricia tries, P1553 R4, rho, and BSGS.
- Worst-case-optimal execution on supplied input is toy/model-bound evidence only.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only tries, zero semantic errors over four sizes, full rank/logs,
  100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on supplied/source-sized tries, one semantic error, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p04_trie_constructor_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p04_binding_collision_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p04_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Leapfrog Triejoin. All claims remain toy, heuristic,
model-bound, and novelty-unverified; no execution bound alone is a breakthrough.

## Exactly one next executable action

1. Expand the smallest proposed endpoint trie node and seek operation to primitive curve work and preserve the first source-table or super-cap projection dependency.
