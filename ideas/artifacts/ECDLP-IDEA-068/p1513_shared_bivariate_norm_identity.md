# P1513 Shared Bivariate Norm-Remainder Identity

Status: `PREREGISTERED_IDENTITY_ONLY_COMMON_NORM_ALGORITHM_OPEN`

This receipt isolates the target-specialized nonlinear exception left by the
P1512 cycle-length gate. It is an exact algebraic identity and a complexity
obligation, not an algorithm, relation campaign, descent, or ECDLP break.

## Shared Universal Circuit

Let `F(X)=product_i (X-x_i)` encode the canonical factor-base x-coordinates.
With Semaev's third summation polynomial, define

```text
A_U(V)   = product_i S3(U,V,x_i),
B(V,W)   = product_j S3(V,W,x_j),
H(U,W)   = Res_V(A_U(V),B(V,W)).
```

P1510 resultant multiplicativity gives the source-markable circuit

```text
H(U,W) = product_(i,j) P_(i,j)(U,W),
P_(i,j)(U,W) = Res_V(S3(U,V,x_i),S3(V,W,x_j)).
```

There are exactly `r^2` constant-degree bivariate leaves. Unlike P1511's
expanded product grammar, the start or target coordinate `U` remains symbolic,
so this circuit is shared before any `Theta(r)` specializations.

Freeze a public target batch by

```text
T(U) = product_t (U-u_t),  degree(T)=Theta(r).
```

Then the target-side A2 support and factor-start A3 support are

```text
N_T(W) = Res_U(T(U),H(U,W)) = product_t H(u_t,W),
N_F(W) = Res_U(F(U),H(U,W)) = product_k H(x_k,W).
```

Their common squarefree factors are exactly the endpoint keys joining the A2
target batch to the A3 start batch, subject to the already frozen complete
addition charts and multiplicity policy. P1509/P1510 marker jets supply the two
within-`H` source indices. Independent target and start markers must additionally
recover `t` and `k`, yielding complete five-factor rows.

## Missing Operation

The required operation is

```text
common_norm(T,F,H)
    -> gcd(N_T,N_F) plus target/start/source jets
```

without materializing either norm or evaluating `H` at all roots of `T` and
`F`. On the frozen family:

```text
size(H circuit)        = Theta(r^2) leaves,
degree_W(N_T)          = Theta(r^3),
degree_W(N_F)          = Theta(r^3),
expected common output = Theta(r),
rho                    = Theta(r^(5/2)).
```

A passing algorithm must be output-sensitive in the common factor, not in the
two norm degrees. Its complete base-field work, coefficient traffic, marker
state, source splitting, and verification must be `o(r^(5/2))`.

## Distinctness Boundary

This is not P1511's closed circuit grammar. P1511 instantiated one `r^2`-leaf
P1510 product for each of `Theta(r)` starts or targets, giving `Theta(r^3)`
leaves before gcd. P1513 admits only the one `r^2`-leaf bivariate `H` circuit and
asks whether the two shared norms can be intersected without specialization.

This is not the rejected straight-line factor atomizer IDEA-106. Generic
factorization of `H`, `N_T`, or `N_F` is neither requested nor credited. The
output must be the common norm factors and their exact target, start, and four
within-transition source labels. A component factor without a source inverse
fails.

This is not P1512. No universal linear determinant may expose one independent
kernel atom for every five-source tuple. The computation is specialized to two
public degree-`r` selector polynomials and may emit only their common fibers.

## Phase 0 Obligation

Derive an exact common-norm algorithm in one of these equivalent forms:

1. a subresultant or Fitting operation on the fiber product
   `T(U)=F(V)=H(U,W)=H(V,W)=0`;
2. a transposed modular-composition or power-projection routine that computes
   only the common norm remainder;
3. a displacement-rank or structured-module recurrence whose input is the
   shared `H` circuit and whose output is the common factor plus source jets.

The derivation must count:

- construction of every bivariate leaf and marker component;
- every operation in quotient algebras of dimensions `r`, `r^2`, or larger;
- all coefficient conversion, transposition, evaluation, interpolation,
  factorization, gcd, and Hasse work;
- unsuccessful target batches, multiplicities, exceptional charts, exact
  source splitting, relation rank, and verification;
- peak state and serialized advice.

Stop with a scoped negative before scaling if any recurrence contains an
`Omega(r^3)` evaluation grid, coefficient vector, matrix, quotient module,
leaf family, or source table, or if the claimed output loses a target/start
label.

## Controls

- P1511's independently audited expanded `r^3`-leaf products;
- the exact P1510 `r^2`-leaf transcript with symbolic target retained;
- planted shared bivariate circuits with `Theta(r)` common norm roots;
- matched random bivariate circuits with identical bidegrees;
- label-permuted and label-dropped circuits;
- dense Sylvester, Bezout, quotient-module, evaluation/interpolation, and
  product/remainder-tree implementations;
- exhaustive ordinary elliptic fixtures with repeated, vertical, return,
  infinity, and nonreduced fibers.

## Decision Boundary

This receipt proves only the shared norm identities and the `r^2` input-circuit
possibility. It does not prove that `common_norm` is sub-rho. P1513 may advance
only after an explicit recurrence with total exponent below `5/2` and a
complete source biconditional survives independent audit.
