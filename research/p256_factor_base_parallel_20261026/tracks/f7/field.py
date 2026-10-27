"""Small exact arithmetic used by the F7 panel. Importing runs no panel."""
import ast
from collections import Counter

P = 2**256 - 2**224 + 2**192 + 2**96 - 1
R = int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551', 16)
B = int('5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b', 16)
G = (int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296', 16),
     int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5', 16))


def poly(values):
    out = [int(v) % P for v in values]
    while out and out[-1] == 0:
        out.pop()
    return out


def add(a, b):
    return poly([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def neg(a):
    return poly([-v for v in a])


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = (out[i+j] + x*y) % P
    return poly(out)


def scale(a, k):
    return poly([k*x for x in a])


def divmod_poly(a, b):
    a, b = poly(a), poly(b)
    if not b:
        raise ZeroDivisionError('zero polynomial divisor')
    q = [0] * max(0, len(a)-len(b)+1)
    inv = pow(b[-1], -1, P)
    while a and len(a) >= len(b):
        degree = len(a)-len(b)
        c = a[-1]*inv % P
        q[degree] = c
        for j, y in enumerate(b):
            a[degree+j] = (a[degree+j]-c*y) % P
        a = poly(a)
    return poly(q), a


def exact_div(a, b):
    q, rem = divmod_poly(a, b)
    if rem:
        raise ValueError('non-exact polynomial division')
    return q


def mod(a, b):
    return divmod_poly(a, b)[1]


def monic(a):
    a = poly(a)
    return scale(a, pow(a[-1], -1, P)) if a else []


def xgcd(a, b):
    a, b = poly(a), poly(b)
    s0, s1, t0, t1 = [1], [], [], [1]
    while b:
        q, rem = divmod_poly(a, b)
        a, b = b, rem
        s0, s1 = s1, sub(s0, mul(q, s1))
        t0, t1 = t1, sub(t0, mul(q, t1))
    if not a:
        return [], [], []
    k = pow(a[-1], -1, P)
    return scale(a, k), scale(s0, k), scale(t0, k)


def gcd(a, b):
    return xgcd(a, b)[0]


def power(a, k):
    if k < 0:
        raise ValueError('negative polynomial exponent')
    out = [1]
    while k:
        if k & 1:
            out = mul(out, a)
        a = mul(a, a)
        k //= 2
    return out


def evaluate(a, x):
    out = 0
    for c in reversed(a):
        out = (out*x+c) % P
    return out


def derivative(a):
    return poly([i*a[i] for i in range(1, len(a))])


class Rat:
    def __init__(self, numerator=(), denominator=(1,)):
        n, d = poly(numerator), poly(denominator)
        if not d:
            raise ZeroDivisionError('zero rational-function denominator')
        g = gcd(n, d)
        n, d = exact_div(n, g), exact_div(d, g)
        k = pow(d[-1], -1, P)
        self.n, self.d = scale(n, k), scale(d, k)

    @staticmethod
    def convert(value):
        return value if isinstance(value, Rat) else Rat([value])

    def __add__(self, value):
        b = self.convert(value)
        return Rat(add(mul(self.n, b.d), mul(b.n, self.d)), mul(self.d, b.d))
    __radd__ = __add__

    def __neg__(self):
        return Rat(neg(self.n), self.d)

    def __sub__(self, value):
        return self + (-self.convert(value))

    def __rsub__(self, value):
        return self.convert(value) - self

    def __mul__(self, value):
        b = self.convert(value)
        return Rat(mul(self.n, b.n), mul(self.d, b.d))
    __rmul__ = __mul__

    def __truediv__(self, value):
        b = self.convert(value)
        return Rat(mul(self.n, b.d), mul(self.d, b.n))

    def __pow__(self, k):
        if not isinstance(k, int) or not 0 <= k <= 64:
            raise ValueError('unsupported rational exponent')
        return Rat(power(self.n, k), power(self.d, k))

    def at(self, x):
        denominator = evaluate(self.d, x)
        if denominator == 0:
            raise ZeroDivisionError('map has a pole at this affine coordinate')
        return evaluate(self.n, x)*pow(denominator, -1, P) % P


def parse_rat(text, expected_y_degree):
    """Parse public map grammar without eval; return its y-homogeneous factor."""
    tree = ast.parse(text.replace('^', '**'), mode='eval')

    def walk(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return Rat([node.value]), (None if node.value == 0 else 0)
        if isinstance(node, ast.Name) and node.id in ('x', 'y'):
            return (Rat([0, 1]), 0) if node.id == 'x' else (Rat([1]), 1)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            r, degree = walk(node.operand)
            return (-r if isinstance(node.op, ast.USub) else r), degree
        if not isinstance(node, ast.BinOp):
            raise ValueError('unsupported map syntax')
        if isinstance(node.op, ast.Pow):
            if not isinstance(node.right, ast.Constant) or type(node.right.value) is not int:
                raise ValueError('map exponent must be a literal integer')
            left, degree = walk(node.left)
            k = node.right.value
            return left**k, (degree*k if degree is not None else None)
        a, da = walk(node.left)
        b, db = walk(node.right)
        if isinstance(node.op, (ast.Add, ast.Sub)):
            if da is not None and db is not None and da != db:
                raise ValueError('map is not homogeneous in y')
            return (a+b if isinstance(node.op, ast.Add) else a-b), (db if da is None else da)
        if isinstance(node.op, ast.Mult):
            return a*b, (None if da is None or db is None else da+db)
        if isinstance(node.op, ast.Div):
            if db is None:
                raise ZeroDivisionError('zero map denominator')
            return a/b, (None if da is None else da-db)
        raise ValueError('unsupported map operation')

    value, degree = walk(tree.body)
    if degree != expected_y_degree:
        raise ValueError('unexpected y degree in serialized map')
    return value


class Curve:
    def __init__(self, a, b):
        self.a, self.b = int(a) % P, int(b) % P
        self.counters = Counter()

    def on(self, point):
        return point is None or (point[1]**2-point[0]**3-self.a*point[0]-self.b) % P == 0

    def neg(self, point):
        return None if point is None else (point[0], -point[1] % P)

    def add(self, point, other):
        self.counters['add_calls'] += 1
        if point is None:
            return other
        if other is None:
            return point
        x, y = point
        u, v = other
        if x == u:
            if (y+v) % P == 0:
                return None
            self.counters['doubling_calls'] += 1
            slope = (3*x*x+self.a)*pow(2*y, -1, P) % P
        else:
            slope = (v-y)*pow(u-x, -1, P) % P
        X = (slope*slope-x-u) % P
        return X, (slope*(x-X)-y) % P

    def mul(self, k, point):
        self.counters['scalar_mul_calls'] += 1
        if k < 0:
            return self.mul(-k, self.neg(point))
        out = None
        while k:
            if k & 1:
                out = self.add(out, point)
            point = self.add(point, point)
            k //= 2
        return out


def jacobian_add(point, other, a):
    X, Y, Z = point
    U, V, W = other
    if not Z:
        return other
    if not W:
        return point
    A, C = X*W*W % P, U*Z*Z % P
    B0, D = Y*W**3 % P, V*Z**3 % P
    if A == C:
        if B0 != D or Y == 0:
            return 0, 1, 0
        yy = Y*Y % P
        s = 4*X*yy % P
        m = (3*X*X+a*pow(Z, 4, P)) % P
        nx = (m*m-2*s) % P
        return nx, (m*(s-nx)-8*yy*yy) % P, 2*Y*Z % P
    h, rr = (C-A) % P, (D-B0) % P
    hh, hhh = h*h % P, h*h*h % P
    nx = (rr*rr-hhh-2*A*hh) % P
    return nx, (rr*(A*hh-nx)-B0*hhh) % P, h*Z*W % P


def jacobian_affine(point):
    X, Y, Z = point
    if not Z:
        return None
    zi = pow(Z, -1, P)
    return X*zi*zi % P, Y*zi**3 % P


def independent_add(point, other, a):
    x = (0, 1, 0) if point is None else (point[0], point[1], 1)
    y = (0, 1, 0) if other is None else (other[0], other[1], 1)
    return jacobian_affine(jacobian_add(x, y, a))
