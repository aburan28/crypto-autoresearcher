# ECDLP-IDEA-367 — AMP–Onsager source reconstruction

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_amp_lacks_iid_measurement_channel_and_exact_support_certificate`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired review_required preflight; execution prohibited`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; state-evolution agreement or approximate support is not an ECDLP break.

## Falsifiable hypothesis

Endpoint features of the five-source relation define a public dense measurement channel with a sparse source vector for which approximate message passing (AMP), including the Onsager correction, converges to the exact labelled tuple and supports blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift source membership to a sparse vector, iterate residual/denoising messages with an Onsager correction, and use state evolution to predict exact-support recovery from endpoint measurements**. It is distinct only if the measurement matrix and dictionary are derived without source incidence, the finite-field structured channel lies in a proved universality class, and the output is exact/zero-safe rather than a correlated score.

## Assumptions

1. A target-uniform public measurement ensemble encodes each exact relation tuple sparsely without listing candidate tuples.
2. Its dependencies satisfy a rigorous AMP state-evolution or universality theorem across campaign and blind targets.
3. A denoiser returns exact signed, repeated, singular, infinity, coloured, and ambiguous source labels.
4. False positives/negatives have a deterministic correction under the frozen setup/query and complete-exponent gates.
5. Matrix/dictionary construction, iterations, precision, retries, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_derived_sparse_measurement_channel | AMP_residual_denoising_iteration | Onsager_correction | state_evolution | exact_support_to_point_section | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the measurement dictionary must construct the missing source-resolving circuit.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; arithmetic source-fibre generation remains the missing operation.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; a column per source tuple is the forbidden incidence table.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; materializing partial-source measurements restores cubic work.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; recovery on a supplied exact source matrix is only a control.

## Closest primary literature

- Donoho, Maleki, and Montanari, [Message-passing algorithms for compressed sensing](https://doi.org/10.1073/pnas.0909892106), introduces the Onsager-corrected iteration for sparse signals in known measurement models.
- Bayati and Montanari, [The dynamics of message passing on dense graphs](https://doi.org/10.1109/TIT.2010.2094817), proves state evolution for iid Gaussian matrices, not structured finite-field elliptic equations.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies nonlinear endpoint equations, not an iid measurement matrix or source dictionary.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, measurement map, dictionary, denoiser, iteration count, precision, restrictions, masks, and verifier.
2. Construct target-independent measurements without enumerating relation tuples or using scalar labels.
3. On known-log targets, run AMP, certify exact support, map support to points, and replay by group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Reuse the identical ensemble/denoiser for fresh scalar-blind `Q+[t]P` targets.
6. Recover a tuple, substitute logs, remove `t`, retain all ambiguity, and verify `[x]P=Q`.
7. Charge matrix/dictionary construction, all iterations, precision, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

AMP assumes a known sparse signal and measurement matrix with randomness/incoherence. Here a coordinate for every tuple is source-sized, while compact nonlinear Semaev features are highly structured and do not satisfy the cited iid theorem. State evolution predicts mean error, not a zero-error rare-support decision; exact certification reintroduces Query2P1. The route merges with observer/mixture/transport lanes IDEAs 240, 308, 329, 330, and 332.

## Proof track

Construct a source-free measurement ensemble, prove an applicable finite-field universality theorem and exact support certificate on all strata, and derive complete exponents at most `0.45`.

## Disproof track

Show dictionary construction is source-sized, exhibit state-evolution failure or support collisions, or prove exact certification requires the original restricted source query.

## Positive and negative controls

- Positive: iid Gaussian sparse-recovery instances with known dictionaries and planted support.
- Negative: structured finite-field matrices, source-permuted columns, equal endpoint features, rare singleton fibres, and blind targets.
- Baselines: IDEAs 240/308/329/330/332, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only measurements, proved state evolution, zero-error exact support/source replay, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on a source-column dictionary, one false support, unproved iid transfer, missed stratum, `B^3` matrix work, or either exponent at least `0.50`.
- Toy state-evolution agreement or approximate recovery is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-367/measurement_ensemble_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-367/state_evolution_and_support_cases.json`
- `ideas/artifacts/ECDLP-IDEA-367/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-367/cost_analysis.md`

## Interpretation boundary

This rejects the screened AMP channel, not AMP in its proved random-matrix domain. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. State evolution is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-367/measurement_ensemble_obligations.md` and prove whether any endpoint-only channel satisfies an AMP universality theorem without a source dictionary.
