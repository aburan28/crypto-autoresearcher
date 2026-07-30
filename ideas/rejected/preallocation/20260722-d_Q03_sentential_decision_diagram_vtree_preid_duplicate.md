# Pre-ID duplicate draft — sentential-decision-diagram source vtree

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q03`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_boolean_knowledge_base`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a compact or canonical diagram is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, compile the exact restricted signed five-source relation
into a canonical sentential decision diagram under a public vtree. Conditioning decides
existence and a satisfying path replays occurrences for rank-complete relations and 100
fresh masked targets with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation recursively decomposes a supplied Boolean function into deterministic,
decomposable sentential decisions structured by a vtree and applies reduction for
canonicity. It counts only if endpoint data construct the Boolean function and vtree without
truth-table/source enumeration and if conditioning preserves exact signed replay. Compiling
a supplied answer predicate is a control.

## Assumptions

1. A public target-independent vtree yields subcap SDD size for every relevant restriction.
2. Prime/sub relations are constructed from endpoints without Query2P1 terminal queries.
3. Decomposability and determinism preserve all signs, multiplicities, and exceptional strata.
4. Conditioning fresh targets does not rebuild the diagram or scan source-sized nodes.
5. A satisfying path returns actual occurrences, not only an existence bit.

## Semantic fingerprint

`public_endpoint_boolean_relation | sdd_vtree_sentential_decomposition | exact_conditioned_existence | satisfying_path_signed_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-b_B06_robdd_shannon_source_compiler_preid_duplicate.md` — an ROBDD needs the supplied truth function and can be exponential.
2. `ideas/rejected/preallocation/20260719-a_A04_zero_suppressed_decision_source_compiler_preid_duplicate.md` — a ZDD compiles a supplied accepting family.
3. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — decomposable circuits must charge source-leaf construction.
4. `ideas/rejected/ECDLP-IDEA-337_barrington_width5_source_branch_program_hypothesis.md` — branching representations do not create the endpoint predicate.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Darwiche, [SDD: A New Canonical Representation of Propositional Knowledge Bases](https://ocs.aaai.org/ocs/index.php/IJCAI/IJCAI11/paper/viewPaper/3341), gives canonical structured diagrams and width-sensitive size bounds for supplied knowledge bases.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not the Boolean relation compiler.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

SDDs are a distinct native representation, but this transplant is a decision-diagram/circuit
merge until an endpoint-only compactness theorem constructs exact terminals. Novelty is
unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, Boolean variables, vtree, apply/reduce rules, restrictions, strata, replay, and verifier.
2. Build the endpoint-only SDD within `B^(9/4+o(1))`; forbid enumerated truth tables, source tuples, target fitting, scalar residues, and hidden decomposition calls.
3. For each known-log target, condition the SDD, unrank one satisfying path, replay signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs while charging compilation, apply, reduction, conditioning, output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge Boolean-function construction, all nodes/edges, vtree search, conditioning, misses, path output, rank, logs, bit complexity, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, SDD query/workspace `N^q,N^q_m`, rank credit `N^r`, output
`N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires
`lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace
`<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

SDD succinctness is relative to a supplied Boolean function and vtree width. Constructing
the exact terminal function is Query2P1 or source enumeration; adversarial target-labelled
relations can have large structured width, and a fresh target changes the function.
Canonicity compresses duplicate subfunctions but does not supply occurrences.

## Proof track

Prove endpoint-only terminal construction, a target-uniform subcap vtree-width theorem,
all-strata conditioning correctness, signed path replay, and complete relation/log/descent
costs.

## Disproof track

Expose truth-table or membership-oracle construction, one exponential-width family, a
conditioning rebuild, false/missed path, lost occurrence, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy Boolean relation with a small planted-vtree SDD and one labelled path.
- Negative: hidden-parity/high-width functions, equal truth values/different sources, empty restrictions, variable reorderings, and blind targets.
- Baselines: ROBDD, ZDD, source-faithful DNNF, P1553 R4, rho, and BSGS.
- Compactness or canonicity is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact all-strata compilation at four sizes, a proved width cap, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on a supplied truth predicate, one width/correctness/replay failure, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q03_vtree_width_theorem.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q03_conditioning_replay_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q03_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not SDDs. All checks would be toy, heuristic, model-bound, and
novelty-unverified; a small diagram or satisfying path is not a breakthrough.

## Exactly one next executable action

1. Define the endpoint-only SDD terminal constructor and prove a restriction-stable vtree-width bound or preserve the first Query2P1/source-enumeration call.
