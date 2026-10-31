# A sufficient condition for unique y-coordinate matching

Derived elementary lemma; no historical-use or novelty claim. Let E be the
smooth short Weierstrass curve y^2=x^3+A*x+B over a field of characteristic
greater than3. Let H be a cyclic subgroup of odd prime order ell different
from the characteristic. Assume H is Frobenius-stable, with Frobenius acting
as the nonzero scalar lambda. Let K(X) be its monic half-kernel polynomial,
of degree d=(ell-1)/2, and let S1 be the sum of its roots.

If a scalar k different from lambda has the same y-coordinate function as
Frobenius on all of H, put a=k/lambda modulo ell. Then
y([a]P)=y(P) for every nonidentity P in H. Every orbit under a has size
ord_ell(a). A fixed y-coordinate has at most3 distinct points, since its
x-coordinates solve the cubic X^3+A*X+B-y(P)^2=0. Order2 would mean
a=-1, but y(-P)=-y(P) cannot equal y(P) on a nonidentity point of odd
order in characteristic different from2. Thus the nontrivial order must
be3. Consequently ell=1 modulo3.

Each such orbit consists of the three distinct roots of that cubic, whose
sum is zero. Summing x over H minus the identity gives zero. The same sum
equals2*S1, because P and -P have the same x-coordinate. Since the
characteristic is not2, S1=0.

Therefore S1 nonzero excludes every false full y-function match. If ell is
not1 modulo3, no such false match exists even when S1=0. This is a necessary
condition for an ambiguity, not a sufficient one. It concerns equality on
the entire cyclic kernel, as in quotient-ring SEA arithmetic; a fingerprint
evaluated at a single point or reduced modulo an improper factor has a
different domain and is not covered.

The signed search k=1 through d with both y([k]P) and -y([k]P) enumerates
all nonzero scalars, so the lemma applies without an unstated sign choice.
For a j=0 model over F103, the order-three automorphism supplies an actual
CM positive control. The experiment constructs both Frobenius-stable
7-kernels of y^2=x^3+1 and requires three y-only matches but one full-point
match on each. This positive control is checked by exact arithmetic; its
isogeny-class catalog label is not a claim about any cryptographic curve.
