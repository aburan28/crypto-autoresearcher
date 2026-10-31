"""Canonical prime-field polynomial arithmetic; primality is a mathematical premise."""
EVENTS = {}


def event(name, count=1):
    EVENTS[name] = EVENTS.get(name, 0) + count


class ObligationError(ValueError):
    pass


def require(condition, obligation):
    if not condition:
        raise ObligationError(obligation)


def integer(x, name, minimum=0):
    require(type(x) is int and x >= minimum, name)
    return x


def field(p):
    return integer(p, 'prime modulus premise', 2)


def scalar(x, p):
    require(type(x) is int and 0 <= x < p, 'canonical field element')
    return x


def canonical(a, p):
    require(type(a) is list and len(a) > 0, 'polynomial representation')
    for x in a:
        scalar(x, p)
    require(len(a) == 1 or a[-1] != 0, 'trailing polynomial zero')
    return a[:]


def modulus(U):
    require(type(U) is dict and set(U) == {'p', 'coeffs'}, 'quotient field binding')
    p = field(U['p']); u = canonical(U['coeffs'], p)
    require(u[-1] == 1, 'monic quotient modulus')
    return p, u


def interval(p, t, s):
    scalar(t, p); integer(s, 'interval bit count')
    require(s < p.bit_length() and (1 << s) < p, 'injective interval length')


def trim(a):
    a = list(a)
    while len(a) > 1 and not a[-1]:
        a.pop()
    return a or [0]


def add(a, b, p):
    event('polynomial_add')
    return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p
                 for i in range(max(len(a), len(b)))])


def scale(a, c, p):
    event('polynomial_scale')
    return trim([x*c % p for x in a])


def sub(a, b, p):
    return add(a, scale(b, -1, p), p)


def inv(a, p):
    event('field_inversion')
    require(a % p != 0, 'nonzero inverse')
    return pow(a, -1, p)


def mul(a, b, p):
    event('polynomial_multiply')
    c = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i+j] = (c[i+j]+x*y) % p
    return trim(c)


def divrem(a, b, p):
    event('polynomial_division')
    require(b != [0], 'nonzero polynomial divisor')
    a = trim(a); q = [0]*max(1, len(a)-len(b)+1); bi = inv(b[-1], p)
    while a != [0] and len(a) >= len(b):
        j = len(a)-len(b); c = a[-1]*bi % p; q[j] = c
        for i, x in enumerate(b):
            a[i+j] = (a[i+j]-c*x) % p
        a = trim(a)
    return trim(q), a


def rem(a, u, p):
    return divrem(a, u, p)[1]


def exact(a, b, p):
    q, r = divrem(a, b, p); require(r == [0], 'exact polynomial division')
    return q


def power(a, n, p):
    r = [1]
    while n:
        if n & 1:
            r = mul(r, a, p)
        n >>= 1
        if n:
            a = mul(a, a, p)
    return r


def powmod(a, n, u, p):
    event('quotient_power'); event('quotient_exponent_bits', n.bit_length())
    r = rem([1], u, p); a = rem(a, u, p)
    while n:
        if n & 1:
            r = rem(mul(r, a, p), u, p)
        n >>= 1
        if n:
            a = rem(mul(a, a, p), u, p)
    return r


def inverse_mod(a, u, p):
    event('polynomial_extended_euclid')
    r0, r1, s0, s1 = u, rem(a, u, p), [0], [1]
    while r1 != [0]:
        q, r = divrem(r0, r1, p)
        r0, r1, s0, s1 = r1, r, s1, sub(s0, mul(q, s1, p), p)
    require(len(r0) == 1 and r0[0] != 0, 'coprime CRT factors')
    return rem(scale(s0, inv(r0[0], p), p), u, p)


def evaluate(a, x, p):
    event('polynomial_evaluation')
    r = 0
    for c in reversed(a):
        r = (r*x+c) % p
    return r


def valuation(a, x, p):
    if a == [0]:
        return float('inf'), [0]
    n = 0; linear = [(-x) % p, 1]
    while True:
        q, r = divrem(a, linear, p)
        if r != [0]:
            return n, a
        n += 1; a = q


def curve_data(curve):
    require(type(curve) is dict and set(curve) == {'p', 'a', 'b'}, 'curve representation')
    p = field(curve['p']); require(p > 3, 'short Weierstrass characteristic')
    a, b = scalar(curve['a'], p), scalar(curve['b'], p)
    require((4*a*a*a+27*b*b) % p != 0, 'nonsingular curve')
    return p, [b, a, 0, 1]


def verify_quotient_witness(U, t, s, e, curve=None):
    event('quotient_witness_verification')
    p, u = modulus(U); interval(p, t, s); k = len(u)-1
    if curve is not None:
        cp, f = curve_data(curve); require(cp == p, 'curve quotient field match')
    require(type(e) is list, 'idempotent list')
    if not k:
        require(e == [], 'empty quotient witnesses'); return True
    require(len(e) == s, 'idempotent bit count')
    weighted = [t]
    for j, v in enumerate(e):
        v = canonical(v, p); require(len(v) <= k, 'reduced idempotent')
        require(rem(sub(mul(v, v, p), v, p), u, p) == [0], 'idempotence')
        weighted = add(weighted, scale(v, pow(2, j, p), p), p)
    n = rem(sub([0, 1], weighted, p), u, p)
    require(powmod(n, k, u, p) == [0], 'interval nilpotence')
    if curve is not None:
        T = rem(mul(f, sub(powmod(f, (p-1)//2, u, p), [1], p), p), u, p)
        require(powmod(T, k, u, p) == [0], 'rational ordinate support')
    return True
