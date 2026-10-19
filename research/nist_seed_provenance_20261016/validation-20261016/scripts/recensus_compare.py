#!/usr/bin/env python3
"""Merge the independent early-abort re-census (out/recensus_raw_*.txt) into
out/recensus_orders_<t>.txt ("i N0 Nt", 0 = early abort, sorted by i), log their hashes,
and compare row by row with the recorded census/orders_<t>.txt.

Mine: N0 = ellsea(E,1), Nt = ellsea(E_twist,1) on the twist model y^2 = x^3 - 3d^2 x + d^3 b0,
both independently (no derivation of one from the other).
Per column, a row is
  exact          : same value (both 0, or the same order)
  zero_vs_composite : one side 0, the other a nonzero COMPOSITE value whose smallest prime
                   factor is small (an early-abort bookkeeping difference, not a disagreement);
                   checked: the nonzero side is consistent with 2(p+1) - (other column)
  MISMATCH       : two different nonzero values, or 0 against a prime value
Classification is then re-run on MY counts with the stated criteria.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import gmpy2

P = load_params()
mine = {}
for fn in sorted(glob.glob(os.path.join(ROOT, "out", "recensus_raw_*.txt"))):
    for line in open(fn):
        t, i, n0, nt = map(int, line.split())
        assert (t, i) not in mine
        mine[(t, i)] = (n0, nt)


def spf_small(n, lim=10 ** 5):
    q = 2
    while q <= lim:
        if n % q == 0:
            return q
        q = int(gmpy2.next_prime(q))
    return None


res = {"runs": {}, "mismatches": [], "zero_vs_composite": [], "complete": True}
for t, field, count in RUNS:
    p = P[FIELD_CURVE[field]]["p"]
    bl = p.bit_length()
    cand = [int(x) for x in open(os.path.join(ROOT, "out", f"q4_candidates_{t}.txt"))]
    missing = [i for i in cand if (t, i) not in mine]
    if missing:
        res["complete"] = False
    path = os.path.join(ROOT, "out", f"recensus_orders_{t}.txt")
    with open(path, "w") as f:
        for i in cand:
            if (t, i) in mine:
                f.write(f"{i} {mine[(t, i)][0]} {mine[(t, i)][1]}\n")
    if not missing:
        order_log(f"independent early-abort re-census, my point counts run {t}", path)
    rec = {}
    for line in open(os.path.join(BUNDLE, "census", f"orders_{t}.txt")):
        i, n0, nt = map(int, line.split())
        rec[i] = (n0, nt)
    stats = {"rows_compared": 0, "exact_both": 0, "zero_vs_composite": 0, "mismatch": 0, "missing_mine": len(missing)}
    acc, bit, tw = [], [], []
    for i in cand:
        if (t, i) not in mine:
            continue
        stats["rows_compared"] += 1
        m0, mt = mine[(t, i)]
        r0, rt = rec.get(i, (None, None))
        row_ok = True
        for col, a, b, other_m, other_r in (("N0", m0, r0, mt, rt), ("Nt", mt, rt, m0, r0)):
            if a == b:
                continue
            nz = a if a else b
            side = "recorded" if b else "mine"
            if (a == 0 or b == 0) and nz and not gmpy2.is_prime(nz, 25):
                q = spf_small(nz)
                # the nonzero side must agree with the twist relation from the other column
                partner = other_r if side == "recorded" else other_m
                consistent = (partner == 0) or (nz == 2 * (p + 1) - partner)
                res["zero_vs_composite"].append({"t": t, "i": i, "col": col, "nonzero_side": side,
                                                 "spf": q, "twist_relation_consistent": consistent})
                stats["zero_vs_composite"] += 1
                if not consistent:
                    res["mismatches"].append({"t": t, "i": i, "col": col, "mine": a, "recorded": b,
                                              "why": "nonzero side inconsistent with 2(p+1) - other"})
                    row_ok = False
            else:
                res["mismatches"].append({"t": t, "i": i, "col": col, "mine": a, "recorded": b})
                stats["mismatch"] += 1
                row_ok = False
        if row_ok and m0 == r0 and mt == rt:
            stats["exact_both"] += 1
        # classification on my counts (twist value: mine, or derived from my N0)
        ntd = mt if mt else (2 * (p + 1) - m0 if m0 else 0)
        if m0 and gmpy2.is_prime(m0, 25):
            if m0.bit_length() > bl:
                bit.append(i)
            elif m0 != p and all(pow(p, k, m0) != 1 for k in range(1, 1024)):
                acc.append(i)
        elif ntd and gmpy2.is_prime(ntd, 25):
            tw.append(i)
    stats.update({"accepted": len(acc), "bitlen": len(bit), "twist_only": len(tw),
                  "accepted_idx": acc, "bitlen_idx": bit, "twist_only_idx": tw})
    res["runs"][str(t)] = stats
out = os.path.join(ROOT, "out", "recensus_compare.json")
with open(out, "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
print("complete:", res["complete"], "rows:", len(mine))
for t, s in res["runs"].items():
    print(t, {k: v for k, v in s.items() if not k.endswith("_idx")})
print("mismatches:", len(res["mismatches"]))
for m in res["mismatches"][:50]:
    print("  MISMATCH", m)
zs = res["zero_vs_composite"]
print("zero_vs_composite:", len(zs), "by side", {s: sum(1 for z in zs if z["nonzero_side"] == s) for s in ("mine", "recorded")},
      "max spf", max([z["spf"] or 10 ** 9 for z in zs], default=None),
      "inconsistent", sum(1 for z in zs if not z["twist_relation_consistent"]))
