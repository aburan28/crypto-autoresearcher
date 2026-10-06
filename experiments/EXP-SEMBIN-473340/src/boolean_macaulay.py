"""Corrected fall-profile instrument for Boolean systems over F_2 (EXP-SEMBIN-473340).

Supersedes the row construction in research/verification/ffd_semaev_core.py
(CORR-20260929-616d03). There, m*f was built as the SET {mm|m for mm in f}, so
monomials that collide after u^2=u collapsed instead of cancelling. Here the
product is accumulated with XOR, so they cancel:  u0u1*(u0+u1) = 0.

Everything is in the Boolean ring R = F_2[u]/(u_j^2+u_j): squarefree monomials
as bitmasks, polynomials as int bitsets over a fixed monomial order.

Two degree conventions, always named in every output (DEC-20260929-d75c82 NA-4):

  reduced : row m*f is in M_D iff deg(reduce(m*f)) <= D.
            This is the observable EXP-SEMBIN-e76704 declared, now computed
            with the correct product.
  formal  : row m*f is in M_D iff deg(m) + deg(f) <= D.
            The standard Macaulay filtration of {f} + field equations; the
            degree a solver actually pays at.

In both:  new_falls(D) = dim(V_D cap R_{<D}) - dim V_{D-1},
          d_ff = min{D : new_falls(D) > 0}.
"""

def popcount(x): return bin(x).count("1")

def bool_mul(f, m):
    """True Boolean product m*f: XOR-accumulate, so colliding monomials cancel."""
    out = set()
    for mm in f:
        out ^= {mm | m}
    return frozenset(out)

def fall_profile(eqs, N, Dmax, convention):
    if convention not in ("reduced", "formal"):
        raise ValueError(convention)
    monos = sorted(range(1 << N), key=lambda m: (popcount(m), m))
    idx = {m: i for i, m in enumerate(monos)}
    degs = [popcount(m) for m in monos]
    fdeg = [max((popcount(m) for m in f), default=-1) for f in eqs]
    def row(P):
        r = 0
        for m in P: r |= 1 << idx[m]
        return r
    def rank_low(rows, D):
        # eliminate on degree-D columns first; rows whose pivot is below D
        # span exactly V_D cap R_{<D}
        order = [i for i, d in enumerate(degs) if d == D] + [i for i, d in enumerate(degs) if d < D]
        piv = []
        for r in rows:
            cur = r
            for p, pr in piv:
                if (cur >> p) & 1: cur ^= pr
            if cur:
                for c in order:
                    if (cur >> c) & 1:
                        piv.append((c, cur)); break
        return len(piv), sum(1 for c, _ in piv if degs[c] < D)
    out = {}
    for D in range(1, Dmax + 1):
        rows = []
        for f, df in zip(eqs, fdeg):
            if df < 0: continue
            for m in monos:
                if convention == "formal":
                    if popcount(m) + df > D: continue
                    P = bool_mul(f, m)
                else:
                    P = bool_mul(f, m)
                    if P and max(popcount(x) for x in P) > D: continue
                if P: rows.append(row(P))
        rk, low = rank_low(rows, D) if rows else (0, 0)
        out[D] = dict(dimVD=rk, lowdim=low)
    for D in sorted(out):
        prev = out[D - 1]["dimVD"] if (D - 1) in out else 0
        out[D]["new_falls"] = out[D]["lowdim"] - prev
    return out

def first_fall(prof):
    for D in sorted(prof):
        if prof[D]["new_falls"] > 0: return D
    return None

def legacy_or_fall_profile(eqs, N, Dmax):
    """The superseded OR-row instrument, reproduced ONLY to report the old value
    beside the corrected one. Never use it as a measurement."""
    monos = sorted(range(1 << N), key=lambda m: (popcount(m), m))
    idx = {m: i for i, m in enumerate(monos)}; degs = [popcount(m) for m in monos]
    out = {}
    for D in range(1, Dmax + 1):
        rows = []
        for f in eqs:
            for m in monos:
                prod = {mm | m for mm in f}
                if max(popcount(x) for x in prod) <= D:
                    r = 0
                    for x in prod: r |= 1 << idx[x]
                    rows.append(r)
        order = [i for i, d in enumerate(degs) if d == D] + [i for i, d in enumerate(degs) if d < D]
        piv = []
        for r in rows:
            cur = r
            for p, pr in piv:
                if (cur >> p) & 1: cur ^= pr
            if cur:
                for c in order:
                    if (cur >> c) & 1: piv.append((c, cur)); break
        out[D] = dict(dimVD=len(piv), lowdim=sum(1 for c, _ in piv if degs[c] < D))
    for D in sorted(out):
        prev = out[D - 1]["dimVD"] if (D - 1) in out else 0
        out[D]["new_falls"] = out[D]["lowdim"] - prev
    return out
