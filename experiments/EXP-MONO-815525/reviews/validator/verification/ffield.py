"""Validator's own finite-field / polynomial toolkit.  Written from scratch;
shares no code with implementation/run_census.py."""

# ---------- F_p[T] ----------
def norm(a, p):
    a = [c % p for c in a]
    while a and a[-1] == 0:
        a.pop()
    return a

def deg(a):
    return len(a) - 1

def sub(a, b, p):
    n = max(len(a), len(b))
    return norm([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
                 for i in range(n)], p)

def mulp(a, b, p):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] = (r[i + j] + x * y) % p
    return norm(r, p)

def divmodp(a, b, p):
    a = a[:]; q = [0] * max(0, len(a) - len(b) + 1)
    inv = pow(b[-1], p - 2, p)
    while len(a) >= len(b) and a:
        s = len(a) - len(b)
        c = a[-1] * inv % p
        q[s] = c
        for i, y in enumerate(b):
            a[s + i] = (a[s + i] - c * y) % p
        a = norm(a, p)
    return norm(q, p), a

def gcdp(a, b, p):
    a, b = norm(a[:], p), norm(b[:], p)
    while b:
        a, b = b, divmodp(a, b, p)[1]
    if a:
        inv = pow(a[-1], p - 2, p)
        a = [c * inv % p for c in a]
    return a

def derivp(a, p):
    return norm([(i * a[i]) % p for i in range(1, len(a))], p)

def powmodp(base, e, mod, p):
    r, b = [1], divmodp(base, mod, p)[1]
    while e:
        if e & 1:
            r = divmodp(mulp(r, b, p), mod, p)[1]
        b = divmodp(mulp(b, b, p), mod, p)[1]
        e >>= 1
    return r

def is_squarefree(f, p):
    return deg(gcdp(f, derivp(f, p), p)) == 0

def has_root_Fp(f, p):
    # gcd(T^p - T, f) degree 0  <=>  no root in F_p
    h = powmodp([0, 1], p, f, p)
    return deg(gcdp(sub(h, [0, 1], p), f, p)) > 0

def is_irreducible_deg23(f, p):
    """f monic, deg 2 or 3: irreducible iff no F_p root."""
    return not has_root_Fp(f, p)

def factor_shape(f, p):
    """Independent full factorization-degree multiset for deg<=4, via
    squarefree test + explicit root finding + degree bookkeeping."""
    f = norm(f[:], p)
    d = deg(f)
    if d <= 0:
        return []
    inv = pow(f[-1], p - 2, p)
    f = [c * inv % p for c in f]
    # split off linear factors by trial (p small here), with multiplicity
    shape = []
    g = f[:]
    for a in range(p):
        while deg(g) > 0:
            # evaluate
            v = 0
            for c in reversed(g):
                v = (v * a + c) % p
            if v:
                break
            q, r = divmodp(g, [(-a) % p, 1], p)
            assert not r
            shape.append(1)
            g = q
    dg = deg(g)
    if dg == 0:
        return sorted(shape)
    if dg in (2, 3):
        shape.append(dg)          # no roots left => irreducible
        return sorted(shape)
    if dg == 4:
        # no linear factors: irreducible, (quad)(quad), or (quad)^2
        if not is_squarefree(g, p):
            return sorted(shape + [2, 2])
        h = powmodp([0, 1], p * p, g, p)
        gg = gcdp(sub(h, [0, 1], p), g, p)
        shape += [2, 2] if deg(gg) == 4 else [4]
        return sorted(shape)
    raise ValueError("deg %d" % dg)
