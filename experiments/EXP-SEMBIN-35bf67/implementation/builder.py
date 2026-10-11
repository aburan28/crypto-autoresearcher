#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 system builder (pure Python, no Sage).

Builds the Weil descent of Semaev 2015 eq. (5) over F_{2^n} = F_2[x]/(f) with
S_3(x1,x2,x3) = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B (curve Y^2 + XY = X^3 + A X^2 + B),
V = span(1, alpha, ..., alpha^{k-1}).

Field elements are Python ints (bit i = coefficient of alpha^i).
A 'Fq-polynomial in Boolean variables' is a dict {monomial_bitmask: Fq element}.
Descended equation l = XOR of the monomials whose coefficient has bit l set.

Variable order: u1_0..u1_{n-1} (t = 3 only), x1_0..x1_{k-1}, x2_..., x3_... .

Also rebuilds the EXP-DREG-001 anchor systems (Sage defaults reproduced without Sage) and
the T11 boolean_null of src/h012_peel_rank.py.
"""
import hashlib
import random
import sys


# ---------------------------------------------------------------- GF(2)[x] helpers
def pmod(a, f):
    df = f.bit_length() - 1
    while a and a.bit_length() - 1 >= df:
        a ^= f << (a.bit_length() - 1 - df)
    return a


def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def mulmod(a, b, f):
    return pmod(pmul(a, b), f)


def powmod(a, e, f):
    r = 1
    a = pmod(a, f)
    while e:
        if e & 1:
            r = mulmod(r, a, f)
        a = mulmod(a, a, f)
        e >>= 1
    return r


def prime_factors(x):
    out, p = [], 2
    while p * p <= x:
        if x % p == 0:
            out.append(p)
            while x % p == 0:
                x //= p
        p += 1
    if x > 1:
        out.append(x)
    return out


def is_irreducible(f):
    """Ben-Or / Rabin test over GF(2)."""
    n = f.bit_length() - 1
    if n <= 0:
        return False
    x = 2
    # x^(2^n) == x mod f
    t = x
    for _ in range(n):
        t = mulmod(t, t, f)
    if t != pmod(x, f):
        return False
    for q in prime_factors(n):
        t = x
        for _ in range(n // q):
            t = mulmod(t, t, f)
        if pgcd(f, t ^ x) != 1:
            return False
    return True


def minimal_weight_irreducible(n):
    """OP-INSTANCE: smallest-a trinomial x^n+x^a+1, else smallest (a,b,c) pentanomial."""
    for a in range(1, n):
        f = (1 << n) | (1 << a) | 1
        if is_irreducible(f):
            return f
    for a in range(3, n):
        for b in range(2, a):
            for c in range(1, b):
                f = (1 << n) | (1 << a) | (1 << b) | (1 << c) | 1
                if is_irreducible(f):
                    return f
    raise ValueError("no pentanomial")


def is_primitive(f):
    n = f.bit_length() - 1
    order = (1 << n) - 1
    if not is_irreducible(f):
        return False
    for q in prime_factors(order):
        if powmod(2, order // q, f) == 1:
            return False
    return True


_CONWAY = {}


def conway(n):
    """Conway polynomial over GF(2) (lexicographically least in Conway order among
    primitive polynomials compatible with all C_d, d | n, d < n). Used only to rebuild
    the EXP-DREG-001 anchors (Sage's default modulus for GF(2^n) when a Conway polynomial
    is in its database); correctness is checked by the anchor system hash."""
    if n in _CONWAY:
        return _CONWAY[n]
    divs = [d for d in range(1, n) if n % d == 0]
    subs = {d: conway(d) for d in divs}
    # Conway order: compare (a_{n-1}, a_{n-2}, ..., a_0) lexicographically.
    for code in range(1 << n):
        # code bits, most significant = a_{n-1}
        coeffs = 0
        for i in range(n):
            if (code >> (n - 1 - i)) & 1:
                coeffs |= 1 << (n - 1 - i)
        f = (1 << n) | coeffs
        if not (f & 1):
            continue
        if not is_primitive(f):
            continue
        ok = True
        for d, cd in subs.items():
            e = ((1 << n) - 1) // ((1 << d) - 1)
            y = powmod(2, e, f)  # alpha^e
            # evaluate cd at y
            acc, deg = 0, cd.bit_length() - 1
            for i in range(deg, -1, -1):
                acc = mulmod(acc, y, f)
                if (cd >> i) & 1:
                    acc ^= 1
            if acc != 0:
                ok = False
                break
        if ok:
            _CONWAY[n] = f
            return f
    raise ValueError("no Conway polynomial found")


class Field:
    def __init__(self, n, f):
        assert f.bit_length() - 1 == n and is_irreducible(f)
        self.n, self.f = n, f
        self.q = 1 << n

    def mul(self, a, b):
        return pmod(pmul(a, b), self.f)

    def sq(self, a):
        return self.mul(a, a)

    def pow(self, a, e):
        return powmod(a, e, self.f)

    def inv(self, a):
        assert a
        return self.pow(a, self.q - 2)

    def sqrt(self, a):
        return self.pow(a, self.q >> 1)

    def tr(self, a):
        t, s = a, a
        for _ in range(self.n - 1):
            s = self.sq(s)
            t ^= s
        assert t in (0, 1)
        return t

    def solve_artin_schreier(self, d):
        """All w in F_q with w^2 + w = d (0 or 2 roots)."""
        if self.tr(d):
            return []
        # linear algebra: map w -> w^2 + w, solve over GF(2)
        n = self.n
        cols = [self.sq(1 << i) ^ (1 << i) for i in range(n)]
        # Gaussian elimination solving sum c_i cols[i] = d
        rows = []  # (vector, combination)
        basis = {}
        for i, c in enumerate(cols):
            comb = 1 << i
            v = c
            while v:
                hb = v.bit_length() - 1
                if hb in basis:
                    bv, bc = basis[hb]
                    v ^= bv
                    comb ^= bc
                else:
                    basis[hb] = (v, comb)
                    break
        v, comb = d, 0
        while v:
            hb = v.bit_length() - 1
            if hb not in basis:
                return []
            bv, bc = basis[hb]
            v ^= bv
            comb ^= bc
        w = comb
        assert self.sq(w) ^ w == d
        return sorted([w, w ^ 1])


# ---------------------------------------------------------------- Fq-polynomials
def padd(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            v = out.get(m, 0) ^ c
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def ppmul(F, p, q):
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = m1 | m2
            v = out.get(m, 0) ^ F.mul(c1, c2)
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def psq(F, p):
    # Frobenius: (sum c m)^2 = sum c^2 m (Boolean m^2 = m, cross terms vanish)
    out = {}
    for m, c in p.items():
        v = out.get(m, 0) ^ F.sq(c)
        if v:
            out[m] = v
        else:
            out.pop(m, None)
    return out


def const(c):
    return {0: c} if c else {}


def var_elem(offset, width):
    """Fq-polynomial sum_{j<width} b_{offset+j} alpha^j."""
    return {1 << (offset + j): 1 << j for j in range(width)}


def S3(F, x1, x2, x3, B):
    s = padd(ppmul(F, x1, x2), ppmul(F, x1, x3), ppmul(F, x2, x3))
    return padd(psq(F, s), ppmul(F, ppmul(F, x1, x2), x3), const(B))


def descend(F, poly):
    eqs = []
    for l in range(F.n):
        e = sorted(m for m, c in poly.items() if (c >> l) & 1)
        eqs.append(e)
    return eqs


def build_system(F, t, k, B, z):
    """Return (N, equations) for eq. (5) at t in {2,3}; equations = list of sorted
    monomial-bitmask lists; zero equations are kept as [] and reported by caller."""
    n = F.n
    if t == 2:
        x1 = var_elem(0, k)
        x2 = var_elem(k, k)
        polys = [S3(F, x1, x2, const(z) if z else {}, B)]
        N = 2 * k
    elif t == 3:
        u = var_elem(0, n)
        x1 = var_elem(n, k)
        x2 = var_elem(n + k, k)
        x3 = var_elem(n + 2 * k, k)
        polys = [S3(F, u, x1, x2, B), S3(F, u, x3, const(z) if z else {}, B)]
        N = n + 3 * k
    else:
        raise ValueError("t must be 2 or 3")
    eqs = []
    for p in polys:
        eqs.extend(descend(F, p))
    return N, eqs


def seed_of(*parts):
    s = "EXP-SEMBIN-35bf67|" + "|".join(str(p) for p in parts)
    return int(hashlib.sha256(s.encode()).hexdigest()[:16], 16)


def primary_instance(cell, stage, i):
    """OP-INSTANCE. Returns dict with field, B, z, system."""
    n, m, t, k = cell
    f = minimal_weight_irreducible(n)
    F = Field(n, f)
    rng = random.Random(seed_of(stage, "%d,%d,%d,%d" % cell, "primary", i))
    B = 0
    while B == 0:
        B = rng.getrandbits(n)
    z = rng.getrandbits(n)
    N, eqs = build_system(F, t, k, B, z)
    return {"cell": list(cell), "stage": stage, "index": i, "arm": "primary",
            "f": f, "A": 1, "B": B, "z": z, "N": N, "equations": eqs}


def boolean_null(eqs, N, rng):
    """T11 boolean_null (src/h012_peel_rank.py): per equation, keep the number of
    monomials of each degree, draw that many distinct random monomials of that degree.
    Monomials are bitmasks; iteration over degrees follows first-appearance order of the
    source equation as in the reference (dict insertion order)."""
    out = []
    for f in eqs:
        by_deg = {}
        for mo in f:
            d = bin(mo).count("1")
            by_deg[d] = by_deg.get(d, 0) + 1
        nf = set()
        for d, cnt in by_deg.items():
            seen = set()
            while len(seen) < cnt:
                mm = 0
                for v in rng.sample(range(N), d):
                    mm |= 1 << v
                if mm not in nf:
                    seen.add(mm)
                    nf.add(mm)
        out.append(sorted(nf))
    return out


def null_instance(cell, stage, i):
    p = primary_instance(cell, stage, i)
    rng = random.Random(seed_of(stage, "%d,%d,%d,%d" % tuple(cell), "null", i))
    neqs = boolean_null([e for e in p["equations"] if e], p["N"], rng)
    return {"cell": list(cell), "stage": stage, "index": i, "arm": "null",
            "source_primary_index": i, "N": p["N"], "equations": neqs,
            "f": p["f"], "B": p["B"], "z": p["z"]}


def write_system(path, N, eqs, meta=None):
    """System file: '# key=value' comment lines, then 'N <N>', 'E <E>', then one line per
    nonzero equation: '<nterms> <hexmask> ...' (constant monomial = 0)."""
    nz = [e for e in eqs if e]
    with open(path, "w") as fh:
        for k, v in (meta or {}).items():
            fh.write("# %s=%s\n" % (k, v))
        fh.write("N %d\nE %d\n" % (N, len(nz)))
        for e in nz:
            fh.write("%d %s\n" % (len(e), " ".join("%x" % mo for mo in e)))
    return len(eqs) - len(nz)


def system_sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------- elliptic curve (char 2)
class Curve:
    """Y^2 + XY = X^3 + A X^2 + B over F_q (points as (x, y) or None for infinity)."""

    def __init__(self, F, A, B):
        self.F, self.A, self.B = F, A, B

    def on(self, P):
        if P is None:
            return True
        F = self.F
        x, y = P
        return F.sq(y) ^ F.mul(x, y) ^ F.mul(F.sq(x), x) ^ F.mul(self.A, F.sq(x)) ^ self.B == 0

    def neg(self, P):
        return None if P is None else (P[0], P[0] ^ P[1])

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 ^ y2 == x2:  # Q = -P
                return None
            # doubling
            if x1 == 0:
                return None
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.sq(lam) ^ lam ^ self.A
            y3 = F.sq(x1) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def lift_x_all(self, x, order="asc"):
        """All points with X = x over F_q; y-order 'asc' or 'desc' by integer value."""
        F = self.F
        rhs = F.mul(F.sq(x), x) ^ F.mul(self.A, F.sq(x)) ^ self.B
        if x == 0:
            ys = [F.sqrt(rhs)]
        else:
            # y = x w, w^2 + w = rhs / x^2
            ws = F.solve_artin_schreier(F.mul(rhs, F.inv(F.sq(x))))
            ys = sorted(F.mul(x, w) for w in ws)
        if order == "desc":
            ys = ys[::-1]
        pts = [(x, y) for y in ys]
        for P in pts:
            assert self.on(P)
        return pts


# ---------------------------------------------------------------- EXP-DREG-001 anchors
def dreg_monosets_hash(monosets_masks):
    """src/h012c_block_m4ri.py monosets_hash on bitmask monomials."""
    h = hashlib.sha256()
    for f in monosets_masks:
        encoded = sorted(tuple(i for i in range(64) if (mo >> i) & 1) for mo in f)
        h.update(len(encoded).to_bytes(8, "big"))
        for mono in encoded:
            h.update(len(mono).to_bytes(4, "big"))
            for v in mono:
                h.update(v.to_bytes(4, "big"))
    return h.hexdigest()


def dreg_anchor_system(n, t=3, ti=0, seed0=2026, yorder="asc", flips=(False, False, False),
                       reverse_vars=True):
    """Rebuild src/h012_peel_rank.build_system(n, t, ti, seed0) without Sage:
    GF(2^n) with Sage's default modulus (Conway), A = 1, B = alpha, V = low-degree
    polynomials, R from gen_decomposable_R with random.Random(seed0 + 1000 ti + n).
    'yorder'/'flips' parametrise the one Sage behaviour not fixed by the source text
    (the order of the two y values returned by lift_x); the system hash decides."""
    k = (n + t - 1) // t
    F = Field(n, conway(n))
    alpha = 2
    A, B = 1, alpha
    E = Curve(F, A, B)
    V = []
    for bits in range(2 ** k):
        V.append(bits)  # sum_j bit_j alpha^j as an int is exactly 'bits'
    rng = random.Random(int(seed0 + 1000 * ti + n))
    cands = []
    for v in V:
        cands.extend(E.lift_x_all(v, yorder))
    idx_sample = _sample_indices(rng, len(cands), t)
    pts = []
    for j, ix in enumerate(idx_sample):
        P = cands[ix]
        if flips[j]:
            P = E.neg(P)
        pts.append(P)
    R = None
    for P in pts:
        R = E.add(R, P)
    assert R is not None
    RX = R[0]
    N, eqs = build_system(F, t, k, B, RX)
    mons = [e for e in eqs if e]
    if reverse_vars:
        # Sage BooleanPolynomialRing(order='degrevlex') reports variable .index() in
        # reversed order (PolyBoRi dp_asc); found by exhaustive R_X search against the
        # recorded EXP-DREG-001 n=15 system hash. Relabelling only; rank-invariant.
        mons = [sorted(_rev_mask(mo, N) for mo in e) for e in mons]
    return {"n": n, "t": t, "k": k, "f": F.f, "N": N, "RX": RX, "equations": mons,
            "system_hash": dreg_monosets_hash(mons), "n_candidates": len(cands),
            "sample": idx_sample, "reverse_vars": reverse_vars}


def _rev_mask(mo, N):
    r = 0
    for i in range(N):
        if (mo >> i) & 1:
            r |= 1 << (N - 1 - i)
    return r


def _sample_indices(rng, n, k):
    """Indices chosen by random.Random.sample(range(n), k) (same draws as sample(pop, k))."""
    return [x for x in rng.sample(range(n), k)]


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "conway":
        for n in map(int, sys.argv[2:]):
            print(n, bin(conway(n)))
    elif cmd == "mwi":
        for n in map(int, sys.argv[2:]):
            print(n, bin(minimal_weight_irreducible(n)))
