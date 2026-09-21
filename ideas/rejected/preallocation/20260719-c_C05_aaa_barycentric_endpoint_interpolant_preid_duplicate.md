# Pre-ID duplicate draft — AAA barycentric endpoint interpolant

## Status and claim labels

- Prospect: `20260719-c-C05`; no canonical ID allocated
- Class / risk / lane: `rational_approximation` / `representation-changing` / pre-ID screen
- State: `merged_rejected_supplied_samples_and_approximate_support`
- Evidence: complete-corpus and primary-literature review only; no experiment
- Labels: finite checks `toy`; extrapolations `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Sample an endpoint-derived relation response on public field probes, use adaptive Antoulas–Anderson support selection to build a low-degree barycentric rational interpolant, and recover exact poles/zeros encoding signed source tuples for rank-complete relations and blind descent below rho/BSGS.

## Mechanism-new operation

The AAA operation greedily selects support samples and solves a Loewner-like least-squares problem for a barycentric rational approximant. It counts only if samples are endpoint-only, exact zero support is certified rather than approximated, and poles invert to point occurrences without a source catalogue.

## Assumptions

1. A target-independent endpoint response has bounded rational degree and exact pole/zero biconditional with all relation strata.
2. Probe production, adaptive selection, linear algebra, exactification, restrictions, pole/source inversion, rank, logs, descent, and memory are charged.
3. Numerical or finite-field approximation error cannot turn a nonzero response into a false zero.
4. The frozen response model serves known-log and fresh scalar-blind targets without source-sensitive resampling.
5. No dense resultant, supplied moment oracle, post-hoc pole selector, or explicit tuple evaluation is admitted.

## Semantic fingerprint

`public_endpoint_probe_response | AAA_greedy_barycentric_support | exact_rational_zero_pole_decision | pole_to_signed_source_inverse | blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact target-label common-factor decision is the residual.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-MX-1478`: a one-transition sparse norm becomes dense on composition.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1477`: materialized forward/backward polynomials miss the query boundary.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1479`: public low-dimensional features did not contain factor logs.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: an exact public source-resolving circuit remains missing.

## Closest primary literature

- Nakatsukasa, Sète, and Trefethen, [The AAA Algorithm for Rational Approximation](https://doi.org/10.1137/16M1106122), constructs an approximation from supplied samples.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but not a low-degree response oracle.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), gives the matched baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, probe set, response definition, restrictions, exactifier, and verifier.
2. Construct target-independent samples/interpolant within `B^(9/4+o(1))` without source-product evaluation.
3. On known-log targets, decide exact restricted existence and invert selected poles/zeros to five verified occurrences.
4. Preserve misses/dependencies, collect at least `B` independent rows, and solve factor logs.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, verify a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge sample production, support selection, exactification, output, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; Pollard rho time and BSGS time/memory remain exponent-`0.50` baselines.

## Likely fatal obstruction

AAA starts from supplied response samples and is approximate. Source-sensitive samples require evaluating the hidden tuple sum or a dense aggregate; a low-degree fit can miss a rare exact zero, and poles of an approximant need not be factor points. Exactification restores interpolation/resultant/source cost. This merges with IDEAs `053/078/194/209/267/373` and pre-ID Ben–Or–Tiwari interpolation `B02`.

## Proof track

Derive endpoint-only exact samples, prove bounded degree and zero/pole/source biconditional under restrictions, then close full descent costs.

## Disproof track

Expand sample production, plant an unsampled rare zero, show spurious poles, or derive exactification/state above the gates.

## Positive and negative controls

- Positive: supplied low-degree rational functions with exact planted poles.
- Negative: same sampled values with different rare zeros, noisy/ill-conditioned samples, exceptional charts, restrictions, blind targets.
- Baselines: IDEAs `053/078/194/209/267/373`, pre-ID `B02`, dense interpolation, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact zero-error source replay, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied source sample, one missed/spurious zero, target resampling, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-c/c05_sample_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-c/c05_rational_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260719-c/c05_cost_analysis.md`

## Interpretation boundary

This rejects this transplant, not AAA. A good fit, correct pole on a toy instance, or relation certificate is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-c/c05_sample_provenance.md` and symbolically expand every proposed response probe into charged endpoint and source operations.
