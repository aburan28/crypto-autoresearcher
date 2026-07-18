# dev/probe_timing.sage — DEV-ONLY timing probe (not an official run).
# Measures actual per-candidate GB wall times for one target at given n values
# to calibrate per-run budgets. Also one MITM target per n.

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ici_lib as L


def probe_crossbred(n_list, t=3, timeout=8.0, fracs=None):
    if fracs is None:
        fracs = [0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1]
    for n in n_list:
        k = (n + t - 1) // t
        Fq, E, alpha, B = L.build_curve(n, 1)
        V = L.make_V_subspace(Fq, alpha, k)
        tgts = L.make_targets(E, t, V, 1, L.cell_seed("crossbred", 1, n))
        if not tgts:
            print("XBRED n=%d: no targets" % n, flush=True)
            continue
        R_X, P_list = tgts[0]
        t0 = time.time()
        Bring, dpolys = L.descend_system(t, Fq, B, R_X, n, k, alpha)
        build_s = time.time() - t0
        nb = Bring.ngens()
        import random
        rng = random.Random(int(1))
        t0 = time.time()
        best, rows, bias = L.crossbred_sweep(
            dpolys, Bring, nb, fracs,
            2, timeout, rng, time.time() + 240.0)
        sweep_s = time.time() - t0
        print("XBRED n=%d nb=%d build=%.1fs sweep=%.1fs best=%s" % (
            n, nb, build_s, sweep_s, best), flush=True)
        for r in rows:
            print("   %s" % r, flush=True)


def probe_mitm(n_list, t=4):
    for n in n_list:
        k = (n + t - 1) // t
        Fq, E, alpha, B = L.build_curve(n, 1)
        V = L.make_V_subspace(Fq, alpha, k)
        from sage.all import PolynomialRing
        Ru = PolynomialRing(Fq, "u")
        tgts = L.make_targets(E, t, V, 1, L.cell_seed("mitm", 1, n))
        if not tgts:
            print("MITM n=%d: no targets" % n, flush=True)
            continue
        R_X, P_list = tgts[0]
        res = L.mitm_t4(Fq, B, V, R_X, Ru, time.time() + 200.0)
        print("MITM n=%d k=%d |V|=%d work=%d wall=%.1fs L1=%d rels=%d exceeded=%s" % (
            n, k, len(V), res["work_units"], res["wall_s"], res["L1_entries"],
            res["n_relations"], res["deadline_exceeded"]), flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "xbred"
    ns = [int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["16"])]
    fracs = ([float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3
             else [0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1])
    if which == "xbred":
        probe_crossbred(ns, fracs=fracs)
    else:
        probe_mitm(ns)
