# ECDLP-IDEA-079 — Zero-free partition conditioning

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `rejected_no_exact_witness_path`
- Evidence scale: `toy` approximation identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; approximating a partition function or pinning a likely atom is not an ECDLP break.

## Falsifiable hypothesis

Construct a partition function over the hypergraph of factor-base decompositions of target `R`. If a target-independent activity regime has a uniform zero-free region and inverse-polynomial conditional-probability margin, approximate ratios under sequential atom pinning self-reduce to one exact source tuple; verification rejects approximation errors. The full conditioning, relation, rank, and target-descent cost would be sub-rho.

## Mechanism-new operation

The proposed operation is **zero-free analytic conditioning of the entire decomposition ensemble followed by verified witness self-reduction**. It is not an exact incidence reporter or post-hoc selector. The candidate is rejected as written because the elliptic decomposition hypergraph is dense/unbounded-degree and no zero-free/separation theorem can certify an exact witness.

## Assumptions

1. The partition function has a compact evaluator on the required complex neighborhood.
2. A uniform zero-free disk holds for every conditioning step.
3. Conditional ratios have a known margin that distinguishes zero from nonzero source participation.
4. Sequential pinning returns exact point sources with bounded backtracking.
5. Factor-base calibration and blind target descent use identical activities.
6. Approximation precision, failures, verification, output, rank, and memory are charged.

## Semantic fingerprint

`elliptic_decomposition_partition_function | zero_free_activity_region | conditional_ratio_self_reduction | verified_exact_source_tuple | full_relation_and_target_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the source-fiber generator target.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, where source-fiber joins remain expensive.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H662`, the transposed membership-matrix hypothesis.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the exact full-rank/truncation boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, where nonlinear phase proxies remain full-state.

## Closest primary literature

- Patel and Regts, [Deterministic polynomial-time approximation algorithms for partition functions and graph polynomials](https://arxiv.org/abs/1607.01167), relies on bounded-degree/zero-free hypotheses and does not output exact elliptic witnesses.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the relation fiber but no zero-free ensemble.
- Pollard, [Monte Carlo methods for index computation](https://doi.org/10.1090/S0025-5718-1978-0491431-9), supplies the generic time baseline.

## Complete factor-base-to-target-descent path

1. Freeze the decomposition hypergraph, activities, approximation region, pinning order, factor base, and exact verifier.
2. Prove the partition-function identity and zero-free/margin bounds.
3. Approximate conditional ratios, pin atoms, backtrack all ambiguous steps, and output exact point sources.
4. Verify and collect independent randomized relation rows; solve factor logs.
5. Condition masked blind targets, combine calibrated logs, unmask, and verify all scalar candidates.

## Full rho/BSGS cost model

Rho and BSGS have time exponent `1/2`; BSGS memory exponent is `1/2`. Let evaluator/setup exponent be `s`, graph degree/size `g`, inverse margin/precision exponent `h`, pin/backtrack exponent `c`, factor-base exponent `beta`, relation/target densities `delta,delta_t`, linear algebra `ell`, and memory `mu`. Then `lambda=max(s,g,h,c,beta+delta+c,ell,delta_t+c)`. Exact verification does not repair a self-reduction that misses every witness.

## Likely fatal obstruction

The relation hypergraph has high degree and severe complex cancellation; zeros can approach the chosen activity, destroying approximation. An approximate nonzero ratio cannot certify the presence of an exact source without exponential precision, and sequential conditioning can branch across `B^m` tuples. The method therefore becomes a probabilistic selector or an exact incidence enumerator.

## Proof track

Prove a uniform zero-free region, separation margin, compact evaluator, exact complete self-reduction, and sub-rho full costs.

## Disproof track

Exhibit zeros/near-cancellation under allowed activities, vanishing conditional margins, missed witnesses, or precision/backtracking exponent at least `1/2`.

## Positive and negative controls

- Bounded-degree graph polynomials in a published zero-free regime.
- Planted unique-witness hypergraphs.
- Dense elliptic decomposition hypergraphs.
- Activities near known zeros and equal-density random controls.
- Exact enumeration and verifier checks.
- Blind masked targets with all backtracking retained.

## Quantitative promotion and falsification gates

The necessary theorem gate is a uniform zero-free disk plus inverse-polynomial margin on all conditioned instances. Promotion would require zero missed sources and upper 95% `lambda,mu<=0.45`. The candidate is rejected because neither the bounded-degree nor exact-witness premise holds for the stated decomposition ensemble.

## Artifact plan

- No-go analysis: `ideas/artifacts/ECDLP-IDEA-079/zero_free_boundary.md`
- Prototype: `ideas/artifacts/ECDLP-IDEA-079/partition_condition.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-079/verify_conditioning.py`
- Runs: `ideas/artifacts/ECDLP-IDEA-079/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-079/analysis.md`

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. Approximation quality or a verified lucky witness is not a relation-generation exponent improvement.

## Exactly one next executable action

1. Compute `ideas/artifacts/ECDLP-IDEA-079/zero_free_boundary.md` for exhaustive tiny decomposition hypergraphs, including all complex zeros and conditional margins.

