# ECDLP-IDEA-403 — Petz-recovery endpoint-source channel

## Status and claim labels

- Class: `sufficiency_recovery_channel`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_recovery_requires_source_faithful_state_reference_and_sufficiency_equality`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; equality in data processing or a correct recovered toy state is not an ECDLP break.

## Falsifiable hypothesis

A public source-faithful density operator and endpoint aggregation channel satisfy exact sufficiency for every signed relation restriction, so the Petz map recovers a state whose measurement returns an occurrence-labelled factor tuple and supports blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode source configurations as a state, apply a fixed completely positive endpoint channel, invoke the modular Petz recovery map under equality of relative entropy, and measure the recovered state to exact factor occurrences**. The proposed primitive is a left recovery map, not sampling or generic matrix inversion.

## Assumptions

1. The state, reference state, channel, and measurement are constructed from public endpoints without source enumeration.
2. Data-processing equality and exact recoverability hold for every target and arbitrary deck restriction.
3. Recovery preserves pure occurrence labels rather than only a mixed aggregate state.
4. Matrix dimension, precision, channel application, modular inverses, and measurement stay within the caps.
5. Encoding, channel, recovery, measurement, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`public_relation_density_state | fixed_endpoint_quantum_channel | Petz_modular_sufficiency_recovery | measurement_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; endpoint aggregation still needs exact source return.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; source-faithful encodings are charged as advice.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`; low-order density summaries do not preserve nonlinear sources.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; phase, signs, and orientation remain charged.
5. `inputs/ledger_inventory.json` — imported `P1479`; the unchanged channel must survive every fresh restriction.

## Closest primary literature

- Petz, [Sufficient subalgebras and the relative entropy of states of a von Neumann algebra](https://doi.org/10.1007/BF01212345), characterizes sufficiency for supplied states and subalgebras.
- Petz, [Sufficiency of channels over von Neumann algebras](https://doi.org/10.1093/qmath/39.1.97), studies channel recoverability under exact sufficiency conditions.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations without a source-faithful state/channel construction.

No checked source supplies the proposed elliptic state, exact sufficient channel, and occurrence measurement; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, state encoding, reference, channel, modular inverses, measurement, restrictions, and verifier.
2. Construct target-independent channel/reference state within `B^(9/4+o(1))` without one basis vector or Kraus record per source tuple.
3. For known-log targets, form the endpoint state, apply and recover through the Petz map, measure one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging failed sufficiency, mixed outcomes, ambiguity, output, and dependent rows; solve factor logs.
5. Apply the unchanged channel/recovery to fresh scalar-blind `Q+[t]P` targets under all restrictions.
6. Substitute factor logs, remove `t`, retain all measurement branches, and verify `[x]P=Q`.
7. Charge encoding, channel, modular arithmetic, recovery, measurement, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The Petz map recovers a supplied state only when the channel is sufficient relative to a supplied reference. Encoding all labelled tuples in the state or channel is the missing source dictionary, while endpoint aggregation normally violates reversibility. A recovered mixed state does not canonically select a factor tuple. This meets IDEAs 058, 253, 282, 307, 316, 328, 331, and 332 at the supplied-state and aggregate-recovery boundary.

## Proof track

Construct public compact states and channel, prove exact sufficiency for all restrictions, prove occurrence-biconditional measurement, and certify `lambda,mu<=0.45`.

## Disproof track

Exhibit strict data-processing loss, equal endpoint states with different sources, a source-indexed matrix basis, or dimension/precision/work above the caps.

## Positive and negative controls

- Positive: supplied finite sufficient channels with known Petz recovery and planted orthogonal source labels must recover exactly.
- Negative: irreversible partial traces, nonorthogonal source mixtures, changed reference states, equal endpoint marginals, signed strata, restrictions, and blind targets.
- Baselines: IDEAs 058/253/282/307/316/328/331/332, explicit density tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only compact encoding, exact sufficiency and occurrence measurement, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one strict data-processing case, source-bearing state/channel entry, mixed-source ambiguity, cap violation, or either exponent at least `0.50`.
- A correct toy Petz recovery is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-403/petz_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-403/sufficiency_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-403/recovered_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-403/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic Petz-recovery route, not recovery theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; state recovery correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-403/petz_source_obligations.md` and classify every state, channel, reference, modular inverse, and measurement entry by endpoint versus source dependence.
