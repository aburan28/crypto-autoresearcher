"""J4: the validator's OWN aggregation of RUN-CERTBIN-a3fc60 (does not run or import analysis.py or impl/).

Inputs (archived bytes): closures.jsonl.gz, certificates.jsonl.gz, certificate-verification.json,
annihilator-verification.json, instances.jsonl.gz (arm / role / stratum / family / slot fields only),
trial-plan-v1.json (power table, for comparison only).
Exact arithmetic: Clopper-Pearson 95% bounds by bisection on dyadic rationals with the exact binomial
CDF (math.comb, fractions.Fraction), to 2^-70; Fisher one-sided tails exactly (hypergeometric, math.comb).
Rules are applied literally from experiments/EXP-CERTBIN-060020/specification.yaml decision_rules.
Output: j4-recompute/recomputed.json
usage: python3 aggregate.py <run_dir> <trial_plan_path>
"""
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RUN, PLAN = sys.argv[1], sys.argv[2]


def jl(name):
    with gzip.open(os.path.join(RUN, name), "rt") as fh:
        return [json.loads(l) for l in fh]


clo = {r["key"]: r for r in jl("closures.jsonl.gz")}
inst = {r["key"]: r for r in jl("instances.jsonl.gz")}
certs = jl("certificates.jsonl.gz")
cv = json.load(open(os.path.join(RUN, "certificate-verification.json")))
av = json.load(open(os.path.join(RUN, "annihilator-verification.json")))

# ------------------------------------------------------------------ exact statistics
PREC = 70


def binom_cdf_le(x, n, p):
    """P(X <= x), X ~ Bin(n, p), p a Fraction: exact."""
    q = 1 - p
    return sum(Fraction(math.comb(n, k)) * p ** k * q ** (n - k) for k in range(0, x + 1))


_CP = {}


def cp95(x, n):
    if (x, n) not in _CP:
        _CP[(x, n)] = _cp95(x, n)
    return _CP[(x, n)]


def _cp95(x, n):
    """Exact Clopper-Pearson two-sided 95%: lower solves P(X >= x | p) = 0.025, upper solves P(X <= x | p) = 0.025.
    Returned as Fractions bracketed to 2^-PREC (lower rounded down, upper rounded up)."""
    a = Fraction(1, 40)
    if x == 0:
        lo = Fraction(0)
    else:
        l, h = Fraction(0), Fraction(1)
        for _ in range(PREC):  # P(X >= x | p) increasing in p
            m = (l + h) / 2
            if 1 - binom_cdf_le(x - 1, n, m) < a:
                l = m
            else:
                h = m
        lo = l
    if x == n:
        up = Fraction(1)
    else:
        l, h = Fraction(0), Fraction(1)
        for _ in range(PREC):  # P(X <= x | p) decreasing in p
            m = (l + h) / 2
            if binom_cdf_le(x, n, m) > a:
                l = m
            else:
                h = m
        up = h
    return lo, up


def fnum(f, d=6):
    return round(float(f), d)


def ci(x, n):
    lo, up = cp95(x, n)
    return {"x": x, "n": n, "rate": fnum(Fraction(x, n)) if n else None, "cp95": [fnum(lo, 6), fnum(up, 6)],
            "_lo": lo, "_up": up}


def fisher_one_sided_greater(a, n1, b, n2):
    """P(A >= a) for A ~ Hypergeometric(total n1+n2, successes a+b, draws n1): X2E higher than pooled."""
    N = n1 + n2
    K = a + b
    den = math.comb(N, n1)
    num = sum(math.comb(K, i) * math.comb(N - K, n1 - i) for i in range(a, min(K, n1) + 1))
    return Fraction(num, den)


def log10_frac(f):
    if f == 0:
        return None
    return math.log10(f.numerator) - math.log10(f.denominator)


# ------------------------------------------------------------------ per-certificate verification
vres = defaultdict(dict)  # (key, closure) -> format -> verification row
for r in cv["results"]:
    vres[(r["key"], r["closure"])][r["format"]] = r
arm_of = {k: inst[k]["arm"] for k in inst}
role_of = {k: inst[k]["role"] for k in inst}

