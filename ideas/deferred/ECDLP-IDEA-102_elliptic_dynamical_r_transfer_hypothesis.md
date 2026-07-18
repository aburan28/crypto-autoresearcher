# ECDLP-IDEA-102 — Elliptic dynamical-R transfer descent

## Status and claim labels

- Class: `composition`
- Risk band: `high-risk`
- State: `deferred_finite_field_identity_required`
- Top lane: `high-risk`
- Evidence scale: no run; any future identity or transfer-matrix preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exact Yang-Baxter identity, commuting transfer matrix, valid relation, or correct toy descent is not an ECDLP break.

## Falsifiable hypothesis

There is an exact finite-field specialization of an elliptic dynamical `R`-matrix or star-triangle relation whose spin states encode public partial elliptic sums and whose local weights enforce membership in a target-independent factor base. The dynamical Yang-Baxter identity reorders a source-labelled `m`-step addition network into commuting transfer matrices with a sub-rho spectral or recursive contraction. Conditioned transfer-matrix elements invert exactly to signed factor-base source tuples, producing `B+sigma` independent rows, calibrated factor logs, and blind target descents with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The operation is **encode partial elliptic addition as a finite-field dynamical face model, apply an exact Yang-Baxter/star-triangle move to reorder contractions, and condition the resulting transfer matrix to recover source spins**. The proposed gain is not another tensor-network contraction order: it is a local integrability identity that would make the global source-labelled transfer operators commute and admit a compact exact spectral representation.

The candidate is deferred behind an identity theorem. Known elliptic dynamical `R`-matrices use highly constrained analytic theta-function weights and a dynamical parameter; their elliptic curve is not automatically the finite-field ECDLP curve. Multiplying weights by an arbitrary factor-base indicator generally destroys the Yang-Baxter or star-triangle identity. Even an exact partition function aggregates paths, so survival also requires source-retaining conditioned matrix elements with complete output accounting.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; a deterministic target-independent factor base `F={F_1,...,F_B}` has `B=N^beta`, and signed relation arity `m` is fixed.
2. Public spin and dynamical-state spaces encode every relevant partial elliptic sum, sign, repeated source, exceptional addition chart, and target boundary condition without hidden scalar labels.
3. Local rational/algebraic weights over a controlled finite extension of `F_p` enforce both elliptic addition and exact factor-base membership and satisfy a symbolic dynamical Yang-Baxter or star-triangle identity on all accepted states.
4. The resulting transfer matrices commute and have a complete exact spectral, Bethe, or recursive representation constructible without enumerating all spin paths.
5. Conditioned matrix elements or marginals recover exact source indices, signs, and multiplicities rather than only a partition sum, trace, determinant, or relation-validity certificate.
6. Weight construction, poles, field extensions, state dimension, transfer matrices, spectral solve, degeneracies, failed fibers, source conditioning, output, `B+sigma` rows, rank, factor logs, blind descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`finite_field_elliptic_face_weights | dynamical_Yang_Baxter_star_triangle_identity | commuting_source_transfer_matrix | conditioned_exact_spin_inverse | blind_descent`

The removal test requires an exact finite-field local identity that remains valid after factor-base restriction and yields source-labelled, not aggregate, outputs. A generic tensor network, matchgate substitution, cluster mutation, analytic identity with no specialization, or post-hoc path selector is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, the closest explicit forward/backward transition network and its dense state-composition boundary.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where materialized serial-S3 state polynomials do not provide complete five-term membership.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact sparse one-transition identity becomes a dense two-transition resultant.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, the nearest proposal to derive exact phases directly from a rational elliptic subtraction circuit.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact transition/value matrices show no useful low public-block or tensor-train rank.

## Closest primary literature

