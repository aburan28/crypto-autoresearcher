# ECDLP-IDEA-093 — Multiplicative-preprojective reflection descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `merged_rejected`
- Evidence scale: `toy` symbolic-representation preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: the multiplicative moment map is an aggregate relation
  constraint; a source-labelled quiver representation already contains the atoms it is
  supposed to recover, so the proposal merges with the occupied Hall/Hecke source path.
- Breakthrough claim: **none**; a valid quiver representation, reflection identity, or
  verified elliptic relation is not an ECDLP break.

## Falsifiable hypothesis

For a target-independent factor base `F` on a generic ordinary prime-field curve, source
points can be encoded as simple factors of a star-quiver representation satisfying a
multiplicative moment-map equation whose determinant projects to elliptic addition. A
frozen sequence of reflection functors reduces the dimension vector while retaining a
canonical inverse to every simple source factor, so `B+sigma` independent factor-base
relations and a separate masked-target decomposition can be recovered with complete time
and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **source-preserving dimension reduction by multiplicative-
preprojective reflection functors**. Each factor-base atom labels one simple star-quiver
factor; the multiplicative moment map enforces the target product, reflection changes the
dimension vector, and inverse reflection is claimed to lift a reduced simple factor back
to its exact curve point. Determinant then returns the elliptic relation.

This operation is rejected as a semantic merge. The moment map records an aggregate
matrix product, not a factorization of a supplied elliptic target. Building a
source-labelled representation requires selecting the source simples first, while
forgetting those labels leaves the same extension multiplicities and determinant quotient
as the rejected Hall/Hecke lanes. A generic quiver solver, dimension-vector retuning, or
relation-only determinant is a control.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order
   `N=p^(1+o(1))`, with challenge `Q=[x]P`.
2. A deterministic target-independent factor base `F={F_1,...,F_B}` has
   `B=N^beta` and complete point/sign labels.
3. A scalar-blind map sends factor atoms and arbitrary targets to star-quiver data and
   makes the multiplicative moment-map equation equivalent to elliptic addition on all
   exceptional charts.
4. Reflection functors are defined along the complete frozen sequence, reduce total
   representation size, and preserve enough information for an exact simple-factor lift.
5. Representation construction, all reflection branches, stabilizers, output,
   relation rank, factor-log linear algebra, blind descent, verification, and peak memory
   are fully charged.
6. No hidden scalar labels, target-selected simple factors, post-hoc orbit choices, or
   precomputed source tables are permitted.

## Semantic fingerprint

`source_labelled_star_quiver | multiplicative_moment_map | reflection_functor_dimension_reduction | simple_factor_source_lift | determinant_back_to_E | blind_descent`

The collision key is `aggregate moment map + source-labelled representation already
containing atoms + determinant/Hall/Hecke projection`. Reflection changes a supplied
representation; it does not construct the missing source-retaining representation from a
target point.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H008`, the nearest hidden
   indecomposable Prym-block realization whose internal factors still need an exact source
   map.
2. `ledger/FINDING-PF-IC-001.md` — imported `PO96`, the closest saturation computation
   where an explicit representation must be constructed before it can be decomposed.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate
   barrier that blocks a representation change without an exact target/source inverse.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where public feature spaces fail to
   contain factor-log orientation.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, the closest exact-membership
   compilation control whose new solver vocabulary does not remove source cost.

## Closest primary literature

- Crawley-Boevey and Shaw, [Multiplicative preprojective algebras, middle convolution and
  the Deligne-Simpson problem](https://arxiv.org/abs/math/0404186), supplies the
  multiplicative moment-map and reflection setting, not an elliptic target-to-simple-
  factor inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the nearby point-decomposition relation that still requires exact sources.
- Shoup, [Lower bounds for discrete logarithms](https://www.shoup.net/papers/dlbounds1.pdf),
  supplies the generic square-root boundary for any scalar-blind representation.

No checked primary source constructs the claimed quiver encoding or reflection descent.
The proposal remains novelty-unverified and is preserved as a merge boundary.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the star quiver, multiplicative parameters, determinant map,
   reflection order, stabilizer convention, and exhaustive tiny-curve reference data.
2. Encode each labelled `F_i` as a simple factor and prove on complete charts that the
   determinant of any accepted moment-map representation equals the elliptic sum of its
   source labels.
3. For known random targets `R=[a]P`, construct target data without using a source tuple,
   apply the frozen reflection sequence, invert every surviving branch to exact
   factor-base points, and independently verify their sum.
4. Retain every miss, duplicate, stabilizer ambiguity, and failed inverse; collect at
   least `B+sigma` independently verified relation rows and their known target scalars.
5. Solve the factor-base logarithm system modulo `N`, then independently verify every
   recovered factor log by scalar multiplication on `E`.
6. Freeze all setup data and query masked blind targets `Q+[t]P` for preregistered random
   masks `t`; lift a complete source-labelled factorization and substitute the calibrated
   factor logs.
7. Unmask the resulting scalar candidate, enumerate every retained ambiguity, and accept
   only after independently checking `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` group operations with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`, quiver/setup exponent be `a`,
