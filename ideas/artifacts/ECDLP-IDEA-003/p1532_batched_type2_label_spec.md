# P1532 row-preserving batched type-2 label specification

## Record status

- Candidate root: `ECDLP-IDEA-003`
- Focus experiment: `P1532`
- Expansion of: `P1531`
- Artifact class: theorem-only producer specification and operation screen
- Decision: `SCOPED_NO_PASS__OPEN_ROW_PRESERVING_BATCH_TRANSFER`
- Evidence scale: exact batch interface and asymptotic controls; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

P1532 changes the unit of work. P1531 charged one Cauchy orbit label at a time, while
Gallant's type-2 algorithm asks for two public, highly structured batches. A joint
algorithm may share work across these queries even if no single label has query exponent
below `alpha/2`. The required output remains the complete vector of row labels; one
global product, aggregate checksum, or collision-only predicate is insufficient.

## Bound predecessor

- `ideas/artifacts/ECDLP-IDEA-003/p1531_r1_independent_audit.md`
  - Decision:
    `INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__RERANK_BATCHED_TYPE2`

The predecessor independently verifies the three-trace separator, Gallant type-2 cost,
square-root Velu boundary, elliptic Fourier/type-1 normal form, and isogeny noncollapse
gate. P1532 must preserve all of them.

## Parameter and label interface

Let

```text
E/F_p ordinary,                  G=<P>, |G|=ell prime,
Q=[x]P,                          x unknown,
ell-1=A*D,                       gcd(A,D)=1,
A=ell^(1-alpha+o(1)),            D=ell^(alpha+o(1)),
H=<b> <= F_ell^*,                |H|=D, -1 in H,
<a> <= F_ell^*,                  |<a>|=A,
K=ceil(sqrt(A)).
```

For three public independent `c_1,c_2,c_3 in F_p`, use the P1531 tagged label

```text
L(R)=(L_(c_1)(R),L_(c_2)(R),L_(c_3)(R)),
L_c(R)=sum_(h in H/{+1,-1}) 1/(c-x([h]R)),
```

with `POLE` in the corresponding coordinate when a denominator vanishes. One public
setup is used for every row.

## Exact Gallant batch

Gallant's outer type-2 collision stage requires

```text
BASE[i]   = L([a^(i*K)]P),       0<=i<K,
TARGET[j] = L([a^(-j)]Q),        0<=j<K.
```

Equality of one base and target label identifies two points in the same `H` orbit. The
subsequent inner search costs `D^(1/2+o(1))` group operations and final scalar
verification checks the recovered logarithm.

A passing evaluator must return all `K` tagged triples in their original row order for
both batches. Hashing, sorting, or streaming rows is allowed if exact collision recovery
and source indices are retained. A product over all rows is not enough.

## Batch cost rectangle

Let

```text
c_B = exponent for the complete target-independent BASE batch and public setup,
b_B = exponent for the complete challenge-dependent TARGET batch,
m_B = peak state exponent for setup, batch evaluation, and collision recovery.
```

The full type-2 path then has

```text
lambda_B=max(c_B,b_B,(1-alpha)/2,alpha/2,final verification),
mu_B=max(m_B,(1-alpha)/2,alpha/2)
```

before an explicitly justified low-memory collision variant. Strict sub-rho time
requires

```text
c_B<1/2,                         b_B<1/2.
```

At `alpha=1/2`, the focus promotion cap additionally requires

```text
c_B<=0.45,                       b_B<=0.45,
mu_B<=0.30.
```

The `K` output rows themselves have exponent `(1-alpha)/2`; any memory claim below
that must stream them into a hash, sort, or low-memory collision procedure and charge
the replay cost.

## Baseline controls

### Direct rows

Evaluating every trace term independently touches `K*D` scalar-orbit points per batch:

```text
c_direct=b_direct=(1-alpha)/2+alpha=(1+alpha)/2>1/2.
```

Batch inversion, shared public constants, and simultaneous scalar multiplication save
constants or logarithms, not the exponent of the row-term traffic.

### Independent square-root Velu rows

Grant that every row scalar set has a favorable additive index system and that automatic
differentiation returns its logarithmic derivative with constant overhead. One row then
costs `D^(1/2+o(1))`, but `K` independent rows cost

```text
(1-alpha)/2+alpha/2=1/2+o(1).
```

This is exactly rho and is a control, not a passing evaluator.

### Union product

Let `S=union_i a^(i*K)H` for the base side, or
`S=union_j a^(-j)H` for the target side. Computing

```text
product_(s in S)(c-x([s]R))
```

returns only the product of all row orbit polynomials. Its logarithmic derivative is the
sum of all row traces. Neither object identifies which row supplied a collision.
Factoring the global object back into its `K` rows, or evaluating `K` row selectors,
must be charged.

### Product-ring packing

Packing the rows into orthogonal idempotents of `F_p^K` and running one square-root
Velu circuit performs each coefficient-ring operation as `K` base-field operations.
It reproduces the independent-row exponent `1/2`; writing a product-ring operation as
unit cost is invalid.

### Fourier row tags

Tagging quotient rows by roots of unity and applying a DFT decomposes the batch into
elliptic Fourier modes. A nonzero normalized mode transforms as `chi(x)^(-1)` and is a
Gallant type-1 distinguisher. Computing all modes materializes at least the row count,
while universal order powers erase the hidden character orientation. This route is
bound to the P1531 Fourier gate.

