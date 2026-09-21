# Pre-ID duplicate draft — Frequent-Directions source sketch

## Status and claim labels

- Prospect: `20260719-b-B11`; no canonical ID allocated
- Class / risk / lane: `streaming_matrix_sketch` / `conservative` / conservative pre-ID screen
- State: `merged_rejected_supplied_row_stream_and_covariance_error`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment; no contract
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; no breakthrough claim

## Falsifiable hypothesis

Stream endpoint-incidence rows through Frequent Directions, shrink low singular directions, and retain a deterministic sketch whose covariance distinguishes every exact target/source relation under restrictions. A sketch direction can be replayed to signed occurrences and complete blind descent below rho.

## Mechanism-new operation

The native operation repeatedly shrinks singular values of a supplied row stream to preserve covariance approximately. It counts only if the row stream is endpoint-derived below the gate and the sketch preserves rare exact support and provenance.

## Assumptions

1. A compact endpoint-derived row stream represents the full signed/chart-complete source problem.
2. Covariance error below a public threshold implies exact existence and returns occurrences.
3. Row generation, SVD/shrink steps, restrictions, output, rank, logs, blind descent, and memory are charged.
4. The same sketch serves known-log and fresh masked targets without replaying the source stream.
5. No explicit source rows, approximate-only promotion, post-hoc direction, or uncharged pass is admitted.

## Semantic fingerprint

`endpoint_incidence_row_stream | frequent_directions_singular_shrinkage | exact_rare_support_decision | source_row_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ECFG-H673` — sketch structure must change exact supply.
2. `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION` — aggregate statistics failed source transfer.
3. `ECFG-H675` — exact source resolution is the missing operation.
4. `ECFG-H676` — explicit source rows restore materialization.
5. `P1476` — membership/output/rank/descent/memory costs are joint.

## Closest primary literature

- Ghashami, Liberty, Phillips, and Woodruff, [Frequent Directions: Simple and Deterministic Matrix Sketching](https://doi.org/10.1137/15M1009718), gives spectral/covariance approximation for a supplied row stream; it does not preserve arbitrary singleton support or row identities.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies no compact source-row stream.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, row grammar/order, sketch size, restrictions, and verifier.
2. Build target-independent sketch within `B^(9/4+o(1))` without source-product materialization.
3. On known-log targets, decide exact restricted existence and replay/verify five occurrences.
4. Collect `B` independent rows and solve factor logs, retaining misses/dependencies.
5. Reuse the sketch on `Q+[t]P`, recover a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge row generation/passes, shrink operations, negative queries, output, rank, logs, descent, precision, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require setup/state `<=B^(9/4)`, fresh online `<=B^(5/4)`, and `lambda,mu<=0.45`; rho/BSGS are exponent `0.50` controls.

## Likely fatal obstruction

Frequent Directions consumes the row stream that the ECDLP route needs to avoid constructing, then preserves quadratic forms only up to additive error. A rare exact relation can be erased by a shrink step and provenance is not retained. This merges with IDEAs `231/324/347/367/387`.

## Proof track

Give an endpoint-only row generator, an exact special-family preservation theorem with row replay, and full descent/cost bounds.

## Disproof track

Plant/delete one low-energy relation below the covariance tolerance, expose a source-bearing row stream, or charge passes/SVD above a cap.

## Positive and negative controls

- Positive: a supplied low-rank stream with a large planted direction and retained row label.
- Negative: low-energy singleton rows, identical covariance sketches/different support, restrictions, chart exceptions, and blind targets.
- Baselines: IDEAs `231/324/347/367/387`, explicit row streaming, Query2P1, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact support/provenance preservation, `1,000` independent rows, `100` blind descents, and all caps/exponents.
- Falsify on one missed source, supplied row stream, target replay, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-b/b11_source_obligations.md`
- `ideas/rejected/preallocation/artifacts/20260719-b/b11_covariance_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260719-b/b11_cost_analysis.md`

## Interpretation boundary

Streaming covariance accuracy is not exact relation discovery, scalar recovery, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-b/b11_source_obligations.md` and classify row generation, shrink loss, and provenance requirements symbolically.
