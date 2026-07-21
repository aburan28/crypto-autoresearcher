# Pre-ID duplicate draft — ROBDD Shannon source compiler

## Status and claim labels

- Prospect: `20260719-b-B06`; no canonical ID allocated
- Class / risk / lane: `decision_diagram` / `conservative` / conservative pre-ID screen
- State: `merged_rejected_predicate_compiler_and_unbounded_diagram`
- Evidence: complete corpus/ledger and primary-literature review only; no experiment; no contract
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; no breakthrough claim

## Falsifiable hypothesis

Apply Shannon expansion to the signed source-index bits, reduce isomorphic subgraphs under a frozen variable order, and obtain a compact ROBDD for exact five-sum existence. Restriction follows edges and a satisfying path replays occurrences within the P1553 gates.

## Mechanism-new operation

The native operation canonically reduces an ordered Boolean decision graph for a supplied Boolean function. It counts only if the ECDLP predicate can be compiled from endpoints below the cap without querying or enumerating its accepting assignments.

## Assumptions

1. A target-independent variable order yields `B^(9/4+o(1))` nodes for every admitted curve/deck family.
2. Compilation and apply operations use endpoint-derived primitives, not Query2P1 or an answer table.
3. Every restriction and blind target reuses state, and a satisfying path returns signed/chart-complete occurrences.
4. Negative branches, target updates, node creation, output, rank, logs, descent, and memory are charged.
5. No successful-instance variable reorder, post-hoc reduction, or explicit truth table is admitted.

## Semantic fingerprint

`public_endpoint_boolean_grammar | robdd_shannon_reduction | exact_restricted_satisfiability | satisfying_assignment_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ECFG-H673` — structure must improve exact supply.
2. `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION` — summaries did not transfer exact witnesses.
3. `ECFG-H675` — a compact exact source-resolving circuit is precisely the open object.
4. `ECFG-H676` — explicit source-fibre compilation restores materialization.
5. `P1476` — full membership/output/rank/descent/memory accounting is required.

## Closest primary literature

- Bryant, [Graph-Based Algorithms for Boolean Function Manipulation](https://doi.org/10.1109/TC.1986.1676819), gives ordered reduced diagrams for supplied Boolean functions and explicitly allows exponential worst-case size.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not compile the exact source predicate.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), supplies the matched baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, Boolean grammar, variable order, restriction/update policy, and verifier.
2. Compile target-independent nodes within `B^(9/4+o(1))` without source enumeration.
3. For known-log targets, restrict the diagram, decide existence, and replay/verify five occurrences.
4. Collect at least `B` independent rows and solve factor logs, retaining misses/dependencies.
5. Reuse unchanged state for `Q+[t]P`, recover a path/tuple, remove `t`, and verify `[x]P=Q`.
6. Charge compilation/apply, target update, negative paths, output, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, require
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)<=0.45` and
`mu=max(a_m,q_m,beta+o,ell_m,u)<=0.45`, `0<=r<=o`, plus setup/state `<=B^(9/4)` and fresh online `<=B^(5/4)`. Rho/BSGS remain `0.50` baselines.

## Likely fatal obstruction

ROBDDs compress a supplied predicate; building the terminal truth values is the missing exact five-sum oracle. Generic diagrams can be exponential and a fresh target changes the function. This is a direct representation variant of pre-ID ZDD `A04` and merges with IDEAs `120/337/371/377/397`.

## Proof track

Give an endpoint-only bounded-size compiler and variable order, prove target updates/restrictions preserve exact source replay, and close full descent costs.

## Disproof track

Find an exponential family, one terminal requiring Query2P1, a fresh-target rebuild, a satisfying/source mismatch, or a cap violation.

## Positive and negative controls

- Positive: a supplied compact Boolean function with a planted satisfying assignment.
- Negative: hard variable orders, single-assignment toggles, absent targets, charts, arbitrary restrictions, and blind targets.
- Baselines: pre-ID `A04`, IDEAs `120/337/371/377/397`, explicit truth tables, Query2P1, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with a uniform node bound/compiler, exact replay, `1,000` independent rows, `100` blind descents, and all exponent/cap gates.
- Falsify on one predicate oracle, exponential node family, target rebuild, source mismatch, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-b/b06_source_obligations.md`
- `ideas/rejected/preallocation/artifacts/20260719-b/b06_order_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260719-b/b06_cost_analysis.md`

## Interpretation boundary

The decision-diagram representation remains useful on supplied compact functions; correctness or toy compression is not an ECDLP breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-b/b06_source_obligations.md` and expand one ROBDD terminal-construction path without a membership oracle.
