# ECDLP-IDEA-152 — Rectangular BGG/Tate source kernel

## Status and claim labels

- Class: `algebraic-representation`
- Risk band: `high-risk-theorem-gated`
- State: `deferred_needs_rectangular_size_and_source_biconditional_theorem`
- Cohort: `20260718-a`
- Evidence scale: literature and semantic audit only; no experiment ran
- Contract posture: deferred theorem track; no run authorized
- Scale labels: every prospective measurement is `toy`; complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid Tate block, BGG correspondence, kernel vector, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The coherent sheaf of a target-specialized five-source elliptic relation scheme admits a bounded rectangular window of its multigraded BGG/Tate resolution whose structured kernel module is constructible directly from compact public equations and has a canonical atomization into exact signed factor-base sources, including primary-local data for nonreduced fibers. If block construction, module atomization, and source inversion remain strictly sub-rho, the rectangular window could replace dense elimination while retaining complete ancestry.

## Mechanism-new operation

The proposed operation is **target-local rectangular Tate-window extraction with a canonically atomized exterior-algebra source module**. The compact relation ideal is sheafified in a frozen multigraded projective embedding, transported through the BGG correspondence, and truncated to a justified rectangle of homological and internal degrees. At target `R`, a designated differential block `D_R`, together with a public multiplication/module action, must support a canonical reduced joint-eigenspectrum and nonreduced primary-local decomposition satisfying

`canonical atoms of ker D_R <-> all exact signed factor-base tuples summing to R`,

including multiplicity and exceptional strata. A vector-space kernel basis alone does not qualify: arbitrary linear combinations are not point atoms.

The rectangle must be derived without computing the full minimal free resolution, dense Macaulay matrices, common norms, resultants, or source-labelled columns. A small block selected after inspecting sources, a kernel giving only cohomology dimensions, or a Tate resolution computed from a materialized relation scheme is a duplicate or control.

## Assumptions

1. Public `E/F_p`, prime-order `<P>` of order `N`, target `Q=[x]P`, factor base `F` of size `B=N^beta`, and fixed five-source arity are frozen.
2. A scalar-blind multigraded projective model handles signs, source ordering, repeated points, infinity, and nonreduced target fibers.
3. The relevant sheaf and Tate differential rectangle are constructible directly from compact equations with dimensions and coefficient growth below the cost gate.
4. The rectangular kernel carries a computable module/multiplication structure whose joint eigenspectrum on reduced fibers and joint primary/nilpotent local algebra on nonreduced fibers invert to exact point identities and multiplicities.
5. The rectangle is chosen by a target-independent theorem, not a post-hoc degree window.
6. Resolution construction, exterior-algebra operations, kernel computation, source output, relation retries, linear algebra, masked descent, coefficient bits, and memory are charged.

## Semantic fingerprint

`target_specialized_relation_sheaf | multigraded_BGG_exterior_algebra_transform | theorem_fixed_rectangular_Tate_window | canonical_joint_primary_kernel_atomization | exact_masked_descent`

The novelty gate is a compact theorem-fixed rectangular block with exact source inversion. Full resolutions, dense syzygy computation, Ulrich/Chow matrices, derived-Tor diagnostics, relation-only cohomology, and post-hoc kernel labelling are duplicates or controls.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator that the Tate block must provide rather than assume.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact public value matrices remain full rank and resist fixed tensor compression.
3. `inputs/ledger_inventory.json` — imported `P1477`, where source-faithful forward and backward state polynomials become dense.
4. `inputs/ledger_inventory.json` — imported `P1478`, where a compact exact transition invariant becomes quadratic on source-complete composition.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`, where tested compact public feature spaces fail to contain factor-log orientation.

## Closest primary literature

- Eisenbud, Fløystad, and Schreyer, [Sheaf Cohomology and Free Resolutions over Exterior Algebras](https://arxiv.org/abs/math/0104203), give explicit BGG/Tate constructions and Beilinson monads; they do not prove a small source-biconditional window for elliptic relation fibers.
- Eisenbud, Erman, and Schreyer, [Tate Resolutions for Products of Projective Spaces](https://arxiv.org/abs/1411.5724), give the directly relevant multigraded Tate construction; its computable windows encode cohomology, not a canonical point-source atomization.
- Bernstein, Gelʹfand, and Gelʹfand, [Algebraic bundles over P^n and problems of linear algebra](https://www.mathnet.ru/eng/faa2008), establish the neighboring correspondence between projective geometry and exterior-algebra complexes; they do not remove resolution construction or source output.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic relation equations but no BGG/Tate source kernel.

No checked primary source supplies the theorem-fixed rectangle, exact source biconditional, or complete sub-rho descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, the multigraded relation model, signs, ordering, exceptional strata, degree rectangle, masks, and independent verifier.
2. Construct a target-independent compact recipe for the relation sheaf and the selected Tate differential block without enumerating source tuples or a full resolution.
3. For each known-log target `R_j=[r_j]P`, specialize the recipe, build `D_R_j`, compute its structured kernel module, and atomize it by joint eigenspectrum or full primary/nilpotent local algebra into exact signed factor-base identities and multiplicities.
4. Verify every emitted tuple by curve membership and elliptic addition; preserve misses, false kernel atoms, nonreduced components, repeated points, infinity, and rank jumps.
5. Collect `B+sigma` verified rows of rank `B`, solve factor-base logarithms, and verify them independently.
6. For fresh masks `R_t=Q+[t]P`, apply the identical rectangle and inverse, substitute verified factor logs, and subtract `t`.
7. Retain every ambiguity candidate and accept only `x` satisfying `[x]P=Q`.
8. Report sheaf construction, block dimensions, coefficient payload, kernels, source output, retries, linear algebra, descent, time, and peak memory against rho and BSGS.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; target-independent sheaf/Tate derivation cost time/memory be `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; specialization, kernel computation, multiplication-action construction, joint eigenspectrum or primary-local splitting, source inversion, and verification per query be `N^q,N^q_m`; relation output and target ambiguity exponents be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every free-module rank, exterior-algebra coefficient, syzygy step, target specialization, kernel vector, source lift, retry, and output is charged. A narrow-looking degree rectangle whose entries or construction encode `B^5` source data fails. Toy block-size slopes are heuristic and model-bound.

