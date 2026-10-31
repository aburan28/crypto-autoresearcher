# Explicit nilpotent-square circuit layout

Prospective implementation detail, 2026-10-31. Unreviewed symbolic counts, not measured work or solving degree. All unknowns are field elements in F_p. U is monic of degree k, with its k coefficients already part of the surrounding chart; curve coefficients are public. Count only added rationality-block variables/equations. All interval, norm, field-range and signed-recovery constraints remain outside this table.

## Modular-product primitive

For L,R of degree<k, let P have degree<k and Q degree<=k-2. Impose every coefficient of L*R-P-U*Q=0. There are 2k-1 coefficient equations and k+(k-1)=2k-1 auxiliary variables when both P and Q are new. Every equation has total degree<=2, even when U is variable. Each P,Q is unique for fixed monic U,L,R. If P is fixed to zero, only k-1 new variables Q remain, while all 2k-1 equations remain. k=1 uses no Q. Empty U=1 is special.

## Degree five

Write C of degree<5 with five new coefficients. Compute W=C² mod U with new W (five coefficients) and quotient Q0 (four): nine equations. D=W-f has degree<5 and is a linear expression, so introduce no new D variables. Compute S=D² mod U, then T=S² mod U, each with five remainder and four quotient coefficients and nine equations. Finally enforce T*D=U*Q3 with four quotient coefficients and nine equations. Thus (C²-f)^5=0 mod U has 5+9+9+9+4=36 auxiliary variables and 4*9=36 equations, all degree<=2. No Euler exponent, dense degree-p polynomial, hidden quotient table or coefficient enumeration is used in this specification.

## Other retained degrees

For k=4, f already has degree<k. Compute C² -> W (seven auxiliaries/equations); D=W-f; D² -> S (seven); S² -> zero (three auxiliaries/seven equations). Including four C coefficients gives21 variables and21 equations.

For k=3, f and U are both monic cubics. Set F=f-U, whose three coefficients are affine expressions in U; no new variables. Compute C² -> W (five); D=W-F; D² -> S (five); S*D -> zero (two auxiliaries/five equations). Including three C coefficients gives15 variables and15 equations.

For k=2, write U=X²+u1 X+u0. The reduction of f=X³+aX+b uses quotient X+q and remainder F1 X+F0. Add variables q,F1,F0 and three equations:

    q+u1=0
    F1+u0+u1*q=a
    F0+u0*q=b.

Then C has two coefficients. C² -> W adds three variables/equations; D=W-F; D² -> zero adds one quotient variable and three equations. Total9 variables and9 equations.

For k=1, U=X+u0. Add v=u0², F=-u0*v-a*u0+b, and constant C with C²=F. Total3 variables and3 equations. This is direct evaluation at -u0, and the required first power is simply zero. k=0 adds neither variables nor equations.

| k | Added field variables | Degree-at-most-two equations |
|---|---:|---:|
| 0 | 0 | 0 |
| 1 | 3 | 3 |
| 2 | 9 | 9 |
| 3 | 15 | 15 |
| 4 | 21 | 21 |
| 5 | 36 | 36 |

These counts follow the stated layouts without simplifications from special coefficients. They are not lower bounds or minimality claims. In each case every variable besides C is uniquely determined by U,C through monic division and fixed evaluation. Thus the previously derived fiber count 2^q*p^(k-r) carries over unchanged to the whole lifted block, conditional on split U, r distinct roots and q nonzero-square f-values. The final zero-remainder equations merely filter C.

The eventual builder must emit these exact layouts and check actual equation degrees/counts with an independent sparse-polynomial evaluator. A quadratic field system alone does not enforce prime-field membership in algebraic-closure solving; range/field constraints must be retained. SAT bit widths and carries are excluded from this field-level table and must be counted separately. The scientific comparison must record term order and its precise degree invariant before interpreting any degree result.
