"""Two controls the frozen design lacks (red team, TASK-20261023-7b5dc6).

(1) Coefficient-matched null: random curves whose Weierstrass coefficients have the size and
    sign pattern of each run curve (perturbation of a4, a6 by up to ~12%), counted with the same
    convention to H = 3e5.  Generic curves of a given coefficient size have small rank on average
    (Bhargava-Shankar), so this separates 'coefficient size' from 'rank'.
(2) Translation mutation: x = x' + t is an isomorphism over Q with integral coefficients; it
    preserves rank, regulator, torsion, conductor and the discriminant (so the model stays minimal),
    but moves the naive-height window.  If N_E(H) at finite H tracked the Neron constant c_E
    (an isomorphism invariant), it would not move.

Seeds are fixed; output rt_null_output.json.
"""
import json, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rt_lib as L

GRID = [1000, 3000, 10000, 30000, 100000, 300000]
H = 300000
R7 = [0, 0, 0, -10012, 346900]
GZ = [1, -1, 1, -6494556985832, 6351402068900282539]
BK = [1, -1, 1, -1608154463, 25555312501831]


def translate(ai, t):
    a1, a2, a3, a4, a6 = ai
    return [a1, a2 + 3 * t, a3 + a1 * t, a4 + 2 * a2 * t + 3 * t * t, a6 + a4 * t + a2 * t * t + t ** 3]


def run_one(ai):
    t0 = time.time()
    pts = L.enumerate_points(ai, H)
    return {"ainvs": ai, "disc": L.discriminant(ai), "counts": L.counts_from_points(pts, GRID),
            "x_points": sorted({(a, d) for a, d, c in pts}), "seconds": round(time.time() - t0, 1)}


def main():
    which = sys.argv[1]
    out = {"H": H, "grid": GRID, "which": which, "rows": []}
    if which == "null":
        rng = random.Random(20261023)
        for base, k, tag in ((R7, 12, "r7-size"), (BK, 12, "bk-size"), (GZ, 12, "gz-size")):
            for i in range(k):
                a4 = base[3] + rng.randint(-abs(base[3]) // 8, abs(base[3]) // 8)
                a6 = base[4] + rng.randint(-abs(base[4]) // 8, abs(base[4]) // 8)
                ai = [base[0], base[1], base[2], a4, a6]
                if L.discriminant(ai) == 0:
                    continue
                r = run_one(ai); r["family"] = tag
                out["rows"].append(r)
                print(tag, i, r["counts"][100000], r["counts"][H], r["seconds"], "s", flush=True)
    elif which == "translate":
        cases = [("r7", R7, t) for t in (0, 1000, 10000, 100000, 1000000)]
        # GZ: shift the window onto the cluster of source generators near x = 1.5e6 (P4 x=1536847, P7 x=1536949)
        cases += [("gz", GZ, t) for t in (0, 1536898, 1634797)]
        # BK: shift the window off its generator cluster (x ~ 1.5e4..3.4e4)
        cases += [("bk", BK, t) for t in (0, 1000000)]
        for tag, base, t in cases:
            ai = translate(base, t)
            assert L.discriminant(ai) == L.discriminant(base)
            r = run_one(ai); r["family"] = tag; r["t"] = t
            out["rows"].append(r)
            print(tag, t, r["counts"], r["seconds"], "s", flush=True)
    json.dump(out, open(os.path.join(HERE, f"rt_null_{which}_output.json"), "w"), default=str)


if __name__ == "__main__":
    main()
