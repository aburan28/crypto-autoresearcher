# IDEA-056 Shared-Module Derivation Gate

## Frozen Candidate

Let `N_r(U,V)` be the exact rational-selector one-transition norm from P1490
and P1491.  For a public start state `u` and a supplied query state `w`, set

```text
f_u(V) = N_r(u,V),
g_w(V) = N_r(V,w).
```

The only faithful quotient module supplied by the IDEA-056 proposal is

```text
A_(u,r) = F_p[V] / (f_u(V)).
```

On the frozen fixtures, `deg(f_u)=2r`, so this module has dimension `2r`.
Let `M_V` be multiplication by `V` in `A_(u,r)` and let

```text
M_w = g_w(M_V).
```

This names the previously unspecified `A_L`, `M1`, and `M2`: `M1=M_V` and
`M2=M_w`.  There is no second target-independent sparse operator in the
frozen mechanism; `M_w` changes with the supplied query `w`.

## Exact Iff Identity

For monic `f_u`, multiplication by `g_w` satisfies

```text
det(M_w) = Res_V(f_u,g_w).
```

Therefore

```text
ker(M_w) != 0
iff Res_V(f_u,g_w)=0
iff gcd(f_u,g_w) != 1.
```

When `f_u` is squarefree, the kernel dimension is the degree of the common
factor.  The common factor itself is the exact intermediate-state polynomial.
P1491 already computes it by half-GCD, opens both endpoint selectors, lifts
all signs, and replays the complete elliptic source.

This is a valid shared-module biconditional and source lift.  It is not a new
algorithmic primitive beyond P1491.

## Fixed-Query Cost

The module vector has `2r` field elements.  An explicit black-box matvec must
at least read and write `Omega(r)` field elements.  With block size `b`, a
generic complete block-Krylov sequence needs `Omega(r/b)` iterations and each
state has `Omega(rb)` field elements, giving `Omega(r^2)` state traffic across
the sequence.  Taking `b=Theta(r)` moves the same quadratic cost into one
block state.

Polynomial structure avoids this quadratic route: direct fast gcd computes
the same decision and source polynomial in `soft-O(r)` field operations.  That
is exactly P1491's independently audited fixed-query primitive.  Block Krylov
is therefore dominated on the only explicit faithful module.

## Symbolic-Batch Cost

Keeping `w` symbolic gives

```text
det(g_W(M_V)) = Res_V(N_r(u,V),N_r(V,W)).
```

P1490 independently verifies generic raw degree `4r^2`, squarefree degree
`2r^2+1`, and dense nonreturn degree `2r^2`.  A lossless coefficient or root
batch therefore restores an `Omega(r^2)` output object.  Krylov projections
over `F_p[W]` do not remove this degree; they encode the same determinant.

## Complete-Campaign Boundary

P1491 verifies every fixed-query decision and source opening, then measures
the missing candidate stream.  Exact three-endpoint support has
`Theta(r^3)` sources, and the complete relation campaign is

```text
Theta(r^3) = Theta(q^(3/5)),
```

above Pollard rho `Theta(q^(1/2))`.  Random supplied-state sampling followed
by the soft-linear predicate is worse.  A different linear-algebra evaluator
for the same fixed-query predicate cannot change this candidate-supply
exponent.

## Review Verdict

IDEA-056 fails its mechanism-new gate under the only explicit shared module:

- fixed query: exact but duplicated by P1491 and direct gcd is asymptotically
  better than block Krylov;
- symbolic batch: the dense degree-`Theta(r^2)` resultant returns;
- complete campaign: the independently measured `Theta(q^(3/5))` candidate
  floor remains.

Do not approve the scaling contract.  A future proposal must provide a
different target-independent module whose source-labelled batch output is not
the P1490/P1491 resultant or A2/A3 support under another evaluator.
