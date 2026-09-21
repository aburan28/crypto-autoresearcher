# H012 (AUTOLAB_TASKS) -- d_reg past the wall: weight-1/2 peeling + core echelon.
#
# The dense bitset echelon of t2_streaming_dreg.py costs O(rank x ncols) bits:
# ~7 GB at (18, D5), ~30+ GB at (21, D5) -- the wall.
# Phase 1: weight-1 column peeling (fill-in-free, exact).
# Phase 2: weight-2 column elimination. A weight-2 column c sits in rows p, t;
#   eliminate: t := t XOR p, remove p and c. EXACT (Gaussian elimination on c).
#   Weight bookkeeping: only columns in (p intersect t) change (-2); fill-in
#   bounded by a row-size cap, eliminations exceeding it are skipped (column
#   blocked) and left for the dense phase.
# rank = #pivots(w1) + #pivots(w2) + rank(core). Memory O(nnz + fill + core).
#
# Validation (t2): n=18 D=5 sem rank must equal 143882. First direct null
# measurement at (18, D5): pred says 145881.
#
# Run: sage -python src/h012_peel_rank.py --n-list 18 --targets 1 --d 5 --which both --tag _n18
import sys, os, time, json, random, gc
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from sage.all import GF
from semaev_tree import (build_field_and_curve, build_chained_system_symbolic,
                         weil_descend_to_F2, gen_decomposable_R, make_V_subspace)
from ic_first_fall_fast import poly_to_monoset, mono_deg
from macaulay_export import macaulay_rows
from math import comb


def boolean_null(monosets, nb, rng):
    """T11-boolean null: same shape, random monomials (identical to t2)."""
    null = []
    for f in monosets:
        by_deg = {}
        for m in f:
            by_deg.setdefault(len(m), 0)
            by_deg[len(m)] += 1
        nf = set()
        for d, cnt in by_deg.items():
            seen = set()
            while len(seen) < cnt:
                mm = frozenset(rng.sample(range(nb), d))
                if mm not in nf:
                    seen.add(mm)
                    nf.add(mm)
        null.append(nf)
    return null


def semireg_rank_pred(eq_degs, nb, Dmax):
    a = [comb(nb, j) if j <= nb else 0 for j in range(Dmax + 2)]
    for d in eq_degs:
        for j in range(d, Dmax + 2):
            a[j] -= a[j - d]
    HF, ok = [], True
    for d in range(Dmax + 2):
        if not ok or a[d] <= 0:
            HF.append(0)
            if a[d] <= 0:
                ok = False
        else:
            HF.append(a[d])
    pred, tot = {}, 0
    for D in range(0, Dmax + 1):
        tot += comb(nb, D) - HF[D]
        pred[D] = tot
    return pred, HF


def peel_and_rank(rows, colidx, row_cap=300, mem_cap_gb=13.0):
    """Two-phase peeling + dense core echelon. Exact rank."""
    ncols = len(colidx)
    t0 = time.time()
    rows_live = [set(colidx[m] for m in r) for r in rows]
    nrows = len(rows_live)
    nnz0 = sum(len(r) for r in rows_live)
    # column -> rows adjacency (list of lists; live entries filtered lazily)
    col_rows = [[] for _ in range(ncols)]
    for i, r in enumerate(rows_live):
        for c in r:
            col_rows[c].append(i)
    weight = np.array([len(cr) for cr in col_rows], dtype=np.int64)
    w_hist0 = {str(w): int((weight == w).sum()) for w in range(0, 8)}
    csr_s = time.time() - t0

    t1 = time.time()
    dead = np.zeros(nrows, dtype=bool)
    blocked = np.zeros(ncols, dtype=bool)
    stack1 = [int(c) for c in np.nonzero(weight == 1)[0]]
    stack2 = []  # lazy-filled weight-2 stack
    pivots1 = pivots2 = elim2 = 0
    fill_in = 0
    max_row_seen = max((len(r) for r in rows_live), default=0)

    def live_rows_of(c):
        return [r for r in col_rows[c] if not dead[r]]

    # phase 1: weight-1
    while stack1:
        c = stack1.pop()
        if weight[c] != 1 or blocked[c]:
            continue
        r = live_rows_of(c)[0]
        dead[r] = True
        pivots1 += 1
        weight[c] = 0
        for c2 in rows_live[r]:
            if weight[c2] > 0:
                weight[c2] -= 1
                if weight[c2] == 1:
                    stack1.append(int(c2))

    # phase 2: weight-2 with elimination
    stack2 = [int(c) for c in np.nonzero((weight == 2) & ~blocked)[0]]
    while stack2:
        c = stack2.pop()
        if weight[c] != 2 or blocked[c]:
            continue
        lr = live_rows_of(c)
        if len(lr) != 2:
            # stale weight (rows died without weight update consistency); fix
            weight[c] = len(lr)
            if len(lr) != 2:
                continue
        p, t = (lr[0], lr[1]) if len(rows_live[lr[0]]) <= len(rows_live[lr[1]]) else (lr[1], lr[0])
        sp, st_ = rows_live[p], rows_live[t]
        new_size = len(sp) + len(st_) - 2 * len(sp & st_)
        if new_size > row_cap or new_size == 0 and len(sp & st_) == len(sp) and len(sp) == len(st_):
            blocked[c] = True
            continue
        inter = sp & st_
        rows_live[t] = st_ ^ sp
        dead[p] = True
        pivots2 += 1
        elim2 += 1
        fill_in += len(rows_live[t]) - len(st_)
        if len(rows_live[t]) > max_row_seen:
            max_row_seen = len(rows_live[t])
        weight[c] = 0
        for c2 in inter:
            if weight[c2] > 0:
                weight[c2] -= 2
                if weight[c2] == 2:
                    stack2.append(int(c2))
                elif weight[c2] == 1:
                    stack1.append(int(c2))
        # any weight-1 columns produced are handled here (phase-2 stack1 drain)
        while stack1:
            c1 = stack1.pop()
            if weight[c1] != 1 or blocked[c1]:
                continue
            lr1 = live_rows_of(c1)
            if len(lr1) != 1:
                weight[c1] = len(lr1)
                continue
            r1 = lr1[0]
            dead[r1] = True
            pivots1 += 1
            weight[c1] = 0
            for c2 in rows_live[r1]:
                if weight[c2] > 0:
                    weight[c2] -= 1
                    if weight[c2] == 1:
                        stack1.append(int(c2))
                    elif weight[c2] == 2:
                        stack2.append(int(c2))
    peel_s = time.time() - t1

    # --- core
    core_rows_idx = np.nonzero(~dead)[0]
    core_col_ids = np.nonzero(weight > 0)[0]
    n_core_rows, n_core_cols = len(core_rows_idx), len(core_col_ids)
    remap = np.full(ncols, -1, dtype=np.int64)
    remap[core_col_ids] = np.arange(n_core_cols)
    t2_ = time.time()
    piv = {}
    core_rank = 0
    flag = "ok"
    for ri in core_rows_idx:
        r = 0
        for c in rows_live[ri]:
            nc = remap[c]
            if nc >= 0:
                r |= 1 << int(nc)
        while r:
            lead = r.bit_length() - 1
            if lead in piv:
                r ^= piv[lead]
            else:
                piv[lead] = r
                core_rank += 1
                break
        if core_rank * max(n_core_cols, 1) / 8.0 > mem_cap_gb * 1e9:
            flag = "MEM_WALL_CORE"
            break
    core_s = time.time() - t2_
    del piv, col_rows, rows_live
    gc.collect()
    return {"nrows": nrows, "ncols": ncols, "nnz": int(nnz0),
            "w_hist0": w_hist0,
            "pivots_w1": pivots1, "pivots_w2": pivots2,
            "core_rows": n_core_rows, "core_cols": n_core_cols,
            "core_rank": core_rank, "rank": pivots1 + pivots2 + core_rank,
            "fill_in": fill_in, "max_row": max_row_seen,
            "flag": flag, "csr_s": round(csr_s, 1),
            "peel_s": round(peel_s, 1), "core_s": round(core_s, 1)}


