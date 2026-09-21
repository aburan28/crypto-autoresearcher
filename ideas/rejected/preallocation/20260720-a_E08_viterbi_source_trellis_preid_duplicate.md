# Pre-ID duplicate draft — Viterbi source trellis

## Status and claim labels

- Prospect: 20260720-a-E08; no canonical ECDLP idea ID was allocated
- Class / risk / lane: trellis_dynamic_program / representation-changing / representation-changing pre-ID screen
- State: merged_rejected_supplied_transition_trellis_and_best_path_only
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; correct maximum-likelihood decoding on a supplied trellis is not an ECDLP break.

## Falsifiable hypothesis

Represent signed elliptic addition as a finite-state trellis whose emissions are public endpoint coordinates. Viterbi survivor recursion would keep the best predecessor for each public state and return an exact source path compatible with a target, providing independent factor-base relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

The Viterbi algorithm performs max-product dynamic programming on a supplied finite-state trellis and backtraces one optimal path. It counts only if states/transitions are endpoint-derived below the gate, optimality is biconditional with exact elliptic compatibility, and discarding non-survivor paths cannot erase the sole valid source under later restrictions. Decoding an explicit source trellis is a control.

## Assumptions

1. A bounded-state, target-independent trellis is complete for every signed and exceptional elliptic addition path.
2. State/transition construction, emissions, metrics, tie handling, survivor pointers, restrictions, backtrace, rank, logs, descent, bit time, and memory are charged.
3. The optimal public-metric path is an exact valid source and a valid path cannot be pruned by an invalid equal-state prefix.
4. Backtrace returns point-faithful factor-base occurrences, not only aggregate states.
5. One frozen trellis/metric serves known-log and fresh scalar-blind targets without target-trained transitions or source labels.

## Semantic fingerprint

public_finite_elliptic_trellis | Viterbi_survivor_recursion | exact_restricted_accepting_path | survivor_backtrace_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 freezes exact restricted existence and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 requires a public exact source-resolving circuit.
3. inputs/ledger_inventory_20260719.json — ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER charges a lossless source DAG.
4. ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md — finite state quotients merge prefixes with different future source behavior.
5. ideas/rejected/ECDLP-IDEA-377_courcelle_mso_tree_automaton_source_compiler_hypothesis.md — automaton solving assumes a supplied source structure and inverse.

## Closest primary literature

- Viterbi, [Error bounds for convolutional codes and an asymptotically optimum decoding algorithm](https://doi.org/10.1109/TIT.1967.1054010), decodes paths in a supplied convolutional-code trellis; it does not construct an elliptic source trellis.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) gives endpoint equations but no bounded source-faithful state machine.
- Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) gives the baseline.

No checked source supplies the trellis compiler, exact restricted source return, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, trellis compiler, state equivalence, emission metric, tie rule, restrictions, and verifier.
2. Construct target-independent trellis/survivor state within B^(9/4+o(1)) without source-product transitions.
3. For known-log R=[kappa]P, run exact restricted decoding, backtrace labelled points A_i with signs epsilon_i using at most 5 ceil(log_2 B)+O(1) charged restriction queries plus negative siblings, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; preserve discarded/tied paths and failures, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse unchanged trellis for fresh R=Q+[t]P, recover a path, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge compiler, all states/transitions, every metric/tie/survivor, restrictions, backtrace, rank, logs, descent, verification, bit operations, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge state/transition/emission construction and survivor storage; q,q_m charge target emissions, all state relaxations, tie expansion, restrictions, bisection, and backtrace. Let delta,delta_t be reciprocal verified relation/target path densities, r independent-rank credit, o output, u tied/discarded paths and state ambiguity, and ell,ell_m factor-log time/state.

Let S_t and E_t be the state and transition sets at stage t. A full decode costs Theta(sum_t |E_t|); score-only memory is O(max_t |S_t|), but source backtrace stores Theta(sum_t |S_t|) survivor pointers unless recomputed, and a dense layer has |E_t|=Theta(|S_t|^2). Set a=log_N(T_trellis+sum|E_t|), a_m=log_N(M_trellis), q=log_N(Q_R sum|E_t|+T_ties+T_backtrace), and q_m=log_N(max|S_t|+M_survivors). Exact existence needs Boolean/min-plus semantics or a proved max-product metric. One-survivor recursion is sound only if each state is a sufficient Markov/completion equivalence; the failure is the unproved elliptic state compiler, not Viterbi under that premise.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require state <=B^(9/4+o(1)), fresh decode/restriction/backtrace <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho and BSGS baselines are 0.50. State count, all transitions, survivor pointers, equal-metric multiplicity, and restriction rebuilds are charged.
The full fresh masked-target decode/tie/backtrace/replay path must also be <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion needs four increasing B values with one-sided 95% upper bounds on sum|E_t|, survivor state, restriction, fresh, and complete exponents, plus zero state-equivalence counterexamples.

## Likely fatal obstruction

Viterbi decoding assumes the trellis and transition/emission semantics. Exact elliptic transitions are the missing source graph; quotienting them into bounded public states merges prefixes whose future valid completions differ. Keeping one survivor per state can discard the only later-compatible source, while retaining all tied/source-labelled survivors materializes the source DAG. This merges with IDEAS 084/120/338/377.
Within this cohort it collides with E09: both assume a supplied sequential source model and lose exact genealogy unless they retain source-scale path state.

## Proof track

Prove a bounded endpoint-only Myhill–Nerode-like state equivalence that is complete under every restriction, an exact public path metric, point-faithful backtrace, and full descent costs.

## Disproof track

Give two prefixes with the same admitted state/metric but different valid target completions, or expose one source-bearing transition/survivor pointer.

## Positive and negative controls

- Positive: a supplied convolutional-style trellis with a unique planted labelled path.
- Negative: equal-state prefixes with distinct future validity, tied metrics, pruned valid paths, exceptional charts, arbitrary restrictions, absent targets, and blind targets.
- Baselines: IDEAS 084/120/338/377, exhaustive trellis path enumeration, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only bounded trellis, restriction-stable exact state equivalence, all-strata backtrace, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source transition, one merged-prefix future mismatch, source-scale tie retention, target-trained metric, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e08_trellis_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e08_equal_state_future_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e08_cost_analysis.md

## Interpretation boundary

This rejects the elliptic trellis compiler, not Viterbi decoding. Toy decoding correctness or a valid source path is not a breakthrough.

## Exactly one next executable action

1. Write ideas/rejected/preallocation/artifacts/20260720-a/e08_trellis_provenance.md and construct the smallest pair of equal public states with different restricted elliptic completions.
