# Pre-ID duplicate draft — King symbolic source execution

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q11`; no canonical ID allocated.
- Disposition: `merged_rejected_symbolic_source_path_search`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a feasible path condition or concrete witness is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, symbolically execute a public partial-addition program over
five factor-base choices, fork only on endpoint-derived conditions, and solve one target path
condition whose model replays signed occurrences. Cached symbolic state supports
rank-complete relations and 100 fresh masked targets with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation executes a supplied program on symbolic inputs, accumulates path
conditions at branches, and invokes a constraint solver for feasibility. It counts only if
the program and branches are source-blind, path exploration is subcap including infeasible
paths, and models replay signed points. Symbolically executing explicit source-choice code is
a control.

## Assumptions

1. A target-independent public program represents all signed decompositions without enumerating them in code.
2. Path count and condition size remain subcap on all restrictions and exceptional strata.
3. Constraint solving is strictly cheaper than Query2P1 and contains no source oracle.
4. Feasible path models retain factor-base indices, signs, and multiplicities.
5. Cached symbolic state generalizes unchanged to 100 fresh masked targets.

## Semantic fingerprint

`public_endpoint_partial_sum_program | king_symbolic_path_execution | exact_restricted_path_feasibility | model_signed_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260722-a_N03_dpll_source_unit_branching_preid_duplicate.md` — solver branching starts from source-bearing variables and constraints.
2. `ideas/rejected/preallocation/20260720-d_H05_astar_heuristic_source_search_preid_duplicate.md` — path search does not construct the source graph or exact heuristic.
3. `ideas/rejected/preallocation/20260721-a_I11_savitch_recursive_source_reachability_preid_duplicate.md` — low-space reachability still charges source-state construction and time.
4. `ideas/rejected/preallocation/20260720-c_G01_hopcroft_dfa_source_partition_preid_duplicate.md` — a compact execution automaton must already encode source transitions.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- King, [Symbolic Execution and Program Testing](https://doi.org/10.1145/360248.360252), executes a supplied program on symbolic inputs and branches by symbolic path conditions.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but not a compact symbolic program or cheap path solver.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

Symbolic execution is native-scope distinct, but its ECDLP transplant is a path-search/solver
merge when the supplied program exposes source choices. No source proves path compactness or
a new endpoint operation; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, program, symbolic inputs, branch policy, solver, restrictions, model replay, strata, and verifier.
2. Build target-independent program/cache within `B^(9/4+o(1))`; forbid source tables, scalar labels, target fitting, and hidden decomposition calls.
3. For each known-log target, explore and solve exact path conditions, decode signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every factor log while charging program construction, forks, solver calls, failures, models, and sparse linear algebra.
5. Reuse identical cached state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge every instruction, symbolic expression, fork/path, merge, solver query, failed condition, model, rank, log, bit operation, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, symbolic query/workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; infeasible paths and solver proofs are
charged. Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and
fresh work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent-`0.50` controls.

## Likely fatal obstruction

The symbolic program's inputs are the factor-base choices and its path conditions are the
source relation equations. Symbolic execution reorganizes search but does not reduce generic
relation density; path explosion, solver cost, and all-negative targets remain. Merging paths
loses occurrence identity unless source provenance is retained.

## Proof track

Prove an endpoint-only compact program, uniform path/solver bounds, restriction-stable exact
model replay, and complete relation/log/descent costs inside both caps.

## Disproof track

Expose source-choice inputs or branch tables, exponential paths/conditions, solver-equivalent
Query2P1, path-merge ambiguity, target rebuild, lost replay, or exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy branch program with one labelled feasible signed path.
- Negative: path-explosion programs, empty fibres, merged equal states/different sources, infeasible branches, and blind targets.
- Baselines: DPLL, A-star, Savitch reachability, P1553 R4, rho, and BSGS.
- A feasible symbolic path is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact path semantics at four sizes/all strata, proved path/solver caps, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on source-choice code, one feasibility/replay error, path or solver cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q11_program_input_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q11_path_explosion_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q11_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not symbolic execution. All evidence remains toy, heuristic,
model-bound, and novelty-unverified; a feasible path, witness, or relation is not a
breakthrough.

## Exactly one next executable action

1. Inline the symbolic partial-sum program and preserve the first source-choice input, Query2P1-equivalent branch, or exponential path family.
