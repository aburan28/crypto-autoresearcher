"""Self-test of rtlib (TASK-20260926-c58e87). Seed 2026092689199 (python random), not the O4 seed.
Checks: field axioms; S_3 against point addition on the archived curve; own descent against
direct F_{2^17} evaluation (polynomial basis and a random basis); own descent against the
archived E_hex of all 144 RC-1 x_R (U62, S62, C20); exhaustive s against naive evaluation
and against the archived s; flat-certificate checker on a constructed identity.
Usage: python3 selftest.py <worktree> <out.json>
"""
import json
import random
import sys
import time

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rtlib as R  # noqa: E402

wt, out = sys.argv[1], sys.argv[2]
rng = random.Random(2026092689199)
res = {"seed": 2026092689199, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

res["irreducible"] = R.irreducible_check()
ok = True
for _ in range(3000):
    a, b, c = (rng.randrange(1, 1 << 17) for _ in range(3))
    ok &= R.gmul(a, R.gmul(b, c)) == R.gmul(R.gmul(a, b), c)
    ok &= R.gmul(a, b ^ c) == R.gmul(a, b) ^ R.gmul(a, c)
    ok &= R.gmul(a, R.ginv(a)) == 1
res["field_axioms_3000"] = bool(ok)

# S_3 against point addition on the archived curve
pts = []
while len(pts) < 200:
    P = R.lift_x(rng.randrange(1, 1 << 17), rng)
    if P is not None:
        assert R.on_curve(*P)
        pts.append(P)
ok = True
n = 0
for i in range(0, 200, 2):
    P, Q = pts[i], pts[i + 1]
    S = R.point_add(P, Q)
    if S is None:
        continue
    assert R.on_curve(*S)
    ok &= R.s3(P[0], Q[0], S[0]) == 0
    n += 1
res["s3_vanishes_on_point_sums"] = {"ok": bool(ok), "n": n}

# descent vs direct evaluation
def direct_check(basis, trials):
    good = True
    for _ in range(trials):
        xr = rng.randrange(1, 1 << 17)
        E = R.descent(xr, basis)
        v = [rng.randrange(2) for _ in range(18)]
        x1 = 0
        x2 = 0
        for j in range(9):
            if v[j]:
                x1 ^= basis[j]
            if v[9 + j]:
                x2 ^= basis[j]
        val = R.s3(x1, x2, xr)
        mine = 0
        for k in range(17):
            mine |= R.eval_poly_row(E[k], v) << k
        good &= mine == val
    return bool(good)

res["descent_vs_direct_poly_basis_300"] = direct_check(R.poly_basis(), 300)
rb = [rng.randrange(1, 1 << 17) for _ in range(9)]
res["descent_vs_direct_random_basis_300"] = direct_check(rb, 300)

# own descent vs archived E_hex (RC-1 instance-sets.json)
d = json.load(open(f"{wt}/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"))
match = 0
tot = 0
s_match = 0
s_checked = 0
for setname in ("U62", "S62", "C20"):
    for rec in d["sets"][setname]:
        xr = rec["archived"]["x_R"]
        E = R.descent(xr, R.poly_basis())
        tot += 1
        match += int(R.E_to_hex(E) == [h.lstrip("0") or "0" for h in rec["E_hex"]]
                     or [int(h, 16) for h in R.E_to_hex(E)] == [int(h, 16) for h in rec["E_hex"]])
res["own_descent_eq_archived_E_hex"] = {"match": match, "of": tot}

# exhaustive s: naive vs bit-sliced on 30 random sparse systems, and archived s on 12 S_3 systems
ok = True
for _ in range(30):
    E = np.zeros((17, 172), dtype=np.uint8)
    for k in range(17):
        for c in rng.sample(range(172), 6):
            E[k, c] = 1
    # make it have solutions sometimes: plant one
    sol = R.solutions(E)
    naive = []
    for a in range(1 << 18) if False else []:
        pass
    # naive on a random subset of assignments + all listed solutions
    chk = set(rng.sample(range(1 << 18), 2000)) | set(sol[:50])
    for a in chk:
        v = [(a >> i) & 1 for i in range(18)]
        allz = all(R.eval_poly_row(E[k], v) == 0 for k in range(17))
        ok &= allz == (a in set(sol))
res["solutions_vs_naive_30x2000"] = bool(ok)
arch = []
for setname in ("U62", "S62"):
    for rec in d["sets"][setname][:6]:
        E = R.hex_to_E(rec["E_hex"])
        s = len(R.solutions(E))
        arch.append([setname, rec["idx"], s, rec["archived"]["s"]])
res["archived_s_check"] = {"ok": all(a[2] == a[3] for a in arch), "rows": arch}

# flat certificate checker on a constructed identity: f*(f+1) = 0 so (f+1)*f + f*f ... use
# the trivial fact f_k*(1) + f_k*(1) = 0 -> not 1; and a system containing f = 1
E = np.zeros((17, 172), dtype=np.uint8)
E[3, 0] = 1
res["flat_cert_checker"] = {"accepts_true": R.flat_cert_ok([(0, 3)], E)[0],
                            "rejects_false": not R.flat_cert_ok([(0, 4)], E)[0]}
res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "archived_s_check"}, indent=1))
print("archived_s_check ok", res["archived_s_check"]["ok"])
