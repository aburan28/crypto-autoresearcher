# Pre-ID duplicate draft — Karp–Miller coverability source acceleration

## Status and claim labels

- Class: `karp_miller_coverability_acceleration`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_vas_transitions_encode_source_incidence_and_omega_coverability_overapproximates_exact_restricted_equality`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct coverability tree is not an ECDLP break.

## Falsifiable hypothesis

Restricted partial-sum construction can be encoded by a compact endpoint-only vector-addition system whose Karp–Miller acceleration decides exact target reachability; charged `O(log B)` dyadic bisection and singleton verification then recover one occurrence-labelled relation below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile partial-source choices as vector-addition transitions, accelerate increasing branches with omega markings, decide a target marking, and deaccelerate a branch to a labelled firing sequence**. The proposed new step is an exact-reachability and occurrence-return refinement of coverability acceleration.

## Assumptions

1. Places and transitions are compiled from endpoints without listing source compatibility or one transition per occurrence.
2. Omega acceleration preserves exact target equality, signs, multiplicities, and arbitrary restrictions.
3. The accelerated tree and target query fit the frozen state and query caps.
4. The accelerated state decides exact restricted existence; direct deacceleration is optional because charged bisection and singleton verification are sufficient.
5. Compilation, expansion, dominance tests, omega nodes, replay, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_vector_addition_system | karp_miller_omega_acceleration | exact_target_reachability_bit | dyadic_bisection_singleton_verification | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; exact target-wise source emission is the live missing interface.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; recursive state compression must charge public construction.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; exact source-resolving circuits failed after full prefix tests.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`; transposed arithmetic generators still hit materialized source cost.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; source-recoverable state does not promote when materialized.

## Closest primary literature

- Karp and Miller, [Parallel program schemata](https://doi.org/10.1016/S0022-0000(69)80011-5), introduces acceleration for supplied vector-addition style transition systems and decides coverability properties.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives equations but not a compact VAS with exact labelled firing replay.

No checked source upgrades coverability to the required endpoint-only exact restricted source return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, restrictions, VAS compiler, order, acceleration rule, target markings, replay rule, and verifier.
2. Build target-independent places, transitions, and accelerated state within `B^(9/4+o(1))` without source enumeration.
3. On known-log targets, update restrictions, decide exact reachability, and use charged `O(log B)` dyadic bisection plus singleton verification to recover and verify five occurrences; firing replay is optional.
4. Collect at least `B` independent rows, charging transition output, incomparable nodes, omega ambiguity, replay length, and dependencies; solve factor logs.
5. Reuse unchanged VAS state for fresh scalar-blind `Q+[t]P` targets under arbitrary restrictions.
6. Substitute logs, remove `t`, retain every replay branch, and verify `[x]P=Q`.
7. Charge compilation, tree expansion, dominance, acceleration, target tests, replay, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`; the total fresh online restriction/bisection sequence plus singleton verification must be at most `B^(5/4+o(1))`; and promotion needs `lambda<=0.45` and `mu<=0.45`. Here `q` charges every `O(log B)` positive-parent/negative-child query and singleton verification, while `o` charges final tuple or direct output. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Karp–Miller starts from a supplied transition system, so source-faithful transitions encode incidence. The natural five-choice encoding has bounded depth/counters and no useful unbounded increasing branch for omega acceleration; forcing acceleration overapproximates exact elliptic equality with coverability. Lack of canonical firing replay is not independently fatal because bisection would suffice after an exact predicate. This meets IDEAs 070, 120, 154, 364, and 397 at the supplied-transition and exact-reachability boundary.

## Proof track

Construct an endpoint-only bounded-place VAS, prove its accelerated decision equals exact restricted relation existence, recover labels by charged bisection and singleton verification, then certify the full descent gates.

## Disproof track

Show transitions materialize source choices, give coverable but not exactly reachable targets, or prove accelerated state/replay above the caps.

## Positive and negative controls

- Positive: supplied bounded VAS instances with unique short firing sequences must be accelerated and replayed exactly.
- Negative: coverable-not-reachable markings, omega count collisions, different firing words with the same marking, restrictions, signed decks, and blind targets.
- Baselines: IDEAs 070/120/154/364/397, explicit VAS enumeration, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only transitions, exact restricted reachability biconditional, charged `O(log B)` bisection and singleton verification, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing transition, one coverability/existence mismatch, one inexact omega acceleration, cap violation, or either exponent at least `0.50`.
- A correct toy coverability tree is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-412/vas_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-412/coverability_exactness_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-412/restricted_existence_bisection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-412/cost_analysis.md`

## Interpretation boundary

This rejects the screened Karp–Miller source route, not Petri-net coverability theory. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; coverability is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-412/vas_source_obligations.md` and classify every place, transition, marking component, omega node, and dominance comparison by endpoint versus source dependence while auditing the exact restricted-existence predicate, positive-parent/negative-child bisection, and singleton verification.
