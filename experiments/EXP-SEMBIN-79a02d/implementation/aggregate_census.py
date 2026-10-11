"""EXP-SEMBIN-79a02d -- aggregate Stage-2 raw run records into stage2/census.json
and evaluate the frozen outcome conditions (stage0/definitions.md section 5)
mechanically. Strata are never pooled: every summary is keyed by
(n, family, enumerated SAT/UNSAT sub-stratum).
usage: aggregate_census.py <out_census.json> <raw-result.json>...
"""
import json, sys
from collections import defaultdict


def compact(r):
    c = {k: r.get(k) for k in ("n", "family", "seed", "status", "N", "V_count", "sat", "n_quadratic",
                                "generator_degree_hist", "d_ff_ic", "d_ff_sem", "d_solv", "seconds", "error")}
    inst = r.get("instance", {})
    c["z"] = inst.get("z"); c["k"] = inst.get("k")
    if "corruption" in inst:
        c["corruption"] = inst["corruption"]; c["corruption_draws"] = inst.get("corruption_draws")
    e = r.get("enumeration")
    if e:
        c["enumeration"] = {"routes": e["routes"], "agree": e["agree"],
                            "E1_count": e.get("E1", {}).get("count"), "E2_count": e.get("E2", {}).get("count")}
    c["macaulay"] = {}
    for D, m in (r.get("mac") or {}).items():
        a, b = m["A"], m["B"]
        c["macaulay"][D] = {"nrows": a["nrows"], "ncols_occurring": a["ncols_occurring"], "ncols_all": a["ncols_all"],
                            "rank_armA": a["rank"], "rank_armB": b["rank"], "dual_agree": m["dual_agree"],
                            "matrix_fingerprint_A": a["fingerprint"], "matrix_fingerprint_B": b["fingerprint"],
                            "rank_lt_nrows": a["rank"] < a["nrows"], "nrows_minus_rank": a["nrows"] - a["rank"],
                            "pred": m["pred"], "deficit": m["pred"] - a["rank"],
                            "pivots_by_degree": a["pivots_by_degree"],
                            "seconds_A": a["seconds"], "seconds_B": b["seconds"],
                            "peak_rss_kb_A": a["peak_rss_kb"], "peak_rss_kb_B": b["peak_rss_kb"]}
    c["solv"] = {}
    for D, s in (r.get("solv") or {}).items():
        a, b = s["A"], s["B"]
        c["solv"][D] = {"dim_W_armA": a["dim_W"], "dim_W_armB": b["dim_W"], "ncols": a["ncols"],
                        "codim": a["codim"], "one_in_W": a["one_in_W"], "iterations": a["iterations"],
                        "iterations_armB": b["iterations"], "round_new_dims": a["round_new_dims"],
                        "level0_rows": a["level0_rows"], "level0_rank": a["level0_rank"],
                        "level0_rejected_degree": a["level0_rejected_degree"],
                        "dual_agree": s["dual_agree"], "solv_holds": s.get("solv_holds"), "r_V": s.get("r_V"),
                        "soundness": s.get("soundness"), "c2_disagreements": s.get("c2_disagreements"),
                        "seconds_A": a["seconds"], "seconds_B": b["seconds"],
                        "peak_rss_kb_A": a["peak_rss_kb"], "peak_rss_kb_B": b["peak_rss_kb"]}
    return c


