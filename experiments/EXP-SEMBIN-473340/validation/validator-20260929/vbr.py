"""Validator's BLIND Boolean-ring first-fall kernel for EXP-SEMBIN-473340.

Written by the validator (VAL-20260929-sembin473340) from the written
definitions ONLY:
  * specification.yaml inputs.observable_naming_NA4
  * research/FFD_SEMAEV_MEASUREMENT1.md section 0
BEFORE reading experiments/EXP-SEMBIN-473340/src/boolean_macaulay.py,
experiments/EXP-SEMBIN-473340/src/test_boolean_macaulay.py,
experiments/EXP-SEMBIN-473340/runs/ or experiments/EXP-SEMBIN-e76704/validation/.

Ring: B = F_2[u_0..u_{N-1}]/(u_j^2 + u_j).  Monomials are squarefree and
represented as bitmasks t in [0, 2^N).  A polynomial is a frozenset of
monomials (coefficients in F_2), or, for linear algebra, a Python int whose
bit t is the coefficient of monomial t (column index = monomial mask).

Definition (MEASUREMENT1 s0 / spec NA-4 (i)):
    V_D          = span of the admissible rows m*f at degree D
    falls(D)     = dim(V_D  cap  R_{<=D-1})
    new_falls(D) = falls(D) - dim V_{D-1}
    d_ff         = min{ D >= 1 : new_falls(D) > 0 }, None if none for D <= Dmax
Row admission (NA-4 (ii)):
    reduced : m*f (XOR product) admitted iff deg(m*f) <= D
    formal  : m*f (XOR product) admitted iff deg m + deg f <= D
    legacy  : S = {t | m : t in f} (set-OR, no cancellation), admitted iff
              max deg over S <= D  (control only)
Computation of falls(D) used here (chosen to differ from a
columns-ordered elimination): since every admitted row has degree <= D,
V_D cap R_{<=D-1} is the kernel of the projection of V_D onto its degree-D
homogeneous part, so falls(D) = rank(rows) - rank(rows restricted to the
degree-D columns).
"""
from itertools import combinations


def popc(m):
    return bin(m).count("1")


def xmul(m, f):
    """Boolean-ring product of monomial m with polynomial f (iterable of
    monomials): XOR-accumulate the monomials t|m."""
    acc = set()
    for t in f:
        x = t | m
        if x in acc:
            acc.remove(x)
        else:
            acc.add(x)
    return frozenset(acc)


def ormul(m, f):
    """Superseded set-OR 'product' (control only)."""
    return frozenset(t | m for t in f)


def pdeg(p):
    return max(popc(t) for t in p) if p else -1


def tobits(p):
    r = 0
    for t in p:
        r ^= 1 << t
    return r


def rank(rows):
    """Rank over F_2 of a list of int bit-rows (XOR basis keyed by top bit)."""
    basis = {}
    for r in rows:
        while r:
            h = r.bit_length()
            b = basis.get(h)
            if b is None:
                basis[h] = r
                break
            r ^= b
    return len(basis)


def degmask(N, D):
    m = 0
    for t in range(1 << N):
        if popc(t) == D:
            m |= 1 << t
    return m


def candidate_rows(eqs, N, conv):
    """All nonzero candidate rows as (admission_degree, bits)."""
    out = []
    for f in eqs:
        f = frozenset(f)
        df = pdeg(f)
        for m in range(1 << N):
            if conv == "legacy":
                p = ormul(m, f)
                if not p:
                    continue
                out.append((pdeg(p), tobits_or(p)))
            else:
                p = xmul(m, f)
                if not p:
                    continue
                if conv == "reduced":
                    out.append((pdeg(p), tobits(p)))
                elif conv == "formal":
                    out.append((popc(m) + df, tobits(p)))
                else:
                    raise ValueError(conv)
    return out


def tobits_or(p):
    r = 0
    for t in p:
        r |= 1 << t
    return r


def profile(eqs, N, Dmax, conv):
    """Full fall profile {D: (dimV_D, falls_D, new_falls_D)} for D = 0..Dmax."""
    cand = candidate_rows(eqs, N, conv)
    prof = {}
    prev_dim = 0  # dim V_{-1} = 0
    for D in range(0, Dmax + 1):
        rows = [b for (ad, b) in cand if ad <= D]
        dV = rank(rows)
        top = degmask(N, D)
        dTop = rank([b & top for b in rows])
        falls = dV - dTop
        nf = falls - prev_dim
        prof[D] = (dV, falls, nf)
        prev_dim = dV
    return prof


def dff(prof):
    for D in sorted(prof):
        if D >= 1 and prof[D][2] > 0:
            return D
    return None


# ---------------------------------------------------------------- self tests
def _eval(p, x):
    """Evaluate Boolean polynomial p at point x (bitmask of ones)."""
    v = 0
    for t in p:
        if t & x == t:
            v ^= 1
    return v


def _span(rows):
    S = {0}
    for r in rows:
        S |= {s ^ r for s in S}
    return S


def selftest(seed=12345, trials=300):
    import random
    rng = random.Random(seed)
    # (a) the product fixture from CORR-20260929-616d03
    assert xmul(0b11, [0b01, 0b10]) == frozenset(), "u0u1*(u0+u1) must be 0"
    assert ormul(0b11, [0b01, 0b10]) == frozenset([0b11])
    # (b) XOR product == pointwise product of functions (ANF bijection)
    for _ in range(trials):
        N = rng.randint(1, 6)
        f = frozenset(rng.sample(range(1 << N), rng.randint(1, min(12, 1 << N))))
        m = rng.randrange(1 << N)
        p = xmul(m, f)
        for x in range(1 << N):
            mv = 1 if (m & x) == m else 0
            assert _eval(p, x) == mv * _eval(f, x)
    # (c) rank vs explicit span size
    for _ in range(trials):
        k = rng.randint(1, 9)
        rows = [rng.randrange(1 << 10) for _ in range(k)]
        assert (1 << rank(rows)) == len(_span(rows))
    # (d) falls(D) via kernel-of-projection == falls(D) via explicit span
    #     enumeration of V_D cap R_{<=D-1}, N = 3, all three conventions
    for _ in range(120):
        N = 3
        neq = rng.randint(1, 3)
        eqs = []
        for _ in range(neq):
            f = frozenset(rng.sample(range(1 << N), rng.randint(1, 5)))
            eqs.append(f)
        for conv in ("reduced", "formal", "legacy"):
            prof = profile(eqs, N, 3, conv)
            cand = candidate_rows(eqs, N, conv)
            for D in range(0, 4):
                rows = [b for (ad, b) in cand if ad <= D]
                S = _span(rows)
                low = [v for v in S if all(popc(t) <= D - 1 for t in range(1 << N) if (v >> t) & 1)]
                assert (1 << prof[D][1]) == len(low), (conv, D)
                assert (1 << prof[D][0]) == len(S)
    return "vbr selftest ok"


if __name__ == "__main__":
    print(selftest())
