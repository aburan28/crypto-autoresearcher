# ECDLP-IDEA-126 — Picard-Lefschetz vanishing-cycle source lift

## Status and claim labels

- Class: `topological-transfer`
- Risk band: `high-risk`
- State: `rejected_path_dependent_cycles_not_exact_finite_field_sources`
- Evidence scale: structural and primary-literature preflight only; no experiment ran
- Scale labels: any prospective computation would be `toy`; cost claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a monodromy matrix, vanishing cycle, relation certificate, or correct toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Embed the target-parameterized elliptic five-source relation fibers in a Lefschetz degeneration whose vanishing cycles give sparse branch coordinates; transport from a reference fiber to a target would then lift exact signed factor-base sources by Picard-Lefschetz monodromy below rho. The hypothesis fails if cycles depend on path/basis, aggregate multiple rational points, fail finite-field specialization, or cannot invert to exact source tuples.

## Mechanism-new operation

The proposed operation is **monodromy-transported vanishing-cycle source lifting**. One would choose a public degeneration and distinguished paths, compute a sparse Picard-Lefschetz action, and attach to each vanishing thimble a canonical rational factor-base source branch that can be transported to the target fiber.

This is new only if the cycle-to-source map is scalar-blind, path-independent after a public normalization, complete over finite fields, and cheaper than explicit branch tracking. A cover or isogeny variant, homology signature, intersection form, monodromy orbit, dense resultant, or path chosen after seeing sources is a duplicate or control. The preflight rejects the declared generic mechanism because vanishing cycles encode homological degeneration data, not a canonical enumeration of finite-field rational source points.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and factor base `F` of size `B=N^beta`.
2. The five-source projective relation family admits a public lift and Lefschetz pencil with controlled bad fibers, signs, infinity, repetitions, and nonreduced strata.
3. A bounded set of vanishing cycles and sparse Picard-Lefschetz transformations is computable uniformly in `p` and the target.
4. Each exact signed factor-base tuple corresponds biconditionally to a publicly normalized vanishing cycle or thimble, including multiplicity and Frobenius descent.
5. Transport paths and orientations are fixed before target/source evaluation and require neither source enumeration nor a dense discriminant table.
6. Lifting, discriminant computation, monodromy, cycle/source inversion, relation collection, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`target_relation_Lefschetz_pencil | vanishing_cycle_basis | Picard_Lefschetz_transport | finite_field_source_lift | path_normalized_biconditional`

