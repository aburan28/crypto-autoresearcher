# ECDLP transfer audit: improved 3SUM-Indexing

Date: 2026-07-18

## Claim boundary

Status: `NEGATIVE RESULT` for a black-box transfer of the published data
structure to the exact `D2+D3=Q` fixed-curve query. The paper remains a useful
technique source for a coordinate-specific compiler. This note is paper-only,
uses no ECDLP implementation, and proves no lower bound for alternate EC
representations.

Primary source:

- Itai Dinur and Alexander Golovnev, "Improved Time-Space Tradeoffs for
  3SUM-Indexing," arXiv:2512.04258v2, 2026-04-23,
  <https://arxiv.org/abs/2512.04258>.

## Published theorem actually needed here

For two integer arrays of lengths `n<=m`, Theorem 5.1 gives, up to
polylogarithmic factors,

```text
S = O(n^(1.5-delta) m),
T = O(n^delta),
0 <= delta <= 1.
```

The algorithm returns a witness pair. Its stated preprocessing time is
quadratic in the one-list case and `O~(n*m)` in the asymmetric construction.
The result is therefore stronger than a decision-only oracle but does not make
offline construction free.

## Direct dimension substitution

For a collision-light five-term factor-base relation with `|F|=B`, the exact
balanced query has

```text
|D2| = Theta(B^2),
|D3| = Theta(B^3).
```

Set `n=|D2|=Theta(B^2)` and `m=|D3|=Theta(B^3)`. The theorem gives

```text
S = O~(B^(6-2*delta)),
T = O~(B^(2*delta)),
0 <= delta <= 1.
```

The smallest published advice exponent occurs at `delta=1`:

```text
S = O~(B^4),
T = O~(B^2).
```

Thus this direct substitution misses both strict targets for the current
fixed-curve program: advice below `B^3` and online work below `B^2`.

The symmetric `kSUM` route is no better. Applying Theorem 2 with six-sum
indexing on the original factor base gives

```text
S = O~(B^(5.5-delta)),
T = O~(B^delta),
0 <= delta <= 1,
```

so even `delta=1` retains `O~(B^4.5)` advice. Grouping as `F+D4` gives the same
exponents through the asymmetric theorem.

These substitutions reject only use of the theorem as a black-box compiler.
They are not lower bounds on a representation that avoids materializing `D3`
or exploits elliptic-coordinate structure inside the sub-functions.

## Why the integer algorithm is not an abelian-group black box

The pair-sum query itself makes sense in any abelian group, but the published
construction uses more than associativity and commutativity:

1. It draws random integer primes `p=O~(n)` and `q=O~(m)`.
2. It routes a query by `y mod q` and maps the sub-function output by `y mod p`.
3. For fixed residue `d`, it finds the first partner `b_j` satisfying
   `a_i+b_j=d mod q` by binary search in a list sorted by integer residues.
4. It bounds false residue collisions by counting prime divisors of nonzero
   integer differences.
5. It recovers and verifies the exact integer witness with a sorted-list
   lookup.

An ordinary prime-order EC subgroup has no nontrivial homomorphism onto the
small residue groups used by this splitter. Mapping a point to its unknown
scalar would solve the problem being studied. Coordinate hashes can be
computed, but they do not generally satisfy the additive partner-lookup law
needed for the sub-functions. Therefore the theorem does not currently
transfer to EC point addition as a black-box abelian-group result.

## Constructive lead that survives

The reusable idea is the sub-function decomposition, not the published
parameter substitution. An EC-specific successor would need maps

```text
h_q : E(F_p) -> [D],
h_p : E(F_p) -> [L],
```

plus a compact data structure that, for a fixed route `d` and source point
`A`, finds a source point `B` with `h_q(A+B)=d`, while preserving exact witness
recovery and bounding route collisions for every target history. A useful map
need not be a group homomorphism, but its partner query, collision law, advice,
construction cost, and traffic must all be proved.

Coordinate predicates, isogenous/model-transformed sets, or recursive source
labels are possible search spaces. A generic random hash is a negative control,
because it supplies no cheap partner lookup.

## Decision

Do not insert the Dinur-Golovnev theorem as an `O~(B^(3-epsilon))` fixed-curve
compiler. Record it as:

- an exact witness-bearing integer indexing upper bound;
- a scoped black-box transfer failure at the actual `D2/D3` dimensions;
- a technique source for designing EC-specific sub-functions.

## Handoff: coordinate sub-function successor

### Claim or task

Find an efficiently computable EC coordinate route whose partner query and
collision bounds replace the integer residue splitter without materializing
`D3`.

### Status

`OPEN`

### Assumptions

- Random ordinary prime-field curves and collision-light `D2/D3` sizes.
- Fixed curve and generator may be preprocessed, with all construction and
  advice charged.
- Exact signed witnesses and arbitrary target queries are required.

### Evidence so far

- The published asymmetric theorem returns witnesses.
- Its direct `D2/D3` substitution bottoms out at `O~(B^4)` advice and
  `O~(B^2)` online time.
- Its efficient sub-functions rely on integer modular residues and sorted
  partner lookup, which have no known prime-order EC analogue.

### Failure modes

- The route behaves as a random hash and requires scanning all partners.
- A small additive quotient is smuggled in through unknown scalar labels.
- Source-set storage or preprocessing recreates materialized `D3`.
- Route collisions or witness replay erase the advertised gain.

### Next concrete action

Write a paper preflight for one explicit coordinate route and derive its
partner-query, collision, advice, construction, traffic, and witness equations
before implementation.

### Artifact paths

- `notes/ecdlp_3sum_indexing_transfer_20260718.md`

