# ECDLP-IDEA-204 — Gorenstein-liaison residual source inversion

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_linkage_requires_source_fiber_ideal_and_preserves_degree_traffic`
- Cohort: `20260718-d`
- Evidence scale: literature and degree audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective finite checks are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a linked residual, exact relation, or valid source tuple is not an ECDLP break.

## Falsifiable hypothesis

The endpoint-conditioned five-source fiber can be embedded in a low-degree arithmetically Gorenstein complete intersection whose residual scheme has sub-`B^2.25` degree and a canonical inverse to the original signed sources. Computing the residual rather than the full fiber would yield independent relations and masked descents below rho and BSGS.

## Mechanism-new operation

The proposed operation is **Gorenstein linkage of a large source fiber to a small residual plus canonical residual-to-source inversion**. It is not merely a different resultant: its load-bearing claim is that linkage changes the represented object before enumeration. The audit rejects the current version because linkage starts from an ideal of the source fiber and a containing complete intersection; constructing either with source fidelity already performs the missing enumeration, while degree conservation prevents an asymptotically tiny residual for free.

## Assumptions

1. Public `E/F_p`, prime-order group of size `N`, factor base `B=N^beta`, and target are frozen.
2. The source-fiber ideal and containing Gorenstein complete intersection are constructed without source enumeration or dense elimination.
3. The complete intersection and residual have total representation size at most `B^2.25`.
4. The residual has a canonical exact inverse to all signed sources on nonreduced and exceptional strata.
5. Ideal construction, saturation/colon operations, degree, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_five_source_scheme | low_degree_Gorenstein_complete_intersection | liaison_residual_compression | canonical_residual_to_exact_sources | blind_descent`

The fingerprint fails if the source ideal is materialized, if the complete intersection has dense fiber degree, or if the residual is matched back to sources post hoc.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1478`, the sparse one-transition/dense-composition norm boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the source-recoverable materialized-product control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the aggregate norm/source-loss boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the required source-query rectangle.

## Closest primary literature

- Peskine and Szpiro, [Liaison des variétés algébriques I](http://eudml.org/doc/142303), develops linkage through a containing complete intersection.
- Dwork, [On the zeta function of a hypersurface](https://doi.org/10.1007/BF02684275), is a nearby aggregate hypersurface representation control, not a source inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the endpoint relation variety whose source restriction remains the missing input.

No checked primary source supplies the proposed compact canonical residual inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the source scheme, complete-intersection grammar, linkage/colon operations, charts, masks, and verifier.
2. Construct the target-independent ambient and endpoint-specialized linkage without enumerating source tuples.
3. Compute residuals for known-log endpoints and invert every residual point to exact signed factor-base sources.
4. Verify relations and preserve embedded components, multiplicities, repeats, poles, infinity, and empty fibers.
5. Collect independent rows, solve factor-base logs, and verify them.
6. Apply the identical frozen linkage to fresh masked targets `Q+[r]P`.
7. Substitute logs, subtract masks, retain ambiguity, and accept only `[x]P=Q`.
8. Charge construction, degrees, colon/saturation work, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one linkage/residual inverse cost `N^q,N^q_m`; ranked rows/query be `N^r`; output and ambiguity be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both must be at most `0.45`; the full degrees of the source scheme and complete intersection are charged even if the residual is small.

## Likely fatal obstruction

Linkage requires `I(X)` and a complete intersection `C` containing `X`; a source-sensitive `I(X)` or `C` already contains the missing factor-base fiber. In the zero-dimensional proper-intersection model, `deg(C)=deg(X)+deg(Y)`, so replacing a high-degree source scheme by a small residual `Y` still requires a comparably high-degree `C`. Liaison does not canonically remember which five factor points produced a residual point.

## Proof track

Construct a sub-`B^2.25` source-free complete intersection containing every endpoint fiber, prove residual degree and exact all-strata inverse bounds, and derive `lambda,mu<=0.45` through blind descent.

## Disproof track

Prove any containing complete intersection has degree/description at least the source fiber, show the source ideal is an input oracle, exhibit residual points with multiple source preimages, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied small linked zero-dimensional schemes with independently known residual/source correspondence.
- Negative control: dense endpoint ideals and complete intersections containing explicitly enumerated source fibers.
- Negative control: residual degree without inverse labels, post-hoc source matching, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires total construction and represented degree at most `B^2.25`, query at most `B^1.25`, 100% source/multiplicity recall, zero false tuples, no source-fiber ideal oracle, and `lambda,mu<=0.45`. Degree/traffic `Omega(B^3)`, a noncanonical inverse, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective degree theorem: `ideas/artifacts/ECDLP-IDEA-204/liaison_degree_theorem.md`
- Prospective inverse specification: `ideas/artifacts/ECDLP-IDEA-204/residual_source_inverse_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-204/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified representation analysis. Finite checks would be toy and scaling heuristic and model-bound. A residual, exact relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-204/liaison_degree_theorem.md` constructing a source-free sub-`B^2.25` complete intersection with canonical residual-source inverse or proving that degree conservation and ideal input force `Omega(B^3)` represented source traffic.
