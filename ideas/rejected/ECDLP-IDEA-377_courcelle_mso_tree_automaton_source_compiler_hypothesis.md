# ECDLP-IDEA-377 — Courcelle MSO tree-automaton source compiler

## Status and claim labels

- Class: `logical`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_bounded_treewidth_structure_and_decomposition_encode_source_incidence`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; successful MSO model checking or toy witness extraction is not an ECDLP break.

## Falsifiable hypothesis

Exact five-deck relation existence and one source witness are MSO-definable on an endpoint-constructible bounded-treewidth structure whose decomposition and compiled tree automaton satisfy the P1553 preprocessing and fresh-target gates.

## Mechanism-new operation

The screened operation is **encode endpoint/source constraints as a bounded-treewidth relational structure, compile the exact relation formula into a finite tree automaton, and self-reduce accepting runs to one occurrence-labelled tuple**. It survives only if the structure and decomposition are built without materializing source incidence.

## Assumptions

1. A target-independent endpoint structure of uniformly bounded or subgate treewidth represents all source tuples biconditionally.
2. Its tree decomposition is compactly constructible from public endpoints rather than supplied as source advice.
3. The MSO formula handles finite-field arithmetic, all signed P1553 strata, occurrence labels, and arbitrary dyadic restrictions exactly.
4. Automaton compilation constants, accepting-run self-reduction, target updates, and source output fit the online gate.
5. Relation density, independent rank, factor logs, blind descent, verification, bit time, and peak memory are charged.

## Semantic fingerprint

`endpoint_relational_structure | bounded_treewidth_decomposition | Courcelle_MSO_tree_automaton | accepting_run_self_reduction | exact_source | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the complete descent path and source costs remain mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact source-resolving circuit is missing.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source generation is unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; a lossless decomposition cannot hide source edges.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; materialized Cartesian products remain a no-promotion control.

## Closest primary literature

- Courcelle, [The monadic second-order logic of graphs I](https://doi.org/10.1016/0890-5401(90)90043-H), establishes linear-time recognizability for fixed MSO properties on supplied bounded-treewidth graphs.
- Courcelle, [Special tree-width and the verification of monadic second-order graph properties](https://doi.org/10.4230/LIPIcs.FSTTCS.2010.13), makes the supplied-decomposition and parameter dependence explicit.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies equations but no bounded-treewidth source structure.

No checked source constructs the required compact relational structure; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, relational signature, MSO formula, structure/decomposition constructor, automaton compiler, restrictions, masks, and verifier.
2. Build target-independent structure, decomposition, and compiled automaton inside `B^(9/4)` without explicit source-product bags.
3. For known-log targets, update target predicates, decide exact restricted existence, self-reduce an accepting run through `O(log B)` deck restrictions, recover one tuple, and verify it.
4. Collect `B` independently verified rows, charge duplicate/dependent outputs, solve factor logs, and verify them independently.
5. Reuse the unchanged structure/formula/compiler for fresh scalar-blind `Q+[t]P`, charging every update, negative restriction, and mask rebuild.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge structure and decomposition construction, compiler size, automaton runs, self-reduction, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; setup/state is at most `B^(9/4+o(1))`, one complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Courcelle's theorem begins with a supplied bounded-treewidth structure and a decomposition. A source-biconditional elliptic structure contains tuple-incidence edges or large product bags; quotienting them away loses occurrence labels and exact witnesses. General finite-field relation structures need not have bounded treewidth, while compiling or rebuilding exact arithmetic/restrictions can be nonuniform and source-sized. This merges with IDEAs 120, 135, 325, 338, and 372 unless a new endpoint-only structural-width theorem is proved.

## Proof track

Prove bounded treewidth and construct the source-biconditional structure/decomposition from endpoints, then bound compiled automaton, exact self-reduction, and complete descent by the frozen gates.

## Disproof track

Exhibit relation instances with unbounded minors/treewidth, or show that any bounded-width quotient identifies distinct source fibres or requires explicit product bags.

## Positive and negative controls

- Positive: supplied bounded-treewidth structures with planted MSO witnesses must decide and self-reduce exactly.
- Negative: grid-minor source incidence, equal quotients with different singleton witnesses, arbitrary restrictions, all strata, compiler blowups, and blind targets.
- Baselines: IDEAs 120/135/325/338/372, explicit factor graphs, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with the endpoint structural-width theorem, source-free decomposition, exact accepting-run lift, `1,000` independent rows, `100` blind descents, frozen setup/query gates, and `lambda,mu<=0.45`.
- Falsify on unbounded treewidth, one source-product bag, one quotient witness collision, one missed stratum, or either exponent at least `0.50`.
- Correct MSO checking on a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-377/treewidth_structure_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-377/minor_and_quotient_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-377/accepting_run_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-377/cost_analysis.md`

## Interpretation boundary

This rejects the screened endpoint-structure route, not Courcelle's theorem. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; model checking is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-377/treewidth_structure_obligations.md` and lower-bound the width of the smallest source-biconditional relation structure.
