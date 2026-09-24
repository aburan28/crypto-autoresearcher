"""Phase 7 of EXP-CERTBIN-e94b27: instrument checks, MR1-MR5, secondary
metrics, RC1-DR-1..7 (mechanical), raw-result recomputation, manifest,
environment and run report. Observations only; no hypothesis verdict."""
import gzip
import json
import os
import platform
import resource
import statistics
import sys
import time
from fractions import Fraction

import numpy as np
import yaml

from common import (REPO, SPEC, EXP_ID, TASK_ID, SRC_RUN, MEM_LIMIT, W5_WATCHDOG, RUN_WATCHDOG, INPUT_FILES,
                    dump_json, load_json_gz, now, sha256_file, S_SELFTEST)
from instances import SET_ORDER
from stats_exact import clopper_pearson, public, separated

NULLS = ["N-AFF62", "N-F262"]
CLOSURES = {"W_4": ["U62", "S62", "C20", "N-AFF62", "N-F262"], "M_5": ["U62", "S62", "N-AFF62", "N-F262"],
            "W_5": ["U62", "S62", "N-AFF62", "N-F262"]}


def _status(rec, verified):
    """per (instance, closure) status."""
    if rec is None:
        return "not_run"
    if rec.get("label") == "UNDETERMINED(budget)":
        return "UNDETERMINED(budget)"
    if not rec.get("one"):
        return "not_refuted"
    if rec.get("certificate") != "emitted":
        return "UNCERTIFIED"
    return "verified" if verified else "certificate_failed"


def load_all(run):
    ck = run.ck
    d = {"p1": load_json_gz(os.path.join(ck, "p1-sets-oracles-base.json.gz"))}
    for c, sl in CLOSURES.items():
        for s in sl:
            d[(c, s)] = load_json_gz(os.path.join(ck, f"p-{c}-{s}.json.gz"))
    d["det"] = load_json_gz(os.path.join(ck, "p5-determinism.json.gz"))
    d["ver"] = json.load(open(os.path.join(run.out, "certificate-verification.json")))
    d["selftest"] = json.load(open(os.path.join(run.out, "selftest.json")))
    d["inputs"] = json.load(open(os.path.join(run.out, "inputs.json")))
    d["csrc_driver"] = json.load(open(os.path.join(ck, "c-src-driver.json")))
    d["timings"] = json.load(open(os.path.join(ck, "timings-phases-1-4.json")))
    d["w5sel"] = json.load(open(os.path.join(ck, "w5-selection.json")))
    return d


def status_table(d, sets):
    vmap = {(r["key"], r["closure"]): r["verified"] for r in d["ver"]["certificates"]}
    st = {}
    for c, sl in CLOSURES.items():
        for s in sl:
            recs = d[(c, s)]["records"]
            for inst in sets[s]:
                k = inst["key"]
                st[(k, c)] = _status(recs.get(k), vmap.get((k, c), False))
    return st, vmap


def cert_counts(d, sets):
    """MR5 certificate counts per set and closure."""
    vmap = {(r["key"], r["closure"]): r for r in d["ver"]["certificates"]}
    out = {}
    for c, sl in CLOSURES.items():
        for s in sl:
            recs = d[(c, s)]["records"]
            sub = [cc for cc in d[(c, s)]["certificates"]]
            ver = sum(1 for cc in sub if vmap.get((cc["key"], c), {}).get("verified"))
            unc = sum(1 for r in recs.values() if r.get("one") and r.get("certificate") != "emitted")
            out[f"{c}/{s}"] = {"reported_refutations": sum(1 for r in recs.values() if r.get("one")),
                               "submitted": len(sub), "verified": ver, "failed": len(sub) - ver,
                               "uncertified": unc}
    return out


