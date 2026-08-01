# Pre-ID duplicate draft — Sinkhorn–Knopp source coupling

## Status and claim labels

- Prospect: `20260719-b-B03`; no canonical ID allocated
- Class / risk / lane: `matrix_scaling` / `conservative` / conservative pre-ID screen
- State: `merged_rejected_supplied_incidence_and_approximate_marginals`
- Evidence: literature and complete-corpus theorem screen only; no experiment ran; no contract
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; no breakthrough claim

## Falsifiable hypothesis

Build a public nonnegative partial-sum compatibility matrix, alternately scale rows and columns to prescribed marginals, and use the resulting balanced coupling to isolate an exact target-compatible source pair that self-reduces to five occurrences. Construction and all downstream work beat rho/BSGS.

## Mechanism-new operation

The native operation alternately applies positive diagonal row/column scalings to a supplied nonnegative matrix. It counts only if it constructs or exposes exact source incidence from endpoints; balancing an explicit compatibility matrix is a control.

## Assumptions

1. A target-independent nonnegative matrix below the setup cap encodes exact signed/chart-complete five-sum existence.
2. Scaling preserves a discrete exact nonzero needed for occurrence replay, not merely approximate marginals.
3. Matrix construction, iterations, precision, restrictions, output, rank, logs, blind descent, and memory are charged.
4. The same state serves calibration and fresh masked targets without target-fitted rescaling advice.
5. No explicit `B^3` incidence, post-hoc threshold, or uncharged entry oracle is admitted.

## Semantic fingerprint

`public_endpoint_matrix | sinkhorn_knopp_diagonal_scaling | balanced_exact_support_locator | signed_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ECFG-H673` — aggregate energy must alter exact relation supply.
2. `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION` — aggregate mass did not give exact sources.
3. `ECFG-H675` — source-resolving public circuitry is missing.
4. `ECFG-H676` — explicit source-fibre matrices hit materialization.
5. `P1476` — complete membership/output/rank/descent/memory costs are mandatory.

These resolve in `inputs/ledger_inventory.json`.

## Closest primary literature

- Sinkhorn and Knopp, [Concerning Nonnegative Matrices and Doubly Stochastic Matrices](https://doi.org/10.2140/pjm.1967.21.343), scales a supplied nonnegative matrix and does not create its zero pattern.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations, not the scaled incidence matrix.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), is the matched baseline.

## Complete factor-base-to-target-descent path

1. Freeze signed decks, charts, restrictions, matrix grammar, precision policy, and verifier.
2. Construct target-independent state within `B^(9/4+o(1))` without enumerating source incidence.
3. For known-log targets, answer exact restricted existence from balanced state and replay five occurrences with charged bisection/verification.
4. Collect `B` independent rows and solve factor logs, retaining failures and rank defects.
5. Reuse unchanged state on `Q+[t]P`, recover a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge entry generation, iteration/precision, restrictions, misses, output, rank, logs, descent, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, require

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)<=0.45`,

`mu=max(a_m,q_m,beta+o,ell_m,u)<=0.45`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, and fresh online work/state `<=B^(5/4+o(1))`. Rho and BSGS are `0.50` baselines.

## Likely fatal obstruction

Positive diagonal scaling preserves the supplied zero pattern: it cannot reveal an absent compatibility edge. Constructing entries is the missing exact incidence operation, while approximate marginal balance can change negligibly when a unique relation is inserted or deleted. This merges with IDEAs `143/231/332/349/396`.

## Proof track

Construct a compact endpoint-only matrix, prove an exact support biconditional and restriction-stable replay, control precision, and close the complete cost path.

## Disproof track

Toggle one rare relation without materially changing scaled marginals, identify an entry oracle/source table, or show matrix/iteration/precision cost beyond a gate.

## Positive and negative controls

- Positive: a supplied scalable matrix with one labelled admissible edge.
- Negative: identical marginals with different zero patterns, unique-edge deletion, dense/no-support cases, chart exceptions, restrictions, and blind targets.
- Baselines: IDEAs `143/231/332/349/396`, explicit incidence, Query2P1, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact—not approximate—support replay, `1,000` independent rows, `100` blind descents, precision included, and both exponent/cap gates.
- Falsify on any supplied entry oracle, one support mismatch, target-dependent matrix rebuild, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-b/b03_source_obligations.md`
- `ideas/rejected/preallocation/artifacts/20260719-b/b03_support_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260719-b/b03_cost_analysis.md`

## Interpretation boundary

This is a scoped transplant rejection; matrix-scaling convergence, toy balance, or a valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-b/b03_source_obligations.md` and expand every matrix entry and zero-pattern decision into endpoint operations.
