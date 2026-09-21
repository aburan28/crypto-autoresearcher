# ECDLP-IDEA-092 — Geometric Littlewood-Richardson source degeneration

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `merged_rejected`
- Evidence scale: `toy` geometric analogy only; no experiment or timing was run
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Schubert degeneration, multiplicity-one branch, or relation witness is not an ECDLP break.

## Falsifiable hypothesis

For each elliptic relation target `R`, a public source-preserving map sends the factor-base relation incidence scheme to an intersection of Schubert varieties. A geometric Littlewood-Richardson degeneration breaks that intersection into a multiplicity-free branch tree; each terminal branch has a certified inverse lift to one exact signed factor-base tuple. If the encoding, degeneration, source lift, relation collection, rank, blind descent, output, and memory are all sub-rho, the branch tree would be a representation-changing source enumerator.

## Mechanism-new operation

The proposed operation is **encode elliptic source incidence as a Schubert intersection, geometrically degenerate it into multiplicity-one components, and lift each terminal component to exact factor atoms**. Merely encoding a relation already found, enumerating a Littlewood-Richardson tree, changing an elimination order, or using multiplicity-free cycle classes as relation-only certificates is a duplicate/control. Survival requires a constructive source-biconditional incidence map whose formation does not itself enumerate the elliptic witnesses.

## Assumptions

1. `E(F_q)` contains a prime-order subgroup `<P>` of order `N`; the public factor base `F` has `B=N^(beta+o(1))` points.
2. A frozen, target-uniform rational map embeds the arity-`m` elliptic relation incidence scheme into a specified Grassmannian/flag incidence problem.
3. Scheme points and multiplicities are preserved: every terminal degeneration branch corresponds to exactly one signed factor-base tuple and every valid tuple occurs.
4. The geometric Littlewood-Richardson branch tree and its inverse source lift can be generated without materializing the original dense relation variety, all branches, or an equivalent source table.
5. Multiplicity one is accompanied by exact point identity and sign, not only a cycle-class coefficient or relation-validity certificate.
6. Encoding, degeneration, rejected branches, `B+sigma` rows, rank, factor logs, masked descent, source output, and memory are fully charged.

## Semantic fingerprint

`elliptic_relation_to_Schubert_intersection | geometric_LR_degeneration | multiplicity_free_branch_tree | certified_source_lift | masked_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate/addition-circuit barrier closest to the missing elliptic-to-incidence encoding.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1447`, where uncalibrated coordinate-energy diagnostics produce no relation or rank evidence.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1449`, the model/instrumentation negative whose dry cell contains zero relation, rank, or descent output.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the conditional five-term membership theorem requiring an implicit query backend below the stated exponent boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where one frozen five-term solver encoding fails its staged completeness and decision gates.

## Closest primary literature

- Vakil, [A geometric Littlewood-Richardson rule](https://arxiv.org/abs/math/0302294), degenerates Schubert intersections into multiplicity-one Schubert components; it does not encode elliptic relation sources or invert components to factor-base atoms.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the elliptic source-incidence system that the proposed Schubert map must construct and solve.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/3-540-69053-0_18), supplies the generic square-root boundary if the representation exposes no non-generic source information.

No checked source gives the required elliptic-incidence/Schubert biconditional or an output-sensitive source inverse. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F`, `B=N^beta`, relation arity, the target-uniform Schubert encoding, degeneration order, branch certificate, inverse source map, masks, and independent elliptic verifier.
2. For each known random `u`, form `R=[u]P`, build the Schubert intersection directly from public curve/factor-base data, execute the geometric degeneration, lift terminal branches to exact signed tuples in `F`, and verify each tuple sums to `R`.
3. Retain independently verified rows until at least `B+sigma` accepted relations exist; charge failed encodings, empty/excess branches, multiplicities, source collisions, duplicates, branch certificates, and complete source output.
4. Build the relation matrix over `Z/NZ`, satisfy the preregistered full-rank threshold, solve all factor logs, and independently verify `[log_P(F_i)]P=F_i` for every factor-base point.
5. For blind `Q=[x]P`, commit a random mask `r`, encode `T=Q+[r]P` with the identical frozen Schubert construction, degenerate, and source-lift without target-trained flags or branch selection.
6. Combine verified factor logs for an accepted tuple, unmask `x=(sum_i epsilon_i log_P(F_i))-r mod N`, enumerate only explicitly bounded sign ambiguity, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho has time exponent `1/2` and negligible-table memory, while BSGS has time and memory exponents `1/2`. Let `beta` be factor-base exponent, `s` Schubert-encoding/setup exponent, `c` degeneration branch-tree exponent, `k` terminal source-lift exponent, `delta,delta_t` reciprocal relation/descent density exponents, `o` source-output exponent, and `ell` rank/factor-log solving. Then `lambda=max(s,c,beta+delta+s+c+k+o,ell,delta_t+s+c+k+o,beta)`, and peak memory is `mu=max(beta,mu_encoding,mu_branch_tree,mu_source_lift,mu_linear_algebra,o)`. Every branch, multiplicity certificate, incidence chart, and lifted tuple is charged; a degeneration tree that enumerates all witnesses has its full output exponent.

