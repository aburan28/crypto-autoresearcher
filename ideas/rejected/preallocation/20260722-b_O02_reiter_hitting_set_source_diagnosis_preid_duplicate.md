# Pre-ID duplicate draft — Reiter hitting-set source diagnosis

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O02`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_conflict_oracle_and_hypergraph_search`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a minimal hitting set or valid relation is not an ECDLP result.

## Falsifiable hypothesis

Endpoint restrictions admit a compact conflict oracle whose Reiter hitting-set tree
enumerates exactly the minimal signed factor-base supports of a target fibre, enabling
verified relation rows, complete factor logs, and fresh blind descent below rho and BSGS.

## Mechanism-new operation

Reiter's HS-tree, with the Greiner–Smith–Wilkerson pruning correction, branches on elements
of supplied minimal conflicts to enumerate minimal diagnoses. It counts only if conflicts
are derived from public endpoints without solving the source problem and every diagnosis
replays an ordered signed occurrence tuple.

## Assumptions

1. Conflict generation is endpoint-only and cheaper than the desired source query.
2. Minimal diagnoses are biconditional with exact five-source decompositions.
3. The tree preserves signs, multiplicities, order, and all exceptional curve strata.
4. Empty fibres have a complete certificate within the online cap.
5. Known-log and masked targets use the same frozen model and branching policy.

## Semantic fingerprint

`public_endpoint_conflict_oracle | Reiter_HS_tree_minimal_diagnoses | exact_restricted_support | signed_tuple_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and replay frontier.
2. `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md` — compact constraints require an endpoint compiler.
3. `ideas/rejected/ECDLP-IDEA-137_matroid_representative_completion_kernel_hypothesis.md` — supplied extension predicates do not create endpoint sources.
4. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — hypergraph access already exposes source incidence.
5. `ideas/rejected/preallocation/20260722-a_N02_davis_putnam_source_resolution_elimination_preid_duplicate.md` — clause reasoning begins after a target formula exists.

## Closest primary literature

- Reiter, [A Theory of Diagnosis from First Principles](https://doi.org/10.1016/0004-3702(87)90062-2), introduces the supplied-conflict diagnosis framework and HS-tree.
- Greiner, Smith, and Wilkerson, [A Correction to the Algorithm in Reiter's Theory of Diagnosis](https://doi.org/10.1016/0004-3702(89)90079-9), repairs pruning that can otherwise miss diagnoses.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives equations but not the compact conflict oracle.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison control.

The named transplant is title-distinct but semantically a supplied-constraint/hypergraph
solver; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, decks, signs, strata, conflict language, HS-tree ordering, restrictions, and point verifier.
2. Compile endpoint-derived target-independent state within `B^(9/4+o(1))`; forbid supplied conflicts, source hyperedges, discrete-log labels, and target advice.
3. For each known-log target, generate conflicts, enumerate one minimal diagnosis, reconstruct signed occurrences, and verify point equality before retaining the row.
4. Retain at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve all factor logs while charging failed diagnoses and dependencies.
5. Reuse identical state for 100 fresh `R=Q+[t]P` targets, recover tuples, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` every time.
6. Charge conflict calls, tree nodes, duplicates, self-reduction, output, densities, verification, rank, algebra, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`. Use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, with every conflict-oracle call
inside `q`. Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`,
and fresh work/workspace `<=B^(5/4+o(1))`. Pollard rho expected time and BSGS
time/memory have exponent `0.50`.

## Likely fatal obstruction

The conflict oracle must already know which partial sources cannot extend to the target,
which is the missing restricted predicate. HS-tree rearranges supplied conflicts; minimal
hitting sets need not have size five, preserve signs, or satisfy elliptic equality, and the
diagnosis family can be exponential.

## Proof track

Prove a compact endpoint-derived conflict system whose minimal diagnoses are exactly the
all-strata signed source tuples and whose oracle plus enumeration satisfies the caps.

## Disproof track

Find one conflict requiring a completion query, one diagnosis not yielding a tuple, one
tuple missed by minimality, an exponential tree, a restriction rebuild, or exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy diagnosis model whose unique diagnosis names five labelled occurrences.
- Negative: duplicate conflicts, nonminimal valid tuples, empty fibres, repeated points, and blind targets.
- Baselines: DPLL/CDCL, explicit hypergraph transversals, Query2P1, rho, and BSGS.
- Controls remain toy and model-bound.

## Quantitative promotion and falsification gates

- Promote only with exact all-strata biconditionality, four frozen sizes, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on a supplied conflict, missed/false tuple, lost provenance, incomplete negative, cap violation, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o02_conflict_oracle_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o02_diagnosis_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o02_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not diagnosis or hitting-set enumeration. Claims remain toy,
heuristic, model-bound, and novelty-unverified; no run or breakthrough is claimed.

## Exactly one next executable action

1. Write the conflict-oracle specification and either prove it is endpoint-only and source-biconditional or preserve its first circular completion query.
