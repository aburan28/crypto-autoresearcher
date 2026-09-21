# PO-transfer-006 Theory Note: Complementary Cofiber Boundary

Date: 2026-07-13

## Claim Taxonomy

- `RESTRICTED THEOREM`: a nonconstant genus-2-to-elliptic map forces a split
  Jacobian.
- `RESTRICTED THEOREM`: complementary quotient fibers give constant-sum
  relations on the target elliptic factor.
- `RESTRICTED THEOREM`: a fixed degree-3 correspondence gives only a bounded
  number of cofiber completions per target point.
- `HEURISTIC / MODEL-BOUND`: without algebraic concentration, target
  factor-base completion has probability on the order of `(B/n)^2` and the
  relation hypergraph needs near-linear support for reusable rank.
- `OPEN`: a complementary label may still correlate with a factorization or
  sieve predicate that invalidates the random-label model.

## Theorem 1: A Faithful Elliptic Transfer Forces Splitting

Let `C` be a smooth projective genus-2 curve over a field `k`, and let
`f:C->E` be a nonconstant morphism to an elliptic curve.  Then the induced
homomorphism

```text
f_*: Jac(C) -> E
```

is nonzero and hence surjective.  Its dual pullback has an elliptic image in
`Jac(C)`.  By Poincare reducibility, there is an elliptic curve `E'` and an
isogeny

```text
Jac(C) ~ E x E'.
```

In particular, `Jac(C)` is not absolutely simple.  For a maximal degree-`d`
elliptic subcover, the complementary construction gives a `(d,d)` split and an
isogeny of degree `d^2` under the standard hypotheses.

### Consequence

A genuinely simple genus-2 Jacobian cannot be the carrier of a nonzero
composable elliptic DLP transfer.  It can only supply a non-homomorphic incidence
label.  Such a label has no scalar consequence until a separately verified
joint relation is found; random joint acceptance is a valid null model.

### Limitation

This does not rule out simple higher-dimensional or non-Jacobian incidence
objects as filters.  It rules out describing their effect as a faithful
homomorphic elliptic transfer.

## Theorem 2: Complementary Fibers Give Constant-Sum Relations

Let

```text
f:C->E,  g:C->E'
```

be finite maps, and let `D_R=g^*(R)` be the degree-`deg(g)` fiber divisor over
`R in E'`, including multiplicities.  Fix a base point `R0`.  In the Jacobian,

```text
[D_R-D_R0] = g^*([R-R0]).
```

Pushing to `E` gives

```text
sum_{P in D_R} f(P) - sum_{P in D_R0} f(P)
    = (f_* g^*)(R-R0).
```

If `f` and `g` are complementary, `f_* g^*=0`.  Therefore

```text
sum_{P in D_R} f(P) = K
```

for a fixed public `K in E`, independent of `R`, whenever exceptional fibers
and basepoint conventions are handled consistently.

For degree three, a rational fiber `D_R=P1+P2+P3` gives

```text
f(P1)+f(P2)+f(P3)=K.
```

This is a native target-coupled relation: if `f(P1)=Q`, cofiber completion gives

```text
Q = K-f(P2)-f(P3).
```

### Limitation

Relation correctness is not a complexity improvement.  A generic group can
generate a matched relation by choosing `A,B` and setting `C=K-A-B`.

## Theorem 3: Fixed Degree Gives Bounded Completion Multiplicity

Assume both maps have degree three and all relevant fibers are separable.  A
target point `Q in E` has at most three lifts through `f`.  Each lift lies in one
`g` fiber and therefore supplies at most one unordered pair of complementary
`E` images.  Hence TCD exposes at most three generic cofiber decompositions of
`Q`, before collisions and exceptional fibers.

More generally, degree pair `(d1,d2)` supplies at most

```text
d1 * binomial(d2-1, d2-1) = d1
```

full-cofiber completions of this exact form.  The multiplicity is bounded when
the cover degrees are fixed.

### Consequence

A fixed `(3,3)` cover cannot win asymptotically from preimage count alone.  A
surviving candidate must show one of:

- cofiber images concentrate in a public factor base;
- different fibers overlap enough to create unusually fast rank growth;
- `phi2` labels admit a norm/factorization sieve unavailable to generic triples;
- a family with growing degree has sublinear fiber-generation cost.

