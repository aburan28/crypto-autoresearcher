# ECDLP-IDEA-334 — Kempf–Ness orbit source section

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_closed_orbit_representative_preserves_compact_gauge_and_requires_source_vector`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a closed-orbit certificate, moment-map zero, valid relation, or toy representative is not an ECDLP break.

## Falsifiable hypothesis

The permutation and sign action on each elliptic source fibre has a compact invariant-theory embedding whose Kempf–Ness minimal representative canonically selects and decodes an exact signed factor tuple within the P1553 bounds.

## Mechanism-new operation

The screened operation is **embed source tuples in a reductive representation, minimize norm along the complexified orbit or solve the moment-map-zero condition, and decode the resulting polystable representative to factor points**. This merges with IDEAs 029, 094, 123, 246, 261, 289, and 318: geometric invariant theory identifies a closed orbit, not a preferred vector inside its compact stabilizer orbit. For the stated finite permutation/sign action and an invariant norm, every point in the orbit has the same norm. Enlarging to a complex reductive auxiliary representation requires the unsupplied embedding, while the initial vector or point-separating invariants already carry the source dictionary.

## Assumptions

1. The endpoint defines a compact representation and invariant coordinates without enumerating source tuples.
2. Each valid source orbit has one publicly canonical representative, not merely a compact-gauge class.
3. The representative decodes biconditionally to every exact signed tuple on all strata.
4. Embedding, invariants, optimization, gauge fixing, output, rank, factor logs, descent, verification, and memory are charged.
5. The same construction applies to fresh masked targets without target-fitted linearization.

## Semantic fingerprint

`endpoint_source_orbit_representation | reductive_GIT_quotient | Kempf_Ness_minimal_norm | exact_gauge_fixed_factor_decode | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed source-fibre generator hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-P1421-EXACT-TRANSPOSED-MATRIX-CONTROL`, the exact supplied pair-state representation control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank public representation boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the aggregate invariant-kernel control.

## Closest primary literature

- Kempf and Ness, [The length of vectors in representation spaces](https://doi.org/10.1007/BFb0066647), relates closed complexified orbits to minimal norm and moment-map conditions for a supplied representation vector.
- Mumford, Fogarty, and Kirwan, [Geometric invariant theory](https://doi.org/10.1007/978-3-642-57916-5), constructs quotients from supplied group actions and invariants; it does not choose a source vector within an orbit.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations without a source-orbit embedding or inverse.

No checked source supplies the endpoint-only representation, canonical compact-gauge section, or complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, coloured decks, group action, representation, norm, gauge rule, source policy, masks, and verifier.
2. For known-log endpoints, construct the representation without sources, find every relevant minimal representative, decode exact tuples, and verify relations.
3. Collect at least `B=N^(1/5)` independent rows, solve every factor log, and independently verify them.
4. Apply the identical quotient and gauge section to fresh scalar-blind masked targets.
5. Substitute logs, remove masks, retain stabilizer ambiguity, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

Let setup and memory be `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, invariant/optimization work excluding output `N^q,N^q_m`, verified rank `N^r`, source output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Representation dimension, invariant generators, orbit closure, optimization precision, stabilizer branches, output, and verification are charged; `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Kempf–Ness starts with a supplied vector and identifies its closed complexified orbit. It cannot reconstruct that vector from quotient invariants. In the declared finite permutation/sign action, an invariant norm is constant on the entire orbit, so minimization cannot select a label; for a larger complexified action, the representation and embedding are unsupplied. A point-separating representation or gauge section therefore imports the source vector or equivalent dictionary.

## Proof track

Construct endpoint-only invariant data, prove a unique computable gauge section and exact all-strata decode, then prove relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Exhibit two labelled tuples in one closed orbit/minimal compact orbit, or prove any separating invariant/gauge section has source-sized representation state.

## Positive and negative controls

- Positive: supplied reductive representations with trivial compact stabilizer and known vectors must recover the known minimal orbit.
- Negative: orbit-equivalent source permutations and nontrivial stabilizers must not yield a preferred labelled tuple.
- Baselines: IDEAs 029/094/123/246/261/289/318, explicit invariant tables, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only representation and unique-section theorems, exact recall, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if a source vector is input, compact gauge remains, representation state reaches `B^3`, or either complete exponent reaches `0.50`.
- Correct orbit classification is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-334/orbit_gauge_collision_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-334/invariant_input_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-334/stabilizer_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-334/cost_analysis.md`

## Interpretation boundary

This rejects the proposed quotient-to-labelled-source section, not geometric invariant theory generally. A closed-orbit or moment-map certificate is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-334/orbit_gauge_collision_receipt.md` exhibiting the smallest admitted source permutation or stabilizer orbit that survives Kempf–Ness minimization.
