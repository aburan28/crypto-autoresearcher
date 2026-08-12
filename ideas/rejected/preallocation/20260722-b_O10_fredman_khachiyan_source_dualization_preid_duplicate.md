# Pre-ID duplicate draft — Fredman–Khachiyan source dualization

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O10`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_monotone_formula_and_transversal_family`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a dual formula, transversal, or valid relation is not an ECDLP result.

## Falsifiable hypothesis

Endpoint restrictions compile to a compact monotone formula whose Fredman–Khachiyan
dualization returns exactly the minimal signed factor-source transversals of a target fibre,
enabling relation rows and fresh blind descent inside `lambda,mu<=0.45`.

## Mechanism-new operation

Fredman–Khachiyan gives quasi-polynomial testing of whether two supplied monotone DNFs are
dual. Minimal-transversal generation follows through standard dualization/transversal
reductions and repeated duality tests; it is not the paper's direct output claim. The route
counts only if the formula is endpoint-derived without source clauses and generated
transversals invert to ordered signed occurrences.

## Assumptions

1. The monotone formula is compact, endpoint-only, and target-uniform.
2. Prime implicants/transversals are biconditional with exact five-source tuples.
3. Signs, repeated occurrences, all strata, and arbitrary restrictions are represented exactly.
4. Formula/output sizes and all-negative duality decisions fit the caps.
5. The same compiler and ordering support relations and 100 fresh masked targets.

## Semantic fingerprint

`public_endpoint_monotone_formula | Fredman_Khachiyan_dualization | minimal_source_transversals | signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — hypergraph representation is source-bearing and containers aggregate.
2. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — formula compilation and source inversion are the missing steps.
3. `ideas/rejected/ECDLP-IDEA-137_matroid_representative_completion_kernel_hypothesis.md` — supplied completion predicates do not create target sources.
4. `ideas/rejected/preallocation/20260722-b_O02_reiter_hitting_set_source_diagnosis_preid_duplicate.md` — minimal transversals need a supplied conflict family.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence/replay owner.

## Closest primary literature

- Fredman and Khachiyan, [On the Complexity of Dualization of Monotone Disjunctive Normal Forms](https://doi.org/10.1006/jagm.1996.0062), gives quasi-polynomial duality testing for supplied monotone DNFs; transversal generation uses reductions and repeated tests.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not compile the required monotone formula or inverse.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

The title is distinct, but the information flow merges with supplied formula, hitting-set,
and hypergraph lanes; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, variables, clauses/terms, dualization policy, restrictions, signs, strata, and verifier.
2. Compile target-independent endpoint state within `B^(9/4+o(1))`; forbid source clauses, explicit transversals, target advice, and scalar labels.
3. For each known-log target, construct allowed formula state, dualize/list one transversal, invert to occurrences, and verify point equality.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs while charging false and duplicate outputs.
5. Reuse identical state for 100 fresh `R=Q+[t]P` targets, recover occurrences, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge formula construction, quasi-polynomial representation dependence, recursion, dual outputs, replay, density, rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`.
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; input/output formula sizes and all
transversals are charged. Promotion requires `lambda,mu<=0.45`, setup/state
`<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`. Pollard rho
expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

The clauses or hyperedges encode the missing target/source incidence. Monotone formulas
cannot natively encode signed cancellation or exact equality without expansion, and the
minimal transversal family can be exponential. Quasi-polynomial time in a supplied
representation does not give a sub-rho endpoint compiler or signed inverse.

## Proof track

Prove a compact endpoint-only monotone encoding whose minimal transversals are exactly
all-strata signed source tuples and whose dualization plus replay satisfies both caps.

## Disproof track

Find one source-bearing clause, formula blowup, transversal/target mismatch, lost sign,
exponential output, target rebuild, or exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy monotone formula with one labelled minimal transversal.
- Negative: equal formulas with different signed sources, exponential duals, empty fibres, repeated signs, and blind targets.
- Baselines: Reiter HS-tree, explicit hypergraph transversal enumeration, Query2P1, rho, and BSGS.
- Controls are toy and model-bound.

## Quantitative promotion and falsification gates

- Promote only with exact formula/source biconditionality, four sizes, bounded input/output, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied clauses, one false/missed tuple, sign loss, output/cap failure, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o10_formula_compiler_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o10_dualization_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o10_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This rejects only the transplant, not monotone dualization. Evidence remains toy,
heuristic, model-bound, and novelty-unverified; no run or breakthrough is claimed.

## Exactly one next executable action

1. Write the endpoint monotone formula and either prove its minimal transversals are exact signed target tuples or preserve the first source-bearing clause or false transversal.
