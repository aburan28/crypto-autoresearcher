# P1510 Multiplicative Truncated-Resultant Compiler Derivation

## Scope

This artifact supplies P1510 Phase 0's missing construction recurrence. It
constructs all 15 marker coefficients of the globally truncated P1509
resultant without endpoint roots, endpoint gcds, endpoint-specific source
indices, or a source table.

The result is an output-sensitive compiler identity. It is not relation
collection, blind descent, or an end-to-end ECDLP complexity result.

## Linearized Products

Let `k=F_p`, let `a_i(V)=S3(u,V,x_i)`, and let
`b_j(V,W)=S3(V,W,x_j)`. Define public marker codes

```text
e_i = E0 + alpha_i E1,
h_j = H0 + alpha_j H1.
```

Write

```text
A       = product_i a_i,
A_lin   = A + sum_i e_i product_(ell != i) a_ell,
B       = product_j b_j,
B_lin   = B + sum_j h_j product_(ell != j) b_ell.
```

P1510 must construct

```text
T = Res_V(A_lin,B_lin) mod (marker degree >= 3).
```

Also define the full marked products

```text
A_prod = product_i (a_i+e_i),
B_prod = product_j (b_j+h_j).
```

Thus `A_prod=A_lin+O(E^2)` and `B_prod=B_lin+O(H^2)`.

## Multiplicative Decomposition Theorem

Partition the 15 marker monomials of total degree at most two into:

1. the constant monomial;
2. pure-E monomials of E-degree one or two;
3. pure-H monomials of H-degree one or two;
4. mixed monomials of bidegree `(E-degree,H-degree)=(1,1)`.

Then every component of `T` is supplied by exactly one of

```text
R_E    = product_j Res_V(A_lin,b_j),
R_H    = product_i Res_V(a_i,B_lin),
R_full = product_(i,j) Res_V(a_i+e_i,b_j+h_j).
```

Specifically:

```text
constant(T) = constant(R_E) = constant(R_H) = constant(R_full),
pure_E(T)   = pure_E(R_E),
pure_H(T)   = pure_H(R_H),
mixed_EH(T) = mixed_EH(R_full).
```

Proof:

- Setting `H=0` gives `Res(A_lin,B)`. Resultant multiplicativity in the
  second input gives `R_E` exactly.
- Setting `E=0` gives `Res(A,B_lin)`. Resultant multiplicativity in the first
  input gives `R_H` exactly.
- The mixed bidegree `(1,1)` coefficient of any polynomial map depends only
  on the constant and linear parts of each input. Replacing `A_lin,B_lin` by
  `A_prod,B_prod` changes the inputs first in pure bidegrees `(2,0)` and
  `(0,2)`, which cannot affect bidegree `(1,1)`. Multiplicativity in both
  inputs then gives `R_full`.
- The four monomial classes exhaust total marker degree at most two.

This avoids a Sylvester matrix of dimension `4r` over the marker ring.

## Constant-Size Pair Factors

Each factor

```text
P_ij(W,E,H) = Res_V(a_i+e_i,b_j+h_j) mod marker_degree^3
```

is the determinant of a `4 x 4` Sylvester matrix of two quadratics. It has
constant marker dimension and bounded W-degree. Compute all `r^2` factors and
multiply them with a balanced product tree, truncating marker degree after
every multiplication. Extract only the four mixed `EH` components from the
result.

The pair stage costs

```text
O(r^2) constant-size resultants + O(M(r^2) log r)
```

base-field operations, where `M(d)` is the cost of multiplying degree-`d`
univariate polynomials over `k`. Peak coefficient state is `O(r^2)`.

## Pure-H Factors

For fixed `i`, work in the two-dimensional algebra

```text
k[V]/(a_i).
```

The leading coefficient of `a_i` is a nonzero base-field constant on every
accepted selector factor. Reduce each `b_j+h_j` to the basis `(1,V)`, multiply
all `r` factors with a balanced product tree while truncating at H-degree one,
and take the quadratic norm at H-degree at most two. This gives

```text
Q_i(H,W) = Res_V(a_i,B_lin).
```

Multiplying all `Q_i` with a balanced tree gives `R_H`. The total cost is

```text
O(r M(r) log r + M(r^2) log r),
```

with `O(r^2)` output and peak state.

## Fraction-Free Pure-E Factors

Fix `j` and write

```text
b_j(V,W) = l(W)V^2 + m(W)V + n(W).
```

For P1490's Semaev factors, `l(W)=(W-x_j)^2`; it is not a unit in `k[W]`.
Avoid a fraction-field black box by representing a quotient-algebra element as

```text
(x0(W)+x1(W)V) / l(W)^s.
```

If `X=(x0,x1,s)` and `Y=(y0,y1,t)`, reduction with
`lV^2=-mV-n` gives the exact fraction-free product

```text
X*Y = (
  l*x0*y0 - n*x1*y1,
  l*(x0*y1+x1*y0) - m*x1*y1,
  s+t+1
).
```

Reduce a leaf `a_i+e_i=c2 V^2+c1 V+c0+e_i` as

```text
(
  l*(c0+e_i)-c2*n,
  l*c1-c2*m,
  1
).
```

Multiply the `r` leaves with a balanced tree, truncating at E-degree one.
Every tree shape ends with denominator exponent

```text
s = 2r-1.
```

For numerator `x0+x1V`, the monic quadratic norm numerator is

```text
N = l*x0^2 - m*x0*x1 + n*x1^2.
```

Since `deg_V(A_lin)=2r`, the resultant identity gives

```text
Res_V(A_lin,b_j) = N / l^(2r-1).
```

Therefore every one of the six pure-E/constant marker components of `N` is
exactly divisible by the public polynomial `l^(2r-1)`. The implementation
must use exact polynomial division and record the zero remainder for every
component. No gcd normalization or endpoint factorization is needed.

Computing all `r` pure-E factors and multiplying them into `R_E` costs

```text
O(r M(r) log r + M(r^2) log r)
```

and `O(r^2)` peak coefficient state.

## Complete Bound

The compiler uses

```text
O(r^2 + r M(r) log r + M(r^2) log r)
```

base-field operations and `O(r^2)` peak coefficient state. Standard fast
univariate polynomial multiplication makes this `O(r^2 polylog r)` work.
The output itself contains 15 dense endpoint-polynomial components of degree
`O(r^2)`, so the construction is quasi-linear in its explicit output size.

The operation transcript must record every polynomial multiplication's input
degrees. Reporting one product-tree, norm, determinant, or resultant call as
one operation is forbidden. The degree-pair transcript lets an independent
auditor evaluate schoolbook, Karatsuba, or standard quasi-linear `M(d)` cost
models without trusting a hidden library counter.

## Exactness and Trust Boundary

The producer receives only public curve/start data, the ordered selector
factor catalog, and public codes. It freezes all 15 coefficient polynomials and
the operation transcript before the verifier receives endpoint roots, P1509
local forms, pointwise gcds, or source partitions.

After freezing, the verifier must evaluate every component at all P1490
endpoints, recover the same first nonzero local form up to a nonzero scalar,
decode every P1509 factor pair, replay every source tag, and retain the growing
return branch as a low-order-zero control.

## Remaining ECDLP Boundary

This construction, if independently verified, removes P1509's global compiler
gap for the frozen two-transition reporter. It does not by itself establish
candidate density, enough independent factor-base rows, linear-algebra cost,
blind target descent, or an end-to-end exponent below one half.
