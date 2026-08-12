# Pre-ID duplicate draft — Pollard p-minus-one smooth-order source filter

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V05`; no canonical ID allocated.
- Disposition: `merged_rejected_smooth_order_filter_and_no_endpoint_source_compiler`.
- Class/risk/lane: algorithm / conservative / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a smooth-order gcd factor or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Each endpoint fibre admits a public multiplicative modulus whose hidden component
order is smooth exactly when the fibre contains an admissible signed tuple. Pollard
`p-1` powering and gcd extraction would therefore return exact occurrences and
support a full factor-base/log/descent campaign with complete exponents `<=0.45`.

## Mechanism-new operation

Pollard's native operation raises a supplied base to an exponent divisible by small
prime powers and takes a gcd with a supplied composite modulus, revealing a factor
when one component's `p-1` is smooth. ECDLP novelty requires an endpoint-derived
modulus whose factors correspond canonically to point occurrences, not an already
materialized resultant or source product.

## Assumptions

1. Public endpoints compile a compact multiplicative modulus without enumerating sources.
2. Its factors correspond bijectively to signed factor-base occurrences and restrictions.
3. Smoothness density yields enough independent relations after all failures are charged.
4. Powering, gcds, factor replay, rank, factor logs, and descent meet both caps.
5. The modulus is target-independent and not a dense resultant or explicit large-prime table.

## Semantic fingerprint

`public_endpoint_composite | smooth_component_order_powering | Pollard_pminus1_gcd_split | exact_factor_to_occurrence_lift | full_descent`

## Five closest ledger entries

1. `ideas/ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md` — smoothness must occur in a useful source-faithful representation.
2. `ideas/ECDLP-IDEA-007_miller_s_unit_descent_hypothesis.md` — factorization data need a complete elliptic source/descent inverse.
3. `ideas/rejected/ECDLP-IDEA-063_provenance_preserving_subresultant_forest_hypothesis.md` — product/gcd trees are occupied once source polynomials exist.
4. `ideas/deferred/ECDLP-IDEA-121_shared_bivariate_common_norm_hypothesis.md` — compact common factors remain compiler/source gated.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact common-factor decisions and charged replay remain the frontier.

## Closest primary literature

- Pollard, [Theorems on factorization and primality testing](https://doi.org/10.1017/S0305004100049252), analyzes factorization by smooth component orders.
- Montgomery, [Speeding the Pollard and elliptic curve methods of factorization](https://www.ams.org/journals/mcom/1987-48-177/S0025-5718-1987-0866113-7/), improves the supplied-modulus factoring stage.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide a compact factor-to-occurrence modulus.

No checked source constructs the required endpoint compiler and exact factor lift. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, factor decks, modulus compiler, smoothness bounds, bases, restrictions, masks, and verifier.
- Build target-independent state under `B^(9/4+o(1))`, excluding explicit source products, dense resultants, target advice, and logs.
- Charge modulus construction, every prime-power exponent, gcd, retry, factor, label lift, occurrence replay, and failure.
- Collect `max(d_FB+32,1000)` verified independent rows, rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical state on 100 fresh masked targets, return tuples, subtract masks, and verify scalars.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, powering/gcd/replay `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity/failure `N^u`, logs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require `lambda,mu<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`.
Rho/BSGS remain `0.50`.

## Likely fatal obstruction

Pollard `p-1` exploits the order of a factor of a supplied integer. A factor whose
identity is a point occurrence can only arise after a source-bearing product or dense
eliminant is built. Aggregate endpoint moduli have factors unrelated to exact tuples,
and a gcd certificate is relation-only until labels and descent are recovered.

## Proof track

Prove a compact endpoint-only modulus, factor/occurrence bijection under arbitrary
restrictions, favorable charged smoothness, full rank/logs, blind descent, and both
cost caps.

## Disproof track

Expose a source product/resultant, find equal moduli with different fibres, show
factors lack point labels, or make complete smoothness/replay cost at least `0.50`.

## Positive and negative controls

- Positive: supplied composites with planted smooth-order factors and external point labels.
- Negative: equal moduli/different fibres, nonsmooth factors, gcd `1`/full modulus, label permutations, empty and fresh targets.
- Baselines: IDEAS 002/007/063/121, P1553 R4, rho, and BSGS.
- A nontrivial gcd or valid row remains toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with compiler/bijection theorems, charged success density, zero label errors, full rank/logs, 100 blind descents, and both exponents `<=0.45`.
- Falsify on one source-sized modulus factor, equal-modulus source collision, unlabeled gcd, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v05_modulus_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v05_equal_modulus_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v05_smoothness_cost.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Pollard `p-1`. Correct factors, gcds, relations, or
validator passes remain `toy`, `heuristic`, `model-bound`, `novelty-unverified`,
and not a breakthrough.

## Exactly one next executable action

1. Audit whether the smallest endpoint eliminant with a point-labelled factor can be constructed without enumerating the factor's source occurrences.
