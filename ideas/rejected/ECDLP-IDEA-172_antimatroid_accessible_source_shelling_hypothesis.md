# ECDLP-IDEA-172 — Antimatroid accessible-source shelling

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `none`
- State: `merged_rejected_extendibility_closure_oracle`
- Cohort: `20260718-c`
- Evidence scale: checked primary literature and semantic no-go only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: every prospective finite check is `toy`; all projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; accessibility, a greedy shelling, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For each endpoint, partial valid signed decompositions form a target-uniform antimatroid whose accessibility and anti-exchange structure admits a canonical greedy shelling. An endpoint-only closure oracle exposes exact factor-base sources one at a time without enumerating completions, yielding complete relation collection and blind masked descent below rho and BSGS.

## Mechanism-new operation

The operation is **antimatroid closure of extendible partial decompositions followed by accessible greedy source shelling**. Removal requires proofs of accessibility, union closure or the equivalent anti-exchange closure law, cheap endpoint-only closure, and exact source recovery. A supplied tuple, extendibility oracle, source-seeded feasible set, generic backtracking, or renamed shelling order is a control.

Independent review found direct overlap with IDEA-137/082/098: closure is source
extendibility, and branching over every accessible choice removes the greedy advantage.
The antimatroid vocabulary therefore does not add an endpoint-to-source operation.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta,m`, feasible-set encoding, closure rule, masks, tie-breaking, and verifier are frozen.
2. Extendible partial source sets form one antimatroid uniformly over known and blindly masked endpoints.
3. Greedy accessible steps recover every exact signed tuple, including repetitions represented as indexed atoms and exceptional strata.
4. Feasibility and closure are evaluated from endpoint data without completion search, scalar labels, or source advice.
5. Closure calls, branches, shelling output, rank, logs, descent, verification, and peak memory are charged.

## Semantic fingerprint

`endpoint_extendible_partial_sources | antimatroid_anti_exchange_closure | accessible_greedy_shelling | exact_source_atoms | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where source-distinct ancestry persists.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`, the staged generator and explicit `B^3` boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, where source-faithful serial states remain above budget.
5. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source query, rank, and descent gate.

## Closest primary literature

- Korte and Lovasz, [Greedoids and Linear Objective Functions](https://doi.org/10.1137/0605024), provides greedy feasibility structure and negative oracle context, not an elliptic closure oracle.
- Korte and Lovasz, [The intersection of matroids and antimatroids](https://doi.org/10.1016/0012-365X(88)90142-2), develops antimatroid/greedoid structure but no endpoint source inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies relation equations, not accessible closure.

No checked primary source supplies the proposed antimatroid source shelling; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze indexed signed atoms, partial-feasibility semantics, antimatroid closure, greedy rule, masks, and verifier.
2. Prove accessibility and union closure or anti-exchange on every endpoint fiber without inspecting a source tuple.
3. For known `R_j=[r_j]P`, query closure and greedily extend the empty feasible set through every admissible branch.
4. Decode maximal feasible sets to signed tuples; preserve closure collisions, branch orderings, misses, repeats, and output.
5. Verify sums, collect `B+sigma` independent relation rows of rank `B`, solve factor logs, and verify every log.
6. Apply the identical closure and shelling to fresh `Q+[t]P` masks.
7. Substitute factor logs, remove masks, retain all source and ordering candidates, and verify `[x]P=Q`.
8. Charge closure construction, feasibility calls, shelling branches, output, rank, descent, time, and bit memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let setup cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one complete closure/shelling query cost `N^q,N^q_m`; output and target ambiguity exponents be `o,u`; and factor-log algebra cost `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every feasibility bit, closure scan, branch, indexed repeat, maximal word, and failed endpoint is included.

## Likely fatal obstruction

Fixed-endpoint partial decomposition fibers are generally not antimatroids: two extendible partial tuples can have a union exceeding arity or incompatible with the endpoint, violating union closure, while deleting or greedily adding an atom need not preserve the chosen fixed-length fiber semantics. Defining feasibility as eventual extendibility only moves the original source search into the closure oracle.

## Proof track

An outside-scope successor must define multiplicity-aware feasible sets, prove antimatroid axioms and an exact maximal-set/source biconditional, construct a cheap endpoint-only closure oracle, and derive complete `lambda,mu<=0.45` descent.

## Disproof track

Give two feasible partial sets with infeasible union, an inaccessible nonempty set, a closure query equivalent to source completion, a lost multiplicity stratum, or a complete time or memory exponent at least `0.5`.

## Positive and negative controls

- Published antimatroids with explicit closure and greedily recoverable basic words.
- Planted source tuples with a supplied extendibility oracle.
- Fixed-cardinality subset systems that fail union closure and source fibers with multiple incompatible completions.
- Direct backtracking, shelling renamings, explicit `B^2/B^3` decks, rho, BSGS, and blind-target fixtures.

## Quantitative promotion and falsification gates

This version is rejected. Reopening requires a new multiplicity-aware antimatroid theorem, endpoint-only closure, exact source recovery, and `lambda,mu<=0.45`. One axiom failure, supplied completion bit, lost or false tuple, hidden source ordering, or either complete exponent at least `0.5` is falsifying.

## Artifact plan

- Prospective scoped no-go: `ideas/artifacts/ECDLP-IDEA-172/antimatroid_axiom_no_go.md`
- Prospective closure and shelling specification: `ideas/artifacts/ECDLP-IDEA-172/closure_shelling_spec.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-172/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-172/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-172/cost_analysis.md`

All paths are prospective; no artifact, contract, experiment, or run exists or is authorized.

## Interpretation boundary

This is scoped rejected, novelty-unverified evidence. Finite checks would be toy and scaling claims remain heuristic and model-bound. Accessibility or a valid decomposition is not an ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-172/antimatroid_axiom_no_go.md` defining partial-source feasibility and exhibiting the first union-closure, accessibility, or endpoint-only closure-oracle obstruction.
