# ECDLP-IDEA-222 — Białynicki–Birula cell source atomizer

## Status and claim labels

- Class: `algebraic-representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_equivariant_fixed_cell_duplicate_of_idea_094`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a torus fixed point, attracting cell, or localization identity is not an ECDLP break.

## Falsifiable hypothesis

A smooth projective compactification of the endpoint relation fiber admits a public torus action whose Białynicki–Birula attracting cells are indexed biconditionally by exact signed factor-base sources. Flowing an endpoint to fixed loci and reversing its cell coordinates would yield relations and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **torus-flow cell decomposition followed by fixed-cell-to-source inversion**. It is an operation-level duplicate of IDEA-094 equivariant fixed-point atomization: both require an endpoint-compatible action, fixed loci that separate source tuples, and a canonical point inverse. A source-separating linearization or fixed-point label installs the missing source atlas.

## Assumptions

1. Public `E/F_p`, prime-order subgroup, factor base `F` of size `B=N^beta`, compactification, and torus action are target-independent.
2. The action preserves the endpoint relation scheme and has bounded fixed data without a source/component enumeration.
3. Every attracting cell has a canonical all-strata inverse to exact signed factor points.
4. Compactification, action, localization, cell output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`compactified_endpoint_relation_fiber | public_torus_action | Bialynicki_Birula_attracting_cells | fixed_cell_exact_source_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact-source predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed source-generator boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-label floor.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-044`, the ordinary divisor-smoothness transfer boundary.

## Closest primary literature

- Białynicki–Birula, [Some theorems on actions of algebraic groups](https://doi.org/10.2307/1970915), establishes attracting-cell decompositions for suitable algebraic group actions.
- Białynicki–Birula, [Some properties of the decompositions of algebraic varieties determined by actions of a torus](https://eudml.org/doc/142008), develops the geometry of the resulting cells.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives the elliptic relation scheme but no source-separating torus action.

No checked source supplies the required elliptic action or source inverse. Novelty remains unverified, and the operation duplicates IDEA-094.

## Complete factor-base-to-target-descent path

1. Freeze the compactification, torus action, one-parameter subgroup, cell charts, masks, inverse, and verifier.
2. Construct the endpoint fiber and fixed/cell data without listing relation components or source tuples.
3. Reverse every accepted cell to exact signed factor points and independently verify each relation.
4. Collect full rank, solve and verify all factor-base logarithms.
5. Apply the same action to fresh `Q+[t]P`, invert target cells, substitute logs, and subtract `t`.
6. Preserve stabilizer/chart ambiguity and accept only `[x]P=Q`, charging output and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, cell query plus exact inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`, the complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Fixed loci, charts, linearizations, and source outputs are charged. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

A generic endpoint relation fiber has no canonical nontrivial torus action compatible with an arbitrary factor base. If fixed loci separate exact point tuples, their labels or weights encode those tuples. If the action is symmetric enough to be public, it retains only aggregate orbit/component data. Constructing the compactified source fiber before localization is itself the missing elimination/source task.

## Proof track

Exhibit a target-independent action and prove bounded fixed-cell data plus a canonical exact point inverse with complete `lambda,mu<=0.45`.

## Disproof track

Prove every admitted action is trivial/aggregate on the generic fiber, demonstrate fixed-cell source collisions, or show the compactification/action data materialize the source components.

## Positive and negative controls

- Positive control: a supplied smooth projective torus variety with planted fixed-point labels and known attracting cells.
- Negative controls: label-erased fixed loci, generic source-fiber compactifications, IDEA-094, IDEA-169 Hilbert flags, source-labelled linearizations, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires an operation distinct from IDEA-094, 100% cell-to-source recall, zero false cells, no source-labelled action, and `lambda,mu<=0.45`. Semantic identity with IDEA-094, a fixed-cell collision, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-222/bb_cell_source_theorem.md`
- Prospective collision set: `ideas/artifacts/ECDLP-IDEA-222/fixed_cell_collisions.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-222/independent_cell_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-222/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected representation analysis. Finite checks would be toy and projections heuristic and model-bound. A fixed point, cell decomposition, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-222/bb_cell_source_theorem.md` showing an endpoint action genuinely distinct from IDEA-094 or preserving the exact semantic-duplicate/fixed-cell collision proof.
