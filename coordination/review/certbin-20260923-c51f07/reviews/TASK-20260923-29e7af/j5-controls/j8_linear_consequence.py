#!/usr/bin/env python3
"""J8(ii) (TASK-20260923-29e7af). (1) Verify on every archived F-S3 / F-RANDX /
F-PLANT instance (D-independent) the DERIVED identity
    sum_k Tr(t^k / x_R^2) * f_k  ==  v_0 + v_9 + Tr(B / x_R^2)
(theta = x_R^{-2} cancels both bilinear terms of Tr(theta*S_3); Tr(x) = r_0 in
this field), using the archived descended_E (impl, unchanged) for f_k and my
own GF(2^17) arithmetic for the coefficients. (2) Check the same combination on
the null families F-AFF-1..3 (paired x_R) and report whether it is linear there.
(3) Split the 1-in-R_4 rate of F-RANDX's unsat arm by T(x_R) = Tr(x_R + A +
B/x_R^2) (0 iff x_R is an x-coordinate of E(F_2^17); 1 iff of the twist)."""
import gzip, json, os, sys
import numpy as np
REPO = "/home/user/crypto-autoresearcher"
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/impl")
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IMPL)
from gf2n import TableField
from macaulay import descended_E, EQ_MONS, EQ_INDEX, affine_combine
from families import E_from_hex
N = 17; MOD = (1 << 17) | (1 << 3) | 1
def mul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> N: a ^= MOD
    return r
def pw(a, e):
    r = 1
    while e:
        if e & 1: r = mul(r, a)
        a = mul(a, a); e >>= 1
    return r
def inv(a): return pw(a, (1 << N) - 2)
def tr(x):
    s, y = 0, x
    for _ in range(N): s ^= y; y = mul(y, y)
    return s
cur = json.load(open(os.path.join(RUN, "curve.json"))); A, B = cur["A"], cur["B"]
F = TableField()
target_lin = np.zeros(len(EQ_MONS), dtype=np.uint8)
target_lin[EQ_INDEX[(0,)]] = 1; target_lin[EQ_INDEX[(9,)]] = 1
P1 = json.load(gzip.open(os.path.join(RUN, "checkpoint/p1-instances.json.gz"), "rt"))
def comb(Emat, xR):
    th = inv(mul(xR, xR))
    c = np.array([tr(mul(th, 1 << k)) for k in range(N)], dtype=np.uint8)
    return (c[:, None] * Emat).sum(axis=0) % 2, tr(mul(B, th))
out = {}
for fam in ("F-S3", "F-RANDX", "F-PLANT"):
    ok = 0; n = 0; bad = []
    for t in P1[fam]["targets"] + P1[fam].get("refs", []):
        xR = t["x_R"]
        if xR == 0: continue
        v, cst = comb(descended_E(F, B, xR), xR)
        want = target_lin.copy(); want[EQ_INDEX[()]] = cst
        n += 1
        if np.array_equal(v, want): ok += 1
        else: bad.append(t.get("idx", t.get("selected_as")))
    out[fam] = {"instances": n, "identity_holds": ok, "fails": bad[:10]}
for d in (1, 2, 3):
    fam = f"F-AFF-{d}"
    A0 = E_from_hex(P1[fam]["A0_hex"]); Aj = [E_from_hex(x) for x in P1[fam]["Aj_hex"]]
    nlin = 0; n = 0
    for t in P1[fam]["targets"][:200]:
        xR = t["x_R"]
        if xR == 0: continue
        v, _ = comb(affine_combine(A0, Aj, xR), xR)
        deg = max((len(EQ_MONS[j]) for j in np.flatnonzero(v)), default=-1)
        n += 1; nlin += deg <= 1
    out[fam] = {"instances_checked": n, "same_combination_is_affine": nlin}
# (3) F-RANDX 1-in-R_4 split by curve/twist membership of x_R
recs = [json.loads(l) for l in gzip.open(os.path.join(RUN, "targets-F-RANDX.jsonl.gz"), "rt")]
sp = {}
for r in recs:
    if r["D"] != 4 or r["stratum"] != "unsat": continue
    xR = r["x_R"]
    T = tr(xR ^ A ^ mul(B, inv(mul(xR, xR)))) if xR else None
    key = f"T(x_R)={T}"
    s = sp.setdefault(key, [0, 0]); s[0] += r["one_in_R"]; s[1] += 1
out["F-RANDX_unsat_D4_one_in_R_by_curve_or_twist"] = {k: {"one_in_R": v[0], "n": v[1], "rate": v[0] / v[1]} for k, v in sp.items()}
recs3 = [json.loads(l) for l in gzip.open(os.path.join(RUN, "targets-F-S3.jsonl.gz"), "rt")]
out["F-S3_T(x_R)_values"] = sorted({tr(r["x_R"] ^ A ^ mul(B, inv(mul(r["x_R"], r["x_R"])))) for r in recs3 if r["x_R"]})
json.dump(out, open(os.path.join(HERE, "j8-linear-consequence.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
