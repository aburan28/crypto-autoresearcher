# ECDLP-IDEA-100 — Hopf-Galois normal-basis source split

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_dimension_source_no_go`
- Top lane: `-`
- Evidence scale: semantic/theorem screen only; no run; any future algebra example would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid Hopf-Galois structure, normal basis, projector, relation, or toy descent is not an ECDLP break.

## Falsifiable hypothesis

Let `A_R` be the finite separable algebra of roots or endpoint branches of an elliptic factor-base relation fiber. Even when its normal closure has large monodromy, `A_R` admits a target-independent nonclassical Hopf-Galois structure associated with a regular subgroup normalized by that monodromy. A Hopf normal basis and a compact set of Hopf actions split `A_R` into source-labelled coordinates without constructing the full splitting field or enumerating its roots. Those coordinates invert exactly to signed factor-base tuples and support `B+sigma` rows, factor-log calibration, and blind descent with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **replace ordinary Galois root permutation by a nonclassical Hopf-Galois action, compute a Hopf normal basis, and use Hopf projectors to recover exact source branches**. The candidate seeks a new algebraic representation of the full separable algebra rather than another solver for the same polynomial. A normal-basis change, ordinary group algebra, coproduct with no source inverse, or projectors defined after roots are known is a control.

The record is rejected because the proposed Hopf-Galois step starts only after the relation algebra `A_R` has been constructed and supplies no new target-side query that finds an accepted relation branch more cheaply. It is therefore a representation/backend substitution for the occupied relation-root algebra unless a successor proves an end-to-end relation-query improvement and an exact source inverse. A Hopf-Galois structure on a degree-`d` extension does have Hopf-algebra dimension `d`, but dimension alone is **not** asserted to be a runtime or memory lower bound: succinct actions or queries may exist. The charged obstruction is that this proposal gives no such query, while any materialized normal basis, action tensor, or source-projector dictionary must be accounted at its actual size and output cost.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; a target-independent factor base `F` has `B=N^beta` and fixed relation arity/split.
2. Every relevant relation/endpoint fiber has a finite separable algebra `A_R` with all signs, multiplicities, repeated sources, and exceptional fibers explicitly handled.
3. Its normal-closure group normalizes a target-independent regular subgroup defining a Hopf-Galois structure over the public base field for a positive-density set of relation and target fibers.
4. The corresponding Hopf algebra, normal basis, and source projectors are computable implicitly without constructing all embeddings, using factor logs, or receiving source-labelled advice.
5. Projector outputs invert biconditionally to exact factor-base indices, signs, and multiplicities rather than only subfields, orbit sums, or representation types.
6. Structure discovery, Hopf algebra arithmetic, basis conversion, all projector outputs, field extensions, failures, `B+sigma` rows, rank, factor logs, blind descent, ambiguity, verification, and peak memory are fully charged.

## Semantic fingerprint

`relation_root_separable_algebra | normalized_regular_subgroup | nonclassical_Hopf_Galois_action | Hopf_normal_basis_projectors | exact_source_split`

The removal test requires a Hopf operation that improves the complete target-to-relation query and then inverts its output to sources. Merely proving that a Hopf-Galois structure exists after constructing `A_R`, or rewriting the same coordinates in a normal basis, is a representation/backend substitution even if the action itself has a succinct description.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-030`, where an exact cyclic cover/deck/Prym algebra gives only scalar or zero action on the visible elliptic factor.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-044`, where ordinary closed-point smoothness on an auxiliary cover gives no hidden factor-base advantage.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier that an alternative algebra action must actually remove.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where a compact exact one-transition algebra composes to a dense quadratic resultant.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where aggregate norm information remains source-incomplete.

## Closest primary literature

- Greither and Pareigis, [Hopf Galois theory for separable field extensions](https://doi.org/10.1016/0021-8693%2887%2990029-9), characterizes Hopf-Galois structures through regular subgroups normalized by the Galois action; the associated Hopf algebra still has the extension degree.
- Crespo and Salguero, [Hopf Galois structures on separable field extensions of odd prime power degree](https://arxiv.org/abs/1807.11409), classifies possible structures in restricted degree families; it does not give sublinear root/source projectors.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring relation algebras without a Hopf-Galois source split.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic square-root comparison boundary.

No checked primary source uses a Hopf-Galois normal basis to compress exact factor-base ancestry in elliptic relation fibers. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the relation-root algebra presentation, normal-closure action, regular subgroup selection, Hopf algebra, normal-basis normalization, projector set, source inverse, and exceptional-fiber policy.
2. For a public output `R`, construct and verify the finite separable algebra and its Hopf-Galois structure without splitting all roots or enumerating source tuples.
3. Compute every accepted Hopf projector coordinate, invert it to exact signed members of `F`, and independently verify that each reconstructed tuple sums to `R`.
4. Apply the frozen construction to known outputs `R_j=[r_j]P`; retain verified rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` rows have rank `B`.
5. Solve all factor-base logarithms and independently verify `[log_P(F_i)]P=F_i` for every point.
6. Choose fresh masks `t`, form `R_t=Q+[t]P`, and apply the identical Hopf algebra, basis, projectors, source inverse, and exact sum verification.
7. Substitute verified factor logs, subtract `t mod N`, retain the complete candidate/ambiguity list, and accept only `x` satisfying `[x]P=Q`.
8. Preserve fibers with no structure, nonseparable cases, alternate regular subgroups, projector collisions, failed inverses, and all intermediate dimensions.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` with constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; relation-algebra degree be `d=N^eta`; target-independent family/Hopf-structure setup time and memory be `N^a,N^am`; the actually used basis/action representation and resident query state be `N^h`; relation and target success probabilities be `N^-delta,N^-delta_t`; complete per-returned-branch work—including target-dependent relation-algebra construction, action, projector, and inverse—be `N^k`; emitted source/projector output and target ambiguity counts be `N^o,N^u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,h,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(am,h,beta+o,ell_m,u)`.

The complete per-target relation-algebra construction and every actually materialized part of the `d`-dimensional Hopf algebra, multiplication/comultiplication/action tensors, regular-subgroup data, basis conversion, field coefficients, failed fibers, projector coordinates, `B+sigma` rows, source tuples, and candidates are charged in `a`, `am`, `h`, `k`, or `o`. If a full degree-`d` object is materialized, the corresponding charged exponent is at least `eta`; the bare equality `dim(H)=d` does not by itself force `lambda` or `mu` to contain `eta`. Succinct generators are allowed, but their complete relation-query and source-output costs remain charged. Promotion would require both `lambda<1/2` and `mu<1/2`.

## Likely fatal obstruction

Hopf-Galois theory is applied here only after a target's separable relation algebra has already been obtained. The proposal contains no new operation that queries the target for an accepted branch before that expensive algebraic stage, so it does not improve the occupied relation-generation path. The regular subgroup has order `d`, the Hopf algebra has dimension `d`, and a normal basis spans the same algebra, but those facts alone are not runtime lower bounds. The concrete danger is instead that source-separating projectors materialize a full basis/action or emit the complete source dictionary, whereas succinct coarse actions yield only intermediate-field/orbit information and leave distinct factor-base tuples indistinguishable. Structure discovery may also require the normal closure or full embedding action, and every such realized cost must be charged rather than inferred from dimension alone.

## Proof track

Construct a positive-density relation family with an explicit normalized regular subgroup, give a target-side Hopf query that obtains accepted relation branches without first materializing the occupied relation algebra/root set, prove that its outputs invert biconditionally to exact source tuples, and bound complete relation construction, structure discovery, relation collection, rank, factor-log calibration, blind descent, output, and memory by `lambda,mu<1/2`.

## Disproof track

Show that the Hopf step begins only after constructing the same relation algebra/root data as the baseline and supplies no cheaper target query; exhibit distinct source roots with identical proposed coarse Hopf invariants; show that the concrete source-separating action materializes or emits the full branch dictionary; or show discovering the regular subgroup requires the full embedding action. Any source-indexed primitive idempotent table or factor-log-labelled normal basis also disproves the mechanism. The abstract dimension `d` alone is not a disproof.

## Positive and negative controls

- Published low-degree separable extensions with classical and nonclassical Hopf-Galois structures.
- Planted regular-subgroup examples with an independently known Hopf normal basis and complete root labels.
- Ordinary Galois/group-algebra normal bases matched for dimension and arithmetic work.
- Coarse Hopf subalgebra/orbit invariants versus a forbidden primitive-projector table containing all roots.
- Exhaustive ordinary toy-curve relation algebras, including reducible and inseparable exceptional fibers.
- Blind masked targets under a frozen structure, plus matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

No active promotion gate remains. A versioned successor must prove a target-side relation query absent from the baseline, a source-separating representation/query-state exponent at most `0.30`, an exact source biconditional, and symbolic `a,am,h,o,u,lambda,mu<=0.45` without primitive source tables. Any later toy preflight would require zero independently verified structure/projector/source/sum/factor-log/descent errors over 20 curves at each of four increasing sizes, at least 1,000 independent rows, and 100 blind descents at each of the two largest sizes. Falsify upon one reproduced coarse-invariant/source collision, proof that the Hopf arm first constructs the occupied relation algebra and offers no end-to-end query improvement, or a lower 95% bound `>=0.50` for structure state, projector output, complete time, or memory.

## Artifact plan

- End-to-end source-query audit: `ideas/artifacts/ECDLP-IDEA-100/hopf_dimension_source_no_go.md`
- Frozen algebra/action specification: `ideas/artifacts/ECDLP-IDEA-100/hopf_galois_spec.yaml`
- Prospective structure prototype: `ideas/artifacts/ECDLP-IDEA-100/hopf_source_split.sage`
- Independent projector/source verifier: `ideas/artifacts/ECDLP-IDEA-100/verify_hopf_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-100/analysis.md`
- Any future receipts: `ideas/artifacts/ECDLP-IDEA-100/runs/<run-id>/`

## Interpretation boundary

This rejected representation-changing record is toy, heuristic, model-bound, and novelty-unverified. The rejection is a scoped end-to-end semantic merge: the Hopf-Galois arm starts after relation-algebra construction and proves no cheaper source query. It is not a theorem that degree or Hopf-algebra dimension alone lower-bounds runtime. A valid regular subgroup, Hopf algebra, normal basis, projector, relation, or toy scalar is not evidence of source compression, a below-rho result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-100/hopf_dimension_source_no_go.md` comparing the complete baseline and Hopf target-to-source query paths and proving either a charged end-to-end improvement or the representation-only semantic merge, without treating dimension `d` alone as a runtime lower bound.
