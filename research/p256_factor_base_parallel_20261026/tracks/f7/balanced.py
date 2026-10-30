"""Balanced split-model genus-two arithmetic, ANTS2008 Algorithms1--5.

Convention: [D_aff + n*infinity_plus + (2-deg(u)-n)*infinity_minus
             - (infinity_plus+infinity_minus)]. Import collects no panel.
"""
from collections import Counter
import field as f


class Context:
    def __init__(self):
        self.F = [f.B, 0, -3 % f.P, 0, 0, 0, 1]
        self.Hplus, self.Hminus = [0, 0, 0, 1], [0, 0, 0, f.P-1]
        self.E = f.Curve(-3, f.B)
        self.counters = Counter()

    def make(self, u, v, n):
        if type(n) is not int:
            raise ValueError('Infinity balance must be an integer')
        return Divisor(self, tuple(f.poly(u)), tuple(f.poly(v)), int(n))

    def identity(self):
        return self.make([1], [], 1)

    def infinity_difference(self):
        return self.make([1], [], 2)

    def point(self, point, n=0):
        z, w = point
        if (w*w-f.evaluate(self.F, z)) % f.P:
            raise ValueError('Affine point is not on the sextic')
        return self.make([-z, 1], [w], n)

    def pullback(self, point):
        if point is None:
            return self.identity()
        if not self.E.on(point):
            raise ValueError('Point is not on the source elliptic curve')
        return self.make([-point[0], 0, 1], [point[1]], 0)

    def affine_step(self, u, v, infinity_sign=None):
        """Return equivalent affine divisor plus exact infinity counterweights."""
        old_degree = len(u)-1
        original_v = list(v)
        if infinity_sign is not None:
            H = self.Hplus if infinity_sign == 1 else self.Hminus
            v = f.add(H, f.mod(f.sub(v, H), u))
            self.counters['infinity_balance_steps'] += 1
        else:
            self.counters['ordinary_reduction_steps'] += 1
        numerator = f.sub(f.mul(v, v), self.F)
        new_u = f.monic(f.exact_div(numerator, u))
        if not new_u:
            raise ValueError('Square model encountered during reduction')
        new_v = f.mod(f.neg(v), new_u)
        new_degree = len(new_u)-1
        if len(v) == 4 and v[-1] == 1:
            weights = (old_degree-3, 3-new_degree)
        elif len(v) == 4 and v[-1] == f.P-1:
            weights = (3-new_degree, old_degree-3)
        else:
            difference = old_degree-new_degree
            if difference % 2:
                raise ValueError('Nonintegral ordinary infinity counterweight')
            weights = (difference//2, difference//2)
        trace = {'operation': 'infinity_balance' if infinity_sign else 'ordinary_reduction',
                 'old_u': u, 'old_v': original_v, 'function_v': v,
                 'new_u': new_u, 'new_v': new_v, 'counterweights': weights}
        return new_u, new_v, weights, trace


class Divisor:
    def __init__(self, context, u, v, n):
        self.context, self.u, self.v, self.n = context, tuple(u), tuple(v), n
        degree = len(u)-1
        if not u or u[-1] != 1 or not 0 <= degree <= 2:
            raise ValueError('Balanced u must be monic with degree at most two')
        if v and len(v) >= len(u):
            raise ValueError('Balanced v must have degree below u')
        if not 0 <= n <= 2-degree:
            raise ValueError('Invalid infinity balance')
        if f.mod(f.sub(context.F, f.mul(v, v)), u):
            raise ValueError('Mumford congruence fails')
        if f.gcd(f.gcd(u, f.derivative(u)), v) != [1]:
            raise ValueError('Repeated hyperelliptic branch point is not semireduced')

    @property
    def degree(self):
        return len(self.u)-1

    @property
    def m(self):
        return 2-self.degree-self.n

    def record(self):
        return {'u': self.u, 'v': self.v, 'n_plus': self.n, 'm_minus': self.m,
                'base': 'infinity_plus+infinity_minus'}

    def __eq__(self, other):
        return isinstance(other, Divisor) and (self.u, self.v, self.n) == (other.u, other.v, other.n)

    def is_identity(self):
        return self.u == (1,) and not self.v and self.n == 1

    def negate(self):
        return self.context.make(self.u, f.mod(f.neg(self.v), self.u), 2-self.degree-self.n)

    def add(self, other, trace=None):
        if self.context is not other.context:
            raise ValueError('Divisor contexts differ')
        C = self.context
        C.counters['additions'] += 1
        u1, v1, u2, v2 = list(self.u), list(self.v), list(other.u), list(other.v)
        d12, a1, a2 = f.xgcd(u1, u2)
        s, a12, a3 = f.xgcd(d12, f.add(v1, v2))
        b1, b2, b3 = f.mul(a12, a1), f.mul(a12, a2), a3
        u = f.monic(f.exact_div(f.mul(u1, u2), f.mul(s, s)))
        numerator = f.add(f.add(f.mul(f.mul(b1, u1), v2), f.mul(f.mul(b2, u2), v1)),
                          f.mul(b3, f.add(f.mul(v1, v2), C.F)))
        v = f.mod(f.exact_div(numerator, s), u)
        omega_plus = self.n+other.n+len(s)-1
        omega_minus = self.m+other.m+len(s)-1
        C.counters['compositions'] += 1
        steps = [{'operation': 'composition', 'gcd_s': s, 'bezout': [b1, b2, b3],
                  'u': u, 'v': v, 'counterweights': [len(s)-1, len(s)-1]}]
        while len(u)-1 > 3:
            u, v, weights, step = C.affine_step(u, v)
            omega_plus += weights[0]
            omega_minus += weights[1]
            steps.append(step)
        for _ in range(16):
            if omega_plus >= 1 and omega_minus >= 1:
                break
            sign = 1 if omega_plus > omega_minus else -1
            u, v, weights, step = C.affine_step(u, v, sign)
            omega_plus += weights[0]
            omega_minus += weights[1]
            steps.append(step)
        else:
            raise RuntimeError('Infinity balancing exceeded infrastructure guard; result unknown')
        if len(u)-1+omega_plus+omega_minus != 4:
            raise ValueError('Divisor-degree conservation failed')
        result = C.make(u, v, omega_plus-1)
        if result.m != omega_minus-1:
            raise ValueError('Incorrect final infinity bookkeeping')
        if trace is not None:
            trace.extend(steps)
        return result

    def subtract(self, other, trace=None):
        return self.add(other.negate(), trace)

    def mul(self, scalar):
        if scalar < 0:
            return self.negate().mul(-scalar)
        out, point = self.context.identity(), self
        while scalar:
            if scalar & 1:
                out = out.add(point)
            point = point.add(point)
            scalar //= 2
        return out

    def norm(self):
        """Root-free elliptic norm, separate from the class addition algorithm."""
        C = self.context
        C.counters['norm_calls'] += 1
        if self.degree == 0:
            return None
        if self.degree == 1:
            z = -self.u[0] % f.P
            point = (z*z % f.P, self.v[0] if self.v else 0)
        else:
            t, s = self.u[0], self.u[1]
            v0 = self.v[0] if self.v else 0
            v1 = self.v[1] if len(self.v) > 1 else 0
            if s:
                slope = -v1*pow(s, -1, f.P) % f.P
                x = (slope*slope-s*s+2*t) % f.P
                point = (x, (-slope*(t+x)-v0) % f.P)
            elif v1 == 0:
                point = C.E.add((-t % f.P, v0), (-t % f.P, v0))
            elif v0 == 0:
                point = None
            else:
                raise ValueError('Mumford congruence contradicts equal-image case')
        if not C.E.on(point):
            raise ValueError('Norm output is off the source elliptic curve')
        return point


# Independent support arithmetic in Fp[i], i²=-1; p=3 mod4.
def qa(x, y):
    return ((x[0]+y[0]) % f.P, (x[1]+y[1]) % f.P)


def qn(x):
    return (-x[0] % f.P, -x[1] % f.P)


def qs(x, y):
    return qa(x, qn(y))


def qm(x, y):
    return ((x[0]*y[0]-x[1]*y[1]) % f.P, (x[0]*y[1]+x[1]*y[0]) % f.P)


def qi(x):
    denominator = (x[0]*x[0]+x[1]*x[1]) % f.P
    if denominator == 0:
        raise ZeroDivisionError('zero extension-field denominator')
    k = pow(denominator, -1, f.P)
    return x[0]*k % f.P, -x[1]*k % f.P


def qd(x, y):
    return qm(x, qi(y))


def qp(x, k):
    out = (1, 0)
    while k:
        if k & 1:
            out = qm(out, x)
        x = qm(x, x)
        k //= 2
    return out


def qe(coefficients, x):
    out = (0, 0)
    for c in reversed(coefficients):
        out = qa(qm(out, x), (c % f.P, 0))
    return out


def sqrt_fp(value):
    value %= f.P
    candidate = pow(value, (f.P+1)//4, f.P)
    return min(candidate, f.P-candidate) if candidate*candidate % f.P == value else None


def sqrt_fp2(value):
    a, b = value
    if b == 0:
        root = sqrt_fp(a)
        if root is not None:
            return root, 0
        root = sqrt_fp(-a)
        return (0, root) if root is not None else None
    norm_root = sqrt_fp((a*a+b*b) % f.P)
    if norm_root is None:
        return None
    inv2 = (f.P+1)//2
    real = sqrt_fp((a+norm_root)*inv2 % f.P)
    if real is None:
        real = sqrt_fp((a-norm_root)*inv2 % f.P)
    if real in (None, 0):
        raise ArithmeticError('Quadratic square-root construction failed')
    root = (real, b*pow(2*real, -1, f.P) % f.P)
    if qm(root, root) != value:
        raise ArithmeticError('Extension square-root certificate failed')
    return min(root, qn(root))


def ec2_add(point, other):
    if point is None:
        return other
    if other is None:
        return point
    x, y = point
    X, Y = other
    if x == X:
        if qa(y, Y) == (0, 0):
            return None
        slope = qd(qa(qm((3, 0), qm(x, x)), (-3 % f.P, 0)), qm((2, 0), y))
    else:
        slope = qd(qs(Y, y), qs(X, x))
    nx = qs(qs(qm(slope, slope), x), X)
    return nx, qs(qm(slope, qs(x, nx)), y)


def support(divisor):
    if divisor.degree == 0:
        return []
    if divisor.degree == 1:
        roots = [(-divisor.u[0] % f.P, 0)]
    else:
        t, s = divisor.u[0], divisor.u[1]
        delta = (s*s-4*t) % f.P
        root = sqrt_fp(delta)
        if root is not None:
            sd = (root, 0)
        else:
            imaginary = sqrt_fp(-delta)
            if imaginary is None:
                raise ArithmeticError('Quadratic support did not split in Fp2')
            sd = (0, imaginary)
        minus_s = (-s % f.P, 0)
        inv2 = ((f.P+1)//2, 0)
        roots = [qm(qa(minus_s, sd), inv2), qm(qs(minus_s, sd), inv2)]
    points = [(z, qe(divisor.v, z)) for z in roots]
    for z, w in points:
        if qm(w, w) != qe(divisor.context.F, z):
            raise ValueError('Extension support point is not on sextic')
    return points


def independent_norm_points(points):
    out = None
    for z, w in points:
        image = (qm(z, z), w)
        if qm(w, w) != qa(qa(qp(image[0], 3), qm((-3 % f.P, 0), image[0])), (f.B, 0)):
            raise ValueError('Point image is off elliptic curve')
        out = ec2_add(out, image)
    if out is None:
        return None
    if out[0][1] or out[1][1]:
        raise ValueError('Support norm is not Fp-rational; conjugate may be missing')
    return out[0][0], out[1][0]
