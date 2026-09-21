# Pre-ID duplicate draft — Kruskal–Katona restricted-shadow compression

## Status and claim labels

- Class: `kruskal_katona_restricted_shadow_compression`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `scoped_rejected_relation_family_is_not_downward_closed_and_shadow_membership_is_query2p1`
- Cohort: `20260719-a`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired `review_required`, unapproved, zero-run theorem preflight
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid Kruskal–Katona shadow bound is not an ECDLP break.

## Falsifiable hypothesis

The positive five-source relation family admits a target-independent colex compression whose restricted lower shadows preserve exact target equality; navigating shadows and singleton verification returns one labelled tuple below rho and BSGS.

## Mechanism-new operation

The screened operation is **compress each uniform relation family to an initial colex segment, expose its nested lower shadows under deck restrictions, and unrank a surviving chain back to five original occurrences**. This is restricted-shadow source navigation, not a post-hoc selector or generic subset unranking.

## Assumptions

1. Compression preserves exact elliptic target equality, signs, multiplicities, and restrictions.
2. Shadow membership is computed from endpoint state without enumerating positive tuples.
3. A compressed shadow chain lifts canonically to original occurrence labels.
4. Compression and inverse maps remain frozen across fresh targets.
5. Shadow construction, membership, output, ambiguity, rank, logs, descent, time, and memory are charged.

## Semantic fingerprint

`positive_five_source_family | colex_compression | restriction_stable_lower_shadows | singleton_chain_source_unranking | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the positive family and its source lift remain the missing public operation.
2. `inputs/ledger_inventory.json` — imported `ECFG-H662`; exact transposed membership is the relevant query baseline.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; exact membership state retains full source rank.
4. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; cubic source generation and target batches are the materialized control.
5. `inputs/ledger_inventory.json` — imported `P1476`; complete five-term query cost must cross the stated exponent gate.

## Closest primary literature

- Katona, [A theorem of finite sets](https://real.mtak.hu/21121/), proves the extremal lower-shadow result for supplied uniform set families; it does not preserve an external elliptic target predicate or label inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides the endpoint relation but no compact positive-family shadow oracle.

No checked source supplies target-equality-preserving compression and source lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed occurrence decks, restriction tree, colex order, compression/lift maps, and verifier independently of targets.
2. Build target-independent compressed family/shadow state within `B^(9/4+o(1))` without listing positive tuples.
3. For known-log targets, answer exact shadow membership under every restriction and use charged `O(log B)` navigation plus singleton verification to recover five occurrences.
4. Collect at least `B` independent verified rows, charge every negative shadow query and lift ambiguity, and solve factor logs.
5. Reuse unchanged compression on fresh scalar-blind `Q+[t]P` targets.
6. Lift a chain, substitute logs, remove `t`, and verify `[x]P=Q`.
7. Charge family construction, compression, shadows, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation/target densities `N^delta,N^delta_t`, query `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Require `0<=r<=o`, setup/state at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and `lambda,mu<=0.45`. Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Kruskal–Katona concerns shadows of a supplied uniform family and deliberately forgets which upper sets produced a lower set. Elliptic target equality is not downward closed, and computing whether a restricted shadow has a valid completion is exactly Query2P1. A lift preserving original occurrences must store the positive family. This meets IDEAs 055, 148, 169, 357, and 361.

## Proof track

Prove a target-equality-preserving compression, endpoint-only exact shadow membership, canonical occurrence lift on all strata, and the complete descent/cost gates.

## Disproof track

Find one compressed pair with different restricted existence, prove shadow membership is equivalent to completion, or show lift state/output exceeds a gate.

## Positive and negative controls

- Positive: supplied downward-closed toy families and colex segments with known inverse labels.
- Negative: equal-size families with different labelled shadows, target-equality violations, repeated occurrences, empty child restrictions, and blind targets.
- Baselines: IDEAs 055/148/169/357/361, explicit positive-family tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact endpoint-only shadow membership, all-strata label lift, `1,000` verified rows at each of two largest toy sizes, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one target-equality-changing compression, one equal-shadow/different-existence pair, one wrong singleton, cap violation, or exponent at least `0.50`.
- Correct extremal shadow counts on supplied toy families are only controls.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-431/shadow_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-431/equal_shadow_relation_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-431/restriction_shadow_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-431/cost_analysis.md`

## Interpretation boundary

This rejects the screened restricted-shadow source route, not Kruskal–Katona theory. Prospective evidence is toy, heuristic, model-bound, and novelty-unverified; a shadow theorem or count is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-431/shadow_source_obligations.md` and classify positive-family membership, each compression move, shadow query, inverse-chain pointer, restriction decision, and occurrence label by endpoint versus source dependence.
