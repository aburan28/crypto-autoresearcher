# ECDLP-IDEA-368 — Pippenger–Spencer nibble source packing

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_nibble_consumes_explicit_relation_hyperedges`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a near-perfect matching in a supplied hypergraph is not an ECDLP break.

## Falsifiable hypothesis

The five-part elliptic relation hypergraph has endpoint-computable degrees/codegrees and a semi-random nibble that emits enough disjoint exact relation edges for full factor rank and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **sample a sparse round of hyperedges, retain a conflict-free subfamily, delete incident vertices, and iterate the Pippenger–Spencer nibble to build an almost-perfect packing**. It is useful only if edge sampling does not require the relation list, degrees/codegrees are computable without source enumeration, and the selected edges are exact labelled relations whose rows achieve rank and target descent.

## Assumptions

1. An endpoint-only oracle samples relation edges with the distribution required by the nibble.
2. Degrees are near regular and maximum codegrees are negligible uniformly over target and source strata.
3. Edge conflicts and deletions are maintained inside setup/state without a source-labelled hypergraph.
4. The packing yields at least `B` independent verified rows and an identical fresh-target edge sampler.
5. Oracle construction, sampling failures, deletions, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`five_part_elliptic_relation_hypergraph | endpoint_edge_sampling_oracle | Pippenger_Spencer_semirandom_nibble | near_matching_relation_rows | rank_and_blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; an edge sampler is the missing source-resolving generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source generation remains above the gate.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit hyperedges are precisely the forbidden source surface.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; regenerating edges from pair advice pays cubic work.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; packing a supplied exact stream is only a post-generation control.

## Closest primary literature

- Pippenger and Spencer, [Asymptotic behavior of the chromatic index for hypergraphs](https://doi.org/10.1016/0097-3165(89)90074-5), obtains near-perfect packings under degree/codegree conditions on a supplied hypergraph.
- Rödl, [On a packing and covering problem](https://doi.org/10.1016/0012-365X(85)90020-8), develops the semi-random packing method for represented uniform set systems.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives an edge predicate rather than a subgate edge sampler.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, edge sampler, nibble rounds, conflict rules, restrictions, masks, and verifier.
2. Construct degree/codegree estimates and edge samples from endpoints without enumerating the hypergraph.
3. On known-log targets, run the nibble, replay every retained edge, and record exact relation rows.
4. Obtain at least `B` independent rows, solve factor logs, and independently verify them.
5. Apply the identical sampler to fresh scalar-blind `Q+[t]P` targets.
6. Recover a target edge, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge sampling, conflicts, deletions, failed rounds, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

The nibble selects among edges that are already sampleable. For elliptic relations, exact edge sampling is the missing source-fibre operation and degree/codegree evaluation can cost the full fibre. A matching controls vertex overlap, not linear independence of relation rows, and it supplies no fresh-target locator. This is post-generation selection merging with IDEAs 064, 137, 147, 200, 257, 345, and 361.

## Proof track

Construct a source-free edge sampler, prove degree/codegree hypotheses and ranked blind descent, and derive complete exponents at most `0.45`.

## Disproof track

Show the sampler enumerates edges, degree/codegree computation is source-sized, or construct near-perfect packings with deficient relation rank or no target descent.

## Positive and negative controls

- Positive: supplied nearly regular low-codegree hypergraphs with planted matchings.
- Negative: source-permuted edge oracles, irregular elliptic fibres, duplicate rows, matching-with-low-rank controls, and blind targets.
- Baselines: IDEAs 064/137/147/200/257/345/361, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only edge sampling, proved nibble hypotheses, 1,000 independent rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on an explicit edge oracle, source-sized degree computation, deficient rank, missed stratum, `B^3` generation, or either exponent at least `0.50`.
- A near matching in a supplied toy hypergraph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-368/edge_sampler_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-368/degree_codegree_rank_cases.json`
- `ideas/artifacts/ECDLP-IDEA-368/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-368/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic nibble, not semi-random packing theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. A matching is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-368/edge_sampler_obligations.md` and prove whether a relation edge can be sampled below the gates without explicit hyperedges.
