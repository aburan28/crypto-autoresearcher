# ECDLP-IDEA-337 — Barrington width-five source branch program

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_branch_program_decides_supplied_predicate_and_satisfying_assignment_recovery_is_unsupplied`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a bounded-width decision program, accepting product, valid relation, or toy path is not an ECDLP break.

## Falsifiable hypothesis

The endpoint relation predicate has a target-independent logarithmic-depth formula whose Barrington width-five permutation program can be evaluated and inverted to a satisfying exact signed source tuple within the P1553 bounds.

## Mechanism-new operation

The screened operation is **compile a shallow relation formula into a width-five non-solvable permutation branching program, evaluate its group product, and recover a satisfying source assignment from an accepting evaluation**. This merges with IDEAs 070, 120, 135, 154, 217, 229, 305, and 327: Barrington compiles a supplied Boolean formula and decides its value. The program is deterministic for a fixed assignment; there is no nondeterministic accepting instruction path to backtrack. A formula over explicit source choices plus a satisfying-assignment recovery procedure is the missing source circuit/inverse; width does not bound program length or factor access.

## Assumptions

1. A logarithmic-depth endpoint formula exists without enumerated factor choices or dense transitions.
2. Its branching-program length, instruction access, and construction fit `B^(9/4)` and per-target evaluation fits `B^(5/4)`.
3. One accepting evaluation has a compact canonical inverse to every exact signed source tuple.
4. Formula construction, instructions, products, satisfying-assignment recovery, output, rank, factor logs, descent, verification, and memory are charged.
5. The same program works on fresh masked targets without target-specific advice.

## Semantic fingerprint

`endpoint_relation_formula | Barrington_width5_permutation_program | group_product_decision | satisfying_assignment_source_recovery | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H680`, the recursive source-resolving circuit hypothesis.
2. `inputs/ledger_inventory.json` — imported `P1477`, the serial endpoint-state representation.
3. `inputs/ledger_inventory.json` — imported `P1478`, the compact transition and dense composition control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry-edge boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE2-TRANSLATED-CIRCUIT-TRADEOFF`, the compact predicate versus exact source-unranking tradeoff.

## Closest primary literature

- Barrington, [Bounded-width polynomial-size branching programs recognize exactly those languages in NC1](https://doi.org/10.1016/0022-0000(89)90037-8), compiles a supplied bounded-depth Boolean formula into a width-five program; it is a decision result, not witness extraction.
- Valiant, [Holographic algorithms](https://doi.org/10.1137/070682575), provides a contrasting aggregate finite-state reduction and makes clear that conserved decision/count values need not retain individual correspondences.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a shallow source formula or witness program.

No checked source constructs the formula, bounds its length/access, or supplies exact source replay and full descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, coloured factor decks, formula grammar, permutation program, instruction oracle, replay rule, source policy, masks, and verifier.
2. Compile known-log endpoints without source tables, evaluate the program, replay every accepted exact tuple, and verify relations.
3. Collect at least `B=N^(1/5)` independent rows, solve all factor logs, and independently verify them.
4. Apply the identical program family and replay rule to fresh scalar-blind masked targets.
5. Substitute logs, remove masks, retain all recovered satisfying assignments, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, formula/program evaluation excluding emission `N^q,N^q_m`, verified rank `N^r`, satisfying-assignment output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Formula size/depth, program length, every instruction query, group products, assignment-recovery queries/branches, output, and verification are charged; `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Barrington's theorem preserves decision complexity for a supplied formula. It does not discover satisfying assignments. The elliptic formula must query explicit source choices or transitions, and an accepting final group product contains no canonical inverse to the satisfying assignment. Repeated decision/self-reduction still requires the source-free formula and must charge every query and recovered assignment. Program length can encode the entire source search despite constant width.

## Proof track

Construct a source-free logarithmic-depth formula and sub-gate program, prove exact all-strata satisfying-assignment recovery, then establish relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Show the formula contains source-index variables/transitions, construct two satisfying assignments with the same accepting product and no canonical inversion, or charge repeated decision queries, program length, and assignment output beyond the gates.

## Positive and negative controls

- Positive: supplied NC1 formulas with unique planted assignments and explicit provenance must decide and replay correctly.
- Negative: equal-output programs with multiple assignments and source-permuted instruction tables must not yield preferred elliptic points.
- Baselines: IDEAs 070/120/135/154/217/229/305/327, explicit formula search, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with source-free formula and replay theorems, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if instructions query source edges, program length/recovery state reaches `B^3`, satisfying assignments collide under the accepting product, or either exponent reaches `0.50`.
- Fast decision of a supplied formula is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-337/formula_source_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-337/accepting_product_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-337/program_length_cost_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-337/cost_analysis.md`

## Interpretation boundary

This rejects the stated branching-program witness route, not bounded-width programs generally. A correct decision or relation is not exact source recovery, a complete ECDLP algorithm, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-337/formula_source_input_receipt.md` expanding the shallow formula leaves and marking every leaf that queries a source choice, transition, or completion.
