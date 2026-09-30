#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J5: own exact aggregation.

Sources (raw only): instances.jsonl.gz, closures.jsonl.gz,
certificates.jsonl.gz, certificate-verification.json. It does NOT run or
import analysis.py, stats.py, report.py or any impl/ module.

Clopper-Pearson 95% (two-sided, alpha/2 = 1/40 each side):
  lower(x, n) = the p with P(X >= x | p) = 1/40 (0 if x = 0)
  upper(x, n) = the p with P(X <= x | p) = 1/40 (1 if x = n)
found by bisection over dyadic rationals p = a / 2^K with EXACT integer tails
(math.comb). The bracket width is 2^-K with K = 96, far below the printed
precision. Tails of the power table are exact Fractions; log10 comes from
mpmath at 60 digits, applied to the exact rational.
"""
from __future__ import annotations

import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import mpmath

mpmath.mp.dps = 60
WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
EXP = WT / "experiments/EXP-CERTBIN-ddfe75"
K = 96
ONE = 1 << K


def jl(p):
    return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]


# ---------------------------------------------------------------- exact CP
def tail_le(x, n, a):
    """40 * sum_{i<=x} C(n,i) a^i (2^K - a)^(n-i)  vs  2^(K n): returns the integer numerator
    of P(X <= x | p = a/2^K) scaled by 2^(K n)."""
    b = ONE - a
    return sum(math.comb(n, i) * a ** i * b ** (n - i) for i in range(x + 1))


def cp_upper(x, n):
    if x == n:
        return (ONE, ONE)
    lo, hi = 0, ONE          # P(X<=x|p) decreasing in p; find p with tail = 1/40
    tot = ONE ** n
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if 40 * tail_le(x, n, mid) > tot:   # tail > 1/40 -> p too small
            lo = mid
        else:
            hi = mid
    return (lo, hi)


def cp_lower(x, n):
    if x == 0:
        return (0, 0)
    lo, hi = 0, ONE          # P(X>=x|p) = 1 - P(X<=x-1|p), increasing in p
    tot = ONE ** n
    while hi - lo > 1:
        mid = (lo + hi) // 2
        ge = tot - tail_le(x - 1, n, mid)
        if 40 * ge < tot:                   # tail < 1/40 -> p too small
            lo = mid
        else:
            hi = mid
    return (lo, hi)


def dec(a, digits=30):
    return mpmath.nstr(mpmath.mpf(a) / mpmath.mpf(ONE), digits)


def cp(x, n):
    if n == 0:
        return {"x": x, "n": n, "defined": False, "note": "0/0: rate and interval undefined"}
    L, U = cp_lower(x, n), cp_upper(x, n)
    lo = mpmath.mpf(L[0]) / ONE
    hi = mpmath.mpf(U[1]) / ONE
    return {"x": x, "n": n, "defined": True, "lower_bracket_hi": dec(L[1]), "upper_bracket_lo": dec(U[0]),
            "lower": float(lo), "upper": float(hi), "lower_6": round(float(mpmath.mpf(L[1]) / ONE), 6),
            "upper_6": round(float(mpmath.mpf(U[0]) / ONE), 6),
            "lower_20sig": mpmath.nstr(mpmath.mpf(L[1]) / ONE, 20), "upper_20sig": mpmath.nstr(mpmath.mpf(U[0]) / ONE, 20),
            "position": ("ceiling" if x == n else "floor" if x == 0 else "interior")}


# ---------------------------------------------------------------- raw data
inst = {r["key"]: r for r in jl(RUN / "instances.jsonl.gz")}
cl = {(r["key"], r["closure"]): r for r in jl(RUN / "closures.jsonl.gz")}
certs = jl(RUN / "certificates.jsonl.gz")
cv = json.load(open(RUN / "certificate-verification.json"))
ver = {c["cid"]: c for c in cv["certificates"]}
assert len(ver) == len(certs) == cv["n_submitted"]

wdag_ok = set()     # keys with a VERIFIED wdag-v1 (closure W_4)
wflat2_ok = set()   # keys with a verified W_4 flat-v1 with max|mu| <= 2
m4_ok = set()       # keys with a verified M_4 flat-v1 with max|mu| <= 2 (or one-node M_4 wdag)
ver_by_kind = defaultdict(Counter)
for c in certs:
    v = ver[c["cid"]]
    assert v["key"] == c["key"] and v["closure"] == c["closure"] and v["format"] == c["format"]
    kind = f'{c["closure"]}|{c["arm"]}|{c["format"]}'
    ver_by_kind[kind]["submitted"] += 1
    ver_by_kind[kind]["verified"] += int(bool(v["verified"]))
    ver_by_kind[kind]["failed"] += int(not v["verified"])
    mx = max((len(mu) for mu, _ in c["body"]), default=0) if c["format"] == "flat-v1" else None
    if not v["verified"]:
        continue
    if c["closure"] == "W_4" and c["format"] == "wdag-v1":
        wdag_ok.add(c["key"])
    if c["closure"] == "W_4" and c["format"] == "flat-v1" and mx <= 2:
        wflat2_ok.add(c["key"])
    if c["closure"] == "M_4" and c["format"] == "flat-v1" and mx <= 2:
        m4_ok.add(c["key"])
    if c["closure"] == "M_4" and c["format"] == "wdag-v1" and len(c["body"]["nodes"]) == 1 and not c["body"]["nodes"][0]["prods"]:
        m4_ok.add(c["key"])

ARMS = ["S3-U62", "S3-C20", "NULL-AFF62", "NULL-F262", "NELL-A20", "N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"]
unsat = {a: [k for k, r in inst.items() if r["arm"] == a and r["role"] == "unsat"] for a in ARMS}
unsat["S_3 (82)"] = unsat["S3-U62"] + unsat["S3-C20"]
exhausted = []   # instances has 144/144 unsat per fresh arm; J2 replay: no EXHAUSTED slot
OUT = {"task": "TASK-20260926-0f8aec", "joint": "J5"}
arms = {}
for a, keys in unsat.items():
    eng_w = [k for k in keys if cl[(k, "W_4")]["one"]]
    w = [k for k in keys if k in wdag_ok]
    w_alt = [k for k in keys if k in wdag_ok or k in wflat2_ok]
    unc = [k for k in eng_w if k not in wdag_ok]
    m4 = [k for k in keys if k in m4_ok]
    m4_eng = [k for k in keys if cl[(k, "M_4")]["one"]]
    notm4 = [k for k in keys if k not in m4_ok and not cl[(k, "M_4")]["one"]]
    arms[a] = {"n": len(keys), "W4_engine": len(eng_w), "W4_verified_wdag": len(w),
               "W4_verified_wdag_or_flat_mu_le2": len(w_alt), "W4_uncertified": len(unc),
               "W4_cp95": cp(len(w), len(keys)), "M4_engine": len(m4_eng), "M4_verified_flat_mu_le2": len(m4),
               "M4_cp95": cp(len(m4), len(keys)),
               "W4_given_not_M4": cp(sum(1 for k in notm4 if k in wdag_ok), len(notm4))}
OUT["arms"] = arms
# MN1 with L1 / L2
nconv = unsat["N-CONV"]
unc = [k for k in nconv if cl[(k, "W_4")]["one"] and k not in wdag_ok]
nC = 144 - len(exhausted)
w = sum(1 for k in nconv if k in wdag_ok)


def dr1_label(w, n):
    t, l, h = math.ceil(Fraction(9, 10) * n), math.floor(Fraction(1, 10) * n), n // 2
    lab = "TENSOR" if w >= t else "LINEAR" if w <= l else "MIXED"
    return {"w": w, "n_C": n, "thresholds": {"tensor": t, "linear": l, "half": h}, "label": lab,
            "E_TENSOR_falsified": w <= h, "E_LINEAR_falsified": w > h, "cp95": cp(w, n),
            "evaluable": n >= 120}


OUT["MN1"] = {"L1": dr1_label(w, nC), "L2": dr1_label(w, nC - len(unc)), "uncertified": len(unc), "exhausted": exhausted}
# N-CONV by source; paired 2x2
by_src = defaultdict(lambda: [0, 0])
for k in nconv:
    s = inst[k]["source_set"]
    by_src[s][1] += 1
    by_src[s][0] += int(k in wdag_ok)
OUT["N-CONV_by_source"] = {s: cp(x, n) for s, (x, n) in by_src.items()}
s3slot = {inst[k]["slot"]: k for k in unsat["S_3 (82)"]}
nslot = {inst[k]["slot"]: k for k in nconv}
pair = Counter()
for slot, k3 in s3slot.items():
    pair[(k3 in wdag_ok, nslot[slot] in wdag_ok)] += 1
OUT["paired_S3_vs_NCONV_W4"] = {"S3_ref_NCONV_ref": pair[(True, True)], "S3_ref_NCONV_not": pair[(True, False)],
                                "S3_not_NCONV_ref": pair[(False, True)], "S3_not_NCONV_not": pair[(False, False)],
                                "pairs": sum(pair.values())}
# references quoted by the rules
OUT["refs"] = {"S3_386_of_386": cp(386, 386), "stage1_324_of_386": cp(324, 386)}
# certificates per kind
OUT["certificates_per_kind"] = {k: dict(v) for k, v in sorted(ver_by_kind.items())}
OUT["uncertified_all_arms"] = sorted(k for k, r in inst.items() if cl[(k, "W_4")]["one"] and k not in wdag_ok)
# satisfiable controls (MN3 C-PS counts) and codim = s fraction
sat = defaultdict(Counter)
for k, r in inst.items():
    if r["role"] != "sat":
        continue
    c = sat[r["arm"]]
    c["n"] += 1
    c["M4_refuted_engine"] += int(bool(cl[(k, "M_4")]["one"]))
    c["W4_refuted_engine"] += int(bool(cl[(k, "W_4")]["one"]))
    c["certificates_verified"] += int(k in wdag_ok or k in m4_ok or k in wflat2_ok)
    if r["s"] <= 31:
        cd = 4048 - cl[(k, "W_4")]["final_dim"]
        c["s_le_31"] += 1
        c["codim_ge_s"] += int(cd >= r["s"])
        c["codim_eq_s"] += int(cd == r["s"])
OUT["satisfiable_controls"] = {a: dict(c) for a, c in sat.items()}
# NC-DR-5 profile fractions (R5 reading; also reported under the literal alternatives)
SUB = [0, 0, 16, 288, 2328]
UNS = [0, 0, 17, 323, 2771]
prof = {}
for a in ARMS + ["S3-S62"]:
    for pop in ("unsat", "sat", "all"):
        keys = [k for k, r in inst.items() if r["arm"] == a and (pop == "all" or r["role"] == pop)]
        if not keys:
            continue
        ref = sub = t5 = 0
        for k in keys:
            rb = cl[(k, "rc_b")]
            if rb["substituted"]:
                sub += 1
                t5 += int(bool(rb["T5_applicable"]))
                ref += int(cl[(k, "R'_4")]["dims_by_deg"] == SUB)
            elif rb["kernel_dim"] == 0:
                ref += int(cl[(k, "M_4")]["dims_by_deg"] == UNS)
        f = Fraction(ref, len(keys))
        lab = "SEMI-REGULAR TRANSFER HOLDS" if f >= Fraction(9, 10) else "FAILS" if f <= Fraction(1, 10) else "MIXED"
        prof[f"{a}|{pop}"] = {"n": len(keys), "reference_profile": ref, "fraction": str(f), "substituted": sub,
                              "T5_applicable": t5, "T5_applicable_fraction": str(Fraction(t5, len(keys))), "label": lab}
OUT["NC-DR-5_profiles"] = prof
# draw statistics (descriptive)
ds = {}
for arm in ("N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"):
    L = jl(RUN / f"draws-{arm}.jsonl.gz")
    ev = [r for r in L if r["s"] is not None]
    per = Counter(r["slot"] for r in L)
    ds[arm] = {"attempts": len(L), "evaluated": len(ev), "unsat_among_evaluated": f"{sum(1 for r in ev if r['s'] == 0)}/{len(ev)}",
               "rejections": dict(Counter(r["outcome"] for r in L if r["outcome"].startswith("rejected"))),
               "attempts_per_slot_max": max(per.values()), "attempts_per_slot_mean": str(Fraction(len(L), 144))}
OUT["draw_statistics"] = ds
# power table (exact)
P = [Fraction(3, 100), Fraction(1, 10), Fraction(1, 2), Fraction(9, 10), Fraction(97, 100)]
n = 144


def pmf(i, p):
    return math.comb(n, i) * p ** i * (1 - p) ** (n - i)


pt = []
for p in P:
    ge130 = sum(pmf(i, p) for i in range(130, n + 1))
    le14 = sum(pmf(i, p) for i in range(0, 15))
    le72 = sum(pmf(i, p) for i in range(0, 73))
    row = {"p": str(p)}
    for name, val in (("P(w >= 130)", ge130), ("P(w <= 14)", le14), ("P(w <= 72)", le72)):
        mv = mpmath.mpf(val.numerator) / mpmath.mpf(val.denominator)
        row[name] = {"value_20sig": mpmath.nstr(mv, 20), "log10": mpmath.nstr(mpmath.log10(mv), 15),
                     "one_minus_value_20sig": mpmath.nstr(1 - mv, 20)}
    pt.append(row)
OUT["power_table_exact"] = {"n": n, "thresholds": {"tensor": math.ceil(Fraction(9, 10) * n), "linear": math.floor(Fraction(1, 10) * n),
                                                   "half": n // 2}, "rows": pt}
json.dump(OUT, open(OUTDIR / "j5-recompute.json", "w"), indent=1, default=str)
print(json.dumps({"MN1": OUT["MN1"], "arms_summary": {a: (v["W4_verified_wdag"], v["n"], v["M4_verified_flat_mu_le2"],
                                                         v["W4_given_not_M4"].get("x"), v["W4_given_not_M4"]["n"])
                                                     for a, v in arms.items()}}, default=str, indent=0)[:4000])