## Likely fatal obstruction

The geometric Littlewood-Richardson rule starts with a Schubert intersection whose points are already defined. No source-preserving construction is known that maps the nonlinear elliptic factor-base relation scheme into that form more cheaply than describing or solving the original incidence. Multiplicity one is a statement about intersection-cycle components, not an identifier for the factor-base atoms inside a point. Building the missing map or traversing all terminal branches therefore enumerates the same witnesses, while a cycle-class identity without an inverse source map is only a relation certificate. The proposal merges with dense elimination, degeneration-order substitution, and source-reporter lanes.

## Proof track

Give explicit equations for a target-uniform elliptic-to-Schubert map, prove a scheme-theoretic bijection including signs and multiplicities, construct a terminal-branch-to-source inverse, and bound encoding, branch output, `B+sigma` relations, rank, logs, blind descent, and memory by `lambda,mu<1/2`.

## Disproof track

Show the encoding requires the original source tuple or a dense resultant; exhibit distinct elliptic tuples that land in one degeneration component; prove multiplicity-free cycle data omits point coordinates; or lower-bound branch/source output by the full relation-incidence size.

## Positive and negative controls

- Positive: published Schubert intersections with known multiplicity-free geometric Littlewood-Richardson trees.
- Positive: planted incidence maps whose terminal branches carry explicit source coordinates.
- Negative: matched Schubert intersections with identical Littlewood-Richardson coefficients but permuted point labels.
- Negative: complete tiny elliptic relation schemes compared against exhaustive signed source tuples.
- Negative: dense resultant and direct Semaev enumeration baselines with identical source-output charging.
- Negative: masked blind targets with frozen flags and no post-hoc branch selector.

## Quantitative promotion and falsification gates

The theorem gate requires an explicit source-bijective encoding, zero branch/source mismatches on exhaustive toy schemes, and symbolic `s,c,k,o,lambda,mu<0.50`. Any future empirical promotion requires at least `B+sigma` accepted rows at every preregistered size, full rank, every factor log verified, at least 100 independent masked descents, and upper 95% bounds `lambda<=0.45` and `mu<=0.45`. Falsify this mechanism if the map consumes a source witness, any terminal branch lacks a unique signed lift, or a proved lower bound or lower 95% scaling bound gives `max(s,c,k,o,lambda,mu)>=0.50`.

## Artifact plan

- Encoding no-go: `ideas/artifacts/ECDLP-IDEA-092/geometric_lr_source_no_go.md`
- Incidence schema: `ideas/artifacts/ECDLP-IDEA-092/schubert_encoding_schema.yaml`
- Source verifier design: `ideas/artifacts/ECDLP-IDEA-092/verify_lr_sources.py`
- Cost worksheet: `ideas/artifacts/ECDLP-IDEA-092/cost_model.json`
- Future runs, if separately approved: `ideas/artifacts/ECDLP-IDEA-092/runs/<run-id>/`

## Interpretation boundary

This merged rejection is toy, heuristic, model-bound, and novelty-unverified. It is an analytic semantic boundary, not an experimental result and not a rejection of geometric degeneration in general. A correct Littlewood-Richardson tree, multiplicity-one component, or valid elliptic relation is not exact factor-source recovery, full-rank logs, blind descent, a better-than-rho result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-092/geometric_lr_source_no_go.md` formalizing that geometric Littlewood-Richardson degeneration presupposes the source incidence and that multiplicity-one cycle components do not by themselves identify factor atoms.
