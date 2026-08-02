# Nested source-norm literature review v1

## Handoff: scalar-only resultant boundary

### Claim or task

Determine whether primary literature supplies an exact scalar-only norm or
resultant specialization with target work and state `o(B^2)`, exact child
substitution, and signed witness recovery.

### Status

`OPEN`, `NOVELTY-UNVERIFIED`. No exact match was found. This is a literature gap,
not a lower bound or novelty claim.

### Assumptions

- Three split source algebras have total tensor dimension `Theta(B^3)`.
- Strict `o(B^2)` excludes `soft-O(B^2)` target work or state.
- Fixed advice and preprocessing remain below and are charged against `o(B^3)`.
- Exactness includes EC exceptional cases, child predicates, and five signed
  public identifiers.

### Evidence so far

#### Closest primary mechanisms

- Jeronimo and Sabia, [Sparse resultants and straight-line
  programs](https://doi.org/10.1016/j.jsc.2017.05.005), JSC 87, 2018. Sparse
  resultant SLP size is polynomial in support and mixed-volume parameters. The
  degree in the target-element coefficient block is already
  `d_1*d_2*d_3=Theta(B^3)` here, so the theorem gives no `o(B^2)` specialization.
  Degree is not a circuit lower bound.
- D'Andrea and Sombra, [A Poisson formula for the sparse
  resultant](https://arxiv.org/abs/1310.6617), PLMS 110(4), 2015. The exact root
  product and multiplicity formula supports the source-norm theorem and norm
  factorization, not its desired complexity.
- D'Andrea and Dickenstein, [Explicit formulas for the multivariate
  resultant](https://arxiv.org/abs/math/0007036), JPAA 164, 2001. Determinantal
  complexes can improve explicit matrices, but still consume explicit
  coefficient representations.
- Poteaux and Schost, [Modular composition modulo triangular sets and
  applications](https://cs.uwaterloo.ca/~eschost/publications/mulmodcomp.pdf),
  Computational Complexity 22, 2013. Norms, power projection, and change of
  order are quasi-linear in the full quotient dimension; here that dimension is
  `Theta(B^3)` and the interfaces carry that many coordinates.
- Bostan, Flajolet, Salvy, and Schost, [Fast computation of special
  resultants](https://cs.uwaterloo.ca/~eschost/publications/BoFlSaSc05.pdf), JSC
  41(1), 2006. Special root-pair sums/products can be computed in
  `O(M(m*n))`; for `m=n=B`, even favorable full output is `soft-O(B^2)` with
  `B^2` coefficients. This is the strongest structured-contraction analogy, not
  an exact match for the three-source EC element.
- Moroz and Schost, [A Fast Algorithm for Computing the Truncated
  Resultant](https://cs.uwaterloo.ca/~eschost/publications/resultant_series_final.pdf),
  ISSAC 2016. Scalar output sensitivity is possible for explicit bivariate
  operands, but the theorem does not fuse three implicit source algebras or
  remove their coefficient-ring boundary.
- Bostan, Jeannerod, and Schost, [Tellegen's Principle into
  Practice](https://cr.yp.to/bib/2003/bostan.pdf), ISSAC 2003. Linear SLPs can be
  transposed at essentially equal cost. The norm is nonlinear; transposition
  does not create a scalar-only norm circuit without a prior circuit.
- Wiedemann, [Solving sparse linear equations over finite
  fields](https://doi.org/10.1109/TIT.1986.1057137), IEEE TIT 32(1), 1986.
  Scalar Krylov projections retain full matrix-vector state; here standard
  vectors have `Theta(B^3)` coordinates unless succinct closure is separately
  proved.
- Bostan, Jeannerod, and Schost, [Solving structured linear systems with large
  displacement rank](https://mathexp.eu/bostan/publications/BoJeSc08.pdf), TCS
  407, 2008. Fast structured solves require supplied low-rank generators. No
  source proves such generators or target-update closure for the EC norm.
- Bosma and Lenstra, [Complete Systems of Two Addition Laws for Elliptic
  Curves](https://www.math.ru.nl/~bosma/pubs/JNT1995.pdf), JNT 53, 1995, and
  Renes, Costello, and Batina, [Complete Addition Formulas for Prime Order
  Elliptic Curves](https://www.iacr.org/archive/eurocrypt2016/96650347/96650347.pdf),
  EUROCRYPT 2016. Complete addition systems may remove explicit branch masks,
  but do not reduce quotient dimension or preserve source labels by themselves.

#### Exact gap

No located source simultaneously:

1. accepts three fixed degree-B split source algebras and the complete
   target-dependent EC membership element;
2. computes its norm with target work and state `o(B^2)`;
3. uses fully charged fixed advice and preprocessing `o(B^3)`;
4. avoids a B2 quotient element, equivalent vector, or equivalent evaluations;
5. handles every EC exceptional branch and zero factor exactly;
6. exposes both child predicates under node-polynomial substitution; and
7. produces an auditable five-ID signed witness.

Logical scalar output and scalar-resident computation are not interchangeable.
Triangular norms and Krylov methods carry full quotient vectors; product-tree
streaming retains `B^3` target evaluations; succinct determinant protocols
reduce verifier work rather than prover computation or witness recovery.

#### Recommended mechanism

The closest constructive candidate is a BFSS-style root-product or power-sum
contraction after a complete addition-law encoding. It becomes relevant only if
the EC element admits a proved bounded-separation form

```text
G_(I,Q)=sum_(ell=1)^r
  a_(ell,Q)(T_1)*b_(ell,Q)(T_2)*c_(ell,Q)(T_3),
```

or an equally compact recurrence/displacement representation whose generators,
moments, selector, and child substitutions are all `o(B^2)`. Computing a full
degree-`B^3` characteristic polynomial does not qualify.

### Failure modes

- Treating mixed-volume degree as a circuit lower bound.
- Calling `soft-O(B^2)` subquadratic.
- Hiding source tables or relation matrices in fixed preprocessing.
- Counting a scalar Krylov projection but omitting its vectors.
- Applying Tellegen transposition to the nonlinear norm map.
- Proving parent zero only, without child values or signed witness recovery.

### Next concrete action

Derive or refute a bounded-separation normal form for the complete-projective
`G_(I,Q)`. Enumerate every tensor factor, generator, moment, selector, and child
substitution; reject the route if any target-dependent object or operation count
is `Omega(B^2)`.

### Artifact paths

- `nested-source-norm-preflight-v1.md`
- `pre-implementation-literature-review-v1.md`
