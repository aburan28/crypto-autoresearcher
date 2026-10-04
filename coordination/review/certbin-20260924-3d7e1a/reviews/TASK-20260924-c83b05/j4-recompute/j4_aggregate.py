#!/usr/bin/env python3
"""J4: validator-owned aggregation of RUN-CERTBIN-c417e0, TASK-20260924-c83b05.

Written from EXP-CERTBIN-e94b27/specification.yaml (metrics, decision_rules,
secondary) and H-CERTBIN-5e71c9 (PA-1..PA-3) only. Imports nothing from
impl/ (in particular NOT analysis.py or stats_exact.py) and does not read
decision-rules.json, cell-summary.json, raw-result.json or run-report.md: the
comparison with the recorded values is a separate step (j4_compare.py).

Inputs (the three per-instance record files named by the review plan, plus
instance-sets.json for set membership and the Stage-1 targets for the 324/386
inheritance check):
  closures.jsonl.gz, certificates.jsonl.gz, certificate-verification.json.

ORDERING RECORD (RV-4): the sha256 of j2-constructions/J2-section.yaml is
read and embedded in the output; that file existed and was sealed before this
script was written.

Clopper-Pearson 95% (two-sided, 0.025 per tail) in exact rational arithmetic
(fractions.Fraction, math.comb): each bound is bracketed by bisection to width
< 2^-100 on the exact binomial tail; for x = n (lower) and x = 0 (upper) the
closed forms 0.025^(1/n) and 1 - 0.025^(1/n) are also given at 40 digits.
"""
import gzip
import hashlib
import json
import os
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from math import comb

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0")
SRC = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
J2 = os.path.join(HERE, "..", "j2-constructions", "J2-section.yaml")
A = Fraction(1, 40)
getcontext().prec = 60


# ---------------------------------------------------------------------------
def tail_ge(x, n, p):          # P(X >= x)
    q = 1 - p
    return sum(comb(n, i) * p ** i * q ** (n - i) for i in range(x, n + 1))


def tail_le(x, n, p):          # P(X <= x)
    q = 1 - p
    return sum(comb(n, i) * p ** i * q ** (n - i) for i in range(0, x + 1))


