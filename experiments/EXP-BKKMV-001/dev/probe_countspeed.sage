# Dev probe: time the uint32 counting engine on the heaviest m=4 and m=5 cells.
import time, random, json, sys
exec(open('experiments/EXP-BKKMV-001/bkkmv1_cert.sage').read().split('# ---------------- stage: poly')[0].replace('import sys, os, json, time, random, subprocess','').replace('T0 = time.time()','T0=0'))

def bench(seed, p, m):
    n = m - 1
    A, B = gen_curve(seed, p)
    polys = semaev_polys(A, B, GF(p), m)
    Sm = polys[m]
    ts, losses, tries, proj = pick_sections(Sm, A, B, p, m, seed)
    fsec = [section_poly(Sm, t, m) for t in ts]
    monoms = [monom_list(f, n, p) for f in fsec]
    t0 = time.time()
    cnt = count_torus(monoms, n, p)
    dt = time.time() - t0
    print(json.dumps({"m": int(m), "p": int(p), "seed": int(seed), "count": jsanitize(cnt), "seconds": float(dt),
                      "losses": [int(x) for x in losses], "supp_sizes": [int(len(mn)) for mn in monoms]}))
    sys.stdout.flush()

bench(20260717, 1009, 4)
bench(20260717, 101, 5)
