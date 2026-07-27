# Pre-ID duplicate draft — Angluin L-star endpoint learner

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q04`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_membership_equivalence_teacher`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a learned automaton or correct classification is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, learn a minimal automaton for exact restricted signed-source
existence using public endpoint experiments, then use accepted words and counterexample
traces to replay factor-base occurrences. One learned automaton supports rank-complete
relations and 100 fresh masked targets with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation maintains an observation table, asks membership and equivalence
queries, closes/consistently refines the table, and constructs a minimal DFA. It counts only
if both teachers are implemented from public endpoints below the gates and counterexamples
carry charged signed source replay. Treating Query2P1 or explicit search as the teacher is a
control.

## Assumptions

1. The exact restricted-source language is regular with target-uniform subcap state complexity.
2. Membership and equivalence queries are source-blind and cheaper than exact decomposition.
3. Counterexamples are produced without post-hoc source selection or scalar leakage.
4. Accepted words retain signs, multiplicities, and all exceptional-stratum semantics.
5. The learned target-independent automaton generalizes to fresh masked targets without retraining.

## Semantic fingerprint

`public_endpoint_query_teacher | angluin_lstar_observation_table | exact_restricted_language | counterexample_signed_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — minimal state can remain source-sized without an indistinguishability theorem.
2. `ideas/rejected/preallocation/20260720-c_G01_hopcroft_dfa_source_partition_preid_duplicate.md` — DFA minimization starts from a supplied source automaton.
3. `ideas/rejected/preallocation/20260719-a_A10_cegar_endpoint_abstraction_source_refinement_preid_duplicate.md` — counterexample refinement invokes the missing concrete oracle.
4. `ideas/rejected/ECDLP-IDEA-138_sumcheck_source_self_reduction_hypothesis.md` — query self-reduction must charge exact source-return oracles.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Angluin, [Learning Regular Sets from Queries and Counterexamples](https://doi.org/10.1016/0890-5401(87)90052-6), learns from a minimally adequate teacher supplying membership answers and equivalence counterexamples.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not either exact teacher.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

The learning loop is title-new here, but its teacher is exactly the occupied endpoint decision
and source-return interface. No primary source provides that ECDLP teacher; novelty is
unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, alphabet, word encoding, teachers, observation-table policy, restrictions, strata, and verifier.
2. Implement endpoint-only membership/equivalence teachers and learn target-independent state within `B^(9/4+o(1))`; forbid source enumeration, target fitting, scalar residues, and hidden decomposition.
3. For each known-log target, query the automaton, replay an accepted word/counterexample to signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every factor log while charging all teacher calls, refinements, words, output, and sparse linear algebra.
5. Reuse identical state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge teacher construction, membership/equivalence queries, counterexample length, table/state growth, failures, replay, rank, logs, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, teacher/query workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. All adaptive queries are charged.
Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh
work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent-`0.50` controls.

## Likely fatal obstruction

L-star's guarantee assumes a minimally adequate teacher. Exact membership is Query2P1;
equivalence requires proving all restrictions or returning a source-bearing counterexample.
Replacing either with samples destroys exact empty-fibre semantics, while exact teachers
already solve the missing problem and may force source-sized automata.

## Proof track

Prove endpoint-only exact teachers, a target-uniform state/query bound, signed
counterexample replay, restriction generalization, and the complete relation/log/descent
path below both caps.

## Disproof track

Expand either teacher to Query2P1/source search, exhibit a source-sized minimal DFA or
adversarial counterexample sequence, find one classification/replay error, or reach
complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied small DFA teacher with one planted accepted signed word.
- Negative: remove equivalence access; use rare singleton languages, empty restrictions, same classification/different sources, and blind targets.
- Baselines: Myhill–Nerode, Hopcroft minimization, CEGAR, P1553 R4, rho, and BSGS.
- Learned accuracy on sampled toy words is only heuristic/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact teachers, zero errors at four sizes/all strata, proved state/query caps, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one oracle-equivalent teacher, classification/replay error, source-sized state/query growth, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q04_teacher_dependency_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q04_adversarial_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q04_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not active automata learning. All results remain toy,
heuristic, model-bound, and novelty-unverified; learned accuracy or a valid source word is
not a breakthrough.

## Exactly one next executable action

1. Implement neither teacher; instead expand their formal specifications and preserve the first exact endpoint query that is equivalent to Query2P1 or source search.