def instrument_checks(d, sets, st, neg):
    p1 = d["p1"]["records"]
    ch = {}
    ch["C-SRC"] = {"pass": bool(d["inputs"]["pass"] and d["csrc_driver"]["pass"]),
                   "violating": [r["path"] for r in d["inputs"]["inputs"] if not r["match"]],
                   "specification_byte_identical": d["inputs"]["specification"]["byte_identical"]}
    ch["C-SELF"] = {"pass": bool(d["selftest"]["C-SELF"]["pass"]),
                    "violating": [k for k, v in d["selftest"]["C-SELF"]["items"].items() if not v["pass"]]}
    ch["C-FIX"] = {"pass": bool(d["selftest"]["C-FIX"]["pass"]), "dimensions": d["selftest"]["C-FIX"]["dimensions"],
                   "violating": [] if d["selftest"]["C-FIX"]["pass"] else ["dimension mismatch"]}
    ch["C-BASE"] = {"pass": all(r["base_agree_archive"] for r in p1.values()),
                    "instances_checked": len(p1),
                    "violating": [k for k, r in p1.items() if not r["base_agree_archive"]]}
    ch["C-ORACLE"] = {"pass": all(r["oracle_agree_archive"] for r in p1.values()),
                      "instances_checked": len(p1),
                      "oracle_A_instances": sum(1 for r in p1.values() if "s_A" in r),
                      "violating": [k for k, r in p1.items() if not r["oracle_agree_archive"]]}
    # C-MONO
    viol = []
    w4 = {s: d[("W_4", s)]["records"] for s in CLOSURES["W_4"]}
    for inst in sets["C20"]:
        if not w4["C20"][inst["key"]].get("one"):
            viol.append({"key": inst["key"], "rule": "C20: 1 in W_4 required (M_4 subset W_4)"})
    for s in SET_ORDER:
        for inst in sets[s]:
            k = inst["key"]
            m4 = p1[k]["M_4"]["one"]
            rw4 = w4[s].get(k) if s in w4 else None
            rm5 = d[("M_5", s)]["records"].get(k) if s in CLOSURES["M_5"] else None
            rw5 = d[("W_5", s)]["records"].get(k) if s in CLOSURES["W_5"] else None
            if rw4 is not None:
                if m4 and not rw4.get("one"):
                    viol.append({"key": k, "rule": "M_4 refutes but W_4 does not"})
                if rw4["final_dim"] < p1[k]["M_4"]["rank"]:
                    viol.append({"key": k, "rule": "dim W_4 < rank M_4"})
            if rw5 is not None and rw5.get("label") != "UNDETERMINED(budget)":
                if rw4 is not None and rw4.get("one") and not rw5.get("one"):
                    viol.append({"key": k, "rule": "W_4 refutes but W_5 does not"})
                if rm5 is not None and rm5.get("one") and not rw5.get("one"):
                    viol.append({"key": k, "rule": "M_5 refutes but W_5 does not"})
                if m4 and not rw5.get("one"):
                    viol.append({"key": k, "rule": "M_4 refutes but W_5 does not"})
    ch["C-MONO"] = {"pass": not viol, "violating": viol,
                    "C20_W4_refuted": sum(1 for i in sets["C20"] if w4["C20"][i["key"]].get("one"))}
    # C-PS1
    ps1 = []
    for c in ("W_4", "M_5", "W_5"):
        for k, r in d[(c, "S62")]["records"].items():
            if r.get("one"):
                ps1.append({"key": k, "closure": c, "certificate_status": st.get((k, c))})
    ch["C-PS1"] = {"pass": not ps1, "violating": ps1,
                   "checked": {"W_4": len(d[("W_4", "S62")]["records"]), "M_5": len(d[("M_5", "S62")]["records"]),
                               "W_5": len(d[("W_5", "S62")]["records"])}}
    # C-CERT
    failed = [{"key": r["key"], "closure": r["closure"], "reason": r["reason"]}
              for r in d["ver"]["certificates"] if not r["verified"]]
    unc = [{"key": k, "closure": c} for (k, c), v in st.items() if v == "UNCERTIFIED"]
    submitted_expected = sum(len(d[(c, s)]["certificates"]) for c, sl in CLOSURES.items() for s in sl)
    ch["C-CERT"] = {"pass": (not failed) and d["ver"]["submitted"] == submitted_expected,
                    "submitted": d["ver"]["submitted"], "submitted_expected": submitted_expected,
                    "verified": d["ver"]["verified"], "failed": len(failed), "violating": failed,
                    "uncertified": unc, "verifier_pid": d["ver"]["pid"],
                    "verifier_imports_from_impl": d["ver"]["imports"]}
    # C-VERIFIER
    n_curve = sum(len(sets[s]) for s in ("U62", "S62", "C20"))
    acc = [r for r in neg.get("certificates", []) if r["verified"]]
    ch["C-VERIFIER"] = {"pass": (d["ver"]["construction_checked"] == n_curve and not d["ver"]["construction_disagreements"]
                                 and neg.get("_built") == 20 and neg.get("submitted") == 20 and not acc),
                        "construction_checked": d["ver"]["construction_checked"], "curve_instances": n_curve,
                        "construction_disagreements": d["ver"]["construction_disagreements"],
                        "negative_controls_built": neg.get("_built"), "negative_controls_rejected":
                            (neg.get("submitted", 0) - len(acc)),
                        "violating": d["ver"]["construction_disagreements"] + [f"accepted corrupted {r['key']} {r['closure']}" for r in acc]}
    # C-NULLS
    shas = {f"{c}/{s}": d[(c, s)]["closure_module_sha256"] for c, sl in CLOSURES.items() for s in sl}
    struct = d["p1"]["c_nulls_structure"]
    ch["C-NULLS"] = {"pass": len(set(shas.values())) == 1 and struct["pass"], "closure_module_sha256_per_set": shas,
                     "structure": struct,
                     "violating": struct["F-AFF-1_two_way_identity_fail"] + struct["F-NULLF2_support_outside_U"]
                     + struct["p1_vs_targets_mismatch"] + ([] if len(set(shas.values())) == 1 else ["code-path hash differs"])}
    ch["C-DET"] = {"pass": bool(d["det"]["pass"]), "violating": d["det"]["mismatches"],
                   "instances": len(d["det"]["instances"]), "pid": d["det"]["pid"]}
    # informational consistency (not a spec control)
    info = []
    for s in CLOSURES["W_5"]:
        for k, r in d[("W_5", s)]["records"].items():
            m5 = d[("M_5", s)]["records"].get(k)
            if m5 is not None and r.get("dims") and r["dims"][0] != m5["rank"]:
                info.append({"key": k, "rule": "W_5 iteration-0 dimension != rank M_5"})
    for (c, s) in [(c, s) for c, sl in CLOSURES.items() for s in sl]:
        for k, r in d[(c, s)]["records"].items():
            if r.get("one") and r.get("engine_self_check_sum_is_1") is False:
                info.append({"key": k, "rule": f"{c}: engine self-check of certificate failed"})
    u62_d3 = [i["key"] for i in sets["U62"] if i["archived"]["one_in_R_3"] is not False]
    ch["X-CONSISTENCY (informational, not a spec control)"] = {
        "pass": not info and not u62_d3, "violating": info,
        "U62_one_in_R_3_not_false": u62_d3,
        "ell_identity_failures": [k for k, r in p1.items() if r.get("ell_identity_holds") is False]}
    return ch


