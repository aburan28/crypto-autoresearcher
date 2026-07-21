# ECDLP-IDEA-409 — Sheffer finite-operator source inversion

## Status and claim labels

- Class: `finite_operator_calculus_inversion`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_restriction_functional_is_query2p1_and_umbral_transform_retains_aggregate_payload_without_labels`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct delta-operator or Sheffer inversion is not an ECDLP break.

## Falsifiable hypothesis

The endpoint-restricted exact relation functional is governed by a target-independent shift-invariant delta operator whose basic Sheffer sequence has a compact umbral inverse, allowing exact restriction bits and one occurrence-labelled tuple to be recovered below rho and BSGS.

## Mechanism-new operation

The screened operation is **derive a shift-invariant delta operator from endpoint restriction updates, construct its basic polynomial/Sheffer sequence, transform the exact relation functional into Sheffer coefficients, and apply the umbral inverse to source occurrences**. The proposal is not a different linear solver: it requires a new finite-operator law tying translations and restrictions to exact sources.

## Assumptions

1. A public exact relation functional and delta operator are computable without Query2P1 calls or source enumeration.
2. The Sheffer sequence and inverse have subgate degree, coefficient, and memory growth.
3. Truncated coefficients preserve rare zero-versus-nonzero existence under every dyadic restriction.
4. Inversion returns factor occurrence labels rather than counts, moments, or an aggregate polynomial.
5. Functional construction, shifts, operator calculus, coefficients, inversion, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_restriction_relation_functional | shift_invariant_delta_operator | Sheffer_basic_sequence_transform | umbral_inverse_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H679`; the current owner requires an actual new nonlinear operation, not a renamed query.
2. `inputs/ledger_inventory.json` — imported `P1474`; restriction updates and exact source return must be charged together.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`; serial state languages and recurrences can densify beyond the gate.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1479`; reparameterizing group-law equations does not remove source inversion.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; full nonlinear phase and labels remain charged.

## Closest primary literature

- Rota, Kahaner, and Odlyzko, [Finite operator calculus](https://doi.org/10.1016/0022-247X(73)90172-8), characterizes delta operators and polynomial sequences of binomial type for supplied shift-invariant operators.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no compact exact restriction functional or Sheffer atom inverse.

No checked source supplies the proposed exact finite-operator law and occurrence inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, restriction variables, functional, delta operator, Sheffer normalization, inverse rule, masks, and verifier.
2. Construct target-independent operator/sequence state within `B^(9/4+o(1))` without evaluating or tabulating all source restrictions.
3. For known-log targets, update the functional under a restriction, transform and invert it to one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging zero/cancellation cases, coefficient output, inverse ambiguity, and dependent rows; solve factor logs.
5. Apply the unchanged operator and inverse to fresh scalar-blind `Q+[t]P` targets under arbitrary restrictions.
6. Substitute factor logs, remove `t`, retain every inverse branch, and verify `[x]P=Q`.
7. Charge functional/operator construction, transforms, coefficient arithmetic, inversion, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Finite operator calculus transforms a supplied functional. Computing the exact relation functional and its restriction updates is already Query2P1. An invertible Sheffer transform preserves the full aggregate payload rather than creating source labels; truncation can miss a rare exact zero, while a complete coefficient set or point inverse can be source-sized. This meets IDEAs 006, 070, 105, 191, and 209 at the recurrence/aggregate-to-atom boundary.

## Proof track

Derive an endpoint-only exact delta-operator law, prove bounded Sheffer state exact under all restrictions, give an occurrence-biconditional umbral inverse, and certify `lambda,mu<=0.45`.

## Disproof track

Show a functional evaluation is Query2P1, exhibit equal retained coefficients with different sources, or prove degree/state/output above the caps.

## Positive and negative controls

- Positive: supplied polynomial functionals with known delta operators, Sheffer bases, and planted atom inverses must replay exactly.
- Negative: equal low-degree coefficients with different supports, rare isolated zeros, non-shift-invariant updates, signed strata, restrictions, and blind targets.
- Baselines: IDEAs 006/070/105/191/209, full coefficient tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only exact functional/operator, restriction-stable occurrence inverse, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one Query2P1 functional call, equal-transform/different-source collision, missed rare zero, cap violation, or either exponent at least `0.50`.
- A correct toy Sheffer transform is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-409/sheffer_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-409/transform_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-409/restricted_inverse_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-409/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic finite-operator route, not Sheffer calculus. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; transform correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-409/sheffer_source_obligations.md` and classify every functional evaluation, shift, delta-operator coefficient, Sheffer basis term, and inverse datum by endpoint versus source dependence.
