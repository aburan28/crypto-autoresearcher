# dev/reverify.sage — post-hoc exact verification of planted targets (sidecar artifact).
# Fixes dev/probe-found verifier bug: junctions are computed by ROOT PROPAGATION
# (solve S_3 quadratics), which is exact even for degenerate samples (x-collisions).
# Writes runs/<run-id>/verification.json; does NOT touch raw.json (immutable).

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ici_lib as L
from sage.all import PolynomialRing


def chain_consistent(Fq, B, R_X, P_list):
    """Exists junctions u_1..u_{t-2} making the chained S_3 system zero with
    the planted x-coords. Junctions found by solving quadratics (roots)."""
    def s3(x, y, z):
        return (x * y + x * z + y * z) ** 2 + x * y * z + B
    Ru = PolynomialRing(Fq, "u")
    u = Ru.gen()
    t = len(P_list)
    xs = [P[0] for P in P_list]
    # current partial assignments: list of dicts mapping junction idx -> value
    partials = [[]]  # lists of u values
    # eq 0: S_3(u_1, x_1, x_2) = 0
    poly0 = s3(u, xs[0], xs[1])
    roots = [r for r, _m in poly0.roots()] if poly0 != 0 else []
    partials = [[r] for r in roots]
    for i in range(1, t - 2):
        # middle eqs: S_3(u_i, u_{i+1}, x_{i+2}) = 0 -> solve for u_{i+1}
        newp = []
        for part in partials:
            poly = s3(part[-1], u, xs[i + 1])
            if poly == 0:
                continue
            for r, _m in poly.roots():
                newp.append(part + [r])
        partials = newp
    # final: S_3(u_{t-2}, x_t, R_X) = 0
    for part in partials:
        if s3(part[-1], xs[-1], R_X) == 0:
            return True
    return False


def verify_run(path, t, ladder, run_ids):
    out_all = {}
    for run_id in run_ids:
        rows = []
        for n in ladder:
            k = (n + t - 1) // t
            for curve_seed in (1, 2, 3):
                Fq, E, alpha, B = L.build_curve(n, curve_seed)
                V = L.make_V_subspace(Fq, alpha, k)
                Vset = set(V)
                cseed = L.cell_seed(path, curve_seed, n)
                tgts = L.make_targets(E, t, V, 8, cseed)
                for ti, (R_X, P_list) in enumerate(tgts):
                    mem = all(P[0] in Vset for P in P_list)
                    S = P_list[0]
                    for P in P_list[1:]:
                        S = S + P
                    decomp = (S[0] == R_X)
                    cc = chain_consistent(Fq, B, R_X, P_list)
                    rows.append({"n": int(n), "curve_seed": int(curve_seed), "idx": int(ti),
                                 "membership": bool(mem), "decomposition": bool(decomp),
                                 "chain_consistent": bool(cc)})
        n_all = len(rows)
        summ = {
            "targets": n_all,
            "membership_pass": sum(r["membership"] for r in rows),
            "decomposition_pass": sum(r["decomposition"] for r in rows),
            "chain_consistent_pass": sum(r["chain_consistent"] for r in rows),
        }
        out_all[run_id] = {"summary": summ, "rows": rows}
        with open(os.path.join("runs", run_id, "verification.json"), "w") as f:
            json.dump(out_all[run_id], f, indent=1)
        print(run_id, summ, flush=True)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    verify_run("crossbred", 3, [10, 12, 14, 16, 18, 20, 22, 24, 26],
               ["RUN-EXP-ICI-001-a", "RUN-EXP-ICI-001-f"])
    verify_run("mitm", 4, [8, 12, 16, 20, 24, 28], ["RUN-EXP-ICI-001-c"])
