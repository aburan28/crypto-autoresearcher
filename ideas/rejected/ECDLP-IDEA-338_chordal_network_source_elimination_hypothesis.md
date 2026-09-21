# ECDLP-IDEA-338 — Chordal-network source elimination

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_solver_backend_requires_source_sparsity_and_separator_state`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: relative top-lane draft is retired, `review_required`, unapproved, and zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a compact ideal representation, membership test, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

The signed addition-tree ideal and factor-base constraints admit a target-independent bounded-width chordal network whose separators retain exact point provenance, so known-log rows and fresh masked-target decompositions can be recovered inside the P1553 campaign and query bounds.

## Mechanism-new operation

The screened operation is **decompose the source-labelled polynomial ideal into a chordal network of triangular sets and replay a compatible separator path to exact factor points**. Chordal networks are more specific than choosing another Grobner solver: the claimed gain requires a theorem that the elliptic constraint graph has bounded separator state after the sparse factor-base predicates are included. Without that theorem this is the supplied-factor join of IDEAs 098, 117, 266, and 325 with a different elimination schedule.

## Assumptions

1. The complete signed addition and factor-base ideal has a target-uniform chordal completion whose largest exact separator table, including provenance payload, has charged cardinality `B^(1/4+o(1))` or less.
2. Network construction does not materialize factor-base leaf products, dense resultants, or `B^3` transition state.
3. Every triangular path lifts all distinct, repeated, signed, infinity, singular, and ambiguous source strata.
4. Separator compatibility gives exact factor points, not only ideal membership or a component count.
5. Construction, failed paths, output, rank, factor logs, blind descent, verification, bit cost, and memory are charged.

## Semantic fingerprint

`signed_addition_tree_ideal | bounded_width_chordal_network | triangular_separator_paths | exact_point_provenance_replay | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1477`, where source-faithful forward and backward state polynomials become dense.
2. `inputs/ledger_inventory.json` — imported `P1478`, where one compact transition becomes a dense composed resultant.
3. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`, the exact one-transition positive control.
4. `inputs/ledger_inventory.json` — imported `P1480`, the structured solver-change control with unresolved source generation.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source membership and cost boundary.

## Closest primary literature

- Cifuentes and Parrilo, [Chordal Networks of Polynomial Ideals](https://doi.org/10.1137/16M106995X), decomposes supplied sparse polynomial ideals into triangular networks; it does not prove bounded width for the factor-base-constrained elliptic ideal or provide source labels.
- Cifuentes and Parrilo, [Exploiting Chordal Structure in Polynomial Ideals](https://doi.org/10.1137/151002666), is the direct sparse-elimination control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than a bounded separator theorem or exact factor-point replay.

No checked source supplies the claimed elliptic network and inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor decks, signed charts, ideal generators, chordal order, separator policy, masks, and verifier.
2. Build the network without target advice, source tables, dense resultants, or omitted strata.
3. Traverse known-log endpoints, emit every exact factor tuple, and independently verify each group relation.
4. Collect at least `B` independently ranked rows, solve all factor logs, and verify the solution.
5. Apply the identical network to fresh scalar-blind masked targets and retain every miss and ambiguity.
6. Substitute factor logs, remove masks, and accept a scalar only after `[x]P=Q`.
7. Serialize construction, traversal, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, network query excluding emission `N^q,N^q_m`, verified rank credit `N^r`, exact output `N^o`, ambiguity `N^u`, and factor-log work `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every separator table, triangular branch, field operation, failed path, and bit is charged; `0<=r<=o`. Promotion requires campaign, setup, state, and log exponents at most `0.45`, fresh-target exponent at most `0.25`, and exact all-strata output. Pollard rho has expected time exponent `0.50` with negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

The sparse addition chain ceases to be bounded-width when each leaf is restricted to an arbitrary factor deck and exact provenance is retained. Separator states then distinguish source leaves or encode the same dense transition/resultant payload, while chordal-network membership and component counts do not identify a factor tuple. This is a solver backend unless a new width-and-replay theorem removes that state.

## Proof track

Prove a target-independent chordal completion and triangular network of charged size below `B^(9/4)`, an exact all-strata source replay theorem, query below `B^(5/4)`, and complete `lambda,mu<=0.45`.

## Disproof track

Exhibit setup or separator state above `B^(9/4)`, a fresh query above `B^(5/4)`, two source tuples merged by the same path signature, a missing stratum, or a reduction to the supplied-factor join/dense-resultant controls.

## Positive and negative controls

- Positive: supplied bounded-treewidth polynomial systems with labelled triangular components must replay their known roots.
- Negative: source-permuted decks, dense random ideals with matched degrees, and membership-only networks must not emit preferred elliptic points.
- Baselines: IDEAs 098/117/266/325, explicit Grobner/resultant solving, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with zero source errors, 1,000 verified rows and 100 blind descents per large size, no source table, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify this version if charged setup/replay state exceeds `B^(9/4)`, a fresh query exceeds `B^(5/4)`, one source stratum is lost, the constructor uses target-specific advice, or either complete exponent reaches `0.50`.
- A faster solve or correct membership decision on supplied ideals is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-338/chordal_width_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-338/separator_source_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-338/all_strata_replay_spec.md`
- `ideas/artifacts/ECDLP-IDEA-338/cost_analysis.md`

## Interpretation boundary

This rejects the unsupplied bounded-width source network, not chordal elimination generally. All finite evidence would be toy, heuristic, model-bound, and novelty-unverified. Correctness, ideal membership, or a valid relation is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-338/chordal_width_obligations.md` expanding the factor-base-constrained primal graph and charging every separator state needed for exact source replay.
