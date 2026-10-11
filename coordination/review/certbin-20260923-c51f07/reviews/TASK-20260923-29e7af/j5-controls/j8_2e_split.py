#!/usr/bin/env python3
"""J8(ii) addendum: F-RANDX unsat-arm 1-in-R_4 rate split by membership of x_R
in x(2E) (T(x_R)=0 and Tr(x_R)=Tr(A)), x(E)\\x(2E), and the twist; compared
with F-S3 (all x_R in x(4E) cap subgroup). Own GF(2^17) code; archived records."""
import gzip, json, os, math
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
HERE = os.path.dirname(os.path.abspath(__file__))
N = 17; MOD = (1 << 17) | (1 << 3) | 1
def mul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> N: a ^= MOD
    return r
def inv(a):
    r, e = 1, (1 << N) - 2
    while e:
        if e & 1: r = mul(r, a)
        a = mul(a, a); e >>= 1
    return r
def tr(x):
    s, y = 0, x
    for _ in range(N): s ^= y; y = mul(y, y)
    return s
c = json.load(open(os.path.join(RUN, "curve.json"))); A, B = c["A"], c["B"]
def cls(x):
    if x == 0: return "zero"
    if tr(x ^ A ^ mul(B, inv(mul(x, x)))): return "twist"
    return "x(2E)" if tr(x) == tr(A) else "x(E)-x(2E)"
out = {}
for fam in ("F-RANDX", "F-S3"):
    for arm in ("unsat", "sat"):
        d = {}
        for l in gzip.open(os.path.join(RUN, f"targets-{fam}.jsonl.gz"), "rt"):
            r = json.loads(l)
            if r["D"] != 4 or r["stratum"] != arm: continue
            k = cls(r["x_R"]); s = d.setdefault(k, [0, 0]); s[0] += r["one_in_R"]; s[1] += 1
        out[f"{fam}/{arm}"] = {k: {"one_in_R": v[0], "n": v[1], "rate": round(v[0] / v[1], 4)} for k, v in d.items()}
def z2(k1, n1, k2, n2):
    p = (k1 + k2) / (n1 + n2); se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (k1 / n1 - k2 / n2) / se
u = out["F-RANDX/unsat"]; s3 = out["F-S3/unsat"]["x(2E)"]
out["z_F-S3_vs_F-RANDX_x(2E)"] = round(z2(s3["one_in_R"], s3["n"], u["x(2E)"]["one_in_R"], u["x(2E)"]["n"]), 2) if "x(2E)" in u else None
json.dump(out, open(os.path.join(HERE, "j8-2e-split.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
