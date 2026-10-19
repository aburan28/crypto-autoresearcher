"""Metered arithmetic for public, small prime-field experiment fixtures."""
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class Field:
    p: int
    counts: Counter = field(default_factory=Counter)

    def add(self, x, y):
        self.counts['field_add'] += 1
        return (x+y) % self.p

    def sub(self, x, y):
        self.counts['field_add'] += 1
        return (x-y) % self.p

    def mul(self, x, y):
        self.counts['field_mul'] += 1
        return x*y % self.p

    def inv(self, x):
        self.counts['field_inv'] += 1
        return pow(x, -1, self.p)

    def sqrt(self, x):
        # Calls have their own unit; pow internals are not field-mul counts.
        self.counts['sqrt_calls'] += 1
        x %= self.p
        if not x:
            return 0
        self.counts['modular_pow'] += 1
        if pow(x, (self.p-1)//2, self.p) != 1:
            return None
        if self.p % 4 == 3:
            self.counts['modular_pow'] += 1
            r = pow(x, (self.p+1)//4, self.p)
            return min(r, self.p-r)
        q, s = self.p-1, 0
        while q % 2 == 0:
            q //= 2
            s += 1
        z = 2
        while True:
            self.counts['modular_pow'] += 1
            if pow(z, (self.p-1)//2, self.p) != 1:
                break
            z += 1
        self.counts['modular_pow'] += 3
        c, t, r, m = pow(z,q,self.p), pow(x,q,self.p), pow(x,(q+1)//2,self.p), s
        while t != 1:
            i, square = 0, t
            while square != 1:
                square = self.mul(square, square)
                i += 1
            self.counts['modular_pow'] += 1
            b = pow(c, 1 << (m-i-1), self.p)
            c = self.mul(b,b)
            r, t, m = self.mul(r,b), self.mul(t,c), i
        return min(r,self.p-r)


@dataclass
class Elliptic:
    f: Field
    a2: int
    a4: int
    a6: int

    def rhs(self, x):
        f = self.f
        return f.add(f.mul(x, f.add(f.mul(x, f.add(x,self.a2)), self.a4)),self.a6)

    def on(self, point):
        return point is None or self.f.mul(point[1],point[1]) == self.rhs(point[0])

    def neg(self, point):
        return None if point is None else (point[0], -point[1] % self.f.p)

    def add(self, left, right):
        f = self.f
        f.counts['group_add'] += 1
        if left is None:
            return right
        if right is None:
            return left
        x,y = left
        u,v = right
        if x == u and (y+v) % f.p == 0:
            return None
        if x == u:
            num = f.add(f.add(f.mul(3,f.mul(x,x)),f.mul(2*self.a2,x)),self.a4)
            slope = f.mul(num,f.inv(f.mul(2,y)))
        else:
            slope = f.mul(f.sub(v,y),f.inv(f.sub(u,x)))
        xx = f.sub(f.sub(f.sub(f.mul(slope,slope),self.a2),x),u)
        return xx, f.sub(f.mul(slope,f.sub(x,xx)),y)

    def mul(self, k, point):
        if k < 0:
            return self.mul(-k,self.neg(point))
        out = None
        while k:
            if k & 1:
                out = self.add(out,point)
            point = self.add(point,point)
            k >>= 1
        return out


def trim(poly):
    out = list(poly)
    while len(out)>1 and out[-1] == 0:
        out.pop()
    return out


def padd(f,a,b,sign=1):
    return trim([f.add(a[i] if i<len(a) else 0, sign*(b[i] if i<len(b) else 0))
                 for i in range(max(len(a),len(b)))])


def pmul(f,a,b):
    out = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j] = f.add(out[i+j],f.mul(x,y))
    return trim(out)


def peval(f,poly,x):
    out = 0
    for c in reversed(poly):
        out = f.add(f.mul(out,x),c)
    return out


def pdiv(f,a,b):
    a,b = trim(a),trim(b)
    if b == [0]:
        raise ZeroDivisionError('zero polynomial')
    out = [0]*max(1,len(a)-len(b)+1)
    inverse = f.inv(b[-1])
    while a != [0] and len(a)>=len(b):
        shift = len(a)-len(b)
        c = f.mul(a[-1],inverse)
        out[shift] = c
        for j,x in enumerate(b):
            a[j+shift] = f.sub(a[j+shift],f.mul(c,x))
        a = trim(a)
    return trim(out),a


def interpolate(f,points):
    if len({x for x,y in points}) != len(points):
        raise ValueError('duplicate interpolation abscissa')
    result = [0]
    for i,(x,y) in enumerate(points):
        numerator,denominator = [1],1
        for j,(u,_) in enumerate(points):
            if i != j:
                numerator = pmul(f,numerator,[-u % f.p,1])
                denominator = f.mul(denominator,f.sub(x,u))
        scale = f.mul(y,f.inv(denominator))
        result = padd(f,result,[f.mul(scale,c) for c in numerator])
    return result


def quadratic_roots(f,poly):
    if len(poly) != 3 or not poly[2]:
        return None
    c,b,a = poly
    disc = f.sub(f.mul(b,b),f.mul(4*a,c))
    root = f.sqrt(disc)
    if root is None or root == 0:
        return None
    inv = f.inv(f.mul(2,a))
    return sorted({f.mul(f.sub(-b,root),inv),f.mul(f.add(-b,root),inv)})
