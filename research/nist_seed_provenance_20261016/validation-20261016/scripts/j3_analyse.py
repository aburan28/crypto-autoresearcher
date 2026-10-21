#!/usr/bin/env python3
"""J3 / J4 analysis of the full counts (out/j3_fullcounts.txt) against the recorded orders.

Checks per row: recorded nonzero N0 == N (full ellcard); recorded nonzero Nt == 2(p+1) - N;
recorded N0 = 0 -> N not prime, smallest prime factor reported (flag > 1000); same for Nt;
prime N / prime Nt certified by N*P = O on 3 random points (+ Hasse), independent of SEA.
J4: twist-only recomputed from the full counts for the counted rows, recorded orders elsewhere.
Writes out/j3_analysis.json.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import gmpy2

P = load_params()
LIM = 10 ** 6
sieve = bytearray([1]) * (LIM + 1)
sieve[0] = sieve[1] = 0
for k in range(2, int(LIM ** 0.5) + 1):
    if sieve[k]:
        sieve[k * k::k] = bytearray(len(sieve[k * k::k]))
PRIMES = [k for k in range(LIM + 1) if sieve[k]]


def spf(n):
    for q in PRIMES:
        if n % q == 0:
            return q
    return None  # > 10^6


rec = {}
for t, field, count in RUNS:
    for line in open(os.path.join(BUNDLE, "census", f"orders_{t}.txt")):
        i, n0, nt = map(int, line.split())
        rec[(t, i)] = (n0, nt)
pfield = {t: P[FIELD_CURVE[f]]["p"] for t, f, c in RUNS}
sample = json.load(open(os.path.join(ROOT, "out", "j3_sample.json")))
cls = json.load(open(os.path.join(ROOT, "out", "j5_classification.json")))

rows = []
for line in open(os.path.join(ROOT, "out", "j3_fullcounts.txt")):
    f = line.split()
    t, i, N, Nt, pN, pNt, hasse, cN, cT = map(int, f[:9])
    rows.append(dict(t=t, i=i, N=N, Nt=Nt, pN=pN, pNt=pNt, hasse=hasse, cN=cN, cT=cT,
                     demo_minus_b=int(f[9]) if len(f) > 9 else None))

mism, flags, checks = [], [], []
by_run = {}
for r in rows:
    t, i, p = r["t"], r["i"], pfield[r["t"]]
    n0r, ntr = rec[(t, i)]
    c = {"t": t, "i": i}
    assert r["Nt"] == 2 * (p + 1) - r["N"]
    assert bool(r["pN"]) == bool(gmpy2.is_prime(r["N"], 25)) and bool(r["pNt"]) == bool(gmpy2.is_prime(r["Nt"], 25))
    if not r["hasse"]:
        mism.append({**c, "what": "full count outside Hasse"})
    if n0r:
        c["N0"] = "match" if n0r == r["N"] else "MISMATCH"
        if n0r != r["N"]:
            mism.append({**c, "what": "recorded N0 != full count", "recorded": n0r, "full": r["N"]})
    else:
        if r["pN"]:
            c["N0"] = "ZERO_BUT_PRIME"
            mism.append({**c, "what": "recorded N0 = 0 but true order prime", "full": r["N"]})
        else:
            q = spf(r["N"])
            c["N0"] = f"zero_ok spf={q}"
            c["spf_N"] = q
            if q is None or q > 1000:
                flags.append({**c, "what": "N0 = 0 with smallest prime factor > 1000", "spf": q})
    if ntr:
        c["Nt"] = "match" if ntr == r["Nt"] else "MISMATCH"
        if ntr != r["Nt"]:
            mism.append({**c, "what": "recorded Nt != 2(p+1) - N", "recorded": ntr, "full": r["Nt"]})
    else:
        if r["pNt"]:
            c["Nt"] = "ZERO_BUT_PRIME"
            mism.append({**c, "what": "recorded Nt = 0 but true twist order prime", "full": r["Nt"]})
        else:
            q = spf(r["Nt"])
            c["Nt"] = f"zero_ok spf={q}"
            c["spf_Nt"] = q
            if q is None or q > 1000:
                flags.append({**c, "what": "Nt = 0 with smallest prime factor > 1000", "spf": q})
    if r["pN"] and r["cN"] != 1:
        mism.append({**c, "what": "prime N failed N*P = O"})
    if r["pNt"] and r["cT"] != 1:
        mism.append({**c, "what": "prime Nt failed Nt*Q = O on twist"})
    c["prime_N_certified"] = bool(r["pN"] and r["cN"] == 1 and r["hasse"])
    c["prime_Nt_certified"] = bool(r["pNt"] and r["cT"] == 1 and r["hasse"])
    if r["demo_minus_b"] is not None:
        c["minus_b_order"] = r["demo_minus_b"]
        c["minus_b_is_twist"] = r["demo_minus_b"] == r["Nt"]
        c["minus_b_is_same"] = r["demo_minus_b"] == r["N"]
    checks.append(c)
    b = by_run.setdefault(t, {"rows": 0, "N0_nonzero_checked": 0, "Nt_nonzero_checked": 0,
                              "N0_zero_checked": 0, "Nt_zero_checked": 0, "prime_N": 0, "prime_Nt": 0,
                              "max_spf": 0})
    b["rows"] += 1
    b["N0_nonzero_checked" if n0r else "N0_zero_checked"] += 1
    b["Nt_nonzero_checked" if ntr else "Nt_zero_checked"] += 1
    b["prime_N"] += r["pN"]; b["prime_Nt"] += r["pNt"]
    for k in ("spf_N", "spf_Nt"):
        if c.get(k):
            b["max_spf"] = max(b["max_spf"], c[k])

# J4: twist-only from full counts where counted, recorded orders elsewhere
full = {(r["t"], r["i"]): r for r in rows}
tw = {}
for t, field, count in RUNS:
    n = 0
    for (tt, i), (n0r, ntr) in rec.items():
        if tt != t:
            continue
        if (t, i) in full:
            r = full[(t, i)]
            if not r["pN"] and r["pNt"]:
                n += 1
        else:
            if not (n0r and gmpy2.is_prime(n0r, 25)) and ntr and gmpy2.is_prime(ntr, 25):
                n += 1
    tw[str(t)] = n
# J4 numeric demonstration: y^2 = x^3 - 3x - b0 counted fully (out/j4_demo_fullcounts.txt)
demo = []
dp = os.path.join(ROOT, "out", "j4_demo_fullcounts.txt")
if os.path.exists(dp):
    for line in open(dp):
        f = line.split()
        t, i, N, Nt = int(f[0]), int(f[1]), int(f[2]), int(f[3])
        mb = int(f[9])
        p = pfield[t]
        demo.append({"t": t, "i": i, "p_mod_4": p % 4, "minus_b_order_equals_twist": mb == Nt,
                     "minus_b_order_equals_curve": mb == N,
                     "expected": "twist" if p % 4 == 3 else "same (isomorphic, -1 is a square)",
                     "as_expected": (mb == Nt) if p % 4 == 3 else (mb == N)})
res = {"n_rows": len(rows), "j4_minus_b_demo": demo, "mismatches": mism, "flags_spf_gt_1000": flags, "by_run": {str(k): v for k, v in by_run.items()},
       "twist_only_recount": tw, "twist_only_total": sum(tw.values()), "checks": checks}
out = os.path.join(ROOT, "out", "j3_analysis.json")
with open(out, "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
print("rows counted", len(rows), "mismatches", len(mism), "spf>1000 flags", len(flags))
for m in mism: print("  MISMATCH", m)
for fl in flags: print("  FLAG", fl)
for t, b in by_run.items(): print(t, b)
print("twist-only recount", tw, "total", res["twist_only_total"])
for d in demo: print("J4 demo", d)
spfs = sorted(set(c.get("spf_N") for c in checks if c.get("spf_N")) | set(c.get("spf_Nt") for c in checks if c.get("spf_Nt")))
print("distinct smallest prime factors seen on zero rows:", spfs)