def aggregate(run, sets, neg):
    t0 = time.time()
    d = load_all(run)
    st, vmap = status_table(d, sets)
    ch = instrument_checks(d, sets, st, neg)
    p1 = d["p1"]["records"]
    # ---- per-instance U62 labels
    labels = {}
    for inst in sets["U62"]:
        k = inst["key"]
        w4, m5, w5 = st[(k, "W_4")], st[(k, "M_5")], st.get((k, "W_5"), "not_run")
        if w5 == "not_run":
            w5 = "not_run" if (k, "W_5") not in st else w5
        if w4 == "verified":
            lab = "W4"
        elif m5 == "verified":
            lab = "M5-only"
        elif w5 == "verified":
            lab = "W5-only"
        elif "UNDETERMINED(budget)" in (w5,):
            lab = "UNDETERMINED(budget)"
        elif "UNCERTIFIED" in (w4, m5, w5) or "certificate_failed" in (w4, m5, w5):
            lab = "UNCERTIFIED"
        else:
            lab = "none"
        labels[k] = {"idx": inst["idx"], "label": lab, "W_4": w4, "M_5": m5, "W_5": w5,
                     "M5_also": m5 == "verified" if lab == "W4" else None}
    U = sets["U62"]
    a = sum(1 for i in U if st[(i["key"], "W_4")] == "verified")
    b = sum(1 for i in U if st[(i["key"], "M_5")] == "verified")
    r = sum(1 for i in U if labels[i["key"]]["label"] in ("W4", "M5-only", "W5-only"))
    ci_a, ci_b, ci_r = clopper_pearson(a, 62), clopper_pearson(b, 62), clopper_pearson(r, 62)
    label_counts = {}
    for v in labels.values():
        label_counts[v["label"]] = label_counts.get(v["label"], 0) + 1
    # ---- MR4 nulls
    mr4 = {}
    ci_null = {}
    for s in NULLS:
        mr4[s] = {}
        for c in ("W_4", "M_5", "W_5"):
            ran = [i for i in sets[s] if (i["key"], c) in st and st[(i["key"], c)] != "not_run"
                   and i["key"] in d[(c, s)]["records"]]
            x = sum(1 for i in ran if st[(i["key"], c)] == "verified")
            ci = clopper_pearson(x, len(ran))
            ci_null[(s, c)] = ci
            mr4[s][c] = {"verified_refuted": x, "n": len(ran), "CP95": public(ci),
                         "undetermined": sum(1 for i in ran if st[(i["key"], c)] == "UNDETERMINED(budget)")}
    # ---- MR5
    s62 = {c: sum(1 for i in sets["S62"] if (i["key"], c) in st and d[(c, "S62")]["records"].get(i["key"], {}).get("one"))
           for c in ("W_4", "M_5", "W_5")}
    s62_n = {c: len(d[(c, "S62")]["records"]) for c in ("W_4", "M_5", "W_5")}
    cc = cert_counts(d, sets)
    mr5 = {"C-PS1_refuted_satisfiable": s62, "C-PS1_checked": s62_n, "certificates": cc,
           "totals": {"submitted": d["ver"]["submitted"], "verified": d["ver"]["verified"],
                      "failed": d["ver"]["failed"],
                      "uncertified": sum(v["uncertified"] for v in cc.values())}}
    # ---- secondary
    def two_by_two(s):
        t = {"W4+M5+": 0, "W4+M5-": 0, "W4-M5+": 0, "W4-M5-": 0}
        for i in sets[s]:
            w = st[(i["key"], "W_4")] == "verified"
            m = st[(i["key"], "M_5")] == "verified"
            t[f"W4{'+' if w else '-'}M5{'+' if m else '-'}"] += 1
        return t
    tables = {s: two_by_two(s) for s in ["U62"] + NULLS}
    dstar = {"4": 324, "5": b, ">5": 62 - b,
             "note": "plain-Macaulay D* of the F-S3 unsat arm (386) extended to D = 5; a reading only, no verdict on HEUR-CERTBIN-TS4"}
    comb = {"W_4": {"numerator": 324 + a, "denominator": 386, "rate": float(Fraction(324 + a, 386))},
            "any_closure_D_le_5": {"numerator": 324 + r, "denominator": 386, "rate": float(Fraction(324 + r, 386))},
            "note": "324 inherited from RUN-CERTBIN-3b7e05 via monotonicity (M_4 subset W_4), checked on C20 (C-MONO)"}
    per_w4 = []
    for s in ("U62", "C20", "S62", "N-AFF62", "N-F262"):
        for i in sets[s]:
            rr = d[("W_4", s)]["records"][i["key"]]
            per_w4.append({"key": i["key"], "set": s, "one": rr["one"], "one_first_iteration": rr["one_first_iteration"],
                           "iterations_to_fixpoint": rr["iterations_to_fixpoint"], "final_dim": rr["final_dim"],
                           "dims": rr["dims"], "dims_by_deg": rr["dims_by_deg"],
                           "ell_in_W4_le1": rr.get("ell_in_W4_le1")})
    first_it_U = {}
    for i in U:
        v = d[("W_4", "U62")]["records"][i["key"]]["one_first_iteration"]
        first_it_U[str(v)] = first_it_U.get(str(v), 0) + 1
    sizes = {}
    vrec = {(x["key"], x["closure"]): x for x in d["ver"]["certificates"]}
    for c in CLOSURES:
        zs = [x["size"] for (k, cl), x in vrec.items() if cl == c]
        md = [x["max_deg_mu"] for (k, cl), x in vrec.items() if cl == c and x["max_deg_mu"] is not None]
        sizes[c] = {"count": len(zs), "min": min(zs) if zs else None, "median": statistics.median(zs) if zs else None,
                    "max": max(zs) if zs else None, "max_deg_mu_max": max(md) if md else None,
                    "max_deg_mu_distribution": {str(x): md.count(x) for x in sorted(set(md))}}
    wall = {f"{c}/{s}": {"wall_seconds": d[(c, s)]["wall_seconds"], "peak_rss_bytes_process_so_far": d[(c, s)]["peak_rss_bytes"],
                         "instances": len(d[(c, s)]["records"])} for c, sl in CLOSURES.items() for s in sl}
    # ---- decision rules
    dr5_fail = [c for c in ("C-PS1", "C-CERT", "C-MONO", "C-BASE", "C-VERIFIER", "C-DET") if not ch[c]["pass"]]
    oracle_void = not ch["C-ORACLE"]["pass"]
    pre_void = [c for c in ("C-SRC", "C-SELF", "C-FIX") if not ch[c]["pass"]]
    blocked = bool(dr5_fail or pre_void or oracle_void)
    drs = {}
    drs["RC1-DR-5"] = {"instrument_controls": {c: ch[c]["pass"] for c in ("C-PS1", "C-CERT", "C-MONO", "C-BASE", "C-VERIFIER", "C-DET")},
                       "failed": dr5_fail, "also_failed_stop_controls": pre_void, "C-ORACLE_failed": oracle_void,
                       "verdict": "PASS" if not blocked else "FAIL: no DR-1..DR-4 verdict issued"}
    if blocked:
        why = f"not evaluable: instrument failure {dr5_fail + pre_void + (['C-ORACLE'] if oracle_void else [])}"
        for k in ("RC1-DR-1", "RC1-DR-2", "RC1-DR-3", "RC1-DR-4"):
            drs[k] = {"verdict": why}
    else:
        if a >= 56:
            v1 = "ARTIFACT (predominant)"
        elif a <= 6:
            v1 = "GENUINE D*_W > 4 (predominant)"
        else:
            v1 = "MIXED"
        drs["RC1-DR-1"] = {"inputs": {"a": a, "n": 62, "CP95": public(ci_a)}, "verdict": v1,
                           "E-A_falsified_(a<=31)": a <= 31, "E-G_falsified_(a>=32)": a >= 32}
        undet = [k for k, v in labels.items() if v["label"] in ("UNDETERMINED(budget)", "UNCERTIFIED")]
        notref_L1 = [k for k, v in labels.items() if v["label"] in ("none", "UNDETERMINED(budget)", "UNCERTIFIED")]
        notref_L2 = [k for k, v in labels.items() if v["label"] == "none"]

        def lab(nnot):
            return "CLEAN" if nnot == 0 else ("NEAR-CLEAN" if nnot <= 3 else "RESIDUE")
        L1 = lab(len(notref_L1))
        L2 = lab(len(notref_L2))
        v2 = L1 if L1 == L2 else "UNDETERMINED (budget or certification)"
        drs["RC1-DR-2"] = {"inputs": {"r": r, "n": 62, "CP95_r": public(ci_r), "undetermined_or_uncertified": len(undet),
                                      "L1_denominator": 62, "L1_not_refuted": len(notref_L1),
                                      "L2_denominator": 62 - len(undet), "L2_not_refuted": len(notref_L2)},
                           "L1": L1, "L2": L2, "verdict": v2,
                           "residue_idx": sorted(labels[k]["idx"] for k in notref_L1)}
        drs["RC1-DR-3"] = {"inputs": {"b": b, "n": 62, "CP95": public(ci_b), "two_by_two_U62": tables["U62"]},
                           "verdict": "M_5 SUFFICES" if b == 62 else f"M_5 refutes {b} of 62",
                           "note": "descriptive; no verdict on TS4"}
        dr4 = {}
        nulls_void = not ch["C-NULLS"]["pass"]
        for X, ciU in (("W_4", ci_a), ("M_5", ci_b)):
            if nulls_void:
                dr4[X] = {"verdict": "not evaluable: C-NULLS failed"}
                continue
            seps = {s: separated(ciU, ci_null[(s, X)]) for s in NULLS}
            dr4[X] = {"U62": public(ciU), "nulls": {s: public(ci_null[(s, X)]) for s in NULLS},
                      "U62_lower_exceeds_null_upper": seps,
                      "verdict": f"S_3-SPECIFIC at {X}" if all(seps.values()) else f"NOT DISTINGUISHED at {X}"}
        drs["RC1-DR-4"] = dr4
    dr2v = drs["RC1-DR-2"].get("verdict")
    drs["RC1-DR-6"] = {"RC1-DR-2_verdict": dr2v, "clean_or_near_clean": dr2v in ("CLEAN", "NEAR-CLEAN"),
                       "note": "recorded, not decided here; the Coordinator decides NA-5 after review"}
    drs["RC1-DR-7"] = {"primary": {"RC1-DR-1": drs["RC1-DR-1"]["verdict"], "RC1-DR-2": dr2v},
                       "note": "everything else is secondary"}
    all_pass = all(ch[c]["pass"] for c in ch if not c.startswith("X-"))
    validity = "completed_valid" if all_pass else "invalid_measurement"
    invalid_reasons = [c for c in ch if not c.startswith("X-") and not ch[c]["pass"]]
    # ---- write artifacts
    out = run.out
    dump_json(os.path.join(out, "instrument-checks.json"), {"experiment_id": EXP_ID, "run_id": run.a.run_id,
                                                              "controls": ch, "all_spec_controls_pass": all_pass,
                                                              "written_at": now()})
    dump_json(os.path.join(out, "decision-rules.json"), {"experiment_id": EXP_ID, "run_id": run.a.run_id,
                                                           "rules": drs, "applied": "mechanically, as frozen in spec v1",
                                                           "written_at": now()})
    cell = {
        "experiment_id": EXP_ID, "run_id": run.a.run_id,
        "MR1_w4_refuted_U62": {"a": a, "n": 62, "CP95": public(ci_a)},
        "MR2_m5_refuted_U62": {"b": b, "n": 62, "CP95": public(ci_b)},
        "MR3_refuted_at_D_le_5_U62": {"r": r, "n": 62, "CP95": public(ci_r), "label_counts": label_counts},
        "MR4_null_refutation_rates": mr4,
        "MR5_soundness_and_certificates": mr5,
        "secondary": {"two_by_two": tables, "plain_macaulay_D_star_unsat_arm": dstar,
                      "combined_unsat_arm_rates": comb,
                      "U62_W4_first_iteration_of_1": first_it_U,
                      "U62_ell_in_W4_le1": sum(1 for i in U if d[("W_4", "U62")]["records"][i["key"]].get("ell_in_W4_le1")),
                      "certificate_sizes": sizes, "wall_and_rss_per_closure_set": wall,
                      "per_instance_W4": per_w4},
        "validity": validity, "invalid_reasons": invalid_reasons,
        "labels": {"measured": "every count and dimension here is measured by the run", "modeled": "none"},
    }
    if blocked:
        cell["void_note"] = "MR1-MR4 void or arm metrics void per the failed controls; numbers kept for the record"
    dump_json(os.path.join(out, "cell-summary.json"), cell)
    raw = raw_result(run, sets)
    agree = {"a": raw["a"] == a, "b": raw["b"] == b, "r": raw["r"] == r, "labels": raw["label_counts"] == label_counts,
             "MR4": all(raw["null_counts"][s][c] == mr4[s][c]["verified_refuted"] for s in NULLS for c in ("W_4", "M_5", "W_5")),
             "MR5_S62": raw["s62_refuted"] == s62,
             "MR5_totals": raw["cert_totals"] == {k: mr5["totals"][k] for k in ("submitted", "verified", "failed")}}
    raw["agreement_with_cell_summary"] = agree
    raw["agreement_all"] = all(agree.values())
    dump_json(os.path.join(out, "raw-result.json"), raw)
    env = environment()
    dump_json(os.path.join(out, "environment.json"), env)
    write_manifest(run, d, ch, validity, invalid_reasons, a, b, r, raw["agreement_all"], env, neg)
    write_report(run, d, ch, drs, cell, labels, a, b, r, ci_a, ci_b, ci_r, mr4, mr5, validity)
    run.log(f"phase 7 done: validity={validity} a={a} b={b} r={r} raw_agree={raw['agreement_all']} ({time.time() - t0:.1f}s)")
    return 0