## Quantitative target

The batch contains

```text
N_batch=K*D=ell^((1+alpha)/2+o(1))
```

individual orbit terms. A row-preserving algorithm quasi-linear in
`sqrt(N_batch)` would have

```text
c_B,b_B <= (1+alpha)/4+o(1).
```

At `alpha=1/2`, this is `3/8+o(1)`, leaving a real gap below rho. This is a target,
not an achieved bound. The algorithm must explain how row boundaries survive the
aggregation; a square-root algorithm for the union product does not meet it.

## Generating-polynomial normal form

For one trace coordinate, define the row generating polynomials

```text
G_BASE,c(Y)   = sum_(i=0)^(K-1) L_c([a^(i*K)]P) Y^i,
G_TARGET,c(Y) = sum_(j=0)^(K-1) L_c([a^(-j)]Q) Y^j.
```

A passing operation may return these six degree-`K-1` polynomials, because their
coefficients are exactly the required row labels. It must construct them directly from
the public curve, point, subgroup generators, and three constants with `c_B,b_B<1/2`.

The following are not passing constructions:

1. Interpolating the coefficients after evaluating every row.
2. Returning only `G(1)`, a norm, a determinant, or a global resultant.
3. Supplying a degree-`K*D` eliminant and charging only its final multipoint evaluation.
4. Using a known toy logarithm or target-specific row permutation.
5. Hiding `K` independent coefficient-ring operations in one symbolic operation.

## Admitted operation classes

### Transposed elliptic resultant

Derive a resultant or power-projection identity that keeps a formal row variable `Y`
through the scalar-orbit aggregation and emits the degree-`K-1` generating polynomial.
Every intermediate degree, resultant, denominator, pole branch, and source inverse must
be bounded. A determinant with dimension `Omega(K*sqrt(D))` is the rho control.

### Quotient q-holonomic recurrence

Derive a target-independent recurrence in the row index for

```text
U_j=L_c([a^j]R).
```

The recurrence must be biconditional on the rational prime subgroup and have order,
coefficient construction, and initial-state cost small enough to emit the required `K`
rows with `c_B,b_B<1/2`. An order-`D`, degree-`D`, or `D`-initial-value recurrence is
the direct control. Citing a generic q-holonomic N-th-term algorithm, whose published
arithmetic cost is quasi-square-root in its index, is not an ECDLP recurrence.

### Batched summation-polynomial elimination

Retain the row tag through Semaev elimination and output all three generating
polynomials, with exact exclusion of false branches, repeated roots, vertical pairs,
poles, and points outside `G`. A relation variety containing all `K*D` point chains is
not an evaluator.

### Nonhomomorphic cyclic-algebra trace

Give a compact encoder of the row-indexed scalar orbit into a cyclic or split algebra
whose trace emits the row coefficients without materializing the `(ell-1)/2`-dimensional
prime-subgroup coordinate algebra. Homomorphic FFE encoders retain the P1531
degree-divisibility gate, and isogenies nonzero on `G` retain the noncollapse theorem.

## Controls and falsification gates

Reject a proposed batch operation on the first applicable condition:

1. It outputs an aggregate but not the `K` row labels with source indices.
2. Setup or target work has exponent at least `1/2`.
3. Peak state exceeds the claimed cap after row storage and collision recovery.
4. It materializes `K*D` points, a degree-`K*D` polynomial, or an equivalent dense
   algebra.
5. It is `K` independent square-root Velu, q-factorial, or orbit-product calls.
6. It normalizes an elliptic Fourier mode and therefore assumes the missing type-1
   character orientation.
7. It uses an isogeny or homomorphism to collapse a multiplicative scalar orbit.
8. It omits divisor-family applicability, bad-setup handling, inner orbit recovery, or
   final `[x]P=Q` verification.

## Primary-source boundary

- Gallant's type-2 query batches:
  <https://eprint.iacr.org/2010/370.pdf>
- Square-root elliptic polynomial evaluation:
  <https://arxiv.org/pdf/2003.10118>
- Square-root q-holonomic product algorithms:
  <https://arxiv.org/abs/2012.08656>
- Universal elliptic Gauss sums and orientation-free powers:
  <https://arxiv.org/pdf/1707.08610>

The batch cost model and row-preserving generating-polynomial target are
`novelty-unverified`. No primary source found in the producer search supplies this exact
ECDLP transfer operation.

## Decision

No admitted construction currently emits the complete structured Gallant label batch
with `c_B,b_B<1/2`.

- Direct rows cost `K*D`.
- Independent square-root Velu rows reach rho exactly.
- A union product loses row identity.
- Product-ring packing pays one base-field operation per row.
- Fourier tags reduce to type-1 hidden-scalar characters.
- No low-order quotient recurrence or row-preserving transposed resultant is supplied.

The scoped disposition is

```text
SCOPED_NO_PASS__OPEN_ROW_PRESERVING_BATCH_TRANSFER
```

Exactly one next action: independently audit this batch cost model and either derive one
explicit row-preserving generating-polynomial recurrence or transposed resultant with
`c_B,b_B<1/2` and complete state, applicability, collision, and recovery costs, or sign
a scoped no-candidate disposition. Do not authorize a contract, solver, or toy fixture.

This specification is not an ECDLP algorithm, a generic-order result, a Shoup-bound
improvement, or a breakthrough.
