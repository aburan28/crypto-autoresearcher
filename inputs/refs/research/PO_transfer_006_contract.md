# Experiment Contract: PO-transfer-006 Trielliptic Cofiber Decomposition

## Candidate

Candidate: use the complementary quotient of an explicit `(3,3)`-split
genus-2 Jacobian as a non-homomorphic label for points on the target elliptic
curve.  For a smooth genus-2 curve

```text
C: y^2 = P(x)Q(x)
```

with complementary degree-3 maps

```text
phi1: C -> E1
phi2: C -> E2,
```

each full `phi2` fiber gives a ternary relation among its three `phi1` images.
Equivalently, a lift of a target point through `phi1`, followed by completion of
its `phi2` cofiber, may expose a small family of two-point decompositions of the
target on `E1`.

Candidate name: **Trielliptic Cofiber Decomposition (TCD)**.

Status before execution: `HYPOTHESIS / TOY / MODEL-BOUND / NOVELTY OPEN`.

This is deliberately harder than asking whether an isogenous elliptic model has
a lower Semaev degree.  The required output is a target-coupled relation source
whose complementary labels improve factor-base hits, rank, or descent beyond a
relation-valid generic triple generator.

## Hard Goal

Construct and publicly verify a `(3,3)`-split correspondence for which the
cofiber relation hypergraph has enough non-random overlap that a reusable
factor base, full rank, and blind target descent can be obtained with total
charged work below Pollard rho on at least three increasing prime fields.

No success is credited for:

- three preimages instead of one;
- a constant-factor decomposition count;
- zero relations without reusable factor-base rank;
- target recovery using hidden factor-base logs;
- a genus-2 system that is not proved to be the advertised cover.

## Faithful Object

Use the generic degree-3 formulas of Djukanovic.  For public parameters
`a,b,c` with the required discriminants nonzero, define

```text
P(x) = x^3 + a*x^2 + b*x + c
Q(x) = 4*c*x^3 + b^2*x^2 + 2*b*c*x + c^2
f1(x) = x^2/P(x)
f2(x) = (b*x+3*c)^2
        *((b^3-4*a*b*c+9*c^2)*x+c*(b^2-3*a*c))/Q(x).
```

The maps are

```text
phi1(x,y) = (f1(x), y*f1'(x)/x)
phi2(x,y) = (f2(x), y*f2'(x)/(b*x+3*c)),
```

followed by the documented changes to standard Weierstrass coordinates.  Every
production point must verify on `C`, its `phi1` image on `E1`, and its `phi2`
image on `E2`.

## Restricted Theory Boundary

An absolutely simple genus-2 Jacobian cannot receive or supply a nonzero
homomorphic elliptic transfer: a nonconstant map `C -> E` induces an elliptic
subvariety of `Jac(C)`, and Poincare reducibility makes the Jacobian isogenous
to a product.  Therefore a faithful composable elliptic-to-Jacobian channel in
genus 2 must be split.  A genuinely simple Jacobian remains relevant only for a
non-composable incidence test, whose joint acceptance must be shown rather than
assumed.

For complementary maps, `phi1_* phi2^*` is zero after basepoint normalization.
Thus the `phi1`-sum of a complete `phi2` fiber is constant.  This proves relation
correctness but not useful factor-base probability.  Fixed fiber degree alone is
only a constant multiplier.

## Hypothesis

For at least one ordinary prime-order `E1/F_p` in the explicit family, the
ternary cofiber hypergraph differs from a relation-valid random ternary
hypergraph in at least one algorithmically useful way:

- a smaller edge set spans almost all factor-base columns;
- low-support cores give rank `B-1` on `B=o(p)` columns;
- blind target vertices have more factor-base cofiber completions than the
  matched `(B/#E1)^2` model;
- complementary labels support an equality-hash or sieve with charged cost
  below generic relation generation.

## Null Hypothesis

The cofiber graph is a bounded-degree algebraic presentation of generic group
relations.  Each target gets only `O(1)` decompositions, factor-base completion
probability remains `Theta((B/#E1)^2)`, small induced subgraphs are rank-poor,
and near-linear many vertices/edges are required before logs or target descent
become recoverable.  Total work is then above rho even before sparse linear
algebra.

