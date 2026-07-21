# ECDLP-IDEA-326 — Polynomial-partitioned Abel–Jacobi incidence router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_partitioning_requires_pair_hyperplanes_and_no_finite_field_exact_source_instantiation_is_supplied`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an incidence bound, correct partition, reported relation, or toy tuple is not an ECDLP break.

## Falsifiable hypothesis

The three `B^2` pair-wedge families in the P1553 six-list Abel–Jacobi formulation admit a target-independent low-degree polynomial partition whose cells support exact zero-wedge reporting in total campaign work and state `B^(9/4+o(1))` and fresh-target work `B^(5/4+o(1))`, including exact signed source replay.

## Mechanism-new operation

The screened operation is **partition one special pair-wedge family by a low-degree polynomial, route the hyperplanes induced by pairs from the other two families through crossed cells, and report exact incidences with source labels**. This is more specific than evaluating a determinant or supplying a point-hyperplane data structure. It nevertheless merges with IDEAs 052, 071, 255, and 257 and the P1552/P1553 wedge frontier: every query hyperplane is indexed by an already chosen pair of source pairs, so constructing or routing the `B^4` query family restores the missing separator. The cited partitioning theorems are real incidence bounds, not a finite-field source-unranking algorithm.

## Assumptions

1. A partition theorem with the required crossing bound holds for the special finite-field Pluecker families, including all singular and repeated strata.
2. The partition and cell conflict lists are constructible without enumerating `B^4` pair-pair hyperplanes or a source-labelled incidence table.
3. Each reported incidence replays the exact six signed coloured points with no post-hoc selector.
4. Partition construction, crossings, boundary recursion, output, rank, factor logs, blind descent, verification, bit work, and live bytes are charged.
5. The same partition handles fresh masked targets under P1553's disjoint-deck and colliding-target policy.

## Semantic fingerprint

`pair_wedge_Pluecker_families | low_degree_polynomial_partition | pair_pair_hyperplane_cell_routing | exact_incidence_source_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H670`, the batched projective point-hyperplane source-leaf proposal.
2. `inputs/ledger_inventory.json` — imported `ECFG-P1429-EXACT-FACTOR-ROOT-HYPERPLANE-CONTROL`, the exact supplied-root hyperplane control.
3. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator and transposed target join.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the pair/four-sum batch-generator hypothesis.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge noncompression boundary.

## Closest primary literature

- Guth and Katz, [On the Erdos distinct distances problem in the plane](https://doi.org/10.4007/annals.2015.181.1.2), introduces polynomial partitioning for a real incidence problem after the relevant points and lines are supplied.
- Guth, [Polynomial partitioning for a set of varieties](https://doi.org/10.1017/S0305004115000468), bounds how supplied varieties cross real partition cells; it does not construct an elliptic source family or finite-field witness decoder.
- Vinh, [The Szemeredi-Trotter type theorem and the sum-product estimate in finite fields](https://doi.org/10.1016/j.ejc.2011.06.008), supplies a finite-field incidence-count control for already specified points and lines, not a labelled source reporter or the required partition construction.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a partitioned exact source locator.

No checked source supplies the required finite-field exact-source partition instantiation, avoids the pair-pair query family, or supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, `B=N^(1/5)`, five signed coloured disjoint factor decks, a `B`-target known-log deck, Pluecker conventions, partition rule, masks, and verifier.
2. Construct the three labelled `B^2` pair-wedge families and the partition without pair-pair enumeration.
3. Route all relation-target queries, report exact six-point tuples on every admitted stratum, verify at least `B` independent rows, solve every factor log, and verify the solve.
4. Reuse the identical partition and routing rule on fresh scalar-blind masked targets, charging resampling or deck rebuilds.
5. Substitute factor logs, remove masks, retain all ambiguity, and accept only candidates satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Let setup time and memory be `N^a,N^a_m`, `beta=1/5`, reciprocal relation and target densities `N^delta,N^delta_t`, one partition/routing query excluding source emission `N^q,N^q_m`, verified rank credit `N^r`, exact output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; partition construction, every crossed cell and boundary object, all query hyperplanes, output, and verification are charged. Promotion requires the campaign term and all setup/state/log terms at most exponent `0.45`, online `delta_t+q+o+u<=0.25`, and at least `B` verified independent rows. Pollard rho has expected time exponent `0.50` and negligible memory exponent; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Polynomial partitioning reduces incidences among supplied geometric objects. In the frozen wedge form, one hyperplane is induced only after choosing two pair-wedge elements, yielding up to `B^4` queries. Building the conflict lists therefore materializes the missing separator, while the cited real polynomial-sign cell argument supplies no finite-field instantiation that preserves exact source labels.

## Proof track

Prove a finite-field special-family partition theorem, a source-free construction and routing algorithm below `B^(9/4)`, exact all-strata replay, sufficient row rank, reusable factor logs, blind descent, and complete `lambda,mu<=0.45`.

## Disproof track

Show that any conflict-list constructor enumerates `Omega(B^3)` relevant pair-pair state or `B^4` queries, exhibit a boundary stratum lost by the partition, or show that the proposed finite-field instantiation lacks the cited cell-crossing guarantee or exact source replay.

## Positive and negative controls

- Positive: supplied low-dimensional real point-hyperplane instances must match direct incidence reporting.
- Negative: random finite-field pair-wedge families and source-shuffled equal-incidence families must not produce preferred point labels.
- Baselines: P1553 direct `3+3`, IDEAs 052/071/255/257, supplied point-hyperplane reporting, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a proved source-free partition/routing receipt, exact recall, 1,000 verified rows and 100 blind descents at each large size, campaign/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete `lambda,mu<=0.45`.
- Falsify this version if query construction or conflict state reaches `B^3`, if one stratum is lost, or if either complete exponent reaches `0.50`.
- A faster supplied-incidence reporter is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-326/partition_query_materialization_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-326/finite_field_partition_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-326/incidence_controls.json`
- `ideas/artifacts/ECDLP-IDEA-326/cost_analysis.md`

## Interpretation boundary

This rejects the declared polynomial-partition route under the frozen source and finite-field interface. It proves no unrestricted incidence or circuit lower bound. Correct incidence reporting or a relation is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-326/partition_query_materialization_receipt.md` locating the first unavoidable pair-pair query or conflict-list object and expressing its size in `B`-exponents before any run.
