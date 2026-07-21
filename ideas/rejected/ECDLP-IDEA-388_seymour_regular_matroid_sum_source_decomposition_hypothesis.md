# ECDLP-IDEA-388 — Seymour regular-matroid sum source decomposition

## Status and claim labels

- Class: `representation-changing`
- Risk band: `conservative`
- Top lane: `representation-changing`
- State: `merged_rejected_regularity_is_unproved_and_constructing_the_matroid_representation_recreates_source_incidence`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run theorem-preflight only; `review_required`, unapproved, and never dispatchable
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a regular toy matroid or correctly replayed circuit is not an ECDLP break.

## Falsifiable hypothesis

The exact signed five-deck relation system has an endpoint-constructible regular-matroid representation admitting Seymour 1-, 2-, and 3-sum decomposition into graphic, cographic, and bounded `R10` pieces, from which a target circuit and its five factor occurrences can be recovered below the campaign gates.

## Mechanism-new operation

The screened operation is **encode admissible factor occurrences as elements of an exact regular matroid, decompose that matroid by Seymour sums, solve compatible local circuit constraints in the basic pieces, and glue one global target circuit with labelled sources**. It is distinct from generic matroid or solver substitutions only if regularity and the representation are derived from endpoint algebra without listing candidate relations.

## Assumptions

1. There is a public matrix/oracle representation whose circuits are in bicondition with exact signed five-factor elliptic relations, including repeated occurrences and every stratum.
2. The represented matroid is regular uniformly over the frozen curve, decks, restrictions, and target shifts.
3. A Seymour decomposition can be constructed within `B^(9/4+o(1))` without querying one oracle entry per source incidence.
4. Local circuits glue without spurious cancellations and yield a canonical occurrence-labelled factor tuple for a fresh target.
5. Representation and decomposition construction, separators, dynamic state, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`elliptic_relation_circuit_matroid | regularity_certificate | Seymour_1_2_3_sum_decomposition | local_circuit_gluing | occurrence_source_lift`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`; complete five-source membership must satisfy the strict end-to-end query gate.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`; materialized source-distinct transition states exceed that gate.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; a lossless source decomposition cannot erase ancestry incidences.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact exact source-resolving representation remains hypothetical.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit source compatibility edges are the no-promotion boundary.

## Closest primary literature

- Seymour, [Decomposition of regular matroids](https://doi.org/10.1016/0095-8956(80)90075-1), proves that regular matroids decompose through 1-, 2-, and 3-sums into graphic, cographic, and `R10` components.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies algebraic relation membership but no regular-matroid representation or source-circuit oracle.

No checked primary source proves that an elliptic factor-deck relation system is regular or gives the required implicit representation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, `B=N^(1/5)` signed factor occurrences, circuit encoding, representation oracle, regularity certificate, sum conventions, restrictions, masks, and verifier.
2. Construct the target-independent matroid representation and Seymour decomposition within `B^(9/4+o(1))`, without enumerating the five-factor relation support or explicit compatibility edges.
3. For known-log targets, insert the target element, propagate exact circuit constraints through the sum tree, glue one accepted global circuit, map it to five occurrence-labelled factors, and verify the signed group sum.
4. Collect at least `B` independent verified relation rows, charging decomposition failures, circuit multiplicity, spurious/dependent rows, and output; solve factor logs and verify them.
5. Apply the unchanged representation and sum-tree algorithm to fresh scalar-blind `Q+[t]P`, with restrictions frozen prospectively and all target-specific updates charged.
6. Recover a factor circuit, substitute verified factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge representation queries, regularity proof, decomposition, separator dynamic programming, circuit gluing, source lift, output, rank, factor logs, descent, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Seymour's theorem starts with a supplied regular matroid. Elliptic summation membership is nonlinear, and the obvious linear matroid records coefficient dependencies rather than the group-law relation sought. Constructing a circuit oracle that distinguishes exactly the valid five-factor sources already solves or materializes the missing incidence problem. Even a regular representation would make circuit finding easy only relative to that representation, not construct the endpoint-conditioned source map. This merges with IDEAs 137, 212, 235, 257, and 345 unless regularity plus a compact public representation are proved.

## Proof track

Give an endpoint-only matrix/oracle, prove the circuit biconditional and regularity, construct its Seymour sum tree subgate, and prove exact source gluing and complete exponents at most `0.45`.

## Disproof track

Find a forbidden minor/nonregular restriction, a linear circuit that is not an elliptic relation, two source assignments with the same decomposition transcript, or a lower bound showing representation queries enumerate source incidences.

## Positive and negative controls

- Positive: supplied graphic, cographic, and regular `R10`-sum matroids with planted labelled circuits must decompose and replay exactly.
- Negative: nonregular binary matroids, label-permuted representations, linear dependencies that fail elliptic verification, target shifts, arbitrary restrictions, repeated factors, all signed strata, and blind targets.
- Baselines: IDEAs 137/212/235/257/345, explicit relation matrices, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only representation of size at most `B^(9/4+o(1))`, a verified regularity/circuit theorem, `1,000` independent rows, `100` blind descents, complete fresh queries at most `B^(5/4+o(1))`, and `lambda,mu<=0.45`.
- Falsify on one nonregular restriction, one circuit/relation mismatch, one hidden source-incidence query, one source-gluing collision, or either exponent at least `0.50`.
- A correct decomposition of a supplied toy matroid is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-388/regular_matroid_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-388/forbidden_minor_cases.json`
- `ideas/artifacts/ECDLP-IDEA-388/circuit_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-388/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic regular-matroid reduction, not Seymour's theorem. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; circuit validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-388/regular_matroid_obligations.md` and test whether the smallest exact source-circuit encoding satisfies the regular-matroid circuit axioms without relation enumeration.
