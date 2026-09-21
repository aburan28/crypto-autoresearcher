# Pre-ID duplicate draft — Goldwasser–Kilian elliptic source certificate

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V11`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_curve_order_certificate_and_no_source_occurrences`.
- Class/risk/lane: mechanism / high-risk / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; an elliptic primality certificate or verified point order is not an ECDLP break.

## Falsifiable hypothesis

For every restricted ECDLP endpoint fibre, a public auxiliary curve and
Goldwasser–Kilian point-order certificate exist exactly when the fibre is nonempty;
the certificate recursion canonically returns the signed factor-base occurrences.
This would support full rank, logs, and 100 blind descents with complete exponents
`<=0.45`.

## Mechanism-new operation

Goldwasser–Kilian certifies a supplied integer by finding a supplied auxiliary
elliptic curve, a sufficiently large prime factor of its order, and a point-order
witness, then recursing. It becomes an ECDLP source mechanism only if endpoints
construct those objects and a point-labelled source inverse without target DLP,
same-field isogeny advice, or source enumeration.

## Assumptions

1. Restricted endpoints compile compact auxiliary certificate instances.
2. Certificate existence is subset-stable and exactly matches source-fibre existence.
3. Curve points/order factors canonically label signed original-curve occurrences.
4. Curve search, order proof, recursion, replay, rank, logs, and descent meet both caps.
5. The auxiliary certificate state is target-independent and source-free.

## Semantic fingerprint

`public_restricted_endpoint | auxiliary_elliptic_primality_instance | Goldwasser_Kilian_point_order_certificate | exact_original_curve_occurrence_inverse | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-107_finite_field_witness_transport_hypothesis.md` — a finite-field witness does not automatically transport sources.
2. `ideas/deferred/ECDLP-IDEA-052_elliptic_wedge_witness_identity_hypothesis.md` — elliptic identities remain certificate-only without a return.
3. `ideas/ECDLP-IDEA-010_torsor_deck_orbit_descent_hypothesis.md` — auxiliary elliptic objects need branch-compatible descent.
4. `ideas/rejected/ECDLP-IDEA-042_hecke_sparse_modular_quotient_descent_hypothesis.md` — same-field auxiliary curves do not remove the original target problem.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted decision plus charged source replay remains required.

## Closest primary literature

- Goldwasser and Kilian, [Almost all primes can be quickly certified](https://doi.org/10.1145/12130.12162), gives randomized elliptic point-order certificates for supplied primality instances.
- Lenstra, [Factoring integers with elliptic curves](https://doi.org/10.2307/1971363), is the nearby auxiliary-curve smooth-order boundary.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies no certificate-to-original-occurrence inverse.

No checked source constructs the required ECDLP certificate compiler and source lift. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, signed decks, restriction compiler, auxiliary-curve sampler, order/factor policy, masks, and verifier.
- Build target-independent state under `B^(9/4+o(1))` without source tables, target fitting, same-field DLP advice, or factor logs.
- Charge every curve trial, point count/order factor, point-order witness, failed certificate, recursive instance, restriction query, and signed replay.
- Verify `max(d_FB+32,1000)` independent relation rows, rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical state on 100 fresh masked targets, return tuples, subtract masks, and verify scalars.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, certificate/replay work `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, logs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`;
rho/BSGS remain `0.50`.

## Likely fatal obstruction

The certificate proves primality or point order of a supplied auxiliary instance; it
does not encode exact sources on the original curve. Constructing an instance whose
certificate is equivalent to a restricted fibre is the missing exact decision
compiler, and any certificate section that labels occurrences already contains the
source dictionary. Curve correctness is relation-only.

## Proof track

Prove endpoint-only certificate construction, exact restriction biconditional,
canonical auxiliary-to-original occurrence inversion, full rank/logs, blind
descent, and both cost caps.

## Disproof track

Hold the certificate fixed while changing original fibres, expose source/target
information in curve choice or order factors, show the output is existence-only, or
reach exponent `0.50`.

## Positive and negative controls

- Positive: supplied auxiliary-curve certificates with external original-source labels.
- Negative: equal certificates/different fibres, point-order witnesses with no source map, failed curve trials, empty restrictions, and fresh targets.
- Baselines: IDEAS 010/042/052/107, P1553 R4, rho, and BSGS.
- Certificate correctness or point-order verification is not a source-return result.

## Quantitative promotion and falsification gates

- Promote only with exact compiler/biconditional/inverse theorems, zero source errors, failure `<=2^-80`, full rank/logs, 100 blind descents, and both exponents `<=0.45`.
- Falsify on one equal-certificate source collision, source-fitted curve/order, existence-only output, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v11_certificate_curve_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v11_equal_certificate_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v11_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Goldwasser–Kilian certification. A correct curve,
point order, certificate, relation, or validator pass remains `toy`, `heuristic`,
`model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Freeze one valid auxiliary point-order certificate and search for two distinct restricted source fibres compatible with its complete transcript.
