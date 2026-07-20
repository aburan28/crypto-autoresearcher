# ECDLP-IDEA-228 — Bernstein–Sato V-filtration source atomizer

## Status and claim labels

- Class: `algebraic-geometry`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `rejected_scoped_generic_smooth_fiber_has_no_source_v_filtration`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and theorem audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a b-function, V-filtration, or singularity invariant is not an ECDLP break.

## Falsifiable hypothesis

A target-independent characteristic-zero lift of the endpoint relation ideal, or a fully specified positive-characteristic analogue, has a Bernstein–Sato/V-filtration-style invariant whose graded pieces separate exact signed factor-source strata before root enumeration. A canonical graded-piece inverse would yield relations and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **b-function/V-filtration stratification followed by exact source-piece inversion**. The direct generic form is scoped-rejected: the all-distinct reduced zero-dimensional relation fiber is smooth finite étale, so singularity/nearby-cycle invariants are locally trivial. Collision strata are lower density; computing D-modules or component ideals for the full source fiber is a dense elimination backend.

## Assumptions

1. Public `E/F_p`, prime-order subgroup, factor base `F` of size `B=N^beta`, endpoint ideal, embedding, and filtration are target-independent.
2. A functorial characteristic-zero lift or a positive-characteristic analogue is specified, preserves the relevant source strata, and charges lift/precision/descent costs.
3. The b-function and graded pieces are computed without dense resultants, source component ideals, or enumerated roots.
4. Graded pieces invert canonically to every generic and exceptional signed point source.
5. Ideal construction, lift/analogue, D-module state, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_relation_ideal | Bernstein_Sato_b_function | Kashiwara_Malgrange_V_filtration | graded_piece_exact_source_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate compression gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the source-ancestry floor.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the conditional implicit-membership frontier.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing endpoint source generator.

## Closest primary literature

- Kashiwara, [B-functions and holonomic systems](https://eudml.org/doc/142441), develops b-functions and V-filtration methods for supplied analytic/algebraic data.
- Budur, Mustaţă, and Saito, [Bernstein–Sato polynomials of arbitrary varieties](https://arxiv.org/abs/math/0408408), extends the invariant to ideals and relates it to V-filtrations.
- Mustaţă, [Bernstein–Sato polynomials in positive characteristic](https://arxiv.org/abs/0711.3794), gives a positive-characteristic analogue whose transfer and computation would still need to be specified and charged here.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the endpoint ideal but not a source-separating singularity invariant.

The classical Kashiwara–Malgrange and Budur–Mustaţă–Saito machinery is characteristic-zero; no checked source supplies the required lift/analogue together with the proposed exact source inversion. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the endpoint ideal, characteristic-zero lift or positive-characteristic analogue, graph embedding, b-function algorithm, filtration, graded inverse, masks, and verifier.
2. Compute the lifted/analogous filtration for known endpoints without decomposing the source algebra into roots/components.
3. Return every exact signed factor point from accepted graded pieces and independently verify each relation.
4. Collect full rank, solve and verify all factor-base logarithms.
5. Apply the identical filtration to fresh `Q+[t]P`, invert target pieces, substitute logs, and subtract `t`.
6. Preserve exceptional-stratum ambiguity and accept only `[x]P=Q`, charging D-module/output memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, filtration plus exact source inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`, the complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Lift and precision costs, ideal degrees, Weyl-algebra/D-module or analogue state, primary pieces, roots, and output are charged. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

On the generic all-distinct fiber there is no singularity for a V-filtration to atomize: the local algebra is a product of separable fields after splitting. b-functions record aggregate singularity exponents, not root identities. Refining to point components requires the primary decomposition/root isolation it was meant to avoid; exceptional collision strata cannot supply generic relation density.

## Proof track

Specify the lift or positive-characteristic analogue, then prove a nontrivial target-uniform graded source biconditional on the generic smooth stratum and complete `lambda,mu<=0.45` without component ideals.

## Disproof track

Show that no admitted lift/analogue preserves a nontrivial generic source filtration, apply the Jacobian/étale criterion to show trivial generic nearby cycles, exhibit equal invariants with different sources, or derive dense module/component state or exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied singular hypersurfaces with known b-functions and labelled vanishing-cycle components.
- Negative controls: smooth finite étale fibers, source-label deletion, IDEA-080/097/105/193/216, dense Macaulay/resultant backends, rho, and BSGS.

## Quantitative promotion and falsification gates

This generic direct version is scoped-rejected. Reopening requires a charged lift or positive-characteristic analogue, nontrivial source-separating generic graded pieces, 100% exact-source recall, zero false components, no dense component ideal, and `lambda,mu<=0.45`. Failure of the lift/analogue, generic étaleness, aggregate invariance, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-228/generic_v_filtration_gate.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-228/b_function_source_collisions.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-228/independent_v_filtration_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-228/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified scoped algebraic-geometry negative. Finite checks would be toy and projections heuristic and model-bound. A b-function, singularity computation, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-228/generic_v_filtration_gate.md` applying the Jacobian/étale criterion to the generic all-distinct fiber and deciding whether any nontrivial source-bearing graded piece remains.
