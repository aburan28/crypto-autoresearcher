# ECDLP-IDEA-345 — Linear matroid-parity source packing

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_failed_augmentation_circuit_is_hidden_relation_oracle`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an optimum in a supplied linear matroid is not an ECDLP break.

## Falsifiable hypothesis

Each coloured factor pair admits a compact public linear-matroid block and a hypothetical reduction from six-source Abel–Jacobi cancellation to a failed augmentation and its labelled fundamental circuit, from which relation sources are replayed for collection and blind target descent inside the frozen bounds.

## Mechanism-new operation

Standard linear matroid parity maximizes a collection of prescribed pairs whose union is independent; it does not select dependent triples as relation certificates. The screened operation is therefore **encode each source pair as a prescribed block, reduce elliptic cancellation to an explicitly defined failed augmentation, and replay a labelled fundamental circuit from that failure**. Without a proved biconditional failed-augmentation oracle, the oracle is the hidden relation predicate, the columns are the missing pair deck, and the operation merges directly with IDEA-257, then IDEAs 137, 157, 212, 215, and 223.

## Assumptions

1. Up to `B^2` pair blocks may be a charged one-time setup only if they fit `B^(9/4)`; no target-specific rebuild, hidden scalar label, or `B^3` campaign/query expansion is omitted.
2. A failed augmentation and its labelled fundamental circuit are biconditional with endpoint cancellation, not merely necessary or sufficient.
3. Augmentation returns every signed source block, including repeated and overlap strata.
4. Representation rank, oracle access, output, relation rank, factor logs, blind descent, and memory are charged.
5. The same matroid representation supports fresh masked targets without rebuilding from successful sources.

## Semantic fingerprint

`coloured_factor_pair_blocks | implicit_linear_matroid_representation | parity_augmentation_relation_biconditional | labelled_block_source_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the full five-source exact-membership and cost gate.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, where materialized source states exceed the gate.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry floor.
5. `inputs/ledger_inventory.json` — imported `P1480`, the supplied bit-vector solver control.

## Closest primary literature

- Lovász, [Matroid matching and some applications](https://doi.org/10.1016/0095-8956(80)90066-0), solves parity for supplied linear-matroid representations; it does not construct columns whose dependence encodes elliptic cancellation.
- Alon, Yuster, and Zwick, [Color-Coding](https://doi.org/10.1145/210332.210337), is a colourful-selection control that also presumes represented candidates.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies a polynomial relation predicate rather than a linear matroid representation.

No checked source supplies the claimed biconditional columns and inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, coloured decks, pair blocks, matroid field, failed-augmentation oracle, masks, and verifier.
2. Construct at most a target-independent `B^2` pair representation inside the `B^(9/4)` setup gate; do not rebuild it from successful targets.
3. Run parity augmentation on known-log endpoints, extract each failed augmentation's labelled fundamental circuit inside `B^(5/4)`, replay blocks to factor points, and verify relations.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Apply the same representation and augmentation to fresh scalar-blind masked targets and extract every labelled fundamental circuit inside `B^(5/4)`.
6. Substitute logs, remove masks, retain all alternatives, and verify `[x]P=Q`.
7. Charge block construction, oracle queries, augmentation, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, parity query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every represented column, independence query, augmentation step, and source emission is charged; `0<=r<=o`. Promotion requires complete exponents at most `0.45`. Pollard rho has expected time exponent `0.50` with negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Matroid parity selects prescribed pairs whose union is independent in a supplied linear representation. Three-pair elliptic cancellation is not such an optimum in the natural Plücker/wedge representation. Although a one-time `B^2` pair surface can fit the setup cap, constructing the failed-augmentation predicate and labelled fundamental circuit can restore `B^3` campaign work or exceed the `B^(5/4)` fresh-query gate; embedding that predicate in the columns simply supplies the missing source oracle. Augmentation then changes only the backend.

## Proof track

Exhibit an implicit low-rank representation, prove relation biconditionality and all-strata replay, and derive setup/query/output plus complete `lambda,mu<=0.45`.

## Disproof track

Find a failed augmentation whose fundamental circuit is a nonrelation or a relation with no such failure, show target-specific column construction exceeds `B^(5/4)`, lose a signed/repeated stratum, or charge representation/oracle work to exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied linear-matroid parity fixtures with planted labelled block solutions must recover them.
- Negative: rank-matched random columns and natural wedge columns on nonrelations must not be decoded as sources.
- Baselines: IDEAs 137/157/212/215/223/257, explicit pair tables, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with zero biconditional errors, at most a target-independent `B^2` pair setup, no target-specific rebuild, 1,000 ranked rows, 100 blind descents, setup/state at most `B^(9/4)`, failed-augmentation circuit extraction and query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on one predicate mismatch, one missing stratum, charged setup above `B^(9/4)`, target work above `B^(5/4)`, a `B^3` campaign, or either exponent at least `0.50`.
- Fast parity on supplied columns is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-345/block_representation_spec.md`
- `ideas/artifacts/ECDLP-IDEA-345/relation_biconditional_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-345/oracle_materialization_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-345/cost_analysis.md`

## Interpretation boundary

This rejects the unsupplied elliptic matroid representation, not linear matroid parity. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. A feasible packing or valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-345/block_representation_spec.md` giving explicit public columns and checking both directions of the relation biconditional before any solver work.
