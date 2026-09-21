# ECDLP-IDEA-235 — Tutte-activity source unranking

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_matroid_ground_set_and_bases_are_source_deck`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Tutte polynomial, activity word, or spanning-tree expansion is not an ECDLP break.

## Falsifiable hypothesis

Each endpoint relation fiber has an implicit ordered matroid whose bases are its exact signed
factor-base source tuples.  Internal/external activity would partition those bases into canonically
unrankable intervals, allowing output-sensitive source recovery, relation collection, and masked
descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **compile an endpoint matroid, use Tutte activities to partition its source
bases, and canonically unrank every exact point tuple from its activity data**.  Computing a Tutte
polynomial, changing edge order, using a supplied graph or matroid, enumerating bases, or applying a
generic matroid solver is a duplicate/control.

## Assumptions

1. The ground set, independence oracle, public order, endpoint specialization, signs, masks, and source decoder are scalar-blind and target-independent.
2. The oracle and activity partition have sub-rho setup, query, output, and memory and do not list all source bases or circuits.
3. Every activity cell has a canonical inverse to all exact signed elliptic point sources, including repeated and boundary cases.
4. Oracle construction, activity traversal, output, relation density, rank, factor logs, blind descent, verification, and memory are fully charged.

## Semantic fingerprint

`endpoint_relation_matroid | implicit_independence_oracle | internal_external_activity_partition | canonical_basis_to_point_source_unranking | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the source-fiber generation gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the failed coordinate source-resolution lane.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the failed arithmetic source-generator lane.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry-edge floor.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge boundary.

## Closest primary literature

- Tutte, [A contribution to the theory of chromatic polynomials](https://doi.org/10.4153/CJM-1954-010-9), develops spanning-tree activity ideas for a supplied graph.
- Gordon and Traldi, [Generalized activities and the Tutte polynomial](https://doi.org/10.1016/0012-365X(90)90019-E), extends activity expansions for supplied matroids and subsets.

Neither source constructs an endpoint elliptic matroid oracle or turns activity classes into hidden
point-labelled sources.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, matroid compiler, ground order, activity convention, unranking rule, and verifier.
2. Construct the endpoint independence/rank oracle without enumerating source bases or source-labelled circuits.
3. Traverse activity intervals, unrank every exact signed point tuple, and independently verify every elliptic sum.
4. Collect independent rows and solve and independently verify all factor logs.
5. Apply the identical matroid/activity/unranking operation to fresh `Q+[t]P`, retain ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging oracle traffic, basis output, rank, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let matroid setup time/memory be `N^a,N^a_m`, reciprocal relation and target densities
`N^delta,N^delta_t`, one activity query plus exact source inverse `N^q,N^q_m`,
independent-rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log completion
`N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Ground-set state, rank queries, circuits, activity traversal, bases, source output, relation rank,
factor logs, masked descent, and verification enter the exponents.  Promotion requires
`lambda,mu<=0.45`.

## Likely fatal obstruction

A matroid requires a ground set and an independence oracle.  If bases are exact elliptic source
tuples, the oracle or its circuits encode the missing source incidence.  Tutte activity partitions a
supplied base set and its polynomial aggregates counts; neither creates the bases nor canonically
maps an activity word to finite-field points.  Unranking all bases therefore reconstructs or traverses
the source deck, and the factor-base addition relation does not generically satisfy matroid exchange.

## Proof track

Exhibit a valid implicit endpoint matroid with sub-rho oracle, prove base/source bijection and
canonical activity unranking on all strata, and establish complete `lambda,mu<=0.45`.

## Disproof track

Find a matroid exchange violation in the source family, show any faithful oracle answers explicit
source incidence, or prove basis enumeration, output, ambiguity, or complete exponent at least
`0.50`.

## Positive and negative controls

- Positive control: supplied graphic and representable matroids with independently enumerated bases and activity intervals.
- Negative controls: source-label permutations, random set systems violating exchange, IDEA-064/082/137/203/206/212/223, P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires verified matroid axioms, an oracle and activity representation of exponent at most
`0.45`, exact all-source recall, no explicit base deck, full factor-log rank, 100 blind descents per
large future toy size, and complete `lambda,mu<=0.45`.  One exchange violation, missed source,
explicit basis traffic, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-235/endpoint_matroid_activity_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-235/activity_unranking_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-235/independent_tutte_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-235/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative algorithm hypothesis.  A valid Tutte polynomial,
activity expansion, matroid oracle, spanning-tree count, toy unranking, relation, or toy scalar is not
crypto-scale ECDLP evidence or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-235/endpoint_matroid_activity_theorem.md` proving a source-blind endpoint matroid with canonical point-source activity unranking or an exchange/oracle-payload obstruction.
