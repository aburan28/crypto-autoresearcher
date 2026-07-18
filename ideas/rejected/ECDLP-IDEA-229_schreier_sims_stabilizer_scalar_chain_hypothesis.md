# ECDLP-IDEA-229 — Schreier–Sims stabilizer scalar chain

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `rejected_scoped_explicit_point_action_has_degree_N_and_transversal_floor`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and group-theoretic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a stabilizer chain, membership certificate, or recovered planted permutation is not an ECDLP break.

## Falsifiable hypothesis

The elliptic prime-order subgroup has a public compact permutation action on endpoint/source states with a short base and strong generating set. Schreier–Sims sifting would expose scalar digits and exact source branches with time and memory below rho and BSGS.

## Mechanism-new operation

The claimed operation is **endpoint-derived permutation action followed by stabilizer-chain scalar/source sifting**. The standard explicit-point formulation is scoped-rejected: an action of a prime-cyclic group has only fixed or size-`N` orbits, so any nontrivial faithful permutation action has degree at least `N`. Explicit generator images, Schreier trees, transversals, or point labels then carry `N`-scale state or a scalar table. Degree alone does not prove that every implicit action representation stores `N` words; such an oracle would be a different operation and must bound construction, sifting, source return, and memory end to end. A nonfaithful compact action erases the scalar.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of size `N`, action domain, generators, base, and source decoder are scalar-blind.
2. The action has sub-square-root represented state and query cost, and any implicit representation avoids enumerating an explicit orbit, factor-point, source-completion table, or transversal.
3. Sifting returns exact scalar orientation and every signed factor-source branch on all strata.
4. Action construction, orbits, Schreier trees, transversals, output, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`prime_cyclic_elliptic_action | compact_permutation_domain | base_strong_generating_set | Schreier_sift_scalar_and_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the compact structured-coordinate gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, the known-scalar CM-orbit compression negative.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless action-edge floor.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition boundary.
5. `inputs/ledger_inventory.json` — imported `P1474`, the orbit sampling/recurrence boundary.

## Closest primary literature

- Sims, [Computation with permutation groups](https://doi.org/10.1145/800204.806264), introduces the computational stabilizer-chain framework for supplied permutation actions.
- Brown, Finkelstein, and Purdom, [A new base change algorithm for permutation groups](https://doi.org/10.1137/0218070), accelerates strong-generating-set manipulation after the action is supplied.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/3-540-69053-0_18), supplies the generic-group boundary against which any public action must be separated.

No checked source constructs the claimed compact elliptic action. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the action domain, generators, base, strong generators, sifting rule, masks, source decoder, and verifier.
2. Construct the action and Schreier data without enumerating the scalar orbit or source transitions.
3. For known endpoints, sift to exact factor scalars or relation sources and independently verify every output.
4. Collect full factor logs and any required independent relation rows.
5. Apply the identical action to fresh `Q+[t]P`, sift all candidates, subtract `t`, and preserve ambiguity.
6. Accept only `[x]P=Q`, charging action degree, orbit/transversal state, output, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup cost `N^a,N^a_m`, reciprocal base/target success densities `N^delta,N^delta_t`, sifting plus exact source inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log completion `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Permutation degree, representation of generator images, Schreier orbits, transversals, point labels, and implicit-oracle queries enter setup/memory. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

For a group of prime order `N`, every point stabilizer is either the whole group or trivial. Hence every orbit has size `1` or `N`, and a nontrivial faithful action contains an `N`-point orbit. Standard explicit Schreier–Sims stores generator action on those points plus Schreier trees/coset transversals, so the admitted point-action route reaches `N`-scale state; labelling the orbit by elliptic states is the full scalar/source orientation. This does not rule out every implicit action oracle, but no such oracle with exact scalar/source sifting and charged sub-rho costs is supplied.

## Proof track

Exhibit a compact implicit representation of the unavoidable `N`-point orbit, with exact scalar/source sifting and complete `lambda,mu<=0.45` without explicit transversals.

## Disproof track

Apply orbit-stabilizer and explicit Schreier–Sims storage accounting, show a nonfaithful action collides on scalars, or demonstrate that the proposed implicit oracle materializes an explicit scalar/source table or has exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied small permutation groups with known bases, strong generators, and independently checked sifts.
- Negative controls: trivial prime-cyclic actions, regular `N`-point actions, CM orbit tables, IDEA-043/099/177/217, rho, and BSGS.

## Quantitative promotion and falsification gates

This explicit-point version is scoped-rejected. Reopening requires an implicit representation of the necessary degree-`N` action with setup/query/memory exponents at most `0.45`, exact scalar/source recall, zero collisions, no explicit orbit/transversal table, and complete `lambda,mu<=0.45`. Explicit `N`-state, nonfaithful collisions, or either complete exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-229/prime_cyclic_action_degree_gate.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-229/action_collision_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-229/independent_schreier_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-229/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified scoped algorithm negative. Finite checks would be toy and projections heuristic and model-bound. A stabilizer chain, correct sift, membership proof, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-229/prime_cyclic_action_degree_gate.md` proving the degree and explicit-transversal state floor for the standard point-action route or exhibiting a charged scalar-blind implicit-action exception.
