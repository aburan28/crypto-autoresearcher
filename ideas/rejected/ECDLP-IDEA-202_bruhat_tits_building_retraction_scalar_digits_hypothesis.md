# ECDLP-IDEA-202 — Bruhat–Tits building-retraction scalar digits

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_finite_prime_order_action_has_fixed_point_or_dlp_oriented_apartment`
- Cohort: `20260718-d`
- Evidence scale: literature and theorem audit only; no experiment ran
- Contract posture: relative top-lane draft is retired, `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a building displacement, digit, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is a public functorial lift of the prime-order elliptic subgroup into a reductive `p`-adic group such that Cartan/Busemann retraction to a bounded-dimensional Bruhat–Tits building converts `[k]P` into a composable short digit path. Comparing the paths for `P` and `Q=[x]P` recovers `x` or exact factor-base relations below rho and BSGS.

## Mechanism-new operation

The proposed operation is **nonarchimedean group lift followed by oriented-apartment retraction to scalar digits**. It is representation-changing rather than an isogeny, pairing, or generic walk. The theorem audit rejects the frozen formulation: a finite cyclic action on a complete CAT(0) Euclidean building has a fixed point and zero stable translation; selecting an apartment and direction that restores nonzero digits is precisely scalar orientation or a discrete logarithm.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of order `N`, factor base `B=N^beta`, and target `Q=[x]P` are frozen.
2. The lift and building are constructed over a field and dimension whose bit cost is below rho.
3. Retraction is functorial for scalar multiplication and does not use `x`, a torsion basis, or a target-conditioned apartment.
4. Digits retain exact signed factor-base sources and all exceptional strata.
5. Extension degree, building state, orientation, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`prime_order_EC_subgroup | public_reductive_p_adic_lift | Bruhat_Tits_building_action | oriented_Cartan_Busemann_digit_retraction | exact_scalar_or_source_inverse`

The fingerprint fails if the image is compact/fixed, if the lift is not homomorphic, or if an oriented apartment is selected from hidden scalar data.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `OFQ-autolab-05`, the repeated-prime orientation/torsion-field question.
2. `inputs/ledger_inventory.json` — imported `ISO-SP-001`, the pairing-based cyclic-orientation lane.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-H003`, the trace-fiber transfer route.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the non-homomorphic cyclic-cover label route.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the extra-factor transfer no-result.

## Closest primary literature

- Bruhat and Tits, [Groupes réductifs sur un corps local](https://www.numdam.org/item/PMIHES_1972__41__5_0/), constructs the buildings and parahoric structure used by the proposed lift.
- Eilenberg and Mac Lane, [Cohomology theory in abstract groups I](https://doi.org/10.2307/1969215), supplies extension/splitting context but no oriented elliptic scalar section.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic square-root comparison boundary.

No checked primary source supplies the required functorial digit retraction; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the local field, reductive group, lift, building, apartment/retraction rule, digit alphabet, masks, and verifier.
2. Construct the lift and prove scalar compatibility without target-conditioned orientation.
3. Retract factor-base points and known-log endpoints, decode exact source/digit relations, and independently verify them.
4. Preserve fixed points, stabilizers, apartment ambiguity, extension coordinates, collisions, infinity, and failed targets.
5. Collect at least `B+sigma` independent rows, solve factor-base logs, and verify them.
6. Apply the identical frozen lift and retraction to fresh masks `Q+[r]P`.
7. Decode, substitute logs, subtract masks, retain ambiguity, and accept only `[x]P=Q`.
8. Charge construction, local-field precision, building exploration, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one lift/retraction/inverse cost `N^q,N^q_m`; independently ranked rows per query be `N^r`; output and apartment ambiguity be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Promotion would require both at most `0.45`; uncharged extension degree or apartment search invalidates the model.

## Likely fatal obstruction

The order-`N` image is finite. Any isometric finite-group action on a complete CAT(0) Euclidean building has a global fixed point, so its stable Cartan/Busemann displacement is zero; prime-to-residue-characteristic finite image is compact/parahoric. A nonhomomorphic lift loses `[k]` compatibility, while a target-dependent apartment, end, or section capable of ordering the orbit encodes the missing scalar orientation. Enumerating enough building state instead costs at least `N`.

## Proof track

Exhibit a bounded-dimensional, below-rho lift with a public target-independent retraction that is nonconstant and scalar-compatible; prove exact source/digit inversion and derive `lambda,mu<=0.45` through blind descent.

## Disproof track

Apply the CAT(0) fixed-point theorem, prove the image lies in a compact parahoric, reduce oriented-apartment selection to DLP/torsion orientation, or show the building/extension state is at least `N^(1/2)`.

## Positive and negative controls

- Positive control: infinite split-torus translations with public cocharacters, outside the finite target subgroup.
- Negative control: finite cyclic actions with a verified fixed point and zero stable displacement.
- Negative control: target-conditioned apartments, scalar-labelled lifts, full torsion fields, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected and its retired contract must not run. A successor requires a theorem evading the fixed-point/compact-image gate, a public nonconstant scalar-compatible retraction, exact all-source inversion, no hidden orientation, and `lambda,mu<=0.45`. A fixed point, zero stable displacement, DLP-equivalent apartment choice, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective fixed-point theorem: `ideas/artifacts/ECDLP-IDEA-202/building_action_fixed_point_theorem.md`
- Prospective orientation reduction: `ideas/artifacts/ECDLP-IDEA-202/apartment_orientation_reduction.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-202/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-202/cost_analysis.md`
- Retired contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-202_building_retraction_preflight.yaml`

All paths are prospective; no artifact root or run exists.

## Interpretation boundary

This is a scoped theorem-level rejection, not an unconditional ECDLP lower bound. Any finite check would be toy, and projections are heuristic and model-bound. A building identity, displacement, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-202/building_action_fixed_point_theorem.md` proving the finite-image fixed-point/zero-displacement obstruction for the proposed lift or exhibiting one explicit bounded-dimensional target-independent lift that evades it; do not execute the retired contract.
