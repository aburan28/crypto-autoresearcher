# Pre-ID duplicate draft — GRASP conflict-clause source search

## Status and claim labels

- Prospect: `20260722-a-N04`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / high-risk / secondary screen.
- State: `merged_rejected_supplied_cnf_target_specific_learning`.
- Evidence: exhaustive ledger/corpus and checked primary literature only; no experiment ran.
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; learned clauses, solver speed, or a relation do not establish ECDLP progress.

## Falsifiable hypothesis

A compact endpoint CNF for signed factor-base relations admits GRASP-style implication graphs, nonchronological backtracking, and reusable conflict clauses that compress the common source geometry across targets. Charged exact model recovery would then supply full-rank relations and 100 fresh blind descents below rho/BSGS.

## Mechanism-new operation

The screened operation analyzes a conflict in an implication graph, derives an asserting clause, backjumps, and reuses learned clauses. It counts only if the initial CNF is endpoint-derived, learning is sound across masked targets, learned state is within setup caps, and satisfying assignments decode occurrence-distinct signed sources.

## Assumptions

1. Public endpoints compile to a compact exact all-strata CNF without source enumeration.
2. Conflict clauses capture target-independent geometry rather than target-specific unsatisfiable branches.
3. Learned-clause growth, propagation, and restarts fit the complete resource gates.
4. Models and implication reasons preserve source signs, multiplicities, and occurrence labels.
5. The same frozen learner handles relation collection and fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_CNF | GRASP_implication_conflict_learning | cross_target_restricted_decision | signed_model_replay | complete_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — owns the exact predicate/replay requirement that clauses cannot assume.
2. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — learned serial states can merge target/source histories.
3. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — knowledge compilation needs a compact endpoint constructor.
4. `ideas/rejected/ECDLP-IDEA-141_unambiguous_rectangle_source_factorization_hypothesis.md` — clause partitions inherit source-width and inversion costs.
5. `inputs/h100_session/HYPOTHESES_100.md` — H015 already proposes SAT/CDCL with cross-target clause reuse, making this a direct ledger duplicate as well as a solver substitution.

## Closest primary literature

- Marques-Silva and Sakallah, [GRASP: A Search Algorithm for Propositional Satisfiability](https://doi.org/10.1109/12.769433), supplies conflict analysis for a given CNF; it does not provide an elliptic CNF or cross-target invariance.
- Davis, Logemann, and Loveland, [A Machine Program for Theorem-Proving](https://doi.org/10.1145/368273.368557), is the nearby branching baseline.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not compile source-faithful bounded-width clauses.

No checked source constructs the proposed ECDLP interface; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, `B=N^(1/5)`, factor base/decks, exceptional strata, CNF vocabulary, implication reasons, learning/restart/deletion policy, restrictions, masks, and verifier.
2. Build only target-independent clauses and reusable learned state within `B^(9/4+o(1))`; forbid source tables, log labels, target-fitted advice, dense resultants, and Query2P1 calls.
3. For known-log `R`, instantiate endpoint clauses, charge propagation/conflicts/learning, recover actual `(A_i,epsilon_i)`, and verify `sum epsilon_i A_i=R`.
4. Collect at least `max(d_FB+32,1000)` verified rows for actual `d_FB`, retain failures/dependencies, require rank `d_FB`, and solve all factor logs.
5. Reuse only proven target-independent state for fresh `R=Q+[t]P`; decode/verify a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 blind targets.
6. Charge compilation, literals, implications, conflicts, learned clauses, deletion/restarts, restrictions, output, verification, density, rank, factor solve, blind descent, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, freeze `beta=1/5`. With setup/state `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, restricted query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`, amplification `N^u`, and factor-log costs `N^ell,N^ell_m`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory remain exponent `0.50`. Clause learning and cross-target validation are fully charged.

## Likely fatal obstruction

GRASP accelerates search only after the CNF and clause-to-source incidence exist. Learned clauses are consequences of a particular encoding and usually a particular target; reusing them across translated targets can be unsound, while retaining only target-independent clauses does not create the missing predicate. Model reasons and learned databases are source-bearing state. This is a solver and cache substitution, not a new mathematical operation.

## Proof track

Construct an endpoint-only CNF and prove a target-separable clause algebra whose reusable learned consequences remain sound, source-invertible, bounded, and complete below both exponents.

## Disproof track

Find one learned clause invalid under a mask, one source-derived clause/reason, indistinguishable learned states with different sources, unbounded database growth, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied related toy CNFs with a formally separated common clause core and labelled models.
- Negative: target-shifted formulas invalidating learned clauses, empty/singleton fibres, source-aliasing models, repeated occurrences, and blind targets.
- Baselines: DPLL/Davis–Putnam, DNNF, P1553 R4, rho, and BSGS.
- All controls are toy/model-bound; solver acceleration is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only after four-size exactness, formally sound target-independent learning, charged signed replay, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on any unsound reused clause, supplied incidence, lost occurrence, target-fitted learning, cap failure, or complete exponent at least `0.50`.
- Correctness or one verified relation is not a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n04_clause_separation_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n04_cross_target_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n04_cost_analysis.md`

The prospective artifact root is not created.

## Interpretation boundary

This rejects the screened transplant, not GRASP/CDCL. Claims remain toy, heuristic, model-bound, and novelty-unverified. No experiment or breakthrough is claimed.

## Exactly one next executable action

1. Write the clause-separation audit and test every proposed reusable clause symbolically under endpoint masking before any solver run.
