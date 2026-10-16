#!/usr/bin/env python3
"""J2 / Q3 / Q4: X9.62 seed-to-c map on the 10 published prime seeds, the five
known-false variants, and the candidate index set of every run.

Q3: c(seed) and (c*b^2 + 27) mod p, plus c against the c printed in FIPS 186-2 and
SP 800-186 where those list the curve.
Q4: for every block i (1-based, i = 1..README count) of each run, keep i when
c != 0, 4c+27 != 0 (mod p) and -27/c is a nonzero square mod p (Euler criterion).
Writes ../out/q3_x962.json and ../out/q4_candidates_<t>.txt (one 1-based index per
line), and logs the candidate files (order.log: candidate index sets).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

P = load_params()
VARIANTS = ["std", "a_noclear", "b_left", "c_nowrap", "d_le", "e_i0"]
q3 = {"curves": {}, "variant_summary": {}}
for name in PRIME_CURVES:
    pr = P[name]
    p, b = pr["p"], pr["b"]
    l = p.bit_length()
    rec = {"l": l, "v": (l - 1) // 160, "w": l - 160 * ((l - 1) // 160) - 1}
    for var in VARIANTS:
        c = x962_c(pr["seed_bytes"], l, var)
        resid = (c * b * b + 27) % p
        rec[var] = {"c": hex(c), "residue": hex(resid), "holds": resid == 0}
    pub = pr.get("c_published", {})
    rec["c_published"] = pub
    rec["c_matches_published"] = {s: int(v, 16) == int(rec["std"]["c"], 16) for s, v in pub.items()}
    q3["curves"][name] = rec
for var in VARIANTS:
    held = [n for n in PRIME_CURVES if q3["curves"][n][var]["holds"]]
    q3["variant_summary"][var] = {"holds_on": len(held), "curves_holding": held}
with open(os.path.join(ROOT, "out", "q3_x962.json"), "w") as f:
    json.dump(q3, f, indent=1, sort_keys=True)
for n in PRIME_CURVES:
    r = q3["curves"][n]
    print(n, "l", r["l"], "v", r["v"], "w", r["w"], "std holds", r["std"]["holds"],
          "c vs published", r["c_matches_published"],
          "variants holding:", [v for v in VARIANTS[1:] if r[v]["holds"]])
for var in VARIANTS:
    print("variant", var, "holds on", q3["variant_summary"][var]["holds_on"], "of 10")

# Q4 candidate sets
summary = {}
for t, field, count in RUNS:
    p = P[FIELD_CURVE[field]]["p"]
    l = p.bit_length()
    s = drand48_byte_stream(t, 20 * count)
    cand = []
    nzero = n4c = 0
    for i0 in range(count):
        c = x962_c(s[20 * i0:20 * i0 + 20], l)
        if c % p == 0:
            nzero += 1
            continue
        if (4 * c + 27) % p == 0:
            n4c += 1
            continue
        q = (-27 * pow(c, -1, p)) % p
        if q != 0 and pow(q, (p - 1) // 2, p) == 1:
            cand.append(i0 + 1)
    path = os.path.join(ROOT, "out", f"q4_candidates_{t}.txt")
    with open(path, "w") as f:
        f.write("".join(f"{i}\n" for i in cand))
    order_log(f"Q4 candidate index set run {t} (1-based block indices)", path)
    summary[t] = {"field": field, "blocks": count, "candidates": len(cand),
                  "c_zero": nzero, "4c+27_zero": n4c, "first": cand[:5], "last": cand[-3:]}
    print("run", t, summary[t])
print("total blocks", sum(v["blocks"] for v in summary.values()),
      "total candidates", sum(v["candidates"] for v in summary.values()))
with open(os.path.join(ROOT, "out", "q4_summary.json"), "w") as f:
    json.dump({str(k): v for k, v in summary.items()}, f, indent=1)
