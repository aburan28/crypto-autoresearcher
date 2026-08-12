# Direct five-source TT literature review v2

## Handoff: corrected exact finite-field zero-witness literature boundary

### Claim or task

Correct the attribution scopes in `literature-review-v1.md`, add the closest
EC-specific primary prior art, and assess whether any source supplies the
compact exact compiler required by frozen v4.

### Status

`OPEN`, `NOVELTY-UNVERIFIED`, with `RESTRICTED THEOREM` negative boundaries.

This v2 supersedes the attribution and search-scope statements in v1. It does
not alter the frozen v4 mathematics or accounting. No implementation,
experiment, novelty claim, or ECDLP improvement is authorized.

Frozen sources:

- `preflight-v4.md` SHA256
  `f07363f317e1ec0fc1b3e759a782ada43909591a9e53269a51e16d21e0d8fcf0`.
- `object-dimension-ledger-v4.md` SHA256
  `48cb902701223bda3413e4360736cb38872b2974e38f42b2a76a98e0bfe6e23f`.
- Historical `literature-review-v1.md` SHA256
  `f51c39ca51716e145edf1097b2cd72d0ffa6d8fecf7ed3a3c9497fba4b32504c`.

### Assumptions

- Exact TT means a materialized tensor train over the stated field and mode
  order. Implicit circuits and sparse support programs are separate objects.
- A repository derivation is labeled as such even when it follows from a cited
  theorem.
- Real- or complex-field genericity is not transferred to finite fields.
- A bounded no-match search cannot establish novelty.

### Evidence so far

#### Exact normalization and location after cores exist

Vilmart's current 2026 preprint gives an exact arbitrary-field TT normal form.
Proposition 18 returns a leading index and value in `O(d*n*r)` after the first
sweep. The sweep, construction of the indicator TT, and all intermediate
Hadamard ranks remain separate charged resources.

Primary source:

- Renaud Vilmart, "A Unique Normal Form for Tensor Trains over Arbitrary
  Fields," arXiv:2607.06271, 2026,
  <https://arxiv.org/abs/2607.06271>.

Minimal exact TT bond rank equals the corresponding unfolding rank by exact
rank factorization over a field. Oseledets gives the standard TT framework and
SVD construction over real/complex fields; arbitrary-field scope here is an
algebraic inference supported by Vilmart, not a finite-field theorem quoted
from Oseledets.

Primary source:

- Ivan V. Oseledets, "Tensor-Train Decomposition," *SIAM Journal on
  Scientific Computing* 33(5), 2011,
  <https://doi.org/10.1137/090752286>.

#### Weighted-automaton route is a repository derivation

Crosswhite and Bacon connect matrix-product algorithms with complex-weighted
finite automata. Droste and Kuich discuss recognizable series and support over
finite semirings. The exact expansion retaining every reachable prefix row in
`F_q^r`, its `q^r` state cap, and the displayed work bound in v1 are repository
derivations. Neither source states that finite-field TT zero-locator theorem.

Primary sources:

- Gregory M. Crosswhite and Dave Bacon, "Finite automata for caching in matrix
  product algorithms," *Physical Review A* 78, 012356, 2008,
  <https://doi.org/10.1103/PhysRevA.78.012356>.
- Manfred Droste and Werner Kuich, "Undecidability of the universal support
  problem for weighted automata over zero-sum-free commutative semirings,"
  *Theoretical Computer Science* 1002, 114599, 2024,
  <https://doi.org/10.1016/j.tcs.2024.114599>.

The repository expansion is exact but grows with the field and supplies no
sub-`B^2` bound here.

#### Hadamard-power rank boundaries

Alon's Lemma 9.2 gives the symmetric-power upper-bound mechanism. Its proof is
field-independent; applying it over an arbitrary field is an extension of the
proof, not a separately stated finite-field theorem in that paper.

Damm and Dietrich prove generic attainment for real matrices. It is evidence
that the bound can be sharp over the reals, not a finite-field or all-
characteristic result.

Smith proves the `p`-rank formula for projective point-hyperplane incidence
matrices. Constructing a low-rank point-hyperplane evaluation matrix and
turning it into incidence by `1-a^(q-1)` is a repository synthesis using that
formula.

Primary sources:

- Noga Alon, "Problems and Results in Extremal Combinatorics I,"
  *Discrete Mathematics* 273, 2003,
  <https://doi.org/10.1016/S0012-365X(03)00227-9>.
- Tobias Damm and Nicolas Dietrich, "Hadamard Powers and Kernel Perceptrons,"
  *Linear Algebra and its Applications* 672, 2023,
  <https://doi.org/10.1016/j.laa.2023.04.020>.
- K. J. C. Smith, "On the p-rank of the incidence matrix of points and
  hyperplanes in a finite projective geometry," *Journal of Combinatorial
  Theory* 7(2), 1969,
  <https://doi.org/10.1016/S0021-9800(69)80046-3>.