def build_system(n, t, ti, seed0):
    k = (n + t - 1) // t
    Fq, E, alpha, A, B = build_field_and_curve(n)
    V = make_V_subspace(Fq, alpha, k)
    rng = random.Random(int(seed0 + 1000 * ti + n))
    R = None
    for _ in range(200):
        try:
            R, _ = gen_decomposable_R(E, t, V, rng=rng)
            break
        except Exception:
            continue
    if R is None:
        return None
    Rh, polys, _ = build_chained_system_symbolic(t, Fq, B, R[0])
    Bring, dpolys = weil_descend_to_F2(polys, n, k, alpha, Rh)
    nb = int(Bring.ngens())
    monosets = [m for m in (poly_to_monoset(p) for p in dpolys) if m]
    eq_degs = [max(mono_deg(m) for m in f) for f in monosets]
    return rng, nb, monosets, eq_degs


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-list', default='18')
    ap.add_argument('--t', type=int, default=3)
    ap.add_argument('--targets', type=int, default=1)
    ap.add_argument('--d', type=int, default=5)
    ap.add_argument('--which', default='both', choices=['sem', 'null', 'both'])
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()

    out_path = Path(__file__).parent.parent / "results" / f"h012_peel_rank{args.tag}.json"
    out = {"experiment": "H012_peel_rank", "t": args.t, "d": args.d, "runs": []}
    if out_path.exists():
        out = json.load(open(out_path))
    print("=== H012: peeling d_reg, t=%d, D=%d, n in %s ===" % (args.t, args.d, args.n_list), flush=True)
    for n in [int(x) for x in args.n_list.split(',')]:
        for ti in range(args.targets):
            built = build_system(n, args.t, ti, args.seed)
            if built is None:
                print("   [n=%d ti=%d] no decomposable R" % (n, ti), flush=True)
                continue
            rng, nb, monosets, eq_degs = built
            pred, HF = semireg_rank_pred(eq_degs, nb, args.d + 1)
            rec = {"n": n, "ti": ti, "nb": nb, "n_eqs": len(monosets),
                   "eq_degs_hist": {str(d): eq_degs.count(d) for d in sorted(set(eq_degs))},
                   "sr_pred_D": pred[args.d]}
            for which in (["sem", "null"] if args.which == "both" else [args.which]):
                ms = monosets if which == "sem" else boolean_null(monosets, nb, rng)
                t0 = time.time()
                rows, colidx, n_low = macaulay_rows(ms, nb, args.d)
                gen_s = time.time() - t0
                st = peel_and_rank(rows, colidx)
                st["gen_s"] = round(gen_s, 1)
                rec[which] = st
                del rows, colidx
                gc.collect()
                # incremental write after EACH system
                out["runs"] = [r for r in out["runs"]
                               if not (r["n"] == n and r["ti"] == ti)]
                out["runs"].append(rec)
                with open(out_path, "w") as fh:
                    json.dump(out, fh, indent=1, default=str)
                print("   [n=%d ti=%d %s] rank=%d (w1=%d w2=%d core=%dx%d core_rank=%d) pred=%d flag=%s" % (
                    n, ti, which, st["rank"], st["pivots_w1"], st["pivots_w2"],
                    st["core_rows"], st["core_cols"], st["core_rank"],
                    pred[args.d], st["flag"]), flush=True)
    print("wrote %s" % out_path, flush=True)


if __name__ == '__main__':
    main()
