# ECDLP-IDEA-155 — Finite-Radon source tomography

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_projection_observability`
- Cohort: `20260718-a`
- Evidence scale: semantic and literature audit only; no experiment ran
- Contract posture: no contract; unapproved; zero runs authorized
- Scale labels: every prospective finite test is `toy`; all complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; exact toy inversion, a valid source tuple, or a recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For each decomposition endpoint `R`, its unknown source measure on the factor-base tuple space admits `N^(c+o(1))`, `c<1/2`, public endpoint-computable finite-Radon projections along target-independent algebraic foliations. A source-faithful inverse transform recovers exact signed factor-base atoms in query exponent `q<1/2`, enabling relation collection and blind target descent with complete time and memory below rho and BSGS.

## Mechanism-new operation

The proposed operation is **endpoint-induced finite-Radon projection followed by exact atomic tomography**. A valid successor must first freeze an explicit affine/grid embedding of the signed ordered tuple space and a target-independent family of lines or algebraic fibers; it would then map the source measure to sums over that defined family, reconstruct the atomic measure by a matching finite Fourier-slice/Radon inverse, and read the point sources.

A standard Fourier transform, supplied projection table, full ambient image reconstruction, generic linear solver, or post-hoc source selector is a duplicate or control. The operation is new only if `R` itself yields the required projections without enumerating preimages and if inversion returns exact point labels.

The record is rejected as underspecified and duplicative because it freezes no affine tuple geometry or measurement family, while the endpoint exposes only the elliptic sum rather than independent measurements of the unknown tuple. For natural explicit families, computing those measurements appears to be the original source-fiber enumeration. Fourier-slice conversion also enters the occupied full-rank additive-character lane, while full ambient reconstruction restores the source-state payload. This is not a general no-go for every sparse tomography family.

## Assumptions

1. `E/F_p`, `<P>`, `N`, `Q=[x]P`, and target-independent signed factor base `F` of size `B=N^beta` are public.
2. An explicit affine/grid embedding of the signed ordered tuple space, projection directions, and algebraic fibrations are frozen from `E,F,N`, never chosen after observing source hits.
3. Every projection is computable from `R` without scalar coordinates, source enumeration, a supplied witness, or an ambient length-`N` array.
4. The inverse is exact over the relevant finite field and handles multiplicities, signs, repetitions, infinity, and exceptional charts.
5. Projection generation, storage, inversion, output, failed targets, rank, linear algebra, descent, and verification are fully charged.
6. All finite evidence remains toy and all asymptotic inference heuristic and model-bound.

## Semantic fingerprint

`endpoint_source_measure | target_independent_algebraic_Radon_fibrations | endpoint_computable_projection_data | source_faithful_inverse_tomography | blind_masked_descent`

The load-bearing novelty is endpoint observability of a sub-rho source-faithful projection family. Inverting supplied projections or reconstructing only aggregate counts does not qualify.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, where deterministic additive-character kernels have full pair-state rank.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, where full-phase and nonlinear character matrices show no useful low-rank source gap.
3. `inputs/ledger_inventory.json` — imported `P1434`, which isolates the missing public source-fiber generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, where explicit recursive source-edge transcripts do not compress.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, which fixes the complete five-term query, setup, source, rank, and descent boundary.

## Closest primary literature

- Matúš and Flusser, [Image representation via a finite Radon transform](https://doi.org/10.1109/34.254058), gives finite-array projection and inversion identities, not endpoint-generated projections of an implicit elliptic source fiber.
- Shliferstein and Chien, [Switching components and the ambiguity problem in the reconstruction of pictures from their projections](https://doi.org/10.1016/0031-3203(78)90004-3), exhibit projection-preserving switching components for specific discrete picture geometries; they do not imply ambiguity for an unspecified elliptic measurement family.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring point-decomposition relation.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/BFb0052236), supplies the generic-group comparison boundary.

No cited source constructs the required source measure, endpoint projection oracle, or exact point inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta,m`, projection directions, fibration equations, normalization, and complete addition charts.
2. Define the exact source measure for each endpoint and an independently enumerable truth representation for tiny fixtures.
3. Derive each prospective Radon projection directly from `R`, recording every field operation and retained coefficient.
4. Invert the frozen projection family to all exact signed source tuples; retain all multiplicities and switching ambiguities.
5. On known-log targets, verify tuples by direct elliptic addition and retain `B+sigma` independent rows of rank `B`.
6. Solve and independently verify every factor-base logarithm.
7. Repeat unchanged for fresh `Q+[t]P`, substitute factor logs, enumerate ambiguity, subtract `t`, and verify `[x]P=Q`.
8. Compare complete setup, projection, inversion, output, rank, descent, verification, and peak memory with rho and BSGS.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let setup exponents be `a,a_m`; projection-family construction and retained representation exponent be `c`; complete projection/inversion query and workspace exponents be `q,q_m`; inverse useful-row and target densities be `delta,delta_t`; source-output exponent be `o`; factor-log linear-algebra exponents be `ell,ell_m`; and ambiguity exponent be `u`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Projection acquisition is included; supplied-measure or supplied-projection timing is invalid. Full image arrays, Fourier tables, switching-component lists, and source output count toward memory.