def bisect(g, lo=Fraction(0), hi=Fraction(1), bits=100):
    """g increasing; returns [lo, hi] with g(lo) < 0 <= g(hi)."""
    for _ in range(bits):
        mid = (lo + hi) / 2
        if g(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


def dec(fr, d=25):
    return format(Decimal(fr.numerator) / Decimal(fr.denominator), f".{d}g")


def cp95(x, n):
    if n == 0:
        return {"x": x, "n": n, "defined": False, "note": "n = 0: no interval (closure not run)"}
    if x == 0:
        lo = (Fraction(0), Fraction(0))
    else:
        lo = bisect(lambda p: tail_ge(x, n, p) - A)             # P(X >= x) increasing in p
    if x == n:
        hi = (Fraction(1), Fraction(1))
    else:
        hi = bisect(lambda p: A - tail_le(x, n, p))             # P(X <= x) decreasing in p
    out = {"x": x, "n": n, "defined": True, "rate": dec(Fraction(x, n), 15),
           "lower_bracket": [dec(lo[0]), dec(lo[1])], "upper_bracket": [dec(hi[0]), dec(hi[1])],
           "_lo": lo, "_hi": hi}
    if x == n:
        out["lower_closed_form_0.025^(1/n)"] = format(Decimal("0.025") ** (Decimal(1) / Decimal(n)), ".40g")
    if x == 0:
        out["upper_closed_form_1-0.025^(1/n)"] = format(1 - Decimal("0.025") ** (Decimal(1) / Decimal(n)), ".40g")
    return out


def pub(c):
    return {k: v for k, v in c.items() if not k.startswith("_")}


def separated(cu, cn):
    """U lower bound strictly above null upper bound, conservatively (U lower
    bracket's low end vs null upper bracket's high end)."""
    if not (cu["defined"] and cn["defined"]):
        return None
    return cu["_lo"][0] > cn["_hi"][1]


# ---------------------------------------------------------------------------
def main():
    j2sha = hashlib.sha256(open(J2, "rb").read()).hexdigest()
    inst = json.load(open(os.path.join(RUN, "instance-sets.json")))
    sets = {s: sorted(v, key=lambda x: x["idx"]) for s, v in inst["sets"].items()}
    set_of = {x["key"]: s for s, v in sets.items() for x in v}
    idx_of = {x["key"]: x["idx"] for v in sets.values() for x in v}
    rec = {}
    for line in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt"):
        r = json.loads(line)
        rec[(r["key"], r["closure"])] = r
    cert = {}
    for line in gzip.open(os.path.join(RUN, "certificates.jsonl.gz"), "rt"):
        c = json.loads(line)
        cert[(c["key"], c["closure"])] = c
    ver = json.load(open(os.path.join(RUN, "certificate-verification.json")))
    verified = {(v["key"], v["closure"]) for v in ver["certificates"] if v["verified"]}
    failed = {(v["key"], v["closure"]) for v in ver["certificates"] if not v["verified"]}

    def status(key, cl):
        """per (instance, closure): not_run | UNDETERMINED(budget) | not_refuted |
        UNCERTIFIED | certificate_failed | verified. A refutation counts only if a
        certificate for exactly this (key, closure) is VERIFIED."""
        r = rec.get((key, cl))
        if r is None:
            return "not_run"
        if r.get("label") == "UNDETERMINED(budget)":
            return "UNDETERMINED(budget)"
        has_v = (key, cl) in verified and (key, cl) in cert
        if not r.get("one"):
            return "verified_but_engine_says_not_refuted" if has_v else "not_refuted"
        if (key, cl) not in cert:
            return "UNCERTIFIED"
        if (key, cl) in failed:
            return "certificate_failed"
        return "verified" if has_v else "UNCERTIFIED"

    CL = ("W_4", "M_5", "W_5")
    st = {(x["key"], c): status(x["key"], c) for v in sets.values() for x in v for c in CL}
    anomalies = [k for k, v in st.items() if v == "verified_but_engine_says_not_refuted"]
    U = [x["key"] for x in sets["U62"]]
    # ---- MR1, MR2
    a = sum(st[(k, "W_4")] == "verified" for k in U)
    b = sum(st[(k, "M_5")] == "verified" for k in U)
    # certificate-only cross-count (spec wording: "a VERIFIED certificate for 1 in X")
    a_cert = sum(((k, "W_4") in verified) for k in U)
    b_cert = sum(((k, "M_5") in verified) for k in U)
    # ---- MR3 labels
    labels = {}
    for k in U:
        w4, m5, w5 = st[(k, "W_4")], st[(k, "M_5")], st[(k, "W_5")]
        if w4 == "verified":
            lab = "W4 (and M5)" if m5 == "verified" else "W4 (not M5)"
        elif m5 == "verified":
            lab = "M5-only"
        elif w5 == "verified":
            lab = "W5-only"
        elif w5 == "UNDETERMINED(budget)":
            lab = "UNDETERMINED(budget)"
        elif "UNCERTIFIED" in (w4, m5, w5) or "certificate_failed" in (w4, m5, w5):
            lab = "UNCERTIFIED"
        else:
            lab = "none"
        labels[k] = lab
    lab_counts = {}
    for v in labels.values():
        lab_counts[v] = lab_counts.get(v, 0) + 1
    r = sum(1 for v in labels.values() if v.startswith("W4") or v in ("M5-only", "W5-only"))
    ci = {"a": cp95(a, 62), "b": cp95(b, 62), "r": cp95(r, 62)}
    # ---- MR4
    mr4 = {}
    for s in ("N-AFF62", "N-F262"):
        mr4[s] = {}
        for c in CL:
            ran = [x["key"] for x in sets[s] if st[(x["key"], c)] != "not_run"]
            xv = sum(st[(k, c)] == "verified" for k in ran)
            mr4[s][c] = {"verified_refuted": xv, "ran_on": len(ran), "set_size": len(sets[s]),
                         "undetermined": sum(st[(k, c)] == "UNDETERMINED(budget)" for k in ran),
                         "CP95": cp95(xv, len(ran))}
    # ---- MR5
    s62 = {c: {"refuted_reported": sum(1 for x in sets["S62"] if rec.get((x["key"], c), {}).get("one")),
               "checked": sum(1 for x in sets["S62"] if (x["key"], c) in rec)} for c in CL}
    per_sc = {}
    for s in sets:
        for c in CL:
            ran = [x["key"] for x in sets[s] if (x["key"], c) in rec]
            if not ran:
                continue
            rep = [k for k in ran if rec[(k, c)].get("one")]
            sub = [k for k in ran if (k, c) in cert]
            per_sc[f"{c}/{s}"] = {"ran_on": len(ran), "reported_refutations": len(rep), "submitted": len(sub),
                                  "verified": sum((k, c) in verified for k in sub),
                                  "failed": sum((k, c) in failed for k in sub),
                                  "uncertified": sum(1 for k in rep if (k, c) not in cert)}
    tot = {"submitted": len(ver["certificates"]), "verified": len(verified), "failed": len(failed),
           "uncertified": sum(v["uncertified"] for v in per_sc.values()),
           "certificate_lines": len(cert)}
    # ---- secondary: 2 x 2
    def two(s):
        t = {"W4+M5+": 0, "W4+M5-": 0, "W4-M5+": 0, "W4-M5-": 0}
        for x in sets[s]:
            w = st[(x["key"], "W_4")] == "verified"
            m = st[(x["key"], "M_5")] == "verified"
            t[f"W4{'+' if w else '-'}M5{'+' if m else '-'}"] += 1
        return t
    tables = {s: two(s) for s in ("U62", "N-AFF62", "N-F262")}
    # ---- secondary: inheritance of 324 / 386 from Stage-1 (own read of the targets)
    s3 = {}
    for line in gzip.open(os.path.join(SRC, "targets-F-S3.jsonl.gz"), "rt"):
        t = json.loads(line)
        s3.setdefault(t["idx"], {})[t["D"]] = t
    unsat = [i for i in s3 if s3[i][4]["stratum"] == "unsat"]
    inherit = {"stage1_unsat_arm_D4": len(unsat),
               "stage1_unsat_one_in_R_4_true": sum(1 for i in unsat if s3[i][4]["one_in_R"] is True),
               "stage1_unsat_one_in_R_4_false": sum(1 for i in unsat if s3[i][4]["one_in_R"] is False),
               "stage1_unsat_one_in_R_3_true": sum(1 for i in unsat if s3[i][3]["one_in_R"] is True),
               "stage1_unsat_D3_true_but_D4_false": sum(1 for i in unsat if s3[i][3]["one_in_R"] is True and s3[i][4]["one_in_R"] is False),
               "U62_equals_unsat_with_one_in_R_4_false": sorted(idx_of[k] for k in U) == sorted(i for i in unsat if s3[i][4]["one_in_R"] is False),
               "C20_is_subset_of_the_324": all(s3[x["idx"]][4]["one_in_R"] is True and s3[x["idx"]][4]["stratum"] == "unsat" for x in sets["C20"]),
               "C20_W4_verified": sum(st[(x["key"], "W_4")] == "verified" for x in sets["C20"]),
               "C20_W4_first_iteration": sorted(set(rec[(x["key"], "W_4")]["one_first_iteration"] for x in sets["C20"]))}
    n324 = inherit["stage1_unsat_one_in_R_4_true"]
    n386 = inherit["stage1_unsat_arm_D4"]
    dstar = {"4 (1 in R_4, inherited)": n324, "5 (b)": b, ">5 (62 - b)": 62 - b}
    comb_rates = {"W_4": {"num": n324 + a, "den": n386, "rate": dec(Fraction(n324 + a, n386), 15)},
                  "any_closure_D_le_5": {"num": n324 + r, "den": n386, "rate": dec(Fraction(n324 + r, n386), 15)},
                  "inherited_via_monotonicity_only": n324, "measured_in_this_run": 62, "spot_check": "C20 (20 of the 324)"}
    # ---- secondary: certificate sizes from certificates.jsonl.gz (own count)
    sizes = {}
    for (k, c), cc in cert.items():
        z = sizes.setdefault(c, {"count": 0, "sizes": [], "maxdeg": {}})
        z["count"] += 1
        z["sizes"].append(len(cc["C"]))
        md = max(len(p[0]) for p in cc["C"])
        z["maxdeg"][str(md)] = z["maxdeg"].get(str(md), 0) + 1
        if len(cc["C"]) != cc["size"] or md != cc["max_deg_mu"]:
            z.setdefault("inconsistent", []).append(k)
    for c, z in sizes.items():
        s_ = sorted(z.pop("sizes"))
        n = len(s_)
        z.update({"min": s_[0], "max": s_[-1], "median": (s_[n // 2] if n % 2 else (s_[n // 2 - 1] + s_[n // 2]) / 2)})
    # ---- secondary: W_4 first iteration on U62, ell
    first_it = {}
    for k in U:
        v = str(rec[(k, "W_4")]["one_first_iteration"])
        first_it[v] = first_it.get(v, 0) + 1
    ell = sum(1 for k in U if rec[(k, "W_4")].get("ell_in_W4_le1"))
    # ---- decision rules (literal)
    drs = {}
    drs["RC1-DR-1"] = {"a": a, "verdict": ("ARTIFACT (predominant)" if a >= 56 else
                                           "GENUINE D*_W > 4 (predominant)" if a <= 6 else "MIXED"),
                       "CP95": pub(ci["a"]), "E-A_falsified": a <= 31, "E-G_falsified": a >= 32}
    undet = [k for k in U if labels[k] in ("UNDETERMINED(budget)", "UNCERTIFIED")]
    notref_L1 = [k for k in U if labels[k] in ("none", "UNDETERMINED(budget)", "UNCERTIFIED")]
    notref_L2 = [k for k in U if labels[k] == "none"]

    def lab(nn):
        return "CLEAN" if nn == 0 else ("NEAR-CLEAN" if nn <= 3 else "RESIDUE")
    L1, L2 = lab(len(notref_L1)), lab(len(notref_L2))
    drs["RC1-DR-2"] = {"L1": L1, "L1_denominator": 62, "L1_not_refuted": len(notref_L1),
                       "L2": L2, "L2_denominator": 62 - len(undet), "L2_not_refuted": len(notref_L2),
                       "verdict": L1 if L1 == L2 else "UNDETERMINED (budget or certification)",
                       "residue_idx": sorted(idx_of[k] for k in notref_L1)}
    drs["RC1-DR-3"] = {"b": b, "two_by_two_U62": tables["U62"], "verdict": "M_5 SUFFICES" if b == 62 else f"M_5 refutes {b} of 62"}
    dr4 = {}
    for X, key in (("W_4", "a"), ("M_5", "b")):
        seps = {s: separated(ci[key], mr4[s][X]["CP95"]) for s in ("N-AFF62", "N-F262")}
        dr4[X] = {"U62_CP95_lower_bracket": ci[key]["lower_bracket"],
                  "null_CP95_upper_brackets": {s: mr4[s][X]["CP95"].get("upper_bracket") for s in seps},
                  "separated": seps,
                  "verdict": f"S_3-SPECIFIC at {X}" if all(v is True for v in seps.values()) else f"NOT DISTINGUISHED at {X}"}
    drs["RC1-DR-4"] = dr4
    drs["RC1-DR-4_note"] = "Only W_4 and M_5 enter DR-4; the W_5 null intervals (n = 0) are undefined and are consumed by no rule."
    # DR-5 from the validator's own J3 control checks (not from instrument-checks.json)
    j3 = json.load(open(os.path.join(HERE, "..", "j3-checks", "controls_results.json")))
    neg = json.load(open(os.path.join(HERE, "..", "j3-checks", "neg_extended_results.json")))
    k6 = j3["K6_C_CERT_C_PS1_consistency"]
    own_controls = {
        "C-PS1": s62["W_4"]["refuted_reported"] == 0 and s62["M_5"]["refuted_reported"] == 0 and s62["W_5"]["refuted_reported"] == 0
                 and s62["W_4"]["checked"] == 62 and s62["M_5"]["checked"] == 62 and s62["W_5"]["checked"] == 10,
        "C-CERT": tot["failed"] == 0 and tot["submitted"] == tot["certificate_lines"] and not k6["reported_without_certificate"],
        "C-MONO": (inherit["C20_W4_verified"] == 20 and not j3["K5_C_MONO"]["own_dimension_monotonicity_checks"]["violations"]),
        "C-BASE": not j3["K2_oracle_base_inputs"]["p1_checkpoint_disagrees_with_stage1"],
        "C-VERIFIER": (j3["K3_E_construction_third_route"]["verifier_agree_flags_all_true"]
                       and not j3["K3_E_construction_third_route"]["own_curve_E_equals_instance_sets_E_hex"]["disagree"]
                       and neg["all_corruptions_rejected_by_sum_test"] and neg["all_bases_accepted"]),
        "C-DET": (not j3["K4_C_DET"]["recomputed_vs_closures_jsonl_mismatch"] and j3["K4_C_DET"]["pid_distinct_from_main"]),
    }
    drs["RC1-DR-5"] = {"own_control_readings": own_controls, "verdict": "PASS" if all(own_controls.values()) else "FAIL"}
    drs["RC1-DR-6"] = {"RC1-DR-2_verdict": drs["RC1-DR-2"]["verdict"],
                       "clean_or_near_clean": drs["RC1-DR-2"]["verdict"] in ("CLEAN", "NEAR-CLEAN"),
                       "note": "recorded, not decided (Coordinator decides NA-5)"}
    drs["RC1-DR-7"] = {"primary": {"RC1-DR-1": drs["RC1-DR-1"]["verdict"], "RC1-DR-2": drs["RC1-DR-2"]["verdict"]}}
    # ---- PA-1..PA-3 (H-CERTBIN-5e71c9)
    pa = {"PA-1": {"a": a, "E-A_threshold_a>=56": a >= 56, "E-G_threshold_a<=6": a <= 6,
                   "E-A_falsified_a<=31": a <= 31, "E-G_falsified_a>=32": a >= 32},
          "PA-2": {"r": r, "label": "CLEAN" if r == 62 else ("NEAR-CLEAN" if 59 <= r <= 61 else "RESIDUE")},
          "PA-3": {"refuted_satisfiable_controls": sum(v["refuted_reported"] for v in s62.values()),
                   "held": sum(v["refuted_reported"] for v in s62.values()) == 0}}
    # ---- pre-data coordinator prior (a)-(d) (specification coordinator_prior)
    w4null = [mr4[s]["W_4"]["verified_refuted"] for s in ("N-AFF62", "N-F262")]
    prior = {
        "(a) modal a in [15, 50] (MIXED)": {"a": a, "in_modal_range": 15 <= a <= 50, "DR-1": drs["RC1-DR-1"]["verdict"]},
        "(b) b >= 56 and DR-2 CLEAN or NEAR-CLEAN": {"b": b, "b>=56": b >= 56, "DR-2": drs["RC1-DR-2"]["verdict"],
                                                     "consistent": b >= 56 and drs["RC1-DR-2"]["verdict"] in ("CLEAN", "NEAR-CLEAN")},
        "(c) NOT DISTINGUISHED at M_5; nulls near 0 at W_4; if a >= 10 then S_3-SPECIFIC at W_4": {
            "DR-4_M_5": dr4["M_5"]["verdict"], "null_W4_verified": w4null, "DR-4_W_4": dr4["W_4"]["verdict"],
            "consistent": dr4["M_5"]["verdict"] == "NOT DISTINGUISHED at M_5" and max(w4null) <= 3
                          and (a < 10 or dr4["W_4"]["verdict"] == "S_3-SPECIFIC at W_4"),
            "operationalization_note": "the prior gives no number for 'near 0'; the validator reads it as <= 3 of 62 per null set and reports the counts so any other reading can be applied"},
        "(d) every W_4 / M_5 refutation certifies": {"failed": tot["failed"], "uncertified": tot["uncertified"],
                                                     "consistent": tot["failed"] == 0 and tot["uncertified"] == 0}}
    out = {"task_id": "TASK-20260924-c83b05", "joint": "J4",
           "ordering_record": {"J2_section_sha256_read_at_aggregation": j2sha,
                               "note": "J2-section.yaml was written and sealed before this script existed (RV-4)"},
           "inputs": ["closures.jsonl.gz", "certificates.jsonl.gz", "certificate-verification.json",
                      "instance-sets.json (set membership)", "Stage-1 targets-F-S3.jsonl.gz (324/386)",
                      "j3-checks/controls_results.json and neg_extended_results.json (own DR-5 readings)"],
           "status_anomalies_verified_certificate_but_engine_not_refuted": anomalies,
           "MR1": {"a": a, "a_certificate_only_count": a_cert, "n": 62, "CP95": pub(ci["a"])},
           "MR2": {"b": b, "b_certificate_only_count": b_cert, "n": 62, "CP95": pub(ci["b"])},
           "MR3": {"r": r, "n": 62, "CP95": pub(ci["r"]), "label_counts": lab_counts},
           "MR4": {s: {c: {**{k: v for k, v in d.items() if k != "CP95"}, "CP95": pub(d["CP95"])} for c, d in m.items()} for s, m in mr4.items()},
           "MR5": {"C-PS1": s62, "certificates_per_closure_set": per_sc, "totals": tot},
           "secondary": {"two_by_two": tables, "D_star_extension": dstar, "combined_unsat_arm_rates": comb_rates,
                         "inheritance_check": inherit, "certificate_sizes": sizes,
                         "U62_W4_first_iteration_of_1": first_it, "U62_ell_in_W4_le1": ell},
           "decision_rules": drs, "PA": pa, "pre_data_prior": prior}
    json.dump(out, open(os.path.join(HERE, "recomputed.json"), "w"), indent=1)
    print(json.dumps({"j2sha": j2sha, "MR1": out["MR1"], "MR2": out["MR2"]["b"], "MR3": out["MR3"]["r"],
                      "labels": lab_counts, "DR": {k: v.get("verdict") for k, v in drs.items() if isinstance(v, dict)},
                      "MR4": {s: {c: (d["verified_refuted"], d["ran_on"]) for c, d in m.items()} for s, m in mr4.items()},
                      "anomalies": anomalies}, indent=1))


if __name__ == "__main__":
    main()
