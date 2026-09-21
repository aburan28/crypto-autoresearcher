# ECDLP-IDEA-210 — Schur-filtration AG-code equivalence descent

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_schur_closure_requires_source_evaluation_tensor`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and information-flow audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; code recovery, a Schur identity, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

A subcubic elliptic AG-code algebra and endpoint-twisted code `C_R` have an iterated Schur/t-closure filtration whose primitive idempotents are exactly all five signed factor sources summing to `R`. Blind closure reconstruction would then produce relations, factor logs, and target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **blind Schur/t-closure reconstruction of an addition pullback** rather than ordinary AG decoding. It merges/rejects because coordinatewise products preserve supplied evaluation positions but do not implement five-fold elliptic addition; encoding that pullback restores the `F^5` evaluation tensor or the missing public source-fiber generator.

## Assumptions

1. Public curve, prime-order group `N`, factor base `B=N^beta`, target, divisors, and code grammar are frozen.
2. Generator matrices are built without an `F^5` evaluation/source table and have length/state at most `B^2.25`.
3. Closure and primitive-idempotent queries cost at most `B^1.25` and return every signed source on every stratum.
4. Twist, evaluation, closure, inverse, output, rank, factor logs, descent, and memory are fully charged.

## Semantic fingerprint

`elliptic_AG_evaluation_algebra | endpoint_twisted_sum_pullback_code | Schur_t_closure_filtration | primitive_idempotents_to_factor_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the implicit-coordinate representation route.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the arithmetic source-fiber generator boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1407-NO-PROMOTION`, the code/evaluation no-promotion control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1408-NO-EC-PROMOTION`, the elliptic-code transfer barrier.

## Closest primary literature

- Couvreur, Márquez-Corbella, and Pellikaan, [Cryptanalysis of McEliece cryptosystems based on algebraic geometry codes and their subcodes](https://arxiv.org/abs/1401.6025), reconstructs geometry already present in supplied code coordinates.
- Couvreur, Márquez-Corbella, and Pellikaan, [Cryptanalysis of public-key cryptosystems that use subcodes of algebraic geometry codes](https://arxiv.org/abs/1409.8220), introduces the t-closure tool without an elliptic sum-fiber compiler.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives the endpoint equation baseline.

No checked source gives the claimed compact sum-pullback generator and labelled inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the codes, divisors, endpoint twist, closure, inverse, masks, and verifier.
2. Build `C_R` for known-log endpoints without a source evaluation tensor.
3. Compute the filtration, map primitive idempotents to exact signed tuples, and verify each row.
4. Collect full rank, solve and verify factor-base logarithms.
5. Apply the unchanged code construction to fresh `Q+[t]P` masks.
6. Substitute logs, subtract `t`, preserve ambiguity, and final-verify `[x]P=Q`, charging all state and output.

## Full rho/BSGS cost model

Rho and BSGS cost `N^(1/2+o(1))`, with BSGS memory matching time. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, closure plus exact inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Promotion requires both time and memory exponents at most `0.45`; an uncharged evaluation tensor invalidates the model.

## Likely fatal obstruction

AG-code reconstruction recovers geometry encoded in a generator matrix. Schur multiplication cannot route addition among distinct factor points. A code containing sum-fiber evaluations has `B^5` coordinates or a `B^3` meet/source deck; translation does not stabilize generic sparse `F`, so a recovered permutation is itself hidden orientation.

## Proof track

Give a compact sum-pullback generator and prove that its closure idempotents are biconditional with all exact signed sources, with complete `lambda,mu<=0.45`.

## Disproof track

Show closure factors through supplied coordinate algebra, source length at least `B^3`, translation requires factor logs, one source is lost, or an exponent is at least `0.50`.

## Positive and negative controls

- Positive control: standard AG codes with supplied evaluation sets and recoverable error-correcting pairs.
- Negative controls: random codes, ordinary error-locator IDEA-014, folded AG IDEA-130, explicit `F^5` tensor, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires code length at most `B^2.25`, query at most `B^1.25`, 100% source recall, zero false tuples, no tensor/source deck, post-aggregation rank `B`, and `lambda,mu<=0.45`. Tensor dependence, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-210/twisted_schur_sum_map_theorem.md`
- Prospective inverse: `ideas/artifacts/ECDLP-IDEA-210/primitive_idempotent_inverse_spec.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-210/fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-210/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-210/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected representation analysis. Finite checks would be toy and projections heuristic and model-bound. Code equivalence, a closure identity, or a relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-210/twisted_schur_sum_map_theorem.md` proving a subcubic five-fold elliptic sum-pullback generator with exact source idempotents, or proving Schur closure requires the source evaluation tensor.
