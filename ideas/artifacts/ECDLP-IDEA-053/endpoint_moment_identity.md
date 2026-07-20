# IDEA-053 Endpoint-Moment Identity Gate

Date: 2026-07-17

## Exact Moment Identity

Let P1490's monic squarefree two-transition endpoint polynomial be

```text
R(W) = W^d + c1 W^(d-1) + c2 W^(d-2) + ... + cd
     = product_(j=1..d) (W-z_j).
```

For endpoint power sums `s_m=sum_j z_j^m`, the first four Newton identities
are

```text
s1 = -c1,
s2 = -(c1*s1 + 2*c2),
s3 = -(c1*s2 + c2*s1 + 3*c3),
s4 = -(c1*s3 + c2*s2 + c3*s1 + 4*c4).
```

These are exact over each frozen base field.  They are also
`s_m=Tr(M_W^m)` in the quotient algebra `F_p[W]/R(W)`.  Thus endpoint moments
can be computed without factoring `R` once its coefficients or its dimension-d
multiplication operator have been materialized.

## State Bound In The Frozen FFE

P1490 proves

```text
d = 2*r^2+1
```

and every frozen `R` is dense with `d+1` nonzero coefficients.  Its root set is
the complete reachable endpoint-x set and also has cardinality `d`.  Therefore
the coefficient route materializes the accepted dense quadratic pair object,
while a companion/quotient trace route stores a dimension-d operator.  Sparse
decoding all keys has output size `d`; it is not an implicit sub-enumeration
oracle on this representation.

## Source-Tag Collision

For public start `P`, deck endpoints `A,B`, and start sign `epsilon`, the
source stream maps

```text
(epsilon,A,B) -> x(epsilon*P + A + B).
```

The stream has `8*r^2` signed ordered sources.  After canonicalizing the
commutative pair `(A,B)`, it still has

```text
2*r*(2*r+1)
```

source tags.  P1505 groups these tags by endpoint x-coordinate.  Every endpoint
has at least two different canonical source tags on every frozen cell.

Choose the lexicographically first source tag over each endpoint to form one
complete assignment and the lexicographically last tag to form another.  The
assignments differ at every endpoint but have the same endpoint-key multiset,
hence the same endpoint moments of every order.  Endpoint moments alone cannot
recover public relation rows.

## Existing Source Opening

P1491 supplies an exact source opening for a supplied endpoint `w`: compute the
pointwise gcd/subresultant in soft-linear work in `r`, then open the two deck
endpoints through the endpoint gcd/sign chain.  Opening all `d=2*r^2+1`
decoded endpoint keys therefore has the existing bound

```text
soft-O(r*d) = soft-O(r^3).
```

With the frozen `r=Theta(q^(1/5))` campaign, this is `q^(3/5+o(1))`, above
Pollard rho.

## Decision Boundary

The first four moment identities are retained as exact positive algebra.  They
do not instantiate IDEA-053's mechanism-new oracle because they consume the
dense P1490 object and erase source tags.  A successor would need a new
source-labelled factored algebra whose moments are computed before both the
quadratic endpoint object and per-endpoint opening, with collision-safe decoding
and complete cycle/rank/descent accounting.

This does not rule out every bivariate or module-valued moment oracle.  It closes
the untagged P1490 squarefree-resultant formulation only.
