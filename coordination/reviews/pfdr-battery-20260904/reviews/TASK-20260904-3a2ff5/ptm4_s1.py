"""PTM-4 (corrected): the s = 1 saturated systems and what the count-1 'artifact tell'
actually detects.  TASK-20260904-3a2ff5."""
import json, os, sys, collections
sys.path.insert(0, "/home/user/crypto-autoresearcher")
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-cbdefb")
from harness.macaulay_fp import ColumnSpace, Ring
import closure as CL
OUT = "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5"
RUNS = "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-cbdefb/runs"

# (a) from the package's own raw records: correlate the count-1 tell with saturation / Z
tab = collections.Counter()
for p in (4099, 16411, 65537):
    raw = json.load(open(os.path.join(RUNS, f"RUN-PFDR-cbdefb-m2-s1-p{p}", "raw-result.json")))
    for arm, recs in (("semaev", [d["semaev"] for d in raw["raw"]["draws"]]),
                      ("noncurve", [d["result"] for d in raw["raw"]["noncurve"]]),
                      ("null1", [o["result"] for d in raw["raw"]["draws"] for o in d.get("null1", [])]),
                      ("null2", [o["result"] for o in raw["raw"]["null2_objects"]])):
        for r in recs:
            if r.get("degenerate"):
                continue
            Z = r["certificate"].get("Z_size")
            h3 = [h for h in r["history"] if h["D"] == 3]
            if not h3:
                continue
            h3 = h3[0]
            tab[(arm, Z, h3["iteration_count"], h3["fall"], h3["dim_W0"], h3["dim_V"],
                 h3.get("dim_I_at_D"))] += 1
rows = [{"arm": k[0], "Z_size": k[1], "iteration_count_at_D3": k[2], "fall_at_D3": k[3],
         "dim_W0": k[4], "dim_V": k[5], "dim_I_at_3": k[6], "count": v}
        for k, v in sorted(tab.items(), key=str)]

# (b) a self-built s = 1 object with a genuine root (Z != empty), showing the same tell
def s3_poly(ring, x1, x2, x3c, a, b):
    R = ring; mul, add = R.mul, R.add
    sc = lambda f, c: {m: (v * c) % R.p for m, v in f.items() if (v * c) % R.p}
    x1x2 = mul(x1, x2); d12 = add(x1, sc(x2, -1))
    t1 = sc(mul(d12, d12), pow(x3c, 2, R.p))
    inner = add(mul(add(x1, x2), add(x1x2, R.constant(a))), R.constant((2 * b) % R.p))
    return R.reduce(add(add(t1, sc(inner, (-2 * x3c) % R.p)),
                        add(mul(add(x1x2, R.constant((-a) % R.p)), add(x1x2, R.constant((-a) % R.p))),
                            sc(add(x1, x2), (-4 * b) % R.p))))

built = {}
p, a, b = 4099, 3245, 455
ring = Ring(p, 2, 0)
e1 = {ring.sq_var(0): 1}; e2 = {ring.sq_var(1): 1}
# choose x_R so that (a_1, a_2) = (1, 0) is a root: x_R a root of S_3(1, 0, X)
import sympy
X = sympy.symbols("X")
ringQ = Ring(p, 0, 1)
xr = None
for cand in range(p):
    if s3_poly(Ring(p, 0, 0), {}, {}, cand, a, b) == {} or True:
        pass
    break
# direct: evaluate S_3(1, 0, cand) mod p over cand
def s3_val(x1, x2, x3, a, b, p):
    return ((x1 - x2) ** 2 * x3 * x3 - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
            + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
roots = [c for c in range(p) if s3_val(1, 0, c, a, b, p) == 0]
built["x_R_roots_of_S3_1_0"] = roots[:5]
for xR in roots[:1]:
    f = s3_poly(ring, e1, e2, xR, a, b)
    cols = ColumnSpace.build(ring, 7)
    r = CL.measure_system(ring, [f], cols, ring.degree(f), 7, engine="sparse",
                          cross_check=False, certificate=True, graded=True)
    built[f"x_R={xR}"] = {"Z_size": r["certificate"]["Z_size"], "d_ff": r["d_ff"], "d_lf": r["d_lf"],
                          "history": [{k: h[k] for k in ("D", "dim_W0", "dim_V", "fall", "fall_dim",
                                                          "iteration_count")} | {"dim_I_at_D": h.get("dim_I_at_D"),
                                       "W0_saturated": h.get("W0_saturated")} for h in r["history"]]}
out = {"package_s1_tell_table": rows, "self_built_s1": built,
       "note": "n = 2, so B_{<=3} = B_{<=2} = B (4 monomials) and D_max = 7 >= n + 1 = 3: "
               "at D = 3 every element of the ring is 'fallen' and W_0(3) is the whole Macaulay "
               "space {S~, a_1 S~, a_2 S~}; whenever dim W_0(3) already equals dim(I cap B), "
               "multiplying the fallen rows inserts nothing and iteration_count = 1 by saturation."}
json.dump(out, open(os.path.join(OUT, "ptm4_s1.json"), "w"), indent=1, default=str)
for r in rows: print(r)
print(json.dumps(built, indent=1)[:1800])
