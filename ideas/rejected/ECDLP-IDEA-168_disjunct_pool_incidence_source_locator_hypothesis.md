# ECDLP-IDEA-168 — Disjunct-pool incidence source locator

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `none`
- State: `rejected_supplied_restricted_decomposition_oracle`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and semantic no-go only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: finite checks would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; group-testing recovery, a valid tuple, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-independent `d`-disjunct family of pools over signed factor-base atoms, together with exact public yes/no tests for whether an endpoint has a decomposition restricted to each pool, yields a nonadaptive group-testing decoder for all exact source supports. The resulting relations and masked target decompositions would be complete and sub-rho.

## Mechanism-new operation

The operation is **restricted-decomposition pool testing followed by disjunct support decoding**. The pooling design is new, but it qualifies only if every pool test is implemented from public endpoint data below budget. Supplying test outcomes, a source tuple, or a materialized pool-sum deck is a control.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, pool matrix, test semantics, masks, and verifier are frozen.
2. Each restricted-decomposition test is exact on all source multiplicities and sign strata.
3. Tests are constructed without enumerating pool tuples or using an unrestricted decomposition oracle.
4. The defective/source model and list decoder remain valid under many possible decompositions.
5. Pool construction, tests, outputs, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`factor_atom_disjunct_pools | exact_restricted_elliptic_decomposition_tests | nonadaptive_support_decoder | exact_source_tuple_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete five-source gate.
3. `inputs/ledger_inventory.json` — imported `ECFG-H680`, the nearest source-locator hypothesis.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1431-CANONICAL-ROOT-PRODUCT-NO-PROMOTION`, where canonical root products do not promote.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge cost boundary.

## Closest primary literature

- Kautz and Singleton, [Nonrandom binary superimposed codes](https://doi.org/10.1109/TIT.1964.1053689), supplies disjunct-code recovery after tests are available.
- Porat and Rothschild, [Explicit nonadaptive combinatorial group testing schemes](https://arxiv.org/abs/0712.3876), supplies efficient pool designs, not elliptic decomposition tests.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies relation equations but no restricted yes/no oracle.

No checked source supplies the complete pipeline; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze pools, restricted-test algorithm, factor base, multiplicity model, masks, decoder, and verifier.
2. Implement every pool test from endpoints without source enumeration or oracle advice.
3. Test known `R_j=[r_j]P`, decode candidate supports, reconstruct full signed tuples, and enumerate all allowed multiplicities.
4. Verify tuples; preserve false tests, support collisions, multiple decompositions, misses, and output.
5. Collect rank `B`, solve and verify factor-base logs.
6. Apply the identical tests to fresh `Q+[t]P` masks.
7. Substitute logs, remove masks, keep all candidates, and verify `[x]P=Q`.
8. Charge pool construction, every restricted test, tuple reconstruction, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, all pool tests plus reconstruction `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

Every pool tuple, yes/no computation, collision, and decoder list is charged.

## Likely fatal obstruction

Each pool test is itself a constrained elliptic decomposition query—the missing source oracle. Materializing pool sums restores `B^m` work, while many possible tuples violate the sparse-defective semantics required for disjunct decoding.

## Proof track

An outside-scope successor must construct exact restricted tests below budget, prove multi-decomposition decoder correctness, and derive `lambda,mu<=0.45`.

## Disproof track

Reduce a pool test to the original relation fiber, expose materialized `B^m` states, produce indistinguishable multi-source outcomes, or derive exponent at least `0.5`.

## Positive and negative controls

- Planted sparse defectives with supplied test outcomes.
- Random and explicit disjunct matrices.
- Supplied decomposition oracles and materialized pool-sum tables.
- Exhaustive toy fibers, rho, BSGS, and blind-target checks.

## Quantitative promotion and falsification gates

This version is rejected. Reopening requires an endpoint-only exact pool-test operation and multi-decomposition source theorem with `lambda,mu<=0.45`. Any supplied outcome, source enumeration, source collision, or exponent at least `0.5` is falsifying.

## Artifact plan

- Oracle-circularity proof: `ideas/artifacts/ECDLP-IDEA-168/disjunct_pool_oracle_no_go.md`
- Prospective pool-test specification: `ideas/artifacts/ECDLP-IDEA-168/pool_test_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-168/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-168/cost_analysis.md`

All paths are prospective; no experiment ran.

## Interpretation boundary

This is rejected, novelty-unverified evidence. Finite checks are toy and costs heuristic and model-bound. Correct group testing after supplied tests is not an ECDLP result or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-168/disjunct_pool_oracle_no_go.md` reducing the declared pool test to constrained decomposition or explicit source-deck construction.
