# Literature map: generalized roots and exact subset norms

**Prepared:** 2026-07-18

## Scope and claim boundary

This refresh covers dedicated generalized root finding for prime-field ECDLP,
bounded multivariate roots, fixed-point-set multipoint evaluation, exact
subset-intersection self-reduction, structured polynomial linear algebra, and
fixed-group preprocessing.

No primary source located in this search gives an exact five-leaf prime-field
decoder with complete witness output, target-specific state `o(B^2)`, and total
one-instance relation work `o(B^2.5)` at `B=n^(1/5)`. No source located gives
the stronger fixed-curve subset-norm operator in
`EXP-ECDLP-SUBSET-NORM-TREE-001`. This is a search boundary, not a novelty proof.
The exact primary-source audit and output-interface table are preserved in
`experiments/EXP-ECDLP-SUBSET-NORM-TREE-001/pre-implementation-literature-review-v1.md`.
The targeted scalar-only norm/resultant follow-up is preserved in
`experiments/EXP-ECDLP-SUBSET-NORM-TREE-001/nested-source-norm-literature-review-v1.md`.

## 1. The generalized-root problem is explicit prior art

Petit, Kosters, and Messeng define prime-field factor bases by a high-degree
rational map `L` represented as a composition of low-degree maps. They combine
the composition chain with Semaev equations, and identify the following problem
as central:

```text
find X_i in K such that f(X_1,...,X_m)=0 and L(X_i)=0 for every i.
```

They explicitly call for a dedicated algorithm that does not rely on Groebner
bases. Their concrete source families use either smooth structure in `p-1` or a
smooth subgroup on an auxiliary elliptic curve represented by an isogeny chain.
Their algorithms are parameter-limited and their asymptotic solver cost is left
open.

- Christophe Petit, Michiel Kosters, and Ange Messeng, *Algebraic Approaches
  for the Elliptic Curve Discrete Logarithm Problem over Prime Fields*, PKC
  2016: https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf

**Consequence.** `EXP-ECDLP-GENROOT-CIRCUIT-001` instantiates a named open
problem. Its possible novelty is an exact dedicated decoder and cost proof, not
the use of composed rational maps or an uneliminated polynomial chain.

## 2. Multivariate small roots are a heuristic lane here

Jochemsz and May give a systematic Coppersmith-style strategy: select polynomial
shifts, scale monomials by candidate bounds, construct and reduce a lattice, and
derive attack-specific root bounds. Their multivariate applications rely on the
usual algebraic-independence and short-vector heuristics; the paper does not
provide a theorem for arbitrary elliptic addition circuits.

- Ellen Jochemsz and Alexander May, *A Strategy for Finding Roots of
  Multivariate Polynomials with New Applications in Attacking RSA Variants*,
  ASIACRYPT 2006: https://www.iacr.org/archive/asiacrypt2006/42840270/42840270.pdf

For five interval-sized sources, the generic box has

```text
X_1*X_2*X_3*X_4*X_5 approximately B^5 approximately p.
```

The literature therefore does not supply a free small-root margin. A positive
claim needs an explicit shift set and determinant inequality for the actual
addition graph, including every full-field auxiliary variable.

## 3. Extension-field EC joins use full multipoint output

Delaplace and May reduce an `F_(p^2)` EC join to a bivariate product polynomial
and evaluate it at every point of the second list. Their algorithm returns all
zero pairs and then performs exact source recovery. Delaplace, Fouque, Kirchner,
and May later replace the multipoint routine and add fixed-curve preprocessing,
but still construct the full evaluation list. They explicitly report large
stored lists as the bottleneck and leave extension to prime fields open.

- Claire Delaplace and Alexander May, *Can We Beat the Square Root Bound for
  ECDLP over F_(p^2) via Representations?*, ePrint 2019/800 and Journal of
  Mathematical Cryptology 14(1), 2020: https://eprint.iacr.org/2019/800
- Claire Delaplace, Pierre-Alain Fouque, Paul Kirchner, and Alexander May,
  *Solving ECDLP over F_(p^l) with Pre-computation via Representation
  Technique*, 2020 preprint: https://inria.hal.science/hal-02427655

**Consequence.** These are strong positive controls for algebraic batch sharing.
They do not provide an exact sparse zero-test that avoids emitting one value per
candidate, and their extension-field structure must not be attributed to an
ordinary prime-field curve.

## 4. Fast multipoint evaluation still reports every value

Kedlaya-Umans-style modular composition and later finite-field multivariate
multipoint algorithms are near-linear in input plus output size in their stated
regimes. The output is the complete vector of `N` evaluations. Fixed generic
point sets can also be preprocessed for quasi-linear bivariate evaluation, but
the algorithm still returns all evaluations and assumes a registered genericity
condition.

- Vishwas Bhargava, Sumanta Ghosh, Zeyu Guo, Mrinal Kumar, and Chris Umans,
  *Fast Multivariate Multipoint Evaluation Over All Finite Fields*:
  https://arxiv.org/abs/2205.00342
- Vincent Neiger, Johan Rosenkilde, and Grigory Solomatov, *Generic Bivariate
  Multi-point Evaluation, Interpolation and Modular Composition with
  Precomputation*: https://arxiv.org/abs/2003.12468
- Kiran Kedlaya and Chris Umans, modular composition and multipoint evaluation:
  https://authors.library.caltech.edu/records/6bpbb-0gh88

**Restricted output boundary.** These methods can accelerate construction of a
`B^2` predicate vector. They do not by themselves give an `o(B^2)` exact
first-witness operator.

## 5. Exact subset-resultant descent is conditional, not expensive by itself