## Likely fatal obstruction

BGG/Tate correspondence preserves information; it does not itself compress the module or construct its resolution cheaply. Betti ranks and differential entries can encode the full Hilbert function and scheme length of the source fiber. A rectangle large enough to distinguish exact points may therefore have dense dimensions or coefficients comparable to Macaulay elimination, while a smaller rectangle can retain only cohomology dimensions and lose source identities. Even a small vector-space kernel has no canonical point basis: arbitrary basis changes mix sources, and nonreduced multiplicity needs primary/nilpotent local data. A source biconditional therefore needs a charged multiplication/module action and canonical atomization theorem beyond the correspondence.

## Proof track

Prove a target-independent degree rectangle; derive its entries directly from the compact elliptic circuit; construct and charge a multiplication/module action; bound every module rank, coefficient, kernel operation, joint eigenspectrum, and primary-local split below `N^(1/2-epsilon)`; prove exact reduced and nonreduced source recovery; and establish `lambda,mu<=0.45` through relation calibration and masked target descent without reducing to a screened dense elimination route.

## Disproof track

Exhibit source-distinct fibers with identical rectangular Tate data; prove the required rectangle or its construction has dimension, coefficient payload, or output at least `N^0.5`; reduce it to a full resolution, dense Macaulay matrix, common norm, or existing scalar-linear kernel; find an exceptional stratum where multiplicity or identity is lost; or derive either complete exponent at least `0.5`.

## Positive and negative controls

- Planted zero-dimensional schemes with supplied small Tate resolutions and known source points.
- Source-distinct schemes sharing Hilbert functions or Betti tables.
- Random dense systems matched for multidegree and scheme length.
- Full minimal resolutions and dense Macaulay matrices as explicit cost controls.
- Exhaustive toy elliptic fibers with signs, repeats, infinity, and nonreduced components.
- Direct enumeration, rho, BSGS, and independent source/scalar verification.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires a checked multigraded rectangle theorem, a canonical reduced/nonreduced kernel-atomization theorem, and formal `lambda,mu<=0.45` including the splitter. A later approved toy preflight must recover `100%` of exhaustive sources with `0` false atoms across at least three frozen curves and every exceptional stratum. Costs strictly above `0.45` and below `0.50` are inconclusive and non-promoting. Falsify on one missed source or multiplicity, one source-distinct collision, basis-dependent atoms, post-hoc rectangle selection, a dense/full-resolution reduction, or either complete exponent at least `0.5`.

## Artifact plan

- Prospective rectangle theorem: `ideas/artifacts/ECDLP-IDEA-152/rectangular_tate_source_theorem.md`
- Frozen projective and exceptional-stratum fixtures: `ideas/artifacts/ECDLP-IDEA-152/fixtures.json`
- Prospective BGG/Tate constructor: `ideas/artifacts/ECDLP-IDEA-152/rectangular_tate_kernel.m2`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-152/verify_sources.py`
- Complete block and cost receipt: `ideas/artifacts/ECDLP-IDEA-152/cost_analysis.md`

All paths are prospective; no experiment or contract is authorized.

## Interpretation boundary

This is a deferred, theorem-gated, novelty-unverified proposal. Any finite computation is toy, and every asymptotic projection is heuristic and model-bound until the rectangle and source-biconditional theorems exist. A correct Tate differential, kernel dimension, relation, or recovered toy scalar is not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-152/rectangular_tate_source_theorem.md` proving explicit multigraded block-size bounds and a charged canonical joint-eigenspectrum/primary-local source atomization before implementing a Tate-resolution experiment.