## Rank Necessity For The Cofiber Hypergraph

Represent each complete rational `g` fiber by one ternary row over its distinct
`f` images.  If a selected subgraph has `t` fiber rows and `B` point columns,
then, independently of geometry,

```text
rank <= t.
```

Recovering `B` point logarithms up to one known scale requires rank at least
`B-1`, so necessarily

```text
t >= B-1.
```

Because each row has three incidences, this also requires average selected
vertex degree approximately three.  A small collection of mostly disjoint
fibers cannot close rank.  The experiment must therefore report columns and
rank together; a large count of valid zero relations is not enough.

## Random-Label Cost Heuristic

Let `n=#E` and let a public factor base have size `B`.  If the two cofiber
completions of a target lift behave as independent uniform points, one completion
hits the factor base with probability approximately

```text
(B/n)^2.
```

With at most three completions, translating the target by public multiples of
the generator needs approximately

```text
n^2/(3*B^2)
```

trials.  Beating a `sqrt(n)` target-descent budget under this model requires
roughly `B > n^(3/4)`.  Generic sparse linear algebra on that many columns is
already far above rho.  This is a model-bound obstruction, not a theorem against
algebraic concentration.

## Proof Track

1. Verify the explicit quotient equations and map normalization.
2. Include exceptional fibers and points at infinity in the divisor proof.
3. Confirm `f_*g^*=0` for the selected complementary pair.
4. Derive finite-field rational-fiber distributions and separability failures.
5. Bound rank growth for a matched random 3-uniform relation hypergraph.

## Disproof Track

1. Search for cells where cofiber completion is measurably biased toward a
   rational-map or norm-smooth factor base.
2. Compare public edge prefixes with relation-valid generic triples.
3. Test whether low-support cores achieve `rank=B-1` before near-full coverage.
4. Shuffle labels while preserving fiber sizes.
5. If all fixed-degree cells match the null, move to a growing-degree
   factorization-label family rather than another constant-degree cover.

## Red-Team Preflight

The first affine probe must fail closed on interpretation:

- `rank >= B-1` is necessary but not target recovery; the final system must
  model the fixed sum `K`, a known generator anchor, the target coefficient, and
  affine RHS compatibility together;
- the strongest control is public EC addition itself, which generates
  `(A,B,K-A-B)` at constant cost; TCD must beat this relation-valid source after
  matching edge count, vertex marginals, degree sequence, duplicates, and prefix
  schedule;
- affine fibers omit poles, branch multiplicities, and points at infinity, so a
  positive result requires projective replay and a base-divisor derivation of
  `K` before promotion;
- quotient-label inversion, cubic factorization, square roots, rejected fibers,
  memory, and sparse linear algebra are part of the algorithmic cost;
- the three tiny preregistered fields can falsify the mechanism but cannot
  support an asymptotic exponent claim without fresh larger cells.

## Handoff: complementary cofiber theorem boundary

### Claim or task

Determine whether a faithful `(3,3)` split correspondence creates useful
factor-base/rank structure beyond its bounded cofiber multiplicity.

### Status

HYPOTHESIS

### Assumptions

- ordinary prime-order toy target groups;
- explicit smooth complementary degree-3 covers;
- public target and factor bases;
- relation-valid generic triples are the primary control.

### Evidence so far

- the split and constant-sum statements follow from standard Jacobian functoriality;
- BNIT established that native split-cover relations can recover toy targets;
- PO4 showed that one incidence reformulation of BNIT does not compress the
  relation search;
- no measured TCD rank or factor-base excess exists yet.

### Failure modes

- fixed-degree labels provide only constant multiplicity;
- the hypergraph needs near-linear support for rank;
- a special `j=0/1728`, MOV-small, or non-prime-order cell creates a false signal;
- exceptional fibers invalidate the affine relation accounting.

### Next concrete action

Run `po_transfer_006_trielliptic_cofiber.sage`, then independently replay every
map and fiber relation before interpreting rank or target descent.

### Artifact paths

- `research/PO_transfer_006_contract.md`
- `research/PO_transfer_006_theory.md`
- planned: `experiments/ecdlp_isogeny/po_transfer_006_trielliptic_cofiber.sage`
