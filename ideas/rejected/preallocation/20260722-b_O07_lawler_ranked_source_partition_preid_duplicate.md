# Pre-ID duplicate draft — Lawler ranked-source partition

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O07`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_optimizer_and_output_charged_enumerator`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a ranked candidate or valid relation is not an ECDLP result.

## Falsifiable hypothesis

An endpoint-derived binary optimization problem ranks source tuples so that Lawler
partitioning enumerates an exact target decomposition after sub-rho total work, preserves
signed occurrences, and supports complete factor logs and fresh scalar-blind descent.

## Mechanism-new operation

Lawler partitions the feasible space of a supplied 0/1 optimization problem and repeatedly
calls an exact optimizer to list the `K` best distinct solutions. It counts only if the
feasible set and optimizer arise from public endpoints without the missing relation oracle,
and all candidates/rejections are included in the end-to-end cost.

## Assumptions

1. The optimization encoding is endpoint-only, target-uniform, and inside setup caps.
2. Every feasible optimum and ranked successor maps to an occurrence-labelled source tuple.
3. A valid target tuple appears within charged sub-rho `K` for every required target.
4. Infeasibility and restriction branches have exact negative semantics.
5. The same objective/tie-breaking works on known-log rows and blind masked targets.

## Semantic fingerprint

`public_endpoint_binary_optimization | Lawler_ranked_partition_subproblems | exact_target_candidate_rank | signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-343_avis_fukuda_reverse_search_source_enumerator_hypothesis.md` — output enumeration begins after a feasible family exists.
2. `ideas/rejected/ECDLP-IDEA-376_eppstein_sidetrack_source_path_router_hypothesis.md` — ranked paths consume a supplied graph and optimizer state.
3. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — compact feasibility needs an endpoint compiler.
4. `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md` — ranked unranking still charges source representation and outputs.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted predicate and replay owner.

## Closest primary literature

- Lawler, [A Procedure for Computing the K Best Solutions](https://doi.org/10.1287/mnsc.18.7.401), ranks solutions of a supplied discrete optimization instance using an optimizer.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not provide the compact feasible set or ranking gap.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

The title is distinct but the information flow is a solver/enumerator merge with IDEAs
343/376; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, binary variables, constraints, objective, optimizer, tie-breaking, restrictions, signs, strata, and verifier.
2. Compile target-independent state within `B^(9/4+o(1))`; forbid source catalogues, target-trained objectives, scalar labels, and hidden Query2P1 calls.
3. For each known-log target, solve and partition subproblems until a tuple appears, replay occurrences, and verify point equality.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log while charging all earlier outputs and failures.
5. Reuse identical state for 100 fresh `R=Q+[t]P` targets, recover tuples, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge compiler, optimizer calls, partitions, queue, duplicates, `K` outputs, density, replay, rank, logs, bits, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`.
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; `q,o,u` include every optimizer
call, partition, queued candidate, and output before success. Promotion requires
`lambda,mu<=0.45`, `B^(9/4)` setup/state, and `B^(5/4)` fresh caps. Pollard rho
expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Lawler assumes the feasible set and exact optimizer. Encoding endpoint-valid tuples is the
missing predicate, while a generic objective gives no sub-rho bound on the rank of the first
relation. Enumerating `K` candidates costs at least `K` outputs and target restrictions rebuild
the optimization instance.

## Proof track

Prove an endpoint-only feasible encoding, a target-uniform ranking gap, exact negative
semantics, signed inverse, and complete costs within both caps.

## Disproof track

Find one source-bearing constraint, a relation of rank `>=N^0.50`, a false feasible solution,
target-specific objective, exponential queue, lost occurrence, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy 0/1 instance with a unique labelled optimum.
- Negative: adversarial ranking with the valid tuple last, ties, empty fibres, repeated signs, and blind targets.
- Baselines: reverse search, Eppstein sidetracks, Query2P1, rho, and BSGS.
- Controls remain toy and model-bound.

## Quantitative promotion and falsification gates

- Promote only with a proved rank bound, exact all-strata feasibility, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on supplied feasibility, one misrank/missed tuple, unpaid output, cap failure, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o07_optimizer_compiler_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o07_adversarial_rank_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o07_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This rejects only the transplant, not Lawler ranking. Claims remain toy, heuristic,
model-bound, and novelty-unverified; no run or breakthrough is claimed.

## Exactly one next executable action

1. Write the endpoint feasibility and objective maps and either prove a uniform sub-rho relation-rank bound or preserve the smallest instance with a late valid tuple.
