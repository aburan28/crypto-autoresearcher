# ECDLP-IDEA-303 — Aldous–Hoover exchangeable source decoder

## Status and claim labels

- Class: `probabilistic_representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_exchangeable_representation_is_nonidentifiable_and_distributional`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exchangeable representation, fitted latent model, valid relation, or toy recovery is not an ECDLP break.

## Falsifiable hypothesis

Random relabelling of factor-base points and known-log relations yields a separately exchangeable incidence array whose Aldous–Hoover latent variables can be canonically inverted into exact factor points, providing reusable relation generation and masked-target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **symmetrize the relation incidence array, recover an Aldous–Hoover representation `f(U,U_i,V_j,W_ij)`, and canonically invert row/column latent variables to factor points**. This is not generic tensor decomposition: it specifically invokes exchangeability to replace explicit labels. The representation theorem is distributional and nonidentifiable under measure-preserving transformations; a point-faithful finite array or canonicalization restores source-sized observations. It therefore merges with IDEAs 001, 104, 131, 241, and 282.

## Assumptions

1. Endpoint-labelled relation observations form one target-uniform separately exchangeable law after public randomization.
2. Its latent representation is algorithmically identifiable, not merely existent up to measure-preserving changes.
3. Latent variables map canonically and biconditionally to exact signed factor points on every stratum.
4. Sample generation, estimation, canonicalization, output, rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`exchangeable_relation_array | Aldous_Hoover_latent_representation | canonical_latent_identification | exact_factor_return | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the batch generator and transposed-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the aggregate-phase versus exact-source gap.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact compact transition and composition control.

## Closest primary literature

- Aldous, [Representations for partially exchangeable arrays of random variables](https://doi.org/10.1016/0047-259X(81)90099-3), proves a latent representation for invariant array laws, not a unique finite-sample decoder.
- Diaconis and Janson, [Graph limits and exchangeable random graphs](https://doi.org/10.4171/138-1/3), makes the measure-preserving nonuniqueness explicit in the graph setting.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives endpoint equations but no exchangeable latent-to-point inverse.

No checked source provides canonical factor labels, target descent, or complete sub-rho costs; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, array schema, relabelling law, estimator, masks, and independent verifier.
2. Generate known-log endpoint observations without enumerating hidden source tuples beyond charged accepted rows.
3. Infer and canonicalize latent variables, return exact signed factor points, and verify every relation independently.
4. Collect independent rows, solve and verify all factor logs.
5. Apply the same latent law and decoder to fresh `Q+[t]P` targets without target-trained canonicalization.
6. Substitute factor logs, remove masks, retain ambiguity, and return candidates.
7. Accept only exact `[x]P=Q`, charging samples, arrays, latent state, outputs, failures, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one sample/inference/inverse `N^q,N^q_m`, rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes sampling, identification, exact inverse, and verification; `o` includes every returned tuple. Rho has time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Aldous–Hoover identifies a law, not labelled latent individuals. Measure-preserving reparameterizations leave the array distribution unchanged while permuting any proposed factor dictionary. Finite target conditioning worsens identifiability; making the array point-faithful requires observations or coordinates that already name the factor base/source deck.

## Proof track

Prove a finite, target-uniform identifiability theorem with a public canonical latent gauge, exact all-strata point inverse, sufficient independent relation density, reusable factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Construct two measure-preserving latent models with identical observable arrays but different exact point labellings, or show that any identifying statistics/materialized array has `N^0.50`-or-worse sample, state, or output cost.

## Positive and negative controls

- Positive: synthetic labelled exchangeable arrays with a frozen canonical latent gauge must be reconstructed.
- Negative: randomly measure-preserving latent reparameterizations must not be mistaken for exact point recovery.
- Baselines: shuffled relation tables, random-oracle arrays, IDEAs 001/104/131/241/282, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with independent all-strata identification, 1,000 verified rows and 100 blind descents per large size, and both full exponents at most `0.45`.
- Falsify if two latent gauges give the same observables but different point labels, if a source-labelled array is required, or if sample/state/output reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-303/exchangeable_identifiability_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-303/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-303/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-303/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of the stated exchangeable-latent inverse, not a universal impossibility theorem for probabilistic ECDLP representations. Latent-model fit or toy correctness is not exact scalar recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-303/exchangeable_identifiability_theorem.md` giving either a public canonical latent-to-point inverse or an explicit equal-law/different-label counterexample before any sampling experiment.
