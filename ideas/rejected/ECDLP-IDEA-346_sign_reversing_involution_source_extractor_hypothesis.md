# ECDLP-IDEA-346 — Sign-reversing-involution source extractor

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_involution_requires_source_signed_terms_and_fixed_points`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cancellation identity or surviving aggregate is not an ECDLP break.

## Falsifiable hypothesis

The source-labelled determinant or generating-function expansion admits a compact public sign-reversing involution pairing every nonrelation term while leaving exact relation tuples as fixed points, and those fixed points can be located and replayed inside the P1553 bounds.

## Mechanism-new operation

The screened operation is **define a sign-reversing involution on source-labelled expansion terms, cancel nonfixed pairs, and extract the fixed terms as exact factor tuples**. It is distinct only if the involution and fixed-point locator are evaluated without enumerating the terms. Otherwise it merges with IDEAs 050, 072, 157, 183, 185, 191, and the determinant-value cancellation controls.

## Assumptions

1. Expansion terms and signs are generated implicitly without a tuple deck.
2. One uniform endpoint-parameterized involution is efficiently computable and has fixed points exactly at valid sources.
3. Fixed points are located rather than merely counted or preserved in an aggregate sum.
4. All signed, repeated, overlap, singular, infinity, and ambiguous strata are covered.
5. Term generation, involution branches, cancellation, output, rank, logs, blind descent, and memory are charged.

## Semantic fingerprint

`source_labelled_generating_expansion | public_sign_reversing_involution | nonrelation_pair_cancellation | exact_fixed_point_source_locator | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `P1477`, where source-faithful serial states become dense.
3. `inputs/ledger_inventory.json` — imported `P1478`, the compact transition and dense-composition boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the witness extraction and nonlinear-composition requirement.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, where materialized products do not improve the complete path.

## Closest primary literature

- Garsia and Milne, [A Rogers–Ramanujan bijection](https://doi.org/10.1016/0097-3165(81)90062-5), develops an involution principle on explicitly represented signed combinatorial sets; it does not locate hidden elliptic fixed points.
- Garsia and Milne, [Method for constructing bijections for classical partition identities](https://doi.org/10.1073/pnas.78.4.2026), is the direct primary involution control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies an endpoint equation rather than a compact signed term set and fixed-point oracle.

No checked source supplies the claimed involution and source locator; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, expansion grammar, signs, involution, fixed-point locator, masks, and verifier.
2. Construct the implicit expansion for known-log endpoints without source enumeration.
3. Apply the involution, locate every fixed point, replay exact factor tuples, and verify relations.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Apply the identical construction to fresh scalar-blind masked targets.
6. Substitute logs, remove masks, retain all fixed-point alternatives, and verify `[x]P=Q`.
7. Charge terms, branches, cancellations, output, rank, logs, descent, verification, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, involution query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every term access, involution step, collision, fixed-point output, and bit is charged; `0<=r<=o`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`. Promotion requires complete exponents at most `0.45`.

## Likely fatal obstruction

An involution proves equality of signed aggregates after the source terms are represented. It does not enumerate fixed points. Computing the branch often asks which partial term can complete, while retaining exact labels restores the full source expansion. Fast determinant moments already demonstrate that cancellation values can be computed without reporting zeros or sources.

## Proof track

Give a source-free implicit term grammar, prove fixed points are exactly all relation tuples, construct a sub-gate fixed-point locator, and derive complete `lambda,mu<=0.45`.

## Disproof track

Show the involution queries completion, find nonrelation fixed points or cancelled relations, prove fixed-point enumeration restores the source deck, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive: explicit signed sets with planted fixed points must cancel and enumerate correctly.
- Negative: equal aggregate sums with different fixed sets and source-permuted term grammars must not yield preferred elliptic points.
- Baselines: direct owner IDEA-157; IDEAs 050/072/183/185/191; raw-ledger controls `ECFG-P1553-DV-V1` and `ECFG-P1553-DV-R1`; determinant contractions; rho; and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact all-strata fixed-point biconditionality, zero source errors, 1,000 ranked rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on one bad fixed point, one cancelled relation, source-sized term access, or either exponent at least `0.50`.
- Aggregate cancellation or a relation-valid identity is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-346/involution_definition.md`
- `ideas/artifacts/ECDLP-IDEA-346/fixed_point_biconditional_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-346/term_materialization_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-346/cost_analysis.md`

## Interpretation boundary

This rejects the proposed hidden fixed-point extractor, not sign-reversing involutions. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Cancellation or correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-346/involution_definition.md` on one complete source grammar and mark every branch that requires a completion or source-membership query.
