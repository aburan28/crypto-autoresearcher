# ECDLP-IDEA-343 — Avis–Fukuda reverse-search source enumerator

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_reverse_search_requires_source_vertex_oracle_and_enumerates_density`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; output-sensitive enumeration of a supplied fibre is not an ECDLP break.

## Falsifiable hypothesis

The exact signed endpoint relation fibre has a public uniform endpoint-parameterized parent map and bounded child oracle, allowing reverse search from a source-free root with delay below `B^(5/4)` and reusable exact enumeration for factor-log collection and blind descent.

## Mechanism-new operation

The screened operation is **orient the implicit relation-fibre graph by a canonical parent map and enumerate exact source tuples by reverse search without a visited table**. The required distinction is a source-free root and child oracle. If a represented tuple or full adjacency list is supplied, the operation merges with IDEAs 070, 120, 125, 157, 172, 266, and 297: enumeration begins after the missing locator.

## Assumptions

1. A canonical root is computed from the endpoint without first finding a factor tuple.
2. Parent and child queries use only public curve/deck data and have bounded branching.
3. Every signed, repeated, singular, infinity, and ambiguous source lies in the oriented fibre graph.
4. Delay, total output, failed targets, rank, logs, blind descent, and memory fit the frozen gates.
5. One uniform endpoint-parameterized parent rule applies to fresh masked targets without successful-target advice.

## Semantic fingerprint

`implicit_relation_fibre_graph | source_free_canonical_root | Avis_Fukuda_parent_orientation | output_sensitive_exact_source_enumeration | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1431-CANONICAL-ROOT-PRODUCT-NO-PROMOTION`, where canonical traversal still constructs every source leaf.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the exact source-edge cost floor.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where source-distinct ancestry prevents lossless compression.
5. `inputs/ledger_inventory.json` — imported `P1477`, where complete serial source states densify.

## Closest primary literature

- Avis and Fukuda, [Reverse Search for Enumeration](https://doi.org/10.1016/0166-218X(95)00026-N), enumerates vertices when a represented start vertex and local adjacency/parent operations are available; it does not find the first elliptic source.
- Alon, Yuster, and Zwick, [Color-Coding](https://doi.org/10.1145/210332.210337), is a nearby witness-enumeration control that also assumes the underlying graph.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies an endpoint equation rather than a root or adjacency oracle.

No checked source supplies the claimed fibre orientation and root; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, fibre vertices, local moves, parent/root rules, masks, and verifier.
2. Construct the root and child oracle for known-log endpoints without a source table.
3. Enumerate and independently verify every emitted signed relation, retaining misses and duplicates.
4. Collect at least `B` independent rows, solve all needed factor logs, and verify them.
5. Run the identical traversal on fresh scalar-blind masked targets.
6. Substitute logs, remove masks, retain ambiguity, and accept only after `[x]P=Q`.
7. Charge root finding, children, delay, total output, rank, logs, descent, verification, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, traversal query excluding emission `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Root construction, every child query, output, and verification are charged; `0<=r<=o`. Promotion requires complete exponents at most `0.45` and fresh-target work at most `0.25`. Pollard rho has expected time exponent `0.50` with negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Reverse search removes the visited set, not the need for one represented vertex and source-complete local neighbors. Finding the first relation is the original rare-event problem, while source-faithful child moves expose the same edge deck. Full enumeration also pays the fibre output size and does not improve a fresh target with no root.

## Proof track

Exhibit a source-free root identity and bounded parent/child theorem covering all strata, then prove delay, output, campaign, blind descent, and complete `lambda,mu<=0.45`.

## Disproof track

Show root construction finds a source, child generation scans source edges, one component/stratum is unreachable, or total delay/output gives exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied connected fibres with known roots and adjacency must enumerate every labelled vertex once.
- Negative: disconnected, source-permuted, and root-withheld fibres must not produce preferred elliptic tuples.
- Baselines: IDEAs 070/120/157/172/266/297, explicit enumeration, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a source-free root, complete children, zero source errors, 1,000 ranked rows, 100 blind descents, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify if the root is a supplied factor tuple, setup/child state exceeds `B^(9/4)`, delay exceeds `B^(5/4)`, a component is missed, or either exponent reaches `0.50`.
- Output-sensitive enumeration after a supplied source is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-343/root_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-343/parent_child_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-343/fibre_component_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-343/cost_analysis.md`

## Interpretation boundary

This rejects the proposed source-free relation-fibre reverse search, not reverse search generally. Every finite test would be toy, heuristic, model-bound, and novelty-unverified. Enumeration correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-343/root_input_receipt.md` deriving the proposed canonical root and marking any step that already finds an exact factor tuple.