## Parameters

- fields: `p in {101, 211, 431}` for the first bounded sweep;
- cell search seed: `20260713`;
- curve family: generic smooth `(3,3)`-split curves with prime-order ordinary
  `E1`, excluding `j(E1) in {0,1728}` and singular/exceptional maps;
- cover parameter `d=1`;
- factor-base sizes: public deterministic sizes near
  `#E1^(1/3)`, `#E1^(1/2)`, and `#E1^(2/3)`;
- target schedule: deterministic public points outside each factor base; target
  discrete logs are neither constructed nor consumed by collection;
- relation shape: the three `phi1` images of one complete rational `phi2` fiber,
  with the fixed fiber sum moved to the row;
- baselines: Pollard rho, BSGS, relation-valid random triples
  `(R,S,K-R-S)`, shuffled-label fibers, and the BNIT/PO4 results.

## Model Of Computation

- Count base-field operations, cover-map evaluations, cubic fiber work, group
  additions, relation verification, retained entries, rank work, and target
  descent.
- A full enumeration of `C(F_p)` is permitted only as a toy discovery oracle;
  the reported algorithmic floor must separately charge how fibers would be
  generated from public quotient labels.
- Do not use target or factor-base discrete logs to choose parameters, labels,
  edges, factor bases, targets, or stopping points.
- Discrete logs may be computed only after collection to verify the recovered
  nullspace scale and blind target answer.

## Metrics

- cover-map verification failures and exceptional affine points;
- complete `phi1` and `phi2` fiber counts and size histograms;
- number of distinct target decompositions per `E1` vertex;
- constancy and public verification of the complementary-fiber sum;
- shuffled-label false-relation rate;
- vertices, edges, degrees, connected components, two-core size, and duplicate
  edges;
- incidence-matrix rank, nullity, and rank per retained edge;
- smallest public edge prefix reaching rank `columns-1` when it exists;
- factor-base edge counts, rank, target completion rate, and matched generic
  completion rate;
- public target recovery and post-hoc verifier result;
- optimistic charged floor, memory, sparse-LA dimensions, ratios to rho/BSGS,
  and three-size exponent fits.

## Positive Controls

- Verify every evaluated map image on the advertised elliptic curve.
- For every complete production `phi2` fiber, verify its three `phi1` images
  sum to the same public constant.
- Plant a target by selecting a public vertex from a complete fiber and verify
  that cofiber completion returns the other two points without using a log.
- Verify the actual log vector lies in the public relation matrix kernel only
  after collection is frozen.

## Negative Controls

- Flip one point sign in each sampled fiber relation; the sum must change.
- Shuffle cover points among matched size-three labels; the constant-sum rate
  must match the finite-group random model.
- Generate the same number of relation-valid generic triples and compare
  coverage, cores, rank, and target completions.
- Add a configuration-model control matched for fiber count, vertex marginals,
  degree sequence, duplicate policy, and public prefix order.
- Add `EC_addition_synthetic_cofiber`: choose two public points and construct
  the third as `K-A-B`, then run the identical factor-base/rank/descent path.
- Compare deterministic factor bases with matched random subsets.

## Success Criterion

Structural success requires all of:

- zero cover/map/relation verification failures;
- a public complementary-label algorithm, not full `C(F_p)` enumeration;
- a factor base of size `B=o(#E1)` with reusable rank at least `B-1`;
- blind target descent using only collected rows and public arithmetic;
- a cofiber completion or rank excess at least `4x` its matched generic control
  on all three sizes;
- memory below `4*sqrt(#E1)` entries.

Algorithmic success additionally requires:

- charged full recovery below `0.8*rho` on at least one size;
- charged exponent at most `0.5` over three sizes;
- no hidden cost from fiber inversion, sparse linear algebra, or target descent;
- no advantage attributable only to constant degree, special endomorphisms, a
  small embedding degree, or a weak/non-prime-order target.

Pre-result red-team rule: the bounded affine sweep is a falsification harness.
It cannot set structural or algorithmic success to true until an independent
projective verifier also passes all of the following:

