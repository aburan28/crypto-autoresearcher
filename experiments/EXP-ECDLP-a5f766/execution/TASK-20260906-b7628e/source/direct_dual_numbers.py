"""Direct ring arithmetic; never imports the coefficient implementation."""
class Dual:
    def __init__(self, a, b, p):
        self.a, self.b, self.p = a % p, b % p, p
    def coerce(self, x):
        return x if isinstance(x, Dual) else Dual(x, 0, self.p)
    def __add__(self, x):
        x = self.coerce(x)
        return Dual(self.a+x.a, self.b+x.b, self.p)
    __radd__ = __add__
    def __neg__(self):
        return Dual(-self.a, -self.b, self.p)
    def __sub__(self, x):
        return self + -self.coerce(x)
    def __rsub__(self, x):
        return self.coerce(x) + -self
    def __mul__(self, x):
        x = self.coerce(x)
        return Dual(self.a*x.a, self.a*x.b+self.b*x.a, self.p)
    __rmul__ = __mul__
    def inv(self):
        t = pow(self.a, -1, self.p)
        return Dual(t, -self.b*t*t, self.p)
    def __truediv__(self, x):
        return self*self.coerce(x).inv()
    def __pow__(self, n):
        r = Dual(1, 0, self.p)
        for _ in range(n):
            r = r*self
        return r
    def pair(self):
        return [self.a, self.b]

def family(p, name):
    z = lambda a,b=0: Dual(a,b,p)
    if name == "V":
        s = z(5,1)
        return [6*s-27, s*s-18*s+54, z(3), s]
    q = [z(3), z(-11), z(3), z(5)]
    return gauge(q,z(1,1)) if name == "G" else q

def gauge(q,u):
    return [q[0]*u**4,q[1]*u**6,q[2]*u**2,q[3]*u**3]

def calculate(p,name,u0,v,c):
    q = family(p,name)
    base = q[2]**2/q[0]
    q = gauge(q,Dual(u0,u0*v,p))
    before = q[2]**2/q[0]
    q = [Dual(t.a,c*t.b,p) for t in q]
    F = q[2]**2/q[0]
    residual = q[3]**2-q[2]**3-q[0]*q[2]-q[1]
    neg = [q[0],q[1],q[2],-q[3]]
    Fneg = neg[2]**2/neg[0]
    return dict(coords=[x.pair() for x in q],negative_coords=[x.pair() for x in neg],
                F=F.pair(),Fneg=Fneg.pair(),base=base.pair(),before=before.pair(),
                incidence=residual.pair())

def point_count(p):
    # Actual exhaustive x,y enumeration, independent of Hasse coefficient.
    return 1+sum((y*y-x*x*x-3*x+11)%p == 0 for x in range(p) for y in range(p))