def raw_result(run, sets):
    """Independent recount from closures.jsonl.gz and certificate-verification.json only."""
    ver = json.load(open(os.path.join(run.out, "certificate-verification.json")))
    vok = {(r["key"], r["closure"]) for r in ver["certificates"] if r["verified"]}
    rows = []
    with gzip.open(os.path.join(run.out, "closures.jsonl.gz"), "rt") as f:
        for line in f:
            rows.append(json.loads(line))
    per = {}
    for x in rows:
        per.setdefault(x["key"], {})[x["closure"]] = x
    U = [i["key"] for i in sets["U62"]]

    def vref(k, c):
        x = per[k].get(c)
        return bool(x and x.get("one") and (k, c) in vok)
    a = sum(vref(k, "W_4") for k in U)
    b = sum(vref(k, "M_5") for k in U)
    r = sum(vref(k, "W_4") or vref(k, "M_5") or vref(k, "W_5") for k in U)
    lc = {}
    inst_rows = []
    for k in U:
        if vref(k, "W_4"):
            lab = "W4"
        elif vref(k, "M_5"):
            lab = "M5-only"
        elif vref(k, "W_5"):
            lab = "W5-only"
        elif per[k].get("W_5", {}).get("label") == "UNDETERMINED(budget)":
            lab = "UNDETERMINED(budget)"
        elif any(per[k].get(c, {}).get("one") for c in ("W_4", "M_5", "W_5")):
            lab = "UNCERTIFIED"
        else:
            lab = "none"
        lc[lab] = lc.get(lab, 0) + 1
    for s in SET_ORDER:
        for i in sets[s]:
            k = i["key"]
            inst_rows.append({"key": k, "set": s, "idx": i["idx"],
                              **{c: {"one": per[k][c].get("one"), "label": per[k][c].get("label"),
                                     "verified_certificate": (k, c) in vok} for c in per[k]}})
    nc = {s: {c: sum(vref(i["key"], c) for i in sets[s]) for c in ("W_4", "M_5", "W_5")} for s in NULLS}
    s62 = {c: sum(1 for i in sets["S62"] if per[i["key"]].get(c, {}).get("one")) for c in ("W_4", "M_5", "W_5")}
    return {"experiment_id": EXP_ID, "run_id": run.a.run_id,
            "source": "recomputed from closures.jsonl.gz and certificate-verification.json only",
            "a": a, "b": b, "r": r, "label_counts": lc, "null_counts": nc, "s62_refuted": s62,
            "cert_totals": {"submitted": ver["submitted"], "verified": ver["verified"], "failed": ver["failed"]},
            "instances": inst_rows}


