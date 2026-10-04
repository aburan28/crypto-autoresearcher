"""J10 O1 and O2 from ARCHIVED records (TASK-20260926-c58e87; RT-4), plus:
  * RM check: the evaluation map B_{<=d} -> F_2^S is onto for |S| <= 2^{d+1} - 1 (random sets,
    m = 5..8, d = 0..4 where 2^{d+1}-1 <= 2^m) and fails for a (d+1)-dimensional affine subspace
    (tightness). Own code. The proof is re-derived in j10-ptm/o1-o3-readings.yaml.
  * the per-degree T4 consequence of j11-ladder/proof-verdicts.yaml:
    dims_by_deg(W_4)[d] = dims_by_deg(W'_4)[d] + dim B'_{<=d-1} (B' in 17 variables), and
    final_dim(W_4) = final_dim(W'_4) + 834, one(W_4) = one(W'_4), on EVERY substituted system;
  * O2: T5 exactness on the arms where T5 applies (final_dim(W_4) = rank R'_4 + 834).
Usage: python3 o1_o2.py <worktree> <out.json>
"""
import collections
import gzip
import itertools
import json
import random
import sys
from math import comb

wt, out = sys.argv[1], sys.argv[2]
run = f"{wt}/experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
CL = collections.defaultdict(dict)
for l in gzip.open(f"{run}/closures.jsonl.gz", "rt"):
    r = json.loads(l)
    CL[r["key"]][r["closure"]] = r
INS = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(f"{run}/instances.jsonl.gz", "rt")}
res = {}

# ---- RM surjectivity machine check -----------------------------------------------------
rng = random.Random(2026092689231)


def ev_rank(S, m, d):
    rows = []
    for deg in range(d + 1):
        for A in itertools.combinations(range(m), deg):
            mask = sum(1 << i for i in A)
            v = 0
            for t, x in enumerate(S):
                if x & mask == mask:
                    v |= 1 << t
            rows.append(v)
    piv = {}
    r = 0
    for v in rows:
        while v:
            hb = v.bit_length() - 1
            if hb in piv:
                v ^= piv[hb]
            else:
                piv[hb] = v
                r += 1
                break
    return r


rm = []
for m in (5, 6, 7, 8):
    for d in range(0, 5):
        size = 2 ** (d + 1) - 1
        if size > 2 ** m or d >= m:
            continue
        ok = all(ev_rank(rng.sample(range(2 ** m), size), m, d) == size for _ in range(100))
        sub = list(range(2 ** (d + 1)))  # the (d+1)-dim subspace on the first d+1 coordinates
        tight = ev_rank(sub, m, d) < len(sub)
        rm.append({"m": m, "d": d, "size": size, "onto_100_random": ok, "subspace_2^(d+1)_not_onto": tight})
res["RM_check"] = rm

# ---- O1: satisfiable controls of every arm ------------------------------------------------
o1 = {}
for arm in sorted({r["arm"] for r in INS.values()}):
    keys = [k for k, r in INS.items() if r["arm"] == arm and r["role"] == "sat"]
    if not keys:
        continue
    rows = []
    for k in keys:
        s = INS[k]["s"]
        w = CL[k]["W_4"]
        m4 = CL[k]["M_4"]
        rows.append((s, 4048 - w["final_dim"], w["one"], m4["one"]))
    o1[arm] = {"n": len(rows), "s_le_31": sum(1 for r in rows if r[0] <= 31),
               "M4_refuted": sum(1 for r in rows if r[3]), "W4_refuted": sum(1 for r in rows if r[2]),
               "codim_ge_s": sum(1 for r in rows if r[1] >= r[0]), "codim_eq_s": sum(1 for r in rows if r[1] == r[0]),
               "codim_minus_s_hist": dict(sorted(collections.Counter(r[1] - r[0] for r in rows).items())),
               "codim_hist": dict(sorted(collections.Counter(r[1] for r in rows).items()))}
res["O1"] = o1

# ---- T4 per-degree consequence on every substituted system ---------------------------------
Bp = [0] + [sum(comb(17, i) for i in range(d)) for d in range(1, 5)]  # dim B'_{<=d-1}: 0,1,18,154,834
t4 = collections.Counter()
viol = []
for k, c in CL.items():
    if "W'_4" not in c:
        continue
    w, wp = c["W_4"], c["W'_4"]
    ok_final = w["final_dim"] == wp["final_dim"] + 834
    ok_one = w["one"] == wp["one"]
    ok_deg = all(w["dims_by_deg"][d] == wp["dims_by_deg"][d] + Bp[d] for d in range(5))
    t4[(INS[k]["arm"], ok_final, ok_one, ok_deg)] += 1
    if not (ok_final and ok_one and ok_deg):
        viol.append({"key": k, "W4": w["dims_by_deg"], "Wp4": wp["dims_by_deg"]})
res["T4_per_degree"] = {"Bprime_le_d_minus_1": Bp,
                        "counts": {f"{a}|final={b}|one={c}|per_degree={d}": v for (a, b, c, d), v in sorted(t4.items())},
                        "violations": viol[:20], "n_violations": len(viol)}

# ---- O2: T5 exactness where applicable ----------------------------------------------------
o2 = collections.Counter()
for k, c in CL.items():
    rb = c.get("rc_b", {})
    if not rb.get("T5_applicable"):
        continue
    ok = (c["W_4"]["final_dim"] == c["R'_4"]["rank"] + 834) and (c["W_4"]["one"] == c["R'_4"]["one"])
    o2[(INS[k]["arm"], INS[k]["role"], ok, tuple(c["W_4"]["dims_by_deg"]), c["W_4"]["one"])] += 1
res["O2_T5_exactness"] = {f"{a}|{b}|exact={c}|W4dbd={list(d)}|one={e}": v for (a, b, c, d, e), v in sorted(o2.items())}
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res, indent=1)[:7000])
