#!/usr/bin/env python3
"""J2 check 5: spot-recheck certificates of the 33 R12 found instances by
EXACT recomputation from the recorded instance fields (fractions.Fraction).
For each instance verify:
  (a) g = x + c with c = r_0 - b_0, and r_i == b_i + c for all i (affine);
  (b) forcing identity s(b_i) == d_i * g(b_i)^2 == d_i * r_i^2 for all i;
  (c) deg s (recorded deg_s == actual degree of recorded s);
  (d) nonsingularity: recompute disc(s) (Sylvester resultant, exact),
      disc != 0, and disc == recorded disc_s;
  (e) class_keys == sorted distinct d_pattern values (string), n_classes.
Do NOT quote the producer's verdict fields; recompute everything.
"""
import json
from fractions import Fraction as Fr

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
P = f"{ROOT}/experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json"
d = json.load(open(P))
found = d["found"]


def peval(p, x):
    s = Fr(0)
    for c in reversed(p):
        s = s * x + c
    return s


def poly_disc(s):
    """Exact discriminant, disc = (-1)^{d(d-1)/2} res(s,s')/lc."""
    # strip trailing zeros to get true degree
    ss = list(s)
    while len(ss) > 1 and ss[-1] == 0:
        ss.pop()
    dd = len(ss) - 1
    lc = ss[-1]
    if lc == 0 or dd < 1:
        raise ValueError("degenerate")
    der = [Fr(i) * ss[i] for i in range(1, len(ss))]
    N = dd + (dd - 1)
    M = [[Fr(0)] * N for _ in range(N)]
    for i in range(dd - 1):
        for j in range(dd + 1):
            M[i][i + j] = ss[dd - j] if (dd - j) >= 0 else Fr(0)
    for i in range(dd):
        for j in range(dd):
            M[(dd - 1) + i][i + j] = der[(dd - 1) - j] if (dd - 1 - j) >= 0 else Fr(0)
    # determinant by fraction Gaussian elimination
    Mm = [row[:] for row in M]
    det = Fr(1)
    for col in range(N):
        piv = None
        for i in range(col, N):
            if Mm[i][col] != 0:
                piv = i
                break
        if piv is None:
            return Fr(0)
        if piv != col:
            Mm[col], Mm[piv] = Mm[piv], Mm[col]
            det = -det
        det *= Mm[col][col]
        inv = Fr(1) / Mm[col][col]
        for i in range(col + 1, N):
            if Mm[i][col] != 0:
                f = Mm[i][col] * inv
                for j in range(col, N):
                    Mm[i][j] -= f * Mm[col][j]
    sign = -1 if (dd * (dd - 1) // 2) % 2 else 1
    return sign * det / lc


def actual_deg(s):
    ss = list(s)
    while len(ss) > 1 and ss[-1] == 0:
        ss.pop()
    return len(ss) - 1


results = []
for rec in found:
    inst = rec["instance"]
    b = [Fr(x) for x in inst["b"]]
    r = [Fr(x) for x in inst["r"]]
    dp = [int(x) for x in inst["d_pattern"]]
    s = [Fr(x) for x in inst["s"]]
    bi = rec["b_index"]
    # (a) affine g = x + c
    c = r[0] - b[0]
    affine = all(r[i] == b[i] + c for i in range(len(b)))
    # (b) forcing identity s(b_i) == d_i * r_i^2  (== d_i * g(b_i)^2)
    ident = all(peval(s, b[i]) == Fr(dp[i]) * r[i] * r[i] for i in range(len(b)))
    # also via g(b_i) explicitly
    ident_g = all(peval(s, b[i]) == Fr(dp[i]) * (b[i] + c) ** 2 for i in range(len(b)))
    # (c) degree
    deg = actual_deg(s)
    deg_ok = (deg == inst["deg_s"])
    # (d) discriminant
    disc = poly_disc(s)
    disc_ok = (disc != 0) and (disc == Fr(inst["disc_s"]))
    # (e) class keys
    ck = sorted(set(str(x) for x in dp))
    nc = len(set(dp))
    ck_ok = (ck == rec["certificate"]["class_keys"])
    nc_ok = (nc == rec["certificate"]["n_classes"])
    results.append({
        "b_index": bi, "c": str(c), "affine": affine,
        "identity": ident, "identity_via_g": ident_g,
        "deg": deg, "deg_ok": deg_ok,
        "disc_nonzero": disc != 0, "disc_match": disc == Fr(inst["disc_s"]),
        "class_keys_ok": ck_ok, "n_classes_ok": nc_ok,
        "all_ok": affine and ident and ident_g and deg_ok and disc_ok and ck_ok and nc_ok,
    })

n_ok = sum(1 for x in results if x["all_ok"])
print(f"instances checked: {len(results)} | all_ok: {n_ok}/{len(results)}")
print("\n== per-instance (all 33) ==")
for x in results:
    flag = "OK " if x["all_ok"] else "FAIL"
    print(f"[{flag}] b_index={x['b_index']:5d} c={x['c']:6s} affine={x['affine']} "
          f"ident={x['identity']} ident_g={x['identity_via_g']} deg={x['deg']}({x['deg_ok']}) "
          f"disc!=0={x['disc_nonzero']} disc_match={x['disc_match']} "
          f"class_keys={x['class_keys_ok']} n_classes={x['n_classes_ok']}")

# detail for 3 named instances (649, 1299, 4995) for the report
print("\n== detail for b_index 649, 1299, 4995 ==")
for bi in (649, 1299, 4995):
    rec = next(r for r in found if r["b_index"] == bi)
    inst = rec["instance"]
    b = [Fr(x) for x in inst["b"]]
    r = [Fr(x) for x in inst["r"]]
    dp = [int(x) for x in inst["d_pattern"]]
    s = [Fr(x) for x in inst["s"]]
    c = r[0] - b[0]
    disc = poly_disc(s)
    print(f"b_index={bi}: b={inst['b']}")
    print(f"   r={inst['r']}  c={c}  d_pattern={dp}")
    print(f"   s={inst['s']}  deg_s(rec)={inst['deg_s']} deg(rec-computed)={actual_deg(s)}")
    print(f"   disc_s(rec)={inst['disc_s']}")
    print(f"   disc(recomputed)={disc}  match={disc == Fr(inst['disc_s'])}  nonzero={disc != 0}")
    print(f"   class_keys(rec)={rec['certificate']['class_keys']} n_classes(rec)={rec['certificate']['n_classes']}")
    print(f"   class_keys(recomputed)={sorted(set(str(x) for x in dp))} n_classes(recomputed)={len(set(dp))}")
    print(f"   identity s(b_i)==d_i*r_i^2 all: {all(peval(s,b[i])==Fr(dp[i])*r[i]*r[i] for i in range(len(b)))}")
