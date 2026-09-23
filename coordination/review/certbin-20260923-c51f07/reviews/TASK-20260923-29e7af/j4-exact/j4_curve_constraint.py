#!/usr/bin/env python3
"""J4 step 0 (TASK-20260923-29e7af). Does the set of curve target x_R (F-S3)
satisfy an F_2-linear constraint in r = coords(x_R)? Own GF(2^17) arithmetic
(f = t^17 + t^3 + 1), no impl import. Reads from targets-*.jsonl.gz only the
fields idx, D, x_R, degenerate (no match flag, no replay field)."""
import gzip, json, os
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
N = 17; MOD = (1 << 17) | (1 << 3) | 1
def mul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> N: a ^= MOD
    return r
def tr(x):
    s, y = 0, x
    for _ in range(N):
        s ^= y; y = mul(y, y)
    assert s in (0, 1)
    return s
tau = sum(tr(1 << j) << j for j in range(N))   # Tr(x) = <tau, r>
def par(x): return bin(x).count("1") & 1
curve = json.load(open(os.path.join(RUN, "curve.json")))
A, B = curve["A"], curve["B"]
def xs(fam, D=4):
    out = []
    with gzip.open(os.path.join(RUN, f"targets-{fam}.jsonl.gz"), "rt") as f:
        for line in f:
            d = json.loads(line)
            if d["D"] == D: out.append((d["idx"], d["x_R"], d["degenerate"]))
    return out
def affine_hull_dim(vals):
    v0 = vals[0]; basis = {}
    for v in vals[1:]:
        x = v ^ v0
        while x:
            h = x.bit_length() - 1
            if h in basis: x ^= basis[h]
            else: basis[h] = x; break
    return len(basis)
res = {"tau_bits": tau, "tau_hex": hex(tau), "Tr_A": tr(A), "Tr_B": tr(B),
       "check_Tr_via_tau_on_1000_random": all(tr(x) == par(x & tau) for x in range(1, 1 << 17, 131))}
refs = json.load(open(os.path.join(RUN, "references.json")))["F-S3"]["references"]
res["F-S3_refs_Tr"] = {k: par(v["x_R"] & tau) for k, v in refs.items() if "x_R" in v}
for fam in ("F-S3", "F-PLANT", "F-RANDX"):
    T = xs(fam)
    trs = [par(x & tau) for _, x, _ in T]
    nd = [x for _, x, dg in T if not dg]
    res[fam] = {"n": len(T), "Tr_values_count": {str(v): trs.count(v) for v in (0, 1)},
                "affine_hull_dim_all": affine_hull_dim([x for _, x, _ in T]),
                "affine_hull_dim_nondegenerate": affine_hull_dim(nd)}
print(json.dumps(res, indent=1))
json.dump(res, open("curve-constraint.json", "w"), indent=1)
