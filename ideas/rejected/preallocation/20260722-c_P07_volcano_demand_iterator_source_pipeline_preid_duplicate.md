# Pre-ID duplicate draft — Volcano demand-iterator source pipeline

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P07`; no canonical ID allocated.
- Disposition: `merged_rejected_execution_engine_and_operator_scheduling`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; pipelining or relation validity is not an ECDLP result.

## Falsifiable hypothesis

A Volcano-style pull pipeline can fuse endpoint factor generation, restricted joining,
verification, and source replay so target demand stops before materializing dense intermediates.
The fused iterator completes relations, factor logs, and blind descent below exponent `0.45`.

## Mechanism-new operation

Volcano exposes a uniform `open/next/close` iterator interface and exchange operators over
supplied algebra operators. It counts only if fusion removes a mathematically necessary source
object rather than rescheduling its construction, and each returned tuple has exact signed
provenance. Ordinary iterator fusion and early stopping are controls.

## Assumptions

1. Every operator is endpoint-derived and scalar-blind.
2. No hidden operator materializes pair/source tables or target-fitted state.
3. Iterator rejects, restarts, buffering, exchange, and all-negative demand are charged.
4. Returned tuples are exact on all strata and replay signed point occurrences.
5. The same physical plan serves relation targets and 100 fresh masks.

## Semantic fingerprint

`public_endpoint_operator_plan | Volcano_pull_iterator_fusion | demand_driven_exact_tuple | charged_signed_provenance | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-325_insideout_faq_source_join_hypothesis.md` — execution order is downstream of relation construction.
2. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — physical fusion cannot erase width/provenance cost.
3. `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md` — dynamic evaluation still needs a source-bearing tree.
4. `ideas/rejected/ECDLP-IDEA-343_avis_fukuda_reverse_search_source_enumerator_hypothesis.md` — early enumeration remains output/source charged.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — missing mathematical endpoint operation.

## Closest primary literature

- Graefe, [Volcano — An Extensible and Parallel Query Evaluation System](https://doi.org/10.1109/69.273032), provides an execution system for supplied operators.
- Selinger et al., [Access Path Selection](https://doi.org/10.1145/582095.582099), is the nearby optimizer control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not supply a sparse source operator; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) controls cost.

This is an execution/scheduling substitution after the missing endpoint predicate, not a new
mathematical information flow; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, logical/physical operators, iterator protocol, buffers, restrictions,
   provenance, strata, and verifier.
2. Compile endpoint-only plan/state within `B^(9/4+o(1))`; forbid source/pair tables, scalar
   residues, target caches, dense resultants, and post-hoc plan choice.
3. For each known-log target, pull until an exact signed tuple or certified exhaustion, replay
   occurrences, and verify the elliptic equation.
4. Collect `max(d_FB+32,1000)` rows, require rank `d_FB`, solve all factor logs, and charge
   rejected tuples, restarts, buffering, provenance, rank, and sparse linear algebra.
5. Reuse identical plan/state for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge every operator call, generation, verification, output, bit cost, and live memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state are `N^a,N^a_m`; relation/target reciprocal densities
`N^delta,N^delta_t`; iterator work/workspace `N^q,N^q_m`; rank credit `N^r`; output
`N^o`; rejection/restart amplification `N^u`; factor-log time/memory `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Volcano changes control flow, not the mathematical operator. A pull iterator still pays to
generate and test every underlying source candidate until success; early stopping without a
public predictive operation is ordinary post-hoc selection.

## Proof track

Identify an operator fusion that algebraically eliminates a source-sized intermediate while
preserving exact signed replay, then prove complete caps and exponents.

## Disproof track

Inline every iterator until source enumeration reappears; find a false/missed exhaustion,
post-hoc plan choice, lost provenance, cap violation, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy operators whose fused iterator emits one labelled tuple.
- Negative: empty pipelines, long reject prefixes, materializing operators, duplicate tuples,
  plan-order permutations, repeated signed points, and blind targets.
- Baselines: InsideOut, dynamic evaluation trees, P1553 R4, rho, and BSGS.
- Pipeline speed on supplied data is toy/model-bound engineering evidence only.

## Quantitative promotion and falsification gates

- Promote only if fusion proves a new endpoint operation, zero errors at four sizes, full
  rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on pure rescheduling, hidden materialization, one semantic error, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p07_operator_inline_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p07_iterator_reject_prefixes.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p07_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects an execution-engine substitution, not Volcano. Evidence remains toy, heuristic,
model-bound, and novelty-unverified.

## Exactly one next executable action

1. Inline the proposed physical plan to primitive endpoint operations and preserve the first source-sized intermediate or post-hoc stop dependency.
