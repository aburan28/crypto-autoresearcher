# Exact auxiliary construction and fibre proofs

Scope: TASK-20261025-929e0f, implementation validation over the published P-256
prime. These are derived mathematical facts and executable certificate checks,
not a scientific performance trial. The exact endpoints, constants and points
are serialized under `receipts/validation-001/`; no endpoint replaces P-256.

## Point count and cyclic 2-primary subgroup

Write p=2^256-2^224+2^192+2^96-1. Here p=3 mod 4, so the quadratic character
satisfies chi(-1)=-1. For f(x)=x^3+x, f(-x)=-f(x). Pairing x and -x therefore
cancels every character-sum term except x=0, whose term is zero. Consequently
#A(F_p)=p+1, exactly; this does not rely on [p+1] annihilating a sampled point.

Furthermore p+1=2^96*(2^160-2^128+2^96+1), with odd second factor. The only
rational nonzero 2-torsion is (0,0), because x^2+1 has no rational root. A
finite abelian 2-group with precisely one nonidentity element of order 2 is
cyclic. Its order is thus 2^96. The retained H satisfies [2^96]H=O and
[2^95]H != O, proving its exact order without factoring the odd cofactor.

Both A and all chain endpoints are nonsingular. Their common order p+1 is
preserved by the explicit F_p-isogenies. Their trace is zero; these are
supersingular curves. No ordinary-volcano conductor direction is asserted.

## Each degree-two map and its dual

Let E be y^2=x^3+A*x^2+B*x+C, with a rational order-two kernel point (r,0).
Put u=x-r, a=A+3r, b=B+2Ar+3r^2. Then

    y^2 = u*(u^2+a*u+b),
    X = u+a+b/u,
    Y = y*(1-b/u^2),
    E': Y^2=X^3-2a*X^2+(a^2-4b)*X.

The hypotheses b != 0 and a^2-4b != 0 are checked. The following identity
proves the map universally over the declared field, rather than only at test
points. With N=u^2+a*u+b,

    X*(X^2-2aX+a^2-4b)
      = N*((u^2+b)^2-4b*u^2)/u^3
      = N*(u^2-b)^2/u^3
      = y^2*(1-b/u^2)^2.

The map extends across u=0 and O by sending both to O. A nonconstant morphism
of elliptic curves preserving O is a group homomorphism; its kernel has the
two points O,(r,0), and its degree is 2. Characteristic p is odd, so it is
separable. A separable isogeny of elliptic curves is unramified.

The normalized dual is obtained by applying the same quotient formula with
(a',b')=(-2a,a^2-4b), followed by X->X/4, Y->Y/8 and u->u+r. The resulting
curve has coefficients (a,b) in u. Substitution yields both compositions [2];
the executable also checks both directions, including sampled source and
independently generated endpoint points. The forced dual composition is a
control and is not reported as a newly found endomorphism.

At edge i use the rational order-two point [2^(95-i)]H_i, where H_i is the
image of H after i edges. Its image H_(i+1) has exact order 2^(95-i). Thus
all 16 kernels and maps are defined over F_p, and the composite Phi_k has
cyclic rational kernel K_k=<[2^(96-k)]H> of order 2^k. The chain degree is
2^k; its sequential representation has k degree-two steps.

## Finite fibres, kernel coordinates, poles and ramification

Let Q=Phi_k(P), with Q != O and Q != -Q (checked as Q_y != 0).
Then Phi_k^{-1}(Q)=P+K_k, and the x-fibre above x(Q) is exactly

    { x(P+jK_k) : 0 <= j < 2^k }.

All these coordinates lie in F_p. If two x values coincided, either the
points would coincide or P+jK_k=-(P+lK_k). The second possibility would give
2Q=O. Therefore there are precisely 2^k distinct coordinates. The degree-2^k
x-map supplies an independent upper bound and hence a completeness proof.
The replayer verifies the full degree/cardinality certificate for every
enumerated case. The producer also compares the independently inverted
quadratic tower with this coset and checks a complete linear factorization
of numerator-c*denominator.

The inverse step solves u^2+(a-X)u+b=0, then x=u+r. No valid finite preimage
has u=0 because b != 0. Squared/cleared-denominator relation encodings must
still preserve these nonvanishing conditions, especially above poles.

For k>=1 put N=2^k. Nonzero kernel points modulo sign have exactly N/2
coordinates; one is x=0, the unique rational source point of order two.
The reduced rational map has a simple pole at infinity and at x=0, and
N/2-1 double finite poles. Thus denominator degree is N-1 and numerator
degree N. Exact factor products certify all poles through degree 4096.
The elliptic isogeny remains unramified; these poles/critical points concern
the induced P^1 x-map. Its critical divisor has degree 2N-2, all simple.
The source elliptic 2-torsion gives no x-map critical point. Critical points
are x(P) with Phi_k(P) in E_k[2] and P not in E_0[2]; this statement is over
the algebraic closure, not a claim that every such P is rational. The checker
uses W=N'(x)D(x)-N(x)D'(x), proves W squarefree, checks gcd(W,x^3+x)=1,
counts the critical poles, and verifies that all remaining critical values
satisfy the exact destination 2-torsion cubic. This distinguishes rational
map ramification from unramified elliptic isogeny geometry.

The 16-edge chain additionally has a compact complete generic-fibre
certificate (65,536 x values) and kernel-coordinate cardinality (32,768).
Target lifts for this full degree are not enumerated. Enumerated complete
finite fibres use degrees 64,256,1024,4096, and the matching kernel domains
use degrees 128,512,2048,8192.

## Fixed target lifts and the comparison boundary

A raw coordinate x is retained only if v^2=x^3-3x+b_256 has a rational
solution. A nonresidue is a certified rejection. Choose 0<v<=floor(p/2) as
the canonical sign. Every retained target point is checked on P-256 and
satisfies [r]P=O. Since r is prime and the affine point is nonzero, its order
is exactly r. Its negative is also in the subgroup. The producer uses affine
arithmetic; the certificate replayer uses independently written Jacobian
formulas for these subgroup checks.

This coordinate reinterpretation is not a group homomorphism. In fact the
published target order r is coprime to p+1, so every rational-point group
homomorphism from E_256(F_p) to A(F_p) is zero. The traces also differ, so no
F_p-isogeny connects these elliptic curves. No P-256 DLP is transferred to
the auxiliary 2-primary group.

The Dickson control uses the same norm-one torus over F_p[i], i^2=-1, order
p+1. A generator zeta of exact order 2^96 and offset z give x_j=Tr(z*zeta_k^j)
and terminal c=Tr(z^(2^k)). The identity Tr(w^2)=Tr(w)^2-2 proves the circuit.
For c != +/-2 the 2^k distinct rational coordinates form the complete fibre
of D_(2^k)(x)=c; a full linear-factor product is checked. Both families have
expanded degree 2^k and quadratic circuits of depth k. The elliptic steps
are rational and have poles, while Dickson steps are polynomial and have no
finite poles. Straight affine elliptic evaluation pays one inversion per
step; projective/batched evaluation changes that primitive count and must be
priced separately. No timing or speed claim is made from these descriptions.

The comparison freezes d=3 and matches the final canonical target base size
by sorting each accepted x set and retaining the first minimum count among
the three families at that raw size. This extra selection must be charged;
it changes the implicit membership predicate. Raw fibre size is not silently
identified with accepted target base size. These finite domains and their
incidence counts prove neither a general acceptance probability nor a
relation yield. The summation-polynomial solver and its full costs remain
unimplemented here.
