"""J1 empirical: independently recompute Q_e for every one of the 6,762
disclosed degree-drop instances and decide, per instance, whether the
signature is ROOT-AT-INFINITY or REPEATED-ROOT (they are different, and
this script separates them)."""
import json, sys, time
sys.path.insert(0, ".")
from ffield import *

RAW = "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-815525/runs/RUN-MONO-815525-1/raw-result.json"
tabs = json.load(open("indep_tables.json"))
VARS = tabs["vars"]
S4 = [(tuple(map(int, k.split(","))), v) for k, v in tabs["S4"].items()]
S3 = [(tuple(map(int, k.split(","))), v) for k, v in tabs["S3"].items()]
IX = {v: i for i, v in enumerate(VARS)}

# ---------------- my own F_{p^3} = F_p[X]/(g) ----------------
class F3:
    def __init__(self, p, e1, e2, e3):
        self.p, self.g = p, [(-e3) % p, e2 % p, (-e1) % p, 1]
    def mul(self, a, b):
        p, g = self.p, self.g
        r = [0]*5
        for i in range(3):
            if a[i]:
                for j in range(3):
                    r[i+j] = (r[i+j] + a[i]*b[j]) % p
        # reduce X^3 = e1 X^2 - e2 X + e3   (g = X^3 - e1X^2 + e2X - e3)
        for k in (4, 3):
            c = r[k]
            if c:
                r[k] = 0
                r[k-1] = (r[k-1] - c*g[2]) % p
                r[k-2] = (r[k-2] - c*g[1]) % p
                r[k-3] = (r[k-3] - c*g[0]) % p
        return [r[0] % p, r[1] % p, r[2] % p]
    def add(self, a, b):
        p = self.p
        return [(a[0]+b[0]) % p, (a[1]+b[1]) % p, (a[2]+b[2]) % p]
    def smul(self, k, a):
        p = self.p
        return [k*a[0] % p, k*a[1] % p, k*a[2] % p]
    def pw(self, a, e):
        r, b = [1,0,0], a[:]
        while e:
            if e & 1: r = self.mul(r, b)
            b = self.mul(b, b)
            e >>= 1
        return r

def qe_from_my_S4(p, A, B, e1, e2, e3):
    """Evaluate MY OWN S_4 table at (x1,x2,x3) = the three conjugate roots of
    g in F_{p^3}, x4 = T symbolic.  Returns [c0..c4] over F_{p^3}."""
    F = F3(p, e1, e2, e3)
    X1 = [0, 1, 0]
    X2 = F.pw(X1, p)
    X3 = F.pw(X2, p)
    pw1 = [[1,0,0]]; pw2 = [[1,0,0]]; pw3 = [[1,0,0]]
    for _ in range(4):
        pw1.append(F.mul(pw1[-1], X1)); pw2.append(F.mul(pw2[-1], X2)); pw3.append(F.mul(pw3[-1], X3))
    Apw = [pow(A, k, p) for k in range(5)]
    Bpw = [pow(B, k, p) for k in range(5)]
    out = [[0,0,0] for _ in range(5)]
    for m, co in S4:
        c = co % p
        if not c: continue
        t = F.smul(c * Apw[m[IX["A"]]] * Bpw[m[IX["B"]]] % p, pw1[m[IX["x1"]]])
        t = F.mul(t, pw2[m[IX["x2"]]]); t = F.mul(t, pw3[m[IX["x3"]]])
        k = m[IX["x4"]]
        out[k] = F.add(out[k], t)
    return out, F, X1, X2, X3

def to_Fp(cs, p):
    r = []
    for c in cs:
        if c[1] % p or c[2] % p: return None
        r.append(c[0] % p)
    return r

def s3_of_e(p, A, B, e1, e2, e3):
    return (A*A - 2*A*e2 - 4*B*e1 + e2*e2 - 4*e1*e3) % p

def disc_cubic(c, p):     # c = [c0,c1,c2,c3]
    a, b, cc, d = c[3], c[2], c[1], c[0]
    return (18*a*b*cc*d - 4*b**3*d + b*b*cc*cc - 4*a*cc**3 - 27*a*a*d*d) % p

d = json.load(open(RAW))
devs = list(d["stage_2"]["deviations_sampled"])
for sw in d["stage_1"]["exhaustive_sweep"]:
    devs += sw["deviations_all"]
print("total disclosed degree-drop instances:", len(devs))

t0 = time.time()
stats = {"qe_match": 0, "deg3": 0, "squarefree": 0, "irreducible_cubic": 0,
         "c4_zero": 0, "c3_nonzero": 0, "s3_zero": 0, "lands_in_Fp": 0,
         "disc_nonzero": 0, "g_irreducible": 0}
bad = []
shapes = {}
for i, r in enumerate(devs):
    p, A, B = r["p"], r["A"], r["B"]
    e = r["e"] if "e" in r else [r["e1"], r["e2"], r["e3"]]
    e1, e2, e3 = e
    gpoly = [(-e3) % p, e2 % p, (-e1) % p, 1]
    if not has_root_Fp(gpoly, p): stats["g_irreducible"] += 1
    cs, F, X1, X2, X3 = qe_from_my_S4(p, A, B, e1, e2, e3)
    fp = to_Fp(cs, p)
    if fp is None:
        bad.append((i, "not F_p-rational")); continue
    stats["lands_in_Fp"] += 1
    if fp[4] % p == 0: stats["c4_zero"] += 1
    if fp[3] % p != 0: stats["c3_nonzero"] += 1
    if s3_of_e(p, A, B, e1, e2, e3) == 0: stats["s3_zero"] += 1
    q = norm(fp[:], p)
    rec = norm(list(r.get("Qe") or r["Qe_coeffs_low_to_high"]), p)
    if q == rec: stats["qe_match"] += 1
    else: bad.append((i, "Qe mismatch", q, rec))
    if deg(q) == 3: stats["deg3"] += 1
    if is_squarefree(q, p): stats["squarefree"] += 1
    if disc_cubic(q, p) != 0: stats["disc_nonzero"] += 1
    sh = tuple(factor_shape(q, p))
    shapes[sh] = shapes.get(sh, 0) + 1
    if sh == (3,): stats["irreducible_cubic"] += 1
    if i % 1500 == 0: print("  ..%d (%.1fs)" % (i, time.time()-t0), flush=True)

print("\n=== J1 independent recomputation over ALL disclosed degree drops ===")
for k, v in stats.items(): print("  %-22s %d / %d" % (k, v, len(devs)))
print("  factor shapes of the recomputed polynomial:", shapes)
print("  anomalies:", bad[:5], "count", len(bad))
print("  elapsed %.1fs" % (time.time()-t0))