- complete fibers include multiplicities, branch points, poles, and points at
  infinity;
- `K` is derived from a fixed base divisor, not inferred only from successful
  affine fibers;
- an augmented public system includes the `K`, generator, and target columns,
  checks RHS compatibility and component membership, recovers an explicit
  target scalar without consuming hidden logs, and verifies `kG=Q`;
- a degree/vertex-marginal preserving configuration-model control and an
  `EC_addition_synthetic_cofiber` control fail to reproduce the claimed excess;
- quotient-label inversion, cubic solving, square roots, rejected fibers,
  exceptional fibers, retained memory, and sparse-LA work are separately
  charged.

Showing only that the post-hoc true log vector lies in a relation kernel is not
target recovery.

## Falsification Criterion

Narrow TCD if the three-size sweep shows any persistent combination of:

- only `O(1)` decompositions per target;
- factor-base completion matching `(B/#E1)^2` or the generic triple control;
- rank requiring `Theta(#E1)` vertices or edges;
- target recovery only from a full near-`#E1` matrix;
- charged relation work above rho before linear algebra;
- shuffled labels reproducing the claimed signal.

This would close only fixed-degree complementary-cofiber multiplicity and its
tested unramified affine factor bases.  It would leave open exceptional or
projective fibers, growing-degree correspondences,
label-conditioned norm factorization, Prym-assisted sieves with a proved query
structure, and non-homomorphic lifts whose labels carry smoothness semantics.

## Proof Track

- Verify the explicit maps symbolically or pointwise on every production cell.
- Prove the constant cofiber-sum theorem from complementarity.
- Formalize why a nonzero elliptic transfer forces a split Jacobian.
- Derive relation and target equations including exceptional fibers and points
  at infinity.
- Bound factor-base completion and rank under a random regular-hypergraph model.

## Disproof Track

- Compare with relation-valid generic triples, not unconstrained random rows.
- Measure whether apparent rank comes from near-complete vertex coverage.
- Merge duplicate points and edges before rank.
- Charge cubic inversion and all failed/exceptional fibers.
- Test whether any excess disappears after curve, target, or factor-base
  randomization.

## Minimal Experiment

1. Find one valid generic `(3,3)` cell at each preregistered prime.
2. Enumerate toy affine cover points and verify both quotient maps.
3. Build complete rational cofibers and prove their constant `E1` sum.
4. Construct the public ternary relation hypergraph and matched controls.
5. Sweep deterministic factor bases and blind targets.
6. Compute rank/core profiles and an optimistic rho comparison.
7. Run an independent public verifier before promoting any signal.

## Planned Reproduction Command

```bash
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_006_trielliptic_cofiber.sage \
  --out experiments/ecdlp_isogeny/po_transfer_006_result.json
```

## Literature Boundary

- T. Shaska, *Genus two curves covering elliptic curves: a computational
  approach*, 2012, https://arxiv.org/abs/1209.3187.
- M. Djukanovic, *Families of (3,3)-split Jacobians*, 2018,
  https://arxiv.org/abs/1811.10075.
- P. Sarkar and S. Singh, *A New Method for Decomposition in the Jacobian of
  Small Genus Hyperelliptic Curves*, 2014,
  https://eprint.iacr.org/2014/815.
- P. Gaudry, *Index Calculus for Abelian Varieties of Small Dimension and the
  Elliptic Curve Discrete Logarithm Problem*, 2009,
  https://doi.org/10.1016/j.jsc.2008.08.005.

The explicit covers, split-Jacobian theorem, and genus-2 decomposition methods
are known.  The proposed cryptanalytic use of complementary cofibers is not
claimed novel until a broader literature review and a non-generic measured
advantage both succeed.

## Required Handoff Outcome

The result must end with one of:

- `POSITIVE SIGNAL`: a replicated non-generic rank/decomposition excess, with
  the next solver/descent obligation;
- `NEGATIVE RESULT`: fixed-degree cofibers match the generic baseline under the
  tested model, with the next growing-degree or factorization-label candidate;
- `INCONCLUSIVE`: exact missing map, fiber, rank, or cost evidence and one
  concrete repair command.
