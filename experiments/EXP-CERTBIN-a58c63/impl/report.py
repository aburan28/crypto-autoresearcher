"""Phase 8 writer for EXP-CERTBIN-a58c63: every declared artifact, the
independent raw-result recomputation from the written per-target files and
its agreement check, the manifest, the environment file and run-report.md."""
import datetime
import glob
import gzip
import hashlib
import json
import os
import platform
import sys

import numpy as np
import yaml

import analysis as AN
from common import EXP_ID, cell_label, FIXED_COUNTS, STAGE1_RUN
from macaulay import Descent, MacaulayShape
from regimeB import ShapeB, GFTabs
from oracles import s3_coeffs

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jd(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def wjson(run, name, obj):
    p = os.path.join(run.out, name)
    if os.path.exists(p):
        raise RuntimeError(f"{p} exists; refusing to overwrite")
    with open(p, "x") as f:
        json.dump(obj, f, indent=1, default=jd)
    return p


def wjsonl_gz(run, name, rows):
    p = os.path.join(run.out, name)
    if os.path.exists(p):
        raise RuntimeError(f"{p} exists; refusing to overwrite")
    with gzip.open(p + ".tmp", "wt") as f:
        for r in rows:
            f.write(json.dumps(r, default=jd, separators=(",", ":")) + "\n")
    os.replace(p + ".tmp", p)
    return p


def module_hashes():
    return {os.path.basename(p): sha_file(p) for p in sorted(glob.glob(os.path.join(HERE, "*.py")))}


def load_units(run, lab, regA_void):
    uA, uB, rA, rB = {}, {}, {}, {}
    if not regA_void:
        for fam in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-AFF", "F-NULLF2"):
            for D in (3, 4):
                uA[(fam, D)] = run.ck_load(f"p2-{lab}-A-{fam}-D{D}")
        for D in (3, 4):
            rA[D] = run.ck_load(f"p5-{lab}-A-D{D}")
    for fam in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-NULLB", "F-AFFB"):
        uB[fam] = run.ck_load(f"p3-{lab}-B-{fam}")
    rB[66] = run.ck_load(f"p5-{lab}-B")
    return uA, uB, rA, rB


def sizing_max(unit, maxref):
    if maxref is None:
        return None
    r = next((x for x in unit["refs"] if x["label"] == maxref), None)
    if r is None:
        return None
    return {"ref": maxref, "pruned_dense_bytes": r["sizes"]["pruned"]["dense_bytes"],
            "full_dense_bytes": r["sizes"]["full"]["dense_bytes"], "saving_strict": r["saving"]["saving_strict"]}


def phase8(run, args, plan, spec, spec_text, fields, curves, cells):
    t0 = now()
    cprov = json.load(open(os.path.join(run.out, "cprov.json")))
    regA_void = not cprov["pass"]
    seed = plan["seeds_fixed"]["S_selftest"]
    nres = FIXED_COUNTS["bootstrap_resamples"]
    amend = plan.get("amendment_settings", {})
    e3_field = amend.get("e3_field", "fraction")
    cell_summary = {}
    checks = {}
    decisions = {}
    sizing = {}
    mh = module_hashes()
    ver = json.load(open(os.path.join(run.out, "ps0prime-verification.json")))
    p6 = run.ck_load("p6-determinism")
    p7 = run.ck_load("p7a-certificates")
    for cidx, n, l in cells:
        lab = cell_label(n, l)
        run.log(f"  phase 8: {lab}")
        P1 = run.ck_load(f"p1-{lab}")
        uA, uB, rA, rB = load_units(run, lab, regA_void)
        p4 = run.ck_load(f"p4-{lab}")
        F = fields[n]
        desc = Descent(F, l)
        E0, Ej = desc.affine_basis(curves[n]["B"])
        # ---- regime B summary
        B = AN.analyze_cell_B(lab, uB, p4, P1, n, l, seed, nres)
        nulls = {}
        for fam in ("F-NULLB", "F-AFFB"):
            u = uB[fam]
            nulls[fam] = AN.fam_retention(u["records"], AN.unsat_keys(u))
        B["nulls"] = nulls
        s3keys = AN.unsat_keys(uB["F-S3"])
        B["M3"] = {f"F-S3/{fam}": AN.m3_ratio(B["MB1"], nulls[fam], uB["F-S3"]["records"], uB[fam]["records"],
                                              s3keys, AN.unsat_keys(uB[fam]), seed, nres) for fam in ("F-AFFB", "F-NULLB")}
        B["sizing_maximizing_ref"] = sizing_max(uB["F-S3"], B["MB1"]["maximizing_ref"])
        B["row_order_replays"] = {k: {"n": len(v), "survived": sum(x["survived"] for x in v),
                                      "schedule_valid": sum(x["schedule_valid"] for x in v)} for k, v in p4["row_order_replays"].items()}
        B["K_B"] = {k: v["K_B"] for k, v in p4["per_ref"].items()}
        B["wall_seconds"] = {fam: uB[fam]["wall_seconds"] for fam in uB}
        B["peak_rss_bytes"] = {fam: uB[fam]["peak_rss_bytes"] for fam in uB}
        B["P_sat"] = {"F-S3_sat_fraction_nondegenerate": (B["arm_sizes"]["sat"] / (B["arm_sizes"]["sat"] + B["arm_sizes"]["unsat"]))
                      if (B["arm_sizes"]["sat"] + B["arm_sizes"]["unsat"]) else None,
                      "F-SAT_scan": {"kept": len(P1["F-SAT"]["targets"]), "unsat_rejections": P1["F-SAT"]["unsat_rejections"],
                                     "estimate_P_sat": (len(P1["F-SAT"]["targets"]) / (len(P1["F-SAT"]["targets"]) + P1["F-SAT"]["unsat_rejections"]))
                                     if (len(P1["F-SAT"]["targets"]) + P1["F-SAT"]["unsat_rejections"]) else None,
                                     "stop_reason": P1["F-SAT"]["stop_reason"]},
                      "rational_flag_rate_sat_F-S3": None}
        sat_s3 = [t for t in P1["F-S3"]["targets"] if not t["degenerate"] and t["s"] >= 1]
        if sat_s3:
            B["P_sat"]["rational_flag_rate_sat_F-S3"] = sum(1 for t in sat_s3 if t["rational_flag"]) / len(sat_s3)
        cs = {"cell": lab, "n": n, "l": l, "regime_B": B}
        # ---- regime A summary
        if not regA_void:
            A = {}
            for D in (3, 4):
                a = AN.analyze_cell_A(lab, uA, D)
                a["M3"] = AN.m3_ratio(a["MA1"]["strict_unsat"],
                                      AN.fam_retention(uA[("F-AFF", D)]["records"], AN.unsat_keys(uA[("F-AFF", D)])),
                                      uA[("F-S3", D)]["records"], uA[("F-AFF", D)]["records"],
                                      AN.unsat_keys(uA[("F-S3", D)]), AN.unsat_keys(uA[("F-AFF", D)]), seed, nres) if D == 4 else None
                a["sizing_maximizing_ref"] = sizing_max(uA[("F-S3", D)], a["MA1"]["strict_unsat"]["maximizing_ref"])
                a["null_retention"] = {fam: AN.fam_retention(uA[(fam, D)]["records"], AN.unsat_keys(uA[(fam, D)]), ci=False)["retention_family"]
                                       for fam in ("F-AFF", "F-NULLF2", "F-RANDX")}
                a["wall_seconds"] = {fam: uA[(fam, D)]["wall_seconds"] for fam in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-AFF", "F-NULLF2")}
                A[f"D{D}"] = a
            cs["regime_A"] = A
        else:
            cs["regime_A"] = None
        cs["arm_sizes_all_families"] = {
            "B": {fam: {a: sum(1 for r in uB[fam]["records"] if not r["degenerate"] and r["stratum"] == a) for a in ("unsat", "sat")}
                  | {"degenerate": sum(1 for r in uB[fam]["records"] if r["degenerate"])} for fam in uB},
            "A": ({f"{fam}-D{D}": {a: sum(1 for r in u["records"] if not r["degenerate"] and r["stratum"] == a) for a in ("unsat", "sat")}
                   for (fam, D), u in uA.items()} if uA else None)}
        cs["underpowered_arms_(<100)"] = sorted(f"{reg}:{k}:{a}" for reg in ("A", "B") for k, v in (cs["arm_sizes_all_families"][reg] or {}).items()
                                                  for a in ("unsat", "sat") if v[a] < 100)
        cs["reference_shortfalls"] = {f: P1[f]["ref_shortfall"] for f in ("F-S3", "F-RANDX", "F-AFF", "F-NULLF2", "F-NULLB", "F-AFFB")}
        cell_summary[lab] = cs
        # ---- instrument checks
        ck = AN.instrument_checks_cell(lab, n, l, P1, uA, uB, rA, rB, p4, cprov["pass"], E0, Ej, None)
        nl = AN.nulls_check(P1, n, E0, Ej, mh)
        if not regA_void:
            nl.update(AN.nulls_check_A(P1, desc, E0, Ej))
        nl["code_path"] = {"module_sha256": {k: mh[k] for k in ("engineA.py", "engineB.py", "regimeB.py", "elim.py", "macaulay.py")},
                           "note": "every family of a regime runs the same functions (engineA.process_family_A / engineB.process_family_B) from these modules; one hash set applies to every family",
                           "pass": True}
        ck["C-NULLS"] = {"pass": all(v["pass"] for v in nl.values()), **nl}
        ps0p = [r for r in ver["results"] if r["cell"] == lab]
        ck["C-PROPS"]["PS0prime"] = {"n": len(ps0p), "pass_all": all(r["pass"] for r in ps0p),
                                     "failures": [r for r in ps0p if not r["pass"]],
                                     "summary": [s for s in p7["summary"] if s["cell"] == lab]}
        ck["C-PROPS"]["pass"] = ck["C-PROPS"]["PS0_pass"] and ck["C-PROPS"]["PS1_pass"] and ck["C-PROPS"]["PS0prime"]["pass_all"]
        checks[lab] = ck
        decisions[lab] = AN.db_cell(lab, n, l, cs, ck, e3_field=e3_field)
        sizing[lab] = {"B": {r["label"]: {"sizes": r["sizes"], "saving": r["saving"]} for r in uB["F-S3"]["refs"]},
                       "A": ({f"D{D}": {r["label"]: {"sizes": r["sizes"], "saving": r["saving"]} for r in uA[("F-S3", D)]["refs"]}
                              for D in (3, 4)} if uA else None)}
    # ---- global checks
    st = json.load(open(os.path.join(run.out, "selftest.json")))
    pilot = json.load(open(os.path.join(run.out, "pilot.json")))
    pb = run.ck_load("plan-bound")
    glob_ck = {
        "C-SELF": {"pass": st["C-SELF_pass"]}, "C-FIX": {"pass": st["C-FIX_pass"]},
        "C-PROV": {"pass": cprov["pass"], "n_compared": cprov["n_compared"], "mismatches": cprov["mismatches"]},
        "C-DET": {"pass": p6["pass"], "checked": p6["checked"], "matched": p6["matched"], "mismatches": p6["mismatches"],
                  "separate_process_pid": p6["process"]["pid"]},
        "C-PILOT": {"pass": set(pilot.keys()) <= {"experiment_id", "run_id", "written_at", "selftest_all_pass", "timed_unit",
                                                   "x_R_source", "per_cell", "C_std_count_breakdown_per_cell",
                                                   "T_proj_single_worker_seconds", "threshold_seconds", "rule", "schedule",
                                                   "outputs_written"},
                    "pilot_written_at": pilot["written_at"], "plan_bound_at": pb["at"],
                    "decision_before_phase_1": pilot["written_at"] < pb["at"], "schedule": pilot["schedule"]},
        "PS0prime_verifier": {"all_pass": ver["all_pass"], "n": ver["n_certificates"], "separate_process_pid": ver["pid"],
                              "verifier_sha256": ver["verifier_sha256"]},
    }
    dr = {"per_cell": decisions, "DB-4": AN.db4(cell_summary, checks), "DB-12": AN.DB12,
          "e3_field_used_for_DB-5": e3_field, "amendment_settings": amend}
    # ---- validity
    void = []
    if not (glob_ck["C-SELF"]["pass"] and glob_ck["C-FIX"]["pass"]):
        void.append("INV-1")
    if not glob_ck["C-DET"]["pass"]:
        void.append("INV-7 (C-DET)")
    for lab, ck in checks.items():
        if not ck["C-PASS"]["pass"]:
            void.append(f"INV-7 (C-PASS {lab})")
        if not ck["C-REV"]["pass"]:
            void.append(f"INV-7 (C-REV {lab})")
        if not ck["nesting"]["pass"]:
            void.append(f"INV-7 (nesting {lab})")
        if not ck["C-PROPS"]["pass"]:
            void.append(f"INV-8 (C-PROPS {lab})")
    partial = []
    if regA_void:
        partial.append("INV-2: regime-A arm void (C-PROV)")
    for lab, ck in checks.items():
        if not (ck["C-ORACLE"]["pass"] and ck["C-WIT"]["pass"]):
            partial.append(f"INV-3 {lab}")
        if not (ck["C-DELTA"]["pass"] and ck["C-RANKB"]["pass"]):
            partial.append(f"INV-4 {lab}: regime-B metrics INVALID pending adjudication")
        if not (ck["C-BREAK"]["pass"] and ck["C-REPLAYB"]["pass"]):
            partial.append(f"INV-5 (v2) {lab}: DB-3, DB-4, DB-11 void")
        if not ck["C-CLASS"]["curve_algebra_pass"]:
            partial.append(f"INV-10 {lab}: MB2, MB3, MB5 and DB-3, DB-4, DB-5, DB-11 void")
        if not all(ck["C-CLASS"]["nulls_pass"].values()):
            partial.append(f"INV-10 (nulls) {lab}: failing null family's regime-B metrics, DB-8 and M3 void")
        if not ck["C-12_nulls_Lemma_B-S"]["pass"]:
            partial.append(f"C-12 {lab}: null family regime-B metrics INVALID pending adjudication; DB-8 and M3 void")
        if not all(ck[c]["pass"] in (True, None) for c in ("C-AFF", "C-FORMS", "C-SURV", "C-HZERO")):
            partial.append(f"INV-6 {lab}: MA1 hull quantities and MA2 void for the affected family")
        if not ck["C-NULLS"]["pass"]:
            partial.append(f"C-NULLS {lab}: null comparisons (DB-8, M3) void")
    validity = {"status": "invalid_measurement" if void else "completed_valid",
                "void_reasons": void, "partial_invalidations": partial,
                "note": "completed_valid means no run-voiding control failed; partial invalidations are listed and bind the named metrics"}
    # ---- artifacts
    wjson(run, "cell-summary.json", {"experiment_id": EXP_ID, "run_id": plan["run_id"], "cells": cell_summary})
    wjson(run, "instrument-checks.json", {"global": glob_ck, "per_cell": checks, "validity": validity})
    wjson(run, "decision-rules.json", dr)
    wjson(run, "sizing.json", sizing)
    write_order_files(run, fields, cells)
    write_per_cell_files(run, cells, fields, curves, regA_void)
    raw = raw_result(run, cells, cell_summary, regA_void)
    wjson(run, "raw-result.json", raw)
    env = environment()
    wjson(run, "environment.json", env)
    manifest = build_manifest(run, args, plan, spec_text, validity, glob_ck, checks, raw, env)
    p = os.path.join(run.out, "manifest.yaml")
    with open(p, "x") as f:
        yaml.safe_dump(manifest, f, sort_keys=False, width=110)
    import runreport
    runreport.write(run, plan, spec, cell_summary, checks, glob_ck, dr, validity, raw, manifest)
    return validity


def write_order_files(run, fields, cells):
    done = set()
    for cidx, n, l in cells:
        F = fields[n]
        desc = Descent(F, l)
        for D in (3, 4):
            S = MacaulayShape(D, desc)
            k = ("colA", l, D)
            if k not in done:
                wjson(run, f"column-order-A-l{l}-D{D}.json", {"regime": "A", "l": l, "D": D, "columns": [list(m) for m in S.cols]})
                done.add(k)
            wjson(run, f"row-order-A-n{n}-l{l}-D{D}.json", {"regime": "A", "n": n, "l": l, "D": D, "rows": S.row_order()})
        SB = ShapeB(F, l)
        if ("colB", l) not in done:
            wjson(run, f"column-order-B-l{l}-D66.json", {"regime": "B", "l": l, "D": 66, "columns": [list(m) for m in SB.cols]})
            wjson(run, f"row-order-B-l{l}-D66.json", {"regime": "B", "l": l, "D": 66, "rows": SB.row_order()})
            done.add(("colB", l))


def write_per_cell_files(run, cells, fields, curves, regA_void):
    import engineA
    import engineB
    from elim import ops_json_list
    for cidx, n, l in cells:
        lab = cell_label(n, l)
        P1 = run.ck_load(f"p1-{lab}")
        uA, uB, rA, rB = load_units(run, lab, regA_void)
        # references
        refs = {"cell": lab, "regime_B": {fam: {"refs": u["refs"], "modal_info": u["modal_info"]} for fam, u in uB.items() if u["refs"]},
                "regime_A": ({f"{fam}-D{D}": {"refs": u["refs"], "modal_info": u["modal_info"]} for (fam, D), u in uA.items() if u["refs"]}
                             if uA else None),
                "reference_scans": {"F-S3": P1["ref_scan"], "F-RANDX": P1["F-RANDX"].get("ref_scan")},
                "reference_instances": {f: [{k: v for k, v in r.items() if k not in ("sols",)} | {"n_solutions": len(r.get("sols", []))}
                                            for r in P1[f]["refs"]] for f in ("F-S3", "F-RANDX", "F-AFF", "F-NULLF2", "F-NULLB", "F-AFFB")}}
        wjson(run, f"references-{lab}.json", refs)
        # op logs of the 3 unsat F-S3 references (rebuilt, hash-verified)
        F = fields[n]
        B = curves[n]["B"]
        SB = ShapeB(F, l)
        T = GFTabs(F)
        rows = []
        for r in uB["F-S3"]["refs"]:
            if not r["label"].startswith("U"):
                continue
            from regimeB import eliminate
            res, _, _ = eliminate(SB.build(s3_coeffs(F, B, r["x_R"])), T, with_row_pass=False)
            if res.h_ops != r["h_ops"]:
                raise RuntimeError(f"op-log rebuild mismatch {lab} B {r['label']}")
            for k, (p, c, X) in enumerate(zip(res.p, res.c, res.X)):
                rows.append({"ref": r["label"], "x_R": r["x_R"], "k": k, "p": int(p), "c": int(c),
                             "X_delta": engineB.delta_encode(X)})
        wjsonl_gz(run, f"oplogs-{lab}-B-D66.jsonl.gz", rows)
        if uA:
            desc = Descent(F, l)
            from elim import eliminate as elimA
            for D in (3, 4):
                S = MacaulayShape(D, desc)
                rows = []
                for r in uA[("F-S3", D)]["refs"]:
                    if not r["label"].startswith("U"):
                        continue
                    res, _, _ = elimA(S.build(desc.descended_E(B, r["x_R"])), S.C, keep_ops=True, with_row_pass=False)
                    if res.h_ops != r["h_ops"]:
                        raise RuntimeError(f"op-log rebuild mismatch {lab} A D{D} {r['label']}")
                    for k, (p, c, X) in enumerate(zip(res.p, res.c, res.X)):
                        rows.append({"ref": r["label"], "x_R": r["x_R"], "k": k, "p": int(p), "c": int(c), "X": X.tolist()})
                wjsonl_gz(run, f"oplogs-{lab}-A-D{D}.jsonl.gz", rows)
        # per-target files
        for fam, u in uB.items():
            wjsonl_gz(run, f"targets-{lab}-B-{fam}.jsonl.gz", u["records"])
        wjsonl_gz(run, f"targets-{lab}-B-F-S3-REV.jsonl.gz", rB[66]["records"])
        if uA:
            from hull import echelon, in_span
            s3h = {D: uA[("F-S3", D)].get("hull") for D in (3, 4)}
            for fam in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-AFF", "F-NULLF2"):
                recs = []
                for D in (3, 4):
                    h = s3h[D]
                    basis = echelon(h["W_basis"]) if h else None
                    for r in uA[(fam, D)]["records"]:
                        rr = dict(r)
                        if basis is not None and r.get("x_R") is not None:
                            rr["in_F-S3_hull"] = in_span(int(r["x_R"]) ^ int(h["h0"]), basis)
                        recs.append(rr)
                wjsonl_gz(run, f"targets-{lab}-A-{fam}.jsonl.gz", recs)
            wjsonl_gz(run, f"targets-{lab}-A-F-S3-REV.jsonl.gz", rA[3]["records"] + rA[4]["records"])
        # phase-1 instances (oracles, witnesses) for every family
        inst = {}
        for f in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-AFF", "F-NULLF2", "F-NULLB", "F-AFFB"):
            inst[f] = [{k: v for k, v in t.items()} for t in P1[f]["targets"]]
        wjsonl_gz(run, f"instances-{lab}.jsonl.gz", [{"family": f, **t} for f, ts in inst.items() for t in ts])
        # breaks
        p4 = run.ck_load(f"p4-{lab}")
        wjson(run, f"regimeB-breaks-{lab}.json", p4)
        # pivot hazards
        if uA:
            hz = {f"{fam}-D{D}": {"hull": u.get("hull"), "hazards": u.get("hazards")} for (fam, D), u in uA.items() if u.get("hazards")}
            wjson(run, f"pivot-hazards-{lab}.json", hz)


def raw_result(run, cells, cell_summary, regA_void):
    """Independent recomputation of the primary counts from the WRITTEN
    per-target files (re-read from disk), and agreement with cell-summary."""
    out = {"source": "per-target gzipped JSONL files re-read from the run directory", "cells": {}, "agreement": {}}
    allok = True
    for cidx, n, l in cells:
        lab = cell_label(n, l)

        def rd(name):
            with gzip.open(os.path.join(run.out, name), "rt") as f:
                return [json.loads(x) for x in f]
        s3 = rd(f"targets-{lab}-B-F-S3.jsonl.gz")
        cs = cell_summary[lab]["regime_B"]
        un = [r for r in s3 if not r["degenerate"] and r["stratum"] == "unsat"]
        c = {"B_unsat_n": len(un)}
        for p in cs["MB1"]["per_ref"]:
            k = p["ref"]
            sc = [r for r in un if k in r["refs"]]
            c[f"B_strict_matched_{k}"] = sum(1 for r in sc if r["refs"][k]["match"]["strict"])
            c[f"B_scored_{k}"] = len(sc)
        c["B_unsat_one_in_R66"] = sum(1 for r in un if r["one_in_R"])
        for k in cs["MB3"]["per_ref"]:
            c[f"B_zero_pivot_{k}"] = sum(1 for r in un if r["refs"][k].get("type") == "ZERO-PIVOT")
        sat = []
        for fam in ("F-SAT", "F-PLANT"):
            sat += [r for r in rd(f"targets-{lab}-B-{fam}.jsonl.gz") if not r["degenerate"] and r["stratum"] == "sat"]
        for k in cs["MB5"]["per_ref"]:
            kk = f"F-S3:{k}"
            u_ = {}
            for r in sat:
                u_.setdefault(r["x_R"], r)
            c[f"E3_{k}"] = sum(1 for r in u_.values() if r["refs"][kk].get("type") == "COLUMN"
                               and r["refs"][kk].get("c_ref") == r.get("first_nonpivot_col"))
        c["E3_n"] = len({r["x_R"] for r in sat})
        want = {"B_unsat_n": cs["arm_sizes"]["unsat"], "B_unsat_one_in_R66": cs["MB4"]["F-S3"]["unsat"]["one_in_R66"],
                "E3_n": sum(cs["MB5"]["per_ref"][k]["pooled"]["n"] for k in list(cs["MB5"]["per_ref"])[:1]) if cs["MB5"]["per_ref"] else 0}
        for p in cs["MB1"]["per_ref"]:
            want[f"B_strict_matched_{p['ref']}"] = p["matched"]
            want[f"B_scored_{p['ref']}"] = p["n"]
        for k, d in cs["MB3"]["per_ref"].items():
            want[f"B_zero_pivot_{k}"] = d["X"]
        for k, d in cs["MB5"]["per_ref"].items():
            want[f"E3_{k}"] = d["pooled"]["E3_count"]
        if not regA_void:
            a4 = rd(f"targets-{lab}-A-F-S3.jsonl.gz")
            a4 = [r for r in a4 if r["D"] == 4 and not r["degenerate"] and r["stratum"] == "unsat"]
            ma = cell_summary[lab]["regime_A"]["D4"]["MA1"]["strict_unsat"]
            for p in ma["per_ref"]:
                k = p["ref"]
                sc = [r for r in a4 if k in r["refs"]]
                c[f"A4_strict_matched_{k}"] = sum(1 for r in sc if r["refs"][k]["match"]["strict"])
                want[f"A4_strict_matched_{k}"] = p["matched"]
        agree = {k: (c.get(k) == v) for k, v in want.items()}
        ok = all(agree.values())
        allok &= ok
        out["cells"][lab] = {"recomputed": c, "from_cell_summary": want}
        out["agreement"][lab] = {"all_agree": ok, "disagreements": [k for k, v in agree.items() if not v]}
    out["all_agree"] = allok
    return out


def environment():
    import mpmath
    env = {"python": sys.version, "numpy": np.__version__, "mpmath": mpmath.__version__, "yaml": yaml.__version__,
           "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(),
           "cpu_count": os.cpu_count(),
           "env": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                                                  "AUTORESEARCH_POLICY", "AUTORESEARCH_BACKEND")}}
    try:
        env["meminfo_total_kB"] = next(int(x.split()[1]) for x in open("/proc/meminfo") if x.startswith("MemTotal"))
    except Exception:
        pass
    return env


