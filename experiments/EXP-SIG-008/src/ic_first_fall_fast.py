"""Crypto-scale IC: FAST first-fall-degree measurement for the Semaev PDP.

Rewrite of ic_solving_degree.py with pure-Python monomial bookkeeping
(no slow Sage polynomial multiplication). A Boolean monomial is a
frozenset of variable indices (x_i^2 = x_i). The product of polynomial f
(a set of monomials) by a multiplier monomial μ is the multiset
{ m ∪ μ : m ∈ f } reduced mod 2 (monomials appearing an even number of
times cancel).

We build the degree-≤D Macaulay matrix over GF(2) and row-reduce to find
the first degree D at which a *linear* (degree ≤ 1) polynomial appears in
the row space. That D is the FIRST-FALL DEGREE d_ff — exactly the
quantity the Petit-Quisquater conjecture claims stays bounded as n grows.

Caps: D ≤ max_D (default 4); hard per-n timeout.
"""
import sys, time, json, signal
from collections import defaultdict
from itertools import combinations
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sage.all import GF, Matrix


def poly_to_monoset(p):
    """Boolean polynomial -> set of frozensets (each = variable indices of a monomial)."""
    monos = set()
    for m in p.monomials():
        idxs = frozenset(g.index() for g in m.variables())
        monos ^= {idxs}  # xor in case of duplicates (shouldn't happen)
    return monos


def mono_deg(mono):
    return len(mono)


def multiply(monoset, mu):
    """Multiply a polynomial (set of monomials) by monomial mu (frozenset).
    Boolean: m*mu = m ∪ mu. Reduce mod 2."""
    counter = defaultdict(int)
    for m in monoset:
        counter[m | mu] ^= 1
    return frozenset(k for k, v in counter.items() if v)


def first_fall_degree(dpolys, nvars, max_D=4):
    """Return (d_ff, n_rows, n_cols) or (None, ...) if not found by max_D."""
    # Represent each input poly as a monoset
    polys = []
    for p in dpolys:
        ms = poly_to_monoset(p)
        if ms:
            polys.append(ms)

    for D in range(2, max_D + 1):
        rows = []
        col_index = {}
        def col_of(mono):
            if mono not in col_index:
                col_index[mono] = len(col_index)
            return col_index[mono]

        for f in polys:
            fdeg = max((mono_deg(m) for m in f), default=0)
            if fdeg > D:
                continue
            max_mult = D - fdeg
            # multiplier monomials of degree 0..max_mult
            mults = [frozenset()]
            for md in range(1, max_mult + 1):
                for combo in combinations(range(nvars), md):
                    mults.append(frozenset(combo))
            for mu in mults:
                prod = multiply(f, mu)
                if not prod:
                    continue
                if max(mono_deg(m) for m in prod) > D:
                    continue
                row = set(col_of(m) for m in prod)
                rows.append(row)

        if not rows:
            continue
        ncols = len(col_index)
        # Build sparse GF(2) matrix
        M = Matrix(GF(2), len(rows), ncols, sparse=True)
        for ri, row in enumerate(rows):
            for c in row:
                M[ri, c] = 1
        M = M.echelon_form()
        # identify columns that are degree-≤1 monomials
        deg_le1_cols = set(c for mono, c in col_index.items() if mono_deg(mono) <= 1)
        for row in M.rows():
            nz = row.nonzero_positions()
            if not nz:
                continue
            if all(c in deg_le1_cols for c in nz):
                return D, len(rows), ncols
    return None, None, None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-list', type=str, default='8,10,12,14,16,18')
    ap.add_argument('--t', type=int, default=3)
    ap.add_argument('--max-D', type=int, default=4)
    ap.add_argument('--per-n-timeout', type=int, default=90)
    ap.add_argument('--n-R', type=int, default=10)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    from semaev_tree import (
        build_field_and_curve, build_chained_system_symbolic,
        weil_descend_to_F2, gen_decomposable_R, make_V_subspace,
    )

    n_list = [int(x) for x in args.n_list.split(',')]
    print(f"=== IC first-fall-degree (fast): t={args.t}, max_D={args.max_D} ===", flush=True)
    print(f"{'n':>4} {'bvars':>6} {'d_ff':>6} {'rows':>8} {'cols':>8} {'time':>8}", flush=True)
    print('-' * 50, flush=True)

    results = []
    out_path = Path(__file__).parent.parent / "results" / f"ic_first_fall_t{args.t}.json"
    out_path.parent.mkdir(exist_ok=True)

    class _TO(Exception):
        pass
    def _h(s, f): raise _TO()
    signal.signal(signal.SIGALRM, _h)

    n_R = args.n_R
    print(f"  (sampling {n_R} random decomposable R per n; reporting d_ff distribution)", flush=True)
    for n in n_list:
        Fq, E, alpha, A, B = build_field_and_curve(n)
        k = (n + args.t - 1) // args.t
        V_sub = make_V_subspace(Fq, alpha, k)
        d_ff_samples = []
        over_count = 0
        t0 = time.time()
        for _ri in range(n_R):
            R = None
            for _ in range(60):
                try:
                    R, _pts = gen_decomposable_R(E, args.t, V_sub); break
                except Exception:
                    continue
            if R is None:
                continue
            Rh, polys, _ = build_chained_system_symbolic(args.t, Fq, B, R[0])
            Bring, dpolys = weil_descend_to_F2(polys, n, k, alpha, Rh)
            nb = Bring.ngens()
            signal.setitimer(signal.ITIMER_REAL, args.per_n_timeout)
            try:
                d_ff, _nr, _nc = first_fall_degree(dpolys, nb, max_D=args.max_D)
            except _TO:
                d_ff = None
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            if d_ff is None:
                over_count += 1
            else:
                d_ff_samples.append(d_ff)
        dt = time.time() - t0
        if d_ff_samples:
            mn, mx = min(d_ff_samples), max(d_ff_samples)
            from statistics import median
            med = median(d_ff_samples)
        else:
            mn = mx = med = None
        results.append({"n": n, "t": args.t, "n_bool": int(nb),
                        "d_ff_min": mn, "d_ff_median": med, "d_ff_max": mx,
                        "n_over_maxD": over_count, "samples": len(d_ff_samples),
                        "time_s": round(dt, 2)})
        print(f"{n:>4} {nb:>6}  d_ff min/med/max = {mn}/{med}/{mx}  "
              f">{args.max_D}: {over_count}/{n_R}  ({dt:.1f}s)", flush=True)
        with open(out_path, 'w') as f:
            json.dump({"t": args.t, "n_R": n_R, "results": results}, f, indent=2)

    print(f"\nResults: {out_path}", flush=True)


if __name__ == '__main__':
    main()
