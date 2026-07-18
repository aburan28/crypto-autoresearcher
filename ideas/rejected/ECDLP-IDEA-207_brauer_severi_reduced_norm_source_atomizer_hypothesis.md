# ECDLP-IDEA-207 — Brauer–Severi reduced-norm source atomizer

## Status and claim labels

- Class: `arithmetic-transfer`
- Risk band: `high-risk`
- Top lane: `-`
- State: `rejected_scoped_finite_field_brauer_split_has_no_canonical_source_ideals`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and theorem audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a reduced norm, split algebra, or valid minimal ideal is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-conditioned cyclic algebra built from public Miller/Kummer symbols contains a reduced-norm-zero element whose minimal right ideals are canonically and biconditionally labelled by exact signed factor-base sources. Factoring this element and repeating on blind masks gives relations, factor logs, and target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **reduced-norm singularization followed by Severi–Brauer minimal-ideal atomization**. It is not merely a norm/resultant backend because the claimed new step is a canonical ideal-to-point inverse. The specified finite-field version is rejected: the Brauer group of a finite field is trivial, so the algebra splits, while choosing and labelling minimal ideals is noncanonical and restores a basis, orientation, or source dictionary.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of order `N`, factor base `F` of size `B=N^beta`, and target are frozen.
2. The cyclic algebra and norm-zero element are constructed from an endpoint without source tuples or hidden scalar orientation.
3. Minimal right ideals exist over the base field and correspond one-to-one to all signed factor points and multiplicities.
4. Splitting data, basis changes, ideal factorization, output, rank, factor logs, descent, and memory are charged.
5. No torsion basis, scalar-labelled cocycle, or explicit ideal table is treated as public for free.

## Semantic fingerprint

`endpoint_Miller_Kummer_symbol | finite_field_cyclic_algebra | reduced_norm_zero | canonical_minimal_right_ideal_atoms | exact_factor_point_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H640`, the sign/orientation relation boundary.
2. `inputs/ledger_inventory.json` — imported `OFQ-autolab-05`, the open torsion-orientation division question.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-H003`, the transfer-orientation hypothesis boundary.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the nonhomomorphic cover-label possibility.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the nearest failed transfer of a native prime-order ECDLP factor.

## Closest primary literature

- Merkurjev and Suslin, [Cohomology of Severi–Brauer varieties and the norm residue homomorphism](https://doi.org/10.1070/IM1983v021n02ABEH001793), supplies the central-simple-algebra and norm-residue setting.
- Lang, [Algebraic groups over finite fields](https://doi.org/10.2307/1969607), supplies the finite-field torsor/splitting boundary behind the scoped collapse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the elliptic relation baseline.

No checked source constructs the proposed endpoint algebra and canonical point-labelled ideal inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the algebra presentation, endpoint element, splitting convention, ideal decoder, masks, and verifier.
2. Prove reduced-norm singularity is biconditional with the complete signed source fiber.
3. Construct the algebra for known endpoints without source advice and factor every minimal right ideal.
4. Map ideals to exact signed factor points, preserving repeats, infinity, multiplicity, and empty fibers, then verify all rows.
5. Collect at least `B+sigma` independent rows and charge duplicated or conjugate ideals.
6. Solve and verify factor-base logarithms.
7. Apply the identical algebra construction to fresh `Q+[r]P` masks.
8. Substitute logs, subtract masks, preserve ambiguity, and verify the recovered scalar.

## Full rho/BSGS cost model

Rho and BSGS have matched `N^(1/2+o(1))` time, with BSGS also using that memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, algebra query plus exact ideal inverse `N^q,N^q_m`, independent rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both time and memory exponents must be at most `0.45`; an uncharged splitting field or torsion basis invalidates the model.

## Likely fatal obstruction

Over `F_p` every central simple algebra splits. Its minimal right ideals form a projective family rather than a canonical source list. A source-sensitive selection needs a matrix basis, torsion orientation, or endpoint-conditioned idempotent carrying the very labels to be recovered; invariant reduced norms aggregate them.

## Proof track

Give an explicit endpoint algebra and element, prove a base-field canonical ideal decomposition and exact point inverse on all strata, and derive complete `lambda,mu<=0.45`.

## Disproof track

Prove the algebra is split and ideal choices are conjugate under an automorphism transitive on source labels, exhibit two source fibers with identical norm data, or charge orientation/state to exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied split matrix algebras with planted labelled minimal ideals.
- Negative control: conjugate bases and ideals with identical reduced norms but permuted factor labels.
- Negative control: ordinary norm/resultant, pairings, torsion-basis orientation, rho, and BSGS.

## Quantitative promotion and falsification gates

This scoped version is rejected. Reopening requires a basis-free canonical ideal section, 100% exact source recall, zero false ideals, no torsion/source advice, setup at most `B^2.25`, query at most `B^1.25`, and `lambda,mu<=0.45`. Transitive ideal ambiguity, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-207/finite_field_ideal_section_theorem.md`
- Prospective inverse specification: `ideas/artifacts/ECDLP-IDEA-207/ideal_point_inverse_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-207/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified scoped negative. Any finite calculation would be toy and any asymptotic extrapolation heuristic and model-bound. Algebra splitting, a norm identity, or a correct ideal is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-207/finite_field_ideal_section_theorem.md` proving either a basis-free endpoint-to-minimal-ideal source section or transitive split-algebra ambiguity for the declared cyclic-algebra family.
