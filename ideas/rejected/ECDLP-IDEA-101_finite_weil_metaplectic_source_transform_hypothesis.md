# ECDLP-IDEA-101 — Finite Weil-metaplectic source transform

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `merged_rejected`
- Top lane: `-`
- Evidence scale: semantic/dimension screen only; no run; any future transform check would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: exact Heisenberg/Weil intertwiners are the occupied theta/character/quadratic-phase transform family; in the proposed Schrödinger/Lagrangian delta-source realization, retaining all `N` point labels restores `N` delta states or a source-indexed dictionary.
- Breakthrough claim: **none**; an exact phase transform, sparse coefficient, valid relation, or correct toy descent is not an ECDLP break.

## Falsifiable hypothesis

Embed the source-labelled elliptic relation tensor in a finite Heisenberg representation whose Lagrangian models are related by canonical Weil/metaplectic intertwiners. There is a target-independent symplectic transformation under which factor-base addition convolution becomes sparse or block diagonal, while conditioned inverse intertwiners recover the exact signed factor-base sources. Computing these transformed coefficients yields `B+sigma` independent rows, factor logs, and blind target descents with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **apply an exact finite Weil intertwiner between Lagrangian models, read sparse relation amplitudes, and invert conditioned amplitudes to source tuples**. The representation would turn elliptic addition incidence into a phase-space operator rather than a coordinate resultant.

The candidate is merged and rejected. Canonical Heisenberg/Weil transforms are exact Fourier/quadratic-phase basis changes already covered by theta, additive-character, heavy-spectrum, and stabilizer proposals. In the **specific finite Heisenberg Schrödinger/Lagrangian model proposed here**, representing all `N` group elements as distinct delta-source states uses a Lagrangian state space of size `N`; scalar-indexed delta states presuppose the DLP orientation, while public point coordinates produce an arbitrary factor-base indicator with no proved sparse spectrum. This does not deny that a cyclic group has faithful one-dimensional characters: such a character is not the proposed delta-source realization and does not by itself invert a transformed relation coefficient to exact factor-base ancestry. Exact delta-source conditioning reconstructs the dense basis/table.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; a deterministic factor base `F={F_1,...,F_B}` has `B=N^beta` and fixed signed relation arity `m`.
2. There is a scalar-blind public map from elliptic points and addition states to a finite symplectic space and Heisenberg representation, including exceptional points and signs.
3. Elliptic addition convolution corresponds exactly to a target-independent operator admitting a canonical Weil/metaplectic transform, not an approximation or a transform indexed by hidden scalars.
4. The transformed factor-base relation tensor has support or block exponent below `1/2` on a positive-density set of ordinary curves and targets.
5. Conditioned inverse transforms recover exact factor-base indices, signs, and multiplicities rather than only a count, phase, character sum, or relation certificate.
6. Representation dimension, all kernels/phases, transform queries, coefficient precision, source conditioning, output, `B+sigma` rows, rank, factor logs, blind descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`finite_Heisenberg_relation_model | canonical_Weil_metaplectic_intertwiner | Lagrangian_sparse_relation_basis | conditioned_inverse_source_transform | blind_descent`

The collision key is `exact character/quadratic-phase basis change + scalar orientation or dense delta-source conditioning`. A new name for Fourier, theta, stabilizer, or additive-character filtering is a merge unless a proved operation removes both the Schrödinger/delta-state footprint and source-output barriers. Faithful one-dimensional cyclic characters are not ruled out; they simply do not supply this source inverse.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1422-EXACT-CHARACTER-FILTER-CONTROL`, the nearest exact deterministic curve-only additive-character kernel control.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, where tested character kernels remain full pair-state rank and truncation loses recall.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact transposed factor-polynomial matrices expose no low public-block or tensor-train rank.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, the closest unverified proposal to derive additive-character phases from the rational subtraction circuit.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1475`, the residual-character support-concentration contract and direct phase-sparsity boundary.

## Closest primary literature

