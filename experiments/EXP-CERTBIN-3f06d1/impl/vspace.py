"""The factor-base subspace V (l = 9) of F_2[t]/(t^17 + t^3 + 1) and the small
F_2 linear algebra on 17-bit integers used by EXP-CERTBIN-3f06d1.

NEW MODULE (not in the Stage-1 impl). A field element is a 17-bit int, bit j =
coefficient of t^j.

  * VBasis(basis) -- b_0..b_{l-1}; x_1 = sum_j v_j b_j, x_2 = sum_j v_{9+j} b_j.
    comb(u) maps the coordinate vector u (bit j = v_j) to the element;
    coord(x) is the LINEAR-ALGEBRA membership test (reduction against an
    echelon form of the basis with coordinate tracking) and returns u or None.
    R1/R2 use the polynomial basis b_j = t^j (Stage-1 V = {deg < 9}); R3 uses the
    reduced row echelon basis of a random rank-9 9 x 17 matrix.
  * draw_random_V(seed) -- the spec's S_V procedure.
"""
import numpy as np

N = 17
L = 9


def int_rank(vals):
    basis = {}
    for v in vals:
        v = int(v)
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                break
    return len(basis)


def rref_desc(rows, nbits=N):
    """Reduced row echelon form with columns in the order bit nbits-1, ..., bit 0
    (i.e. t^16, ..., t^0). Rows are returned ordered by leading bit DESCENDING
    (row 0 has the highest leading degree). Zero rows are dropped."""
    rows = [int(r) for r in rows]
    out = []
    for col in range(nbits - 1, -1, -1):
        piv = None
        for i, r in enumerate(rows):
            if (r >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        pr = rows.pop(piv)
        rows = [r ^ pr if (r >> col) & 1 else r for r in rows]
        out = [r ^ pr if (r >> col) & 1 else r for r in out]
        out.append(pr)
    return out


class VBasis:
    def __init__(self, basis, label):
        self.basis = [int(b) for b in basis]
        self.l = len(self.basis)
        self.label = label
        self.size = 1 << self.l
        span = [0] * self.size
        for u in range(1, self.size):
            j = (u & -u).bit_length() - 1
            span[u] = span[u & (u - 1)] ^ self.basis[j]
        self.span = span
        self.np_span = np.array(span, dtype=np.int64)
        # echelon form with coordinate tracking (independent of the span table)
        ech = []  # list of (lead_bit, vec, coordmask), kept fully reduced on lead bits
        for j, b in enumerate(self.basis):
            v, m = b, 1 << j
            for lb, ev, em in ech:
                if (v >> lb) & 1:
                    v ^= ev
                    m ^= em
            if v == 0:
                raise ValueError("basis is linearly dependent")
            lb = v.bit_length() - 1
            ech2 = []
            for (elb, ev, em) in ech:
                if (ev >> lb) & 1:
                    ev ^= v
                    em ^= m
                ech2.append((elb, ev, em))
            ech = ech2 + [(lb, v, m)]
        ech.sort(key=lambda t: -t[0])
        self.ech = ech
        self.is_polynomial = self.basis == [1 << j for j in range(self.l)]

    def comb(self, u):
        return self.span[u]

    def coord(self, x):
        """Linear-algebra membership test: returns u with comb(u) = x, or None."""
        u = 0
        for lb, ev, em in self.ech:
            if (x >> lb) & 1:
                x ^= ev
                u ^= em
        return u if x == 0 else None

    def contains(self, x):
        return self.coord(x) is not None

    def as_json(self):
        return {"label": self.label, "l": self.l,
                "basis_b0_to_b8": self.basis,
                "basis_bits_t16_to_t0": [format(b, "017b") for b in self.basis],
                "is_polynomial_basis": self.is_polynomial}


def polynomial_V():
    return VBasis([1 << j for j in range(L)], "polynomial {deg < 9}")


def draw_random_V(seed):
    """S_V: draw 9 x 17 matrices over F_2 (iid Bernoulli(1/2) entries; one
    integers(0, 2, size=(9, 17)) call per matrix, column j <-> t^(16-j)) until
    one has rank 9. V = row space; basis b_0..b_8 = its RREF with columns in the
    order t^16, ..., t^0 (row order: leading degree descending)."""
    g = np.random.Generator(np.random.PCG64(seed))
    rejected = []
    draws = 0
    while True:
        M = g.integers(0, 2, size=(L, N))
        draws += 1
        rows = [int(sum(int(M[i, j]) << (N - 1 - j) for j in range(N))) for i in range(L)]
        rk = int_rank(rows)
        if rk != L:
            rejected.append({"draw": draws, "rank": rk, "rows_bits_t16_to_t0": [format(r, "017b") for r in rows]})
            continue
        basis = rref_desc(rows)
        assert len(basis) == L
        return VBasis(basis, "random rank-9 RREF (S_V)"), {
            "draws": draws, "rank_rejections": len(rejected), "rejected": rejected,
            "accepted_matrix_rows_bits_t16_to_t0": [format(r, "017b") for r in rows],
            "procedure": "one integers(0, 2, size=(9, 17)) call per matrix; column j <-> t^(16-j); accept first rank 9; basis = RREF, columns t^16..t^0, rows by leading degree descending"}


# ---------------------------------------------------------------------------
# small linear algebra on ints (used for hulls, Sigma, restrictions)
# ---------------------------------------------------------------------------
class Echelon:
    """Incremental echelon basis of int vectors (leading = highest bit)."""

    def __init__(self):
        self.rows = {}  # lead bit -> vector

    def reduce(self, v):
        v = int(v)
        while v:
            h = v.bit_length() - 1
            r = self.rows.get(h)
            if r is None:
                return v
            v ^= r
        return 0

    def add(self, v):
        """Insert; return True iff v increased the rank."""
        v = self.reduce(v)
        if v == 0:
            return False
        self.rows[v.bit_length() - 1] = v
        return True

    def rank(self):
        return len(self.rows)

    def basis(self):
        return [self.rows[k] for k in sorted(self.rows, reverse=True)]


def parity(x):
    return int(x).bit_count() & 1


def affine_hull(rs):
    """rs: list of ints (ordered; rs[0] = h_0). Returns (h0, W basis list,
    zero_in_H)."""
    if not rs:
        return None, [], None
    h0 = int(rs[0])
    ech = Echelon()
    for r in rs[1:]:
        ech.add(int(r) ^ h0)
    Wb = ech.basis()
    zero_in_H = (ech.reduce(h0) == 0)
    return h0, Wb, zero_in_H


def in_affine(h0, Wb, x):
    ech = Echelon()
    for w in Wb:
        ech.add(w)
    return ech.reduce(int(x) ^ h0) == 0


def restrict(a, Wb):
    """<a, w_i> for the W basis w_1..w_d, packed as a d-bit int (bit i = w_i)."""
    out = 0
    for i, w in enumerate(Wb):
        if parity(int(a) & w):
            out |= 1 << i
    return out


def solve_affine_system(eqs, nvars):
    """eqs: list of (coeff int over nvars bits, rhs bit). Solve over F_2.
    Returns None if inconsistent, else (particular solution int, kernel basis
    list)."""
    piv = {}  # pivot bit -> (row, rhs), fully reduced
    for a, b in eqs:
        a, b = int(a), int(b)
        for pb, (pr, prhs) in piv.items():
            if (a >> pb) & 1:
                a ^= pr
                b ^= prhs
        if a == 0:
            if b:
                return None
            continue
        pb = a.bit_length() - 1
        for k in list(piv):
            pr, prhs = piv[k]
            if (pr >> pb) & 1:
                piv[k] = (pr ^ a, prhs ^ b)
        piv[pb] = (a, b)
    x0 = 0
    for pb, (pr, prhs) in piv.items():
        if prhs:
            x0 |= 1 << pb
    free = [i for i in range(nvars) if i not in piv]
    kern = []
    for f in free:
        v = 1 << f
        for pb, (pr, prhs) in piv.items():
            if (pr >> f) & 1:
                v |= 1 << pb
        kern.append(v)
    return x0, kern
