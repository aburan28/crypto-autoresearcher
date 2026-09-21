# ECDLP-IDEA-201 — Orlik–Solomon master-function source extractor

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_arrangement_algebra_requires_source_labelled_divisors`
- Cohort: `20260718-d`
- Evidence scale: literature and representation audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective finite checks are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a critical point, residue, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

The divisors contributed by factor-base sources admit a compact Orlik–Solomon/Aomoto algebra whose master-function critical points localize complete elliptic target fibers. Residues at those points can then be inverted to exact signed five-source tuples, yielding independent relations and masked descents below rho and BSGS.

## Mechanism-new operation

The proposed operation is **arrangement-combinatorial cohomology plus master-function critical-point inversion to labelled elliptic sources**. It is not a dense resultant or an ordinary residue solver: the claimed gain is a compact intersection-lattice representation and exact critical-point-to-source inverse. The audit finds that the hyperplanes/divisors and their weights are already source-labelled input, while Orlik–Solomon data aggregate intersection incidence rather than create the missing endpoint fiber.

## Assumptions

1. Public `E/F_p`, prime-order `G` of order `N`, factor base `F` of size `B=N^beta`, and target are frozen.
2. A target-independent arrangement or logarithmic-divisor model is built without enumerating factor-base tuples.
3. Its Orlik–Solomon/Aomoto representation and master-function system have size at most `B^2.25`.
4. Every critical point has a bounded, exact, all-strata signed-source inverse.
5. Arrangement construction, nonlinear reduction, residues, failed targets, rank, factor logs, blind descent, and memory are charged.

## Semantic fingerprint

`factor_base_logarithmic_divisors | compact_Orlik_Solomon_Aomoto_algebra | target_master_function_critical_points | residue_to_exact_signed_sources | blind_descent`

The fingerprint fails if divisor incidence is source-enumerated, if critical points are aggregate-only, or if nonlinear elliptic constraints are handed to a generic eliminator.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1478`, the sparse one-transition norm whose composition becomes dense.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where an aggregate norm loses row/source identity.
4. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the implicit membership and source-query rectangle.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the exact transposed aggregate-rank control.

## Closest primary literature

- Orlik and Solomon, [Combinatorics and topology of complements of hyperplanes](https://doi.org/10.1007/BF01392549), constructs an algebra from a supplied hyperplane intersection lattice.
- Orlik and Terao, [The number of critical points of a product of powers of linear functions](https://doi.org/10.1007/BF01241120), counts master-function critical points but does not canonically label elliptic sources.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies nonlinear elliptic fibers rather than a hyperplane arrangement inverse.

No checked primary source supplies the proposed source extractor; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the divisor/arrangement functor, weights, critical equations, charts, masks, and verifier.
2. Build the compact intersection algebra without enumerating source intersections.
3. Specialize known-log endpoints, solve the admitted critical system, and invert every residue to exact signed sources.
4. Verify all relations and preserve repeated divisors, dependent sets, poles, nonreduced points, infinity, and empty fibers.
5. Collect full-rank rows, solve factor-base logarithms, and verify them.
6. Apply the identical frozen representation to fresh masked targets `Q+[r]P`.
7. Substitute logs, subtract masks, retain ambiguity, and verify `[x]P=Q`.
8. Charge construction, algebra size, critical solving, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one critical solve and source inverse be `N^q,N^q_m`; independently ranked rows per query be `N^r`; output and ambiguity be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both must be at most `0.45`; aggregate cohomology or critical-point counts alone do not enter as a gain.

## Likely fatal obstruction

Orlik–Solomon and Aomoto constructions take the list of source hyperplanes/divisors and their incidence as input. Generic elliptic addition fibers are nonlinear; linearizing them introduces a large arrangement or elimination algebra. Critical points and residues aggregate supplied divisors and have no canonical map to the five original factor points, so exact replay restores `B` source marks or the dense source deck.

## Proof track

Construct a source-free arrangement functor of size at most `B^2.25`, prove a target-uniform critical-point/source biconditional on every stratum, and derive `lambda,mu<=0.45` through blind descent.

## Disproof track

Show the intersection lattice requires source-tuple incidence, exhibit distinct source fibers with identical Orlik–Solomon/Aomoto data, reduce critical inversion to dense primary decomposition, or derive `max(lambda,mu)>=0.50`.

## Positive and negative controls

- Positive control: a supplied toy hyperplane arrangement with independently labelled critical points.
- Negative control: aggregate characteristic polynomials, Betti numbers, or critical-point counts.
- Negative control: source-labelled divisor decks, dense nonlinear elimination, post-hoc residue matching, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires total arrangement/algebra size at most `B^2.25`, query at most `B^1.25`, exact 100% source/multiplicity recall, zero false tuples, no source-tuple incidence input, and `lambda,mu<=0.45`. A `B^3` incidence object, aggregate-only residue, one source collision, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective representation theorem: `ideas/artifacts/ECDLP-IDEA-201/orlik_solomon_size_theorem.md`
- Prospective critical inverse: `ideas/artifacts/ECDLP-IDEA-201/master_function_source_inverse_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-201/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified representation analysis. Tests would be toy; asymptotic projections are heuristic and model-bound. A cohomology class, critical point, exact source, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-201/orlik_solomon_size_theorem.md` proving a source-free sub-`B^2.25` arrangement model with exact critical-point source inversion or proving that its intersection data contains `Omega(B^3)` labelled incidence.