- Felder, [Elliptic quantum groups](https://arxiv.org/abs/hep-th/9412207), constructs elliptic dynamical quantum-group/face-model structures; it does not specialize arbitrary prime-field elliptic factor-base incidence to an exact source decoder.
- Spiridonov, [Elliptic beta integrals and solvable models of statistical mechanics](https://arxiv.org/abs/1011.3798), relates elliptic beta integrals to star-triangle identities; the weights are analytic and do not supply a finite-field factor-base restriction.
- Etingof, [Geometric crystals and set-theoretical solutions to the quantum Yang-Baxter equation](https://arxiv.org/abs/math/0112278), gives algebraic/geometric Yang-Baxter maps, not the required elliptic-addition membership model or source descent.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring exact addition relation without an integrable transfer identity.

No checked primary source gives an exact finite-field dynamical `R`/star-triangle model retaining arbitrary elliptic factor-base source labels. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, spin/dynamical-state sets, local addition and membership weights, spectral parameters, boundary convention, Yang-Baxter/star-triangle normalization, transfer direction, conditioning rule, source inverse, and pole/exceptional-state policy.
2. Prove the local finite-field identity symbolically and independently verify that the complete `m`-step network has nonzero paths exactly for signed factor-base tuples summing to a public output `R`.
3. Use the identity to reorder the network, construct/diagonalize or recursively contract the commuting transfer matrices, condition successive source spins, and output every accepted exact tuple; independently verify membership, signs, multiplicities, and elliptic sum.
4. Apply the frozen network to known outputs `R_j=[r_j]P`; retain verified rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` rows have rank `B`.
5. Solve all factor-base logarithms modulo `N` and independently verify `[log_P(F_i)]P=F_i` for every point.
6. Choose fresh masks `t`, form blind targets `R_t=Q+[t]P`, and apply the identical local weights, transfer identity, spectral/contraction algorithm, source conditioning, and exact sum verification.
7. Substitute verified factor logs, subtract `t mod N`, retain every degeneracy/ambiguity candidate, and accept only `x` satisfying `[x]P=Q`.
8. Preserve identity failures, poles, zero/cancelled weights, incomplete spectra, missed paths, failed conditionals, and all charged state sizes.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` with constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; materialized spin/dynamical-state count be `N^v`; weight/identity/setup time and memory be `N^a,N^am`; target-independent compiled transfer/spectral build work and resident state be bounded by `N^s`; relation and target success probabilities be `N^-delta,N^-delta_t`; complete per-returned-path target-dependent contraction, spectral-solve, and conditioning work be `N^k`; emitted source/path and target-ambiguity counts per successful fiber be `N^o,N^u`; extension-degree/coefficient work and resident state be bounded by `N^h`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,v,s,h,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(am,v,s,h,beta+o,ell_m,u)`.

These are the fully charged time and peak-memory exponents. Every spin, dynamical value,
local weight, pole branch, transfer entry, eigen/Bethe state, degeneracy, failed target,
conditioned marginal, source path, `B+sigma` row, and candidate is charged. Commutativity
or a closed partition function receives no credit if exact source conditioning traverses
the full path space. Promotion requires both `lambda<1/2` and `mu<1/2`.

## Likely fatal obstruction

Integrability is rigid. Felder-type elliptic weights satisfy the dynamical Yang-Baxter equation because of special theta-function identities over analytic elliptic data; the spectral elliptic curve and dynamical labels are not generic `E(F_p)` point addition. Reducing or algebraically specializing can encounter poles, roots of unity, or lost identities. More decisively, multiplying local weights by the arbitrary indicator of `F` usually breaks the identity. If the unrestricted model remains integrable, its transfer trace sums many paths and forgets source provenance; recursive conditioning can require one state or matrix entry per factor-base point or partial sum, reproducing the dense transition network.

## Proof track

Construct explicit finite-field local weights, prove the dynamical Yang-Baxter/star-triangle identity including factor-base restriction and exceptional charts, prove transfer commutativity and completeness, give a biconditional conditioned-matrix-element/source inverse, and derive complete relation-collection, rank, factor-log, blind-descent, output, extension, and memory bounds with `lambda,mu<1/2`.

## Disproof track

Show no proposed weight specialization satisfies the exact identity on all states; exhibit one factor-base restriction that breaks it; prove the transfer matrices have full state rank or incomplete Bethe spectrum; find distinct source paths with identical conditioned data; or lower-bound state/output/conditioning cost by `N^(1/2)`. Any scalar-indexed spin or target-chosen weight also disproves the mechanism.

## Positive and negative controls

- Published low-state elliptic face/star-triangle models with independently checked local identities over their native domains.
- A planted finite-field rational `R`-matrix model with known commuting transfers and exact spin paths.
- Random local weights and the same weights multiplied by arbitrary factor-base indicators.
- P1477/P1478 transition/resultant networks, generic tensor contraction, matchgate, and cluster-rewrite controls matched for state/output size.
- Exhaustive ordinary toy-curve addition paths with all source tuples and exceptional charts known.
- Blind masked targets under frozen weights, with complete path output and matched rho/BSGS accounting.

## Quantitative promotion and falsification gates

The theorem gate requires an exact symbolic finite-field Yang-Baxter/star-triangle identity with factor-base membership, a complete source biconditional, and symbolic `v,s,h,a,am,o,u,lambda,mu<=0.45`. A future toy preflight requires zero independently verified identity/source/sum/factor-log/descent errors over 20 curves at each of four increasing sizes, at least 1,000 independent rows, 100 blind descents at each of the two largest sizes, and fresh rank at least `0.8B`; all upper 95% exponent bounds must be at most `0.45`. Falsify after one reproducible identity failure on an accepted state, one unresolved source collision, or a lower 95% bound `>=0.50` for transfer state, source conditioning, complete time, or memory.

## Artifact plan

- Finite-field identity theorem gate: `ideas/artifacts/ECDLP-IDEA-102/finite_field_identity_gate.md`
- Frozen weight/network specification: `ideas/artifacts/ECDLP-IDEA-102/dynamical_r_spec.yaml`
- Prospective transfer prototype: `ideas/artifacts/ECDLP-IDEA-102/dynamical_r_transfer.sage`
- Independent identity/source verifier: `ideas/artifacts/ECDLP-IDEA-102/verify_transfer_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-102/analysis.md`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-102/runs/<run-id>/`

## Interpretation boundary

This deferred high-risk candidate is toy, heuristic, model-bound, and novelty-unverified. An exact local identity, commuting transfer family, correct partition function, valid relation, or recovered toy scalar establishes only scoped correctness. It does not establish a source-retaining finite-field specialization, a better-than-rho algorithm, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-102/finite_field_identity_gate.md` deriving or disproving an exact finite-field dynamical Yang-Baxter/star-triangle identity that still enforces the frozen factor-base indicator and retains conditioned source labels.