Frobenius powers of a TT preserve its displayed bond dimensions by applying
Frobenius to each core. Products of those powers are Hadamard products and
have no corresponding rank-preservation theorem.

#### Valid repository five-mode obstruction

For mode order `(i1,i2,i3,i4,i5)`, indices in `[0,B)`, and prime `p>B^2`, let

```text
g=i1+B*i2-i3-B*i4.
```

This scalar has a TT of rank at most two. Its exact Fermat indicator is

```text
1-g^(p-1)=delta_(i1,i3)*delta_(i2,i4).
```

The central unfolding is `I_(B^2) tensor 1_(1 by B)` and has rank exactly
`B^2`. Reordering to `(i1,i3,i2,i4,i5)` lowers the maximum rank to `B`.

This is a valid repository-derived `RESTRICTED THEOREM`: no universal compiler
can map every constant-rank input in that fixed order to a subquadratic-rank
Fermat indicator. It does not prove high rank for the RCB-derived `g_Q`, every
mode order, implicit circuits, sparse cores, or non-TT locators.

Andrews et al. give a characteristic-zero non-closure-under-powering result
for read-once oblivious algebraic branching programs. It is an analogy only,
not a finite-field TT theorem.

Primary source:

- Robert Andrews et al., "On Closure Properties of Read-Once Oblivious
  Algebraic Branching Programs," ITCS 2026,
  <https://doi.org/10.4230/LIPIcs.ITCS.2026.9>.

#### Closest EC-specific primary prior art

Renes, Costello, and Batina are the exact provenance for the complete
short-Weierstrass projective addition circuit bound by v4. Their formula is
complete under its stated curve/subgroup and characteristic conditions. It
does not analyze TT ranks or a five-source Fermat indicator.

- Joost Renes, Craig Costello, and Lejla Batina, "Complete Addition Formulas
  for Prime Order Elliptic Curves," EUROCRYPT 2016,
  <https://doi.org/10.1007/978-3-662-49890-3_16>.

Semaev establishes exact summation-polynomial zero semantics and recursive
resultant construction. Those polynomials encode existence through
coordinates; they do not automatically retain the signed public identifiers
required by v4 or give a batched sub-`B^2` witness locator.

- Igor Semaev, "Summation Polynomials and the Discrete Logarithm Problem on
  Elliptic Curves," IACR ePrint 2004/031,
  <https://eprint.iacr.org/2004/031.pdf>.

Petit, Kosters, and Messeng give composed rational-map factor bases and leave
dedicated generalized root finding as an open algorithmic direction. This is
nearby representation work, not the direct complete-addition TT compiler.

- Christophe Petit, Michiel Kosters, and Ange Messeng, "Algebraic Approaches
  for the Elliptic Curve Discrete Logarithm Problem over Prime Fields," PKC
  2016, <https://doi.org/10.1007/978-3-662-49387-8_1>.

Delaplace and May give the closest exact list zero-test comparator: form a
product polynomial, evaluate it on a second list, and recover zero pairs for
an extension-field ECDLP representation. The method evaluates the complete
second list and does not directly provide an ordinary-prime-field five-mode
TT construction below the current output boundary.

- Claire Delaplace and Alexander May, "Can We Beat the Square Root Bound for
  ECDLP over F_(p^2) via Representation?" *Journal of Mathematical
  Cryptology* 14(1), 2020,
  <https://doi.org/10.1515/jmc-2019-0025>.

Amadori, Pintore, and Sala study prime-field point-decomposition systems,
including five-term experiments. They do not give an exact batched sub-`B^2`
locator or an intermediate TT-rank theorem for the present circuit.

- Alessandro Amadori, Federico Pintore, and Massimiliano Sala, "On the
  Discrete Logarithm Problem for Prime-Field Elliptic Curves," *Finite Fields
  and Their Applications* 51, 2018,
  <https://doi.org/10.1016/j.ffa.2018.01.009>.

#### Precise open gap

No source reviewed here supplies for the actual bound RCB equality scalar:

- a constructible exact TT for `1-g_Q^(p^2-1)` with every target resource
  strict `o(B^2)`;
- controlled intermediate ranks through norm and Fermat powering;
- charged fixed-curve preprocessing and resident advice strict `o(B^3)`;
- exact five-identifier recovery and negative certification;
- a coordinate-specific dense-minor theorem that closes this route.

This no-match statement records the bounded search only. Novelty remains
unverified.

### Failure modes

- Treating the generic five-mode obstruction as EC-specific.
- Attributing repository automaton or incidence constructions to source
  theorems.
- Transferring real-generic rank attainment to finite fields.
- Treating Vilmart's post-sweep locator as construction of the indicator TT.
- Treating summation-polynomial existence semantics as signed witness
  recovery.
- Calling a bounded no-match search evidence of novelty.

### Next concrete action

Audit this v2 against the two frozen v4 hashes; if attribution scope passes,
derive or refute the first norm-Hadamard central-rank certificate using the RCB
circuit as the exact primary-source-bound object.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v4.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v4.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/literature-review-v1.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/literature-review-v2.md`

