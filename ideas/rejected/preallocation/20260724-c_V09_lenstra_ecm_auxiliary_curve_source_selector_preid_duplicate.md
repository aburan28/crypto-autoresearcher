# Pre-ID duplicate draft — Lenstra ECM auxiliary-curve source selector

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V09`; no canonical ID allocated.
- Disposition: `merged_rejected_auxiliary_curve_smooth_order_control_and_h077_duplicate`.
- Class/risk/lane: representation / representation-changing / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; an auxiliary-curve factor, group-law failure, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Random auxiliary curves attached to a public ECDLP endpoint have smooth component
orders precisely for admissible signed source fibres. Lenstra ECM scalar
multiplication would expose a failed denominator whose gcd identifies exact point
occurrences, enabling full factor logs and 100 blind descents with complete
exponents `<=0.45`.

## Mechanism-new operation

ECM changes the factoring group per trial: a supplied composite is reduced modulo
an unknown factor, and a random curve whose group order is smooth causes a
noninvertible denominator. For ECDLP novelty, endpoints must compile the composite
and a factor-to-occurrence section; random same-field curves alone are only a
smooth-order representation control.

## Assumptions

1. Endpoint data compile a compact composite whose factors label exact signed sources.
2. Auxiliary-curve smoothness is correlated with valid fibres, not only random group order.
3. Denominator gcds lift canonically to point occurrences under arbitrary restrictions.
4. Curve trials, scalar chains, gcds, replay, rank, logs, and descent meet both caps.
5. The construction uses no same-field DLP, source product, or target-fitted curve.

## Semantic fingerprint

`public_endpoint_composite | random_auxiliary_elliptic_curves | smooth_order_denominator_failure | exact_factor_to_occurrence_section | full_descent`

## Five closest ledger entries

1. `inputs/h100_session/HYPOTHESES_100.md` (`H077`) — already screens ECM-style stage-1 for DLP and records the random-curve-order obstruction.
2. `ideas/ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md` — useful auxiliary smoothness needs a faithful projected return.
3. `ideas/ECDLP-IDEA-010_torsor_deck_orbit_descent_hypothesis.md` — auxiliary curves/covers must return branch-compatible sources.
4. `ideas/rejected/ECDLP-IDEA-042_hecke_sparse_modular_quotient_descent_hypothesis.md` — same-field auxiliary representations do not remove target descent.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact common-factor replay remains the live gate.

## Closest primary literature

- Lenstra, [Factoring integers with elliptic curves](https://doi.org/10.2307/1971363), changes auxiliary groups to exploit smooth order modulo an unknown factor.
- Montgomery, [Speeding the Pollard and elliptic curve methods of factorization](https://www.ams.org/journals/mcom/1987-48-177/S0025-5718-1987-0866113-7/), optimizes the supplied-composite stage.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies no factor-to-occurrence composite.

The native operation is already locally proposed in H077, and no checked source supplies the missing ECDLP section. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, signed decks, composite compiler, curve sampler, scalar bounds, restrictions, masks, and verifier.
- Build target-independent state under `B^(9/4+o(1))`, excluding source products, same-field DLP advice, target fitting, and logs.
- Charge every curve rejection, discriminant gcd, scalar multiplication, denominator inversion/failure, gcd, factor lift, replay, and unsuccessful trial.
- Verify `max(d_FB+32,1000)` independent rows, rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical eligible state on 100 fresh masked targets, return tuples, subtract masks, and verify scalars.

## Full rho/BSGS cost model

With `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, curve/gcd/replay costs `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, logs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`.
Rho/BSGS remain `0.50`.

## Likely fatal obstruction

ECM factors a supplied integer; it does not solve a prime-order ECDLP or create a
source-bearing modulus. Random auxiliary curve orders are independent of the hidden
target scalar. If a modulus factor labels an occurrence, constructing it already
materializes source information. A denominator failure is an unlabeled gcd
certificate, and H077 already owns this transplant.

## Proof track

Prove endpoint-only composite construction, nonrandom smoothness correlation,
factor/occurrence bijection across restrictions, full rank/logs, blind descent, and
both complete cost caps.

## Disproof track

Show auxiliary orders are target-independent, expose a source product, hold ECM
transcripts fixed across different fibres, or obtain complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied composites with planted smooth-order ECM factors and external source labels.
- Negative: random same-size curves, equal composites/different fibres, nonsmooth orders, full/identity gcds, label permutations, and fresh targets.
- Baselines: H077, IDEAS 002/010/042, `p-1`, P1553 R4, rho, and BSGS.
- A correct factor or curve-law failure is representation-only evidence.

## Quantitative promotion and falsification gates

- Promote only with a new compiler/section theorem beyond H077, significant endpoint-conditioned smoothness after matched controls, zero label errors, full rank/logs, 100 blind descents, and both exponents `<=0.45`.
- Falsify on H077 semantic identity, target-independent order statistics, one source-bearing factor, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v09_composite_curve_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v09_matched_order_controls.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v09_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects this ECDLP transplant, not ECM. Correct factoring, smooth-order events,
relations, or validator passes remain `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Compare the proposed endpoint-conditioned auxiliary-curve order distribution with a matched random-curve control and record whether any nonconstant source-labelled statistic remains.
