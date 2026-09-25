"""Phase 7: aggregation, instrument checks, decision rules NC-DR-1..9,
cell-summary, raw-result, manifest and run report. Applies the frozen rules
mechanically; adds no threshold and drops no system."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import common
import stats
from common import FRESH_ARMS, ROOT, now, read_jsonl_gz, sha256_file, write_json

UNSAT_ARMS = ["S3-U62", "S3-C20", "NULL-AFF62", "NULL-F262", "NELL-A20",
              "N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"]
LADDER = ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144", "NULL-F262", "NULL-AFF62", "S_3 (82)"]
_CP = {}


def cp(x, n):
    if (x, n) not in _CP:
        _CP[(x, n)] = stats.cp95_json(x, n)
    return _CP[(x, n)]


def level(w, n):
    """NC-DR-1 thresholds."""
    if n < 120:
        return "NOT EVALUABLE (sample)"
    if w >= -(-9 * n // 10):
        return "TENSOR"
    if w <= n // 10:
        return "LINEAR"
    return "MIXED"


def level_nosample(w, n):
    if n == 0:
        return "NOT EVALUABLE (empty)"
    if w >= -(-9 * n // 10):
        return "TENSOR-level"
    if w <= n // 10:
        return "LINEAR-level"
    return "MIXED-level"


def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def phase7(R, args):
    t0 = time.time()
    R.log(7, "start")
    out = R.out
    from driver import all_systems
    systems = all_systems(R)
    skey = {s["key"]: s for s in systems}
    cl = {}
    for r in read_jsonl_gz(out / "closures.jsonl.gz"):
        cl[(r["key"], r["closure"])] = r
    certs = read_jsonl_gz(out / "certificates.jsonl.gz")
    cv = json.load(open(out / "certificate-verification.json"))
    cons = json.load(open(out / "construction-verification.json"))
    drp = json.load(open(out / "draw-replay-verification.json"))
    ncv = json.load(open(out / "negative-controls-verification.json"))
    det = json.load(open(out / "determinism.json"))
    eng = json.load(open(out / "engine-provenance" / "summary.json"))
    st = json.load(open(out / "selftest.json"))
    inp = json.load(open(out / "inputs.json"))
    p0 = R.load("p0")
    p1 = R.load("p1")
    p3 = R.load("p3")
    p4 = R.load("p4")
    ver = {c["cid"]: c for c in cv["certificates"]}

    # ---- per-system flags ---------------------------------------------------------
    per = {}
    for s in systems:
        k = s["key"]
        per[k] = {"m4_engine": cl[(k, "M_4")]["one"], "w4_engine": cl[(k, "W_4")]["one"],
                  "m4_verified": False, "w4_verified": False, "w4_flat_verified": False,
                  "wdag_submitted": False, "failed_certs": []}
    for c in certs:
        v = ver.get(c["cid"], {})
        p = per[c["key"]]
        if c["format"] == "wdag-v1":
            p["wdag_submitted"] = True
        if not v.get("verified"):
            p["failed_certs"].append(c["cid"])
            continue
        if c["closure"] == "M_4" and c["format"] == "flat-v1" and v.get("counts_for_M4"):
            p["m4_verified"] = True
        if c["closure"] == "W_4" and c["format"] == "wdag-v1":
            p["w4_verified"] = True
        if c["closure"] == "W_4" and c["format"] == "flat-v1":
            p["w4_flat_verified"] = True
    for k, p in per.items():
        p["w4_uncertified"] = p["w4_engine"] and not p["wdag_submitted"]
        p["m4_uncertified"] = p["m4_engine"] and not any(
            c["key"] == k and c["closure"] == "M_4" for c in certs)

    def arm_sys(arm, role="unsat"):
        if arm == "S_3 (82)":
            return [s for s in systems if s["arm"] in ("S3-U62", "S3-C20") and s["role"] == role]
        return [s for s in systems if s["arm"] == arm and s["role"] == role]

    # ---- instrument checks -----------------------------------------------------------
    ic = {}

    def put(cid, ok, detail, inv):
        ic[cid] = {"pass": bool(ok), "detail": detail, "invalidation_rule": inv}

    put("C-ENGINE", eng["pass"], {k: eng[k]["pass"] for k in ["a_tree_rule", "b_hashes", "c_replay_rc1",
                                                              "d_pytest", "e_build_info"]}, "INV-1")
    put("C-SRC", inp["pass"], [p for p, v in inp["files"].items() if not v["equal"]], "INV-2")
    put("C-SELF", st["C-SELF_pass"], {k: st[k]["pass"] for k in ["modulus_irreducible", "field_axioms",
                                                                 "E_S3_vs_direct", "exhaustive_s_vs_naive",
                                                                 "substitution_vs_direct",
                                                                 "engine_WD_vs_literal_small",
                                                                 "extractor_depth_ge2_extra"]}, "INV-3")
    put("C-FIX", st["C-FIX_pass"], st["C-FIX"]["dims"], "INV-3")
    put("C-CONSTRUCT", p1["checks"]["C-CONSTRUCT"]["pass"], p1["checks"]["C-CONSTRUCT"], "INV-3")
    put("C-SUPPORT", p1["checks"]["C-SUPPORT"]["pass"], p1["checks"]["C-SUPPORT"], "INV-3")
    put("C-REG", p1["checks"]["C-REG"]["pass"], p1["checks"]["C-REG"], "INV-4")
    ell_ok = p1["checks"]["C-ELL_S3"]["pass"] and p3["checks"]["C-ELL_fresh"]["pass"]
    put("C-ELL", ell_ok, {"S3": p1["checks"]["C-ELL_S3"], "fresh": p3["checks"]["C-ELL_fresh"]}, "INV-8")
    put("C-TOP", p4["checks"]["C-TOP"]["pass"], p4["checks"]["C-TOP"], "INV-8")
    put("C-T4", p4["checks"]["C-T4"]["pass"], p4["checks"]["C-T4"], "INV-8")
    put("C-WDAG", p4["checks"]["C-WDAG"]["pass"], p4["checks"]["C-WDAG"], "INV-8")
    put("C-ORACLE2", cons["V2"]["pass"], cons["V2"], "INV-7")
    put("C-DRAW", drp["pass"], {a: {"pass": v["pass"], "mismatches": v["mismatches"][:5]}
                                for a, v in drp["arms"].items()}, "INV-7")
    sat_ver = [c["cid"] for c in certs if skey[c["key"]]["role"] == "sat" and ver.get(c["cid"], {}).get("verified")]
    ps_ok = p4["checks"]["C-PS_engine"]["pass"] and not sat_ver
    put("C-PS", ps_ok, {"engine": p4["checks"]["C-PS_engine"], "verified_certificates_on_satisfiable": sat_ver},
        "INV-5 (and INV-7 if a satisfiable-control certificate verifies)")
    put("C-CERT", cv["n_failed"] == 0 and cv["n_submitted"] > 0,
        {"submitted": cv["n_submitted"], "verified": cv["n_verified"], "failed": cv["n_failed"]}, "INV-6")
    # C-VERIFIER: every corrupted certificate rejected; >= 3 per type per kind unless vacuous; V1 agreement
    short = []
    for kname, kp in p4["ncplan"].items():
        for typ, tv in kp["types"].items():
            if tv["built"] < 3 and not tv["vacuous"]:
                short.append(f"{kname} type {typ}: built {tv['built']}")
    ver_ok = ncv["pass"] and cons["pass_V1"] and not short
    put("C-VERIFIER", ver_ok, {"negative_controls": ncv["n"], "rejected": ncv["n_rejected"],
                               "accepted": ncv["accepted"], "source_not_verified": ncv["source_not_verified"],
                               "kinds": p4["ncplan"], "shortfalls": short, "V1_construction_agreement": cons["pass_V1"],
                               "V1_E_mismatch": cons["E_mismatch"][:10]}, "INV-6")
    put("C-DET", det["pass"], {"a": det["a_draw_logs"], "b": det["b_recompute"]["mismatches"][:10],
                               "c": det["c_threads1"]["mismatches"][:10]}, "INV-9")
    write_json(out / "instrument-checks.json", {"checks": ic, "all_pass": all(v["pass"] for v in ic.values())})
    void_run = any(not ic[c]["pass"] for c in ["C-ENGINE", "C-SRC", "C-SELF", "C-FIX", "C-CONSTRUCT",
                                                "C-SUPPORT", "C-REG", "C-ELL", "C-TOP", "C-T4", "C-WDAG",
                                                "C-PS", "C-DET"])
    counts_void = not ic["C-CERT"]["pass"] or not ic["C-VERIFIER"]["pass"]
    arm_void = not ic["C-ORACLE2"]["pass"] or not ic["C-DRAW"]["pass"]

    # ---- metrics ------------------------------------------------------------------------
    exhausted = {a: R.load(f"p2-{a}")["exhausted"] for a in FRESH_ARMS}
    arm_rows = {}
    for arm in UNSAT_ARMS + ["S_3 (82)"]:
        ss = arm_sys(arm)
        n = len(ss)
        w = sum(per[s["key"]]["w4_verified"] for s in ss)
        m = sum(per[s["key"]]["m4_verified"] for s in ss)
        unc = sum(per[s["key"]]["w4_uncertified"] for s in ss)
        w_eng = sum(per[s["key"]]["w4_engine"] for s in ss)
        m_eng = sum(per[s["key"]]["m4_engine"] for s in ss)
        notm = [s for s in ss if not per[s["key"]]["m4_engine"]]
        wc = sum(per[s["key"]]["w4_verified"] for s in notm)
        arm_rows[arm] = {"n": n, "W4_verified": w, "W4_engine": w_eng, "W4_uncertified": unc,
                         "W4_cp95": cp(w, n), "M4_verified": m, "M4_engine": m_eng, "M4_cp95": cp(m, n),
                         "W4_given_not_M4": {"x": wc, "n": len(notm), "cp95": cp(wc, len(notm))["cp95"]}}
        if arm == "NULL-AFF62":
            arm_rows[arm]["label"] = "one affine draw"
    sat_rows = {}
    for arm in ["S3-S62"] + FRESH_ARMS:
        ss = arm_sys(arm, "sat") if arm != "S3-S62" else [s for s in systems if s["arm"] == "S3-S62"]
        le31 = [s for s in ss if s["s"] <= 31]
        sat_rows[arm] = {"n": len(ss),
                         "M4_refuted_engine": sum(per[s["key"]]["m4_engine"] for s in ss),
                         "W4_refuted_engine": sum(per[s["key"]]["w4_engine"] for s in ss),
                         "certificates_verified": sum(1 for c in certs if c["key"] in {s["key"] for s in ss}
                                                      and ver.get(c["cid"], {}).get("verified")),
                         "s_le_31": len(le31),
                         "codim_ge_s": sum(1 for s in le31 if cl[(s["key"], "W_4")]["codim"] >= s["s"]),
                         "codim_eq_s": sum(1 for s in le31 if cl[(s["key"], "W_4")]["codim"] == s["s"])}
        sat_rows[arm]["codim_eq_s_fraction"] = (sat_rows[arm]["codim_eq_s"] / len(le31)) if le31 else None
    # certificates per (closure, arm, format)
    cert_tab = {}
    for c in certs:
        kk = f"{c['closure']}|{c['arm']}|{c['format']}"
        t = cert_tab.setdefault(kk, {"submitted": 0, "verified": 0, "failed": 0})
        t["submitted"] += 1
        t["verified" if ver.get(c["cid"], {}).get("verified") else "failed"] += 1
    unc_tab = {}
    for s in systems:
        p = per[s["key"]]
        if p["w4_uncertified"]:
            unc_tab.setdefault(f"W_4|{s['arm']}", []).append(s["key"])
        if p["m4_uncertified"]:
            unc_tab.setdefault(f"M_4|{s['arm']}", []).append(s["key"])
    # N-CONV stratified and paired table
    nconv = arm_sys("N-CONV")
    strat = {}
    for src in ["U62", "S62", "C20"]:
        ss = [s for s in nconv if s["source_set"] == src]
        w = sum(per[s["key"]]["w4_verified"] for s in ss)
        strat[src] = {"w": w, "n": len(ss), "cp95": cp(w, len(ss))["cp95"] if ss else None}
    s3_by_slot = {s["slot"]: s for s in systems if s["arm"] in ("S3-U62", "S3-C20")}
    pair = {"S3_ref_NCONV_ref": 0, "S3_ref_NCONV_not": 0, "S3_not_NCONV_ref": 0, "S3_not_NCONV_not": 0,
            "pairs": 0}
    for s in nconv:
        if s["slot"] in s3_by_slot:
            a = per[s3_by_slot[s["slot"]]["key"]]["w4_verified"]
            b = per[s["key"]]["w4_verified"]
            pair["pairs"] += 1
            pair[f"S3_{'ref' if a else 'not'}_NCONV_{'ref' if b else 'not'}"] += 1
    # semi-regular transfer per arm (NC-DR-5): unsat systems (verdict), sat and all reported
    semireg = {}
    for arm in ["S3-U62", "S3-C20", "S3-S62", "NULL-AFF62", "NULL-F262", "NELL-A20"] + FRESH_ARMS:
        res_ = {}
        for pop in ["unsat", "sat", "all"]:
            ss = [s for s in systems if s["arm"] == arm and (pop == "all" or s["role"] == pop)]
            if not ss:
                continue
            hit = 0
            t5 = 0
            nsub = 0
            for s in ss:
                rb = cl[(s["key"], "rc_b")]
                if rb["substituted"]:
                    nsub += 1
                    hit += cl[(s["key"], "R'_4")]["dims_by_deg"] == [0, 0, 16, 288, 2328]
                    t5 += bool(rb["T5_applicable"])
                elif rb["kernel_dim"] == 0:
                    hit += cl[(s["key"], "M_4")]["dims_by_deg"] == [0, 0, 17, 323, 2771]
            fr = hit / len(ss)
            res_[pop] = {"n": len(ss), "reference_profile": hit, "fraction": fr, "substituted": nsub,
                         "T5_applicable": t5, "T5_applicable_fraction": t5 / len(ss),
                         "label": ("SEMI-REGULAR TRANSFER HOLDS" if fr >= 0.9 else "FAILS" if fr <= 0.1 else "MIXED")}
        semireg[arm] = res_
    # draw statistics
    draw_stats = {}
    for arm in FRESH_ARMS:
        att = read_jsonl_gz(out / f"draws-{arm}.jsonl.gz")
        rej = {}
        s_draws = [a for a in att if a["s"] is not None]
        for a in att:
            if a["outcome"].startswith("rejected:"):
                rej[a["outcome"][9:]] = rej.get(a["outcome"][9:], 0) + 1
        per_slot = {}
        for a in att:
            per_slot[a["slot"]] = per_slot.get(a["slot"], 0) + 1
        draw_stats[arm] = {"attempts": len(att), "evaluated": len(s_draws),
                           "unsat_fraction_among_evaluated": (sum(1 for a in s_draws if a["s"] == 0) / len(s_draws)) if s_draws else None,
                           "rejections": rej, "attempts_per_slot_max": max(per_slot.values()),
                           "attempts_per_slot_mean": len(att) / len(per_slot),
                           "exhausted": exhausted[arm]}
    # fall profiles / P per arm (descriptive)
    prof = {}
    for arm in ["S3-U62", "S3-C20", "S3-S62", "NULL-AFF62", "NULL-F262", "NELL-A20"] + FRESH_ARMS:
        ss = [s for s in systems if s["arm"] == arm]
        Ps = [cl[(s["key"], "M_4")]["P"] for s in ss]
        fal = [cl[(s["key"], "M_4")]["fallen"] for s in ss]
        rk = [cl[(s["key"], "M_4")]["rank"] for s in ss]
        its = {}
        for s in ss:
            w = cl[(s["key"], "W_4")]
            kk = f"{w['iterations_to_fixpoint']}/{w['one_first_iteration']}"
            its[kk] = its.get(kk, 0) + 1
        prof[arm] = {"P": [min(Ps), max(Ps)], "fallen": [min(fal), max(fal)], "rank_M4": [min(rk), max(rk)],
                     "W4_iterations/one_first": its}

    # ---- decision rules ------------------------------------------------------------------
    dr = {}
    nC = len(nconv)
    w1 = arm_rows["N-CONV"]["W4_verified"]
    uncN = arm_rows["N-CONV"]["W4_uncertified"]
    L1 = {"w": w1, "n_C": nC, "cp95": cp(w1, nC)["cp95"], "label": level(w1, nC),
          "E_TENSOR_falsified": w1 <= nC // 2, "E_LINEAR_falsified": w1 > nC // 2}
    n2 = nC - uncN
    L2 = {"w": w1, "n_C": n2, "cp95": cp(w1, n2)["cp95"], "label": level(w1, n2),
          "E_TENSOR_falsified": w1 <= n2 // 2, "E_LINEAR_falsified": w1 > n2 // 2}
    if L1["label"] == L2["label"]:
        v1 = L1["label"]
    else:
        v1 = "UNDETERMINED (certification)"
    voided = void_run or counts_void or arm_void
    dr["NC-DR-1"] = {"L1_uncertified_as_not_refuted": L1, "L2_uncertified_excluded": L2,
                     "uncertified": uncN, "exhausted_unsat_slots": [e for e in exhausted["N-CONV"] if e["role"] == "unsat"],
                     "thresholds_at_n_C": {"tensor": -(-9 * nC // 10), "linear": nC // 10, "half": nC // 2},
                     "verdict": v1 if not voided else "VOID (instrument check failure; see NC-DR-8)"}
    ref386 = cp(386, 386)["cp95"]
    s3in = arm_rows["S_3 (82)"]["W4_cp95"]["cp95"]
    dr["NC-DR-2"] = {"N-CONV_cp95": L1["cp95"], "S3_386_cp95": ref386,
                     "label": "AT S_3's RATE" if overlap(L1["cp95"], ref386) else "BELOW S_3",
                     "in_run_S3_82": {"cp95": s3in, "label": "AT S_3's RATE" if overlap(L1["cp95"], s3in) else "BELOW S_3"}}
    lad = {}
    iv = {a: arm_rows[a]["W4_cp95"]["cp95"] for a in LADDER}
    for X in LADDER:
        for Y in LADDER:
            if X == Y:
                continue
            lab = "ABOVE" if iv[X][0] > iv[Y][1] else "NOT DISTINGUISHED"
            nm = lambda a: a + (" [one affine draw]" if a == "NULL-AFF62" else "")  # noqa: E731
            lad[f"{nm(X)} vs {nm(Y)}"] = f"{nm(X)} ABOVE {nm(Y)}" if lab == "ABOVE" else "NOT DISTINGUISHED"
    dr["NC-DR-3"] = {"intervals": {a: {"x": arm_rows[a]["W4_verified"], "n": arm_rows[a]["n"], "cp95": iv[a]}
                                   for a in LADDER}, "pairs": lad}
    above = lambda X, Y: iv[X][0] > iv[Y][1]  # noqa: E731
    nL = arm_rows["N-CONVL"]
    lv_L = level_nosample(nL["W4_verified"], nL["n"])
    n17 = arm_rows["N-CONV17"]
    lv_17 = level_nosample(n17["W4_verified"], n17["n"])
    if v1 == "TENSOR" and above("N-CONV", "N-ELL144") and above("N-CONV", "NULL-F262"):
        comp = "CONVOLUTION TENSOR"
        sub = None
    elif v1 == "LINEAR":
        comp = "LOWER-DEGREE PART REQUIRED"
        sub = {"TENSOR-level": "SEMAEV LINEAR PART SUFFICES (curve constant not required)",
               "LINEAR-level": "CURVE CONSTANT REQUIRED (with the confound that the drawn curves' targets are not x(2E))"}.get(lv_L, "MIXED")
    else:
        comp = "MIXED"
        sub = None
    if lv_17 == "TENSOR-level":
        app = "CONVOLUTION FORMS SUFFICE WITHOUT THE COKERNEL FALL"
    elif lv_17 == "LINEAR-level" and comp == "CONVOLUTION TENSOR":
        app = "THE RANK-16 COKERNEL IS NEEDED"
    else:
        app = f"descriptive: N-CONV17 {n17['W4_verified']}/{n17['n']} ({lv_17})"
    dr["NC-DR-4"] = {"NC-DR-1": v1, "N-CONV_above_N-ELL144": above("N-CONV", "N-ELL144"),
                     "N-CONV_above_NULL-F262": above("N-CONV", "NULL-F262"),
                     "N-CONVL_level": lv_L, "N-CONV17_level": lv_17,
                     "verdict": comp if not voided else "VOID (instrument check failure; see NC-DR-8)",
                     "sub_label": sub, "appended_N-CONV17_reading": app,
                     "rates": {a: f"{arm_rows[a]['W4_verified']}/{arm_rows[a]['n']}" for a in LADDER},
                     "note": ("rule (3) applied literally when NC-DR-1 is UNDETERMINED or NOT EVALUABLE"
                              if v1 not in ("TENSOR", "LINEAR", "MIXED") else None)}
    dr["NC-DR-5"] = {"per_arm": semireg, "population_for_label": "unsatisfiable systems of the arm (trial plan); satisfiable and all reported",
                     "note": "descriptive; no verdict on any heuristic"}
    m4 = arm_rows["N-CONV"]["M4_cp95"]
    dr["NC-DR-6"] = {"per_arm_M4": {a: {"x": arm_rows[a]["M4_verified"], "n": arm_rows[a]["n"],
                                        "cp95": arm_rows[a]["M4_cp95"]["cp95"]} for a in UNSAT_ARMS + ["S_3 (82)"]},
                     "N-CONV_label": "N-CONV M_4 AT STAGE-1 RATE" if overlap(m4["cp95"], [0.799, 0.875]) else "N-CONV M_4 NOT AT STAGE-1 RATE",
                     "stage1_interval": [0.799, 0.875],
                     "N-CONV_W4_given_M4_unrefuted": arm_rows["N-CONV"]["W4_given_not_M4"],
                     "note": "descriptive"}
    rec7 = {"CONVOLUTION TENSOR": "the n = 19 cell quotes S_3-specificity against an N-CONV-type arm (same-support nulls insufficient)",
            "LOWER-DEGREE PART REQUIRED": "N-ELL-type and same-support nulls carry the contrast, and an N-CONVL-type arm discriminates",
            "MIXED": "both arms"}
    dr["NC-DR-7"] = {"recommendation": rec7.get(dr["NC-DR-4"]["verdict"], "not evaluable (NC-DR-4 void)"),
                     "note": "recorded by the executor; decided by the Coordinator after review"}
    dr["NC-DR-8"] = {"checks": {k: v["pass"] for k, v in ic.items()}, "all_pass": all(v["pass"] for v in ic.values()),
                     "run_void": void_run, "counts_void_INV6": counts_void, "arm_metrics_void_INV7": arm_void}
    dr["NC-DR-9"] = {"primary": {"NC-DR-1": dr["NC-DR-1"]["verdict"], "NC-DR-4": dr["NC-DR-4"]["verdict"]},
                     "secondary": ["NC-DR-2", "NC-DR-3", "NC-DR-5", "NC-DR-6", "NC-DR-7"]}
    write_json(out / "decision-rules.json", dr)

    summary = {"MN1_w4_refuted_NCONV": {"w": w1, "n_C": nC, "cp95": L1["cp95"], "uncertified": uncN},
               "MN2_w4_refuted_by_arm": {a: {"x": v["W4_verified"], "n": v["n"], "cp95": v["W4_cp95"]["cp95"]}
                                         for a, v in arm_rows.items()},
               "MN3_soundness_and_certificates": {"satisfiable_controls": sat_rows, "certificates": cert_tab,
                                                  "uncertified": unc_tab},
               "secondary": {"arms": arm_rows, "N-CONV_by_source": strat, "paired_S3_vs_NCONV_W4": pair,
                             "semi_regular": semireg, "draw_statistics": draw_stats, "profiles": prof},
               "labels": {"measured": "every count and rate here is measured on this run; no number is modeled"}}
    write_json(out / "cell-summary.json", summary)
    raw = {"experiment_id": "EXP-CERTBIN-ddfe75", "run_id": args.run_id,
           "MN1": summary["MN1_w4_refuted_NCONV"], "MN2": summary["MN2_w4_refuted_by_arm"],
           "MN3": summary["MN3_soundness_and_certificates"],
           "per_system": [{"key": s["key"], "arm": s["arm"], "role": s["role"], "slot": s["slot"], "s": s["s"],
                           "source_set": s["source_set"], "idx": s["idx"], "x_R": s["x_R"],
                           "M4_engine": per[s["key"]]["m4_engine"], "M4_verified": per[s["key"]]["m4_verified"],
                           "W4_engine": per[s["key"]]["w4_engine"], "W4_verified": per[s["key"]]["w4_verified"],
                           "W4_uncertified": per[s["key"]]["w4_uncertified"],
                           "P": cl[(s["key"], "M_4")]["P"], "fallen": cl[(s["key"], "M_4")]["fallen"],
                           "W4_final_dim": cl[(s["key"], "W_4")]["final_dim"],
                           "W4_one_first_iteration": cl[(s["key"], "W_4")]["one_first_iteration"],
                           "rc_b_label": cl[(s["key"], "rc_b")]["label"]} for s in systems],
           "decision_rules": {k: dr[k].get("verdict", dr[k].get("label")) for k in dr}}
    write_json(out / "raw-result.json", raw)
    # raw vs summary agreement (MN1-MN3)
    agree = {}
    for arm in UNSAT_ARMS:
        x = sum(1 for r in raw["per_system"] if r["arm"] == arm and r["role"] == "unsat" and r["W4_verified"])
        agree[arm] = x == summary["MN2_w4_refuted_by_arm"][arm]["x"]
    agree["MN1"] = sum(1 for r in raw["per_system"] if r["arm"] == "N-CONV" and r["role"] == "unsat"
                       and r["W4_verified"]) == summary["MN1_w4_refuted_NCONV"]["w"]
    for a in sat_rows:
        pool = [r for r in raw["per_system"] if r["arm"] == a and r["role"] == "sat"]
        agree[f"MN3_{a}_sat_M4"] = sum(r["M4_engine"] for r in pool) == sat_rows[a]["M4_refuted_engine"]
        agree[f"MN3_{a}_sat_W4"] = sum(r["W4_engine"] for r in pool) == sat_rows[a]["W4_refuted_engine"]
    agree["MN3_certificates"] = sum(v["submitted"] for v in cert_tab.values()) == cv["n_submitted"] and \
        sum(v["verified"] for v in cert_tab.values()) == cv["n_verified"]
    validity = "completed_valid" if not (void_run or counts_void or arm_void) else "invalid_measurement"
    R.log(7, "aggregated", validity=validity, raw_summary_agree=all(agree.values()))
    import report
    report.write_all(R, args, dict(systems=systems, per=per, arm_rows=arm_rows, sat_rows=sat_rows, dr=dr, ic=ic,
                                   cert_tab=cert_tab, unc_tab=unc_tab, validity=validity, agree=agree,
                                   p0=p0, eng=eng, st=st, inp=inp, cv=cv, ncv=ncv, det=det, drp=drp, cons=cons,
                                   semireg=semireg, strat=strat, pair=pair, draw_stats=draw_stats, prof=prof,
                                   t0=t0))
    R.log(7, "end", seconds=round(time.time() - t0, 1))
    R.mark("p7")
