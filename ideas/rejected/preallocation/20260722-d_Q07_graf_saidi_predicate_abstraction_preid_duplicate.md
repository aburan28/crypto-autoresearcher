# Pre-ID duplicate draft — Graf–Saïdi predicate source abstraction

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q07`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_predicates_and_theorem_queries`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a verified abstract transition is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, choose public predicates over partial-sum states, construct
an exact abstract state graph with theorem-prover successor queries, and traverse it to an
accepting target state whose trace replays signed factor-base occurrences. One abstraction
supports rank-complete relations and 100 fresh masked targets below exponent `0.45`.

## Mechanism-new operation

The native operation partitions a supplied concrete state space by predicates and asks a
theorem prover which abstract successors are possible. It counts only if predicates,
successor formulas, and exact proofs are endpoint-derived without source incidence and if an
accepting abstract trace has a charged signed concretization. Source-specific predicate
discovery or exact concrete checking is a control.

## Assumptions

1. A fixed public predicate set yields a subcap abstract graph for all targets and restrictions.
2. Theorem-prover successor queries are strictly cheaper than Query2P1 and contain no source tuples.
3. Abstract reachability is biconditional with concrete restricted-source existence.
4. Every accepting abstract trace concretizes to signed occurrences on all exceptional strata.
5. The same graph and predicates serve relation collection and fresh masked descent.

## Semantic fingerprint

`public_endpoint_predicates | graf_saida_abstract_successor_graph | exact_restricted_reachability | accepting_trace_signed_concretization | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-a_A10_cegar_endpoint_abstraction_source_refinement_preid_duplicate.md` — exact refinement requires the missing concrete oracle.
2. `ideas/rejected/preallocation/20260722-a_N01_mackworth_ac3_source_arc_filter_preid_duplicate.md` — local predicate filtering does not establish global source existence.
3. `ideas/rejected/preallocation/20260722-a_N07_dechter_bucket_source_elimination_preid_duplicate.md` — exact elimination begins with supplied source factors.
4. `ideas/rejected/preallocation/20260722-a_N03_dpll_source_unit_branching_preid_duplicate.md` — theorem/SAT search is downstream of formula construction.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Graf and Saïdi, [Construction of Abstract State Graphs with PVS](https://doi.org/10.1007/3-540-63166-6_10), constructs an abstract graph from supplied predicates using theorem-prover postcondition checks.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies concrete equations but not a compact exact predicate basis.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

The graph-construction method is native-scope distinct, but its ECDLP use merges with
CEGAR/local-consistency/solver lanes unless the public predicates remove the source-return
obstruction. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, concrete states, predicate basis, abstraction, successor queries, restrictions, trace concretizer, strata, and verifier.
2. Build predicates and target-independent abstract graph within `B^(9/4+o(1))`; forbid source incidence, scalar labels, target fitting, and hidden decomposition calls.
3. For each known-log target, traverse exact abstract successors, concretize one accepting trace to signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs while charging theorem calls, graph growth, restrictions, trace output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge predicate construction, every prover query/proof, abstract edge/state, rejected trace, concretization, rank, logs, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, prover/query workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires
`lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace
`<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

The method assumes useful predicates and exact theorem-prover postconditions. Predicates
strong enough to separate empty from rare nonempty source fibres encode source incidence;
weak predicates create spurious accepting traces whose concretization invokes Query2P1.
Exact predicate refinement can grow to one predicate per source configuration.

## Proof track

Prove an endpoint-only finite predicate basis, exact subcap successor queries,
restriction-stable concrete replay, and the full relation/log/descent path.

## Disproof track

Find a source-specific predicate, a spurious/missed abstract trace, a prover query equivalent
to exact source search, graph blowup/rebuild, lost replay, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy state system with an exact labelled predicate partition.
- Negative: omit one source predicate; include spurious reachability, empty restrictions, equal abstract traces/different sources, and blind targets.
- Baselines: CEGAR, AC-3, bucket elimination, P1553 R4, rho, and BSGS.
- Verified abstract transitions are only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact reachability/replay at four sizes/all strata, fixed predicate/graph caps, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-bearing predicate/query, spurious or missed trace, replay loss, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q07_predicate_dependency_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q07_spurious_trace_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q07_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not predicate abstraction. All findings remain toy, heuristic,
model-bound, and novelty-unverified; a proved edge or accepting trace is not a breakthrough.

## Exactly one next executable action

1. Expand one proposed abstract-successor proof obligation and preserve the first source-specific predicate or exact concrete-source query it requires.
