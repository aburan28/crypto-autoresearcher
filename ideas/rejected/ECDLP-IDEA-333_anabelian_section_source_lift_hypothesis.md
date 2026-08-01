# ECDLP-IDEA-333 — Anabelian section source lift

## Status and claim labels

- Class: `arithmetic-transfer`
- Risk band: `high-risk`
- Top lane: `high_risk`
- State: `merged_rejected_no_domain_correct_section_enumeration_or_compact_source_construction_is_supplied`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a reconstructed curve, valid group section, relation, or toy point is not an ECDLP break.

## Falsifiable hypothesis

An endpoint relation fibre admits a compact arithmetic fundamental-group extension whose publicly distinguished sections correspond biconditionally to exact signed factor tuples and can be enumerated and replayed inside the P1553 bounds.

## Mechanism-new operation

The screened operation is **replace the finite relation fibre by its arithmetic fundamental-group extension, identify point-theoretic decomposition-group sections, and reconstruct each factor point from its section**. This merges with IDEAs 010, 023, 043, 074, 114, 125, and 127: a decomposition group or section attached to a rational point already names the source point up to conjugacy. The checked anabelian reconstruction and finite-field/log-curve results do not supply section enumeration or a compact source construction for this zero-dimensional relation fibre.

## Assumptions

1. A suitable hyperbolic auxiliary object and its profinite extension are constructible compactly from the endpoint without listing source points.
2. Exact source tuples correspond to publicly distinguishable sections with no conjugacy or automorphism ambiguity.
3. All such sections are enumerable and convertible back to signed elliptic points within the P1553 rectangle.
4. Group presentation, quotients, section search, reconstruction, output, rank, logs, descent, verification, and memory are charged.
5. The construction is target-independent and works on fresh masked targets and every source stratum.

## Semantic fingerprint

`endpoint_relation_fibre | arithmetic_fundamental_group_extension | point_theoretic_section_selection | exact_decomposition_group_point_reconstruction | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H001`, the non-generic correspondence/Jacobian transfer hypothesis.
2. `inputs/ledger_inventory.json` — imported `TRANSFER-H003`, the trace-fibre source-return obligation.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the nonhomomorphic cover-label and exact-pushforward control.
4. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-ancestry boundary.

## Closest primary literature

- Grothendieck, [Letter to G. Faltings](https://www.cambridge.org/core/books/geometric-galois-actions/letter-to-g-faltings-translation-into-english/40DF62D52D03CB79DD15DCEA24D85368), formulates anabelian reconstruction and section ideas for arithmetic hyperbolic curves.
- Koenigsmann, [On the Section Conjecture in anabelian geometry](https://doi.org/10.1515/crll.2005.2005.588.221), studies sections up to conjugacy versus rational points in its arithmetic domain; it is not a section-enumeration algorithm for a finite relation fibre.
- Mochizuki, [The profinite Grothendieck conjecture for closed hyperbolic curves over number fields](https://www.kurims.kyoto-u.ac.jp/~motizuki/The%20Profinite%20Grothendieck%20Conjecture%20for%20Closed%20Hyperbolic%20Curves%20over%20Number%20Fields.pdf), reconstructs Hom/isomorphism data for hyperbolic curves from supplied Galois-compatible outer fundamental-group data; it is not a section-enumeration theorem.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies a finite-field endpoint equation, not point-theoretic group sections.

No checked source gives the required domain-correct zero-dimensional section enumeration, compact source construction, or complete ECDLP route; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, factor decks, auxiliary hyperbolic object, profinite quotient schedule, section equivalence, source policy, masks, and verifier.
2. From known-log endpoints construct the group extension, enumerate all point-theoretic sections, reconstruct exact signed factor points, and verify relations.
3. Collect at least `B=N^(1/5)` independent rows, solve every factor log, and verify them.
4. Apply the identical extension/section/reconstruction process to fresh scalar-blind masked targets.
5. Substitute logs, remove masks, retain all conjugacy ambiguity, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, group/section work excluding output `N^q,N^q_m`, rank credit `N^r`, exact point output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every quotient, generator, relation, conjugacy class, section branch, reconstruction, output, and verification is charged; `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Anabelian results reconstruct a hyperbolic object or morphism from a supplied profinite group; they do not cheaply enumerate rational points of a finite relation fibre. A point-theoretic section or decomposition subgroup is already a point label. Constructing the full source-faithful group object and selecting sections restores the source deck, conjugacy ambiguity, or unbounded quotient state.

## Proof track

Prove a domain-correct section-enumeration theorem, compact endpoint-only group construction, complete and canonical section-to-point inversion, relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Show the auxiliary category is outside the cited theorems, exhibit conjugate/indistinguishable sections for distinct source tuples, or prove the group presentation/decomposition subgroups encode the source list.

## Positive and negative controls

- Positive: supplied arithmetic curves with known point decomposition groups must reconstruct the known points within the theorem's actual domain.
- Negative: conjugate sections and equal group extensions with differently labelled source points must not yield a preferred tuple.
- Baselines: IDEAs 010/023/043/074/114/125/127, cover enumeration, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a domain-correct compact section theorem, exact all-strata replay, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if a point section/decomposition group is supplied, quotient state reaches `B^3`, source points remain conjugate, or either exponent reaches `0.50`.
- Reconstruction from supplied point sections is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-333/section_domain_and_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-333/conjugacy_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-333/section_to_point_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-333/cost_analysis.md`

## Interpretation boundary

This rejects the declared finite-fibre section route and proves no general anabelian impossibility. A curve reconstruction, group isomorphism, or toy point section is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-333/section_domain_and_input_receipt.md` matching the proposed auxiliary object to the hypotheses of the cited theorems and identifying every point-labelled group input.
