# ECDLP-IDEA-401 — Wiener–Itô chaos source projection

## Status and claim labels

- Class: `homogeneous_chaos_decomposition`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_no_canonical_exact_gaussian_lift_and_low_chaos_erases_factor_atoms`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct chaos expansion or low-degree projection is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-uniform exact Gaussian functional encodes the signed relation fiber, and a bounded set of Wiener–Itô homogeneous-chaos kernels retains enough occurrence provenance for restriction-stable inversion to factor points and complete blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the finite relation indicator to a Gaussian functional, decompose it orthogonally into multiple stochastic integrals by chaos degree, restrict selected kernels, and invert them to exact source atoms**. It is not merely a Fourier backend: the proposed operation uses degree-orthogonal stochastic kernels and their purported atom inverse.

## Assumptions

1. A canonical exact Gaussian lift is public, finite, and uniform across curves and targets.
2. Subgate chaos degrees retain zero-versus-nonzero membership under every deck restriction.
3. Kernel coefficients canonically determine factor occurrences, signs, repetitions, and pairing.
4. Exact arithmetic replaces analytic approximation without coefficient or precision blowup.
5. Lift, kernels, projection, inverse, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`finite_elliptic_relation_indicator | exact_Gaussian_lift | Wiener_Ito_homogeneous_chaos_projection | chaos_kernel_to_factor_atom_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; endpoint membership must return an exact restricted source.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; aggregate transforms require a typed inverse to points.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`; quadratic summaries do not preserve full nonlinear sources.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; phase and occurrence orientation remain charged.
5. `inputs/ledger_inventory.json` — imported `P1479`; every restricted fresh target must reuse the same transform.

## Closest primary literature

- Wiener, [The homogeneous chaos](https://doi.org/10.2307/2371268), gives the orthogonal chaos decomposition for supplied Gaussian functionals.
- Itô, [Multiple Wiener integral](https://doi.org/10.2969/jmsj/00310157), develops multiple stochastic integrals and orthogonality, not a finite-field atom inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives finite-field relation equations without a canonical Gaussian lift.

No checked source supplies the proposed exact lift and source-atom inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, Gaussian space, exact lift, chaos basis, truncation, restrictions, and verifier.
2. Construct target-independent lift and kernels within `B^(9/4+o(1))`, charging every coefficient and precision bit.
3. For known-log targets, project the restricted functional, decide exact existence, invert kernels to one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging empty fibers, cancellations, ambiguity, output, and dependent rows; solve factor logs.
5. Apply the unchanged lift and projection to fresh scalar-blind `Q+[t]P` targets.
6. Substitute factor logs, remove `t`, retain all inverse branches, and verify `[x]P=Q`.
7. Charge lift, chaos expansion, restriction, inversion, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Wiener chaos is defined after a Gaussian probability space and functional are supplied. There is no canonical exact Gaussian lift of a generic finite-field relation fiber. Low chaos retains moments or aggregate kernels and can erase a rare exact zero; the full expansion or atom-faithful kernel family grows with the source dictionary. This meets IDEAs 001, 048, 104, 191, 303, 320, and 367 at the aggregate-to-atom boundary.

## Proof track

Construct an exact public lift, prove a bounded chaos degree is exact under arbitrary restrictions, prove kernel-to-occurrence inversion, and certify `lambda,mu<=0.45`.

## Disproof track

Exhibit two fibers with identical retained kernels but different exact sources, show the lift imports source state, or prove exact degree/state/output above the caps.

## Positive and negative controls

- Positive: supplied finite Gaussian polynomial chaoses with planted kernels and labelled atoms must reconstruct exactly.
- Negative: equal low moments with different supports, isolated rare atoms, truncated high-degree components, relabelled factors, signed strata, restrictions, and blind targets.
- Baselines: IDEAs 001/048/104/191/303/320/367, full expansion, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a canonical exact lift, restriction-stable bounded chaos, exact atom inverse, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one equal-kernel/different-source pair, source-bearing lift, missing atom, cap violation, or either exponent at least `0.50`.
- A correct toy chaos decomposition is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-401/gaussian_lift_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-401/chaos_kernel_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-401/restricted_atom_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-401/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic chaos route, not Wiener–Itô theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; expansion correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-401/gaussian_lift_obligations.md` and classify each random variable, kernel, and inverse datum as endpoint-derived or source-bearing.
