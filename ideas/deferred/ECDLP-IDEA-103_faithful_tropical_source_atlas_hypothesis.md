# ECDLP-IDEA-103 — Faithful tropical source atlas

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `deferred_theorem_required`
- Evidence scale: no run; any future atlas preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a faithful tropicalization, correct source lift, valid
  relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Let `E(F_p)` contain a public prime-order subgroup `<P>` of order
`N=p^(1+o(1))`, let `F` be a target-independent factor base of size
`B=N^beta`, and freeze a finite set `Sigma` of sign patterns. Define the
positive-dimensional universal addition family
`s: Z=disjoint_union_(epsilon in Sigma) E^m -> E` by
`s(epsilon,X_1,...,X_m)=sum_i epsilon_i X_i`. Its geometric fiber `Z_R` has
dimension `m-1`; the accepted factor-base witnesses form only the finite discrete subset
`A_R={(epsilon,X_1,...,X_m) in Z_R(F_p): X_i in F}`. The hypothesis is that a
target-independent finite family of toric embeddings of the relevant analytic family
jointly separates every point of every `A_R`, and that a bounded tropical cell/residue
word has a public exact inverse to the signed source tuple. Metric or skeletal
faithfulness on the positive-dimensional analytic space does not imply this discrete
source injectivity. If the atlas, inverse, relation collection, factor-log linear
algebra, and blind target descent all have time and peak-memory exponents below `1/2`,
the representation would provide a complete below-rho ECDLP path.

## Mechanism-new operation

The operation is **jointly tropicalize the universal marked addition correspondence in a
finite source-faithful atlas, then invert a target cell word to exact factor-base
sources**. It is not a Newton-polytope score, a toric degeneration, a cluster chamber, a
same-field isogeny, or a tropical label attached after recovering a relation. Those are
controls. Payne's inverse-limit theorem and faithful tropicalization of finite skeletal
subgraphs motivate the representation, but do not supply the required finite uniform
atlas or inverse. This record is deferred until both are proved with sub-rho size bounds.

## Assumptions

1. `E,P,N`, fixed arity `m`, and a sign-canonical factor base
   `F={F_1,...,F_B}` with `B=N^beta` are public.
2. The analytic object being tropicalized is the positive-dimensional family `Z -> E`
   above, or a separately specified proper compactification with the same accepted
   discrete subsets `A_R`; all embeddings, valuations, overlap maps, and exceptional
   branches are target-independent and defined over a field where exact finite-field
   source recovery is meaningful.
3. Joint tropical coordinates separate every point of each finite subset `A_R`, not
   merely points of a chosen skeleton, branch metrics, divisor classes, multiplicities,
   or target sums. No faithful-skeleton theorem is treated as proving this condition.
4. A public inverse returns all source indices, signs, and multiplicities without hidden
   factor logs, target-specific advice, or enumeration of `F^m`.
5. Atlas construction, coordinate height, field extensions, overlaps, cell traversal,
   source output, misses, rank, factor logs, descent, verification, and memory are charged.
6. Any finite-size exponent extrapolation remains toy, heuristic, model-bound, and
   novelty-unverified.

## Semantic fingerprint

`universal_marked_addition_fiber | finite_joint_tropicalization | source_faithful_skeleton_atlas | bounded_cell_word | exact_point_source_inverse | blind_descent`

The required new operation is the exact source inverse. An atlas that is faithful only as
a topological or metric embedding, or that needs one chart per source tuple, is a no-go.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-044`, where ordinary
   cover-divisor smoothness is inherited and supplies no hidden source advantage.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate
   barrier that a finite tropical atlas must genuinely remove.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1449`, the nearest frozen
   coordinate-expansion matrix and model boundary.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1474`, where a compact orbit
   representation fails without an invariant source-functional deck.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, whose exact compact transition
   identity still lacks a source-resolving composition operation.

## Closest primary literature

- Payne, [Analytification is the limit of all tropicalizations](https://arxiv.org/abs/0805.1916),
  proves that a quasiprojective analytification is recovered as the inverse limit of all
  tropicalizations; it does not give the bounded finite source atlas required here.
- Baker, Payne, and Rabinoff,
  [Nonarchimedean geometry, tropicalization, and metrics on curves](https://arxiv.org/abs/1104.0320),
  show that tropicalizations can stabilize isometrically on finite subgraphs of curve
  analytifications; metric faithfulness is not an inverse to factor-base source tuples.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the comparison addition fibers and factor-base decomposition obligation.

No checked source proves a finite target-uniform tropical atlas with exact point-source
inversion and sub-rho construction. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the universal marked addition fiber, compactification, valuation
   field, finite embedding family, overlap rules, sign convention, and exhaustive tiny
   source truth.
2. Construct and independently verify the joint tropical atlas, including all boundary,
   tangent, repeated-point, and chart-overlap cases, without indexing charts by source
   tuples.
3. For known random outputs `R_j=[r_j]P`, compute the target cell data, enumerate only the
   branches allowed by the bounded atlas, invert each cell word to exact points in `F`,
   and independently verify their signed elliptic sum.
4. Preserve misses, ambiguous inverses, duplicate tuples, overlap multiplicities, and
   rejected branches; collect exactly `B+sigma` verified rows whose coefficient matrix
   has rank `B` modulo `N`.
5. Solve every factor-base logarithm and independently verify
   `[log_P(F_i)]P=F_i` for all `i`.
6. Freeze the atlas and query masked blind targets `Q+[t]P` with fresh public masks `t`;
   apply the identical cell traversal and exact source inverse.
7. Substitute verified factor logs, subtract each mask, retain the full ambiguity set,
   and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` group operations with constant-state memory; BSGS has