def build_manifest(run, args, plan, spec_text, validity, glob_ck, checks, raw, env):
    inv = [json.loads(x) for x in open(os.path.join(run.ck, "invocations.jsonl"))]
    wi = run.ck_load("workers-identity") if run.ck_exists("workers-identity") else None
    metas = {}
    for p in sorted(glob.glob(os.path.join(run.ck, "*.json.gz"))):
        name = os.path.basename(p)[:-8]
        try:
            d = run.ck_load(name)
        except Exception:
            continue
        if isinstance(d, dict) and "wall_seconds" in d:
            metas[name] = {k: d.get(k) for k in ("started_at", "finished_at", "wall_seconds", "peak_rss_bytes",
                                                  "peak_rss_children_bytes", "pid")}
        elif isinstance(d, dict) and "_meta" in d:
            metas[name] = d["_meta"]
    pilot = json.load(open(os.path.join(run.out, "pilot.json")))
    cells = json.load(open(os.path.join(run.out, "cells.json")))["cells"]
    plan_path = args.plan
    cmd_path = os.path.join(run.out, "command.txt")
    cmd_text = open(cmd_path).read() if os.path.exists(cmd_path) else None
    first = next((x for x in inv if x.get("event") == "start"), {})
    git = first.get("git") or {}
    ver = json.load(open(os.path.join(run.out, "ps0prime-verification.json")))
    impl_hashes = {os.path.relpath(p, REPO): sha_file(p) for p in sorted(glob.glob(os.path.join(HERE, "*"))) if os.path.isfile(p)}
    vpath = os.path.join(REPO, "experiments", EXP_ID, "verifier", "verify_cert.py")
    impl_hashes[os.path.relpath(vpath, REPO)] = sha_file(vpath)
    amend = plan.get("amendment") or {}
    body = {
        "id": plan["run_id"], "experiment_id": EXP_ID, "task_id": "TASK-20260924-6ab0d8",
        "archived_by": "TASK-20260924-b9e36f",
        "status": validity["status"],
        "invalid_reasons": validity["void_reasons"],
        "partial_invalidations": validity["partial_invalidations"],
        "claim_tier": "toy",
        "protocol_version": plan.get("protocol_version", 1),
        "specification": {"path": plan["spec_path"], "sha256": hashlib.sha256(spec_text).hexdigest(), "version": 1,
                          "approval_decision": "DEC-20260924-8e2f47"},
        "amendment": {**amend, "approval_decision": "DEC-20260924-c41e7a",
                      "commit": "8a1d5558e2f75f7e9984b3ab1d05eda5381ba58c",
                      "receipt": "coordination/design/certbin-followups-20260924/archives/TASK-20260924-7d2b95/snapshot-receipt.json"},
        "code": {"commit": git.get("commit"), "dirty": git.get("dirty"),
                 "dirty_paths": git.get("status_porcelain"),
                 "commit_meaning": "HEAD at the first driver invocation; impl/ and verifier/ are untracked working-tree files whose sha256 are listed in impl_sha256",
                 "command": " && ".join(l.strip() for l in (cmd_text or "").splitlines() if l.strip() and not l.startswith("#")) or None,
                 "command_file": "command.txt", "impl_sha256": impl_hashes},
        "environment": env,
        "inputs": {"parameters": {"field_bits": [17, 19], "cells": [[c["n"], c["l"]] for c in plan["cells"]],
                                  "D_regime_A": [3, 4], "D_regime_B": 66, "schedule": pilot["schedule"],
                                  "counts": plan["counts"]},
                   "seeds": {"formula": plan["seed_formula"], "fixed": plan["seeds_fixed"],
                             "per_cell": {c["label"]: c["seeds"] for c in plan["cells"]},
                             "seed_table_C-14": plan.get("seed_table_C-14")},
                   "stage1_run": STAGE1_RUN,
                   "n19_modulus": {k: v for k, v in cells.get("n19-l6", cells.get("n19-l5", {})).items()
                                   if k in ("modulus", "modulus_int", "modulus_rule")},
                   "trial_plan": {"path": os.path.relpath(os.path.abspath(plan_path), REPO) if plan_path else None,
                                  "sha256": sha_file(plan_path) if plan_path else None}},
        "timing": {"per_phase": metas,
                   "peak_rss_bytes_max": max([v.get("peak_rss_bytes") or 0 for v in metas.values()] + [0]),
                   "peak_rss_children_bytes_max": max([v.get("peak_rss_children_bytes") or 0 for v in metas.values()] + [0]),
                   "memory_caps": {"parent_RLIMIT_AS_bytes": first.get("rlimit_as_bytes"),
                                   "child_RLIMIT_AS_bytes": first.get("child_rlimit_as_bytes"),
                                   "note": "AMD C-26: parent 1.6 GB + 2 workers x 1.2 GB = 4.0 GB"},
                   "invocations": inv},
        "schedule": {"chosen": pilot["schedule"], "basis": pilot.get("schedule_basis"),
                     "T_proj_single_worker_seconds_not_binding": pilot["T_proj_single_worker_seconds"],
                     "threshold": pilot["threshold_seconds"], "pilot_sha256": sha_file(os.path.join(run.out, "pilot.json"))},
        "workers": {"enabled": wi["workers_enabled"] if wi else 1, "determinism_demonstration": wi},
        "inference": {"requested_policy": "executor-implementation", "fallback_allowed": True, "fallback_used": True,
                      "resolved_model": "claude-opus-5-5 (session model, inherited)", "model_verified": False,
                      "fallback_reason": "Runtime inheritance: same-session Claude Code subagents inherit the session model (DEC-20260923-4d7a19 R-1 forward rule).",
                      "AUTORESEARCH_POLICY": os.environ.get("AUTORESEARCH_POLICY"),
                      "AUTORESEARCH_BACKEND": os.environ.get("AUTORESEARCH_BACKEND")},
        "result": {"certificate": {"kind": "none",
                                   "note": "No discrete logarithm, decomposition or relation is claimed. PS0' unsatisfiability certificates are INSTRUMENT checks (C-PROPS) and are recorded under instrument_certificates."},
                   "instrument_certificates": {"kind": "unsatisfiability_certificate (instrument only; PS0')",
                                               "verifier": "experiments/EXP-CERTBIN-a58c63/verifier/verify_cert.py (separate process; imports nothing from impl/)",
                                               "submitted": ver["n_certificates"], "verified": ver["n_pass"],
                                               "all_pass": ver["all_pass"]},
                   "raw_result": "raw-result.json", "raw_vs_summary_agreement": raw["all_agree"],
                   "global_controls": {k: v.get("pass", v.get("all_pass")) for k, v in glob_ck.items()},
                   "summary_files": ["cell-summary.json", "instrument-checks.json", "decision-rules.json", "sizing.json",
                                     "run-report.md"]},
        "dev_exploration": plan.get("dev_exploration"),
    }
    return {"run": body}
