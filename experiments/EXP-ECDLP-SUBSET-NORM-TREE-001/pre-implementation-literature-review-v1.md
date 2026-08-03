# Pre-implementation literature review v1

## Handoff: implicit compatibility operator boundary

### Claim or task

Determine whether primary literature already supplies an exact,
witness-preserving, sub-`|D2|`-state operator for fixed-curve `D2+D3`
compatibility.

### Status

`OPEN`, `NOVELTY-UNVERIFIED`: no exact match was found in the searched primary
literature. This is a literature-search boundary, not an impossibility theorem
or a novelty proof.

### Assumptions

- The regime is five-term decomposition with `B approximately p^(1/5)`,
  `N2=Theta(B^2)`, and `N3=Theta(B^3)` only when measured supports are
  collision-light.
- Arithmetic is exact over `F_p` or a registered finite extension.
- A valid witness contains five signed public source identifiers, not only
  coordinates or an x-orbit.
- Target-independent preprocessing, target-specific state and work, and target
  batching are charged separately.
- Resultant predicates include poles, identity, inverse, doubling, multiplicity,
  orientation, and terminal provenance.

### Evidence so far

No located construction simultaneously:

1. avoids materializing `C_Q` and an `N2`-value target profile;
2. uses `o(N2)` target-specific work and resident state;
3. restricts exactly and cheaply to both children at every product-tree node;
4. returns signed D2 and D3 source identifiers; and
5. charges fixed-curve preprocessing and terminal witness lift.

#### Exact generalized-root and EC eliminant prior art

- Petit, Kosters, and Messeng, [Algebraic Approaches for the Elliptic Curve
  Discrete Logarithm Problem over Prime
  Fields](https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf), PKC
  2016, DOI `10.1007/978-3-662-49387-8_1`. They define composed rational-map
  factor bases and explicitly leave a dedicated non-Groebner generalized-root
  algorithm and its asymptotic cost open.
