"""Convention sensitivity, PHASE A.

(1) READING 1 executed literally in R = F_p[a] with the field equations adjoined
    (polyring.py), compared cell by cell with the squarefree computation.
(2) READING 2b: the reduced ring with the multiplication condition deg_B(h v) <= D
    (instead of deg(h) + deg_B(v) <= D).  This is the second defensible reading of
    'closed under multiplication' once one works in R/(a^2 - a); if it moved a fall
    degree, the quantity would be convention-dependent and that would be the finding.
"""
import json
import sys
import time

sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/"
                   "pfdr-battery-20260904/reviews/TASK-20260904-42b33a/scripts")

import numpy as np
from hky import (SquarefreeRing, semaev_S3_digit, deg_poly, closure_B, dim_leq,
                 zero_set, ideal_cap_dim, LinSpace, popcount)
from polyring import PolyRing, closure_poly, dim_leq_poly, field_eqs, mask_to_exp
from params import INSTANCES, D_MAX

OUTDIR = ("/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/"
          "reviews/TASK-20260904-42b33a/tables/")


# ---------------------------------------------------------------- reading 2b
def closure_B_2b(ring, gen, D):
    p, n = ring.p, ring.n
    Dm = min(D, n)
    N = ring.ncols(Dm)
    W = LinSpace(N, p)
    dg = deg_poly(gen)
    if dg < 0 or dg > D:
        return W, 0, 0
    W.add_rows(np.array([ring.vec(gen, Dm)]))
    allmon = [m for m in range(1 << n)]
    rounds = productive = 0
    while True:
        rows = []
        for i in range(W.dim):
            e = ring.deg_of_col(Dm, int(W.piv[i]))
            v = W.R[i]
            seg = v[ring.seg(Dm, e):]
            nz = np.nonzero(seg)[0]
            if nz.size == 0:
                continue
            for h in allmon:
                if h == 0:
                    continue
                # deg_B(h v) <= D ?
                t = ring.tgt_full(e, h)
                dg = ring.degs_full(e, h)
                if int(dg[nz].max()) > D:
                    continue
                rows.append(np.bincount(t[nz], weights=seg[nz], minlength=1 << n))
        rounds += 1
        if not rows:
            break
        # map full-ring vectors down to level-D columns
        A = np.array(rows)[:, ring.off[Dm]:]
        grew = W.add_rows(A)
        if not grew:
            break
        productive += 1
    return W, rounds, productive


def _tgt_full(self, e, h):
    key = ("full", e, h)
    t = self._tgt.get(key)
    if t is None:
        src = self.order[self.off[e]:]
        t = np.array([self.pos[m | h] for m in src], dtype=np.int64)
        self._tgt[key] = t
    return t


def _degs_full(self, e, h):
    key = ("deg", e, h)
    t = self._tgt.get(key)
    if t is None:
        src = self.order[self.off[e]:]
        t = np.array([popcount(m | h) for m in src], dtype=np.int64)
        self._tgt[key] = t
    return t


SquarefreeRing.tgt_full = _tgt_full
SquarefreeRing.degs_full = _degs_full


def falls_from(dims, top):
    out = []
    for D in range(1, top + 1):
        if dims[D][0] > dims[D - 1][1]:
            out.append(D)
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {"reading1_polynomial_ring": [], "reading2b_reduced_degB": []}

    if which in ("all", "poly"):
        smax = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 12
        for (p, cs, a, b, ts, xR) in INSTANCES[:nmax]:
            for s in range(2, smax + 1):
                n = 2 * s
                t0 = time.time()
                gen = semaev_S3_digit(p, a, b, xR, s)
                gens = [{mask_to_exp(m, n): c for m, c in gen.items()}] + field_eqs(n)
                dims = {}
                prev = 0
                falls = []
                per_deg = {}
                for D in range(0, D_MAX + 1):
                    pr = PolyRing(n, p, D)
                    W, r, pd = closure_poly(pr, gens, D)
                    lhs = dim_leq_poly(W, pr, D - 1) if D > 0 else 0
                    fall = bool(D > 0 and lhs > prev)
                    per_deg[str(D)] = {"N": pr.N, "dim": W.dim, "lhs": lhs,
                                       "prev": prev, "fall": fall,
                                       "rounds": r, "productive": pd}
                    if fall:
                        falls.append(D)
                    prev = W.dim
                rec = {"p": p, "curve_seed": cs, "target_seed": ts, "s": s,
                       "falls": falls, "d_ff": falls[0] if falls else None,
                       "d_lf": falls[-1] if falls else None,
                       "per_degree": per_deg, "seconds": round(time.time() - t0, 2)}
                out["reading1_polynomial_ring"].append(rec)
                print("R1poly", p, cs, ts, "s=", s, "falls", falls,
                      f"{rec['seconds']}s", flush=True)

    if which in ("all", "2b"):
        smax = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 12
        for (p, cs, a, b, ts, xR) in INSTANCES[:nmax]:
            for s in range(2, smax + 1):
                n = 2 * s
                t0 = time.time()
                gen = semaev_S3_digit(p, a, b, xR, s)
                ring = SquarefreeRing(n, p, D_MAX)
                prev = 0
                falls = []
                per_deg = {}
                for D in range(0, D_MAX + 1):
                    W, r, pd = closure_B_2b(ring, gen, D)
                    lhs = dim_leq(W, ring, D, D - 1) if D > 0 else 0
                    fall = bool(D > 0 and lhs > prev)
                    per_deg[str(D)] = {"dim": W.dim, "lhs": lhs, "prev": prev,
                                       "fall": fall, "rounds": r, "productive": pd}
                    if fall:
                        falls.append(D)
                    prev = W.dim
                rec = {"p": p, "curve_seed": cs, "target_seed": ts, "s": s,
                       "falls": falls, "d_ff": falls[0] if falls else None,
                       "d_lf": falls[-1] if falls else None,
                       "per_degree": per_deg, "seconds": round(time.time() - t0, 2)}
                out["reading2b_reduced_degB"].append(rec)
                print("R2b", p, cs, ts, "s=", s, "falls", falls,
                      f"{rec['seconds']}s", flush=True)

    tag = which + "_" + "_".join(sys.argv[2:])
    with open(OUTDIR + f"variants_{tag}.json", "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("wrote", OUTDIR + f"variants_{tag}.json")


if __name__ == "__main__":
    main()
