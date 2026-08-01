# ECDLP-IDEA-216 — Normalization–conductor-square source splitter

## Status and claim labels

- Class: `algebraic-geometry`
- Risk band: `conservative`
- Top lane: `-`
- State: `rejected_scoped_generic_etale_conductor_trivial_or_source_fiber_required`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and generic-fiber theorem audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; normalization, a conductor square, or a valid component is not an ECDLP break.

## Falsifiable hypothesis

The fixed-target signed relation scheme has a normalization whose conductor pullback square exposes a bounded branch module. Gluing data would split that module into primitive exact factor sources, enabling relation collection and blind target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **normalization/conductor gluing followed by primitive source splitting**, rather than dense elimination. The scoped generic version is rejected: the reduced zero-dimensional all-distinct fiber is finite étale and already normal, so its conductor is trivial; constructing the fiber or splitting its finite algebra into primitive labelled idempotents performs the source/root finding.

## Assumptions

1. Public curve/group/factor base `B=N^beta` and endpoint are frozen with an implicit fixed-target relation scheme constructed without source enumeration.
2. Normalization and conductor are computed from a compact presentation, not a dense resultant or explicit finite fiber.
3. A bounded branch module persists generically and returns every exact signed source across all strata.
4. Presentation, normalization, conductor, idempotent/root splitting, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`implicit_fixed_target_relation_scheme | normalization_conductor_pullback_square | bounded_branch_module | conductor_gluing_to_exact_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, the nonhomomorphic cover/branch-label route.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the missing arithmetic source-fiber generator.
3. `inputs/ledger_inventory.json` — imported `ECFG-H682`, the normalization/decomposition hypothesis boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the implicit-coordinate representation route.
5. `inputs/ledger_inventory.json` — imported `ECFG-H633`, the component/branch source-recovery barrier.

## Closest primary literature

- Ferrand, [Conducteur, descente et pincement](https://www.numdam.org/articles/10.24033/bsmf.2455/), develops conductor squares and gluing for a supplied normalization.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the elliptic endpoint scheme but not its compact source algebra.

No checked source gives the compact relation presentation and labelled conductor inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the saturated relation presentation, normalization, conductor, gluing decoder, masks, and verifier.
2. Prove generic dimension/reducedness and build the algebra without enumerating the finite source fiber.
3. For known endpoints, split conductor data to exact signed factor tuples and verify every row.
4. Collect full rank, solve and verify factor-base logarithms.
5. Apply the same construction to fresh `Q+[t]P`, substitute logs, subtract `t`, preserve ambiguity, and final-verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho and BSGS cost `N^(1/2+o(1))`; BSGS memory matches. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, normalization/source query `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Dense fiber degree, root splitting, and output enter the setup/query terms; both exponents must be at most `0.45`.

## Likely fatal obstruction

On the generic all-distinct fixed-target fiber, a reduced zero-dimensional `F_p` algebra is finite étale and normal, so the conductor square is tautological. Exceptional collision strata do not provide generic relation density. Even after normalization, primitive idempotent splitting is factor/root finding and labelling them requires the missing source inverse.

## Proof track

Prove a compact generic relation algebra with nontrivial bounded conductor and exact all-strata source gluing, followed by complete `lambda,mu<=0.45`.

## Disproof track

Use the Jacobian criterion to prove generic étaleness/normality and zero conductor, show normalization construction materializes the source algebra, reduce idempotent splitting to root finding, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied singular finite schemes with known normalization/conductor and planted branch labels.
- Negative controls: generic finite étale algebras, exceptional collision strata, dense resultants, explicit source fibers, rho, and BSGS.

## Quantitative promotion and falsification gates

This scoped version is rejected. Reopening requires nontrivial generic conductor, compact algebra/state at most `B^2.25`, query at most `B^1.25`, 100% source recall, zero false tuples, no explicit fiber/root deck, and `lambda,mu<=0.45`. Generic normality, trivial conductor, source-root dependence, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective square: `ideas/artifacts/ECDLP-IDEA-216/conductor_square_spec.md`
- Prospective generic gate: `ideas/artifacts/ECDLP-IDEA-216/generic_etale_gate.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-216/fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-216/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-216/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified scoped negative. Finite checks would be toy and projections heuristic and model-bound. A normalization, conductor computation, component, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-216/generic_etale_gate.md` applying the Jacobian criterion and normalization/conductor construction to the symbolic generic all-distinct signed five-source fiber, certifying whether its conductor is trivial.
