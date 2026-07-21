# ECDLP-IDEA-402 — Postnikov k-invariant source tower

## Status and claim labels

- Class: `homotopy_tower_source_routing`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_finite_source_fiber_is_discrete_so_pi0_is_the_source_list_and_higher_layers_are_empty_or_supplied`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Postnikov tower or k-invariant calculation is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible connected topological realization of each relation fiber has a bounded Postnikov tower whose homotopy groups and k-invariants route a target through successive exact lifting problems to one occurrence-labelled factor tuple below rho and BSGS.

## Mechanism-new operation

The screened operation is **replace a source fiber by successive Eilenberg–Mac Lane fibrations, compute its homotopy groups and k-invariants, solve the layerwise obstruction problems, and lift back to exact factor occurrences**. Its proposed information flow is layered homotopy obstruction routing rather than homology alone.

## Assumptions

1. A public finite topological realization preserves every signed source and restriction exactly.
2. The realization is connected without adding source-labelled paths or cells.
3. A bounded number of compact homotopy groups and k-invariants separates source occurrences.
4. Layerwise lifts are canonical, restriction-stable, and subgate across all strata.
5. Realization, tower, invariants, obstruction solves, source lift, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`finite_relation_fiber_realization | Postnikov_successive_EM_fibrations | k_invariant_obstruction_routing | tower_lift_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; exact endpoint existence must lead to a source, not only a topological certificate.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; aggregate invariants require a point-faithful inverse.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; source occurrence labels and all restrictions remain part of the interface.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless paths retain source-distinct edges.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-labelled cells or paths are explicit source edges.

## Closest primary literature

- Postnikov, [Investigations in the homotopy theory of continuous mappings](https://bookstore.ams.org/trans2/7), develops successive homotopy stages and k-invariants for supplied spaces.
- Whitehead, [Combinatorial homotopy I](https://doi.org/10.1090/S0002-9947-1949-0030759-2), provides the cellular homotopy setting but no finite-field source compiler.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies a discrete algebraic fiber rather than a connected source space.

No checked source constructs the proposed point-faithful connected realization and layer inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, realization functor, cells, basepoints, tower convention, k-invariants, restrictions, and verifier.
2. Build the target-independent realization and tower within `B^(9/4+o(1))` without one cell or path per source transition.
3. For known-log targets, solve exact restricted existence layer by layer, lift through every fibration to one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging disconnected components, obstruction failures, ambiguity, output, and dependent rows; solve factor logs.
5. Reuse the unchanged tower on fresh scalar-blind `Q+[t]P` targets and restrictions.
6. Substitute factor logs, remove `t`, retain all lift branches, and verify `[x]P=Q`.
7. Charge realization/tower construction, invariant arithmetic, lifting, source output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The actual finite source fiber is discrete: all higher homotopy groups vanish, while `pi_0` is exactly the source list. Connecting the points adds paths and cells whose attachment data encode source transitions; retaining only genuine higher invariants loses the occurrence labels. This meets IDEAs 069, 181, 232, 251, 298, and 317 at the component-versus-source boundary.

## Proof track

Construct an endpoint-only compact connected realization, prove bounded Postnikov data are source-biconditional under restrictions, give a canonical point lift, and certify `lambda,mu<=0.45`.

## Disproof track

Prove the realization's `pi_0` or attachment data materialize the source deck, exhibit equal tower data with different occurrences, or show tower/lift cost above the caps.

## Positive and negative controls

- Positive: supplied finite CW complexes with known Postnikov towers and planted lifts must replay exact obstruction classes.
- Negative: discrete equal-cardinality fibers with relabelled points, connected thickenings with equal tower invariants, omitted components, signed strata, restrictions, and blind targets.
- Baselines: IDEAs 069/181/232/251/298/317, explicit source-cell complexes, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with compact endpoint-only realization, exact restricted point lift, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on source-sized `pi_0`, one source-labelled cell/path, equal-tower/different-source collision, cap violation, or either exponent at least `0.50`.
- A correct toy tower is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-402/postnikov_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-402/tower_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-402/restricted_lift_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-402/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic Postnikov route, not Postnikov theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; tower correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-402/postnikov_source_obligations.md` and classify every component, cell, path, homotopy group, k-invariant, and lift datum by source dependence.