time and memory exponents `1/2`. Let `B=N^beta`. Let target-independent atlas setup take
`N^(a+o(1))` time and `N^(a_m+o(1))` peak memory. Let complete chart enumeration,
incidence construction, and overlap indexing produce `N^(g+o(1))` chart/overlap records,
each with at most `N^(h+o(1))` encoded embedding coefficients, valued-extension words,
valuation-precision words, and boundary data. Thus the unshared chart/height payload has
time and storage exponent `g+h`; a shared encoding may replace `g+h` only by its measured
total decode-inclusive exponent. Let one complete tropical evaluation, overlap traversal,
and exact source inversion attempt, excluding written output, take `N^(q+o(1))` time and
`N^(q_m+o(1))` working memory. Let exact source tuples emitted per accepted fiber have
exponent `o`, and let residual scalar ambiguity per emitted target source have exponent
`u`; writing these lists costs their full time and storage. Let reciprocal usable-relation
and target success probabilities be `N^delta` and `N^delta_t`. Let factor-log linear
algebra take `N^(ell+o(1))` time and `N^(ell_m+o(1))` memory, with `ell>=2beta` absent
proved structure. Finally, let verification of one emitted source tuple or scalar
candidate take `N^(v+o(1))` time and `N^(v_m+o(1))` working memory.

The fully charged time exponent is

`lambda=max(a,g+h,beta+delta+q+o+v,ell,delta_t+q+o+u+v)`,

and the complete peak-memory exponent is

`mu=max(a_m,g+h,q_m,ell_m,beta+o,o+u,v_m)`.

These are upper bounds for the complete relation-collection, factor-log, and blind-target
path. Every embedding coefficient, valued extension, chart, overlap, failed target,
ambiguous inverse, emitted source, candidate, and verifier operation is charged. An
inverse-limit statement using an unbounded embedding family or an explicit source-indexed
atlas has its complete time and storage charged and cannot beat rho.

## Likely fatal obstruction

Faithful tropicalization theorems preserve an analytification or a chosen finite skeleton,
not the labels of all points in a growing finite factor base. Distinct algebraic source
tuples can share the same valuation vector and target cell. Separating them may require
additional embeddings until the atlas or coefficient height is comparable to the full
`B^m` incidence object. Inverting a tropical point to its residue-field sources can also
be exactly the original polynomial-membership problem.

## Proof track

Construct a finite family of embeddings independent of `R`; prove joint injectivity on all
factor-base source branches, an exact residue/source inverse, and bounds
`a,h,q+o,mu<1/2`. Then prove that the seven-step relation, rank, factor-log, and blind
descent path succeeds without source-indexed advice.

## Disproof track

Exhibit two distinct signed source tuples with identical joint tropical data, prove that
separating the growing factor base requires `N^(1/2-o(1))` charts or height, show that
residue lifting reconstructs the occupied membership solve, or derive
`lambda>=1/2` after density and source output are charged.

## Positive and negative controls

- Positive control: published faithful tropicalizations of a fixed finite skeleton with
  independently verified metric preservation.
- Positive source control: planted toric curves whose valuation cells have a known exact
  residue/source inverse.
- Negative control: random source tuples with matched valuation marginals and deliberate
  tropical collisions.
- Mechanism controls: a single Newton polytope, the cluster-scattering IDEA-076 atlas,
  the stable-log-map IDEA-087 degeneration, and explicit source-indexed charts.
- Leakage control: permute factor-base labels while preserving all tropical coordinates.
- Baseline control: matched Pollard-rho and memory-matched BSGS accounting.

## Quantitative promotion and falsification gates

No run is admissible before a theorem proves finite target-uniform joint injectivity, an
exact source inverse on every chart, and symbolic `lambda,mu<=0.45`. A future toy preflight
would use at least 20 ordinary curves at each of four increasing sizes, exhaustive truth
through 18 bits, at least `1,000` independent verified rows and `100` blind descents at
each of the two largest sizes, zero source or overlap errors, fresh rank at least `0.8B`,
and upper 95% bounds `lambda,mu<=0.45` under the complete upper-bound formulas above.
Falsify as written on one reproducible
source collision, target-dependent chart choice, or lower 95% bound at least `0.50` for
atlas size, inversion, complete time, or peak memory.

## Artifact plan

- Theorem gate: `ideas/artifacts/ECDLP-IDEA-103/finite_atlas_source_inverse.md`
- Atlas specification: `ideas/artifacts/ECDLP-IDEA-103/tropical_atlas.yaml`
- Prospective constructor: `ideas/artifacts/ECDLP-IDEA-103/build_atlas.sage`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-103/verify_sources.py`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-103/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-103/analysis.md`

## Interpretation boundary

This deferred record is toy, heuristic, model-bound, and novelty-unverified. A correct
tropicalization, isometric skeleton, cell count, exact relation, or recovered toy scalar
is not evidence of a below-rho algorithm or a breakthrough. Only a source-faithful finite
atlas with complete factor-log and blind-descent accounting could reopen the lane.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-103/finite_atlas_source_inverse.md` proving either a finite target-uniform tropical source atlas with an exact residue/source inverse and symbolic sub-rho bounds, or an explicit source-collision obstruction.
