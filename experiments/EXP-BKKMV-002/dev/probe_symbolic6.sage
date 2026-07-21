# probe_symbolic6.sage — EXP-BKKMV-002 dev probe (NOT a run)
# Feasibility probe for the OPTIONAL P6 control: direct symbolic computation of ONE
# sectioned S_6 polynomial f = Res_X(S_5(x1..x4, X), S_3(x5, t, X)) over GF(1000003),
# seed 20260717 curve, first valid section t (same stream as the m=6 runs will use).
# If this completes well within ~240 s, P6 (symbolic cross-check) is feasible as RUN-e.
# Writes dev/probe_symbolic6.json with timings and, on success, the exact support
# summary (size, corner vector, per-var maxes) + sha256 of sorted support for
# later comparison against the fiberwise engine. Timeout/kill => P6 censored
# (infrastructure, NOT evidence).

import json, time, random, hashlib, sys

T0 = time.time()
def elapsed(): return time.time() - T0

def jsan(o):
    from sage.rings.integer import Integer
    from sage.rings.rational import Rational
    if isinstance(o, Integer): return int(o)
    if isinstance(o, Rational): return int(o) if o.denominator() == 1 else str(o)
    if isinstance(o, dict): return {str(k): jsan(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [jsan(v) for v in o]
    if isinstance(o, (int, float, str, bool)) or o is None: return o
    try: return float(o)
    except Exception: return str(o)

OUT = "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-BKKMV-002/dev/probe_symbolic6.json"
rec = {"probe": "symbolic6", "seed": 20260717, "p": 1000003, "status": "started", "checkpoints": []}
def ck(msg):
    rec["checkpoints"].append({"t": round(float(elapsed()), 3), "msg": msg})
    sys.stderr.write("[%.1fs] %s\n" % (elapsed(), msg)); sys.stderr.flush()

seed, p = 20260717, 1000003
rngc = random.Random(int(seed * 10000007 + p))
while True:
    A = rngc.randrange(p); B = rngc.randrange(p)
    if (4 * A**3 + 27 * B**2) % p != 0: break
ck("curve A=%d B=%d" % (A, B))

F = GF(p)
R = PolynomialRing(F, 6, 'x')
g = R.gens()
a, b = F(A), F(B)
S3 = (g[0]*g[1] + g[0]*g[2] + g[1]*g[2] + a)**2 - 4*(g[0]*g[1]*g[2] - b)*(g[0] + g[1] + g[2])
s3a = S3.subs({g[2]: g[5]})
s3b = S3.subs({g[0]: g[2], g[1]: g[3], g[2]: g[5]})
S4 = s3a.resultant(s3b, g[5])
ck("S4 done")
s4a = S4.subs({g[3]: g[5]})
s3c = S3.subs({g[0]: g[3], g[1]: g[4], g[2]: g[5]})
S5 = s4a.resultant(s3c, g[5])
ck("S5 done")

def is_qr(u, p):
    u %= p
    return u == 0 or pow(u, (p - 1) // 2, p) == 1

# first valid section candidate from the m=6 stream
rngs = random.Random(int(seed * 10000033 + p * 131 + 6))
t = None
for _ in range(100):
    cand = rngs.randrange(1, p)
    if is_qr((cand**3 + A*cand + B) % p, p):
        t = cand; break
assert t is not None
rec["t"] = int(t)
ck("section t=%d" % t)

A_poly = S5.subs({g[4]: g[5]})                       # S_5(x1..x4, X)
B_poly = S3.subs({g[0]: g[4], g[1]: F(t), g[2]: g[5]})  # S_3(x5, t, X)
ck("start resultant (deg 8 x deg 2)")
tres = time.time()
f6 = A_poly.resultant(B_poly, g[5])
rec["resultant_seconds"] = round(float(time.time() - tres), 3)
ck("resultant done")

supp = sorted(tuple(int(v) for v in e[:5]) for e in f6.exponents())
rec["support_size"] = len(supp)
maxes = [max(e[i] for e in supp) for i in range(5)]
rec["deg_per_var"] = maxes
rec["total_degree_max"] = max(sum(e) for e in supp)
full = 1
for v in maxes: full *= (v + 1)
rec["full_box_size"] = int(full)
corners = []
import itertools
for c in itertools.product(*[[0, v] for v in maxes]):
    corners.append(c in set(supp))
rec["corners_present_count"] = int(sum(corners))
rec["corners_total"] = len(corners)
h = hashlib.sha256()
for e in supp:
    h.update(bytes(e))
    h.update(b";")
rec["support_sha256_sorted"] = h.hexdigest()
rec["status"] = "completed"
rec["wall_seconds"] = round(float(elapsed()), 3)
with open(OUT, "w") as fh:
    json.dump(jsan(rec), fh, indent=1)
print(json.dumps(jsan({k: rec[k] for k in ["status","resultant_seconds","support_size","deg_per_var","corners_present_count","wall_seconds"]})))
