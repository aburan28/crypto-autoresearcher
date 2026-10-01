"""J2 (2): replay of the S3-PRIMARY stream from seed 2026092460601 with own point arithmetic,
the draw rule read from the specification only. Compares attempt by attempt with the archived
draws-S3-PRIMARY.jsonl.gz and the kept keys of instances.jsonl.gz; rebuilds E_S3(x_R) for every
kept S_3 system by own Moebius-interpolation descent and compares E_hex / E_sha256.

usage: python3 replay_primary.py <run_dir>
"""
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gf219 as G  # noqa: E402

RUN = sys.argv[1]
SEED = 2026092460601
q = G.Q_ORDER


def load_jsonl(path):
    with gzip.open(path, "rt") as fh:
        return [json.loads(l) for l in fh]


g = np.random.Generator(np.random.PCG64(SEED))
mine = []
seen = set()
U, S = [], []
attempt = 0
while attempt < 5000 and (len(U) < 400 or len(S) < 100):
    a = int(g.integers(0, q))
    b = int(g.integers(0, q))
    R = G.padd(G.smul(a, G.P_PT), G.smul(b, G.Q_PT))
    rec = {"attempt": attempt, "a": a, "b": b}
    if R is None:
        rec["outcome"] = "R_is_O"
        rec["x_R"] = None
    else:
        x = R[0]
        rec["x_R"] = x
        rec["qR_is_O"] = G.smul(q, R) is None
        rec["TrX_eq_TrA"] = G.tr(x) == G.tr(G.A_CURVE)
        if x < 1024:
            rec["outcome"] = "degenerate"
        elif x in seen:
            rec["outcome"] = "duplicate"
        else:
            seen.add(x)
            sB = G.s_bruteforce(x)
            sA, _ = G.s_quadratic(x)
            rec["s"] = sB
            rec["sA"] = sA
            if sB == 0:
                if len(U) < 400:
                    rec["outcome"] = "kept:S3-U400"
                    U.append(attempt)
                else:
                    rec["outcome"] = "unsat_not_kept"
            else:
                if len(S) < 100:
                    rec["outcome"] = "kept:S3-SAT100"
                    S.append(attempt)
                else:
                    rec["outcome"] = "sat_not_kept"
    mine.append(rec)
    attempt += 1

arch = load_jsonl(os.path.join(RUN, "draws-S3-PRIMARY.jsonl.gz"))
inst = load_jsonl(os.path.join(RUN, "instances.jsonl.gz"))
res = {"seed": SEED, "numpy_version": np.__version__, "my_attempts": len(mine), "archived_attempts": len(arch)}
mism = []
for i in range(max(len(mine), len(arch))):
    m = mine[i] if i < len(mine) else None
    r = arch[i] if i < len(arch) else None
    if m is None or r is None:
        mism.append({"attempt": i, "mine": m, "archived": r})
        continue
    for k in ("attempt", "a", "b", "x_R", "outcome", "s", "sA"):
        if m.get(k) != r.get(k):
            mism.append({"attempt": i, "field": k, "mine": m.get(k), "archived": r.get(k)})
res["attempt_field_mismatches"] = mism
from collections import Counter  # noqa: E402
res["my_outcomes"] = dict(Counter(m["outcome"] for m in mine))
res["archived_outcomes"] = dict(Counter(r["outcome"] for r in arch))
res["sA_ne_s_in_my_replay"] = sum(1 for m in mine if "s" in m and m["s"] != m["sA"])
res["C-TR19_primary_qR_not_O"] = sum(1 for m in mine if m.get("x_R") is not None and not m["qR_is_O"])
res["C-TR19_primary_TrX_ne_TrA"] = sum(1 for m in mine if m.get("x_R") is not None and not m["TrX_eq_TrA"])

# kept keys and E rebuild
by_key = {r["key"]: r for r in inst}
kept_mism = []
e_mism = []
s_sys_mism = []
sol_mism = []
for arm, lst in (("S3-U400", U), ("S3-SAT100", S)):
    for idx, att in enumerate(lst):
        key = f"{arm}:{idx}"
        r = by_key.get(key)
        m = mine[att]
        if r is None or r["attempt"] != att or r["x_R"] != m["x_R"] or r["arm"] != arm or r.get("s") != m["s"]:
            kept_mism.append({"key": key, "mine_attempt": att, "mine_x": m["x_R"], "archived": None if r is None else {k: r.get(k) for k in ("attempt", "x_R", "arm", "s")}})
            continue
        E = G.descend_E(m["x_R"])
        hx = G.E_to_hex(E)
        if hx != r["E_hex"] or G.E_sha256(hx) != r["E_sha256"]:
            e_mism.append(key)
        s_b, sols = G.s_system(E, True)
        if s_b != m["s"]:
            s_sys_mism.append(key)
        if arm == "S3-SAT100":
            _, solg = G.s_bruteforce(m["x_R"], True)
            if sorted(r.get("solutions", [])) != sols or sols != solg:
                sol_mism.append(key)
n_arch_primary = sum(1 for r in inst if r["arm"] in ("S3-U400", "S3-SAT100"))
res["archived_primary_kept_count"] = n_arch_primary
res["my_kept"] = {"S3-U400": len(U), "S3-SAT100": len(S)}
res["kept_key_mismatches"] = kept_mism
res["E_hex_or_sha_mismatches_own_descent"] = e_mism
res["E_checked"] = len(U) + len(S)
res["s_via_boolean_system_mismatches"] = s_sys_mism
res["sat100_solution_list_mismatches"] = sol_mism
res["S3-U400_x_R_first5"] = [mine[a]["x_R"] for a in U[:5]]
res["pass"] = not (mism or kept_mism or e_mism or s_sys_mism or sol_mism) and n_arch_primary == 500
with gzip.open(os.path.join(HERE, "my-draws-S3-PRIMARY.jsonl.gz"), "wt") as fh:
    for m in mine:
        fh.write(json.dumps(m, sort_keys=True) + "\n")
with open(os.path.join(HERE, "replay-S3-PRIMARY.json"), "w") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("attempt_field_mismatches",)}, indent=1))
print("attempt_field_mismatches:", len(mism), mism[:10])