# recount certificates by (closure, arm, format)
submitted = Counter((c["closure"], arm_of[c["key"]], c["format"]) for c in certs)
recount = {}
for key3 in sorted(submitted):
    clos, arm, fmt = key3
    rows = [vres[(c["key"], clos)].get(fmt) for c in certs if c["closure"] == clos and arm_of[c["key"]] == arm and c["format"] == fmt]
    ver = sum(1 for r in rows if r and r["valid"])
    cnt = sum(1 for r in rows if r and r["valid"] and r.get("counts"))
    mx = Counter(r["max_mu"] for r in rows if r)
    recount["|".join(key3)] = {"submitted": submitted[key3], "verified": ver, "failed": submitted[key3] - ver,
                               "counting": cnt, "max_mu_distribution": dict(sorted(mx.items()))}
# cross-check that the certificate list and the verification list correspond one to one
cv_pairs = Counter((r["key"], r["closure"], r["format"]) for r in cv["results"])
ce_pairs = Counter((c["key"], c["closure"], c["format"]) for c in certs)
recount_consistency = {"certificates_in_file": len(certs), "verification_rows": len(cv["results"]),
                       "same_multiset": cv_pairs == ce_pairs}


def verified_wdag_W4(k):
    r = vres.get((k, "W_4"), {}).get("wdag-v1")
    return bool(r and r["valid"])


def verified_flat_M4_le2(k):
    r = vres.get((k, "M_4"), {}).get("flat-v1")
    return bool(r and r["valid"] and r["max_mu"] <= 2)


def verified_W4_any_counting(k):
    """W_4 counted: wdag-v1 valid, or (never here) a flat certificate with max|mu| <= 2."""
    if verified_wdag_W4(k):
        return True
    r = vres.get((k, "W_4"), {}).get("flat-v1")
    return bool(r and r["valid"] and r["max_mu"] <= 2)


def keys(arm, role="unsat", stratum=None, family=None):
    return [k for k, r in inst.items() if r["arm"] == arm and r["role"] == role
            and (stratum is None or r.get("stratum") == stratum) and (family is None or r.get("family") == family)]


def undetermined(k):
    return clo[k].get("label") == "UNDETERMINED(budget)" or "W_4" not in clo[k]


def engine_one(k, c):
    return bool(clo[k].get(c, {}).get("one"))


out = {"inputs": {f: None for f in ("closures.jsonl.gz", "certificates.jsonl.gz", "certificate-verification.json",
                                    "annihilator-verification.json", "instances.jsonl.gz")}}
import hashlib  # noqa: E402

for f in out["inputs"]:
    out["inputs"][f] = hashlib.sha256(open(os.path.join(RUN, f), "rb").read()).hexdigest()

U = keys("S3-U400")
N0 = len(U)
out["S3-U400_size"] = N0
out["undetermined_S3-U400"] = [k for k in U if undetermined(k)]
out["certificate_recount"] = recount
out["certificate_recount_consistency"] = recount_consistency

# ------------------------------------------------------------------ MR19-1 / N19-DR-1
eng_ref_W4 = [k for k in U if engine_one(k, "W_4")]
ver_W4 = [k for k in U if verified_wdag_W4(k)]
uncert = [k for k in eng_ref_W4 if not verified_W4_any_counting(k)]
undet = [k for k in U if undetermined(k)]
w = len(ver_W4)
N_L1 = N0
N_L2 = N0 - len(set(uncert) | set(undet))


def dr1_label(w, N):
    if N < 300:
        return "NOT EVALUABLE (sample)"
    if w >= math.ceil(Fraction(9, 10) * N):
        return "PERSISTS"
    if w <= math.floor(Fraction(1, 10) * N):
        return "DECAYS"
    return "PARTIAL"


