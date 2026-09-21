# ECDLP-IDEA-113 — Lattes arboreal digit descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `rejected_branch_tree_no_go`
- Top lane: `-`
- Evidence scale: semantic/theorem screen only; no run; any future tree check would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Lattes diagram, arboreal action, recovered branch, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For a fixed small integer `d`, quotient multiplication by `[d]` on an ordinary prime-field elliptic curve to a public Lattes map `phi_d` on `P^1`. The inverse tree of `phi_d`, together with Frobenius/arboreal labels, is hypothesized to admit a target-independent quotient with fewer than `N^(1/2)` states that retains a biconditional branch word for every signed factor-base source tuple. Exact branch unranking would then produce full-rank relation rows and blind target descents with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **quotient the iterated Lattes preimage tree by its arboreal Galois action while retaining an exact branch-word inverse to elliptic sources**. The claimed gain is not another rational map, ladder, preimage DAG, or same-field isogeny: it requires a lossless orbit quotient whose state count is genuinely smaller than the number of scalar branches and whose labels can be computed from a public output without first choosing its hidden branch.

The scoped formulation is rejected. At depth `h`, `[d]^h` has `d^(2h)` geometric preimages. Quotienting by sign or Galois orbits removes only public symmetries; recovering the branch corresponding to an arbitrary factor-base point restores the missing orientation. If the quotient is source-faithful, its states or backpointers have the full branch exponent. If it is smaller, distinct sources collide and exact descent fails.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; a deterministic target-independent factor base `F` has `B=N^beta`, and relation arity `m` is frozen.
2. A public quotient `pi:E->{P^1}` and degree-`d^2` Lattes map satisfy `pi([d]R)=phi_d(pi(R))` on complete charts, including signs, poles, ramification, and points at infinity.
3. A target-independent finite arboreal state quotient can be built without enumerating the `d^(2h)` preimage tree, using factor logarithms, or seeing the target scalar.
4. Every accepted quotient state has a public exact inverse to all signed factor-base indices and multiplicities represented by that state.
5. Known-output relation collection and a masked target use the identical tree depth, orbit quotient, branch rule, ambiguity policy, and verification path.
6. Tree construction, extension fields, ramification, orbit enumeration, source output, failed branches, `B+sigma` rows, rank, factor logs, blind descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`Lattes_multiplication_quotient | arboreal_Galois_preimage_tree | lossless_orbit_state_quotient | exact_branch_source_unranking | blind_descent`

The removal test is a proved sub-rho source-faithful quotient of the inverse tree. A rational-map parameter change, explicit preimage table, post-hoc branch selector, same-field isogeny, or ordinary meet-in-the-middle ladder is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1408-PREIMAGE-DAG`, the nearest exact recursive-preimage DAG whose shared evaluations did not yet compress source edges.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the direct lossless-ancestry boundary that canonical witness edges remain uncompressed.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H650`, the closest fused preimage/factor-base/four-sum DAG hypothesis and its restricted cost theorem.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, whose forward/backward transition representation becomes dense when exact endpoint ancestry is retained.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact sparse one-transition identity becomes a dense two-transition composition.

## Closest primary literature

