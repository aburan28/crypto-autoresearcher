# ECDLP-IDEA-099 — Relative Galois-resolvent block intersection

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_merged_generic_monodromy`
- Top lane: `-`
- Deduplication verdict: relative resolvents are a subgroup-invariant backend for the occupied forward/backward transition intersection; **conditionally**, if the transition action is primitive `S_d` or `A_d`, a source-separating resolvent has dense transition degree. No such monodromy theorem is claimed here for the actual family.
- Evidence scale: no run; any future resolvent/monodromy preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Galois group, resolvent, common root, relation, or toy descent is not an ECDLP break.

## Falsifiable hypothesis

Let the exact forward and backward partial-addition transition polynomials for an output `R` have root sets carrying source ancestry. Their generic monodromy admits a target-independent subgroup chain with useful index `N^gamma`, `gamma<1/2`, and a relative invariant whose resolvent roots label blocks containing compatible forward and backward endpoints. Computing and intersecting these low-degree resolvents, then lifting one common block through the subgroup chain, outputs an exact signed factor-base tuple without materializing the dense transition/resultant object. The same construction yields `B+sigma` independent rows, factor logs, and blind descents with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The operation is **replace root-level forward/backward composition by relative Galois-resolvent block labels, intersect the labels, and lift only the common block to exact endpoint sources**. It is not a different polynomial solver or a dense resultant under new vocabulary: the proposed mathematical gain is a low-index imprimitivity or subgroup invariant that survives composition while retaining a public ancestry inverse.

The candidate is rejected and merged after the semantic screen. Relative resolvents do not create a block system; they expose subgroup invariants of the existing root action. This record supplies neither a proved low-index block system for the actual transition family nor a charged method that recovers exact endpoints from such blocks without expanding the occupied transition intersection. It therefore merges with the P1477/P1478 root/resultant backend regardless of whether the unknown family monodromy is large. **Conditionally**, if a future theorem proves primitive `S_d` or `A_d` monodromy, every subgroup whose orbit singles out a root or useful endpoint block has index at least `d`, with pair/source refinements quadratic or larger. The actual family is not asserted here to have either monodromy group. A future proved non-generic low-index block theorem plus a fully charged source lift would require a versioned successor rather than promotion of this record.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; `F={F_1,...,F_B}` is target-independent with `B=N^beta`, and a fixed split arity is used.
2. Forward and backward transition polynomials are public, separable on a controlled open set, and can be constructed implicitly without enumerating endpoint tuples.
3. Their generic arithmetic/geometric monodromy groups and a target-independent subgroup chain can be computed or proved for the complete curve/factor-base family.
4. A relative invariant of subgroup index `N^gamma`, `gamma<1/2`, labels compatible endpoint blocks and has a public exact lift to endpoint indices, signs, multiplicities, and exceptional branches.
5. Resolvent coefficients and common-block tests use no target scalar, factor logarithm, post-hoc selector, or source-indexed advice.
6. Monodromy setup, invariant evaluation, resolvent construction, coefficient height, factorization, intersection, block lifting, failures, relation density, `B+sigma` rows, rank, factor logs, blind descent, output, verification, and peak memory are fully charged.

## Semantic fingerprint

`forward_backward_transition_polynomials | relative_Galois_resolvent | low_index_block_invariant | common_resolvent_label_intersection | exact_endpoint_lift`

The removal test is exact: survival requires a useful subgroup index below the dense transition degree and an exact source inverse. Computing the same roots/resultant with a Galois package, or a source-free monodromy certificate, is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, where a sparse factor equation gives an exact logarithmic one-transition norm and endpoint extractor but no compressed composition.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, the exact subgroup-norm composition whose two-transition resultant becomes dense quadratic.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where materialized forward/backward state polynomials fail complete five-term membership.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, the serial-S3 forward/backward state-compression contract and closest direct transition-intersection formulation.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where exact shared aggregate norms remain source-incomplete after held-out accounting.

## Closest primary literature

- Stauduhar, [The determination of Galois groups](https://doi.org/10.1090/S0025-5718-1973-0327712-4), introduces subgroup traversal with relative resolvents for polynomial Galois groups; it does not give compressed endpoint intersection for elliptic relation states.
- Fieker and Kluners, [Computation of Galois groups of rational polynomials](https://arxiv.org/abs/1211.3588), develops practical invariant and resolvent methods; its cost is governed by the relevant permutation action and it provides no ECDLP source decoder.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring addition equations but not the low-index monodromy structure.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic square-root comparison boundary.

No checked source proves a low-index relative resolvent with an exact factor-base ancestry inverse for these transition families. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B`, split arity, forward/backward transition constructions, root ordering convention, generic monodromy group, subgroup chain, relative invariant, resolvent normalization, intersection rule, lift map, and exceptional-fiber policy.
2. Prove or compute the generic monodromy on source-labelled toy truth, construct the forward and backward relative resolvents for a public output `R`, and certify coefficients without expanding all endpoint roots.
3. Intersect resolvent labels, lift every common block through the subgroup chain to exact forward/backward endpoint source lists, join them, and independently verify each signed factor-base tuple sums to `R`.
4. Apply the frozen procedure to known random outputs `R_j=[r_j]P`; retain verified rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` rows have rank `B`.
5. Solve all factor-base logarithms modulo `N` and independently verify `[log_P(F_i)]P=F_i` for every `i`.
6. Choose fresh masks `t`, form `R_t=Q+[t]P`, and apply the identical resolvent construction, common-label intersection, block lift, endpoint inverse, and sum verification.
7. Substitute verified factor logs, subtract `t mod N`, retain all candidates and ambiguity branches, and accept only `x` satisfying `[x]P=Q`.
8. Preserve inseparable fibers, wrong group predictions, reducible resolvents, empty/common blocks, failed lifts, rejected candidates, and complete intermediate sizes.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` with constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; monodromy/invariant setup time and memory be `N^a,N^am`; useful subgroup index and resolvent degree be `N^gamma`; coefficient/field-height state be `N^h`; reciprocal relation and target success exponents be `delta,delta_t`; per-resolvent evaluation, factorization, intersection, and lift exponent be `k`; emitted endpoint/source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,gamma,h,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(am,gamma,h,beta+o,ell_m,u)`.

Every subgroup invariant, orbit representative, resolvent coefficient, splitting/factor field, failed target, common block, endpoint lift, `B+sigma` row, source tuple, and candidate is charged. If a useful invariant has index `d`, `d(d-1)`, or the full endpoint count, that degree and storage replace any short symbolic formula. Promotion requires both `lambda<1/2` and `mu<1/2`, not merely exact monodromy or one-transition extraction.

## Likely fatal obstruction

No low-index block theorem or charged source lift is known for the actual transition family, so the proposed resolvent currently only renames the occupied root-level intersection. As a conditional obstruction, **if** the action is primitive `S_d` or `A_d`, it has no nontrivial block system; a subgroup invariant capable of identifying one endpoint has orbit/index at least the transition degree, while identifying compatible endpoint pairs can require quadratic index. Computing that relative resolvent would materialize the same dense composition that P1477/P1478 exposed. This conditional does not establish the actual monodromy. Coarser invariants, when available, distinguish only aggregate orbit type unless an independent exact ancestry inverse is proved and charged.

## Proof track

Determine the generic arithmetic and geometric monodromy, exhibit a proper low-index subgroup/block system, construct a separating invariant, prove that common resolvent labels are biconditional with compatible endpoint pairs, give the exact ancestry lift, and derive complete relation-collection, factor-log, blind-descent, output, and memory bounds with `lambda,mu<1/2`.

## Disproof track

One sufficient disproof track would prove that the actual generic monodromy is `S_d` or `A_d` in a primitive action and lower-bound every useful subgroup index by the dense transition degree. Other disproof tracks are to exhibit endpoint collisions under every proposed smaller invariant or show that resolvent coefficients and lifting enumerate the full root set. Any invariant selected after observing roots or annotated by source indices also disproves the mechanism. This record has not completed the monodromy theorem.

## Positive and negative controls

- Published low-degree polynomials with known Galois groups and independently verified relative resolvents.
- Planted imprimitive transition families with a known low-index block system and exact endpoint labels.
- Matched primitive `S_d/A_d` families where only trivial/coarse low-index invariants exist.
- P1477 state polynomials, P1478 subgroup norms/resultants, and explicit root intersection charged at full cost.
- Exhaustive ordinary toy-curve endpoint tuples with computed permutation actions and source truth.
- Blind masked targets under a frozen subgroup chain, plus matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

No active promotion gate remains. A versioned successor must prove non-generic imprimitive monodromy, a useful subgroup index exponent `gamma<=0.30`, an exact common-label/source biconditional, and symbolic `a,am,h,o,u,lambda,mu<=0.45`. Any later toy preflight would require zero independently verified resolvent/block/source/sum/factor-log/descent errors over 20 curves at each of four increasing sizes, at least 1,000 independent rows, 100 blind descents at each of the two largest sizes, and fresh rank at least `0.8B`. The present formulation remains merged because no useful block theorem or independently charged source lift is supplied. Proved primitive `S_d/A_d` monodromy or a dense-index theorem would strengthen that rejection but is not assumed; common-label lifting equal to the P1477/P1478 root/resultant intersection already confirms the merge.

## Artifact plan

- Generic-monodromy merge proof: `ideas/artifacts/ECDLP-IDEA-099/generic_monodromy_merge.md`
- Frozen transition and invariant specification: `ideas/artifacts/ECDLP-IDEA-099/resolvent_spec.yaml`
- Prospective resolvent prototype: `ideas/artifacts/ECDLP-IDEA-099/relative_resolvent_intersection.sage`
- Independent endpoint verifier: `ideas/artifacts/ECDLP-IDEA-099/verify_resolvent_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-099/analysis.md`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-099/runs/<run-id>/`

## Interpretation boundary

This rejected/merged conservative record is toy, heuristic, model-bound, and novelty-unverified. Its disposition is a semantic merge plus a missing charged block-to-source recovery theorem, not a claim that the actual transition family has `S_d` or `A_d` monodromy. The primitive-monodromy discussion is conditional. A correct Galois group, subgroup chain, resolvent, common block, verified relation, or recovered toy scalar does not establish a compact source inverse, a better-than-rho algorithm, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-099/generic_monodromy_merge.md` formalizing the unconditional semantic merge and the missing charged block-to-source recovery, with primitive `S_d/A_d` monodromy stated only as a conditional sufficient obstruction.
