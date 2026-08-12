# Pre-ID duplicate draft — Atkin–Morain ECPP CM source chain

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V12`; no canonical ID allocated.
- Disposition: `merged_rejected_cm_curve_certificate_chain_and_same_field_representation_control`.
- Class/risk/lane: representation / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; constructing a CM curve or verifying an ECPP chain is not an ECDLP break.

## Falsifiable hypothesis

Each restricted ECDLP endpoint deterministically selects a CM discriminant whose
Atkin–Morain ECPP curve and recursive order chain encode one exact signed source
tuple. CM construction, Cornacchia norms, and certificate recursion would return
full relation rank and 100 blind descents with complete exponents `<=0.45`.

## Mechanism-new operation

ECPP chooses a discriminant, solves a norm equation, constructs a curve with
controlled order, and verifies a recursive point-order certificate for a supplied
integer. ECDLP novelty requires the discriminant/order chain to be endpoint-derived
and to admit an exact inverse to original-curve occurrences without same-field
isogeny variants, target fitting, or source enumeration.

## Assumptions

1. Endpoint restrictions canonically select small discriminants and certificate integers.
2. CM curve/order data preserve signed occurrence identity and empty-fibre semantics.
3. The auxiliary-to-original point section is public, exact, and non-DLP.
4. Discriminant search, class polynomials, norms, curve construction, recursion, replay, logs, and descent meet both caps.
5. No source-labelled ideal, isogeny path, or target scalar enters the chain.

## Semantic fingerprint

`public_restricted_endpoint | CM_discriminant_and_norm_selection | Atkin_Morain_ECPP_curve_chain | exact_auxiliary_to_original_occurrence_section | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-018_cm_ray_class_artin_descent_hypothesis.md` — CM/class-field data do not supply original-curve source orientation.
2. `ideas/ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md` — auxiliary curves help only with a faithful projection and return.
3. `ideas/ECDLP-IDEA-010_torsor_deck_orbit_descent_hypothesis.md` — branch-compatible auxiliary descent remains explicit.
4. `ideas/rejected/ECDLP-IDEA-042_hecke_sparse_modular_quotient_descent_hypothesis.md` — same-field modular/isogeny variants are representation controls.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact endpoint source replay and blind descent remain the gate.

## Closest primary literature

- Atkin and Morain, [Elliptic curves and primality proving](https://doi.org/10.1090/S0025-5718-1993-1199989-X), constructs CM curves and recursive certificates for supplied primality instances.
- Morain and Nicolas, [On Cornacchia's algorithm](https://www.lix.polytechnique.fr/~morain/Articles/cornac.pdf), supplies the norm-equation subroutine used in CM construction.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide a CM certificate chain whose factors are exact ECDLP occurrences.

No checked source constructs the required generic-prime endpoint-to-source section. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, signed decks, restriction compiler, discriminant order, class-polynomial policy, masks, and verifier.
- Build target-independent state under `B^(9/4+o(1))` without source ideals, isogeny advice, target fitting, or factor logs.
- Charge every discriminant rejection, class polynomial, norm root, curve twist, order factor, point-order witness, recursion, restriction query, and source replay.
- Verify `max(d_FB+32,1000)` independent relation rows, rank `d_FB`, and solve every factor-base log.
- Reuse byte-identical state on 100 fresh masked targets, return tuples, subtract masks, and verify scalars.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal densities
`N^delta,N^delta_t`; CM/certificate/replay work `N^q,N^q_m`; rank credit
`N^r`; output `N^o`; ambiguity/failure `N^u`; logs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require `lambda,mu<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`;
rho/BSGS remain `0.50`.

## Likely fatal obstruction

ECPP certifies a supplied integer; CM data determine auxiliary curve order, not the
hidden scalar or exact source fibre on the original curve. An auxiliary-to-original
section requires an isogeny/correspondence with point orientation, precisely the
occupied transfer obstruction. If discriminants encode the desired tuple, their
selection is source advice; the certificate itself is relation-only.

## Proof track

Prove endpoint-only discriminant/instance construction, exact restriction
biconditional, non-DLP all-strata auxiliary-to-source section, full rank/logs, blind
descent, and complete sub-rho costs.

## Disproof track

Hold the ECPP chain fixed while changing original fibres, expose a source-labelled
ideal/isogeny, show auxiliary orders are scalar-independent, or reach exponent
`0.50`.

## Positive and negative controls

- Positive: supplied ECPP chains with an external auxiliary-to-source dictionary.
- Negative: equal chains/different fibres, CM twists, isogenous same-order curves, failed norm roots, empty restrictions, and fresh targets.
- Baselines: IDEAS 002/010/018/042, Goldwasser–Kilian, P1553 R4, rho, and BSGS.
- Correct CM construction or certificate verification is representation-only evidence.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/biconditional/section theorems, zero source errors, failure `<=2^-80`, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-fitted discriminant/ideal, equal-chain source collision, same-field isogeny-only section, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v12_cm_chain_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v12_equal_chain_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v12_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not ECPP. Correct CM curves, norm solutions,
certificates, relations, or validator passes remain `toy`, `heuristic`,
`model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Freeze one complete ECPP CM chain and test whether any chain-only rule distinguishes two original-curve endpoint fibres with different signed source sets.
