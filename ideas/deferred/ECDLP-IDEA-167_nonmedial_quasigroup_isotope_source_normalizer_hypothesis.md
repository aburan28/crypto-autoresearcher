# ECDLP-IDEA-167 — Nonmedial quasigroup-isotope source normalizer

## Status and claim labels

- Class: `algebraic-representation`
- Risk band: `high-risk-theorem-gated`
- Top lane: `none`
- State: `deferred_needs_nonmedial_law_and_endpoint_normal_form_theorem`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: theorem-deferred; no contract or run is authorized
- Scale labels: any finite evidence is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a quasigroup identity, normal form, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is a public rational nonmedial quasigroup isotope of elliptic addition with a sparse factor-base subquasigroup and a target-uniform unique normal form. Normalizing a public endpoint then unpacks to every exact signed factor-base source word, enabling complete relation collection and masked target descent below rho and BSGS.

## Mechanism-new operation

The operation is **nonmedial rational isotope evaluation followed by canonical endpoint-to-source normalization**. IDEA-117 uses quasigroup graphs only as a functional-dependency observation; IDEA-122 covers affine/Mal'tsev structure. This candidate survives only with an explicit nonmedial law and normalizer. A medial isotope, bijective rewrite of supplied sources, or confluent system seeded by known relations is a control.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, rational isotope maps, normal-form order, masks, and verifier are frozen.
2. The law is total on declared charts, nonmedial, and preserves a sparse factor-base vocabulary.
3. Endpoint normalization constructs exact source words without a start witness or scalar-oriented map.
4. Confluence, termination, branch output, and normal-form state remain sub-rho on all strata.
5. Law construction, rewriting, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`public_nonmedial_elliptic_isotope | sparse_factor_base_subquasigroup | confluent_endpoint_normalizer | exact_source_words | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H640`, the sign/orientation relation hypothesis.
2. `inputs/ledger_inventory.json` — imported `ECFG-H641`, the symbolic relation-backend boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the implicit source representation hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1416-EXPLICIT-S3-NO-PROMOTION`, the explicit S3 state no-promotion result.
5. `inputs/ledger_inventory.json` — imported `P1480`, the frozen CSP/backend control.

## Closest primary literature

- Toyoda, [On axioms of linear functions](https://doi.org/10.3792/pia/1195578751), gives the affine characterization of medial quasigroups.
- Bruck, [Some results in the theory of quasigroups](https://doi.org/10.1090/S0002-9947-1944-0009963-X), supplies the neighboring structural theorem.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies elliptic relation equations, not a normalizer.

No checked source supplies the proposed law and source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the rational law, charts, subquasigroup, rewrite order, factor base, masks, and verifier.
2. Prove nonmediality, totality, sparse-base preservation, confluence, and termination without source enumeration.
3. Normalize known `R_j=[r_j]P` and unpack every normal form to signed factor-base tuples.
4. Verify tuples; preserve chart failures, nonconfluence, ambiguity, repeats, infinity, and output.
5. Collect rank `B`, solve and verify factor-base logs.
6. Normalize fresh `Q+[t]P` masks with the identical rules.
7. Substitute logs, remove masks, retain all candidates, and verify `[x]P=Q`.
8. Charge law construction, rewrite states, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, normalization/source inversion `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

All rewrite branches, completion rules, charts, and source words are charged.

## Likely fatal obstruction

Medial public isotopes are affine by Toyoda-Bruck. A nonmedial public isotope can still be only a bijective rewrite of addition, leaving decomposition unchanged; a scalar-oriented isotope or unique endpoint normalizer may encode the DLP or enumerate the original source fiber.

## Proof track

Give one explicit rational law, prove nonmedial sparse closure and a canonical source normal form, and derive complete `lambda,mu<=0.45` descent.

## Disproof track

Prove the law medial/affine, reduce the normalizer to original decomposition, expose hidden scalar orientation, find nonconfluence/source collisions, or derive an exponent at least `0.5`.

## Positive and negative controls

- Finite nonmedial quasigroups with known normal forms.
- Medial Toyoda-Bruck isotopes and IDEA-117/122 controls.
- Rewriting systems seeded with supplied relations.
- Exhaustive toy fibers, rho, BSGS, and blind-target verification.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires the explicit nonmedial-law, sparse-closure, normal-form, and `lambda,mu<=0.45` theorems. A later approved toy test needs complete all-strata recall and zero false tuples. Affine collapse, supplied relations, nonconfluence, source loss, or exponent at least `0.5` falsifies this version.

## Artifact plan

- Isotope/normalizer theorem: `ideas/artifacts/ECDLP-IDEA-167/nonmedial_normalizer_theorem.md`
- Rational law specification: `ideas/artifacts/ECDLP-IDEA-167/isotope_spec.md`
- Fixtures, verifier, and cost receipt: `ideas/artifacts/ECDLP-IDEA-167/fixtures.json`, `ideas/artifacts/ECDLP-IDEA-167/independent_verifier.py`, and `ideas/artifacts/ECDLP-IDEA-167/cost_analysis.md`

All paths are prospective; no experiment is authorized.

## Interpretation boundary

This is deferred and novelty-unverified. Finite checks are toy and projections heuristic and model-bound. A quasigroup identity or valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-167/nonmedial_normalizer_theorem.md` specifying the rational law and proving sparse closure plus endpoint/source normal forms before implementing rewriting.
