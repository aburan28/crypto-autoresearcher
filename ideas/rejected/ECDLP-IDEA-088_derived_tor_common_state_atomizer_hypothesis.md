# ECDLP-IDEA-088 — Derived-Tor common-state atomizer

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `merged_rejected`
- Screen disposition: derived tensor product is a generic intersection backend; no experiment was run
- Evidence scale: semantic/theorem screen only; any future check would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a nonzero Tor group, intersection multiplicity, valid relation, or correct toy descent is not an ECDLP break.

## Falsifiable hypothesis

Let `X_u^+` encode forward factor-base partial sums ending at common state `u`, and let `X_{R,u}^-` encode backward complements from output `R` to `u`. The derived intersection `O_{X^+} tensor^L O_{X_R^-}` has bounded Tor amplitude and a target-independent multigraded witness basis whose basis vectors invert exactly to the two endpoint source lists. If that basis and inverse are implicitly computable with sub-rho output, then `B+sigma` full-rank relation rows and blind target descents can be emitted below the rho/BSGS boundary.

## Mechanism-new operation

The screened operation is **replace classical forward/backward intersection by a derived tensor product and read exact endpoint ancestry from a multigraded Tor basis**. Higher Tor can retain excess-intersection information that a set-theoretic common state loses. However, a generic free resolution, Koszul complex, sparse solver, dense resultant, shared union GCD, or source-free Tor dimension is only an intersection backend/control. The screen found no new mathematical operation that compresses endpoint ancestry: source multigrading materializes the same dense incidence object, so this record is merged and rejected without promotion.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; the target-independent factor base has size `B=N^beta`, and the forward/backward split is fixed.
2. Forward and backward incidence schemes have public implicit presentations that do not enumerate all endpoint tuples.
3. Their derived tensor product has uniformly bounded Tor amplitude and a canonical multigraded basis, not merely dimensions or Euler characteristics.
4. Each basis vector has an exact public inverse to signed endpoint indices and multiplicities, including nontransverse and repeated-source branches.
5. The grading, resolution order, and inverse are frozen before relation and target instances and contain no factor logs or target-scalar advice.
6. Resolution construction, syzygies, Tor bases, common-state collisions, endpoint output, failed intersections, `B+sigma` rows, rank, factor logs, blind descent, candidate lists, and peak memory are fully charged.

## Semantic fingerprint

`forward_backward_incidence_schemes | derived_tensor_product | bounded_Tor_amplitude | multigraded_witness_basis | exact_endpoint_ancestry`

The semantic screen rejects the candidate unless derived structure gives a smaller source-invertible object than the classical dense incidence. Merely changing the intersection solver or retaining a source-free homology class is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, where forward/backward serial-`S3` state polynomials become dense and fail held-out recurrence compression.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact one-transition norm identity composes to a dense quadratic two-transition resultant.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where amortized normalized row norms do not promote after complete held-out accounting.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1428-EXACT-SHARED-UNION-CONTROL`, the exact balanced shared-union product/GCD primitive that remains a positive backend control.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where a bit-vector solver substitution for serial-`S3` membership fails its staged completeness gate.

## Closest primary literature

- Arinkin, Căldăraru, and Hablicsek, [Derived intersections and the Hodge theorem](https://arxiv.org/abs/1311.2629), studies formality of derived intersections; it does not give a factor-base endpoint basis or ECDLP descent.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring forward/backward addition equations without derived source atomization.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic-group comparison boundary.

No checked primary source supplies the claimed multigraded Tor-to-endpoint inverse. Novelty remains unverified, and the generic-backend overlap is already sufficient for the merged disposition.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F`, split arity, common-state coordinates, forward/backward ideals, multigrading, resolution policy, Tor-basis normalization, and exceptional-intersection policy.
2. Build implicit forward and backward incidence modules for a public output `R`, form a verified free/Koszul resolution, and compute the derived tensor product without expanding all endpoint tuples.
3. Enumerate every relevant Tor-basis vector, apply the proposed ancestry inverse to both endpoint source lists, join them, and independently verify that the complete signed factor-base tuple sums to `R`.
4. Apply the frozen construction to known outputs `R_j=[r_j]P`; retain rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` verified rows have rank `B`.
5. Solve for all factor logs and independently verify every equality `[log_P(F_i)]P=F_i`.
6. Choose fresh masks `t`, set `R_t=Q+[t]P`, and apply the identical derived intersection, Tor-basis normalization, endpoint inverse, and exact sum verification.
7. Combine verified factor logs to recover candidates for `x+t`, subtract `t mod N` to unmask, and retain every ambiguity branch.
8. Accept only a scalar satisfying `[x]P=Q`; preserve empty intersections, unresolved Tor classes, and rejected candidates.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` with constant-state memory; BSGS has time and memory exponents `1/2`. Let resolution/derived-tensor construction time/memory exponents be `d_t,d_m`, common-state exponent be `c`, Tor-basis exponent be `tau`, factor-base exponent be `beta`, reciprocal relation/target success exponents be `delta,delta_t`, per-basis normalization/ancestry-inverse exponent be `k`, endpoint/source output exponent be `o`, target ambiguity exponent be `a`, linear-algebra time/memory exponents be `ell,ell_m`, and `sigma=N^o(1)`. Then

