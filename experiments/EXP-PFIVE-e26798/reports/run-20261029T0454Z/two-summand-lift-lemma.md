# Exact rational lifting for two summands

This is a mathematical derivation reviewed separately from the frozen experiment. It is not a measured result, a formal proof-assistant artifact, or a novelty claim. It gives an exact encoding simplification to test under a future contract.

Let \(E:y^2=f(x)=x^3+ax+b\) be nonsingular over \(\mathbb F_p\), with \(p>3\). Fix a finite rational target \(R=(r,s)\) with \(s\ne0\), equivalently \(2R\ne O\). With the standard third summation polynomial

\[
S_3(x_1,x_2,r)=(x_1-x_2)^2r^2
-2\big((x_1+x_2)(x_1x_2+a)+2b\big)r
+(x_1x_2-a)^2-4b(x_1+x_2),
\]

every pair \(x_1,x_2\in\mathbb F_p\) satisfies

\[
S_3(x_1,x_2,r)=0
\iff
\exists P_1,P_2\in E(\mathbb F_p):
 x(P_i)=x_i,\quad P_1+P_2=R.
\]

## Explicit witness and certificate identity

Put \(T=x_1+x_2\), \(V=x_1x_2\),
\(N=V-rT-2r^2-a\), and

\[
\lambda=N/(2s),\qquad y_i=\lambda(x_i-r)-s.
\]

Substituting \(s^2=r^3+ar+b\) and expanding gives

\[
N^2-4s^2(T+r)=S_3(x_1,x_2,r).
\]

For an independent indeterminate \(X\), this yields the coefficient identity

\[
f(X)-\big(\lambda(X-r)-s\big)^2
-(X-x_1)(X-x_2)(X-r)
=-\frac{S_3(x_1,x_2,r)}{4s^2}(X-r)^2.
\]

When \(S_3=0\), the right side vanishes. The line
\(y=\lambda(X-r)-s\) therefore intersects the cubic at
\(P_1=(x_1,y_1),P_2=(x_2,y_2),-R\), counted with multiplicity.
The chord-and-tangent law gives \(P_1+P_2=R\). All recovered coordinates are rational; no square-root extraction is needed. Conversely, a decomposition implies the summation-polynomial equation by its defining property.

The formula divides only by the fixed nonzero value \(2s\). Equal summand coordinates, a summand coordinate equal to \(r\), rational two-torsion summands, and a target of order three are all allowed. Intersection multiplicity handles tangent cases.

The same identity gives an exact quadratic encoding with one auxiliary field variable:

\[
\lambda^2=x_1+x_2+r,\qquad
2s\lambda=x_1x_2-r(x_1+x_2)-2r^2-a.
\]

For every \(S_3\) model the second equation determines \(\lambda\) uniquely, and the first follows from the identity. Conversely, these two equations imply \(S_3=0\). This replaces a quartic coordinate equation by two quadratic equations with an extra field variable. It does not establish lower solving degree: representing that extra variable and the consequences of elimination can absorb the apparent reduction. Comparing these equivalent encodings is a concrete next SAT/algebra experiment, outside the completed frozen contract.

## Independent Frobenius argument

The defining property of the summation polynomial first gives lifts over the algebraic closure whose sum is \(R\). Rational abscissas imply that Frobenius sends each lift to itself or its negative. If exactly one lift is nonrational, applying Frobenius to the sum forces that lift to be two-torsion, hence rational, a contradiction. If both are nonrational, Frobenius sends their sum to \(-R\), contradicting \(2R\ne O\).

The defining property is standard: see Proposition 2.1 of [Kosters and Yeo, Notes on summation polynomials](https://arxiv.org/html/1503.08001), referring to Semaev's construction. The HTML primary source was inspected on 2026-10-29. The implication and explicit identity above are recorded as a derivation, without asserting that they are new.

## Exact boundaries

The target assumption is essential. On \(E/\mathbb F_5:y^2=x^3+x\), let \(R=(0,0)\) and \(x_1=x_2=1\). Then \(S_3(1,1,0)=0\), but \(f(1)=2\) is a nonsquare. Neither coordinate has a rational lift. Over \(\mathbb F_{25}\), \(P=(1,\sqrt2)\) satisfies \(2P=R\).

The statement also fails for three summands. On \(E/\mathbb F_7:y^2=x^3+x+1\), take \(R=(0,1)\), with \(2R=(2,5)\ne O\). Since \(f(1)=3\) is a nonsquare, \(P=(1,\sqrt3)\) is nonrational, but \(P+(-P)+R=R\). Thus \(S_4(1,1,0,0)=0\) although the first two coordinates have no rational lifts. This counterexample uses repeated coordinates; it does not settle further restricted predicates.

For two summands, separate existential curve-coordinate membership equations are redundant at the projected \((x_1,x_2)\) model-set level. Any retained \(y\)-variables must still be constrained or replaced by the displayed witness map. A factor base restricting signs, subgroup membership on a curve with cofactor, or distinctness constraints still requires those checks. The corrective point fixtures use full curves of prime order, where the subgroup qualification introduces no extra restriction.

Both displayed denominator-cleared polynomial identities were also checked exactly by [check_lift_identity.py](check_lift_identity.py); the retained [verification output](lift-identity-check.json) binds its script hash and SymPy version. This checks the algebraic expansion, not a formalization of the group-law proof.

This establishes neither ideal equality nor a reduction of degree of regularity, solving degree, or runtime. Redundant equations can help a solver. The next controlled comparison should preserve identical complete projected model sets while comparing the membership encoding with an x-only encoding plus witness reconstruction; it must include reconstruction and proof-check costs.