- Gurevich and Hadani, [The categorical Weil representation](https://arxiv.org/abs/1108.0351), constructs canonical intertwining kernels between finite-field Lagrangian models; it does not encode arbitrary elliptic factor-base sources or give sublinear source inversion.
- Green and Tao, [An inverse theorem for the Gowers U3 norm](https://arxiv.org/abs/math/0503014), is nearby primary work on quadratic-phase structure; it does not imply concentration for generic elliptic relation indicators, and its scope must not be transferred without proof.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring relation tensor without a sparse metaplectic basis.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic square-root comparison boundary.

No checked source gives a scalar-blind finite Weil model with sparse, exact, source-invertible elliptic relation coefficients. Novelty remains unverified, and the operation family is occupied.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the symplectic space, Heisenberg representation, Lagrangian models, point/state embedding, phase normalization, intertwiner sequence, sparsity rule, conditioned inverse, and exceptional-state policy.
2. Construct and verify the relation operator for a public output `R` without scalar labels or source enumeration; apply the exact canonical intertwiner and enumerate every accepted transformed coefficient/block.
3. Condition and invert each accepted coefficient to exact signed members of `F`, then independently verify the reconstructed tuple and its elliptic sum `R`.
4. Apply the frozen transform to known outputs `R_j=[r_j]P`; retain verified rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` rows have rank `B`.
5. Solve all factor-base logarithms and independently verify `[log_P(F_i)]P=F_i` for every point.
6. Choose fresh masks `t`, form `R_t=Q+[t]P`, and apply the identical operator construction, transform, coefficient selection, conditioned inverse, and exact sum verification.
7. Substitute verified factor logs, subtract `t mod N`, retain the complete ambiguity list, and accept only `x` satisfying `[x]P=Q`.
8. Preserve zero/cancelled coefficients, missed sources, phase ambiguities, failed inverse branches, rejected candidates, and complete transform dimensions.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` with constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; the materialized/query footprint of the proposed finite Heisenberg Schrödinger delta-state realization be `N^v`; kernel/setup time and memory be `N^a,N^am`; transformed support/block count be `N^s`; reciprocal relation and target success probabilities be `N^-delta,N^-delta_t`; work per returned transformed/source branch be `N^k`; source-output and target-ambiguity counts be `N^o,N^u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,v,s,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(am,v,s,beta+o,ell_m,u)`.

Every Schrödinger/Lagrangian delta state actually materialized or queried, intertwining kernel, phase, coefficient, cancellation, source-conditioning query, failed target, `B+sigma` row, and output candidate is charged. A fast formula for one coefficient receives no credit if exact source recovery in this realization queries all coefficients or all `N` delta states. The exponent `v` is not a claim about the minimum dimension of an arbitrary faithful representation of the cyclic subgroup. Promotion would require both `lambda<1/2` and `mu<1/2`.

## Likely fatal obstruction

The proposed irreducible finite-Heisenberg Schrödinger representation has dimension determined by its Lagrangian size. Encoding all order-`N` point states as **distinct delta-source states in that realization** therefore entails `N` positions or an equivalent source dictionary. A scalar-indexed delta coordinate makes the desired orientation the discrete logarithm itself. A public coordinate embedding avoids that circularity but makes factor-base membership an arbitrary sparse indicator; no generic sparse Weil spectrum is proved. Conditioning enough coefficients to identify the original tuple then performs the full inverse transform or materializes a source dictionary. A faithful one-dimensional cyclic character exists but carries only a phase under a chosen scalar orientation; it neither contradicts this realization-specific obstruction nor provides exact source provenance.

## Proof track

A versioned successor must construct a scalar-blind symplectic/Heisenberg model of elliptic addition, prove a target-independent transform with support exponent below `1/2`, prove an exact conditioned source biconditional, and derive full relation-collection, rank, factor-log, blind-descent, output, and memory exponents below `1/2`.

## Disproof track

Prove that every scalar-blind **Schrödinger/Lagrangian delta-source realization of the proposed kind** must expose `N` point states or an equivalent source dictionary, show that its point embedding requires scalar coordinates, exhibit dense transformed support under public coordinates, or find distinct source tuples with identical conditioned coefficients below the full inverse-transform threshold. Reduction to additive-character, theta, or stabilizer filtering confirms the merge. The existence of faithful one-dimensional cyclic characters is not a disproof target.

## Positive and negative controls

- Published finite Heisenberg representations with independently checked canonical intertwiners.
- Planted quadratic-phase/stabilizer functions with genuinely sparse Weil transforms and known inverse sources.
- Random sparse point indicators and generic relation tensors matched for dimension and density.
- Exact P1422 character kernels, P1475 residual-character buckets, theta transforms, and ordinary Fourier transforms.
- A forbidden scalar-indexed embedding compared with a public-coordinate embedding on exhaustive ordinary toy curves.
- Blind masked targets under a frozen transform, plus matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

No active promotion gate remains for this merged formulation. A versioned mechanism-new successor must prove `v,s<=0.30` for its explicitly specified representation/query model, an exact source biconditional, and symbolic `a,am,o,u,lambda,mu<=0.45` without scalar orientation. Any later toy preflight would require zero independently verified transform/source/sum/factor-log/descent errors over 20 curves at each of four increasing sizes, at least 1,000 independent rows, and 100 blind descents at each of the two largest sizes. Falsify if the delta-source embedding uses hidden scalar indices, transformed support has lower 95% exponent `>=0.50`, one accepted coefficient has unresolved source multiplicity, or every complete arm has `lambda>=0.50`.

## Artifact plan

- Transform-family merge proof: `ideas/artifacts/ECDLP-IDEA-101/weil_character_merge.md`
- Frozen representation specification: `ideas/artifacts/ECDLP-IDEA-101/weil_model_spec.yaml`
- Prospective transform prototype: `ideas/artifacts/ECDLP-IDEA-101/finite_weil_transform.sage`
- Independent coefficient/source verifier: `ideas/artifacts/ECDLP-IDEA-101/verify_weil_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-101/analysis.md`
- Any future receipts: `ideas/artifacts/ECDLP-IDEA-101/runs/<run-id>/`

## Interpretation boundary

This merged/rejected record is toy, heuristic, model-bound, and novelty-unverified. A correct Heisenberg representation, canonical intertwiner, sparse planted transform, phase identity, verified relation, or toy scalar is not evidence of generic source compression, a below-rho result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-101/weil_character_merge.md` proving that scalar-blind exact source inversion in the proposed finite-Heisenberg Schrödinger/delta-source realization either queries all `N` point states or reduces to the occupied additive-character/theta/quadratic-phase transform family, without making a claim about arbitrary faithful cyclic representations.