def main():
    out_path = sys.argv[1]
    recs = {}
    sources = []
    censored = []
    for p in sys.argv[2:]:
        d = json.load(open(p))
        sources.append({"raw": p, "n": d["n"], "phase": d["phase"], "modulus_int": d["modulus_int"],
                        "modulus_source": d["modulus_source"]})
        for nr in d.get("not_started", []):
            censored.append({"n": d["n"], "phase": d["phase"], **nr})
        for r in d["records"]:
            key = (r["n"], r["family"], r["seed"])
            if d["phase"] == "main":
                recs[key] = compact(r)
            else:  # d5: merge D=5 macaulay
                base = recs.setdefault(key, {"n": r["n"], "family": r["family"], "seed": r["seed"], "macaulay": {}})
                if r.get("status") == "ok":
                    base["macaulay"].update(compact(r)["macaulay"])
                else:
                    base.setdefault("d5_failures", []).append({"status": r.get("status"), "error": r.get("error")})
    instances = [recs[k] for k in sorted(recs, key=lambda k: (k[0], ["anchor", "planted", "uniform_z", "null", "known_false_a", "known_false_b"].index(k[1]), k[2]))]

    # ---- summaries, never pooled across (n, family, sat-substratum)
    groups = defaultdict(list)
    for r in instances:
        if r.get("status") != "ok":
            continue
        sub = "sat" if r.get("sat") else "unsat"
        groups[(r["n"], r["family"], sub)].append(r)
    summary = []
    for (n, fam, sub), rs in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        def vals(f):
            return [f(r) for r in rs]
        s = {"n": n, "family": fam, "substratum": sub, "instances": len(rs), "seeds": vals(lambda r: r["seed"]),
             "V_counts": vals(lambda r: r["V_count"]),
             "d_ff_ic": vals(lambda r: r["d_ff_ic"]), "d_ff_sem": vals(lambda r: r["d_ff_sem"]),
             "d_solv": vals(lambda r: r["d_solv"]),
             "solv4_holds": vals(lambda r: r["solv"]["4"]["solv_holds"]),
             "solv4_codim": vals(lambda r: r["solv"]["4"]["codim"]),
             "solv4_one_in_W": vals(lambda r: r["solv"]["4"]["one_in_W"]),
             "solv4_iterations": vals(lambda r: r["solv"]["4"]["iterations"])}
        for D in ("4", "5"):
            have = [r for r in rs if D in r.get("macaulay", {})]
            s[f"D{D}_measured"] = len(have)
            s[f"D{D}_rank_lt_nrows_all"] = all(r["macaulay"][D]["rank_lt_nrows"] for r in have) if have else None
            s[f"D{D}_nrows_minus_rank"] = [r["macaulay"][D]["nrows_minus_rank"] for r in have]
            s[f"D{D}_deficit"] = [r["macaulay"][D]["deficit"] for r in have]
            s[f"D{D}_rank"] = [r["macaulay"][D]["rank_armA"] for r in have]
            s[f"D{D}_nrows"] = [r["macaulay"][D]["nrows"] for r in have]
        summary.append(s)

    # ---- frozen-condition evaluation
    ok = [r for r in instances if r.get("status") == "ok"]
    dual_fail = []
    for r in instances:
        for D, m in r.get("macaulay", {}).items():
            if not m["dual_agree"]:
                dual_fail.append((r["n"], r["family"], r["seed"], "mac", D))
        for D, s in (r.get("solv") or {}).items():
            if not s["dual_agree"]:
                dual_fail.append((r["n"], r["family"], r["seed"], "solv", D))
    c2 = [(r["n"], r["family"], r["seed"], D, s["c2_disagreements"]) for r in ok for D, s in r["solv"].items() if s.get("c2_disagreements")]
    enum_dis = [(r["n"], r["family"], r["seed"]) for r in ok if not r["enumeration"]["agree"]]
    prim = [r for r in ok if r["family"] in ("planted", "uniform_z", "anchor")]
    dff_low = [(r["n"], r["family"], r["seed"], r["d_ff_ic"]) for r in prim if isinstance(r["d_ff_ic"], int) and r["d_ff_ic"] < 4]
    c3_viol = [(r["n"], r["family"], r["seed"], D) for r in prim for D, m in r.get("macaulay", {}).items() if int(D) >= 4 and not m["rank_lt_nrows"]]
    c3_viol_all = [(r["n"], r["family"], r["seed"], D) for r in instances for D, m in r.get("macaulay", {}).items() if int(D) >= 4 and not m["rank_lt_nrows"]]
    per_n_primary_ok = {n: len([r for r in prim if r["n"] == n]) for n in (12, 15)}
    failed = [(r["n"], r["family"], r["seed"], r.get("status"), r.get("error")) for r in instances if r.get("status") not in ("ok", None)]
    conds = {
        "1_O-BUILDER-MISMATCH": False,  # stage1 PASS (stage1/builder-equality.json)
        "2_O-IMPEDIMENT_stage2_incomplete": not all(v > 0 for v in per_n_primary_ok.values()),
        "3_O-ARTIFACT": {"triggered": bool(dual_fail), "dual_rank_disagreements": dual_fail, "pooling": "none (summaries keyed by n, family, sub-stratum)"},
        "4_O-C2-FALSE": {"triggered": bool(c2 or enum_dis), "c2_disagreements": c2, "enumeration_disagreements": enum_dis},
        "5_O-A1-COST-FAIL": {"triggered": False, "evaluable": False, "reason": "frozen cells (12,3,3,4),(15,3,3,5) are not Semaev Table 1/2 rows"},
        "6_O-DFF-ANOMALY": {"triggered": bool(dff_low), "primary_instances_with_d_ff_ic_lt_4": len(dff_low), "primary_instances": len(prim), "examples": dff_low[:5]},
        "7_O-C3-FALSE": {"triggered": bool(c3_viol), "stage0_target": "nrows (not degree-exactly-D count)", "rank_eq_nrows_primary": c3_viol, "rank_eq_nrows_any_arm": c3_viol_all},
        "8_O-C1-FALSE": {"triggered": False, "evaluable": False, "reason": "Stage 3 impeded (stage3/impediment.json)"},
        "9_O-C1b-FALSE": {"triggered": False, "evaluable": False, "reason": "Stage 3 impeded"},
        "10_O-COINCIDE": {"triggered": False, "evaluable": False, "reason": "d_F4 unmeasured (Stage 3 impeded); measured quantities d_ff_ic, d_solv, rank-vs-nrows are not all equal on primary instances"},
    }
    order = [("1_O-BUILDER-MISMATCH", "O-BUILDER-MISMATCH"), ("2_O-IMPEDIMENT_stage2_incomplete", "O-IMPEDIMENT"),
             ("3_O-ARTIFACT", "O-ARTIFACT"), ("4_O-C2-FALSE", "O-C2-FALSE"), ("5_O-A1-COST-FAIL", "O-A1-COST-FAIL"),
             ("6_O-DFF-ANOMALY", "O-DFF-ANOMALY"), ("7_O-C3-FALSE", "O-C3-FALSE"), ("8_O-C1-FALSE", "O-C1-FALSE"),
             ("9_O-C1b-FALSE", "O-C1b-FALSE"), ("10_O-COINCIDE", "O-COINCIDE")]
    label = "O-SEPARATED"
    for key, lab in order:
        v = conds[key]
        trig = v if isinstance(v, bool) else v["triggered"]
        if trig:
            label = lab
            break
    out = {"schema": "EXP-SEMBIN-79a02d.stage2.census.v1", "experiment_id": "EXP-SEMBIN-79a02d",
           "definitions": "stage0/definitions.md (frozen 2026-10-05T16:48:10Z)",
           "sources": sources, "instance_count": len(instances), "instances_ok": len(ok),
           "failed_or_invalid": failed, "censored_not_started": censored,
           "strata_pooled": False, "summary_by_n_family_substratum": summary,
           "frozen_condition_evaluation": conds, "mechanical_label_by_frozen_precedence": label,
           "instances": instances}
    json.dump(out, open(out_path, "w"), indent=1)
    print(label)
    print(json.dumps({k: (v if isinstance(v, bool) else v.get("triggered")) for k, v in conds.items()}))


if __name__ == "__main__":
    main()
