# ECDLP-IDEA-146 — Weak-near-unanimity bounded-width descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative-theorem-gated`
- Top lane: `conservative`
- State: `deferred_needs_factor_base_preserving_WNU_bounded_width_theorem`
- Cohort: `20260718-a`
- Evidence scale: paper preflight only; no experiment ran
- Contract posture: retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs permitted
- Scale labels: every prospective finite test is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; local consistency, a satisfying tuple, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

The fixed-arity projective elliptic decomposition CSP admits a public idempotent weak-near-unanimity (WNU) polymorphism that preserves the factor-base, sign, infinity, repetition, and target relations and gives target-uniform bounded relational width. Enforcing the resulting local-consistency system would then emit every required exact signed factor-base tuple without enumerating the relation fiber, allowing a complete relation campaign and blind masked-target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **factor-base-preserving WNU closure followed by source-faithful bounded-width consistency**. It acts on the actual elliptic constraint language before witness materialization. This differs from IDEA-122's Maltsev/few-subpowers lane: a WNU term supports bounded-width local consistency rather than affine-coset generation. It is new only if its preservation theorem holds for the public factor-base unary relation and its consistency witnesses lift biconditionally to exact sources; changing only the CSP solver is a duplicate control.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and public factor base `F` of size `B=N^beta`.
2. One fixed projective recursive-`S3` signature represents five-source addition, signs, infinity, repeated points, factor-base membership, and a scalar-blind target parameter.
3. A public constant-arity WNU term preserves every basic relation, including the nonalgebraically closed unary relation `F`, on every admitted target and exceptional stratum.
4. A constant-width consistency algorithm returns exact source assignments, not merely satisfiability or a quotient/coset certificate.
5. No operation uses a supplied witness, scalar-labelled table, post-hoc selector, or explicit pair/triple source deck.
6. Setup, local-consistency tables, failed targets, source output, `B+sigma` rank, factor-log solving, blind descent, ambiguity, verification, and peak bit memory are charged.

## Semantic fingerprint

`projective_elliptic_relation_CSP | factor_base_preserving_WNU_polymorphism | bounded_width_local_consistency | exact_signed_source_lift | blind_masked_target_descent`

The removal test is a proved non-affine WNU operation on the actual public relation language plus an exact source lift. Affine/coset closure is IDEA-122; SAT/SMT substitution is a control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, whose unresolved public source-fiber generator is exactly what source-faithful local consistency must supply.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1476`, which requires a complete five-term query exponent below `B^(3/2)`, bounded setup, exact sources, rank, and descent.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where materialized forward/backward serial-`S3` states exceed the complete-query gate.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where a frozen bit-vector CSP backend fails; WNU helps only through a new preservation theorem.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where lossless witness ancestry remains source-distinct and large.

## Closest primary literature

- Barto and Kozik, [Constraint Satisfaction Problems of Bounded Width](https://doi.org/10.1109/FOCS.2009.32), characterize the WNU/bounded-width mechanism but do not prove that an elliptic factor-base relation has the required polymorphism or source lift.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic relation equations but no bounded-width WNU algorithm.

No checked primary source supplies this exact preserving operation and complete descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, the projective constraint signature, WNU identities, consistency width, target masks, and exceptional-stratum policy.
2. Prove preservation of every relation by the same public WNU term without enumerating `F^5` or using scalar indices.
3. Build the bounded-width consistency instance for a public endpoint `R` and lift every accepted local view to an exact signed factor-base tuple.
4. Verify every tuple by direct curve membership and elliptic addition; preserve misses, false lifts, repetitions, infinity cases, and ambiguity.
5. Apply the identical recipe to known `R_j=[r_j]P` until `B+sigma` independently verified rows have rank `B`, charging failed queries and outputs.
6. Solve the factor-base logarithms and independently verify every `[log_P(S)]P=S`.
7. Apply the frozen recipe to fresh `Q+[t]P` masks, substitute verified factor logs, subtract `t`, and retain every candidate.
8. Accept only `x` satisfying `[x]P=Q` and serialize complete time, memory, rank, output, and descent receipts.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; let WNU/CSP construction cost `N^a` time and `N^a_m` memory; reciprocal relation and target densities be `N^delta` and `N^delta_t`; one complete consistency-and-source query cost `N^q` time and `N^q_m` memory; source output and target ambiguity exponents be `o` and `u`; and factor-log linear algebra cost `N^ell` time and `N^ell_m` memory. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

For the baseline `beta=0.20`, constant density/output and `q<=0.25` are needed to reach `lambda<=0.45`. A `B^2` per-query table or width-dependent source expansion already makes the relation campaign at least `N^0.60`.

## Likely fatal obstruction

A generic factor-base subset is not closed under any useful WNU term. Requiring preservation may force an affine/coset language already occupied by IDEA-122, while retaining arbitrary factor-base membership destroys bounded width. Even if local consistency decides existence, exact source unranking can restore the lossless `B^m` ancestry or the P1434 source oracle.

## Proof track

Give an explicit public WNU term; prove all-strata preservation, constant relational width, and a source-assignment biconditional; then derive the stated `lambda,mu<=0.45` through rank, verified factor logs, and blind descent.

## Disproof track

Exhibit a generic admitted curve/factor base on which every candidate WNU violates membership or collapses to affine/coset closure; prove width or exact source lifting grows with `B`; or reduce the lift to an explicit completion table.

## Positive and negative controls

- Supplied bounded-width CSPs with planted WNU operations and known witnesses.
- The same schemas with one factor-base unary relation chosen to break preservation.
- IDEA-122 Maltsev/coset closure and P1480 bit-vector solving as explicit duplicate/backend controls.
- Exhaustive tiny elliptic fibers, including signs, repetitions, infinity, and nonunique tuples.
- Matched generalized-birthday, rho, BSGS, known-log, and blind unknown-log controls.

## Quantitative promotion and falsification gates

Remain deferred. Before any run, independent review must prove one target-uniform preserving WNU, constant width, and exact source lifting. A later toy gate requires `100%` recovery and `0` false tuples on every exhaustive frozen fiber, `B+sigma` verified rank-`B` rows, `100` successful blind descents at each of the two largest sizes, and complete `lambda,mu<=0.45`. Falsify on one source miss, affine/coset collapse, width growth, a `B^2` per-query/source stage, or complete time or memory exponent at least `0.50`.

## Artifact plan

- Bounded-width theorem: `ideas/artifacts/ECDLP-IDEA-146/bounded_width_theorem.md`
- CSP encoder specification: `ideas/artifacts/ECDLP-IDEA-146/csp_encoder_spec.md`
- Frozen fixtures: `ideas/artifacts/ECDLP-IDEA-146/fixtures.json`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-146/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-146/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-146_wnu_bounded_width_preflight.yaml`

All experiment artifacts are prospective. The retired contract permits zero runs.

## Interpretation boundary

This is a deferred, theorem-gated, novelty-unverified proposal. All finite evidence would be toy and all cost projections remain heuristic and model-bound. A correct consistency certificate, tuple, relation, or toy scalar would establish only scoped correctness, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-146/bounded_width_theorem.md` proving or refuting factor-base preservation, constant width, and exact source lifting for the frozen projective relation signature before implementing a CSP solver.