## Likely fatal obstruction

Radon inversion is useful only after projection values are supplied, and this record gives no endpoint formula for any defined tuple-space measurement. For a particular frozen family, deriving one projection may require summing over compatible tuples, while full inversion may reconstruct the ambient source array. Some discrete projection families admit switching components, but that ambiguity is family-specific; every successor must prove or refute injectivity on its explicitly defined elliptic source-measure class rather than assume a universal nullspace.

## Proof track

Give explicit algebraic foliations, prove endpoint formulas for every projection without source enumeration, prove injectivity on the exact source-measure class, construct the source inverse, and derive `c,q,q_m,lambda,mu<=0.45`.

## Disproof track

For one explicitly frozen measurement geometry, exhibit two distinct source measures with identical projections, prove projection acquisition is equivalent to source counting/enumeration, reduce the construction to the full-rank character kernels, or show that exact inversion stores or touches a `B^2`-or-larger ambient image.

## Positive and negative controls

- Positive tomography control: sparse finite images with supplied projections and exact known inverse.
- Positive elliptic correctness control: exhaustive tiny source measures and all projections.
- Negative identifiability control: matched switching-component image pairs only for the exact projection family that admits them.
- Mechanism control: full finite Fourier/Radon reconstruction and explicit source enumeration.
- Character control: ledger additive-character and full-phase matrices.
- Leakage control: forbid supplied projections, scalar indices, target-selected directions, and discarded inverse branches.

## Quantitative promotion and falsification gates

A fresh successor requires zero projection or source errors through exhaustive 16-bit fixtures, at least 1,000 verified relations and 100 blind descents at each of two largest toy sizes, upper 95% `c,q,q_m<=0.20`, no ambient object above `N^0.45`, and complete `lambda,mu<=0.45`. Falsify on one indistinguishable source pair, one projection requiring source enumeration, one missed source, or complete `lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Prospective observability theorem: `ideas/artifacts/ECDLP-IDEA-155/finite_radon_observability_theorem.md`
- Prospective switching fixtures: `ideas/artifacts/ECDLP-IDEA-155/switching_components.json`
- Prospective projection implementation: `ideas/artifacts/ECDLP-IDEA-155/radon_projection.py`
- Prospective independent inverse verifier: `ideas/artifacts/ECDLP-IDEA-155/verify_tomography.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-155/cost_analysis.md`

No contract, experiment, run, or prospective artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified representation evidence. A correct finite-Radon inverse or valid toy source proves only scoped functionality. All finite tests would be toy, all scaling claims heuristic and model-bound, and no such result is a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-155/finite_radon_observability_theorem.md` freezing one affine signed-tuple geometry and projection family, then deciding endpoint computability and injectivity without evaluating the original source-fiber sum.
