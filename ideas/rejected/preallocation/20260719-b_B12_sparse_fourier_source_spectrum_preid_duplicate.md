# Pre-ID duplicate draft — Sparse-Fourier source spectrum

## Status and claim labels

- Prospect: `20260719-b-B12`; no canonical ID allocated
- Class / risk / lane: `spectral_recovery` / `high-risk` / high-risk pre-ID screen
- State: `merged_rejected_sparse_spectrum_or_sample_oracle_assumed`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: every finite check `toy`; extrapolations `heuristic`, `model-bound`, `novelty-unverified`; breakthrough claim **none**

## Falsifiable hypothesis

View the exact target-labelled source indicator as a signal on a public finite index group, use sublinear sparse-Fourier hashing/filtering to recover its heavy spectral coefficients, and invert a coefficient to a signed five-source tuple. Sampling, source replay, factor logs, and blind descent beat rho/BSGS.

## Mechanism-new operation

The native operation hashes Fourier frequencies into bins, filters and estimates a promised sparse/heavy spectrum from sample access. It counts only if the ECDLP signal has proved sparse spectrum, samples are endpoint-derived without Query2P1, and inversion returns source occurrences without a scalar DLP.

## Assumptions

1. A public target-uniform indexing group gives a `k=B^o(1)`-sparse or suitably heavy exact spectrum for generic decks.
2. Time-domain sample access costs within the online cap and does not decide exact source existence itself.
3. Frequency indices can be decoded to signed occurrence labels without scalar characters or an order-`N` dictionary.
4. Samples, filters, collisions, failures, output, rank, logs, blind descent, bit time, and memory are charged.
5. No post-hoc heavy-bin choice, target-specific spectrum, explicit source signal, or approximate-only promotion is admitted.

## Semantic fingerprint

`public_endpoint_signal | sparse_fourier_hash_filter_recovery | exact_spectral_source_locator | signed_occurrence_inversion | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ECFG-H673` — spectral/additive structure must alter exact supply.
2. `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION` — aggregate concentration failed to transfer exact sources.
3. `ECFG-H675` — exact source-resolving circuitry remains missing.
4. `ECFG-H676` — explicit source-fibre sampling/materialization restores the boundary.
5. `P1476` — membership/output/rank/descent/memory costs must be combined.

## Closest primary literature

- Hassanieh, Indyk, Katabi, and Price, [Nearly Optimal Sparse Fourier Transform](https://doi.org/10.1145/2213977.2214029), assumes sample access and Fourier sparsity; it does not establish either property for elliptic source indicators.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no sparse spectrum/source inverse.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), is the matched generic baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, indexing group, sampling/filter policy, restrictions, and verifier.
2. Build target-independent spectral state within `B^(9/4+o(1))` without source-product materialization or discrete logs.
3. On known-log targets, recover exact restricted existence/frequencies and replay five verified occurrences.
4. Collect at least `B` independent rows and solve factor-base logs, retaining misses/collisions/dependencies.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, recover a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge sample generation, filters/hashes, precision/probability, output, rank, logs, descent, verification, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require setup/state `<=B^(9/4+o(1))`, total fresh online `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Rho and BSGS remain exponent `0.50` baselines.

## Likely fatal obstruction

Generic exact relation indicators have no proved sparse/heavy spectrum; character aggregates discard occurrence provenance. Sample access is the missing exact predicate, and interpreting a frequency as a scalar can import the original DLP. This merges with IDEAs `001/048/078/124/224` and CountSketch `347`.

## Proof track

Prove a generic special-family sparsity theorem, endpoint-only sample oracle, collision-safe exact source inversion, and the complete descent/cost gates.

## Disproof track

Show flat/dense spectrum, one sample requiring Query2P1, a frequency/source collision, hidden scalar DLP, or complete exponent/cap violation.

## Positive and negative controls

- Positive: a supplied exactly sparse signal with planted recoverable frequency/source labels.
- Negative: flat random spectra, phase-cancelled sources, equal spectra with different occurrences, charts, restrictions, and blind targets.
- Baselines: IDEAs `001/048/078/124/224/347`, full FFT, Query2P1, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with proved sparse spectrum/sample oracle/source inverse, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one oracle sample, dense spectrum, source ambiguity, scalar DLP, target-specific preprocessing, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-b/b12_source_obligations.md`
- `ideas/rejected/preallocation/artifacts/20260719-b/b12_spectral_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260719-b/b12_cost_analysis.md`

## Interpretation boundary

Sparse-Fourier correctness on a promised signal, a heavy coefficient, or a toy relation is not an ECDLP breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-b/b12_source_obligations.md` and freeze the signal, sample oracle, sparsity bound, and frequency-to-source inverse before any numerical check.
