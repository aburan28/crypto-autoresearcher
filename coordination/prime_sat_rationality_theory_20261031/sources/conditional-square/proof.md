# Conditional square witnesses for linear ordinate coefficients

Derived 2026-10-31 by root; UNREVIEWED theory, no solver execution or benchmark. This extends the common-root localization argument in ../shared-chart-signed-recovery/proof.md. It does not change the implementation currently under independent review.

## Domain and retained obligations

Work over F_p, prime p>3, with nonsingular E: y^2=f(x)=x^3+a*x+b. The supplied normalized chart h=A+B*y has exact pole order at most six, deg A<=3 and deg B<=1. Its nonzero norm N=A^2-f*B^2 must already satisfy the full norm coefficient identity and split over F_p. In the intended encoding the interval idempotents/nilpotence constraints give split U, and the known rational target supplies the extra norm root. Keep the target vanishing constraint, multiplicities, all lower-pole strata, and signed reconstruction/checking.

The common-root localization argument says that rational support of the zero divisor of h is equivalent to f being square-or-zero on the support of gcd(A,B). Brief justification: at a noncommon norm root with f nonzero, B is nonzero and -A/B is a rational ordinate. A common root contributes both geometric signs; these are rational exactly when f is square-or-zero. Branch roots have ordinate zero. Repeated roots alter orders, not this support test. Removing one rational target cannot remove a nonsquare pair. This argument is conditional on split norm and is not a replacement for those constraints.

## Linear B: no polynomial gcd witness

Suppose B=b1*X+b0 with b1 nonzero. Introduce alpha,z satisfying b1*z=1 and b1*alpha+b0=0. Their values are unique. Put c=A(alpha) and F=f(alpha). The only possible common root is alpha. Thus the residual rationality obligation is

    c != 0 OR there exists beta in F_p with beta^2=F.

An exact existential encoding is

    beta^2 = F + c*u.

If c!=0, every beta admits unique u=(beta^2-F)/c. If c=0, the equation is precisely the required square-root equation, with u arbitrary. Projection onto original chart coefficients is therefore exact. This includes F=0.

For fixed valid chart coefficients, the (beta,u) fiber has p solutions when c!=0, p solutions when c=0 and F=0, and 2p solutions when c=0 and F is a nonzero square. Nonsquare F with c=0 gives zero solutions. These free fibers are a concrete search cost, so the shorter encoding is not automatically preferable.

## Guarded encoding with bounded auxiliary fibers

Replace the preceding single equation by these five equations, introducing e,u,beta:

    c*u = 1-e
    c*e = 0
    u*e = 0
    (1-e)*beta = 0
    beta^2 = e*F.

If c!=0, the second equation forces e=0, the first gives u=c^-1, and the fourth gives beta=0. The last equation then holds, regardless of F. If c=0, the first forces e=1, the third gives u=0, and the last requires beta^2=F. Conversely these assignments satisfy all five equations in the respective cases. In particular e is automatically Boolean; no separate e^2=e is necessary. Alternatively multiply the first equation by e and use c*e=0 to derive e=e^2.

For each chart coefficient tuple the fiber now has exactly one element when c!=0; one when c=0,F=0; two when c=0,F is a nonzero square; zero otherwise. The two square-root signs correspond to the same balanced signed multiset and must be projected away. If unique auxiliary witnesses are needed, impose the integer representative condition 0<=beta<=(p-1)/2 for c=0. This introduces a real bit-comparison cost; it is optional for projected enumeration and is not included in the field-equation count below.

## Explicit quadratic lift and exact size

Write A=a3*X^3+a2*X^2+a1*X+a0, retaining zero or fixed coefficients for lower charts. Introduce q1,q2,c,v,F with equations

    q1 = a3*alpha+a2
    q2 = q1*alpha+a1
    c  = q2*alpha+a0
    v  = alpha^2
    F  = alpha*v+a*alpha+b.

All are of total degree at most two in chart and auxiliary variables (curve coefficients a,b are public constants). Combine these five evaluation equations, the two equations for alpha,z, and the five guard equations. The resulting generic block has TEN auxiliary field variables (alpha,z,q1,q2,c,v,F,e,u,beta) and TWELVE field equations of degree at most two. Evaluation variables are unique for fixed alpha and chart coefficients. A chart with monic or absent coefficients can simplify this generic block; no simplification is used in the stated count.

The simple slack variant uses nine auxiliary field variables and eight equations, also degree at most two after the same lift, but has the p or 2p fibers described above. These are symbolic counts of this block only, not operation measurements or counts for the complete SAT encoding.

This construction replaces the Euler rationality block for the linear-B stratum, conditionally on all retained norm/splitting constraints. It does not remove the interval bit-idempotent construction, norm multiplications, group witness reconstruction, range/carry constraints, or proof checking. Field quadratic equations do not imply a low degree of regularity, and bit-blasting may dominate their cost.

## Complete B stratification

Use disjoint strata: (i) b1!=0, with the block above; (ii) b1=0 and b0!=0, certified by b0*z=1, in which A and B have no common roots and the rationality block is vacuous; (iii) b1=b0=0, retaining the original full support rationality test or a separately proved replacement. The normalized odd-pole charts already require a nonzero B; impossible strata can be excluded only by their existing chart shape. Keep all admissible zero-B even-pole charts. No restriction to the generic stratum is allowed.

Each h belongs to exactly one stratum. Target/interval constraints may make a stratum empty, but that must follow from checked equations, not an empirical absence. For finite target outside the interval, retain its extra norm factor throughout; it need not be an interval root. No comparison with a coset/Graeffe domain is licensed by this derivation.

## Next test and limitations

First obtain independent algebraic review of projection equivalence and fibers; then admit a fixed software implementation of the block and complete chart union. The eventual controlled comparison must use the same complete projected signed outputs, a baseline with full Euler quotient rationality, and both slack and guarded variants. Charge chart setup, constraints, range conversion, search, auxiliary projection, signed reconstruction, and certificate checking. Record polynomial generators/term order before measuring any degree invariant. Do not infer solving degree from the maximum displayed generator degree. No tests or scientific runs were performed for this note.

Source read by root on 2026-10-31: Andrew Sutherland, MIT 18.782 Lecture 23, https://math.mit.edu/classes/18.782/2023sp/LectureNotes23.pdf, Theorem 23.3 and its proof supply standard pole-order/basis background. The conditional-square block and fiber calculation above are the present derivation, not a result attributed to that source. No claim of literature novelty is made. Canonical research graphs remain unchanged because no accepted finding or decision is changed.
