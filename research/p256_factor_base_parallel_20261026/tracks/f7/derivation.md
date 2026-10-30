# F7 balanced classes and a root-free norm

Prospective derivation, 26 October 2026; no second-pass observation data.
The smooth genus-two curve is `C:w^2=z^6-3z^2+b`, over the published P-256
field of characteristic different from 2 and 3. Its two rational infinities
are denoted I+ and I-, with `w/z^3` tending to +1 and -1. The cover
`pi(z,w)=(z^2,w)` maps both to the elliptic identity O.

For this particular sextic, its derivative is `6z(z^4-1)`. A common zero
would require `b=0`, `b=2` or `b=-2`; the fixed P-256 coefficient satisfies
none of these. Thus it is squarefree over the algebraic closure. A monic
squarefree sextic in odd characteristic gives the stated smooth genus-two
split model. This is a direct argument, not a count from finite fixtures.

Represent a class by the balanced triple `(u,v,n)`:

    [D_aff(u,v) + n I+ + (2-deg(u)-n) I- - (I+ + I-)].

Here u is monic of degree at most two, `deg v < deg u`, `u | f-v^2`, the
affine divisor is semireduced, and `0 <= n <= 2-deg u`. Composition,
reduction, infinity balancing and inversion follow the established split
model algorithms named in `literature.md`. The code retains their polynomial
Bezout and infinity-counterweight traces. It does not use Sage 10.6's
ambiguous even-degree pair addition.

The identity is `(1,0,1)`. The class T=`[I+-I-]` is `(1,0,2)`, while -T is
`(1,0,0)`. The pair `(u,v)` alone cannot distinguish them. T is nonzero:
if `I+-I-` were principal, a function with one simple pole would define a
degree-one map from C to the projective line, contradicting genus two.
Nevertheless `pi_* T=O`. Thus norm equality cannot establish class equality.

The principal divisor of `w-z^3` is explicit. At I-, its pole order is three;
at I+, `w-z^3=-3/(2z)+...` has a simple zero. The finite zeros satisfy
`z^2=b/3,w=z^3`. If A denotes their affine degree-two divisor, then

    div(w-z^3)=A+I+-3I-,
    [A-(I++I-)]+2T=0.

This supplies an infinity-sensitive class control independent of matching
elliptic norms. Divisors of `z-c` supply cancellation controls, including the
two opposite w signs and their infinity terms.

For an affine degree-two divisor with
`u=z^2+s z+t`, `v=v1 z+v0`, let its roots be alpha,beta. If s is nonzero,
the line through their elliptic images has slope `L=-v1/s`; this remains
valid on a double support by the tangent limit. Their sum is

    X = L^2-s^2+2t,
    Y = -L(t+X)-v0.

If s=0, the congruence implies the equal-image exception: v1=0 gives
`[2](-t,v0)` and v0=0 gives O. A degree-one support `(z,w)` has norm
`(z^2,w)`. Infinity terms contribute O. These formulas define the root-free
norm implementation; the separate reference splits u in Fp[i] and sums the
actual image points, retaining multiplicities. It rejects a missing
Frobenius conjugate when the resulting image is not Fp-rational.

For a source point P=(x,y), the balanced pullback is
`u=z^2-x,v=y,n=0`, with both infinities subtracted. It has norm `[2]P`.
For O, pullback is the identity class, not an artificial affine pair. The
fixed panel checks balanced pullback addition as class equality separately
from the norm computation.

The reference norm checker does not independently certify all class
arithmetic: it sees the norm kernel as zero. Principal identities, full
balanced representations and associativity checks therefore retain their
own scope. This implements genus-two correspondence arithmetic, not the
original plane-quartic Jacobian, a target-image relation solver or an ECDLP
cost advantage.
