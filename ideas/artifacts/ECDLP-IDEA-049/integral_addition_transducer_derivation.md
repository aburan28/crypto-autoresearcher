# IDEA-049 Integral Addition Transducer Derivation Gate

Date: 2026-07-17

## Generic Affine Lift

For affine points `P1=(x1,y1)`, `P2=(x2,y2)`, and
`P3=P1+P2=(x3,y3)` on `y^2=x^3+a*x+b` over `F_p`, choose standard integer
representatives in `[0,p-1]`.  A complete generic secant chart introduces a
slope `lambda` and three integer quotients:

```text
lambda*(x2-x1) - (y2-y1)             = k_s*p,
lambda^2 - x1 - x2 - x3              = k_x*p,
lambda*(x1-x3) - y1 - y3             = k_y*p.
```

The doubling chart replaces the first equation by

```text
lambda*(2*y1) - (3*x1^2+a) = k_d*p.
```

Vertical, identity, and point-at-infinity cases require separate deterministic
charts.  A two-addition decomposition needs two copies of the generic or
exceptional equations and an exact chart selector.

For standard representatives the universal elementary bounds are

```text
|k_s| <= p-1,
-2 <= k_x <= p-2,
|k_y| <= p-1.
```

Keeping integer curve equations introduces still larger quotients because
`x^3/p=Theta(p^2)`; keeping them modulo `p` leaves full-size x/y variables.

## Complete-Slope Lower Bound

Fix a nonidentity point `P`.  For every nonvertical affine `Q`, the secant line
through `P,Q` has a slope in `F_p`.  A line through `P` meets the cubic in at
most two further points, so each slope has at most two such `Q`.  Therefore a
complete chart on a group of order `N` contains at least

```text
M >= (N-O(1))/2
```

distinct slope residues.

A centered interval `[-H,H]` contains at most `2H+1` residues while `H<p/2`.
Consequently every target-independent centered representative system covering
the complete chart satisfies

```text
H >= (M-1)/2 >= (N-O(1))/4 = Omega(p)
```

on ordinary prime-field curves with `N=p+O(sqrt(p))`.  Thus the slope variable
has exponent one, not a bound `p^eta` with `eta<1`.  For slopes of centered
height `Omega(p)`, the x-update quotient also reaches `Omega(p)` on generic
coordinates.

This is a root-region failure before lattice construction: a Coppersmith lattice
whose declared bound excludes valid roots cannot be complete, regardless of
its determinant.

## Elimination Control

Reducing the lifted equations modulo `p` and eliminating `lambda` gives

```text
(y2-y1)^2 - (x2-x1)^2*(x1+x2+x3) = 0 mod p,
```

the denominator-free ordinary addition equation.  Combining it with the curve
equations and eliminating y signs gives the standard Semaev `S3` relation.
Eliminating the modulus-scale slopes and quotients therefore returns the nearby
dense modular/Semaev control rather than a bounded integer transducer.

## Decision Boundary

The natural complete affine lift is exact and invertible when all variables and
charts are retained.  It does not place every hidden variable in a sub-modulus
small-root box.  This does not rule out a special factor base with a proved
low-height addition circuit, a non-affine integral model, or a different
operation-preserving transducer.  Any successor must supply that construction
and prove its root region without source-selected recentering.
