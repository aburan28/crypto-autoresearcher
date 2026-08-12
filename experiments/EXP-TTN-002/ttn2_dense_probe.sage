# EXP-TTN-002 auxiliary: dense symbolic S6 probe (infrastructure context, NOT evidence).
# Attempts the full symbolic formal-degree resultant S_6 = Res_X(S3(x1,x2,X), S5(X,x3..x6))
# at p=101, seed 20260717 (EXP-TTN-001 dense-baseline analog for m=6).
# Run from repo root: sage experiments/EXP-TTN-002/ttn2_dense_probe.sage
import json, time, random

OUT = "experiments/EXP-TTN-002/runs/RUN-TTN-002-c/probe_dense_S6.json"
p = 101
seed = 20260717
rng = random.Random("curve-%d-%d" % (seed, p))
while True:
    a = rng.randrange(p)
    b = rng.randrange(p)
    if (4 * a * a * a + 27 * b * b) % p != 0:
        break

def s3_sym(R, u, v, w, a, b):
    return ((u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * w
            + (u * v - a) ** 2 - 4 * b * (u + v))

probe = {"p": p, "seed": seed, "curve": {"a": a, "b": b}, "status": "started"}
Fp = GF(p)
R = PolynomialRing(Fp, names=['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'X', 'Z', 'W'])
x1, x2, x3, x4, x5, x6, X, Z, W = R.gens()
t0 = time.time()
S4p = s3_sym(R, Z, x4, W, a, b).resultant(s3_sym(R, W, x5, x6, a, b), W)
probe["t_S4_symbolic_s"] = time.time() - t0
probe["S4_terms"] = len(S4p.monomials())
t1 = time.time()
S5p = s3_sym(R, X, x3, Z, a, b).resultant(S4p, Z)
probe["t_S5_symbolic_s"] = time.time() - t1
probe["S5_terms"] = len(S5p.monomials())
with open(OUT, "w") as fh:
    json.dump(probe, fh, indent=1, default=lambda o: int(o))
t2 = time.time()
S6p = s3_sym(R, x1, x2, X, a, b).resultant(S5p, X)
probe["t_S6_symbolic_s"] = time.time() - t2
probe["S6_terms"] = len(S6p.monomials())
probe["status"] = "completed"
with open(OUT, "w") as fh:
    json.dump(probe, fh, indent=1, default=lambda o: int(o))
print("PROBE DONE", probe)