def environment():
    import numpy
    return {"python_version": sys.version, "python_executable": sys.executable,
            "numpy_version": numpy.__version__, "numpy_location": numpy.__file__,
            "pyyaml_version": yaml.__version__,
            "platform": platform.platform(), "machine": platform.machine(), "cpu_count": os.cpu_count(),
            "mem_total_kB": open("/proc/meminfo").readline().split()[1],
            "env": {k: os.environ.get(k) for k in ("PYTHONDONTWRITEBYTECODE", "OMP_NUM_THREADS",
                                                   "OPENBLAS_NUM_THREADS", "AUTORESEARCH_SESSION_MODEL")},
            "rlimit_as_bytes": MEM_LIMIT, "compiled_helpers": "none (pure Python + numpy)", "sage": "not used",
            "randomness": {"S_selftest": S_SELFTEST, "note": "the only seed; used by selftest.py only. No instance is drawn."}}


def write_manifest(run, d, ch, validity, reasons, a, b, r, raw_ok, env, neg):
    out = run.out
    invs = [json.loads(line) for line in open(os.path.join(run.ck, "invocations.jsonl"))]
    impl_dir = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")
    ver_dir = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/verifier")
    impl_sha = {f: sha256_file(os.path.join(impl_dir, f)) for f in sorted(os.listdir(impl_dir))
                if os.path.isfile(os.path.join(impl_dir, f))}
    ver_sha = {f: sha256_file(os.path.join(ver_dir, f)) for f in sorted(os.listdir(ver_dir))
               if os.path.isfile(os.path.join(ver_dir, f))}
    plan = os.path.join(REPO, run.a.plan)
    tim = d["timings"]["timings_seconds"]
    arts = {}
    for f in sorted(os.listdir(out)):
        p = os.path.join(out, f)
        if os.path.isfile(p) and f not in ("manifest.yaml", "run-report.md", "stdout.log", "stderr.log"):
            arts[f] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
    total = 0
    for root, _, files in os.walk(out):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    man = {"run": {
        "id": run.a.run_id, "experiment_id": EXP_ID, "task_id": TASK_ID, "status": validity,
        "invalid_reasons": reasons, "claim_tier": "toy",
        "certificate": {"kind": "unsatisfiability_certificate",
                        "verifier": "experiments/EXP-CERTBIN-e94b27/verifier/verify_cert.py (separate process)",
                        "submitted": d["ver"]["submitted"], "verified": d["ver"]["verified"], "failed": d["ver"]["failed"],
                        "independence": "code-level only (no shared import); same author as the closure engine (EX-10)"},
        "code": {"commit_at_first_invocation": invs[0]["git"].get("commit"),
                 "dirty_at_first_invocation": invs[0]["git"].get("dirty"),
                 "dirty_paths_at_first_invocation": invs[0]["git"].get("status_porcelain"),
                 "impl_sha256": impl_sha, "verifier_sha256": ver_sha,
                 "invocations": [{"argv": i["argv"], "at": i["at"], "pid": i["pid"], "commit": i["git"].get("commit"),
                                  "dirty": i["git"].get("dirty")} for i in invs],
                 "verifier_invocations": [{"argv": "verify_command (see command.txt)", "pid": d["ver"]["pid"],
                                           "finished_at": d["ver"]["finished_at"]},
                                          {"argv": neg.get("_command"), "pid": neg.get("pid"),
                                           "finished_at": neg.get("finished_at")}],
                 "command_file": "command.txt"},
        "trial_plan": {"path": run.a.plan, "sha256": sha256_file(plan),
                       "written_at": json.load(open(plan))["written_at"]},
        "specification": {"path": SPEC, "sha256": sha256_file(os.path.join(REPO, SPEC)),
                          "byte_identical_to_approved": d["inputs"]["specification"]["byte_identical"]},
        "inference": {"requested_policy": "executor-implementation", "canonical_policy": "executor-implementation",
                      "backend": "anthropic", "adapter_resolved_model_id": "claude-sonnet-5",
                      "resolved_model_id": "claude-opus-5-5",
                      "model_provenance": "operator-supplied (executor session model as reported by the Claude Code runtime)",
                      "model_verified": False, "requested_reasoning_effort": "medium", "reasoning_effort": None,
                      "fallback_used": True,
                      "fallback_reason": ("Claude Code subagent inherits the session model (claude-opus-5-5); the adapter "
                                          "binds executor-implementation to claude-sonnet-5. fallback_allowed: true in the "
                                          "handoff (DEC-20260923-4d7a19 R-1)."),
                      "independent_session": False,
                      "note": "The model wrote the code. Every number comes from deterministic code; no model in the computational loop."},
        "environment": {"see": "environment.json", "python_version": env["python_version"].split()[0],
                        "numpy_version": env["numpy_version"]},
        "inputs": {"receipt": "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json",
                   "files": {r["path"]: r["sha256"] for r in d["inputs"]["inputs"]}, "C-SRC": d["inputs"]["pass"]},
        "seeds": {"S_selftest": S_SELFTEST, "other_randomness": "none (zero sampling)"},
        "timing": {"selftest_wall_seconds": d["selftest"]["wall_seconds"], "phases_seconds": tim,
                   "phase5_determinism_seconds": d["det"]["wall_seconds"],
                   "phase6_verifier_seconds": d["ver"]["wall_seconds"],
                   "phase6_negative_controls_verifier_seconds": neg.get("wall_seconds")},
        "resources": {"memory_cap": "RLIMIT_AS 3 GiB set in-process (selftest, driver)", "workers": 1,
                      "OMP/OPENBLAS threads": 1, "run_watchdog_seconds": RUN_WATCHDOG,
                      "w5_per_instance_watchdog_seconds": W5_WATCHDOG,
                      "peak_rss_bytes": {"selftest": d["selftest"]["peak_rss_bytes"],
                                         "phases_1_4": d["timings"]["peak_rss_bytes"],
                                         "phase5": d["det"]["peak_rss_bytes"],
                                         "phase7": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}},
        "result": {"a_MR1": a, "b_MR2": b, "r_MR3": r, "raw_result_agrees_with_cell_summary": raw_ok,
                   "controls": {c: ch[c]["pass"] for c in ch}},
        "artifacts": arts,
        "package_bytes_at_manifest_time": total,
        "maximum_runs": 2, "run_attempt": 1,
        "written_at": now()}}
    with open(os.path.join(out, "manifest.yaml"), "w") as f:
        yaml.safe_dump(man, f, sort_keys=False, width=120)


