# ECDLP-IDEA-081 — Toric Markov-fiber walk

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `rejected_scalar_statistic_no_go`
- Evidence scale: `toy` fiber-connectivity preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a connected Markov fiber or sampled valid relation is not an ECDLP break.

## Falsifiable hypothesis

There is a public integer/toric encoding of factor-base exponent vectors whose fiber at target `R` is exactly the set of elliptic decompositions of `R`. A bounded implicit Markov basis connects this fiber, and a rapidly mixing walk reaches a bounded-support source vector with setup, mixing, hit, output, relation-rank, and blind-descent exponents below `1/2`.

## Mechanism-new operation

The operation is **implicit toric fiber connectivity plus source-preserving Markov moves before relation enumeration**. It is not an explicit large-prime table, generic random walk on `<P>`, post-hoc selector, or Markov basis computed from scalar labels. Survival requires an exact small sufficient statistic for elliptic addition, bounded moves, rapid mixing, and exact point-source output.

## Assumptions

1. The toric sufficient statistic is computable from public point data without factor logs.
2. Its fiber equals, rather than contains, valid elliptic decompositions.
3. A target-independent bounded Markov basis is implicit and sub-rho to construct/query.
4. The walk mixes and hits useful bounded-support vectors at proved sub-rho cost.
5. Each vector maps to exact points/signs and independent relation rows.
6. Rejections, mixing diagnostics, rank, descent, verification, and memory are charged.

## Semantic fingerprint

`public_toric_sufficient_statistic | target_decomposition_fiber | implicit_bounded_Markov_basis | rapidly_mixing_source_walk | exact_rows_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1472`, the exact two-large-prime occupancy/query boundary.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1472`, the adjacent restricted theorem for implicit deck queries.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H678`, the open partial-relation/cycle-merger lane.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1471`, where explicit partial-relation enrichment fails.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-005`, where multiplicity duplicates search without rank gain.

## Closest primary literature

- Diaconis and Sturmfels, [Algebraic algorithms for sampling from conditional distributions](https://doi.org/10.1214/aos/1030563990), proves Markov-basis fiber connectivity but not an elliptic sufficient statistic or rapid mixing.
- Gaudry, Thomé, Thériault, and Diem, [A double large prime variation for small-genus curves](https://doi.org/10.1090/S0025-5718-06-01900-4), supplies the nearby partial-relation control.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies exact relation equations but no toric fiber.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F`, exponent-vector encoding, sufficient statistic, Markov moves, walk kernel, and stopping rule.
2. Prove fiber equality and move validity/connectivity against exhaustive tiny decompositions.
3. Initialize without a secret source, walk with complete transition logging, and output bounded-support vectors.
4. Map vectors to point sources, verify relations, and collect a full-rank factor-log system.
5. Walk masked blind target fibers, combine calibrated logs, unmask, and verify all scalar candidates.

## Full rho/BSGS cost model

Rho time and BSGS time/memory exponents are `1/2`. Let encoding/setup exponent be `s`, Markov-basis size/query `m`, mixing exponent `tau`, inverse hit probability `delta`, factor-base exponent `beta`, source/output `o`, linear algebra `ell`, target hit exponent `delta_t`, and memory `mu`. The complete exponent is `lambda=max(s,m,beta+tau+delta+o,ell,tau+delta_t+o)`. Explicit tables and all rejected steps are charged.

## Likely fatal obstruction

The group equation is not a small integer sufficient statistic unless scalar labels are embedded. Without them, toric fibers include false vectors; with them, the encoding already solves factor logs. A target-fiber walk also needs an initial point in that fiber, which is already a decomposition. Markov bases can be exponentially large, and connectivity says nothing about mixing or useful-support hitting. This collapses into an explicit large-prime graph or assumes the missing source oracle.

## Proof track

Construct the scalar-blind exact statistic and implicit moves; prove connectivity, mixing/hit bounds, exact source lift, independent rank, and full sub-rho descent.

## Disproof track

Show fiber equality or initialization requires scalar labels/a known decomposition, the move basis/mixing/hit exponent is at least `1/2`, or emitted rows reproduce ordinary occupancy/rank controls.

## Positive and negative controls

- Published contingency-table fibers with known Markov bases.
- Planted small elliptic fibers with exhaustive connectivity.
- False sufficient statistics that preserve coordinates but not group sums.
- Explicit 2LP graph and uniform random-walk controls.
- Multiple starts and conductance diagnostics.
- Blind masked targets with complete transition logs.

## Quantitative promotion and falsification gates

The identity gate requires exact fiber equality and source-valid moves on every tiny case. Future promotion requires lower 95% conductance bounds supporting `tau<=0.20`, 1,000 independent rows, 100 blind descents, and upper 95% `lambda,mu<=0.45`. Falsify if scalar-blind fiber equality fails or lower 95% basis/mixing/hit exponent is at least `0.50`.

## Artifact plan

- Fiber theorem: `ideas/artifacts/ECDLP-IDEA-081/toric_fiber.md`
- Move generator: `ideas/artifacts/ECDLP-IDEA-081/markov_moves.sage`
- Walk: `ideas/artifacts/ECDLP-IDEA-081/fiber_walk.py`
- Verifier: `ideas/artifacts/ECDLP-IDEA-081/verify_fiber_sources.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-081/analysis.md`

## Interpretation boundary

This deferred idea is toy, heuristic, model-bound, and novelty-unverified. Fiber connectivity or a valid sampled relation is not a useful mixing, rank, descent, or breakthrough result.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-081/toric_statistic_no_go.md` proving that an integer sufficient statistic exact for prime-order subgroup sums either embeds hidden scalar columns or admits false fibers, with connectivity and mixing treated separately.
