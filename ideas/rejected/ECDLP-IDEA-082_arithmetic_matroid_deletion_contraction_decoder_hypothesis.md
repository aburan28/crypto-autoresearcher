# ECDLP-IDEA-082 — Arithmetic-matroid deletion–contraction decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `rejected_rank_one_collapse`
- Evidence scale: `toy` matroid identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a circuit or multiplicity computation is not an ECDLP break.

## Falsifiable hypothesis

Attach an arithmetic matroid to factor-base atoms and partial elliptic relations. A target-aware deletion–contraction recursion isolates a target-containing circuit, and arithmetic multiplicities recover its coefficients and exact source points with a sub-rho recursion tree; repeated relation collection and blind descent then solve the target.

## Mechanism-new operation

The proposed operation is **arithmetic-matroid deletion–contraction with multiplicity-guided exact circuit/source recovery**. It is rejected as written: a finite cyclic ambient group has free arithmetic-matroid rank zero, while linearizing over `F_N` produces a rank-one vector matroid; neither public structure supplies scalar orientation. A generic rank oracle or relation-only circuit is an occupied control.

## Assumptions

1. A scalar-blind arithmetic-matroid representation is publicly computable from points.
2. Its circuits are exactly elliptic relations with recoverable coefficients.
3. Multiplicities distinguish target-containing circuits without factor logs.
4. Deletion–contraction prunes to fewer than `N^(1/2)` states.
5. Exact point sources, rank, factor-log solving, descent, and memory are charged.
6. No oracle uses hidden scalar coordinates.

## Semantic fingerprint

`factor_atom_arithmetic_matroid | target_deletion_contraction | multiplicity_guided_circuit | exact_source_coefficients | relation_rank_and_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H396`, the closest nonlinear relation-constraint lane.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H397`, the quotient/module invariant control.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H638`, the pre-candidate certificate boundary.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H629`, the source-split signal lane.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where public feature spaces do not contain factor logs.

## Closest primary literature

- D'Adderio and Moci, [Arithmetic matroids, the Tutte polynomial and toric arrangements](https://doi.org/10.1016/j.aim.2012.09.001), develops arithmetic multiplicities but no elliptic scalar orientation.
- Diaconis and Sturmfels, [Algebraic algorithms for sampling from conditional distributions](https://doi.org/10.1214/aos/1030563990), is the nearby combinatorial-fiber framework.
- Shoup, [Lower bounds for discrete logarithms](https://doi.org/10.1007/3-540-69053-0_18), supplies the generic representation boundary.

## Complete factor-base-to-target-descent path

1. Freeze the ground set, rank/multiplicity oracles, target extension, deletion order, factor base, and exhaustive relations.
2. Prove every matroid circuit maps bijectively to an exact elliptic relation.
3. Run deletion–contraction, recover coefficients/sources, and verify every relation.
4. Collect full rank, solve and verify factor logs.
5. Add masked targets, isolate circuits, unmask the resulting scalar, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho and BSGS have time exponent `1/2`; BSGS memory exponent is `1/2`. Let representation setup `s`, oracle `k`, recursion-tree exponent `r`, factor-base exponent `beta`, inverse circuit/target densities `delta,delta_t`, output `o`, linear algebra `ell`, and memory `mu`. Then `lambda=max(s,r+k,beta+delta+r+k+o,ell,delta_t+r+k+o)`. Scalar-labelled ranks or multiplicities are costed as a DLP oracle.

## Likely fatal obstruction

In the finitely generated abelian-group definition, the finite cyclic subgroup has free rank zero; after scalar linearization over `F_N`, all nonzero points span the same rank-one space. Both underlying matroids are degenerate for this purpose, while nontrivial arithmetic multiplicities require determinants or indices in hidden scalar coordinates. Public point equality/addition can verify a proposed circuit but does not supply its coefficients or pruning oracle. The recursion therefore branches over subsets or hides DLP labels.

## Proof track

Construct a scalar-blind higher-rank representation whose arithmetic circuits retain exact points, and prove sub-rho recursion and full descent.

## Disproof track

Prove rank-one collapse, show multiplicity evaluation requires factor logs, or establish recursion/output exponent at least `1/2`.

## Positive and negative controls

- Integer vector configurations with known arithmetic matroids.
- Planted higher-rank modules and their deletion–contraction trees.
- Prime cyclic subgroup ground sets.
- Scalar-labelled forbidden oracle versus public group operations.
- Exhaustive true circuit verification.
- Blind target insertions.

## Quantitative promotion and falsification gates

The necessary gate is a scalar-blind nontrivial rank/multiplicity oracle on complete toy instances. Promotion would require zero circuit/source errors and upper 95% `lambda,mu<=0.45`. The candidate is rejected because the stated ground set collapses to rank one and nontrivial multiplicities require the missing orientation.

## Artifact plan

- No-go: `ideas/artifacts/ECDLP-IDEA-082/rank_one_matroid_no_go.md`
- Prototype: `ideas/artifacts/ECDLP-IDEA-082/deletion_contraction.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-082/verify_circuits.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-082/analysis.md`

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. It closes only the stated scalar-blind arithmetic-matroid representation.

## Exactly one next executable action

1. Formalize `ideas/artifacts/ECDLP-IDEA-082/rank_one_matroid_no_go.md` by computing every public rank and arithmetic-multiplicity candidate on exhaustive prime cyclic groups.
