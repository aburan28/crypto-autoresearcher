# Pre-ID duplicate draft — Valuated-matroid tropical source basis

## Status and claim labels

- Class: `valuated_matroid_tropical_source_basis`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_relation_fibres_are_not_matroid_bases_and_useful_valuations_are_source_bearing`
- Cohort: `20260719-a`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; optimizing a supplied valuated matroid is not an ECDLP break.

## Falsifiable hypothesis

Endpoint equations define a compact valuated matroid whose minimum bases coincide with restricted five-source tuples; tropical exchange and tie-breaking return a unique labelled basis below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile an endpoint valuation oracle satisfying valuated Plücker exchange, optimize to a restriction-compatible minimum basis, and lift that basis to five exact elliptic occurrences**. The new operation is valuated-matroid exchange plus source-basis lift, not a generic matroid solver or tropical reparameterization.

## Assumptions

1. Five-source relation tuples are bases of one target-independent matroid.
2. Public valuations encode target equality without hidden scalar or incidence data.
3. Minimum bases remain exact under arbitrary deck restrictions and signed strata.
4. Ties and exchange paths have bounded charged ambiguity.
5. Oracle construction, exchanges, output, rank, logs, descent, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_valuated_plucker_oracle | tropical_basis_exchange | restriction_compatible_minimum_basis | labelled_source_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; a valuation oracle must construct exact sources from endpoints.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact valuation needs a point-faithful inverse.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; arithmetic source generation and occurrence labels remain unresolved.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-labelled exchange edges are materialized source state.
5. `inputs/ledger_inventory.json` — imported `P1478`; local exact transition structure densifies in full source composition.

## Closest primary literature

- Dress and Wenzel, [Valuated matroids](https://doi.org/10.1016/0001-8708(92)90028-J), defines and studies valuations on supplied matroids; it does not make arbitrary elliptic relation fibres into bases or construct source labels.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no valuated-matroid source oracle.

No checked source supplies the proposed compiler and labelled lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, restrictions, matroid ground set, valuation oracle, exchange/tie policy, and verifier.
2. Build target-independent valuated-matroid state within `B^(9/4+o(1))` without enumerating relation tuples.
3. On known-log targets, decide exact restricted existence and recover five occurrences by basis optimization or charged bisection plus singleton verification.
4. Collect at least `B` independent verified rows, charge ties/exchanges/output, and solve factor logs.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`.
6. Lift the selected basis, substitute logs, remove `t`, and verify `[x]P=Q`.
7. Charge oracle creation, tropical exchanges, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Require `0<=r<=o`, setup/state at most `B^(9/4+o(1))`, complete fresh restricted query at most `B^(5/4+o(1))`, and `lambda,mu<=0.45`. Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Fixed-target elliptic five-sum fibres do not satisfy basis exchange on a target-independent ground set. A valuation that forces precisely the valid tuples must evaluate the missing source predicate or hidden scalar; ties and tropical minima discard occurrence provenance. This meets IDEAs 029, 081, 103, 192, and 248.

## Proof track

Prove a target-independent matroid structure and endpoint-derived valuated exchange oracle, exact restriction/minimum-basis equivalence, labelled lift, and full descent gates.

## Disproof track

Exhibit a basis-exchange failure, a source-bearing valuation, equal valuation/minimum data with different occurrences, or a state/query cap violation.

## Positive and negative controls

- Positive: supplied representable valuated toy matroids with planted unique minimum bases.
- Negative: nonmatroid relation families, equal-weight ties, relabelled bases, restriction-induced exchange failures, and blind targets.
- Baselines: IDEAs 029/081/103/192/248, ordinary matroid optimization, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a proved matroid, endpoint-only valuation, exact all-strata return, `1,000` verified rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one exchange axiom failure, hidden-source valuation, label collision, wrong restriction, cap violation, or exponent at least `0.50`.
- Correct optimization of a supplied toy valuated matroid is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-430/valuated_matroid_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-430/basis_exchange_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-430/restriction_basis_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-430/cost_analysis.md`

## Interpretation boundary

This rejects the screened valuated-matroid source basis, not valuated matroids. Prospective evidence is toy, heuristic, model-bound, and novelty-unverified; an optimization receipt is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-430/valuated_matroid_source_obligations.md` and test the basis-exchange axiom while classifying every ground element, valuation, exchange edge, tie branch, restriction bit, and occurrence label.
