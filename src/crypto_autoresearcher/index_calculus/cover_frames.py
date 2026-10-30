"""Shifted even-sextic frames for the same short-Weierstrass curve.

Software interface only: no shift search, scientific collection, logarithm
oracle, Jacobian/isogeny certificate, or subgroup-action claim is supplied.
Callers retain field/order certificates and all original base/source bindings.
"""
from dataclasses import dataclass

from .curve import Curve, Point, is_probable_prime, sqrt_mod


@dataclass(frozen=True)
class ShiftedCover:
    p: int
    a: int
    b: int
    h: int

    def __post_init__(self):
        if self.p <= 3 or not is_probable_prime(self.p):
            raise ValueError('prime characteristic >3 required')
        # This probable-prime guard does not replace a caller's certificate
        # beyond the deterministic range documented by is_probable_prime.
        Curve(self.p,self.a,self.b)
        if self.c0 == 0:
            raise ValueError('singular even sextic: f(h)=0')

    @property
    def c4(self):
        return 3*self.h % self.p

    @property
    def c2(self):
        return (3*self.h*self.h+self.a) % self.p

    @property
    def c0(self):
        return (self.h**3+self.a*self.h+self.b) % self.p

    @property
    def polynomial(self):
        """Ascending coefficients of f(X²+h), including the X⁴ term."""
        return (self.c0,0,self.c2,0,self.c4,0,1)

    @property
    def auxiliary_coefficients(self):
        """E2: V²=U³+c2 U²+(c4 c0) U+c0²; not assumed isogenous to E."""
        return (self.c2,self.c4*self.c0 % self.p,self.c0*self.c0 % self.p)

    def rhs(self,x):
        u = (x*x+self.h) % self.p
        return (u**3+self.a*u+self.b) % self.p

    def is_on_cover(self,point):
        return point is not None and (point[1]*point[1]-self.rhs(point[0])) % self.p == 0

    def image(self,point):
        if not self.is_on_cover(point):
            raise ValueError('affine point is not on the cover')
        x,y = point
        return ((x*x+self.h) % self.p,y % self.p)

    def lifts(self,point: Point):
        """All rational affine lifts of an E point; zero has one deck lift."""
        if point is None:
            return ()
        curve = Curve(self.p,self.a,self.b)
        if not curve.is_on_curve(point):
            raise ValueError('point is not on the fixed elliptic curve')
        root = sqrt_mod(point[0]-self.h,self.p)
        if root is None:
            return ()
        return tuple((x,point[1] % self.p) for x in sorted({root,-root % self.p}))

    def auxiliary_image(self,point):
        if not self.is_on_cover(point):
            raise ValueError('affine point is not on the cover')
        x,y = point
        if x % self.p == 0:
            return None  # The two affine points map to E2's infinity.
        inverse = pow(x,-1,self.p)
        return (self.c0*inverse**2 % self.p,self.c0*y*inverse**3 % self.p)