- Semaev, [Summation Polynomials and the Discrete Logarithm Problem on Elliptic
  Curves](https://eprint.iacr.org/2004/031), ePrint 2004/031. Summation-polynomial
  vanishing is an exact coordinate-lift characterization; it does not supply a
  sub-`B^2` relation finder.
- Jochemsz and May, [A Strategy for Finding Roots of Multivariate
  Polynomials](https://www.iacr.org/archive/asiacrypt2006/42840270/42840270.pdf),
  ASIACRYPT 2006, DOI `10.1007/11935230_18`. The general multivariate lattice
  strategy relies on algebraic-independence and short-vector heuristics. It is
  not a theorem for the EC addition circuit.

#### Explicit-output evaluation and composition

- Delaplace and May, [Can We Beat the Square Root Bound for ECDLP over
  F_(p^2) via Representations?](https://eprint.iacr.org/2019/800.pdf), ePrint
  2019/800. Their Zero-Join routine returns all zero pairs, and the ECDLP cost
  uses a distribution heuristic. Replacing full multievaluation by a cheaper
  zero test is explicitly left open.
- Nuesken and Ziegler, [Fast Multipoint Evaluation of Bivariate
  Polynomials](https://arxiv.org/abs/cs/0403022), ESA 2004, DOI
  `10.1007/978-3-540-30140-0_49`. The algorithm emits the complete evaluation
  vector.
- Giorgi, Grenet, and Roche, [Fast In-place Algorithms for Polynomial
  Operations](https://arxiv.org/abs/2002.10304), ISSAC 2020, DOI
  `10.1145/3373207.3404061`. Constant extra workspace does not remove the
  preallocated `N`-element multipoint output.
- Neiger, Salvy, Schost, and Villard, [Faster Modular
  Composition](https://cs.uwaterloo.ca/~eschost/publications/NSSV24.pdf), JACM
  71(2), 2024, DOI `10.1145/3638349`. The dense interface returns a degree-`<N`
  polynomial, hence `N` coefficients.
- Neiger, Rosenkilde, and Solomatov, [Generic Bivariate Multi-point Evaluation,
  Interpolation and Modular Composition with
  Precomputation](https://arxiv.org/abs/2003.12468), ISSAC 2020, DOI
  `10.1145/3373207.3404032`. Balanced fixed inputs admit charged preprocessing
  and quasilinear online work, but the interface still returns `N` evaluations
  or an `N`-coefficient remainder.

#### Transposition, resultants, and structured linear algebra

- Bostan, Lecerf, and Schost, [Tellegen's Principle into
  Practice](https://specfun.inria.fr/bostan/publications/BoLeSc03.pdf), ISSAC
  2003, DOI `10.1145/860854.860870`. Transposition preserves linear-map circuit
  complexity. Existential zero-OR, gcd selection, and witness extraction are
  nonlinear and are not supplied by the theorem.
- Borodin and Moenck, [Fast Modular
  Transforms](https://doi.org/10.1016/S0022-0000(74)80029-2), JCSS 8(3), 1974,
  and Moenck, [Fast Computation of
  GCDs](https://doi.org/10.1145/800125.804045), STOC 1973. These establish exact
  product/remainder-tree, CRT, evaluation, interpolation, and fast-GCD
  primitives when their polynomial operands are explicit.
- Villard, [On Computing the Resultant of Generic Bivariate
  Polynomials](https://perso.ens-lyon.fr/gilles.villard/BIBLIOGRAPHIE/PDF/vil18.pdf),
  ISSAC 2018, DOI `10.1145/3208976.3209020`. Generic Sylvester structure,
  selected inverse blocks, and approximant reconstruction accelerate full
  resultant computation; the theorem does not establish genericity, hereditary
  generators, or signed provenance for this EC specialization.
- Bostan, Jeannerod, Mouilleron, and Schost, [On Matrices with Displacement
  Structure](https://mathexp.eu/bostan/publications/BoJeMoSc17.pdf), SIAM J.
  Matrix Anal. Appl. 38(3), 2017, DOI `10.1137/16M1062855`. A supplied
  displacement generator of length `alpha` represents an `N x N` matrix using
  `O(N*alpha)` elements. This compresses a quadratic matrix, not an explicit
  `N`-value output, and no cited result proves small `alpha` here.
- Jeannerod, Neiger, and Villard, [Fast Computation of Approximant Bases in
  Canonical Form](https://arxiv.org/abs/1801.04553), J. Symbolic Computation 98,
  2020, DOI `10.1016/j.jsc.2019.07.011`. This is an exact module engine only
  after a small approximant instance has been derived.
- Kaltofen and Villard, [On the Complexity of Computing
  Determinants](https://repository.lib.ncsu.edu/bitstreams/380e186d-b9f9-4e65-82f4-2f45f9a67e81/download),
  Computational Complexity 13, 2004, DOI `10.1007/s00037-004-0185-3`. Block
  Krylov and block-Hankel generators support exact randomized determinant
  algorithms, but do not prove a short generator for the translated EC operator.
- Andrews and Wigderson, [Constant-Depth Arithmetic Circuits for Linear Algebra
  Problems](https://ieee-focs.org/FOCS-2024-Papers/pdfs/FOCS2024-1oojWxXs5YAKfs3z3lBRMF/167400c367/167400c367.pdf),
  FOCS 2024, DOI `10.1109/FOCS61266.2024.00138`. Polynomial-size constant-depth
  resultant and piecewise-GCD circuits do not imply sublinear sequential work,
  sublinear state, implicit coefficient access, or witness extraction.

#### Witness-returning preprocessing models

- Golovnev, Guo, Horel, Park, and Vaikuntanathan, [Data Structures Meet
  Cryptography: 3SUM with Preprocessing](https://arxiv.org/abs/1907.08355), STOC
  2020, DOI `10.1145/3357713.3384342`. Their kSUM-indexing model genuinely
  returns source indices, but allows computationally unbounded preprocessing and
  measures probes to advice rather than charged EC arithmetic. It is an analogy,
  not an ECDLP complexity transfer.

#### Exact self-reduction and its unresolved oracle

For a D2 node `I`,

```text
M_I(Z) = product_(R in I) (Z-enc(R))
C_Q(Z) = product_(S in D3) (Z-enc(Q-S)).
```

For monic `M_I`, exact resultant identities give

```text
Norm_(K[Z]/(M_I)/K)(C_Q mod M_I)
  = Res(M_I,C_Q)
  = product_(R in I) C_Q(enc(R)),

Res(M_I,C_Q)=0 iff deg(gcd(M_I,C_Q))>0.
```

For `I=I_0 disjoint-union I_1`, the resultant factors across the children.
Thus an exact node oracle yields a D2 leaf in `ceil(log2(N2))` oracle calls. The
call count is not an arithmetic bound: constructing, specializing, restricting,
and certifying the oracle remains unresolved, and a D2 leaf alone does not
provide its signed D3 source IDs.

#### Precise open interface

The missing theorem or algorithm is:

> From fixed-curve advice of size `o(B^3)` and target `Q`, construct in
> `o(B^2)` work and target-resident state an exact representation of
> `C_Q mod M_D2`, or directly `Res(M_D2,C_Q)`, without constructing `C_Q` or its
> `B^2` evaluations; restrict it efficiently to both child moduli and recover
> five signed public source identifiers.

No cited source proves low displacement rank for the target translation, a
sub-`B^2` target-dependent generator, hereditary child restriction, or exact D3
provenance at the terminal root.

### Failure modes

- Treating an explicit open problem as an existing generalized-root solver.
- Confusing `O(1)` extra workspace with `o(N)` total output representation.
- Applying transposition to a nonlinear existential predicate.
- Counting logarithmic oracle calls without charging oracle specialization.
- Treating low ordinary rank, low displacement rank, and short target state as
  interchangeable.
- Returning an x-coordinate or common root without signed source identifiers.
- Hiding `C_Q`, an `N2`-value vector, or unbounded preprocessing in advice.

### Next concrete action

Write the exact root-node translated-D3 remainder or norm map over the oriented
quadratic encoding and derive or refute one displacement equation. Reject that
operator family at the root if target specialization emits `Theta(B^2)` values,
materializes `C_Q`, or lacks a signed terminal witness.

### Artifact paths

- `theory.md`
- `contract.md`
- `object-dimension-ledger.md`
- `../../notes/ecdlp_generalized_root_subset_norm_literature_20260718.md`
