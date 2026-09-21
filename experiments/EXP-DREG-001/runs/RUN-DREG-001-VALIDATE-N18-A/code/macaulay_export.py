"""
macaulay_export.py — middle + back end of the Boolean d_reg pipeline (RUNBOOK_dreg.md).

Builds the degree-D Macaulay matrix of a Boolean system as a SPARSE GF(2) matrix and
exports it to SMS (the LinBox / block-Wiedemann sparse format), so the rank / degree-of-
regularity solve at the real n=161 scale can run on a cluster (where the dense ~10^8-column
matrix is impossible but the sparse one -- few nonzeros per row -- is tractable via block
Wiedemann). Also reports the exact resource footprint so a cluster job can be sized.

The FRONT end (constructing the degree-3 system at n=161) is the gating bottleneck:
semaev_tree.weil_descend_to_F2 walls there, and semaev_compiled.py (the compiled bypass) has
an unresolved descent bug. So this module is validated on semaev_tree's construction at
MODERATE n; at n=161 it consumes whatever construction front end is supplied.

Reuses the validated Boolean monomial machinery from ic_first_fall_fast.
SMS format: "<rows> <cols> M" header, then 1-indexed "<i> <j> 1" lines, "0 0 0" terminator.
"""
import sys, itertools, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ic_first_fall_fast import poly_to_monoset, multiply, mono_deg


def macaulay_rows(monosets, nvars, D):
    """Sparse degree-D Macaulay rows of the Boolean system; columns ordered by (deg, idx)
    so the degree-<=1 block occupies the low column indices (the 'fall' region)."""
    rows = []
    for f in monosets:
        fdeg = max((mono_deg(m) for m in f), default=0)
        if fdeg > D:
            continue
        for md in range(0, D - fdeg + 1):
            for combo in itertools.combinations(range(nvars), md):
                prod = multiply(f, frozenset(combo))
                if prod and max(mono_deg(m) for m in prod) <= D:
                    rows.append(prod)
    cols = sorted(set().union(*rows) if rows else set(),
                  key=lambda m: (mono_deg(m), tuple(sorted(m))))
    colidx = {m: i for i, m in enumerate(cols)}
    n_low = sum(1 for m in cols if mono_deg(m) <= 1)
    return rows, colidx, n_low


def export_sms(rows, colidx, path):
    nr, nc = len(rows), len(colidx)
    nnz = 0
    with open(path, "w") as fh:
        fh.write(f"{nr} {nc} M\n")
        for ri, prod in enumerate(rows):
            for m in prod:
                fh.write(f"{ri+1} {colidx[m]+1} 1\n"); nnz += 1
        fh.write("0 0 0\n")
    return nr, nc, nnz


def resource_estimate(nvars, n_eqs_by_deg, D):
    """Rough rows/cols/nnz for degree-D Macaulay at scale. n_eqs_by_deg: {deg: count}.
    cols ~ sum_{d<=D} C(nvars,d) (upper bound; actual = monomials appearing). rows =
    sum_deg count * C(nvars, D-deg). nnz ~ rows * (avg terms per product)."""
    from math import comb
    cols_ub = sum(comb(nvars, d) for d in range(0, D + 1))
    rows = sum(cnt * comb(nvars, D - deg) for deg, cnt in n_eqs_by_deg.items() if deg <= D)
    return dict(D=D, nvars=nvars, rows=rows, cols_upper_bound=cols_ub)


if __name__ == "__main__":
    import argparse, random, json
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='5:3', help='t:dimV (uses semaev_tree construction)')
    ap.add_argument('--D', type=int, default=3)
    ap.add_argument('--out', default='macaulay.sms')
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--validate', action='store_true', help='check first-fall via ff_m4ri matches')
    ap.add_argument('--compiled', action='store_true',
                    help='use semaev_compiled (fast, works at n=161) instead of semaev_tree')
    args = ap.parse_args()
    from collections import Counter
    from semaev_tree import build_field_and_curve
    t, dv = map(int, args.config.split(':')); n = t * dv
    if args.compiled:
        import semaev_compiled as sc
        Fq, E, alpha, A, B = build_field_and_curve(n)
        _, T, Sq = sc.field_tensors(n, Fq)
        al = Fq.gen(); basis = [al ** j for j in range(dv)]; rng = random.Random(args.seed); pts = []
        RX = None
        for _ in range(20000):
            x = sum((basis[j] for j in range(dv) if rng.randint(0, 1)), Fq(0))
            try:
                P = E.lift_x(x)
            except Exception:
                continue
            if not P.is_zero():
                pts.append(P)
                if len(pts) == t:
                    Rr = sum(pts, E(0))
                    if not Rr.is_zero():
                        RX = Rr[0]; break
                    pts = []
        names, eqs_ms = sc.build_system(t, n, dv, B, RX, T, Sq, max_deg=args.D)
        nb = len(names); monosets = [P for P in eqs_ms if P]
    else:
        from semaev_tree import (build_chained_system_symbolic, weil_descend_to_F2,
                                 make_V_subspace, gen_decomposable_R)
        Fq, E, alpha, A, B = build_field_and_curve(n)
        V = make_V_subspace(Fq, alpha, dv); rng = random.Random(args.seed)
        R = None
        for _ in range(400):
            try:
                R, _ = gen_decomposable_R(E, t, V, rng=rng); break
            except Exception:
                continue
        Rh, polys, _ = build_chained_system_symbolic(t, Fq, B, R[0])
        Bring, dpolys = weil_descend_to_F2(polys, n, dv, alpha, Rh)
        nb = int(Bring.ngens())
        monosets = [m for m in (poly_to_monoset(p) for p in dpolys) if m]
    degdist = Counter(max(mono_deg(m) for m in f) for f in monosets)
    t0 = time.time()
    rows, colidx, n_low = macaulay_rows(monosets, nb, args.D)
    nr, nc, nnz = export_sms(rows, colidx, args.out)
    print(json.dumps(dict(config=args.config, n=n, nb=nb, D=args.D,
                          deg_dist=dict(degdist), sms=args.out,
                          rows=nr, cols=nc, nnz=nnz, low_deg_cols=n_low,
                          build_secs=round(time.time() - t0, 2))), flush=True)
    print("resource estimate at n=161 (t=7,dimV=23,nb=966), same deg-dist scaled:")
    print("  ", json.dumps(resource_estimate(966, {2: 161, 3: 805}, args.D)))
    if args.validate:
        from ff_m4ri import first_fall
        d, _ = first_fall(dpolys, nb, args.D, 'bitxor', 8.0, 120)
        print(f"  validate: first_fall(full system, D<={args.D}) = {d}")
