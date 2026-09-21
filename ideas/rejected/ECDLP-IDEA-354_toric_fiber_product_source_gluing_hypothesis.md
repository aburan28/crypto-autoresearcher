# ECDLP-IDEA-354 — Toric-fiber-product source gluing

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `merged_rejected_common_multigrading_is_source_provenance_join`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `retired review_required preflight; execution prohibited`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Gröbner basis, compatible lift, or normal form is not an ECDLP break.

## Falsifiable hypothesis

Public two- and three-source partial-addition ideals share an endpoint-only multigrading whose toric fiber product and compatible Markov lifts decide exact restricted fibre nonemptiness inside the P1553 gates.

## Mechanism-new operation

The screened operation is **form a toric fiber product of partial-relation ideals over a common endpoint grading, lift projected-fiber moves, and decide exact nonemptiness after source-deck restrictions**. It is distinct only if the grading and projected fibers are constructed without tuple labels and restrictions update below the query gate.

Minimum-interface correction: a canonical normal form and all fibre points are unnecessary. A target-labelled, subset-stable exact nonemptiness bit under arbitrary dyadic deck restrictions, with `O(log B)` charged reductions, suffices to recover one signed tuple.

## Assumptions

1. Partial-addition ideals are compact and homogeneous under a shared public endpoint grading.
2. Projected fibers and compatible Markov lifts are computed without enumerating transitions.
3. Restricted normal-form or ideal reduction decides exact fibre nonemptiness, so bisection can select one exact source tuple.
4. Target updates, collisions, multiplicities, signs, and all exceptional strata are complete.
5. Ideals, grades, lifts, reduction, output, rank, logs, blind descent, and memory are charged.

## Semantic fingerprint

`endpoint_graded_partial_relation_ideals | toric_fiber_product | compatible_projection_markov_lifts | subset_stable_exact_fibre_decision | dyadic_source_bisection | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the exact source-resolving partition or circuit is the missing operation.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public arithmetic source-fibre generation and transposed batching remain unresolved.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless ancestry survives exact graph compilation.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-faithful recursive layouts retain one terminal record per witness.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1434-GENERATIVE-RULE-POSITIVE-CONTROL`; a supplied graded/generative fibre is an exact control, not an endpoint-only constructor.

## Closest primary literature

- Sullivant, [Toric fiber products](https://doi.org/10.1016/j.jalgebra.2006.10.004), begins with two ideals already homogeneous under the same multigrading and constructs generators under stated degree hypotheses.
- Rauh and Sullivant, [Lifting Markov bases and higher codimension toric fiber products](https://arxiv.org/abs/1404.6392), assumes projected-fiber descriptions and compatible lifts; it does not derive an endpoint-only source grading.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than the common grading or inverse.

No checked source gives an exact source-free elliptic construction; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, partial ideals, grading, lifts, normal form, masks, and verifier.
2. Construct target-independent graded ideals and the toric fiber product without source multidegrees.
3. For known-log targets, reduce restricted target fibres to exact existence bits, bisect to one signed tuple, and replay it.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Apply the identical product and reduction to fresh `Q+[t]P` targets.
6. Lift sources, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge ideal construction, grading, projected fibers, Markov lifts, normal forms, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, and setup/query/density/rank/output/ambiguity/log exponents `a,a_m,q,q_m,delta,delta_t,r,o,u,ell,ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Require `0<=r<=o`, setup/state at most `B^(9/4)`, fresh query at most `B^(5/4)`, and complete `lambda,mu<=0.45`. Rho time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

The literature glues ideals already supplied with compatible gradings and projected fibres; it does not construct an endpoint-derived grading or a subset-stable exact restricted-fibre nonemptiness updater. A coarse endpoint grade can merge tuples, but that collision alone does not close a decision route because bounded restriction correction is allowed. In the audited constructions, making restricted nonemptiness exact introduces tuple/source multidegrees or recomputes projected fibres, reproducing the transition table and the information flow of IDEAs 088/117/325. Pointwise grade separation is only a stronger direct-router control.

## Proof track

Construct an endpoint-only grading and compatible lifts, prove subset-stable exact nonemptiness plus bisection on all strata, and derive complete sub-gate costs.

## Disproof track

Produce a restricted-fibre family with identical available graded state but different exact nonemptiness for which every public updater exceeds the gates, or prove exact restriction updates store at least one token per P1434 witness.

## Positive and negative controls

- Positive: a small toric hierarchical model with supplied grades, projected fibers, and known lifts.
- Negative: source-permuted elliptic fibers sharing all coarse endpoint grades and equal Hilbert data.
- Baselines: IDEAs 081/088/117/195/325, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a source-free grading theorem, subset-stable zero-error nonemptiness plus charged bisection, 1,000 independent rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and `lambda,mu<=0.45`.
- Falsify on a grade-collision family whose every public correction or source section exceeds the gates, source-labelled projected-fibre state, `B^3` gluing traffic, or either exponent at least `0.50`.
- A valid normal form or Gröbner basis cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-354/toric_grade_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-354/projected_fiber_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-354/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-354/cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-derived source gluing, not toric fiber products. All finite checks would be toy, heuristic, model-bound, and novelty-unverified. Algebraic correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-354/toric_grade_obligations.md` and prove whether endpoint-only grading supports subset-stable exact restricted-fibre nonemptiness and charged bisection without one grade or basis token per P1434 witness.
