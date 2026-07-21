# Pre-ID duplicate draft — Benders source-cut generation

## Status and claim labels

- Prospect: `20260719-d-D07`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `projection_cut_decomposition` / `conservative` / pre-ID screen
- State: `merged_rejected_source_recourse_oracle_and_cut_materialization`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Treat fifth-label choices as complicating master variables and the remaining four-source elliptic completion as a recourse problem. Endpoint-derived Benders feasibility cuts would converge to exact restricted target-label support, after which a recourse certificate would replay a signed source tuple for factor logs and blind descent below rho and BSGS.

## Mechanism-new operation

Benders decomposition projects out recourse variables and iteratively adds dual feasibility/optimality cuts to a master problem. It counts only if the recourse separation oracle and returned cuts are constructed endpoint-only below the gate; calling Query2P1 or a source solver as the subproblem is a control.

## Assumptions

1. Complete signed elliptic compatibility admits a compact master/recourse formulation with valid dual certificates on every chart.
2. Formulation, subproblem solves, cut coefficients, master iterations, restrictions, recourse replay, rank, logs, descent, bit time, and memory are charged.
3. Cuts remain valid and sufficient under arbitrary dyadic source restrictions.
4. One frozen formulation serves known-log and fresh scalar-blind targets without target-trained cuts.
5. No source oracle, explicit tuple columns, dense resultant, post-hoc selector, or uncharged separation call is admitted.

## Semantic fingerprint

`fifth_label_master_projection | Benders_recourse_feasibility_cuts | exact_restricted_master_support | recourse_certificate_to_signed_sources | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact fifth-label support is the residual itself.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: the compact source-resolving circuit is missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: a source-returning recourse oracle cannot be assumed.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: explicit recourse rows/columns cross the source boundary.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1477`: dense represented forward/backward state misses the query cap.

## Closest primary literature

- Benders, [Partitioning procedures for solving mixed-variables programming problems](https://doi.org/10.1007/BF01386316), alternates a supplied master with supplied recourse subproblems and dual cuts.
- Geoffrion, [Generalized Benders decomposition](https://doi.org/10.1007/BF00934810), extends convex nonlinear master/dual-cut decomposition; those convex dual cuts do not by themselves certify exact integer recourse or create elliptic source separation.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) set the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, master/recourse variables, cut rules, restrictions, and verifier.
2. Build target-independent formulation/state within `B^(9/4+o(1))` without source-column materialization.
3. On known-log targets, generate enough valid cuts to decide exact restricted support and replay five verified occurrences.
4. Collect at least `B` independent rows, preserve failed subproblems/dependencies, and solve factor-base logarithms.
5. Reuse unchanged formulation for fresh scalar-blind `Q+[t]P`, recover/verify recourse, remove `t`, and verify `[x]P=Q`.
6. Charge every master/subproblem iteration, cut, negative branch, replay, rank, logs, descent, verification, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge the full master/recourse formulation, source-free separation data, initial cuts, and reusable state; let `q,q_m` charge every target/restriction master solve, recourse oracle call, integer exactification, generated cut, negative branch, bisection, and replay. Let `delta,delta_t` be reciprocal verified relation/target success, `o` output, `r` verified independent-rank credit, `u` integrality/recourse ambiguity plus cut-iteration and rebuild overhead, and `ell,ell_m` factor-log time/state.

For `B=N^beta`, `beta=1/5`, require `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`, `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, total fresh formulation/separation/cut/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Rho time and BSGS time/memory are exponent-`0.50`; Query2P1 recourse, integer branch work, accumulated cuts, and target-trained cuts are charged.

## Likely fatal obstruction

The recourse feasibility oracle is exactly restricted four-source completion/Query2P1. Classical Benders cuts certify represented linear/convex recourse; integer recourse needs extra combinatorial machinery and can retain an integrality gap. Any exact formulation either materializes source incidences or accumulates point-separating cuts that reproduce the source table. This merges with IDEAs `199/335/353/365/378` and pre-ID `A10/C04`.

## Proof track

Construct endpoint-only master and recourse separation, prove exact integer/source biconditional and a sub-gate cut bound under restrictions, then close replay and descent.

## Disproof track

Expose one Query2P1/source-bearing subproblem, an integrality gap, exponentially many cuts, or any complete exponent outside the gates.

## Positive and negative controls

- Positive: a supplied block-structured mixed program with planted recourse and exact Benders convergence.
- Negative: equal relaxations with different integer source support, infeasible recourse, adversarial restrictions, exceptional charts, and blind targets.
- Baselines: IDEAs `199/335/353/365/378`, pre-ID `A10/C04`, monolithic source ILP, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only separation, exact integer/source cuts for all restrictions, bounded iterations, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source oracle/cut, one relaxation mismatch, target-trained cut, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d07_recourse_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d07_integrality_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d07_cost_analysis.md`

## Interpretation boundary

This rejects the elliptic decomposition, not Benders optimization. A valid dual cut or solved planted instance is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d07_recourse_provenance.md` and classify the exact information consumed and returned by every proposed separation call.