per-target construction and reflection exponent be `q`, inverse source-output exponent be
`o`, reciprocal relation and target success densities be `N^delta` and `N^delta_t`,
factor-log linear algebra be `N^ell` with `ell>=2beta` absent proved structure, and peak
memory be `N^mu`.

The fully charged exponent is

`lambda=max(a, beta+delta+q+o, ell, delta_t+q+o)`,

and memory must satisfy `mu>=max(beta, representation_state, branch_output)`. If the
source-labelled representation is supplied explicitly, its construction/output size is
charged in `a` or `o`; if the moment-map fiber or inverse-reflection tree has
`N^r` branches, then `r` is included in `q+o`. Offline advice is not omitted or divided
away for a single challenge.

## Likely fatal obstruction

The multiplicative moment map constrains a product of matrices only after the matrices or
their conjugacy classes are supplied. It does not canonically factor a point `R` into
factor-base simples. Reflection functors preserve equivalence data of a supplied
representation, but inverse reflection can branch over the original extension variety.
Keeping source labels makes the input representation the desired witness; dropping them
leaves only an aggregate orbit/determinant and reproduces the Hall/Hecke source-forgetting
obstruction. Faithful target orientation can additionally force an order-`N` state space.

## Proof track

Construct a scalar-blind target-to-quiver map, prove a biconditional between its
multiplicative moment-map solutions and exact factor-base decompositions, and prove that a
frozen reflection sequence plus inverse returns all source points with sub-rho state,
branching, and output. Then prove relation rank, factor-log calibration, blind descent,
verification, and `lambda,mu<1/2`.

## Disproof track

Show that target data determines only the aggregate moment-map orbit, that constructing a
representation requires the source factors, that inverse reflection enumerates the full
extension fiber, that determinant loses the simple factors, or that complete time/output/
memory has exponent at least `1/2`.

## Positive and negative controls

- Positive primitive control: published multiplicative-preprojective representations with
  known reflection equivalences and simple factors.
- Positive source control: planted toy quiver representations whose factor labels and
  determinant sums are exhaustive.
- Negative aggregation control: erase simple labels while retaining the same moment-map
  orbit and determinant.
- Mechanism controls: Hall/Hecke extension enumeration, a generic quiver solver, and a
  source tuple supplied before reflection.
- Leakage control: forbid scalar coordinates, target-selected conjugacy classes, hidden
  atom tables, and discarded inverse branches.
- Baseline control: matched Pollard-rho and BSGS runs on every completed toy family.

## Quantitative promotion and falsification gates

No active promotion gate remains for this merged formulation. A versioned successor
would first require zero target/moment-map/source-lift errors on exhaustive ordinary curves
through 18 bits, at least `1,000` independent verified rows and `100` blind descents at
each of the two largest sizes, fresh rank at least `0.8B`, and upper 95% bounds
`a,q+o,lambda,mu<=0.45`. Falsify on one independently reproduced source mismatch, any
need to supply the simple factors before target construction, lower 95% inverse-branch or
state exponent `>=0.50`, or complete `lambda>=0.50` in every arm.

## Artifact plan

- Merge proof: `ideas/artifacts/ECDLP-IDEA-093/quiver_hall_merge.md`
- Representation specification: `ideas/artifacts/ECDLP-IDEA-093/star_quiver_spec.yaml`
- Toy checker: `ideas/artifacts/ECDLP-IDEA-093/reflection_descent.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-093/verify_quiver_sources.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-093/analysis.md`
- Any future runs: `ideas/artifacts/ECDLP-IDEA-093/runs/<run-id>/`

## Interpretation boundary

This record is toy, heuristic, model-bound, and novelty-unverified. A correct moment-map
identity, reduced dimension vector, reflected representation, determinant equality, valid
relation, or recovered toy scalar is not evidence of a better-than-rho algorithm or a
cryptanalytic breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-093/quiver_hall_merge.md` proving that target-only multiplicative moment-map data cannot recover simple source factors without reconstructing the occupied Hall/Hecke extension fiber.
