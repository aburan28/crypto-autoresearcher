# ECDLP-IDEA-146 — Weak-near-unanimity bounded-width descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `rejected_exact_sparse_factor_base_WNU_no_go`
- Cohort: `20260718-a`
- Evidence scale: paper preflight only; no experiment ran
- Contract posture: retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs permitted
- Scale labels: every prospective finite test is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; local consistency, a satisfying tuple, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

The fixed-arity projective elliptic decomposition CSP admits a public idempotent weak-near-unanimity (WNU) polymorphism that preserves the factor-base, sign, infinity, repetition, and target relations and gives target-uniform bounded relational width. Enforcing the resulting local-consistency system would then emit every required exact signed factor-base tuple without enumerating the relation fiber, allowing a complete relation campaign and blind masked-target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **factor-base-preserving WNU closure followed by source-faithful bounded-width consistency**. It acts on the actual elliptic constraint language before witness materialization. This differs from IDEA-122's Maltsev/few-subpowers lane only if a non-affine bounded-width algebra survives the public factor-base unary relation; changing only the CSP solver is a duplicate control.

Independent red-team review closes the stated prime-cyclic operation. A polymorphism preserving the group-addition graph is affine. The idempotent WNU identities force equal coefficients `c` with `m*c=1 (mod N)`, so a fixed-arity operation is barycentric averaging. In the one-dimensional prime cyclic group, a nonempty subset closed under repeated affine averages is a singleton or the whole group. The required sparse factor base `1<B<N` therefore cannot be preserved. An arity growing with `N`, a supplied non-group language, or an operation that abandons the addition graph is outside the claimed bounded-width mechanism and must receive a new ID.

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

- Barto and Kozik, [Constraint Satisfaction Problems of Bounded Width](https://doi.org/10.1109/FOCS.2009.32), give the bounded-width algebraic conditions, which require more than displaying one WNU term; they do not make a sparse elliptic factor base closed under averaging.
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

In the stated prime-cyclic addition language, every polymorphism is affine; fixed-arity idempotent WNU identities force barycentric averaging. A sparse non-singleton factor base is not closed under that operation. Dropping the unary factor-base relation makes local consistency irrelevant to source recovery, while retaining source labels restores the lossless `B^m` ancestry or the P1434 oracle.

## Proof track

A mechanism-new successor would have to prove a non-affine operation outside the prime-cyclic addition polymorphism classification, preserve a sparse factor base, provide the full bounded-width operation family and exact source lift, and retain `lambda,mu<=0.45`.

## Disproof track

The scoped disproof is the affine-polymorphism reduction: equal WNU coefficients give averaging, and repeated averaging closes any two-point subset to the whole prime cyclic group. Thus `B=N^beta`, `0<beta<1`, violates preservation before source lifting or cost claims arise.

## Positive and negative controls

- Supplied bounded-width CSPs with planted WNU operations and known witnesses.
- The same schemas with one factor-base unary relation chosen to break preservation.
- IDEA-122 Maltsev/coset closure and P1480 bit-vector solving as explicit duplicate/backend controls.
- Exhaustive tiny elliptic fibers, including signs, repetitions, infinity, and nonunique tuples.
- Matched generalized-birthday, rho, BSGS, known-log, and blind unknown-log controls.

## Quantitative promotion and falsification gates

This operation is rejected at the sparse-factor-base preservation gate. Reopening under a new ID requires a proved non-affine operation outside the scoped group-addition language, a full bounded-width algebra, exact source lifting, and complete `lambda,mu<=0.45`. Costs strictly above `0.45` and below `0.50` are inconclusive and non-promoting; a complete time or memory exponent at least `0.50` is falsifying.

## Artifact plan

- Existing theorem-only producer receipt: `ideas/artifacts/ECDLP-IDEA-146/bounded_width_theorem.md`
- Prospective independent theorem audit: `ideas/artifacts/ECDLP-IDEA-146/bounded_width_theorem_audit.md`
- CSP encoder specification: `ideas/artifacts/ECDLP-IDEA-146/csp_encoder_spec.md`
- Frozen fixtures: `ideas/artifacts/ECDLP-IDEA-146/fixtures.json`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-146/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-146/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-146_wnu_bounded_width_preflight.yaml`

The theorem-only producer receipt exists and is hash-indexed; it is not an experiment
run. Every other artifact is prospective. The retired contract permits zero runs.

## Interpretation boundary

This is rejected, scoped, novelty-unverified evidence. All finite evidence would be toy and all cost projections remain heuristic and model-bound. A correct consistency certificate, tuple, relation, or toy scalar would establish only scoped correctness, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-146/bounded_width_theorem_audit.md` independently checking the affine-polymorphism, Cauchy–Davenport, fixed-arity, and x-only-scope boundaries of the existing theorem receipt, without implementing a CSP solver.
