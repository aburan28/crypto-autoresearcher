# ECDLP-IDEA-398 — Matched-pair bicrossproduct source factorization

## Status and claim labels

- Class: `matched_pair_group_factorization`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_prime_order_group_has_no_nontrivial_matched_factorization_and_auxiliary_actions_encode_sources`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid matched pair or bicrossproduct identity is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible matched pair of auxiliary groups factors every signed five-source relation into two mutually acting coordinates whose bicrossproduct multiplication preserves occurrence ancestry and admits a canonical stagewise inverse, enabling relation collection and blind target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **construct compatible left and right mutual actions, form the matched-pair product, split an endpoint into its two ordered components, and reverse the mutual actions to exact factor occurrences**. This is not a same-field isogeny or solver substitution; its proposed new information is an exact factorization with typed back-actions.

## Assumptions

1. Public endpoint data construct both factors and mutual actions without hidden scalars or source enumeration.
2. Every signed source tuple maps biconditionally to one bounded bicrossproduct word on every chart and restriction.
3. The two components and back-actions retain signs, repetitions, order, and occurrence labels.
4. Restricted queries reuse one target-independent structure and return exact existence plus a source lift.
5. Group construction, actions, factorization, output, rank, factor logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_group_extension | compatible_mutual_actions | matched_pair_bicrossproduct_factorization | typed_back_action_source_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; endpoint equations still need an exact source-return operation.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; a reusable representation must expose more than a supplied source deck.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; complete nonlinear phase and orientation remain charged.
4. `inputs/ledger_inventory.json` — imported `P1479`; a representation change must preserve the full restricted-source interface.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; an expanded product carrying source words is not compression.

## Closest primary literature

- Majid, [Matched pairs of Lie groups associated to solutions of the Yang–Baxter equations](https://doi.org/10.2140/pjm.1990.141.311), constructs matched-pair factorizations from supplied compatible actions.
- Majid, [Hopf-von Neumann algebra bicrossproducts](https://doi.org/10.1016/0022-1236(91)90031-Y), forms bicrossproducts from a supplied matched pair; it does not construct one from an elliptic endpoint.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies symmetric endpoint equations without matched factors or typed back-actions.

No checked source provides the proposed prime-order elliptic matched pair and source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed factor decks, auxiliary groups, mutual actions, word convention, restrictions, and independent verifier.
2. Construct the target-independent matched-pair state within `B^(9/4+o(1))` without one action record per source transition.
3. For known-log targets, query restricted exact existence, factor one endpoint, reverse every back-action to an occurrence-labelled tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charging empty fibers, ambiguous words, output, and dependent rows; solve and verify factor logs.
5. Apply the unchanged operation to fresh scalar-blind `Q+[t]P` targets under the same signed restrictions.
6. Substitute factor logs, remove `t`, retain every ambiguity branch, and verify `[x]P=Q`.
7. Charge construction, actions, factorization, source lift, output, rank, linear algebra, target descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

A prime-order cyclic ECDLP subgroup has no nontrivial internal subgroup factorization. Any useful external factors and mutual actions therefore encode an auxiliary source representation. If their words distinguish all factor occurrences, the action tables or word state materialize the source deck; if they do not, back-action inversion is noncanonical. This meets IDEAs 100, 145, 167, 178, and 391 at the supplied-action and lost-ancestry boundary.

## Proof track

Construct the factors and mutual actions from endpoints alone, prove all-strata biconditionality and a restriction-stable typed inverse, and derive complete `lambda,mu<=0.45` bounds.

## Disproof track

Prove prime-order factorization triviality for the declared interface, exhibit equal bicrossproduct summaries with different factor occurrences, or show action/state/output size above the frozen caps.

## Positive and negative controls

- Positive: supplied finite matched pairs with labelled exact factorizations must replay both components and back-actions.
- Negative: a prime cyclic group, relabelled source occurrences with fixed aggregate products, missing action entries, all signed strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 100/145/167/178/391, Query2P1, explicit source tables, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only nontrivial matched pair, exact source-biconditional inverse, `1,000` independent rows, `100` blind descents, frozen caps, and `lambda,mu<=0.45`.
- Falsify on trivial factorization, one supplied source action, one equal-summary/different-source collision, one missed stratum, cap violation, or either exponent at least `0.50`.
- A correct toy bicrossproduct is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-398/matched_pair_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-398/back_action_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-398/restricted_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-398/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic matched-pair route, not matched-pair theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; factorization correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-398/matched_pair_source_obligations.md` and classify every factor, action, and inverse datum as endpoint-derived or source-bearing advice.
