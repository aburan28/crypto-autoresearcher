# ECDLP-IDEA-320 — Independent-component cumulant source separation

## Status and claim labels

- Class: `statistical_algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_ica_requires_multiple_source_mixtures_and_retains_gauge`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: retired `review_required`, unapproved, zero-run contract at `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-320_ica_source_separation_preflight.yaml`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; cumulant diagonalization, statistical separation, a relation, or toy point recovery is not an ECDLP break.

## Falsifiable hypothesis

Public scalar-blind features of many known-log endpoints form multiple linear mixtures of statistically independent factor sources, and joint cumulant diagonalization separates reusable point atoms and supports exact blind target descent with complete time and memory exponents at most `0.45`.

## Mechanism-new operation

The screened operation is **construct several endpoint feature mixtures, jointly diagonalize higher cumulants as in independent component analysis, and map separated components to exact signed factor points**. This is a concrete blind-source operation rather than a generic tensor decomposition. It nevertheless assumes multiple mixtures of the same independent sources; ECDLP endpoints are many-to-one sums of different hidden tuples. ICA also returns components only up to permutation and scaling, whose point resolution is the missing source dictionary. It merges with IDEAs 124, 191, 241, 259, and 279.

## Assumptions

1. Target-independent public features provide multiple linear mixtures sharing fixed statistically independent factor components.
2. Relevant components are non-Gaussian/nondegenerate and identifiable over the finite-field or lifted model.
3. Permutation and scaling gauges are resolved canonically to exact signed factor points without scalar labels.
4. Sample generation, cumulants, diagonalization, output, relation density, rank, factor logs, descent, verification, uncertainty, and memory are charged.
5. The identical feature map and unmixing apply to fresh masked targets without retraining on their sources.

## Semantic fingerprint

`multi_endpoint_public_feature_mixtures | higher_joint_cumulants | ICA_unmixing | gauge_resolved_exact_factor_components | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing arithmetic source-fiber generator and batch join.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving feature boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed multi-target source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the tested full-rank phase-feature boundary.
5. `inputs/ledger_inventory.json` — imported `P1479`, the negative public-feature factor-log compression result.

## Closest primary literature

- Comon, [Independent component analysis, a new concept?](https://doi.org/10.1016/0165-1684(94)90029-9), studies supplied real random linear mixtures and cumulant-based separation under independence assumptions; it does not provide a finite-field ECDLP mixture law or point gauge.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), does not provide shared linear mixtures, independent components, or a gauge-resolved point inverse.

No checked source supplies the ECDLP mixture identity, exact finite-field component-to-point map, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor decks, signs, public feature channels, endpoint batch, cumulant orders, unmixing normalization, masks, and verifier.
2. On known-log endpoints, form features without source labels, estimate or compute exact cumulants, separate components, map them to exact signed factor points, and verify relations.
3. Collect independent rows, solve every factor-base logarithm, and independently verify the factor-log solution.
4. Apply the identical frozen feature/unmixing map to fresh `Q+[t]P` targets without target-trained components.
5. Substitute verified logs, remove masks, retain gauge and statistical ambiguity, and return scalar candidates.
6. Accept only `[x]P=Q`, charging features, samples, cumulants, diagonalization, output, rank, factor logs, descent, verification, and peak memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one feature/cumulant/unmix/source return `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All samples, failed identifiability cells, cumulant tensors, gauge resolution, and point outputs are charged. Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

ICA observes repeated linear mixtures of a fixed latent vector. Relation endpoints instead aggregate different unordered factor tuples, and public endpoint features do not expose separate mixture channels for their individual points. Even in a favorable synthetic mixture, ICA returns components up to permutation and scaling; resolving those gauges to factor points is the hidden source dictionary or scalar orientation.

## Proof track

Prove an exact shared-mixture identity, finite-field cumulant identifiability, canonical gauge-to-point resolution, sufficient relation rank, reusable factor logs, blind descent, uncertainty bounds, and `lambda,mu<=0.45`.

## Disproof track

Show that endpoints are not common-source linear mixtures, construct equal cumulants with different point tuples, prove gauge resolution needs source labels, or show sample/state/output or either exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied synthetic non-Gaussian finite mixtures with planted mixing matrix and point labels must separate up to the declared gauge.
- Negative: shuffled endpoints, Gaussian/equal-cumulant components, and gauge-permuted source dictionaries must not produce exact elliptic labels.
- Baselines: IDEAs 124/191/241/259/279, P1434, P1479, tensor decomposition, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact all-strata component-to-point return, 1,000 independently verified rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if no shared-mixture identity exists, gauge resolution imports source labels, or sample/state/output or either exponent reaches `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-320/ica_mixture_identity.md`
- `ideas/artifacts/ECDLP-IDEA-320/cumulant_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-320/independent_ica_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-320/cost_analysis.md`

## Interpretation boundary

This rejects the specified shared-mixture ICA route only. Correct cumulant diagonalization, statistical separation, a relation, or toy factor recovery is not complete ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-320/ica_mixture_identity.md` proving an exact public shared-source mixture law or an equal-cumulant/different-factor-source collision.
