# Pre-ID duplicate draft — Ben-Or–Tiwari sparse source interpolation

## Status and claim labels

- Prospect: `20260719-b-B02`; no canonical ID allocated
- Class / risk / lane: `algebraic_interpolation` / `representation-changing` / representation-changing pre-ID screen
- State: `merged_rejected_black_box_or_sparse_support_assumed`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; breakthrough claim **none**

## Falsifiable hypothesis

Encode the target-labelled five-deck relation indicator as a sparse multivariate polynomial, evaluate it at a short geometric progression, and apply Ben-Or–Tiwari interpolation to recover a monomial whose exponent vector is the signed source tuple. The black-box evaluator and interpolation fit the P1553 caps and support blind target descent.

## Mechanism-new operation

The native operation recovers a promised sparse polynomial from black-box evaluations by exponential substitution and recurrence/root recovery. It counts only if both the sparse polynomial and its evaluations are built from endpoint state without already solving exact source existence.

## Assumptions

1. The exact coloured relation indicator has `N^o(1)` effective monomial sparsity after a public, target-uniform encoding.
2. Each black-box evaluation is endpoint-derived and costs within the fresh-query cap on every chart and restriction.
3. Construction, evaluations, recurrence, roots/discrete exponent decoding, output, rank, logs, descent, and memory are charged.
4. One recovered monomial gives real signed occurrences, not only a relation value or coefficient.
5. No explicit support table, scalar character oracle, post-hoc sparsifier, or dense eliminant is admitted.

## Semantic fingerprint

`endpoint_black_box | ben_or_tiwari_sparse_interpolation | exponent_vector_source_recovery | exact_restricted_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ECFG-H673` — structure must improve exact relation supply.
2. `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION` — aggregate concentration did not supply sources.
3. `ECFG-H675` — an exact public source-resolving circuit remains missing.
4. `ECFG-H676` — source-fibre compilation restores materialization.
5. `P1476` — charge membership, output, rank, descent, and memory together.

All five are exact entries in `inputs/ledger_inventory.json`.

## Closest primary literature

- Ben-Or and Tiwari, [A Deterministic Algorithm for Sparse Multivariate Polynomial Interpolation](https://doi.org/10.1145/62212.62241), assumes black-box access and sparse support; it does not construct an ECDLP relation oracle.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but not sparse labelled support.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), remains the matched baseline.

## Complete factor-base-to-target-descent path

1. Freeze the curve, five signed decks, all exceptional charts, encoding, restrictions, and verifier.
2. Build the target-independent evaluation/interpolation state within `B^(9/4+o(1))` without source-product materialization.
3. For known-log targets, evaluate under arbitrary restrictions, interpolate exact support, and recover five occurrences with verification.
4. Collect at least `B` independent verified rows and solve factor-base logs, retaining failures and dependencies.
5. Reuse the same state on fresh scalar-blind `Q+[t]P`, recover a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge black-box construction/calls, field extensions, exponent decoding, output, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Setup/state must be `<=B^(9/4+o(1))`, fresh restricted query plus replay `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50` baselines.

## Likely fatal obstruction

The natural indicator has one monomial per valid occurrence and generic support is not promised sparse across the `B`-target campaign; constructing or evaluating it exactly is Query2P1/source search. Kronecker exponents also require a large decoding range, and recovering exponents can import a discrete-log problem. This merges with IDEAs `078/105/182/209/266`.

## Proof track

Prove a target-uniform sparse encoding and an endpoint-only evaluator, bounded exponent decoding, exact occurrence replay, and the complete descent gates.

## Disproof track

Show dense support, one evaluation that invokes source search, exponent collisions/hidden discrete logs, loss on a restriction, or a complete exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied sparse polynomial with planted source monomials must interpolate exactly.
- Negative: dense/cancelling indicators, equal evaluations with different source supports, repeated charts, no-hit restrictions, and fresh blind targets.
- Baselines: IDEAs `078/105/182/209/266`, P1553 R4, dense interpolation, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only after a theorem bounds support/evaluation/decoding, plus `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one uncharged black-box/source oracle, support beyond the cap, source mismatch, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-b/b02_source_obligations.md`
- `ideas/rejected/preallocation/artifacts/20260719-b/b02_support_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260719-b/b02_cost_analysis.md`

## Interpretation boundary

Sparse-polynomial interpolation correctness is not relation collection or ECDLP progress; every finite check remains toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-b/b02_source_obligations.md` with an explicit black-box circuit and symbolic support bound before any fixture is generated.
