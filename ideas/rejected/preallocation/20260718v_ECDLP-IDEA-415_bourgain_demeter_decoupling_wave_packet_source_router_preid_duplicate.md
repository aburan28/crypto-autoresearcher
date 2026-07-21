# Pre-ID duplicate draft — Bourgain–Demeter decoupling wave-packet source router

## Status and claim labels

- Class: `l2_decoupling_wave_packet_router`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_wave_packets_require_source_incidence_and_lp_control_does_not_decide_exact_restricted_existence`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired theorem preflight only; `review_required`, unapproved, zero-run
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an analytic decoupling inequality is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-derived oscillatory extension operator for the elliptic five-term relation admits exact multiscale decoupling into a subgate family of packets that decides exact nonemptiness under every restriction; charged `O(log B)` dyadic bisection plus singleton verification then recovers a relation below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the relation indicator to an oscillatory extension operator, partition frequency space into curved caps, apply `l2` decoupling and induction on scales, isolate a heavy packet, and invert it to source occurrences**. The required new operation is an exact packet-to-source principle, not a Fourier parameter sweep.

## Assumptions

1. The extension operator and cap amplitudes are computed from endpoints without summing over the hidden source relation.
2. Analytic approximation and `Lp` norm bounds preserve exact zero versus nonzero existence under every restriction.
3. Packet count, precision, induction depth, and residual fit the state/query caps.
4. Packet state decides exact restricted existence; a direct packet-to-occurrence inverse is optional because charged bisection and singleton verification are sufficient.
5. Operator construction, transforms, norms, packets, precision, inversion, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`elliptic_relation_extension_operator | curved_cap_wave_packets | exact_decoupled_nonempty_bit | dyadic_bisection_singleton_verification | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; exact source generation cannot be replaced by an aggregate norm.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; coordinate expansion and preprocessing remain charged.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; tested public predicates did not isolate exact sources.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; full phase matrices show no compact exact source law.
5. `inputs/ledger_inventory.json` — imported `P1478`; sparse analytic transitions still densify at exact composition.

## Closest primary literature

- Bourgain and Demeter, [The proof of the `l2` decoupling conjecture](https://doi.org/10.4007/annals.2015.182.1.9), bounds norms of supplied extension operators after cap decomposition.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides finite-field endpoint equations but no real/complex extension operator with exact occurrence inversion.

No checked source supplies the proposed exact finite-field packet compiler or source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, restrictions, phase lift, extension operator, cap schedule, precision, packet inverse, and verifier.
2. Build target-independent multiscale packet state within `B^(9/4+o(1))` without enumerating source amplitudes.
3. On known-log targets, update restrictions, decide exact nonemptiness from the decoupled packet state, and use charged `O(log B)` dyadic bisection plus singleton verification to recover and verify five occurrences.
4. Collect at least `B` independent verified rows, charging transforms, precision, residual, packet output, ambiguity, and dependencies; solve factor logs.
5. Reuse unchanged packet geometry on fresh scalar-blind `Q+[t]P` targets.
6. Substitute logs, remove `t`, retain every packet inverse branch, and verify `[x]P=Q`.
7. Charge operator construction, cap transforms, induction, norms, precision, residual, inversion, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`; the total fresh online restriction/bisection sequence plus singleton verification must be at most `B^(5/4+o(1))`; and promotion needs `lambda<=0.45` and `mu<=0.45`. Here `q` charges every `O(log B)` positive-parent/negative-child query and singleton verification, while `o` charges final tuple or direct output. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Decoupling bounds aggregate `Lp` mass for a supplied function; it does not decide whether a rare exact finite-field relation exists. Constructing packet amplitudes faithfully requires source incidence, and approximation can erase a positive-parent/negative-child distinction needed by bisection. A noncanonical cap inverse alone is not fatal because exact restricted existence would suffice. This meets IDEAs 044, 155, 326, 341, and 359 at the aggregate-analytic-to-exact-predicate boundary.

## Proof track

Construct an endpoint-only exact finite-field analogue, prove chart-complete restriction-stable zero/nonzero preservation, recover labels by charged bisection and singleton verification, then certify the full descent gates.

## Disproof track

Show packet amplitudes are source sums, exhibit equal retained packet data for restrictions with different existence bits, or prove precision/packet state above the caps.

## Positive and negative controls

- Positive: supplied sparse trigonometric polynomials with planted isolated packets and known atoms must decouple and invert exactly.
- Negative: equal norms with different supports, rare singleton atoms below residual, phase cancellation, signed restrictions, and blind targets.
- Baselines: IDEAs 044/155/326/341/359, full Fourier tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only exact amplitudes, chart-complete restriction-stable existence, charged `O(log B)` bisection and singleton verification, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-amplitude sum, one equal-state/different-existence collision, one residual-missed relation, cap violation, or either exponent at least `0.50`.
- A correct analytic inequality on a supplied toy function is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-415/decoupling_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-415/norm_support_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-415/restricted_existence_bisection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-415/cost_analysis.md`

## Interpretation boundary

This rejects the screened decoupling source router, not decoupling theory. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; an `Lp` estimate is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-415/decoupling_source_obligations.md` and classify every phase, amplitude, cap, norm estimate, residual term, and heavy packet by endpoint versus source dependence while auditing the exact restricted-existence predicate, positive-parent/negative-child bisection, and singleton verification.
