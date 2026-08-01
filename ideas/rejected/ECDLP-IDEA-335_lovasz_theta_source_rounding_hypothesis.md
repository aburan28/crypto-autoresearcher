# ECDLP-IDEA-335 — Lovasz-theta source rounding

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_theta_relaxation_requires_explicit_conflict_graph_and_rounding_is_not_exact_source_recovery`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an SDP bound, rounded independent set, valid relation, or toy tuple is not an ECDLP break.

## Falsifiable hypothesis

The six-list source conflicts admit a compact implicit graph whose Lovasz-theta semidefinite solution has a target-independent exact rounding rule that returns relation tuples within the P1553 campaign and query rectangles.

## Mechanism-new operation

The screened operation is **encode incompatible partial source assignments as graph edges, solve an orthonormal-representation/theta SDP, and round one feasible independent transversal to an exact signed tuple**. This merges with IDEAs 104, 123, 137, 200, 231, 257, 289, and 328: constructing conflict edges is source incidence, theta is an aggregate bound/relaxation, and rounding is approximate unless a separate exact integrality theorem already identifies the source.

## Assumptions

1. The conflict graph and SDP operator are evaluable implicitly without `B^3` edges or source-labelled adjacency.
2. The frozen special graph has an exact integrality/rounding theorem on every source stratum.
3. Rounding returns all required independent relation rows, not one post-hoc planted witness.
4. Graph construction, SDP rank/precision, rounding, output, rank, factor logs, descent, verification, and memory are charged.
5. The same graph grammar and rounding rule apply to fresh masked targets.

## Semantic fingerprint

`elliptic_partial_assignment_conflict_graph | Lovasz_theta_orthonormal_representation | exact_integral_rounding | signed_source_transversal | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed relation-batch generator hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-H670`, the supplied bilinear leaf-incidence hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the explicit lossless edge-state boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank public matrix control.

## Closest primary literature

- Lovasz, [On the Shannon capacity of a graph](https://doi.org/10.1109/TIT.1979.1055985), introduces the theta function as a computable aggregate upper bound from a supplied graph.
- Goemans and Williamson, [Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming](https://doi.org/10.1145/227683.227684), is a generic SDP-rounding contrast, not a theta-specific rounding theorem, and returns an approximation from a supplied relaxation rather than an exact elliptic source witness.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint constraints, not a compact conflict graph or integrality theorem.

No checked source supplies the implicit graph, exact rounding, or full ECDLP descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, coloured decks, conflict predicate, SDP operator, exact rounding rule, source policy, masks, and verifier.
2. For known-log targets, solve the implicit theta relaxation, round exact tuples on all strata, and verify every relation.
3. Collect at least `B=N^(1/5)` independent rows, solve all factor logs, and independently verify them.
4. Apply the identical graph and rounding rule to fresh scalar-blind masked targets.
5. Substitute logs, remove masks, retain every rounding branch, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, graph/SDP work excluding output `N^q,N^q_m`, verified rank `N^r`, exact output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Adjacency evaluation, SDP dimension/rank, precision, iterations, all rounding trials, output, and verification are charged; `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The theta function acts on a supplied graph and provides a bound or relaxation. The elliptic conflict graph's adjacency is the missing source incidence. Generic SDP rounding is probabilistic and approximate; an exact integral special-family theorem would itself be the new source locator and is unsupplied.

## Proof track

Prove a compact adjacency oracle, bounded-rank exact theta formulation, integrality and all-strata rounding, relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Show adjacency answers source completion, exhibit an integrality gap or label-permuted equal SDP solution, or charge graph/SDP state at `B^3` or worse.

## Positive and negative controls

- Positive: supplied perfect-graph instances with known exact theta integrality must round correctly.
- Negative: graphs with theta gaps and source-label permutations must not yield preferred elliptic tuples.
- Baselines: IDEAs 104/123/137/200/231/257/289/328, explicit conflict graph, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with compact graph and exact integrality theorems, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if explicit adjacency reaches `B^3`, an SDP gap exists, one source is missed, or either exponent reaches `0.50`.
- An approximation ratio or correct bound is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-335/conflict_graph_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-335/theta_integrality_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-335/sdp_gap_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-335/cost_analysis.md`

## Interpretation boundary

This rejects the declared theta-rounding path, not semidefinite methods generally. A bound or approximate rounded solution is not exact source recovery, a complete ECDLP algorithm, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-335/conflict_graph_input_receipt.md` expressing one adjacency query in elliptic source terms and measuring the smallest complete implicit graph representation.
