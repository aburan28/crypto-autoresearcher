# Assumption checks before second-pass data

These are static derivations and source-inspection notes. They are not
experimental outcomes, timed comparisons or formal proof certificates. They
were written before any second-pass panel ran; the S3 execution gate remains
closed. Source provenance is internal unless stated otherwise below.

## F1: quotient representation and explicit growth

Let p be odd, S=2^k and F(T)=D_S(T)-c with c different from both critical
values 2 and -2. The quadratic chain identifies its scalar algebra with
A=F_p[T]/F(T), of dimension S. On the separable fully split fibres used by
the fixed cases, A is a product of S copies of F_p.

Multiplication by T is an operator C. The induced symmetric operators on
exterior-cube(A) have characters (s1,s2,s3) for distinct unordered triples
of roots. Applying the symmetric S4 relation polynomial gives a diagonal
character test after scalar extension. Consequently its exact kernel
dimension counts the distinct triples satisfying that polynomial. Rational
elliptic lifts, signs, repeated-coordinate strata and extraction still require
their own checks. The exterior-cube dimension is C(S,3), equal to 560 at
S=16; this is an explicit representation size, not a speed bound.

The worker's proposed implementation evaluates the fixed-degree S4 relation
through sparse powers of C, keeping the long Dickson composition as a
quadratic chain. A complete root enumeration may serve as a separate oracle;
it is not an implicit extractor. If coordinate spectra collide on an n-state
kernel, E1+t*E2+t^2*E3 separates every pair for some t among
2*C(n,2)+1 distinct field values, provided that many values exist: each pair
forbids at most two roots of a nonzero quadratic. This proves existence of
a separating choice, not that extraction or the resulting arithmetic is cheap.

Sources read: first-pass F1/cubic-divisor derivations and exact S4 source;
PKM2016 introduction/section2.1, retrieved and read by the F1 worker, with
dedicated composed-system solving explicitly unresolved. The exterior
representation is a proposed derived implementation, not attributed as a new
published result.

## F4: anchored sampling is structured

Fix nonzero P in a prime-order group E(F_p) of odd order r>3. A function
y+a1*x+a0 vanishing at P has exactly one free slope a1 in F_p and exact
pole order3 at O. Its residual rational zeros Q,R satisfy Q+R=-P.

On E(F_p) minus {O,-P}, the involution Q -> -P-Q has one fixed point.
There are therefore ((r-2)+1)/2=(r-1)/2 unordered rational residual pairs,
with multiplicity retained. Each determines one normalized line, including
tangencies. Thus exactly (r-1)/2 of the p slopes have fully rational finite
zero divisor. This is an exact all-rational-zero law for this conditioned
sampling scheme, not a factor-base-smoothness or stitching-yield law.

Writing Q=kP shows residual inverse-orbit edges [k]--[k+1], up to the
identification [k]=[-k]. The terminal pair has coefficient2 at
k=(r-1)/2. Removing base vertices can yield one-outside-point columns; the
tangent at P has residual point -2P. Ordinary graph valence and weighted
incidence support are different conventions. Several anchors may permit
branching, but a random-graph collision model is not justified automatically.

This argument was derived independently by the F4 worker and root before
data. The worker read Zaslavsky sectionIV and Diem sections1-2 from primary
sources; Diem's stated complexity theorem assumes genus at least2 and is not
transferred to this genus-one target.

## F5: transported instances preserve solution sets

For each certified isogeny phi of degree ell coprime to r between the
same-order rational groups, phi restricts to an isomorphism. Its inverse on
the order-r subgroup is [ell^{-1} mod r] composed with the dual isogeny.
The dual itself generally has differential scale ell and is not a normalized
Velu map. For every tuple, signs and Q, sum(sign_i*P_i)=Q if and only if
sum(sign_i*phi(P_i))=phi(Q).

Matched transport therefore preserves exact decomposition sets. It does not
by itself settle the cost of membership formulas, map discovery or solving
on a differently chosen endpoint base. The second-pass controls retain the
same source labels and account for all inverse/denominator exceptions.
Sources: prior exact maps and dual identities; current official Sage
dual/composition/scaling documentation read by the geometry worker.

## F6: the arity fixes the capacity comparison

The relation f3(x,y,xQ)=0 has two factor-base summands. For a fixed signed
base with 2M nonzero points, a necessary half-coverage condition is
2*C(2M+1,2) >= r-1, whose leading scale is M=sqrt(r)/2. The exponent is
1/2. The first-pass three-summand threshold cannot be used for this
two-variable lattice. The new prescribed widths through 2^84 lie below
that two-summand capacity scale on P-256.

Small coefficient norms imply integer vanishing only under the precise
divisibility, box and norm hypotheses. Several short polynomials also need
an independent zero-dimensional extraction argument; neither matrix rank nor
LLL termination establishes it. Sources: first-pass explicit bounds and
Galbraith's corrected chapters17 and19 read by the F6 worker.

## F7: infinity classes are essential

For C: w^2=z^6-3*z^2+b, the smooth even-degree model has two rational
infinities. In the balanced convention
D=div(u,v)+n*infinity_plus+(2-deg(u)-n)*infinity_minus
-(infinity_plus+infinity_minus), the identity is (1,0,1) and
T=[infinity_plus-infinity_minus] is (1,0,2).

Both infinities map to O under pi(z,w)=(z^2,w), so norm(T)=O. However T is
nonzero: a principal divisor infinity_plus-infinity_minus would give a
degree-one map from a genus-two curve to P1. Equal norms cannot certify
equality of Jacobian classes.

At p different from2 and3 and nonzero b, the function w-z^3 has divisor
Z+infinity_plus-3*infinity_minus, where Z is the degree-two finite divisor
z^2=b/3, w=z^3. The leading local expansions give a zero of order1 at
infinity_plus and a pole of order3 at infinity_minus. This supplies a
principal/infinity-balancing control, including nonsplit Z.

Sources: the even-degree cover and smoothness checks of the first pass;
Galbraith-Harrison-Mireles Morales, ANTS2008, sections2-4 and algorithms1-5,
primary author PDF read by the geometry worker; Sage even-degree arithmetic
issue37109. The balanced arithmetic and norm still need actual execution
and independent checks before a computational conclusion.