The removal test is a canonical finite-field rational-source inverse from a sparse cycle representation. A same-field cover, fixed multiplicity transfer, homology-only certificate, monodromy statistic, dense branch table, or post-hoc path selector is a duplicate or control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-017`, where branch-divisor automorphisms and naive cubic gluing do not explain a hidden quotient; monodromy must supply a genuine source inverse rather than another symmetry diagnostic.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-030`, where a genuine cyclic cover has deck/Prym maps scalar or zero on the visible elliptic factor; a vanishing-cycle lift must escape the same scalar transfer.
3. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-045`, where an extra Prym factor still lacks a useful native-prime correspondence; topological transport needs an explicit non-scalar rational bridge.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, where exact transition polynomials densify under backward composition; explicit branch continuation cannot simply materialize those states.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where one transition norm is exact but composition becomes dense; a sparse monodromy word is useful only with a complete source inverse that removes this obstruction.

## Closest primary literature

- Seidel, [Vanishing cycles and mutation](https://arxiv.org/abs/math/0007115), develops Picard-Lefschetz theory through Floer-theoretic vanishing cycles; it does not identify finite-field factor-base source tuples.
- Seidel, [More about vanishing cycles and mutation](https://arxiv.org/abs/math/0010032), studies invariance under choices and mutations of vanishing paths; that machinery highlights rather than removes the path/basis issue for exact sources.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic relation family but no monodromy-based source descent.

No checked primary source proves a canonical finite-field cycle/source biconditional or a complete sub-rho ECDLP path. Novelty remains unverified; the declared homological lift is rejected.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, a projective lift, Lefschetz pencil, reference fiber, vanishing paths, orientations, Frobenius action, and exceptional-fiber policy.
2. Construct the discriminant and a sparse vanishing-cycle basis without enumerating target fibers or factor-base tuples.
3. Compute target transport words and apply Picard-Lefschetz transformations to obtain every target cycle coordinate.
4. Invert the transported cycles to exact signed factor-base tuples with multiplicity and independently verify curve membership and elliptic addition.
5. Apply the identical frozen transport to known multiples until `B+sigma` verified rows have rank `B`, charging all bad paths and outputs.
6. Solve and independently verify every factor-base logarithm.
7. Transport to blind `Q+[t]P`, decode complete sources, substitute factor logs, subtract `t`, and retain all candidates.
8. Accept only `[x]P=Q` and preserve discriminant, path, monodromy, source, rank, factor-log, descent, time, and memory receipts.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; lift, pencil, and discriminant setup time/memory be `N^a,N^a_m`; cycle basis, monodromy generators, and transport state be `N^c,N^c_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; transport, source inversion, and exact verification per query be `N^k`; cycle/source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time/memory be `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

`mu=max(a_m,c_m,beta+o,ell_m,u)`.

All discriminant coefficients, bad fibers, path words, intersection matrices, Frobenius descent, source branches, failed targets, relation rows, factor logs, and blind candidates are charged. A sparse monodromy matrix does not compensate for a dense cycle/source dictionary or discriminant.

## Likely fatal obstruction

Vanishing cycles are homology classes defined relative to a degeneration, path system, and basis. Hurwitz moves change their presentation while preserving aggregate categorical or intersection data. Multiple rational points and source tuples can contribute to the same cycle class, and Frobenius can permute branches without a rational chosen lift. Making the map source-biconditional requires tracking individual algebraic branches through the discriminant, which is the dense source-continuation problem. Existing cover/Prym negatives further show that auxiliary geometry can be genuine while its map on the native prime-order factor remains scalar, zero, or fixed multiplicity.

## Proof track

Historic survival would require a public lift valid across the finite-field family, a path-normalization theorem, a Frobenius-compatible cycle/source biconditional, sparse discriminant and transport construction, and `lambda,mu<=0.45` through blind descent. No such rational source theorem is present, and homology alone is non-biconditional, so the declared mechanism is rejected.

## Disproof track

Exhibit two distinct rational source tuples with the same transported homology class; show a Hurwitz move changes the chosen source while preserving all recorded cycle data; show Frobenius has no rational fixed lift; reduce source recovery to explicit branch continuation; or derive `lambda>=1/2` or `mu>=1/2`. Any one closes the mechanism.

## Positive and negative controls

- Classical Lefschetz fibrations with independently known vanishing cycles and Picard-Lefschetz matrices.
- The same fibrations under two Hurwitz-related path bases to test presentation dependence.
- Planted zero-dimensional families with unique branches versus colliding branches sharing homology data.
- Exhaustive toy elliptic relation fibers over several extensions with explicit Frobenius orbits.
- Frozen cyclic-cover/Prym transfer negatives and dense branch continuation as matched controls.
- Blind known-log targets with independent tuple/scalar verification and matched rho/BSGS accounting.

## Quantitative promotion and falsification gates

This record is rejected. Historic promotion required a path- and Frobenius-compatible source biconditional; `100%` exhaustive source recall with zero false cycles; discriminant, transport, source-output, and complete-path `lambda,mu<=0.45`; and no branch table. Falsify on any homology collision, path-dependent source, nonrational lift, fixed-multiplicity/scalar transfer, missed branch, post-hoc selector, or time/memory exponent at least `0.5`.

## Artifact plan

- Cycle/source obstruction gate: `ideas/artifacts/ECDLP-IDEA-126/vanishing_cycle_source_gate.md`
- Prospective pencil and path fixtures: `ideas/artifacts/ECDLP-IDEA-126/pencil_fixtures.json`
- Prospective monodromy analyzer: `ideas/artifacts/ECDLP-IDEA-126/picard_lefschetz.sage`
- Independent rational-source verifier: `ideas/artifacts/ECDLP-IDEA-126/verify_sources.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-126/cost_analysis.md`

These are prospective paths only; no artifact or experiment was created.

## Interpretation boundary

This is a rejected, novelty-unverified, high-risk transfer proposal. Its cost model is heuristic and model-bound and any future evidence would begin at toy scale. A vanishing cycle, monodromy action, cover, relation, or correct toy scalar is not a generic ECDLP improvement. No breakthrough is claimed.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-126/vanishing_cycle_source_gate.md` formalizing path and Frobenius invariance and exhibit one identical-cycle/different-rational-source toy fiber before any monodromy implementation is authorized.
