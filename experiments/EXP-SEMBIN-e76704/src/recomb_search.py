"""D_ff^max separation search.

Question (KN-OPEN-7f0511 item A, recommended first attempt): is there an
invertible F_2 matrix M with D_ff(M) > D_ff(I) for a Weil-descended Semaev
system?  Such an M shows Nagao's D_ff^max and the plain D_ff SEPARATE on
exactly the system class under dispute -- which is the cheap half of the
open problem.

Instrument is REUSED VERBATIM from ffd_semaev.py so numbers are comparable
with the existing cells.  It therefore measures the Boolean-ring (reduced,
"fake") observable, definition #4, not #3.  That limitation is inherited
deliberately: the question here is about M, not about the ring.
"""
import sys, json, itertools, random
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from ffd_semaev import build_system, a_real_xR, popcount

def _tables(N):
    monos = sorted(range(1 << N), key=lambda m: (popcount(m), m))
    idx = {m: i for i, m in enumerate(monos)}
    degs = [popcount(m) for m in monos]
    return monos, idx, degs

def _rows_upto(eqs, D, monos, idx):
    """All m*f_i with deg(m*f_i) <= D, as column bitmasks. Boolean ring."""
    rows = []
    for f in eqs:
        if not f:
            continue
        for m in monos:
            prod = {mm | m for mm in f}
            if max(popcount(x) for x in prod) <= D:
                r = 0
                for x in prod:
                    r |= 1 << idx[x]
                rows.append(r)
    return rows

def _rank_and_lowpart(rows, D, degs):
    """Eliminate degree-D columns first; return (rank, dim of zero-hi subspace)."""
    order = [i for i, d in enumerate(degs) if d == D] + \
            [i for i, d in enumerate(degs) if d < D]
    piv = []
    for r in rows:
        cur = r
        for p, pr in piv:
            if (cur >> p) & 1:
                cur ^= pr
        if cur:
            for col in order:
                if (cur >> col) & 1:
                    piv.append((col, cur)); break
    return len(piv), sum(1 for col, _ in piv if degs[col] < D)

def new_falls_at(eqs, N, D, tabs=None):
    """new_falls(D) = dim(V_D cap R_{<D}) - dim V_{D-1}, exactly as ffd_semaev."""
    monos, idx, degs = tabs or _tables(N)
    rows_D = _rows_upto(eqs, D, monos, idx)
    if not rows_D:
        return 0
    _, lowdim = _rank_and_lowpart(rows_D, D, degs)
    prev = 0
    if D > 1:
        rows_p = _rows_upto(eqs, D - 1, monos, idx)
        if rows_p:
            prev, _ = _rank_and_lowpart(rows_p, D - 1, degs)
    return lowdim - prev

def ffd(eqs, N, Dmax=None, tabs=None):
    tabs = tabs or _tables(N)
    for D in range(1, (Dmax or N) + 1):
        if new_falls_at(eqs, N, D, tabs) > 0:
            return D
    return None

# ---- GL_l(F_2) ----
def invertible(rowsM, l):
    piv = []
    for r in rowsM:
        cur = r
        for p, pr in piv:
            if (cur >> p) & 1:
                cur ^= pr
        if cur:
            for c in range(l):
                if (cur >> c) & 1:
                    piv.append((c, cur)); break
    return len(piv) == l

def all_GL(l):
    for bits in itertools.product(range(1 << l), repeat=l):
        if invertible(list(bits), l):
            yield list(bits)

def sample_GL(l, count, rng):
    seen = set(); out = []
    while len(out) < count:
        M = [rng.randrange(1 << l) for _ in range(l)]
        if invertible(M, l):
            t = tuple(M)
            if t not in seen:
                seen.add(t); out.append(M)
    return out

def recombine(eqs, M):
    """f^(M)_i = XOR of f_j over bits of M_i (F_2 coefficients => symmetric diff)."""
    out = []
    for r in M:
        acc = set()
        for j in range(len(eqs)):
            if (r >> j) & 1:
                acc ^= set(eqs[j])
        out.append(frozenset(acc))
    return out

def run_cell(n, nprime, seed, exhaustive_upto=4, samples=400):
    rng = random.Random(seed)
    xR = a_real_xR(n, 1, 1, rng)
    if xR is None:
        return None
    basis = ([1] + [1 << j for j in range(1, nprime)])[:nprime]
    eqs = build_system(n, nprime, 1, xR, basis)
    l, N = len(eqs), 2 * nprime
    tabs = _tables(N)
    base = ffd(eqs, N, tabs=tabs)
    if base is None:
        return dict(n=n, nprime=nprime, N=N, l=l, base_ffd=None, note="no fall at any D")

    if l <= exhaustive_upto:
        Ms, mode = list(all_GL(l)), f"exhaustive |GL_{l}(F2)|"
    else:
        Ms, mode = sample_GL(l, samples, rng), f"sampled {samples} of GL_{l}(F2)"

    seps, degen, worst = [], 0, base
    for M in Ms:
        req = recombine(eqs, M)
        if any(len(f) == 0 for f in req):
            degen += 1
        if new_falls_at(req, N, base, tabs) > 0:
            continue                      # still falls at base degree: no separation
        d = ffd(req, N, tabs=tabs)
        worst = max(worst, d if d is not None else N + 1)
        seps.append(dict(M=M, ffd=d))
    return dict(n=n, nprime=nprime, N=N, l=l, base_ffd=base, mode=mode,
                n_M=len(Ms), n_separating=len(seps), n_zero_generator=degen,
                D_ff_max_observed=worst,
                example=seps[0] if seps else None)

if __name__ == "__main__":
    cells = [(3,2),(4,2),(5,2),(3,3),(4,3),(5,3),(6,3)]
    out = []
    print(f"{'cell':>10} {'N':>2} {'l':>2} {'D_ff(I)':>8} {'M tried':>8} "
          f"{'separating':>11} {'D_ff^max':>9}  mode")
    print("-" * 88)
    for (n, np_) in cells:
        r = run_cell(n, np_, seed=n * 100 + np_)
        if r is None:
            continue
        out.append(r)
        print(f"n={n} n'={np_:<4} {r['N']:>2} {r['l']:>2} {str(r['base_ffd']):>8} "
              f"{r.get('n_M','-'):>8} {r.get('n_separating','-'):>11} "
              f"{str(r.get('D_ff_max_observed')):>9}  {r.get('mode','')}")
    json.dump(out, open(f"{sys.path[0]}/recomb_results.json", "w"), indent=1)
    print("\nwrote recomb_results.json")
