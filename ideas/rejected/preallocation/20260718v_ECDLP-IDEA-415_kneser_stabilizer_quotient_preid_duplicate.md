# Pre-ID duplicate draft — Kneser stabilizer-quotient source lift

## Status and claim labels

- Class: `kneser_sumset_stabilizer_quotient`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_prime_order_stabilizer_is_trivial_or_full_and_quotient_lift_has_no_occurrence_provenance`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct sumset stabilizer bound is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-derived factor-deck sumsets have a nontrivial target-independent stabilizer whose Kneser quotient decides exact existence for every restricted five-sum query; charged `O(log B)` dyadic bisection and singleton verification then recover original factor occurrences below rho and BSGS.

## Mechanism-new operation

The screened operation is **compute the period subgroup of a restricted iterated sumset, pass to the quotient where Kneser's inequality controls growth, search the compressed quotient, and lift a target coset to five labelled occurrences**. The required new operation is a useful subgroup quotient inside the prime-order ECDLP group, not a parameter change to pair-sum tables.

## Assumptions

1. The exact relevant sumset stabilizer is computed from public deck descriptions without materializing sumsets or Query2P1.
2. The stabilizer is nontrivial, proper, target-independent, and stable under arbitrary restrictions.
3. Quotient search and lift fit the state and query caps with signs and multiplicities.
4. The quotient decides exact restricted existence; a canonical direct coset lift is optional because charged bisection and singleton verification are sufficient.
5. Stabilizer computation, quotient state, search, lift, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`restricted_factor_deck_sumsets | kneser_period_subgroup | exact_quotient_nonempty_bit | dyadic_bisection_singleton_verification | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; exact source-fiber generation remains required after any quotient.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; a structural quotient must survive complete preprocessing accounting.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; predicate-defined factor bases did not create a source-resolving quotient.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; nonlinear phase structure has no demonstrated compact quotient.
5. `inputs/ledger_inventory.json` — imported `P1479`; public feature quotients did not contain factor logs.

## Closest primary literature

- Kneser, [Summenmengen in lokalkompakten abelschen Gruppen](https://doi.org/10.1007/BF01186598), relates sumset growth to a supplied sumset's stabilizer.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies elliptic relation equations but no useful restriction-stable period subgroup or occurrence lift.

No checked source supplies the proposed prime-order quotient and labelled lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the prime-order curve group, signed decks, restrictions, stabilizer rule, quotient encoding, lift policy, and verifier.
2. Build target-independent stabilizer and quotient state within `B^(9/4+o(1))` without enumerating pair or higher sumsets.
3. For known-log targets, update restrictions, decide exact quotient existence, and use charged `O(log B)` dyadic bisection plus singleton verification to recover and verify five occurrences.
4. Collect at least `B` independent verified rows, charging stabilizer tests, coset output, lift ambiguity, cancellation, and dependencies; solve factor logs.
5. Reuse unchanged quotient machinery on fresh scalar-blind `Q+[t]P` targets.
6. Substitute logs, remove `t`, preserve all coset-lift branches, and verify `[x]P=Q`.
7. Charge stabilizer construction, quotient arithmetic, search, lifting, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The ECDLP group has prime order, so its only subgroups are trivial and the whole group. The whole stabilizer cannot distinguish restricted empty from nonempty fibers; the trivial stabilizer gives no quotient compression. Restrictions destroy accidental symmetry, and Kneser's cardinality bound is not an exact target-membership predicate. Lack of labelled summands alone is not fatal because bisection would suffice. This is a clean scoped no-go meeting IDEAs 027, 118, 340, 351, and 389 at the sumset-growth-to-exact-predicate boundary.

## Proof track

Exhibit an endpoint-derived auxiliary group with a nontrivial proper restriction-stable stabilizer, prove its quotient decides exact restricted existence, recover labels by charged bisection, and certify the complete descent gates.

## Disproof track

Prove the stabilizer is trivial/full in the charged group, show restrictions destroy it, or exhibit equal retained quotient states for restrictions with different existence bits.

## Positive and negative controls

- Positive: supplied composite-order groups with planted periodic sumsets and uniquely labelled lifts must compress and replay exactly.
- Negative: prime-order aperiodic sumsets, full-group sumsets, accidental periods broken by restrictions, repeated occurrences, and blind targets.
- Baselines: IDEAs 027/118/340/351/389, explicit quotient tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a nontrivial proper target-independent stabilizer, exact restriction-stable existence, charged `O(log B)` bisection and singleton verification, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on the prime-order subgroup dichotomy, one restriction that kills the period, one equal-quotient/different-existence collision, cap violation, or either exponent at least `0.50`.
- A periodic toy sumset in a composite group is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-415/stabilizer_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-415/prime_order_no_go.md`
- `ideas/artifacts/ECDLP-IDEA-415/coset_lift_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-415/cost_analysis.md`

## Interpretation boundary

This rejects the screened Kneser quotient in the prime-order campaign, not Kneser's theorem. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; a sumset bound is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-415/prime_order_no_go.md` and formalize the trivial/full stabilizer dichotomy for every restricted signed deck sumset used by the proposed descent.