For squarefree split polynomials, a node product `M_I` and target polynomial
`C_Q` share a root exactly when their resultant vanishes. An exact node oracle
therefore supports a binary root-to-leaf witness self-reduction in
`O(log |I|)` oracle calls. This is an elementary gcd/resultant consequence.

The unresolved cost is constructing or specializing the oracle. Materializing
`C_Q` emits `Theta(B^3)` coefficients; evaluating every D2 leaf emits
`Theta(B^2)` values. The self-reduction changes neither output unless an exact
implicit operator is supplied.

Preprocessed kSUM and 3SUM-indexing data structures confirm that witness-returning
queries can be studied separately from enumeration, but their models and
integer modular maps do not automatically transfer to a prime-order EC group.

- Tsvi Kopelowitz and Ely Porat, *The Strong 3SUM-INDEXING Conjecture is
  False*: https://arxiv.org/abs/1907.11206
- Alexander Golovnev, Siyao Guo, Thibaut Horel, Sunoo Park, and Vinod
  Vaikuntanathan, *Data Structures Meet Cryptography: 3SUM with Preprocessing*:
  https://arxiv.org/abs/1907.08355
- Itai Dinur and Alexander Golovnev, *Improved Time-Space Tradeoffs for
  3SUM-Indexing*: https://arxiv.org/abs/2512.04258

## 6. Structured linear algebra is a conditional mechanism

Fast algorithms exist for matrices already proved to be Toeplitz-like,
Hankel-like, block-Krylov, or low-displacement. Pernet, Signargout, Karpman, and
Villard give subquadratic characteristic-polynomial algorithms under explicit
structured-matrix and genericity hypotheses, motivated in part by bivariate
resultant computation.

- Clement Pernet, Hippolyte Signargout, Pierre Karpman, and Gilles Villard,
  *Computing the Characteristic Polynomial of Generic Toeplitz-like and
  Hankel-like Matrices*: https://arxiv.org/abs/2104.02497

**Consequence.** This supports the algorithmic toolbox in the subset-norm
preflight, but not its central premise. The coordinate-translated D3 node
operator still needs an explicit displacement equation and rank bound. Full
rank does not preclude short displacement generators; low ordinary rank is not
the required property.

Bostan, Jeannerod, Mouilleron, and Schost show that a supplied displacement
generator of length `alpha` can represent an `N` by `N` structured matrix in
`O(N*alpha)` elements. This compresses a quadratic matrix, not an explicit
`N`-value target output. Villard's generic bivariate resultant algorithm and
Kaltofen-Villard block-Krylov determinant machinery likewise become relevant
only after a valid small generator and specialization map are derived.

- Alin Bostan, Claude-Pierre Jeannerod, Christophe Mouilleron, and Eric Schost,
  *On Matrices with Displacement Structure*: https://mathexp.eu/bostan/publications/BoJeMoSc17.pdf
- Gilles Villard, *On Computing the Resultant of Generic Bivariate
  Polynomials*: https://perso.ens-lyon.fr/gilles.villard/BIBLIOGRAPHIE/PDF/vil18.pdf
- Erich Kaltofen and Gilles Villard, *On the Complexity of Computing
  Determinants*: https://doi.org/10.1007/s00037-004-0185-3

## 7. Fixed-group preprocessing must remain a separate claim

Corrigan-Gibbs and Kogan prove that a generic prime-order DLP algorithm with
`S` bits of group-specific advice, online time `T`, and success probability
`epsilon` satisfies

```text
S*T^2 = Omega(epsilon*n).
```

The bound is tight up to logarithmic factors, and Rotem-Segev provide a fully
constructive matching algorithm in the model. These theorems concern arbitrary
target DLP, not a five-term relation oracle.

- Henry Corrigan-Gibbs and Dmitry Kogan, *The Discrete-Logarithm Problem with
  Preprocessing*: https://people.eecs.berkeley.edu/~henrycg/pubs/eurocrypt18discrete/
- Lior Rotem and Gil Segev, *A Fully-Constructive Discrete-Logarithm
  Preprocessing Algorithm with an Optimal Time-Space Tradeoff*:
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2022.12

The 2026 structured generic-group model adds a route for formalizing partial
non-generic structure, but a coordinate predicate, recursive circuit, or
subset-norm operator must first be embedded in its precise partial-operation
model.

- Henry Corrigan-Gibbs, Alexandra Henzinger, and David J. Wu, *The Structured
  Generic-Group Model*: https://people.eecs.berkeley.edu/~henrycg/pubs/structured-generic-groups/

**Consequence.** A Tier A subset tree may be a meaningful fixed-curve online
result even with `Theta(B^3)` advice. It is not a one-instance exponent result,
and the generic preprocessing ratio becomes a cryptanalytic comparison only
after relation collection, rank, sparse linear algebra, descent, and
arbitrary-target recovery share the same boundary.

## Novelty and priority assessment

1. **Bounded-source exact circuit:** closest to the explicit PKM open problem,
   but currently has no positive lattice inequality. Priority is the symbolic
   shift and determinant census, not implementation.
2. **Subset-norm tree:** exact self-reduction is routine; the potentially new
   object is a compact, exact, witness-lifting root-node operator. Priority is
   one displacement equation at the root, not a tree benchmark.
3. **Multipoint evaluation:** mandatory positive control and reusable primitive,
   but full-vector output prevents it from satisfying either core hypothesis.
4. **Fixed-curve preprocessing:** report as its own attack class. A strong
   online exponent with large advice can matter operationally without being a
   generic ECDLP break.

## Next concrete action

For the generalized-root lane, derive one explicit shift family and evaluate its
slack exponent at `B=p^(1/5)`. In parallel, write the root-node translated-D3
operator over the registered quadratic point encoding and attempt one exact
displacement equation. Neither task authorizes solver implementation.
