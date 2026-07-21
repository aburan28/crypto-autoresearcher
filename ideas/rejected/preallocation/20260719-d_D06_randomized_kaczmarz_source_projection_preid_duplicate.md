# Pre-ID duplicate draft — Randomized-Kaczmarz source projection

## Status and claim labels

- Prospect: `20260719-d-D06`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `randomized_linear_projection` / `conservative` / pre-ID screen
- State: `merged_rejected_supplied_linear_system_and_approximate_residual`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Lift signed elliptic partial-sum compatibility to a sparse consistent linear system whose rows can be sampled endpoint-only. Randomized Kaczmarz projections would converge to a sparse indicator of one source tuple, yielding exact restricted existence, relation rows, factor logs, and fresh blind descent below rho and BSGS.

## Mechanism-new operation

Randomized Kaczmarz projects the iterate onto a randomly selected row hyperplane with probability proportional to row norm. It counts only if the exact sparse system and row sampler are generated without source enumeration and convergence yields an exact occurrence rather than an approximate vector; changing the linear solver is a control.

## Assumptions

1. A sub-gate public linearization is consistent exactly when a signed relation exists on every chart.
2. Matrix/row construction, row-norm distribution, condition number, precision, iterations, restrictions, rounding, replay, rank, logs, descent, bit time, and memory are charged.
3. An exact source inverse follows from the limit without a dense dictionary or post-hoc selector.
4. One frozen system/operator serves known-log and fresh scalar-blind targets.
5. No supplied relation matrix, approximate zero, dense lift, scalar-labelled variable, or solver-only improvement is admitted.

## Semantic fingerprint

`endpoint_sparse_linearization | norm_sampled_Kaczmarz_projections | exact_consistency_and_support | iterate_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: the missing operation is exact restricted support.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a public exact source-resolving circuit is absent.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: source rows cannot be assumed as linear input.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-MX-1478`: exact transition linearizations become dense on composition.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1479`: tested public feature spaces do not recover factor logs.

## Closest primary literature

- Strohmer and Vershynin, [A randomized Kaczmarz algorithm with exponential convergence](https://doi.org/10.1007/s00041-008-9030-4), analyzes Euclidean row projections over real/complex supplied consistent systems with expected squared-norm convergence; it does not give exact finite-field support or build elliptic source rows.
- Wiedemann, [Solving sparse linear equations over finite fields](https://doi.org/10.1109/SFCS.1986.37), is the occupied sparse-linear/Krylov neighborhood after a matrix is represented.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) set the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, variables, row sampler, precision/exact arithmetic, restrictions, and verifier.
2. Construct target-independent sparse operator state within `B^(9/4+o(1))` without relation-row materialization.
3. Decide exact restricted consistency and recover five labelled occurrences on known-log targets.
4. Collect at least `B` independent verified relations, preserve failures/dependencies, and solve factor-base logarithms.
5. Reuse unchanged state for fresh scalar-blind `Q+[t]P`, recover/verify a source vector, remove `t`, and verify `[x]P=Q`.
6. Charge row generation, sampling, all projections, conditioning/precision, negative queries, replay, rank, logs, descent, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge exact operator/row construction, norm-sampling advice, lifted variables, and reusable state; let `q,q_m` charge target rows, every projection/iteration, precision or field simulation, exact support certification, restrictions, rounding, bisection, and replay. Let `delta,delta_t` be reciprocal verified relation/target success after convergence and support checks, `o` output, `r` verified independent-rank credit, `u` nonuniqueness/conditioning ambiguity plus failure amplification/restarts, and `ell,ell_m` factor-log time/state.

With `B=N^beta`, `beta=1/5`, require `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`, `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, total fresh row/projection/certification/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Rho and BSGS controls have exponent `0.50`; supplied matrices, real/complex-to-finite-field translation, precision, and exactification are charged.

## Likely fatal obstruction

Kaczmarz accelerates Euclidean solution only after matrix rows are supplied. A faithful row set or row sampler encodes the missing source incidences; nonlinear elliptic addition needs a dense/growing lift, and expected norm convergence cannot certify exact finite-field support. Consistency alone also neither selects a unique solution nor proves it is a sparse source indicator. This merges with IDEAs `056/267/367/372/387`, pre-ID `B10/B11/C06`, and dense-state receipts.

## Proof track

Prove a bounded exact endpoint-only linearization, source-free row sampler, exact support inverse, favorable conditioning/iteration count, and complete descent costs.

## Disproof track

Expose one source-bearing row, nonlinear/dense closure, a field/domain mismatch, nonunique consistent solutions, finite-precision false support, ambiguous inverse, or complete exponent outside the gates.

## Positive and negative controls

- Positive: a supplied sparse consistent system with a planted one-sparse solution.
- Negative: nonunique consistent systems with distinct sparse supports, identical low-order projections with different exact supports, ill-conditioned systems, inconsistent targets, restrictions, exceptional charts, and blind targets.
- Baselines: IDEAs `056/267/367/372/387`, pre-ID `B10/B11/C06`, exact sparse solvers, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only rows, exact all-strata support/replay, proven iteration and precision costs, `1,000` independent rows, `100` blind descents, and `lambda,mu<=0.45`.
- Falsify on one supplied source row, one approximate/exact mismatch, target rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d06_row_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d06_projection_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d06_cost_analysis.md`

## Interpretation boundary

This rejects the transplant, not randomized Kaczmarz. Convergence on a planted linear system or a correct approximate residual is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d06_row_provenance.md` and symbolically expand every proposed row and sampling weight into its endpoint/source dependencies.
