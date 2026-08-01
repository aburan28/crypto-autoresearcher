# Pre-ID duplicate draft — Biere bounded-source unrolling

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q10`; no canonical ID allocated.
- Disposition: `merged_rejected_sat_unrolling_of_source_choices`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a SAT witness or bounded proof is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, encode five signed factor-base selections as bounded
transitions, unroll them into a compact SAT instance, and solve exact restricted target
reachability. A satisfying trace replays occurrences for rank-complete relations and 100
fresh masked targets with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation unfolds a supplied finite transition relation for `k` steps and reduces
bounded reachability to propositional satisfiability. It counts only if each unrolled
transition is compiled from public endpoints without source-index enumeration and if SAT
models replay exact signed points. Unrolling an explicit source-choice system is a control.

## Assumptions

1. A five-step target-independent transition grammar is complete and source-blind.
2. Tseitin/CNF construction stays sparse and does not encode a source table in clauses.
3. SAT solving, model extraction, and all-negative cases fit the online cap.
4. Models preserve signs, multiplicities, and exceptional addition strata.
5. Identical compiled state serves relations and 100 fresh masked targets.

## Semantic fingerprint

`public_endpoint_bounded_transition | biere_sat_unrolling | exact_restricted_reachability | sat_model_signed_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260722-a_N03_dpll_source_unit_branching_preid_duplicate.md` — DPLL searches supplied source clauses.
2. `ideas/rejected/preallocation/20260722-a_N04_grasp_conflict_clause_source_search_preid_duplicate.md` — CDCL is an occupied downstream solver lane.
3. `ideas/rejected/preallocation/20260722-a_N05_chaff_two_watch_source_propagator_preid_duplicate.md` — watched literals change propagation engineering only.
4. `ideas/rejected/ECDLP-IDEA-337_barrington_width5_source_branch_program_hypothesis.md` — compact branching state still needs source-bearing transitions.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Biere et al., [Symbolic Model Checking without BDDs](https://doi.org/10.1007/3-540-49059-0_14), unrolls a supplied transition system and reduces bounded model checking to SAT.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies a relation equation but not a subcap exact source-transition CNF.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

Bounded unrolling is native-scope distinct but the transplant is a direct SAT/branch-program
solver substitution after source-formula construction. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, transition grammar, depth, CNF encoding, restrictions, model decoder, strata, and verifier.
2. Build target-independent transition/CNF templates within `B^(9/4+o(1))`; forbid explicit source tables, scalar residues, target fitting, and hidden decomposition calls.
3. For each known-log target, instantiate and solve the bounded formula, decode signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every factor log while charging template construction, clauses, SAT, models, failures, output, and sparse linear algebra.
5. Reuse identical templates for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge all variables/clauses, preprocessing, decisions/conflicts, UNSAT proofs, models, restrictions, rank, logs, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, SAT/query workspace `N^q,N^q_m`, rank credit `N^r`, output
`N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; all CNF and UNSAT costs are charged.
Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh
work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent-`0.50` controls.

## Likely fatal obstruction

The bounded transition relation is the missing source-bearing object. Encoding five choices
over a factor base supplies `5 log B` choice bits plus elliptic constraints whose exact
solutions are the relation catalogue; SAT changes the solver but not generic density,
source enumeration, proof size, or fresh-target cost.

## Proof track

Prove an endpoint-only subcap transition/CNF compiler, bounded worst-case SAT/UNSAT costs,
all-strata exact model replay, and the full relation/log/descent path.

## Disproof track

Expose source-index variables/clauses, dense relation encoding, hard SAT/UNSAT families,
target-specific rebuild, model/replay error, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy transition CNF with one planted signed trace.
- Negative: delete one source transition; use empty fibres, same endpoint/different models, hard UNSAT formulas, and blind targets.
- Baselines: DPLL, GRASP/CDCL, Chaff, branch programs, P1553 R4, rho, and BSGS.
- SAT correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact SAT/UNSAT and replay at four sizes/all strata, proved clause/solve caps, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-bearing clause/template, solve/replay error, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q10_unrolling_dependency_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q10_sat_unsat_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q10_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not bounded model checking. All evidence remains toy,
heuristic, model-bound, and novelty-unverified; a SAT model, UNSAT proof, or row is not a
breakthrough.

## Exactly one next executable action

1. Expand the bounded-transition CNF schema and preserve the first variable or clause whose construction enumerates a factor-base source choice.
