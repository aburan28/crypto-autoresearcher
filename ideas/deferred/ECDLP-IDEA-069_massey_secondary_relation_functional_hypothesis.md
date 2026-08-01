# ECDLP-IDEA-069 — Massey secondary-relation functional

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `deferred_missing_finite_field_defining_system`
- Evidence scale: `toy` symbolic-identity preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deferral boundary: no explicit finite-field line bundles, Ext/Hom bases, defining system, normalization, complete map-span basis, or masked-scalar equation
- Breakthrough claim: **none**; a nonzero higher product or consistent relation label is not an ECDLP break.

## Falsifiable hypothesis

There is a target-independent finite collection of line bundles and explicit defining
systems on an ordinary `E/F_p` (or the ledger's fixed cyclic cover) whose triple Massey
product defines a computable secondary functional `mu` on source-labelled divisor
relations. After quotienting every functional induced by known maps, `mu` remains
nonzero, obeys a complete `A_infinity` composition law, and gives a bounded-degree,
sub-square-root evaluable equation in the masked scalar of `Q+[t]P`. Together with
factor-base calibration and exact source relations, that equation recovers `x` with full
time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is a **secondary, source-evaluable Massey functional outside the
ordinary homomorphism/map span**. Binary composition records only the group relation and
is already closed by the ledger. The proposed `m_3` value retains the choice and order
of three source extensions; the `A_infinity` identity supplies a correction law under
relation composition, and an explicit defining-system normalization makes the value
public and reproducible.

A generic cohomology class, theta value, pairing, relation checksum, unbased Massey
product, or post-hoc label does not qualify. The operation must return a scalar equation
that completes blind target descent.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N!=p` and `Q=[x]P`.
2. All line bundles, extension representatives, defining systems, bases, and normalizations are public and target independent.
3. The resulting `m_3` value is defined on every accepted source tuple, including degenerate and exceptional cases.
4. The quotient by known pullback, norm, trace, pairing, and map-span functionals is computed exactly before testing novelty.
5. The masked-target equation has bounded degree or a residual list of size `N^(rho_mu)` with evaluator plus list exponent below `1/2`.
6. Bundle construction, extension arithmetic, relation collection, calibration, target queries, residual candidates, verification, and memory are charged.
7. Every extrapolation remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`source_labelled_line_bundle_extensions | normalized_triple_Massey_product | quotient_known_map_span | A_infinity_relation_cocycle | bounded_degree_masked_scalar_equation | verified_target_recovery`

The proposal is deferred until the secondary value is explicitly defined and shown to
be neither zero nor a repackaged Weil pairing/homomorphism, with a derived target equation
rather than relation validity alone.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H003`, the closest nonlinear trace-fiber/correspondence mechanism.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H004`, the closest non-homomorphic cyclic-cover label outside ordinary map span.
3. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-NR-009`, where a theta-quotient representation still exposes the original orientation.
4. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-POS-006`, the closest positive theta/self-pairing branch-separation control.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H638`, the closest source-labelled relation-functional/signature control.

## Closest primary literature

- Polishchuk, [Massey and Fukaya products on elliptic curves](https://arxiv.org/abs/math/9803017), computes triple products and Kronecker identities but gives no finite-field DLP functional.
- Polishchuk, [`A_infinity`-structures on an elliptic curve](https://arxiv.org/abs/math/0001048), shows the role of triple products in elliptic bundle categories but not a source-normalized scalar decoder.
- Polishchuk, [A-infinity algebras associated with elliptic curves and Eisenstein–Kronecker series](https://arxiv.org/abs/1604.07888), gives explicit higher products in a different analytic/algebraic setting.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.iacr.org/archive/eurocrypt1997/12330062/12330062.pdf), supplies the generic square-root baseline that any usable non-generic channel must escape.

No checked source supplies the quotient-by-map-span, finite-field normalization, or
masked-scalar descent claimed here. Novelty is unverified and applicability may fail.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, a target-independent factor base, optional fixed cover, line-bundle collection, defining systems, and map-span basis.
2. Compute `m_3` symbolically and prove independence from all allowed representative changes after the frozen normalization.
3. On exhaustive tiny curves, evaluate `mu` for every source tuple and quotient its values by all known map-induced functionals.
4. Derive and machine-check the `A_infinity` composition identity for verified factor-base relations.
5. Collect enough source-labelled relations to calibrate every factor-base quantity and any required secondary state.
6. Evaluate the same normalized functional on randomized `Q+[t]P` relations.
7. Solve the preregistered bounded-degree equation or complete residual list for `x+t`, subtract `t`, and retain every candidate.
8. Independently verify the unique recovered `x` by `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` group operations with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let factor-base size be `B=N^beta`, setup exponent
`a`, per-source `mu` evaluation exponent `kappa`, reciprocal relation and target
densities `N^delta,N^delta_t`, relation-calibration exponent `ell`, residual scalar-list
exponent `rho_mu`, candidate verification exponent `rho_mu`, and memory exponent `nu`.
The complete time exponent is
`lambda=max(a,delta+kappa,ell,delta_t+kappa,rho_mu,2beta)`.
When one source evaluation emits one usable row, calibration requires
`ell>=beta+delta+kappa`; this `N^beta` row term may not be hidden in a functional oracle.
All defining-system searches, exceptional branches, map-span reduction, discarded
relations, and target equations are included. If `mu` separates scalars only through
an `N`-dimensional dictionary or order-`N` root-of-unity DLP, set the corresponding
time or memory exponent to `1`.

## Likely fatal obstruction

For `N!=p`, any genuinely additive scalar-valued functional into the characteristic-`p`
additive group kills `<P>`, while a multiplicative value capable of carrying order `N`
usually moves the DLP to `mu_N`. Higher products may depend on a defining system, reduce
by `A_infinity` identities to theta/pairing data in the known map span, or yield a
relation invariant with no injective target equation. Separating `N` scalars may require
degree, output, or residual list `N^(1/2)` or larger.

## Proof track

Construct the normalized finite-field `m_3`; prove representative independence and
complete source evaluation; compute the exact quotient by known maps; derive the masked
scalar equation and bound its degree, density, calibration, residual list, verification,
and memory so `lambda,nu<1/2`.

## Disproof track

Prove the normalized functional vanishes or lies in the known map/pairing span, find a
defining-system ambiguity, show no bounded-degree target equation exists, or prove the
residual list/evaluator/representation has exponent at least `1/2`.

## Positive and negative controls

- Positive category control: reproduce a published triple-product identity on a supported tiny curve/field model.
- Positive source control: planted extension data with a known nonzero `m_3` and exact normalization.
- Negative map-span control: ordinary pullback, norm, trace, Weil-pairing, and binary relation functionals must reduce to zero in the quotient.
- Negative torsion control: random ordinary prime-order curves with no exceptional automorphisms.
- Target control: random masked known scalars and completely blind challenge points.
- Leakage control: prohibit scalar-labelled bases, target-chosen bundles, post-hoc defining systems, and discarded residual candidates.

## Quantitative promotion and falsification gates

Phase 1 requires one symbolic normalization valid on complete charts, zero representative
or composition mismatches on exhaustive instances, and a quotient rank at least one
after all known map-span columns are included. Phase 2 uses at least 20 ordinary curves
per size, three seeds, at least 1,000 verified relations and 100 blind masked targets at
each of the two largest completed sizes. Promotion requires zero false scalar recoveries,
upper 95% residual-list exponent `rho_mu<=0.20`, upper 95% `lambda,nu<=0.45`, and
stable leave-largest-size-out fits.

Falsify the scoped mechanism if the quotient is identically zero on every exhaustive
ordinary curve, any normalization/composition error is independently reproduced, target
equations leave at least `N^(1/2)` candidates with lower 95% confidence, or complete-cost
`lambda>=0.50` on every arm. Infrastructure failure is not mathematical falsification.

## Artifact plan

- Retired draft contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-069_massey_functional_preflight.yaml`
- Derivation: `ideas/artifacts/ECDLP-IDEA-069/massey_identity.md`
- Map-span basis: `ideas/artifacts/ECDLP-IDEA-069/map_span.yaml`
- Implementation: `ideas/artifacts/ECDLP-IDEA-069/massey_functional.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-069/verify_functional.sage`
- Runs: `ideas/artifacts/ECDLP-IDEA-069/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-069/analysis.md`
- Retain defining systems, bases, extension representatives, values, quotient matrices, sources, relations, target equations, candidates, commands, seeds, environment, resources, stdout, and stderr.

## Interpretation boundary

The deferred hypothesis is toy, heuristic, model-bound, novelty-unverified, and deliberately
high-risk. A nonzero Massey product, correct `A_infinity` identity, or relation label is
not a cryptanalytic result. Promotion requires a complete blind scalar recovery path and
matched rho/BSGS costs.

## Exactly one next executable action

1. Derive `ideas/artifacts/ECDLP-IDEA-069/massey_identity.md` with explicit finite-field line bundles, Ext/Hom bases, defining systems, normalization, complete known-map span, and a machine-checkable masked-scalar equation before requesting a replacement contract.
