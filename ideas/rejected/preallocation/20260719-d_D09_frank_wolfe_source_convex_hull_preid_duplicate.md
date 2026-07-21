# Pre-ID duplicate draft — Frank–Wolfe source convex hull

## Status and claim labels

- Prospect: `20260719-d-D09`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `conditional_gradient_sparse_mixture` / `high-risk` / pre-ID screen
- State: `merged_rejected_source_linear_minimization_oracle_and_fractional_mixture`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Embed signed elliptic source tuples as vertices of a public convex body whose target lies in the body exactly when a relation exists. Frank–Wolfe conditional-gradient steps would call an endpoint-only linear minimization oracle and produce a sparse vertex mixture from which one exact tuple, rank-complete relations, and fresh blind descent can be recovered below rho and BSGS.

## Mechanism-new operation

Frank–Wolfe replaces projected gradients by repeated linear minimization over a supplied compact convex domain, producing sparse convex combinations. It counts only if the domain and oracle are endpoint-derived and exact membership/source recovery follows from finite iterations; using a source optimizer or approximate rounding is a control.

## Assumptions

1. A bounded-dimensional convex embedding is exact for every signed, repeated, tangent, vertical, infinity, and nonreduced source stratum.
2. Domain/oracle construction, curvature, iterations, precision, restrictions, rounding, replay, rank, logs, descent, bit time, and memory are charged.
3. Sparse convex mixtures cannot fractionally combine incompatible sources into a false target.
4. One frozen domain serves known-log and fresh scalar-blind targets without target-trained features.
5. No explicit vertex table, post-hoc selector, SDP/LP solver substitution, dense resultant, or scalar-labelled embedding is admitted.

## Semantic fingerprint

`endpoint_source_convex_body | Frank_Wolfe_linear_minimization_steps | exact_membership_not_approximation | sparse_vertices_to_signed_occurrence | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted support is the residual.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a public exact source circuit is missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: the vertex/source generator cannot be assumed.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: an explicit vertex oracle is source incidence.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1479`: compact feature representations have not yielded factor logs.

## Closest primary literature

- Frank and Wolfe, [An algorithm for quadratic programming](https://doi.org/10.1002/nav.3800030109), optimizes over a supplied convex feasible region using linear subproblems; it does not construct an exact discrete-source polytope.
- Jaggi, [Revisiting Frank–Wolfe: projection-free sparse convex optimization](https://proceedings.mlr.press/v28/jaggi13.html), formalizes finite-iteration sparsity and approximate primal gaps, not exact rare support.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) set the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, embedding, convex body, oracle, restrictions, rounding rule, and verifier.
2. Construct target-independent domain/oracle state within `B^(9/4+o(1))` without materializing source vertices.
3. On known-log targets, decide exact restricted membership and recover five verified labelled occurrences.
4. Collect at least `B` independent rows, preserve failed/ambiguous iterates, and solve factor-base logarithms.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, recover/verify a vertex, remove `t`, and verify `[x]P=Q`.
6. Charge oracle construction/calls, all iterations, precision/rounding, negative queries, replay, rank, logs, descent, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge construction/storage of the convex embedding, feasible-domain representation, linear-minimization oracle, and reusable curvature data; let `q,q_m` charge target objective formation, every oracle/line-search iteration, precision, exact discrete-membership certification, restrictions, rounding, bisection, and replay. Let `delta,delta_t` be reciprocal verified integer relation/target success, `o` output, `r` verified independent-rank credit, `u` fractional/source ambiguity plus convergence amplification/restarts, and `ell,ell_m` factor-log time/state.

For `B=N^beta`, `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Setup/state must be `<=B^(9/4+o(1))`, fresh oracle/iteration/exactification/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho time and BSGS time/memory remain exponent `0.50` controls. Source-vertex optimization, full precision, rounding, and target-trained embeddings are charged.

## Likely fatal obstruction

The linear minimization oracle over source vertices is already a source selector. Convexification forgets integrality: mixtures of incompatible tuples can match an endpoint even when no tuple does, and driving an approximate gap to an exact finite-field zero may require source-sized precision/iterations. This merges with IDEAs `191/335/349/367/396` and pre-ID `B03/B10`.

## Proof track

Construct an endpoint-only exact convex embedding and oracle, prove integrality and a finite exact convergence/source theorem under restrictions, then close full costs.

## Disproof track

Expose one source-bearing oracle call, a convex-hull/integer-support mismatch, precision blowup, or complete exponent outside the gates.

## Positive and negative controls

- Positive: a supplied simplex with a planted vertex target and exact linear oracle.
- Negative: a target in the convex hull but outside the discrete vertex set, equal low-order features with different sources, restrictions, exceptional charts, and blind targets.
- Baselines: IDEAs `191/335/349/367/396`, pre-ID `B03/B10`, explicit vertex LP, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only domain/oracle construction, exact integer/source equivalence and replay, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source oracle, one fractional false positive, target-trained embedding, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d09_oracle_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d09_fractional_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d09_cost_analysis.md`

## Interpretation boundary

This rejects the discrete-source transplant, not Frank–Wolfe optimization. A decreasing primal gap or sparse toy mixture is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d09_oracle_provenance.md` and state exactly how one linear-minimization call avoids enumerating or selecting source vertices.