L1 = dr1_label(w, N_L1)
L2 = dr1_label(w, N_L2)
ci1 = ci(w, N_L1)
lo386, up386 = cp95(386, 386)
dr1 = {"w": w, "N_L1": N_L1, "N_L2": N_L2, "L1": L1, "L2": L2,
       "verdict": L1 if L1 == L2 else "UNDETERMINED (budget or certification)",
       "thresholds": {"ceil_0.9N": math.ceil(Fraction(9, 10) * N_L1), "floor_0.1N": math.floor(Fraction(1, 10) * N_L1), "floor_N/2": N_L1 // 2},
       "cp95_L1": ci1["cp95"], "cp95_L2": ci(w, N_L2)["cp95"] if N_L2 else None,
       "E-PERSIST_falsified": w <= N_L1 // 2, "E-DECAY_falsified": w > N_L1 // 2,
       "engine_reported_W4_refutations": len(eng_ref_W4), "uncertified": uncert, "undetermined": undet,
       "n17_cp95_lower_386_of_386": fnum(lo386, 8),
       "n17_comparison": "NO DETECTABLE DROP FROM n = 17" if ci1["_up"] >= lo386 else "BELOW THE n = 17 FIGURE"}
out["N19-DR-1"] = dr1
out["MR19-1"] = {"w": w, "N": N_L1, "cp95": ci1["cp95"], "counts_wdag_v1_only": True,
                 "flat_W4_certs_counting_toward_W4": sum(1 for k in U if (vres.get((k, "W_4"), {}).get("flat-v1") or {}).get("max_mu", 9) <= 2)}

# ------------------------------------------------------------------ N19-DR-2
m4_ver = [k for k in U if verified_flat_M4_le2(k)]
m4_eng = [k for k in U if engine_one(k, "M_4")]
m3_eng = [k for k in U if engine_one(k, "M_3")]
m3_ver = [k for k in U if (vres.get((k, "M_3"), {}).get("flat-v1") or {}).get("valid")]
c2 = ci(len(m4_ver), N0)
if c2["_up"] < Fraction(799, 1000):
    dr2v = "LOWER"
elif c2["_lo"] > Fraction(875, 1000):
    dr2v = "HIGHER"
else:
    dr2v = "CONSISTENT"
notM4 = [k for k in U if not engine_one(k, "M_4")]
cond = ci(sum(1 for k in notM4 if verified_wdag_W4(k)), len(notM4)) if notM4 else None
out["N19-DR-2"] = {"m_verified_M4": len(m4_ver), "m_engine_M4": len(m4_eng), "N": N0, "cp95": c2["cp95"], "verdict": dr2v,
                   "reference_interval": [0.799, 0.875],
                   "conditional_W4_rate_on_M4_nonrefuted": {k: v for k, v in (cond or {}).items() if not k.startswith("_")},
                   "M3_count_engine": len(m3_eng), "M3_count_verified": len(m3_ver)}

# ------------------------------------------------------------------ MR19-2 / N19-DR-3
rcb_app = [k for k in U if clo[k]["rc_b"].get("applicable") and "R4" in clo[k]["rc_b"]]
Nb = len(rcb_app)
sig = [clo[k]["rc_b"]["sigma"] for k in rcb_app]
for k in rcb_app:
    assert clo[k]["rc_b"]["sigma"] == clo[k]["rc_b"]["R4"]["dims_by_deg"][3] - 360
gt = sum(1 for s in sig if s > 0)
eq = sum(1 for s in sig if s == 0)
lt = sum(1 for s in sig if s < 0)
full = sum(1 for k in rcb_app if clo[k]["rc_b"]["R4"]["dims_by_deg"][3] == 1160)
if Nb < 300:
    dr3v = "NOT EVALUABLE (sample)"
elif gt >= math.ceil(Fraction(9, 10) * Nb):
    dr3v = "NON-SEMI-REGULAR PERSISTS"
elif eq >= math.ceil(Fraction(9, 10) * Nb):
    dr3v = "SEMI-REGULAR AT n = 19"
else:
    dr3v = "MIXED"
prof = Counter(tuple(clo[k]["rc_b"]["R4"]["dims_by_deg"]) for k in rcb_app)
out["N19-DR-3"] = {"N_b": Nb, "sigma_gt_0": gt, "sigma_eq_0": eq, "sigma_lt_0": lt, "ceil_0.9Nb": math.ceil(Fraction(9, 10) * Nb),
                   "full_1160": full, "full_fraction": fnum(Fraction(full, Nb)) if Nb else None, "verdict": dr3v,
                   "sigma_distribution": dict(sorted(Counter(sig).items())),
                   "R4_profile_distribution": {str(list(p)): c for p, c in prof.most_common()}}
out["MR19-2"] = {k: out["N19-DR-3"][k] for k in ("N_b", "sigma_gt_0", "sigma_eq_0", "sigma_lt_0", "full_1160")}

# ------------------------------------------------------------------ MR19-3 per arm and closure
ARMS = ["S3-U400", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"]


def rates(ks):
    return {"W_4": ci(sum(1 for k in ks if verified_wdag_W4(k)), len(ks)),
            "M_4": ci(sum(1 for k in ks if verified_flat_M4_le2(k)), len(ks)),
            "W_4_engine": sum(1 for k in ks if engine_one(k, "W_4")),
            "M_4_engine": sum(1 for k in ks if engine_one(k, "M_4")),
            "M_3_engine": sum(1 for k in ks if engine_one(k, "M_3"))}


def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if not (isinstance(k, str) and k.startswith("_"))}
    return d


per_arm = {a: rates(keys(a)) for a in ARMS}
per_stratum = {s: rates(keys("F-RANDX19", stratum=s)) for s in ("X2E", "XE-NOT-2E", "TWIST")}
per_family = {d: rates(keys("N-AFF19", family=d)) for d in range(1, 6)}
out["MR19-3"] = {"per_arm_unsat": strip(per_arm), "F-RANDX19_per_stratum": strip(per_stratum),
                 "N-AFF19_per_family": strip(per_family)}
# C-PS on satisfiable controls
sat = [k for k in inst if role_of[k] == "sat"]
cps = {"n": len(sat), "refuted_any": 0, "codim_lt_s": 0, "s_le_31": 0, "codim_eq_s_where_s_le_31": 0, "per_arm": {}}
for k in sat:
    r = clo[k]
    s = inst[k]["s"]
    codim = 6196 - r["W_4"]["final_dim"]
    ref = engine_one(k, "M_3") or engine_one(k, "M_4") or engine_one(k, "W_4")
    cps["refuted_any"] += ref
    cps["codim_lt_s"] += codim < s
    a = arm_of[k]
    pa = cps["per_arm"].setdefault(a, {"n": 0, "refuted": 0, "codim_lt_s": 0, "s_le_31": 0, "codim_eq_s": 0})
    pa["n"] += 1
    pa["refuted"] += ref
    pa["codim_lt_s"] += codim < s
    if s <= 31:
        cps["s_le_31"] += 1
        cps["codim_eq_s_where_s_le_31"] += codim == s
        pa["s_le_31"] += 1
        pa["codim_eq_s"] += codim == s
out["C-PS_recount"] = cps
out["ann-v1"] = {"submitted": av["submitted"], "verified_reported": av["verified"],
                 "verified_recount": sum(1 for r in av["results"] if r["valid"]),
                 "keys": [r["key"] for r in av["results"]]}

# ------------------------------------------------------------------ N19-DR-4
dr4 = {}
for clos in ("W_4", "M_4"):
    s3 = per_arm["S3-U400"][clos]
    row = {}
    for X in ("N-F219", "N-AFF19", "N-ELL19"):
        x = per_arm[X][clos]
        row[X] = {"S3_cp95_lower": fnum(s3["_lo"]), "X_cp95_upper": fnum(x["_up"]),
                  "X_count": f"{x['x']}/{x['n']}",
                  "verdict": "S_3 ABOVE X" if s3["_lo"] > x["_up"] else "NOT DISTINGUISHED"}
    fam = {}
    for d in range(1, 6):
        x = per_family[d][clos]
        fam[d] = {"X_count": f"{x['x']}/{x['n']}", "X_cp95_upper": fnum(x["_up"]),
                  "verdict": "S_3 ABOVE X" if s3["_lo"] > x["_up"] else "NOT DISTINGUISHED"}
    row["N-AFF19_per_family"] = fam
    dr4[clos] = row
out["N19-DR-4"] = dr4

# ------------------------------------------------------------------ N19-DR-5
cv5 = per_arm["N-CONV19"]["W_4"]
wc, nc = cv5["x"], cv5["n"]
dr5v = "TENSOR-LEVEL" if wc >= math.ceil(Fraction(9, 10) * nc) else ("BELOW" if wc <= math.floor(Fraction(1, 10) * nc) else "MIXED")
s3w = per_arm["S3-U400"]["W_4"]
overlap = not (cv5["_up"] < s3w["_lo"] or s3w["_up"] < cv5["_lo"])
pair = {}
for clos in ("W_4", "M_4"):
    tab = Counter()
    for k in keys("N-CONV19"):
        s3k = inst[k]["s3_key"]
        a = verified_wdag_W4(s3k) if clos == "W_4" else verified_flat_M4_le2(s3k)
        b = verified_wdag_W4(k) if clos == "W_4" else verified_flat_M4_le2(k)
        tab[(a, b)] += 1
    pair[clos] = {"S3_ref&CONV_ref": tab[(True, True)], "S3_ref&CONV_not": tab[(True, False)],
                  "S3_not&CONV_ref": tab[(False, True)], "S3_not&CONV_not": tab[(False, False)]}
out["N19-DR-5"] = {"w_c": wc, "n_c": nc, "cp95": [fnum(cv5["_lo"]), fnum(cv5["_up"])], "verdict": dr5v,
                   "AT_S3_RATE": overlap,
                   "N-CONV19_ABOVE_N-ELL19": cv5["_lo"] > per_arm["N-ELL19"]["W_4"]["_up"],
                   "N-CONV19_ABOVE_N-F219": cv5["_lo"] > per_arm["N-F219"]["W_4"]["_up"],
                   "paired_2x2_on_shared_x_R": pair,
                   "shared_slots": len(set(inst[k]["slot"] for k in keys("N-CONV19")))}

# ------------------------------------------------------------------ N19-DR-6
dr6 = {}
for clos in ("M_4", "W_4"):
    x = per_stratum["X2E"][clos]
    o1 = per_stratum["XE-NOT-2E"][clos]
    o2 = per_stratum["TWIST"][clos]
    a, n1 = x["x"], x["n"]
    b, n2 = o1["x"] + o2["x"], o1["n"] + o2["n"]
    if (a == n1 and b == n2) or (a == 0 and b == 0):
        v = "SATURATED (not evaluable)"
        p = None
    else:
        p = fisher_one_sided_greater(a, n1, b, n2)
        v = "MODULATED" if p < Fraction(1, 100) else ("WEAK" if p < Fraction(1, 5) else "ABSENT")
    s3 = per_arm["S3-U400"][clos]
    rep = not (x["_up"] < s3["_lo"] or s3["_up"] < x["_lo"])
    dr6[clos] = {"X2E": f"{a}/{n1}", "pooled_XE-NOT-2E+TWIST": f"{b}/{n2}", "fisher_one_sided_p": None if p is None else float(p),
                 "fisher_log10_p": None if p is None else log10_frac(p), "verdict": v, "RANDX_X2E_REPLICATES_PRIMARY": rep,
                 "X2E_cp95": x["cp95"], "S3_cp95": s3["cp95"]}
out["N19-DR-6"] = dr6

# ------------------------------------------------------------------ N19-DR-7
REF_SUB = [0, 0, 18, 360, 3267]
REF_UNSUB = [0, 0, 19, 399, 3819]
ELL_ARMS = ("S3-U400", "S3-SAT100", "F-RANDX19", "N-CONV19", "N-ELL19")


def ref_ok(k):
    r = clo[k]
    if arm_of[k] in ELL_ARMS:
        rb = r["rc_b"]
        return bool(rb.get("applicable") and "R4" in rb and rb["R4"]["dims_by_deg"] == REF_SUB)
    return r["M_4"]["dims_by_deg"] == REF_UNSUB


def t5(k):
    rb = clo[k]["rc_b"]
    return bool(rb.get("T5_applicable"))


def dr7_label(f):
    if f >= Fraction(9, 10):
        return "SEMI-REGULAR TRANSFER HOLDS"
    if f <= Fraction(1, 10):
        return "FAILS"
    return "MIXED"


dr7 = {}
for a in ["S3-U400", "S3-SAT100", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"]:
    ks_both = [k for k in inst if arm_of[k] == a and not undetermined(k)]
    ks_unsat = [k for k in ks_both if role_of[k] == "unsat"]
    res = {}
    for nm, ks in (("both_roles", ks_both), ("unsat_only", ks_unsat)):
        if not ks:
            continue
        n_ref = sum(1 for k in ks if ref_ok(k))
        f = Fraction(n_ref, len(ks))
        res[nm] = {"reference": "substituted" if a in ELL_ARMS else "unsubstituted", "n": len(ks), "with_reference_profile": n_ref,
                   "fraction": fnum(f), "verdict": dr7_label(f),
                   "T5_applicable": sum(1 for k in ks if t5(k)), "T5_fraction": fnum(Fraction(sum(1 for k in ks if t5(k)), len(ks)))}
    res["readings_agree"] = len({v["verdict"] for kk, v in res.items() if isinstance(v, dict)}) == 1
    dr7[a] = res
out["N19-DR-7"] = dr7

# ------------------------------------------------------------------ N19-DR-9 / -10
out["N19-DR-9"] = {"mechanical_flag": "ELIGIBLE" if (L1 == "PERSISTS" and L2 == "PERSISTS") else "NOT ELIGIBLE",
                   "rule": "ELIGIBLE iff N19-DR-1 returns PERSISTS under both labels"}
out["N19-DR-10"] = {"primary": ["N19-DR-1", "N19-DR-3"]}

# ------------------------------------------------------------------ secondary
ref_unsub_S3 = sum(1 for k in U if clo[k]["M_4"]["dims_by_deg"] == REF_UNSUB)
out["secondary"] = {
    "S3-U400_M4_profile_distribution": {str(p): c for p, c in Counter(tuple(clo[k]["M_4"]["dims_by_deg"]) for k in U).most_common(8)},
    "S3-U400_W4_dims_distribution": {str(p): c for p, c in Counter(tuple(clo[k]["W_4"]["dims"]) for k in U).most_common(5)},
    "S3-U400_ell_route_true": sum(1 for k in U if clo[k].get("ell_route")),
    "ell_route_true_by_arm": {a: sum(1 for k in inst if arm_of[k] == a and clo[k].get("ell_route")) for a in ELL_ARMS},
    "ell_route_computed_by_arm": {a: sum(1 for k in inst if arm_of[k] == a and clo[k].get("ell_route") is not None) for a in ELL_ARMS},
    "S3-U400_M4_equals_unsubstituted_reference": ref_unsub_S3,
}
# power table
def ptail_ge(t, n, p):
    return 1 - binom_cdf_le(t - 1, n, p)


P = [Fraction(2, 100), Fraction(5, 100), Fraction(10, 100), Fraction(50, 100), Fraction(84, 100), Fraction(90, 100), Fraction(95, 100), Fraction(99, 100)]
pt = []
for p in P:
    pt.append({"p": float(p), "P(w>=360|N=400)": ptail_ge(360, 400, p), "P(w<=40|N=400)": binom_cdf_le(40, 400, p),
               "P(w<=200|N=400)": binom_cdf_le(200, 400, p), "P(c>=180|n=200)": ptail_ge(180, 200, p),
               "P(c<=20|n=200)": binom_cdf_le(20, 200, p)})
cpb = {f"{x}/{n}": [fnum(v, 8) for v in cp95(x, n)] for x, n in ((0, 200), (200, 200), (0, 400), (400, 400), (386, 386))}
out["power_table_recomputed"] = {"rows": [{k: (float(v) if isinstance(v, Fraction) else v) for k, v in r.items()} for r in pt],
                                 "rows_log10": [{k: (log10_frac(v) if isinstance(v, Fraction) else v) for k, v in r.items()} for r in pt],
                                 "cp95": cpb}
json.dump(strip(out), open(os.path.join(HERE, "recomputed.json"), "w"), indent=1, default=str)
print(json.dumps(strip({k: v for k, v in out.items() if k not in ("power_table_recomputed", "certificate_recount")}), indent=1, default=str)[:12000])
