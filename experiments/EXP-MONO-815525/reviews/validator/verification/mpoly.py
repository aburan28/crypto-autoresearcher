"""Independent multivariate polynomial engine + independent derivation of
S_3, S_4, and the leading T-coefficient c_4.  No sympy, no imported tables.
Validator's own code for EXP-MONO-815525 review (J1)."""
from itertools import permutations

VARS = ("x1", "x2", "x3", "x4", "U", "A", "B", "y1", "y2")
N = len(VARS)
IDX = {v: i for i, v in enumerate(VARS)}
ZERO = (0,) * N


def var(name):
    e = [0] * N
    e[IDX[name]] = 1
    return {tuple(e): 1}


def const(c):
    return {ZERO: c} if c else {}


def add(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            v = out.get(m, 0) + c
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def neg(p):
    return {m: -c for m, c in p.items()}


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = tuple(x + y for x, y in zip(ma, mb))
            v = out.get(m, 0) + ca * cb
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def smul(k, p):
    return {m: k * c for m, c in p.items()} if k else {}


def power(p, n):
    r = const(1)
    for _ in range(n):
        r = mul(r, p)
    return r


def coeffs_in(p, name):
    """dict deg -> polynomial coefficient (that variable removed)."""
    i = IDX[name]
    out = {}
    for m, c in p.items():
        d = m[i]
        mm = list(m)
        mm[i] = 0
        mm = tuple(mm)
        blk = out.setdefault(d, {})
        v = blk.get(mm, 0) + c
        if v:
            blk[mm] = v
        else:
            blk.pop(mm, None)
    return {d: b for d, b in out.items() if b}


def degree_in(p, name):
    cs = coeffs_in(p, name)
    return max(cs) if cs else -1


def coeff_list(p, name):
    """[c0, c1, ...] as polynomials, length deg+1"""
    cs = coeffs_in(p, name)
    d = max(cs) if cs else -1
    return [cs.get(k, {}) for k in range(d + 1)]


def sylvester_resultant(f, g, name):
    """Res_name(f,g) via the Sylvester matrix determinant (permutation
    expansion; matrices here are 4x4 so this is exact and cheap)."""
    fc = coeff_list(f, name)          # low..high
    gc = coeff_list(g, name)
    m, n = len(fc) - 1, len(gc) - 1
    size = m + n
    M = [[const(0) for _ in range(size)] for _ in range(size)]
    for i in range(n):                 # n rows of f
        for k in range(m + 1):
            M[i][i + (m - k)] = fc[k]
    for i in range(m):                 # m rows of g
        for k in range(n + 1):
            M[n + i][i + (n - k)] = gc[k]
    det = {}
    for perm in permutations(range(size)):
        sgn = 1
        seen = list(perm)
        # parity
        par = 0
        vis = [False] * size
        for s in range(size):
            if not vis[s]:
                j, L = s, 0
                while not vis[j]:
                    vis[j] = True
                    j = perm[j]
                    L += 1
                par += L - 1
        sgn = -1 if par % 2 else 1
        term = const(sgn)
        ok = True
        for i in range(size):
            e = M[i][perm[i]]
            if not e:
                ok = False
                break
            term = mul(term, e)
        if ok:
            det = add(det, term)
    return det


def subst(p, mapping):
    """mapping: varname -> polynomial"""
    out = {}
    for m, c in p.items():
        term = const(c)
        for i, d in enumerate(m):
            if d:
                v = VARS[i]
                term = mul(term, power(mapping.get(v, var(v)), d))
        out = add(out, term)
    return out


def to_str(p):
    if not p:
        return "0"
    parts = []
    for m in sorted(p, reverse=True):
        c = p[m]
        s = [] if c == 1 and any(m) else [str(c)]
        for i, d in enumerate(m):
            if d == 1:
                s.append(VARS[i])
            elif d > 1:
                s.append("%s^%d" % (VARS[i], d))
        parts.append("*".join(s))
    return " + ".join(parts)
