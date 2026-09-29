"""Blind re-derivation driver (validator, VAL-20260929-sembin473340).

REUSED (system construction only, as the task permits, disclosed):
  * experiments/EXP-SEMBIN-473340/src/ffd_semaev_core_v1.py: build_system,
    random_matched, on_curve (imported; its fall_profile is NOT used)
  * indep_basis and the seeding loop: copied verbatim from
    experiments/EXP-SEMBIN-473340/src/remeasure.py lines 30-44 and 59-74
    (which are verbatim from research/verification/ffd_semaev_measure.py).
    remeasure.py is NOT imported because it imports boolean_macaulay.
NOT READ before this file produced its output:
  experiments/EXP-SEMBIN-473340/src/boolean_macaulay.py,
  experiments/EXP-SEMBIN-473340/src/test_boolean_macaulay.py,
  experiments/EXP-SEMBIN-473340/runs/, experiments/EXP-SEMBIN-e76704/validation/.
The first-fall computation is vbr.py (validator's own).

usage: python3 blind_rederive.py OUT.json n,np [n,np ...]
"""
import sys, os, json, random, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, HERE)
sys.path.insert(1, SRC)
from ffd_semaev_core_v1 import build_system, random_matched, on_curve  # noqa: E402
import vbr  # noqa: E402

SEM_DRAWS, NULL_DRAWS = 10, 25
CONVS = ("reduced", "formal", "legacy")


def indep_basis(n, nprime, rng):          # verbatim copy (remeasure.py 30-44)
    for _ in range(400):
        b=[rng.randrange(1,1<<n) for _ in range(nprime)]
        rows=list(b); r=0
        for bit in range(n):
            p=None
            for i in range(r,len(rows)):
                if (rows[i]>>bit)&1: p=i;break
            if p is None: continue
            rows[r],rows[p]=rows[p],rows[r]
            for i in range(len(rows)):
                if i!=r and ((rows[i]>>bit)&1): rows[i]^=rows[r]
            r+=1
        if r==nprime: return b
    return None


def systems(n, npr):
    """Yield ('semaev', s, meta, eqs) and ('null', t, meta, eqs) exactly as the
    frozen loop constructs them."""
    N = 2 * npr; a2 = a6 = 1
    for s in range(SEM_DRAWS):
        rng = random.Random(n * 7919 + npr * 131 + s)
        xs = [x for x in range(1 << n) if any(on_curve(x, y, a2, a6, n) for y in range(1 << n))]
        if not xs:
            continue
        xR = rng.choice(xs); basis = indep_basis(n, npr, rng)
        if basis is None:
            continue
        eqs = build_system(n, npr, a6, xR, basis)
        if not eqs:
            continue
        yield ("semaev", s, dict(xR=xR, basis=basis, seed=n * 7919 + npr * 131 + s), eqs)
        if s == 0:
            for t in range(NULL_DRAWS):
                r2 = random.Random(n * 31 + npr * 7 + t)
                nl = random_matched(eqs, N, r2)
                yield ("null", t, dict(seed=n * 31 + npr * 7 + t), nl)


def run_cell(n, npr):
    N = 2 * npr; Dmax = min(N, 6)
    dist = {k: {c: Counter() for c in CONVS} for k in ("semaev", "null")}
    draws = []
    for kind, idx, meta, eqs in systems(n, npr):
        rec = dict(kind=kind, idx=idx, **meta, neqs=len(eqs),
                   eq_degrees=[vbr.pdeg(f) for f in eqs],
                   n_constant_generators=sum(1 for f in eqs if vbr.pdeg(f) == 0))
        for c in CONVS:
            prof = vbr.profile(eqs, N, Dmax, c)
            d = vbr.dff(prof)
            rec[c] = dict(dff=d, profile={str(D): list(v) for D, v in prof.items()})
            dist[kind][c][d] += 1
        draws.append(rec)
    out = dict(n=n, nprime=npr, N=N, Dmax=Dmax, draws=draws)
    for c in CONVS:
        out[c] = dict(
            semaev={str(k): v for k, v in sorted(dist["semaev"][c].items(), key=lambda kv: (kv[0] is None, kv[0]))},
            null={str(k): v for k, v in sorted(dist["null"][c].items(), key=lambda kv: (kv[0] is None, kv[0]))})
    return out


def main():
    outpath = sys.argv[1]
    cells = [tuple(int(x) for x in a.split(",")) for a in sys.argv[2:]]
    t0 = time.time()
    res = dict(producer="validator blind kernel vbr.py", cells=[])
    for n, npr in cells:
        c0 = time.time()
        r = run_cell(n, npr)
        r["seconds"] = round(time.time() - c0, 2)
        res["cells"].append(r)
        print(json.dumps({k: r[k] for k in ("n", "nprime", "reduced", "formal", "legacy", "seconds")}), flush=True)
    res["elapsed_seconds"] = round(time.time() - t0, 2)
    with open(outpath, "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
