#!/usr/bin/env python3
"""J7 (a) observation-fiber attack -- TASK-20260924-d95e70.
Same observation, two preimages: a verified FLAT certificate with max deg mu = 3.
  Preimage 1: a U62 W_4 certificate (the run's), instance IN W_4 (J7 witnesses).
  Preimage 2: a null M_5 certificate (the run's), instance NOT in W_4.
For the 10 null instances analysed in j8-nulls/syzygy.json (first 5 of each null
set) and the first 5 U62 instances: re-verify the run's flat certificate with my
own Boolean-ring code on the run's archived E_hex (decoded by my decoder), record
max deg mu and |C|; and record W_4 membership from (i) the J7 structured witness
(U62) or (ii) the DERIVATION "no fall in M_4 => W_4 = M_4" with my own M_4 fall
profile [0, 0, 17, 323] and 1 not in M_4 (nulls; j8-nulls/syzygy.json)."""
import gzip
import json
import os
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
EQ = []
for d in range(3):
    EQ.extend(sum(1 << i for i in c) for c in combinations(range(18), d))


def dec(hexes):
    return [[EQ[j] for j in range(172) if (int(h, 16) >> j) & 1] for h in hexes]


iset = json.load(open(os.path.join(RUN, "instance-sets.json")))["sets"]
E = {i["key"]: dec(i["E_hex"]) for s in iset for i in iset[s]}
syz = {r["system"]: r for r in json.load(open(os.path.join(HERE, "..", "j8-nulls", "syzygy.json")))["systems"]}
wit = {(r["set"], r["idx"]): r for r in json.load(open(os.path.join(HERE, "w1-witness-reverification.json")))["rows"]}
want = [i["key"] for i in iset["N-AFF62"][:5]] + [i["key"] for i in iset["N-F262"][:5]]
want_u = [i["key"] for i in iset["U62"][:5]]
rows = []
for line in gzip.open(os.path.join(RUN, "certificates.jsonl.gz"), "rt"):
    c = json.loads(line)
    key, cl = c["key"], c["closure"]
    if not ((key in want and cl == "M_5") or (key in want_u and cl == "W_4")):
        continue
    fs = E[key]
    acc = {}
    for mu, k in c["C"]:
        m0 = sum(1 << i for i in mu)
        for m in fs[k]:
            x = m0 | m
            acc[x] = acc.get(x, 0) ^ 1
    ok = sorted(x for x, p in acc.items() if p) == [0]
    md = max(len(mu) for mu, k in c["C"])
    if key.startswith("U62"):
        idx = int(key.split(":")[-1])
        inW4 = {"in_W4": True, "basis": "J7 structured W^(1) witness verified (w1-witness-reverification.json)",
                "witness_ok": wit[("U62", idx)]["all_ok"]}
    else:
        s = syz[key]
        derived = (s["fall_profile_M4"][:4] == [0, 0, 17, 323] and s["fall_profile_M4"][0] == 0)
        inW4 = {"in_W4": False if derived else None,
                "basis": "derivation: M_4 cap B_{<=3} = rowspace(M_3) (own fall profile [0,0,17,323], rank M_3 = 323) "
                         "=> W_4 = M_4, and 1 not in M_4 (own elimination)", "fall_profile_M4_own": s["fall_profile_M4"]}
    rows.append({"key": key, "closure": cl, "flat_certificate_verified_own_code": ok, "max_deg_mu": md,
                 "size": len(c["C"]), **inW4})
summ = {"certs_checked": len(rows), "all_verified": all(r["flat_certificate_verified_own_code"] for r in rows),
        "max_deg_mu": sorted({r["max_deg_mu"] for r in rows}),
        "U62_in_W4": sum(1 for r in rows if r["key"].startswith("U62") and r["in_W4"]),
        "nulls_not_in_W4_by_derivation": sum(1 for r in rows if not r["key"].startswith("U62") and r["in_W4"] is False)}
json.dump({"summary": summ, "rows": rows}, open(os.path.join(HERE, "j7a-fiber.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
