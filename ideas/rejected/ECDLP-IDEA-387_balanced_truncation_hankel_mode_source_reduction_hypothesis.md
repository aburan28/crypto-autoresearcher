# ECDLP-IDEA-387 — Balanced-truncation Hankel-mode source reduction

## Status and claim labels

- Class: `linear-systems`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_approximate_hankel_modes_do_not_preserve_exact_membership_and_full_realization_is_source_sized`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a low toy Hankel rank or accurate response approximation is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-derived linear input/output realization of serial Semaev transitions has only `B^(1/4+o(1))` simultaneously controllable and observable Hankel modes, and exact removal of the remaining modes preserves complete five-factor membership plus occurrence-labelled blind descent.

## Mechanism-new operation

The screened operation is **form controllability and observability operators for the target-to-source transition system, balance their Hankel modes, truncate modes declared jointly negligible, and backproject an accepted reduced response to factor occurrences**. It differs from ordinary Krylov or recurrence substitutions only if truncation is exact over the finite-field relation predicate and the reduced realization is constructed without the full source-state operator.

## Assumptions

1. Public endpoint equations determine a compact linear realization of every signed two-/three-deck transition without a state per source tuple.
2. A finite-field analogue of balanced truncation separates an exact zero-response subspace from every source-bearing mode, rather than merely bounding analytic error.
3. The retained modes give a biconditional for membership and a canonical, restriction-stable factor-occurrence inverse.
4. The balanced basis is target-uniform and construction plus state fit within `B^(9/4+o(1))`; a complete fresh query fits within `B^(5/4+o(1))`.
5. Realization construction, Gramian/Hankel work, truncation error certification, backprojection, output, rank, factor logs, blind descent, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_transition_realization | controllability_observability_Hankel_modes | exact_balanced_truncation | source_backprojection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H679`; compact cyclic recurrences still require exact source recovery.
2. `inputs/ledger_inventory.json` — imported `ECFG-MX-1478`; one sparse exact transition becomes dense on source-complete composition.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`; compact public features do not contain the needed factor information.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; exact source histories retain distinguishable ancestry information.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`; an exact reduced state did not cross the complete-source gate.

## Closest primary literature

- Moore, [Principal component analysis in linear systems: controllability, observability, and model reduction](https://doi.org/10.1109/TAC.1981.1102568), derives balanced realizations and truncation for stable linear systems with analytic error criteria.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives exact nonlinear finite-field membership equations, not a stable low-order input/output system.

No checked primary source gives an exact finite-field balanced truncation that preserves elliptic relation sources; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, `B=N^(1/5)` signed factor decks, serial transition variables, input/output convention, finite-field balancing rule, truncation certificate, restrictions, masks, and verifier.
2. Construct a target-independent realization and its controllability/observability data within `B^(9/4+o(1))`, without enumerating the two-/three-deck state product.
3. For known-log targets, inject the endpoint residual, propagate only retained Hankel modes, decide exact membership, backproject one accepted response to five occurrence-labelled factors, and verify the signed group sum.
4. Collect at least `B` independent verified rows, charging rejected responses, false positives, missed sources, ambiguity, output, and dependent rows; solve factor logs and verify them.
5. Reuse the unchanged realization and retained modes on fresh scalar-blind `Q+[t]P`, with restrictions frozen before outcomes and every target-dependent recomputation charged.
6. Backproject a factor tuple, substitute verified factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge full/reduced realization construction, Hankel or Gramian arithmetic, certification, propagation, source lift, output, rank, logs, descent, verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Balanced truncation is an approximation method whose small Hankel singular values control norm error, not exact preservation of rare zeros or labelled preimages. Finite fields supply neither the ordered singular-value notion nor stability/error theory used by Moore. Any exact source-bearing realization must distinguish the partial-source histories that existing transition, observer, and memory formulations already expose; constructing its full controllability/observability operators recreates source-sized state. This merges with IDEAs 056, 267, 308, 329, and 330 unless an exact quotient theorem replaces analytic truncation.

## Proof track

Define an exact finite-field balancing invariant, prove discarded modes are source-null for every prospective target/restriction, give a canonical source backprojection, and derive complete exponents at most `0.45`.

## Disproof track

Produce two source instances with identical retained modes but different membership or factor occurrences, or prove that every source-distinguishing mode has nonzero Hankel contribution and the minimal exact realization is source-sized.

## Positive and negative controls

- Positive: supplied low-order stable linear systems and synthetic finite-field systems with a proven exact unreachable/unobservable summand must reduce and backproject exactly.
- Negative: tiny-norm but membership-critical modes, equal-response/different-source systems, random dense transitions, target shifts, arbitrary restrictions, all signed strata, and blind targets.
- Baselines: IDEAs 056/267/308/329/330, full transition matrices, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an exact source-null truncation theorem, retained dimension at most `B^(1/4+o(1))`, `1,000` independent rows, `100` blind descents, frozen state/query caps, zero membership/source errors, and `lambda,mu<=0.45`.
- Falsify on one mode whose removal changes exact membership, one retained-response/source collision, full-realization construction above the setup cap, restriction-specific retraining, or either exponent at least `0.50`.
- A small approximation error or low toy numerical rank is only a model-bound control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-387/hankel_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-387/exact_mode_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-387/source_backprojection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-387/cost_analysis.md`

## Interpretation boundary

This rejects the screened exact-source use of balanced truncation, not model reduction. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; response accuracy or toy relation validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-387/hankel_source_obligations.md` and identify the first mode whose removal can change an exact membership bit or factor occurrence.