- Milnor, [On Lattes maps](https://arxiv.org/abs/math/0402147), develops the quotient dynamics arising from affine maps on elliptic curves; it does not give a compact source-faithful inverse tree for ECDLP.
- Boston and Jones, [Arboreal Galois representations](https://doi.org/10.1007/s10711-006-9113-9), study Galois actions on iterated preimages; they do not provide target-computable branch orientation or source unranking.
- Leung, [Arboreal Galois groups of rational maps with nonreal Julia sets](https://arxiv.org/abs/2412.03313), proves nonabelian arboreal results for classes including Lattès maps associated to duplication; it does not provide a compressed source decoder.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic square-root comparison boundary.

No checked primary source gives an arboreal quotient that both compresses and exactly orients arbitrary prime-field elliptic source branches. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m,d,h`, the Lattes charts, ramification conventions, arboreal quotient, state ordering, branch inverse, and ambiguity budget before observing outcomes.
2. Construct the quotient inverse-tree state object without a source table; independently verify the complete commutative Lattes diagram on every retained chart.
3. For a public output `R`, query its quotient state, unrank every represented branch to exact signed members of `F`, and verify each elliptic sum equals `R`.
4. Apply the frozen procedure to known outputs `R_j=[r_j]P`; retain verified rows until exactly `B+sigma` rows have coefficient rank `B` modulo `N`.
5. Solve all factor-base logarithms and independently verify `[log_P(F_i)]P=F_i` for every factor-base point.
6. Choose fresh masks `t`, form `R_t=Q+[t]P`, and run the identical tree query, orbit quotient, branch unranking, membership checks, and elliptic-sum verification.
7. Substitute verified factor logs, subtract `t`, retain every branch ambiguity candidate, and accept only `x` satisfying `[x]P=Q`.
8. Preserve ramified fibers, missing branches, collisions, extension degrees, duplicate rows, rejected candidates, and complete serialized and working state.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` and constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; Lattes/tree plus factor-base construction time and memory be `N^a,N^a_m`; quotient-state size and working state be `N^s,N^s_m`; reciprocal relation and target success probabilities be `N^delta,N^delta_t`; complete per-query orbit/branch/source enumeration plus exact elliptic verification work be `N^k`; returned source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,s,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(a_m,s_m,beta+o,ell_m,u)`.

All preimage polynomials, orbit representatives, extension elements, branch backpointers, failed queries, `B+sigma` rows, outputs, and verification enter these exponents. A `d^(2h)` or `N^(1/2)` frontier in any complete term is not a speedup.

## Likely fatal obstruction

The Lattes quotient forgets precisely the elliptic translation orientation needed to distinguish preimage branches. Arboreal symmetry can compress a set of conjugate branches only while they remain indistinguishable. Exact source recovery breaks that symmetry and requires a branch representative or backpointer per relevant source. At the depth needed to resolve an `N`-scale scalar, the faithful tree has `N^(1-o(1))` leaves; stopping near half depth reproduces a BSGS-sized frontier rather than beating it.

## Proof track

Construct a target-independent arboreal quotient, prove a biconditional quotient-state-to-source inverse on all accepted fibers, and prove symbolic bounds `a,a_m,s,s_m,k,o,u,lambda,mu<=0.45` through relation rank, factor logs, and blind descent.

## Disproof track

Exhibit two distinct accepted sources with the same quotient state, prove that any exact inverse needs one state/backpointer per branch orbit, or lower-bound tree/query/output time or memory by `N^(1/2)`. A target-scalar-selected branch or explicit preimage table also disproves the mechanism.

## Positive and negative controls

- Published postcritically finite Lattes maps with explicitly known small preimage trees.
- Planted shallow trees whose source branches and Galois orbits are independently labelled.
- The same trees after dropping orientation, which must exhibit source collisions.
- ECFG-P1408's lossless preimage DAG and a matched meet-in-the-middle scalar ladder.
- Exhaustive ordinary toy curves including ramified, sign, infinity, and extension-field branches.
- Blind masked targets with matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

This rejected formulation has no active promotion gate. A versioned successor must first prove a source-faithful quotient with `a,a_m,s,s_m,k,o,u,lambda,mu<=0.45` and no branch table. A later toy preflight would require zero source/sum/factor-log/descent errors on 20 curves at four increasing sizes, 1,000 independent rows and 100 blind descents at each of the two largest sizes. Falsify after one reproduced source collision or a lower 95% bound `>=0.50` for tree state, query, output, complete time, or memory.

## Artifact plan

- Arboreal branch lower-bound receipt: `ideas/artifacts/ECDLP-IDEA-113/arboreal_branch_no_go.md`
- Frozen Lattes/tree specification: `ideas/artifacts/ECDLP-IDEA-113/lattes_tree_spec.yaml`
- Prospective toy tree enumerator: `ideas/artifacts/ECDLP-IDEA-113/lattes_tree.sage`
- Independent branch/source verifier: `ideas/artifacts/ECDLP-IDEA-113/verify_arboreal_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-113/analysis.md`

## Interpretation boundary

This rejected proposal is toy, heuristic, model-bound, and novelty-unverified. The branch-state argument is scoped to a source-faithful Lattes inverse-tree quotient, not a generic ECDLP lower bound. A correct diagram, small shallow tree, relation, or toy scalar is not evidence of a below-rho algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-113/arboreal_branch_no_go.md` proving or refuting that every target-independent source-faithful arboreal quotient needs one distinguishable state or backpointer per accepted Lattes branch orbit.
