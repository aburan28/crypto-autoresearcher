# ECDLP-IDEA-375 — PQ-tree consecutive-ones source ordering

## Status and claim labels

- Class: `combinatorial`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_consecutive_ones_matrix_is_source_incidence_and_endpoint_fibres_need_not_be_interval`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid PQ-tree ordering or toy relation is not an ECDLP break.

## Falsifiable hypothesis

Elliptic source occurrences admit a public order in which every target/restriction incidence row has the consecutive-ones property, so a compact PQ-tree can retain all feasible source orders and support exact fresh-target source bisection below the P1553 gates.

## Mechanism-new operation

The screened operation is **insert endpoint-derived interval constraints into a PQ-tree, maintain the permissible source orders, and unrank one order/leaf compatible with a fresh target and arbitrary dyadic restrictions**. It is distinct from generic treewidth or grammar compression only if the binary constraint rows are constructed without enumerating source incidences.

## Assumptions

1. A target-independent ordering of signed deck occurrences makes every exact relation constraint consecutive.
2. Constraint rows are endpoint-derived and compact; no row lists the source tuples it accepts.
3. PQ reductions preserve exact singleton witnesses, occurrence labels, all signed strata, and arbitrary dyadic restrictions.
4. Unranking one compatible order yields an exact factor tuple rather than an aggregate permutation class.
5. Constraint construction, reductions, restrictions, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_constraint_rows | consecutive_ones_property | PQ_tree_permissible_orders | exact_leaf_unranking | occurrence_source | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; source construction and the complete descent path remain charged.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; compact source-resolving structure is the missing object.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform generation from endpoint data remains unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless transitions cannot be supplied as free rows.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit source-edge materialization is a no-promotion boundary.

## Closest primary literature

- Booth and Lueker, [Testing for the consecutive ones property, interval graphs, and graph planarity using PQ-tree algorithms](https://doi.org/10.1016/S0022-0000(76)80045-1), compresses permissible orders for a supplied binary matrix.
- Hsu, [A simple test for the consecutive ones property](https://doi.org/10.1006/jagm.2001.1205), gives a decomposition-based test for supplied rows.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not provide interval incidence rows or a universal point order.

No checked source proves consecutive-ones structure for elliptic source fibres; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, five disjoint signed decks of size `B`, public occurrence order, row constructor, PQ templates, restrictions, masks, and verifier.
2. Construct a target-independent PQ-tree state within `B^(9/4)` without listing accepted source tuples or pair-pair edges.
3. For each known-log target, add exact endpoint constraints, reject empty restrictions, bisect positive children, unrank one occurrence-labelled tuple, and verify the group sum.
4. Collect at least `B` independent verified rows, charge repeated/dependent rows, solve factor logs, and verify them independently.
5. Reuse the unchanged order, row constructor, and PQ reductions for fresh scalar-blind `Q+[t]P`, charging mask resampling and every negative restriction.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge row construction, all PQ reductions/rebuilds, exact source output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; setup/state is at most `B^(9/4+o(1))`, a complete fresh restricted query is at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

PQ-trees compress the solutions of an already supplied consecutive-ones matrix. In this application each row is the source-incidence predicate, so constructing it is Query2P1 or an explicit source table. Generic elliptic translations scramble coordinate orders and need not produce interval fibres; retaining arbitrary scattered supports makes the PQ representation source-sized. This merges with IDEAs 120, 135, 297, 338, and 343 unless a new endpoint-only interval theorem is proved.

## Proof track

Prove a target-uniform public order and endpoint-only row constructor with exact consecutive-ones semantics, restriction stability, source unranking, and complete exponents at most `0.45`.

## Disproof track

Produce one valid deck/target family whose accepted occurrences alternate in every public order, or show that forming a constraint row enumerates the hidden source fibre.

## Positive and negative controls

- Positive: supplied interval matrices with planted occurrence labels must reduce and unrank exactly.
- Negative: Tucker forbidden submatrices, alternating singleton supports, equal PQ summaries with different source labels, all strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 120/135/297/338/343, explicit incidence matrices, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with the public-order theorem, source-free row construction, exact bisection/unranking, `1,000` independent rows, `100` blind descents, frozen setup/query gates, and `lambda,mu<=0.45`.
- Falsify on one forbidden submatrix, one row requiring source enumeration, one missed singleton/stratum, source-sized rebuild, or either exponent at least `0.50`.
- A correct PQ-tree implementation on a supplied toy matrix is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-375/consecutive_ones_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-375/tucker_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-375/source_unranking_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-375/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic PQ-tree route, not PQ-tree algorithms. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; an interval ordering is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-375/consecutive_ones_obligations.md` and derive the smallest exact endpoint-incidence matrix whose Tucker obstruction can be checked without source advice.