def write_report(run, d, ch, drs, cell, labels, a, b, r, ci_a, ci_b, ci_r, mr4, mr5, validity):
    spec = yaml.safe_load(open(os.path.join(REPO, SPEC)))["experiment"]
    L = []
    L.append(f"# {run.a.run_id} -- {EXP_ID} (RC-1) run report")
    L.append("")
    L.append(f"Task {TASK_ID}. Validity status: **{validity}**. Observations only; no hypothesis status, "
             "evidence record or knowledge entry is written or implied here.")
    L.append("")
    L.append("## Claim tier and scope (verbatim from the specification)")
    L.append("")
    L.append(f"- claim_tier: {spec['claim_tier_and_scope']['claim_tier']}")
    L.append(f"- statement: {spec['claim_tier_and_scope']['statement']}")
    L.append(f"- sota_delta: {spec['claim_tier_and_scope']['sota_delta']}")
    L.append(f"- dominated_by: {spec['claim_tier_and_scope']['dominated_by']}")
    L.append(f"- affected_vs_safe: {spec['claim_tier_and_scope']['affected_vs_safe']}")
    L.append("")
    L.append("## Independence disclosure (EX-10)")
    L.append("")
    L.append("The same executor wrote the closure engine (impl/) and the verifier (verifier/). Their independence is "
             "code-level only: verify_cert.py imports nothing from impl/ or EXP-CERTBIN-4e92d7/impl/, rebuilds f_0..f_16 "
             "by evaluating S_3 at all 2^18 points with its own F_{2^17} arithmetic plus a Moebius transform, and runs "
             "as a separate process. It is NOT author-independent; the author-independent second verification belongs "
             "to the review round.")
    L.append("")
    L.append("## Instrument checks")
    L.append("")
    for c, v in ch.items():
        L.append(f"- {c}: {'PASS' if v['pass'] else 'FAIL'}" + ("" if v["pass"] else f" -- violating: {json.dumps(v.get('violating'))}"))
    L.append("")
    L.append("## Primary metrics (verified certificates only)")
    L.append("")
    L.append(f"- MR1 a = {a}/62, CP95 [{ci_a['lower']}, {ci_a['upper']}]")
    L.append(f"- MR2 b = {b}/62, CP95 [{ci_b['lower']}, {ci_b['upper']}]")
    L.append(f"- MR3 r = {r}/62, CP95 [{ci_r['lower']}, {ci_r['upper']}]; U62 labels: {json.dumps(cell['MR3_refuted_at_D_le_5_U62']['label_counts'])}")
    for s, v in mr4.items():
        L.append(f"- MR4 {s}: " + "; ".join(f"{c} {x['verified_refuted']}/{x['n']} CP95 [{x['CP95']['lower']}, {x['CP95']['upper']}]"
                                             for c, x in v.items()))
    L.append(f"- MR5 refuted satisfiable controls (S62): {json.dumps(mr5['C-PS1_refuted_satisfiable'])} of {json.dumps(mr5['C-PS1_checked'])}; "
             f"certificates {json.dumps(mr5['totals'])}")
    L.append("")
    L.append("## Decision rules (applied mechanically)")
    L.append("")
    for k in ("RC1-DR-1", "RC1-DR-2", "RC1-DR-3", "RC1-DR-4", "RC1-DR-5", "RC1-DR-6", "RC1-DR-7"):
        v = drs[k]
        if k == "RC1-DR-4" and "verdict" not in v:
            L.append(f"- {k}: " + "; ".join(f"{X}: {v[X]['verdict']}" for X in v))
        elif k == "RC1-DR-2" and "L1" in v:
            L.append(f"- {k}: {v['verdict']} (L1 = {v['L1']}, L2 = {v['L2']}); residue idx: {v['residue_idx']}")
        elif k == "RC1-DR-6":
            L.append(f"- {k}: RC1-DR-2 returned {v['RC1-DR-2_verdict']}; clean_or_near_clean = {v['clean_or_near_clean']} (recorded, not decided here)")
        elif k == "RC1-DR-7":
            L.append(f"- {k}: primary verdicts: {json.dumps(v['primary'])}")
        else:
            L.append(f"- {k}: {v['verdict']}")
    L.append("")
    L.append("## Pre-registered predictions PA-1..PA-3 (H-CERTBIN-5e71c9 C1): threshold readings")
    L.append("")
    evaluable = drs["RC1-DR-5"]["verdict"] == "PASS"
    if evaluable:
        pa1 = ("held (a >= 56, E-A threshold)" if a >= 56 else
               "failed (a <= 31: E-A falsified by the frozen rule)" if a <= 31 else
               "neither E-A (>= 56) nor its falsification (<= 31) threshold reached")
        L.append(f"- PA-1: a = {a}. {pa1}. E-G threshold (a <= 6): {'met' if a <= 6 else 'not met'}; "
                 f"E-G falsified by the frozen rule (a >= 32): {a >= 32}.")
        L.append(f"- PA-2: r = {r}; label {drs['RC1-DR-2']['verdict']} (CLEAN iff r = 62; NEAR-CLEAN iff 59 <= r <= 61; RESIDUE iff r <= 58).")
        nsat = sum(mr5["C-PS1_refuted_satisfiable"].values())
        L.append(f"- PA-3: refuted satisfiable controls = {nsat}; {'held' if nsat == 0 else 'failed (instrument failure, never evidence)'}.")
    else:
        L.append("- PA-1..PA-3: not evaluable (RC1-DR-5 instrument failure).")
    L.append("")
    L.append("## Coordinator prior (a)-(d): which parts the observations contradict")
    L.append("")
    if evaluable:
        dr4 = drs["RC1-DR-4"]
        L.append(f"- (a) modal expectation a in [15, 50] (MIXED): observed a = {a} -> "
                 f"{'consistent' if 15 <= a <= 50 else 'overturned (observed outside the modal range)'}.")
        bcl = drs["RC1-DR-2"]["verdict"] in ("CLEAN", "NEAR-CLEAN")
        L.append(f"- (b) b >= 56 and D <= 5 picture CLEAN or NEAR-CLEAN: observed b = {b}, DR-2 {drs['RC1-DR-2']['verdict']} -> "
                 f"{'consistent' if (b >= 56 and bcl) else 'overturned'}.")
        m5v = dr4.get("M_5", {}).get("verdict")
        w4v = dr4.get("W_4", {}).get("verdict")
        cpart = []
        cpart.append(f"'NOT DISTINGUISHED at M_5' expected, observed '{m5v}'")
        cpart.append(f"nulls near 0 at W_4 and, if a >= 10, 'S_3-SPECIFIC at W_4' expected; observed null W_4 counts "
                     f"{[mr4[s]['W_4']['verified_refuted'] for s in mr4]}, '{w4v}'")
        c_ok = (m5v == "NOT DISTINGUISHED at M_5") and ((a < 10) or (w4v == "S_3-SPECIFIC at W_4"))
        L.append(f"- (c) {'; '.join(cpart)} -> {'consistent' if c_ok else 'overturned (at least in part)'}.")
        dok = mr5["totals"]["failed"] == 0 and mr5["totals"]["uncertified"] == 0
        L.append(f"- (d) every W_4 / M_5 refutation certifies: failed = {mr5['totals']['failed']}, uncertified = "
                 f"{mr5['totals']['uncertified']} -> {'consistent' if dok else 'overturned'}.")
    else:
        L.append("- not evaluable (instrument failure)")
    L.append("")
    L.append("## Secondary observations")
    L.append("")
    sec = cell["secondary"]
    L.append(f"- 2 x 2 (W_4 verified refutation) x (M_5 verified refutation): {json.dumps(sec['two_by_two'])}")
    L.append(f"- Plain-Macaulay D* of the F-S3 unsat arm extended to D = 5: {json.dumps({k: v for k, v in sec['plain_macaulay_D_star_unsat_arm'].items() if k != 'note'})} (a reading; no verdict on HEUR-CERTBIN-TS4)")
    cr = sec["combined_unsat_arm_rates"]
    L.append(f"- Combined unsat-arm rates at the Stage-1 cell: W_4 {cr['W_4']['numerator']}/386; any closure at D <= 5 {cr['any_closure_D_le_5']['numerator']}/386 (324 inherited via monotonicity, checked on C20)")
    L.append(f"- U62: iteration at which 1 first appears in W_4: {json.dumps(sec['U62_W4_first_iteration_of_1'])}; ell in W_4 cap B_<=1 on {sec['U62_ell_in_W4_le1']}/62")
    L.append(f"- Certificate sizes per closure: {json.dumps(sec['certificate_sizes'])}")
    L.append("")
    L.append("## Scope")
    L.append("")
    L.append("Toy tier. One cell: n = 17, f = t^17 + t^3 + 1, m = 2, l = 9, V = {deg < 9}, curve A = 97044, "
             "B = 126251, archived subgroup targets of RUN-CERTBIN-3b7e05. Nothing here transfers to other n, other "
             "curves, F4 step degrees or Semaev's Assumption 1. A non-refutation at W_5 concerns derivations of a-priori "
             "degree <= 5 only. No discrete logarithm and no relation is claimed; sota_delta zero; oracle A and parallel "
             "rho dominate.")
    L.append("")
    with open(os.path.join(run.out, "run-report.md"), "w") as f:
        f.write("\n".join(L) + "\n")
