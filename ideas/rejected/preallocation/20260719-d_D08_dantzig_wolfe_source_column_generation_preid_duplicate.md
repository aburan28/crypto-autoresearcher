# Pre-ID duplicate draft — Dantzig–Wolfe source-column generation

## Status and claim labels

- Prospect: `20260719-d-D08`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `column_generation_decomposition` / `conservative` / pre-ID screen
- State: `merged_rejected_source_pricing_oracle_and_explicit_columns`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Decompose signed elliptic completion into four/five deck blocks linked only by public endpoint conservation. A Dantzig–Wolfe restricted master would request negative-reduced-cost source columns from endpoint-only pricing oracles until it certifies exact target support and returns a tuple, enabling factor logs and blind descent below rho and BSGS.

## Mechanism-new operation

Dantzig–Wolfe replaces block feasible regions by convex combinations of their extreme points and generates columns by pricing. It counts only if block extreme points and the pricing oracle are endpoint-derived and exact integer source replay follows; enumerating tuple columns or using a completion oracle is a control.

## Assumptions

1. Signed elliptic compatibility has a compact block-angular exact formulation with no source-sized linking matrix.
2. Column generation, pricing, master solves, integrality, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. The LP master has no fractional/source-recombination gap at zero feasibility.
4. One frozen block formulation serves known-log and fresh scalar-blind targets.
5. No explicit large-prime/source columns, post-hoc selector, dense resultant, or uncharged pricing oracle is admitted.

## Semantic fingerprint

`endpoint_block_angular_formulation | Dantzig_Wolfe_priced_extreme_columns | exact_integer_restricted_support | selected_columns_to_signed_sources | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact subset-stable support is the residual.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: the public source-resolving circuit is missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: a source generator cannot be hidden in pricing.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: generated extreme columns are explicit source records.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1477`: represented source state misses the online boundary.

## Closest primary literature

- Dantzig and Wolfe, [Decomposition principle for linear programs](https://doi.org/10.1287/opre.8.1.101), alternates a coordinating master with pricing over supplied block polyhedra.
- Gilmore and Gomory, [A linear programming approach to the cutting-stock problem](https://doi.org/10.1287/opre.9.6.849), makes the column-generation/source-pattern boundary explicit.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) set the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, block formulation, pricing rule, restrictions, and verifier.
2. Build target-independent block/master state within `B^(9/4+o(1))` without explicit source columns.
3. On known-log targets, price enough columns to decide exact restricted support and replay five verified occurrences.
4. Collect at least `B` independent rows, preserve failed pricing/dependencies, and solve factor-base logarithms.
5. Reuse unchanged formulation for fresh scalar-blind `Q+[t]P`, recover/verify columns, remove `t`, and verify `[x]P=Q`.
6. Charge block construction, every pricing/master solve, columns, negative iterations, replay, rank, logs, descent, verification, bit work, and memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge block-polytope/linking-row construction, initial columns, pricing data, and restricted-master state; let `q,q_m` charge every target/restriction pricing call, master solve, branch-and-price/integrality work, generated column, negative iteration, bisection, and replay. Let `delta,delta_t` be reciprocal verified relation/target success, `o` output, `r` verified independent-rank credit, `u` fractional/source ambiguity plus column-generation and rebuild overhead, and `ell,ell_m` factor-log time/state.

With `B=N^beta`, `beta=1/5`, require `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`, `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, fresh formulation/pricing/master/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Pollard rho and BSGS remain exponent-`0.50` controls; source pricing, every explicit column, integer exactification, and target-dependent reoptimization are charged.

## Likely fatal obstruction

Pricing an extreme column is the missing source-generation problem, and the reduced-cost objective does not certify rare exact target support. Even if every block polytope is integral, the linking restricted master need not be integral. Explicit columns are source tuples; fractional convex combinations can recombine incompatible occurrences, while an exact integrality theorem is absent and charged branch-and-price restores combinatorial search. This merges with IDEAs `120/199/343/365/368` and pre-ID `A09/C04`.

## Proof track

Construct endpoint-only pricing, prove integrality of the linking restricted master and whole formulation—not only the block polyhedra—with a sub-gate column count for all restrictions, then close occurrence replay and complete descent.

## Disproof track

Expose one source-generating pricing call, a fractional/source mismatch, source-sized column set, or complete exponent outside the gates.

## Positive and negative controls

- Positive: a supplied block-angular integral program with planted columns and exact master recovery.
- Negative: fractional recombination without a valid tuple, equal reduced-cost data with different source support, restrictions, exceptional charts, and blind targets.
- Baselines: IDEAs `120/199/343/365/368`, pre-ID `A09/C04`, explicit tuple columns, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only pricing, exact integrality/replay on all restrictions, bounded columns/iterations, `1,000` independent rows, `100` blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-bearing priced column, one fractional mismatch, target rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d08_pricing_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d08_fractional_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d08_cost_analysis.md`

## Interpretation boundary

This rejects the elliptic column generator, not Dantzig–Wolfe decomposition. A valid reduced-cost column or solved planted LP is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d08_pricing_provenance.md` and expand the pricing oracle into the exact endpoint/source operations it must perform.