`lambda=max(d_t, c, tau, beta+delta+tau+k+o, ell, delta_t+tau+k+o+a, beta)`

and

`mu=max(d_m, c, tau, beta+o, ell_m, a)`.

All resolution modules and differentials, syzygies, multidegrees, common states, Tor representatives, endpoint ancestry, rejected basis vectors, `B+sigma` rows, factor logs, and target candidates are charged. If source multigrading has one degree or basis vector per endpoint tuple, `tau`, `d_m`, or `o` becomes the full dense-incidence exponent. Bounded homological amplitude alone does not bound resolution ranks, basis count, output, `lambda`, or `mu`.

## Likely fatal obstruction

The derived tensor product is a generic way to represent intersection and excess multiplicity; it does not create missing endpoint labels. If multigrading is coarse, multiple forward and backward source tuples meeting at the same state contribute to the same Tor class, so only an aggregate intersection witness survives. If the grading is refined to exact factor-base endpoints, the free modules, basis degrees, or ancestry map explicitly contain the forward/backward incidence table. Resolution ranks and differentials then inherit the same dense state object seen in `P1477/P1478/P1428`, and source lifting can enumerate the Cartesian join. Thus the proposed operation changes the intersection backend but does not remove the recorded composition/output obstruction.

## Proof track

To reopen the record, construct implicit incidence modules and prove bounded resolution ranks, canonical multigraded Tor representatives, a biconditional exact endpoint inverse, and complete `lambda,mu<1/2` bounds through relation rank and blind descent. The proof must show where derived structure removes states that every classical backend must retain.

## Disproof track

Exhibit distinct endpoint tuples in one normalized Tor class, prove that exact multigrading requires one generator per incidence witness, or lower-bound a resolution rank, ancestry join, output, or memory exponent by `1/2`. Reduction to a generic resultant/GCD/sparse-solver backend with the same state object confirms the merge boundary.

## Positive and negative controls

- Transverse intersections where only `Tor_0` survives and endpoint sources are already explicit.
- Planted excess intersections with known bounded Tor amplitude and known many-to-one ancestry.
- Classical resultant, shared-union GCD, and forward/backward state-polynomial backends matched for input and output size.
- Source-erased grading versus a forbidden tuple-indexed multigrading that stores the complete incidence table.
- Exhaustive endpoint tuples on ordinary toy curves, including repeated states and nontransverse branches.
- Blind masked targets with complete candidate output, plus matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

Reopening requires a theorem proving canonical exact endpoint ancestry and symbolic `d_t,d_m,tau,o,lambda,mu<=0.45` without tuple-indexed generators. Any later toy preflight requires zero independently verified endpoint, sum, factor-log, or blind-descent errors, at least 1,000 independent rows, and 100 blind targets at each of two largest sizes; all upper 95% bounds must remain at most `0.45`. Falsify the scoped mechanism after one independently reproduced many-to-one Tor/source collision or a lower 95% bound of at least `0.50` for resolution rank, ancestry output, `lambda`, or `mu`. No run has been performed, so the present rejection is a semantic and cost-model merge, not an empirical performance claim.

## Artifact plan

- Merge/no-go proof: `ideas/artifacts/ECDLP-IDEA-088/derived_tor_merge_boundary.md`
- Frozen incidence-module specification: `ideas/artifacts/ECDLP-IDEA-088/incidence_modules.yaml`
- Prospective derived-intersection prototype: `ideas/artifacts/ECDLP-IDEA-088/derived_tor_atomizer.sage`
- Independent endpoint verifier: `ideas/artifacts/ECDLP-IDEA-088/verify_tor_ancestry.py`
- Prospective counterexample corpus: `ideas/artifacts/ECDLP-IDEA-088/counterexamples.jsonl`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-088/analysis.md`

## Interpretation boundary

This merged/rejected record is toy, heuristic, model-bound, and novelty-unverified. A bounded Tor amplitude, nonzero derived intersection, correct multiplicity, verified relation, or toy target descent would establish only scoped correctness. It would not establish source compression, a below-rho result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-088/derived_tor_merge_boundary.md` proving that coarse Tor grading loses endpoint ancestry while exact endpoint multigrading materializes the dense forward/backward incidence object.
