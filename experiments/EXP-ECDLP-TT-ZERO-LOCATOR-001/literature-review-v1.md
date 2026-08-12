# Direct five-source TT literature review v1

## Handoff: exact finite-field zero witnesses and rank boundary

### Claim or task

Determine whether primary literature gives an exact low-rank construction or
zero-witness algorithm for `h=1-g^(q-1)` when `g` is a constant-rank five-mode
tensor train over `F_q`.

### Status

`RESTRICTED THEOREM`, `OPEN`, `NOVELTY-UNVERIFIED`.

A universal bounded-rank construction is false in fixed five-mode order. No
exact primary-source match was found for the repository's direct elliptic
equality tensor through 2026-07-18. A coordinate-specific construction or rank
theorem remains open; this bounded search is not a novelty claim.

### Assumptions

- Arithmetic is exact over a finite field and every entry of `g` is a field
  scalar. The indicator identity is not transferred to a quotient ring with
  nilpotents without a separate scalar-reduction proof.
- TT rank is exact unfolding rank in the registered mode order.
- A succinct arithmetic circuit, finite-state support automaton, and
  materialized TT are different resident representations and are charged
  separately.
- The explicit counterexample below uses prime `p>B^2` and five modes of size
  `B`.

### Evidence so far

#### Exact nullity and leading-index extraction

Vilmart's 2026 arbitrary-field TT normal form supplies an exact first sweep,
zero-tensor test, and leading nonzero index. Proposition 18 returns the leading
index and coefficient of a nonzero first-swept order-`d` TT in `O(d*n*r)`,
where `n` is maximum mode size and `r` maximum rank. This solves witness
location only after a TT for the desired indicator has been constructed.

Primary source:

- Renaud Vilmart, [A Unique Normal Form for Tensor Trains over Arbitrary
  Fields](https://doi.org/10.48550/arXiv.2607.06271), arXiv:2607.06271, 2026.

Matrix-product states and weighted automata use the same matrix-product
mechanism. Over a finite semiring, support is effectively recognizable. A
direct exact state expansion can retain every reachable prefix row vector in
`F_q^(r_k)`, yielding at most `q^(r_k)` states and work bounded by

```text
O(sum_k n_k*q^(r_(k-1))*r_(k-1)*r_k).
```

This is exact but useless for the present growing-field sub-`B^2` gate without
additional structure.

Primary sources:

- Gregory M. Crosswhite and Dave Bacon, [Finite automata for caching in matrix
  product algorithms](https://doi.org/10.1103/PhysRevA.78.012356), *Physical
  Review A* 78, 012356, 2008.
- Manfred Droste and Werner Kuich, [Undecidability of the universal support
  problem for weighted automata over zero-sum-free commutative
  semirings](https://doi.org/10.1016/j.tcs.2024.114599), *Theoretical Computer
  Science* 1002, 114599, 2024.

#### Hadamard powers can grow exact rank

Exact TT bond ranks equal the ranks of the corresponding unfolding matrices.
If a matrix `A` has rank `r`, then over any field

```text
rank(A^circ-k)<=binom(r+k-1,k).
```

For a Fermat indicator this upper bound is already `q+1` when `r=2`; it is not
a compactness theorem. In characteristic zero, generic matrices attain the
symmetric-power bound up to ambient dimensions. Finite fields also exhibit
severe growth: a rank-`t+1` point--hyperplane evaluation matrix over
`F_(p^e)` becomes a projective incidence matrix after the `q-1` indicator,
whose `p`-rank is `binom(p+t-1,t)^e+1`.

Primary sources:

- Ivan V. Oseledets, [Tensor-Train
  Decomposition](https://doi.org/10.1137/090752286), *SIAM Journal on
  Scientific Computing* 33(5), 2295--2317, 2011.
- Noga Alon, [Problems and results in extremal combinatorics
  I](https://doi.org/10.1016/S0012-365X(03)00227-9), *Discrete Mathematics*
  273, 31--53, 2003, Lemma 9.2.
- Tobias Damm and Nicolas Dietrich, [Hadamard powers and kernel
  perceptrons](https://doi.org/10.1016/j.laa.2023.04.020), *Linear Algebra and
  its Applications* 672, 93--107, 2023.
- K. J. C. Smith, [On the p-rank of the incidence matrix of points and
  hyperplanes in a finite projective
  geometry](https://doi.org/10.1016/S0021-9800(69)80046-3), *Journal of
  Combinatorial Theory* 7(2), 122--129, 1969.

Frobenius powers alone preserve exact TT ranks: applying `x -> x^(p^j)` to
every core realizes `g^(p^j)` with the same bonds. The intervening Hadamard
products have no such guarantee.

#### Explicit five-mode obstruction

Fix mode order `(i1,i2,i3,i4,i5)`, with each index in `[0,B)`, over `F_p` for
`p>B^2`, and define

```text
g=i1+B*i2-i3-B*i4,
```

independent of `i5`. As a sum of five univariate functions, `g` has a standard
TT realization of rank at most two. Because both base-`B` integers lie in
`[0,B^2-1]`,

```text
g=0 iff (i1,i2)=(i3,i4).
```

Therefore

```text
h=1-g^(p-1)=delta_(i1,i3)*delta_(i2,i4).
```

Its `(i1,i2)|(i3,i4,i5)` unfolding is
`I_(B^2) tensor 1_(1 by B)` and has rank exactly `B^2`. Every exact TT for
`h` in this order has central bond at least `B^2`.

This repository-derived restricted counterexample proves that no universal
fixed-order TT compiler can map every constant-rank five-mode scalar to its
Fermat zero indicator while keeping all output ranks subquadratic. Reordering
the example lowers its maximum rank to `B`, so the theorem is mode-order-
specific and does not rule out a useful reordered or coordinate-specific
elliptic construction.

#### Precise open gap

No searched primary source supplies for the direct EC equality tensor:

- an exact TT for `1-g_Q^(p^2-1)` with proved sub-`B^2` construction;
- a scalar-circuit leading-zero algorithm with strict sub-`B^2` target work;
- a witness-preserving row-space basis for every intermediate power;
- an additive-expansion theorem proving a `B^2` nonsingular minor for the
  actual coordinate circuit.

Small arithmetic-circuit size does not imply small TT width. A 2026
characteristic-zero roABP closure result provides an adjacent representation-
gap theorem, but is only an analogy for these finite-field evaluation tensors.

Primary source:

- Robert Andrews et al., [On Closure Properties of Read-Once Oblivious
  Algebraic Branching
  Programs](https://doi.org/10.4230/LIPIcs.ITCS.2026.9), ITCS 2026.

### Failure modes

- Conflating `g` not identically zero with existence or absence of a zero
  entry.
- Charging only the `O(log q)` indicator circuit while omitting exact TT
  width, state, and witness extraction.
- Using numerical TT rounding in an exact finite-field contract.
- Treating real-generic rank theorems as finite-field results.
- Assuming Frobenius preserves ranks of products rather than individual
  Frobenius powers.
- Ignoring mode order in the explicit obstruction.
- Inferring a rank lower bound for the curve-derived tensor from generic
  counterexamples.
- Treating a bounded no-match literature search as novelty evidence.

### Next concrete action

Prove or refute that one actual intermediate in the bound RCB plus norm-
indicator circuit has central rank `o(B)`: either exhibit a witness-preserving
exact row-space basis and construction schedule, or construct an explicit
`B by B` nonsingular minor that triggers the dense-core `B^2` gate.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v2.md`
