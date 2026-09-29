"""rtlib -- TASK-20260924-d95e70 (red team, REVIEW-CERTBIN-20260924-3d7e1a) own code.

Written from the specification text (object block) and the review plan only.
Imports NOTHING from experiments/*/impl or verifier/. The archived engine is
imported separately, and only where the card permits (J7/J9 cross-checks).

Contents
  * F_{2^17} = F_2[t]/(t^17 + t^3 + 1): mul, pow, inv, trace.
  * descent(B, xR): f_0..f_16 of S_3(x_1, x_2, x_R) by SYMBOLIC expansion
      S_3 = (x_1 x_2)^2 + x_R^2 x_1^2 + x_R^2 x_2^2 + x_R x_1 x_2 + B,
    x_1 = sum_{j<9} v_j t^j, x_2 = sum_{j<9} v_{9+j} t^j.
  * Boolean ring B = F_2[v]/(v_i^2 + v_i): polynomials are Python sets of
    monomial bit masks; product = XOR-accumulation of ORed masks.
  * Macaulay space over an arbitrary variable list and degree bound, and an
    echelon basis with Python-int rows (bit position = column index, columns
    in ASCENDING degree so the highest set bit is a highest-degree monomial),
    with optional provenance tracking (which input rows XOR to a basis row).
  * A LITERAL mutant closure W_D (every low-lead basis row multiplied at every
    iteration, full re-reduction), written from spec object.mutant_closure_W_D.
"""
from itertools import combinations
import random

N = 17
MOD = (1 << 17) | (1 << 3) | 1
L = 9
NV = 18
NEQ = 17


# ---------------------------------------------------------------- field
def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> N:
            a ^= MOD
    return r


def gpow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gmul(r, a)
        a = gmul(a, a)
        e >>= 1
    return r


def ginv(a):
    assert a != 0
    return gpow(a, (1 << N) - 2)


def gtr(x):
    s, y = 0, x
    for _ in range(N):
        s ^= y
        y = gmul(y, y)
    assert s in (0, 1)
    return s


def tpow(e):
    return gpow(2, e)  # t = 2 as a bit vector


# ---------------------------------------------------------------- descent
def descent(B, xR):
    """Returns [f_0..f_16], each a frozenset of monomial masks over v_0..v_17."""
    coef = {}

    def add(m, c):
        coef[m] = coef.get(m, 0) ^ c

    xR2 = gmul(xR, xR)
    for i in range(L):
        for j in range(L):
            m = (1 << i) | (1 << (L + j))
            add(m, tpow(2 * (i + j)) ^ gmul(xR, tpow(i + j)))
    for i in range(L):
        add(1 << i, gmul(xR2, tpow(2 * i)))
        add(1 << (L + i), gmul(xR2, tpow(2 * i)))
    add(0, B)
    fs = []
    for k in range(NEQ):
        fs.append(frozenset(m for m, c in coef.items() if (c >> k) & 1))
    return fs


def eval_poly(f, u):
    """f: set of masks; u: assignment bit mask. Returns f(u) in F_2."""
    return sum(1 for m in f if (m & u) == m) & 1


def s3_direct(B, xR, u):
    x1 = sum(((u >> j) & 1) << j for j in range(L))
    x2 = sum(((u >> (L + j)) & 1) << j for j in range(L))
    e = gmul(x1, x2) ^ gmul(x1, xR) ^ gmul(x2, xR)
    return gmul(e, e) ^ gmul(gmul(x1, x2), xR) ^ B


def selftest_descent(B, xR, fs, trials=64, seed=0):
    rng = random.Random(seed)
    for _ in range(trials):
        u = rng.getrandbits(NV)
        val = s3_direct(B, xR, u)
        for k in range(NEQ):
            if eval_poly(fs[k], u) != (val >> k) & 1:
                return False
    return True


# ---------------------------------------------------------------- Boolean ring
def padd(*ps):
    out = set()
    for p in ps:
        out ^= set(p)
    return out


def pmul(p, q):
    out = set()
    for a in p:
        for b in q:
            out ^= {a | b}
    return out


def deg(p):
    return max((bin(m).count("1") for m in p), default=-1)


def ell_of(B, xR, fs):
    """c_k = Tr(t^k / x_R^2); returns (c list, ell = sum c_k f_k as a set)."""
    th = ginv(gmul(xR, xR))
    c = [gtr(gmul(th, tpow(k))) for k in range(NEQ)]
    ell = set()
    for k in range(NEQ):
        if c[k]:
            ell ^= set(fs[k])
    return c, ell


def substitute(p, c0):
    """pi: v_0 -> v_9 + c0 on a polynomial (set of masks)."""
    out = set()
    for m in p:
        if m & 1:
            mm = m & ~1
            out ^= {mm | (1 << 9)}
            if c0:
                out ^= {mm}
        else:
            out ^= {m}
    return out


