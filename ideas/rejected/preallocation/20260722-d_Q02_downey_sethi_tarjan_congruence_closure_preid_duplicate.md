# Pre-ID duplicate draft — Downey–Sethi–Tarjan source congruence closure

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q02`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_term_equalities`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a correct congruence class or proof trace is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, form an endpoint-derived term DAG for partial elliptic sums,
close public equalities under congruence, and read a target class whose proof forest replays an
exact signed five-point occurrence. The same closure supports rank-complete relations and
100 fresh masked-target descents with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation computes the least congruence containing supplied vertex equalities in
an ordered successor DAG. It counts only if the term graph and seed equalities are produced
without enumerating source terms and if class membership is biconditional with restricted
elliptic-source existence. Closing a supplied source-term graph is a control.

## Assumptions

1. The public term DAG is target-independent, source-blind, and inside the setup cap.
2. Seed equalities are complete for elliptic addition without encoding factor-base tuples.
3. Congruence classes preserve signs, multiplicities, exceptional charts, and proof ancestry.
4. Subset restrictions can be applied without rebuilding a source-sized DAG.
5. One closure serves relation collection and all fresh masked targets.

## Semantic fingerprint

`public_endpoint_term_dag | downey_sethi_tarjan_congruence_closure | exact_restricted_target_class | proof_forest_signed_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-c_C08_equality_saturation_source_egraph_preid_duplicate.md` — e-classes start from supplied terms and equalities.
2. `ideas/rejected/preallocation/20260719-b_B05_knuth_bendix_source_normal_form_preid_duplicate.md` — completion cannot manufacture absent relations.
3. `ideas/rejected/ECDLP-IDEA-084_confluent_factor_word_rewriting_hypothesis.md` — the completed presentation is source/Cayley state.
4. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — quotient states remain large without a source-blind indistinguishability theorem.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Downey, Sethi, and Tarjan, [Variations on the Common Subexpression Problem](https://doi.org/10.1145/322217.322228), computes congruence closure of a supplied graph and equivalence relation.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but not a compact source-term DAG.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

The closure algorithm is title-new in this cohort but its ECDLP information flow merges with
e-graph and rewriting owners. No source supplies the endpoint DAG compiler; novelty is
unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, term grammar, successor order, seed equalities, restrictions, proof forest, strata, and verifier.
2. Build the endpoint-only DAG and congruence state within `B^(9/4+o(1))`; forbid explicit tuple terms, scalar labels, and hidden decomposition calls.
3. For each known-log target, test its class, replay a signed proof path to occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every factor log while charging DAG construction, closure, restrictions, proof output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge every term/equality, union/find or propagation step, restriction update, failed query, proof edge, rank, log, bit operation, and peak live byte.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, closure query/workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires
`lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace
`<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Congruence closure derives only consequences of seed equalities over supplied terms. A term
DAG rich enough to contain the target and five factor-base leaves materializes the missing
source catalogue; a sparse source-blind DAG lacks the target/source biconditional. Proof
forests replay derivations but cannot invent absent leaf occurrences.

## Proof track

Prove a subcap endpoint-only term compiler, complete all-strata seed theory, bounded classes,
restriction-stable proof replay, and the full relation/log/descent path.

## Disproof track

Find explicit source terms or tuple equalities in the input, a missed/false class merge,
source-sized closure, lost signed ancestry, restriction rebuild, or complete exponent
`>=0.50`.

## Positive and negative controls

- Positive: a supplied toy term DAG with one labelled equality chain to a planted tuple.
- Negative: delete the source-bearing seed; test equal endpoints/different occurrences, empty restrictions, congruence cycles, and blind targets.
- Baselines: equality saturation, Knuth–Bendix, P1553 R4, rho, and BSGS.
- Closure correctness is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact closure and replay at four sizes/all strata, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied source term/equality, semantic error, ancestry loss, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q02_term_dag_dependency_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q02_congruence_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q02_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not congruence closure. Evidence remains toy, heuristic,
model-bound, and novelty-unverified; a proof forest or valid relation is not a breakthrough.

## Exactly one next executable action

1. Trace one target-class construction back to the seed DAG and either prove an endpoint-only restricted signed inverse inside both caps or preserve its first source term.