# ---------------------------------------------------------------- Macaulay
class Space:
    """Monomials of degree <= D over the variables `vars_`, columns in
    ascending degree (bit 0 = constant)."""

    def __init__(self, vars_, D):
        self.vars = list(vars_)
        self.D = D
        mons = []
        for d in range(D + 1):
            for c in combinations(self.vars, d):
                m = 0
                for i in c:
                    m |= 1 << i
                mons.append(m)
        self.mons = mons
        self.col = {m: i for i, m in enumerate(mons)}
        self.coldeg = [bin(m).count("1") for m in mons]
        self.C = len(mons)

    def to_int(self, p):
        r = 0
        for m in p:
            r ^= 1 << self.col[m]
        return r

    def bits(self, r):
        s = bin(r)[:1:-1]  # little-endian string of bits
        return [i for i, ch in enumerate(s) if ch == "1"]

    def to_poly(self, r):
        mons = self.mons
        return {mons[b] for b in self.bits(r)}

    def multipliers(self, dmax):
        out = []
        for d in range(dmax + 1):
            for c in combinations(self.vars, d):
                m = 0
                for i in c:
                    m |= 1 << i
                out.append(m)
        return out


class Echelon:
    """Echelon basis keyed by leading (highest) bit. Optional provenance."""

    def __init__(self, track=False):
        self.rows = {}
        self.prov = {} if track else None
        self.track = track

    def add(self, r, p=0):
        """Reduce r; if nonzero store it. Returns True iff rank increased."""
        rows = self.rows
        if self.track:
            prov = self.prov
            while r:
                lb = r.bit_length() - 1
                br = rows.get(lb)
                if br is None:
                    rows[lb] = r
                    prov[lb] = p
                    return True
                r ^= br
                p ^= prov[lb]
            return False
        while r:
            lb = r.bit_length() - 1
            br = rows.get(lb)
            if br is None:
                rows[lb] = r
                return True
            r ^= br
        return False

    def reduce(self, r):
        rows = self.rows
        while r:
            lb = r.bit_length() - 1
            br = rows.get(lb)
            if br is None:
                return r
            r ^= br
        return 0

    def rank(self):
        return len(self.rows)

    def dims_by_deg(self, coldeg, D):
        cnt = [0] * (D + 1)
        for lb in self.rows:
            cnt[coldeg[lb]] += 1
        out, acc = [], 0
        for d in range(D + 1):
            acc += cnt[d]
            out.append(acc)
        return out


def macaulay(space, eqs, dmu, track=False):
    """Rows mu*f_k, deg mu <= dmu, row index = mu_index * len(eqs) + k.
    Returns (Echelon, row_labels)."""
    ech = Echelon(track=track)
    labels = []
    mus = space.multipliers(dmu)
    idx = 0
    for mu in mus:
        for k, f in enumerate(eqs):
            prod = set()
            for m in f:
                prod ^= {mu | m}
            ech.add(space.to_int(prod), (1 << idx) if track else 0)
            labels.append((mu, k))
            idx += 1
    return ech, labels


def times_var(space, r, j):
    """v_j * (row int) in the same space; caller guarantees the degree bound."""
    bj = 1 << j
    mons, col = space.mons, space.col
    acc = {}
    for b in space.bits(r):
        c = col[mons[b] | bj]
        acc[c] = acc.get(c, 0) ^ 1
    out = 0
    for c, par in acc.items():
        if par:
            out |= 1 << c
    return out


def literal_W(space, eqs, D, max_iter=50):
    """LITERAL W_D (spec object.mutant_closure_W_D): W^(0) = rowspace(M_D);
    W^(i+1) = W^(i) + span{v_j * b : b in a basis of W^(i) cap B_{<=D-1},
    j over space.vars}; stop at the first i with dim W^(i+1) = dim W^(i).
    Every low-degree basis row is multiplied at every iteration.
    Returns dict with dims per iteration, fixpoint index, first iteration
    containing 1, final dims_by_deg, and the final Echelon."""
    ech, _ = macaulay(space, eqs, D - 2)
    dims = [ech.rank()]
    one_first = 0 if 0 in ech.rows else None
    i = 0
    while True:
        low = [r for lb, r in ech.rows.items() if space.coldeg[lb] <= D - 1]
        prods = []
        for r in low:
            for j in space.vars:
                prods.append(times_var(space, r, j))
        new = Echelon()
        new.rows = dict(ech.rows)
        for p in prods:
            new.add(p)
        if new.rank() == dims[-1]:
            break
        i += 1
        ech = new
        dims.append(ech.rank())
        if one_first is None and 0 in ech.rows:
            one_first = i
        if i >= max_iter:
            raise RuntimeError("max_iter")
    return {"dims": dims, "iterations_to_fixpoint": i, "final_dim": dims[-1],
            "one": one_first is not None, "one_first_iteration": one_first,
            "dims_by_deg": ech.dims_by_deg(space.coldeg, D)}, ech
