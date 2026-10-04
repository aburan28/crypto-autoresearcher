"""Phase 7: instrument checks, metrics MR19-1..3 and secondaries, the
mechanical decision rules N19-DR-1..10, raw-result / cell-summary agreement,
and the run report. Observations only: no verdict on any hypothesis."""
from __future__ import annotations

import json
import math
import os
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

import common as C
import stats as ST

ARMS = ["S3-U400", "S3-SAT100", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"]


def jl(path):
    return json.loads(Path(path).read_text())


def cp(k, n):
    c = ST.cp95(k, n)
    return None if c is None else {"k": k, "n": n, "rate": k / n if n else None, "cp95": [c[0], c[1]],
                                   "cp95_str": [c[2], c[3]]}


def overlap(a, b):
    return a is not None and b is not None and not (a["cp95"][1] < b["cp95"][0] or b["cp95"][1] < a["cp95"][0])


def phase7(R):
    out = R.out
    inst = C.read_jsonl_gz(out / "instances.jsonl.gz")
    clos = {r["key"]: r for r in C.read_jsonl_gz(out / "closures.jsonl.gz")}
    certv = jl(out / "certificate-verification.json")
    annv = jl(out / "annihilator-verification.json")
    ncv = jl(out / "negative-controls-verification.json")
    consv = jl(out / "construction-verification.json")
    drawv = jl(out / "draw-replay-verification.json")
    det = jl(out / "determinism.json")
    back = jl(out / "backend-check.json")
    lit = jl(out / "literal-check.json")
    self_ = jl(out / "selftest.json")
    s17 = jl(out / "slice17.json")
    ep = jl(out / "engine-provenance" / "engine-provenance.json")
    inputs = jl(out / "inputs.json")
    support = jl(out / "support.json")
    p0, p1, p2, p3, p4 = (R.load(n) for n in ("phase0", "phase1", "phase2", "phase3", "phase4"))
    p4post = R.load("phase4-post")
    na = jl(out / "annihilators-nonarchived.json")

    # ---- verified certificate lookup ------------------------------------------
    vc = {}
    for c in certv["results"]:
        vc.setdefault((c["key"], c["closure"]), []).append(c)

    def verified(key, closure, fmt=None):
        return any(c["valid"] and c.get("counts") and (fmt is None or c["format"] == fmt)
                   for c in vc.get((key, closure), []))

    annok = {a["key"]: a["valid"] for a in annv["results"]}

    # ---- per-system raw results ---------------------------------------------------
    raw = []
    for r in inst:
        k = r["key"]
        c = clos[k]
        und = c.get("label") == "UNDETERMINED(budget)"
        row = {"key": k, "arm": r["arm"], "role": r["role"], "s": r["s"], "x_R": r.get("x_R"),
               "stratum": r.get("stratum"), "family": r.get("family"), "slot": r.get("slot"),
               "undetermined": und}
        if not und:
            row.update({
                "M_3_one": c["M_3"]["one"], "M_4_one": c["M_4"]["one"], "W_4_one": c["W_4"]["one"],
                "M_3_verified": verified(k, "M_3"), "M_4_verified": verified(k, "M_4", "flat-v1"),
                "W_4_verified_wdag": verified(k, "W_4", "wdag-v1"),
                "W_4_engine_flat_counts": verified(k, "W_4", "flat-v1"),
                "M_4_rank": c["M_4"]["rank"], "M_4_dims_by_deg": c["M_4"]["dims_by_deg"],
                "M_3_rank": c["M_3"]["rank"], "W_4_final_dim": c["W_4"]["final_dim"],
                "W_4_iterations": c["W_4"]["iterations_to_fixpoint"],
                "W_4_one_first_iteration": c["W_4"]["one_first_iteration"],
                "W_4_dims_by_deg": c["W_4"]["dims_by_deg"], "derived": c["derived"],
                "ell_route": c.get("ell_route"),
                "rc_b_label": c["rc_b"].get("label"), "kernel_dim": c["rc_b"].get("kernel_dim"),
                "sigma": c["rc_b"].get("sigma"), "R4_dims_by_deg": (c["rc_b"].get("R4") or {}).get("dims_by_deg"),
                "R3_rank": c["rc_b"].get("R3_rank"), "T5_applicable": c["rc_b"].get("T5_applicable"),
                "ann_verified": annok.get(k)})
            row["W_4_uncertified"] = bool(row["W_4_one"] and not row["W_4_verified_wdag"])
        raw.append(row)
    rawby = {x["key"]: x for x in raw}

    def arm_rows(arm, role="unsat", stratum=None, family=None):
        return [x for x in raw if x["arm"] == arm and x["role"] == role
                and (stratum is None or x["stratum"] == stratum) and (family is None or x["family"] == family)]

    # ---- instrument checks ------------------------------------------------------------
    ic = {}

    def put(cid, status, **kw):
        ic[cid] = {"status": status, **kw}

    ep_t = ep.get("finished_utc")
    draw_mt = {f: os.path.getmtime(out / f) for f in
               ["draws-S3-PRIMARY.jsonl.gz", "draws-N-CONV19.jsonl.gz", "draws-N-ELL19.jsonl.gz",
                "draws-N-F219.jsonl.gz", "draws-N-AFF19.jsonl.gz", "draws-F-RANDX19.jsonl.gz"]}
    ep_mt = os.path.getmtime(out / "engine-provenance" / "engine-provenance.json")
    put("C-ENGINE", "pass" if ep["pass"] and all(t > ep_mt for t in draw_mt.values()) else "fail",
        items={k: v.get("pass") for k, v in ep["items"].items()}, engine_record_finished_utc=ep_t,
        draw_files_after_engine_record=all(t > ep_mt for t in draw_mt.values()))
    put("C-SRC", "pass" if inputs["pass"] else "fail",
        files=[{k: f[k] for k in ("path", "status", "governing")} for f in inputs["files"]])
    put("C-SEED", "pass" if self_["items"]["C-SEED"]["pass"] else "fail",
        other_occurrences=self_["items"]["C-SEED"]["other_occurrences"])
    put("C-SELF", "pass" if self_["controls"]["C-SELF"] else "fail",
        items={k: v["pass"] for k, v in self_["items"].items() if k.startswith("C-SELF")})
    put("C-FIX", "pass" if self_["controls"]["C-FIX"] else "fail", dims=self_["items"]["C-FIX"]["dims"])
    put("C-CURVE", "pass" if self_["controls"]["C-CURVE"] else "fail")
    put("C-ELL0", "pass" if self_["controls"]["C-ELL0"] else "fail", tau=self_["items"]["C-ELL0"]["tau"],
        coordinator_reading_true=self_["items"]["C-ELL0"]["equals_coordinator_reading"])
    put("C-SLICE17", "pass" if s17["pass"] else "fail")
    ch2 = p2["checks"]
    tr = ch2["S3-PRIMARY"]["tr19_violations"] + ch2["S3-PRIMARY"]["qR_not_O"] + ch2["F-RANDX19"]["tr19_violations"]
    tr_v = drawv.get("randx_tr19_violations_verifier", [])
    put("C-TR19", "pass" if not tr and not tr_v else "fail", violations=tr, verifier_violations=tr_v)
    ell_bad = p4["checks"]["C-ELL"]
    put("C-ELL", "pass" if not ell_bad else "fail", violating=ell_bad)
    aff = ch2["S3-PRIMARY"]["aff_violations"] + ch2["F-RANDX19"]["aff_violations"]
    put("C-AFF19", "pass" if not aff else "fail", violating=aff)
    outside = ch2["support_outside_U"]
    put("C-SUPPORT", "pass" if not (outside["N-ELL19"] or outside["N-F219"]) else "fail",
        outside_U=outside, coordinator_reading_object_parts=
        bool(support["coordinator_reading_object_parts_true_on_S3_primary_kept"] and ch2["coordinator_reading_F-RANDX19"]),
        note="a false Coordinator reading is recorded, never a failure")
    orc = ch2["S3-PRIMARY"]["oracle_disagreements"] + ch2["F-RANDX19"]["oracle_disagreements"]
    put("C-ORACLE", "pass" if not orc else "fail", disagreements=orc)
    put("C-ORACLE2", "pass" if consv["C-ORACLE2_pass"] else "fail",
        s_mismatch=consv["s_mismatch"], solution_failures=consv["solution_failures"])
    put("C-DRAW", "pass" if drawv["pass"] else "fail", per_arm=drawv["per_arm"], draw_logs=drawv["draw_logs"])
    put("C-TOP19", "pass" if not p4["checks"]["C-TOP19"] else "fail", violating=p4["checks"]["C-TOP19"],
        slots_compared=len(p4["top19"]))
    t4n = sum(1 for c in clos.values() if c.get("T4", {}).get("applicable"))
    put("C-T4", "pass" if not p4["checks"]["C-T4"] else "fail", violating=p4["checks"]["C-T4"], systems_checked=t4n)
    pe = p4["pred_eval"]
    put("C-PRED", "pass" if not p4["checks"]["C-PRED"] else "fail", violating=p4["checks"]["C-PRED"],
        applicable=sum(1 for x in pe if x["ok"] is not None), not_applicable=sum(1 for x in pe if x["ok"] is None),
        predictions_sha256=p3["predictions_sha256"], predictions_written_utc=p3["predictions_written_utc"])
    put("C-WDAG", "pass" if not p4["checks"]["C-WDAG"] else "fail", dimension_mismatches=p4["checks"]["C-WDAG"],
        uncertified=[x["key"] for x in raw if x.get("W_4_uncertified")])
    put("C-MONO", "pass" if not p4["checks"]["C-MONO"] else "fail", violating=p4["checks"]["C-MONO"])
    ps_bad = p4["checks"]["C-PS"]
    put("C-PS", "pass" if not ps_bad else "fail", violating=ps_bad)
    put("C-CERT", "pass" if certv["C-CERT_pass"] else "fail",
        failed=[{"key": c["key"], "closure": c["closure"], "format": c["format"], "reasons": c["reasons"]}
                for c in certv["results"] if not c["valid"]])
    s3nr = [x["key"] for x in arm_rows("S3-U400") if not x["undetermined"] and not x["W_4_one"]]
    if not s3nr:
        put("C-NONREF", "vacuous", reason="W_4 refutes all of S3-U400 (declared, not cited as passed)",
            controls_checked=sum(1 for a in annv["results"] if not a["key"].startswith("S3-U400")),
            controls_failed=[a["key"] for a in annv["results"] if not a["valid"]])
    else:
        miss = [k for k in s3nr if annok.get(k) is not True]
        ctl_bad = [a["key"] for a in annv["results"] if not a["valid"]]
        put("C-NONREF", "pass" if not miss and not ctl_bad else "fail", S3_nonrefuted=len(s3nr),
            S3_without_verified_ann=miss, failed=ctl_bad)
    # C-VERIFIER: every negative rejected; each kind has >= 3 of each type or declared vacuous; V1 agreement
    plan = p4["negative_controls_plan"]
    short = {}
    for kind, pk in plan.items():
        for typ, v in pk["types"].items():
            if isinstance(v, int) and v < 3:
                short[f"{kind}:{typ}"] = v
    put("C-VERIFIER", "pass" if (ncv["C-VERIFIER_negatives_pass"] and not short and consv["V1_construction_pass"])
        else "fail", accepted_negatives=ncv["accepted"], kinds=plan, types_below_3=short,
        construction_agreement=consv["V1_construction_pass"], E_mismatch=consv["E_mismatch"])
    put("C-BACKEND", "pass" if back.get("pass") else "fail",
        differences=[r for r in back.get("results", []) if r["differences"]], systems=back.get("systems"))
    put("C-LIT", "pass" if lit.get("pass") else "fail",
        differences=[r for r in lit.get("results", []) if r["differences"]], systems=lit.get("systems"))
    put("C-DET", "pass" if det.get("pass") else "fail", a=det["a"]["pass"], b=det["b"]["pass"], c=det["c"]["pass"])
    mods = [p0["impl_module_sha256"], p1["impl_module_sha256"], p2["impl_module_sha256"], p3["impl_module_sha256"],
            p4["impl_module_sha256"]]
    same = all(m == mods[0] for m in mods)
    put("C-NULLS", "pass" if same else "fail", impl_module_sha256_per_phase=mods,
        note="every arm is processed by the same process and the same functions (process_system for closures); "
             "module hashes recorded at each phase are identical across phases and therefore across arms")
    failed = [k for k, v in ic.items() if v["status"] == "fail"]
    void_run = any(k in failed for k in ["C-ENGINE", "C-SRC", "C-SEED", "C-SELF", "C-FIX", "C-CURVE", "C-ELL0",
                                         "C-SLICE17", "C-PS", "C-ELL", "C-AFF19", "C-TOP19", "C-T4", "C-PRED",
                                         "C-WDAG", "C-MONO", "C-NONREF", "C-BACKEND", "C-LIT", "C-DET"]) \
        or (ic["C-SUPPORT"]["status"] == "fail")
    void_counts = any(k in failed for k in ("C-CERT", "C-VERIFIER"))
    void_arms = any(k in failed for k in ("C-ORACLE", "C-ORACLE2", "C-DRAW"))
    void_split = "C-TR19" in failed
    void_controls = "C-NULLS" in failed

    # ---- metrics ----------------------------------------------------------------------
    U = arm_rows("S3-U400")
    N_full = len(U)
    und = [x for x in U if x["undetermined"]]
    unc = [x for x in U if x.get("W_4_uncertified")]
    w = sum(1 for x in U if x.get("W_4_verified_wdag"))
    N1 = N_full
    N2 = N_full - len(und) - len(unc)

    def dr1(wv, N):
        if N < 300:
            return "NOT EVALUABLE (sample)"
        if wv >= math.ceil(0.9 * N):
            return "PERSISTS"
        if wv <= math.floor(0.1 * N):
            return "DECAYS"
        return "PARTIAL"

    lab1, lab2 = dr1(w, N1), dr1(w, N2)
    cp_w1, cp_w2 = cp(w, N1), cp(w, N2)
    ref386 = ST.cp95(386, 386)
    dr = {}
    verdict1 = lab1 if lab1 == lab2 else "UNDETERMINED (budget or certification)"
    dr["N19-DR-1"] = {
        "inputs": {"w": w, "N_L1": N1, "N_L2": N2, "uncertified": [x["key"] for x in unc],
                   "undetermined_budget": [x["key"] for x in und], "cp95_L1": cp_w1, "cp95_L2": cp_w2,
                   "thresholds_L1": {"PERSISTS": math.ceil(0.9 * N1), "DECAYS": math.floor(0.1 * N1),
                                     "half": math.floor(N1 / 2)}},
        "label_L1": lab1, "label_L2": lab2, "verdict": verdict1,
        "E-PERSIST_falsified_L1": w <= math.floor(N1 / 2), "E-DECAY_falsified_L1": w > math.floor(N1 / 2),
        "E-PERSIST_falsified_L2": w <= math.floor(N2 / 2), "E-DECAY_falsified_L2": w > math.floor(N2 / 2),
        "n17_comparison": ("NO DETECTABLE DROP FROM n = 17" if cp_w1 and cp_w1["cp95"][1] >= ref386[0]
                           else "BELOW THE n = 17 FIGURE"),
        "n17_reference": {"W_4": "386/386", "cp95_lower_386_386": ref386[2]},
        "n17_reading": ("the n = 17 figure imports 304 Stage-1 flags (82 RC-1-certified plus 304 Stage-1 flags) and "
                        "the cells differ in curve, cofactor (h = 4 vs h = 2) and subgroup-target class (x(4E) vs x(2E))")}
    m4 = sum(1 for x in U if x.get("M_4_verified"))
    m3 = sum(1 for x in U if x.get("M_3_verified"))
    cpm = cp(m4, N1)
    notm4 = [x for x in U if not x["undetermined"] and not x.get("M_4_verified")]
    wcond = sum(1 for x in notm4 if x.get("W_4_verified_wdag"))
    dr["N19-DR-2"] = {"inputs": {"m": m4, "N": N1, "cp95": cpm, "n17_cp95": [0.799, 0.875], "M_3_count": m3,
                                 "W_4_rate_on_S3-U400_not_M4_refuted": cp(wcond, len(notm4))},
                      "verdict": ("LOWER" if cpm["cp95"][1] < 0.799 else "HIGHER" if cpm["cp95"][0] > 0.875
                                  else "CONSISTENT")}
    subs = [x for x in U if not x["undetermined"] and x.get("sigma") is not None]
    Nb = len(subs)
    sp = sum(1 for x in subs if x["sigma"] > 0)
    s0 = sum(1 for x in subs if x["sigma"] == 0)
    sn = sum(1 for x in subs if x["sigma"] < 0)
    full = sum(1 for x in subs if x["R4_dims_by_deg"][3] == 1160)
    if Nb < 300:
        v3 = "NOT EVALUABLE (sample)"
    elif sp >= math.ceil(0.9 * Nb):
        v3 = "NON-SEMI-REGULAR PERSISTS"
    elif s0 >= math.ceil(0.9 * Nb):
        v3 = "SEMI-REGULAR AT n = 19"
    else:
        v3 = "MIXED"
    prof = {}
    for x in subs:
        kk = json.dumps(x["R4_dims_by_deg"])
        prof[kk] = prof.get(kk, 0) + 1
    other_labels = {}
    for x in U:
        if x.get("sigma") is None:
            other_labels[x.get("rc_b_label")] = other_labels.get(x.get("rc_b_label"), 0) + 1
    dr["N19-DR-3"] = {"inputs": {"N_b": Nb, "sigma_gt_0": sp, "sigma_eq_0": s0, "sigma_lt_0": sn,
                                 "FULL_1160": full, "FULL_fraction": full / Nb if Nb else None,
                                 "threshold": math.ceil(0.9 * Nb), "profile_distribution": prof,
                                 "rc_b_not_substituted_labels": other_labels},
                      "verdict": v3}

    def rate(rows, key):
        rr = [x for x in rows if not x["undetermined"]]
        return cp(sum(1 for x in rr if x.get(key)), len(rr)) if rr else None

    per_arm = {}
    for arm in ARMS:
        for role in ("unsat", "sat"):
            rows = arm_rows(arm, role)
            if not rows:
                continue
            per_arm[f"{arm}|{role}"] = {"n": len(rows), "M_3": rate(rows, "M_3_verified"),
                                        "M_4": rate(rows, "M_4_verified"), "W_4": rate(rows, "W_4_verified_wdag"),
                                        "engine_W_4_one": sum(1 for x in rows if x.get("W_4_one"))}
    for st in ("X2E", "XE-NOT-2E", "TWIST"):
        rows = arm_rows("F-RANDX19", stratum=st)
        per_arm[f"F-RANDX19:{st}|unsat"] = {"n": len(rows), "M_4": rate(rows, "M_4_verified"),
                                            "W_4": rate(rows, "W_4_verified_wdag")}
    fam = {}
    for d in range(1, 6):
        for role in ("unsat", "sat"):
            rows = arm_rows("N-AFF19", role, family=d)
            fam[f"{d}|{role}"] = {"n": len(rows), "M_4": rate(rows, "M_4_verified"), "W_4": rate(rows, "W_4_verified_wdag")}
    s3W, s3M = per_arm["S3-U400|unsat"]["W_4"], per_arm["S3-U400|unsat"]["M_4"]
    dr4 = {}
    for X in ("N-F219", "N-AFF19", "N-ELL19"):
        xa = per_arm.get(f"{X}|unsat")
        dr4[X] = {}
        for clo, s3 in (("W_4", s3W), ("M_4", s3M)):
            xr = xa[clo] if xa else None
            dr4[X][clo] = {"S3": s3, "X": xr,
                           "verdict": "S_3 ABOVE X" if (s3 and xr and s3["cp95"][0] > xr["cp95"][1]) else "NOT DISTINGUISHED"}
    dr["N19-DR-4"] = {"inputs": {"per_family_N-AFF19": fam}, "comparisons": dr4,
                      "note": "D <= 5 cleanliness is not computed and is not a statistic of this contract"}
    cv = per_arm.get("N-CONV19|unsat")
    wc, nc = (sum(1 for x in arm_rows("N-CONV19") if x.get("W_4_verified_wdag")),
              len([x for x in arm_rows("N-CONV19") if not x["undetermined"]]))
    v5 = ("TENSOR-LEVEL" if nc and wc >= math.ceil(0.9 * nc) else "BELOW" if wc <= math.floor(0.1 * nc) else "MIXED")
    pair = {}
    for clo, f in (("M_4", "M_4_verified"), ("W_4", "W_4_verified_wdag")):
        t = {"S3+ CONV+": 0, "S3+ CONV-": 0, "S3- CONV+": 0, "S3- CONV-": 0}
        for x in arm_rows("N-CONV19"):
            s3k = f"S3-U400:{x['slot']}"
            a, b = rawby[s3k].get(f), x.get(f)
            t[f"S3{'+' if a else '-'} CONV{'+' if b else '-'}"] += 1
        pair[clo] = t
    dr["N19-DR-5"] = {"inputs": {"w_c": wc, "n_c": nc, "rate": cv["W_4"] if cv else None,
                                 "paired_2x2_on_shared_x_R": pair},
                      "verdict": v5, "AT_S3_RATE": overlap(cv["W_4"], s3W) if cv else None,
                      "N-CONV19_ABOVE_N-ELL19": bool(cv and per_arm.get("N-ELL19|unsat") and
                                                     cv["W_4"]["cp95"][0] > per_arm["N-ELL19|unsat"]["W_4"]["cp95"][1]),
                      "N-CONV19_ABOVE_N-F219": bool(cv and per_arm.get("N-F219|unsat") and
                                                    cv["W_4"]["cp95"][0] > per_arm["N-F219|unsat"]["W_4"]["cp95"][1])}
    dr6 = {}
    for clo, f in (("M_4", "M_4_verified"), ("W_4", "W_4_verified_wdag")):
        g1 = [x for x in arm_rows("F-RANDX19", stratum="X2E") if not x["undetermined"]]
        g2 = [x for x in arm_rows("F-RANDX19") if x["stratum"] in ("XE-NOT-2E", "TWIST") and not x["undetermined"]]
        a = sum(1 for x in g1 if x.get(f))
        c_ = sum(1 for x in g2 if x.get(f))
        b, d = len(g1) - a, len(g2) - c_
        if (a == len(g1) and c_ == len(g2)) or (a == 0 and c_ == 0):
            v = "SATURATED (not evaluable)"
            p = None
        else:
            pf = ST.fisher_one_sided_greater(a, b, c_, d)
            p = ST.fmt(pf)
            pv = float(pf)
            v = "MODULATED" if pv < 0.01 else "WEAK" if pv < 0.2 else "ABSENT"
        x2 = cp(a, len(g1)) if g1 else None
        dr6[clo] = {"table": {"X2E": [a, b], "pooled XE-NOT-2E + TWIST": [c_, d]}, "fisher_one_sided_p": p,
                    "verdict": v, "RANDX_X2E_REPLICATES_PRIMARY": overlap(x2, s3W if clo == "W_4" else s3M)}
    dr["N19-DR-6"] = {"inputs": {"strata": {st: per_arm[f"F-RANDX19:{st}|unsat"] for st in ("X2E", "XE-NOT-2E", "TWIST")},
                                 "n17_M4_rates_descriptive": "0.845 / 0.60 / 0.66"}, "results": dr6}
    dr7 = {}
    for arm in ARMS:
        rows = [x for x in raw if x["arm"] == arm and not x["undetermined"]]
        if not rows:
            continue
        if arm in ("N-F219", "N-AFF19"):
            ref = sum(1 for x in rows if x["M_4_dims_by_deg"] == C.REF_UNSUB and x["M_3_rank"] == 399)
            kind = "unsubstituted [0, 0, 19, 399, 3819]"
        else:
            ref = sum(1 for x in rows if x.get("R4_dims_by_deg") == C.REF_SUB)
            kind = "substituted [0, 0, 18, 360, 3267]"
        fr = ref / len(rows)
        dr7[arm] = {"reference": kind, "systems": len(rows), "with_reference_profile": ref, "fraction": fr,
                    "T5_applicable_fraction": sum(1 for x in rows if x.get("T5_applicable")) / len(rows),
                    "verdict": ("SEMI-REGULAR TRANSFER HOLDS" if fr >= 0.9 else "FAILS" if fr <= 0.1 else "MIXED")}
    dr["N19-DR-7"] = {"per_arm": dr7, "note": "descriptive; no verdict on any heuristic"}
    dr["N19-DR-8"] = {"instrument_checks": {k: v["status"] for k, v in ic.items()}, "failed": failed,
                      "voids": {"run_void": void_run, "refutation_counts_void (INV-6)": void_counts,
                                "arm_metrics_void (INV-7)": void_arms, "x2E_split_void": void_split,
                                "control_comparisons_void (C-NULLS)": void_controls}}
    dr["N19-DR-9"] = {"flag": "ELIGIBLE" if (lab1 == "PERSISTS" and lab2 == "PERSISTS") else "NOT ELIGIBLE",
                      "note": "recorded by the executor; decided by the Coordinator after review; nothing is priced"}
    dr["N19-DR-10"] = {"primary": ["N19-DR-1", "N19-DR-3"], "secondary": ["N19-DR-2", "N19-DR-4", "N19-DR-5",
                                                                           "N19-DR-6", "N19-DR-7"]}
    if void_run:
        for k in ("N19-DR-1", "N19-DR-2", "N19-DR-3", "N19-DR-4", "N19-DR-5", "N19-DR-6", "N19-DR-7"):
            dr[k]["voided_by_N19-DR-8"] = True
    elif void_counts:
        for k in ("N19-DR-1", "N19-DR-2", "N19-DR-4", "N19-DR-5", "N19-DR-6"):
            dr[k]["voided_by_N19-DR-8"] = "INV-6"

    # ---- certificate and ann counts -----------------------------------------------------
    cert_counts = {}
    for c in certv["results"]:
        arm = c["key"].split(":")[0]
        kk = f"{c['closure']}|{arm}|{c['format']}"
        e = cert_counts.setdefault(kk, {"submitted": 0, "verified": 0, "failed": 0, "counting": 0})
        e["submitted"] += 1
        e["verified"] += int(c["valid"])
        e["failed"] += int(not c["valid"])
        e["counting"] += int(bool(c.get("counts")))
    uncert = {}
    for x in raw:
        if x.get("W_4_uncertified"):
            uncert[x["arm"]] = uncert.get(x["arm"], 0) + 1
    ann_counts = {"submitted": annv["submitted"], "verified": annv["verified"], "failed": annv["failed"],
                  "per_arm": {}}
    for a in annv["results"]:
        arm = a["key"].split(":")[0]
        e = ann_counts["per_arm"].setdefault(arm, {"submitted": 0, "verified": 0})
        e["submitted"] += 1
        e["verified"] += int(a["valid"])
    ps_rows = [x for x in raw if x["role"] == "sat" and not x["undetermined"]]
    ps_small = [x for x in ps_rows if x["s"] <= 31]
    cps = {"satisfiable_controls": len(ps_rows),
           "refuted_M_3": sum(1 for x in ps_rows if x["M_3_one"]), "refuted_M_4": sum(1 for x in ps_rows if x["M_4_one"]),
           "refuted_W_4": sum(1 for x in ps_rows if x["W_4_one"]),
           "codim_ge_s": sum(1 for x in ps_rows if 6196 - x["W_4_final_dim"] >= x["s"]),
           "codim_eq_s_among_s_le_31": [sum(1 for x in ps_small if 6196 - x["W_4_final_dim"] == x["s"]), len(ps_small)],
           "per_arm": {arm: {"n": sum(1 for x in ps_rows if x["arm"] == arm),
                             "refuted_any": sum(1 for x in ps_rows if x["arm"] == arm and (x["M_3_one"] or x["M_4_one"] or x["W_4_one"]))}
                       for arm in ARMS}}

    summary = {
        "experiment_id": C.EXPERIMENT_ID, "run_id": R.args.run_id,
        "MR19-1": {"w": w, "N": N1, "cp95": cp_w1, "N_L2": N2, "cp95_L2": cp_w2},
        "MR19-2": dr["N19-DR-3"]["inputs"],
        "MR19-3": {"per_arm": per_arm, "N-AFF19_per_family": fam, "C-PS": cps, "certificates": cert_counts,
                   "uncertified_W_4_refutations": uncert, "ann_v1": ann_counts},
        "secondary": {"M_4_S3-U400": cpm, "M_3_S3-U400": m3,
                      "W_4_rate_S3-U400_not_M4_refuted": cp(wcond, len(notm4)),
                      "ell_route_S3-U400": sum(1 for x in U if x.get("ell_route")),
                      "T5_applicable_and_reference_fractions": dr7,
                      "derived_distributions": derived_dists(raw),
                      "W_4_iteration_distribution": iter_dist(raw),
                      "draw_statistics": p2["draw_stats"], "sizes": p2["sizes"], "sizes_by_role": p2["sizes_by_role"],
                      "shortfalls": p2["shortfalls"], "F-RANDX19_strata": p2["F-RANDX19_strata"],
                      "paired_2x2": pair, "x2E_split": dr6,
                      "closure_wall_seconds_measured": wall_stats(clos)},
        "all_values_are": "measured on this run's systems (counts of systems); no modeled number appears here"}
    # ---- raw vs summary cross-check --------------------------------------------------------
    chk = {"MR19-1_w": sum(1 for x in raw if x["arm"] == "S3-U400" and x["role"] == "unsat" and x.get("W_4_verified_wdag")) == w,
           "MR19-2_sigma_gt_0": sum(1 for x in raw if x["arm"] == "S3-U400" and x.get("sigma") is not None and x["sigma"] > 0) == sp,
           "MR19-3_arm_counts": all(
               (per_arm[k]["W_4"] or {}).get("k", 0) == sum(1 for x in raw if f"{x['arm']}|{x['role']}" == k and x.get("W_4_verified_wdag"))
               for k in per_arm if "|" in k and ":" not in k)}
    summary["raw_vs_summary_check"] = {"checks": chk, "pass": all(chk.values())}
    status = ("invalid_measurement" if (void_run or void_counts) else "completed_valid")
    C.write_json(out / "instrument-checks.json", {"checks": ic, "failed": failed, "validity_status": status})
    C.write_json(out / "decision-rules.json", dr)
    C.write_json(out / "cell-summary.json", summary)
    C.write_json(out / "raw-result.json", {"experiment_id": C.EXPERIMENT_ID, "run_id": R.args.run_id,
                                           "validity_status": status, "systems": raw})
    write_manifest(R, status, ic, summary, dr, p0, p3, p4, na)
    write_report(R, status, ic, summary, dr, p2, na)
    return status


def wall_stats(clos):
    out = {}
    for c in clos.values():
        for k, v in (c.get("wall_seconds_measured") or {}).items():
            out.setdefault(k, []).append(v)
    return {k: {"n": len(v), "sum": round(sum(v), 1), "median": float(np.median(v)), "max": max(v)}
            for k, v in out.items()}


def derived_dists(raw):
    out = {}
    for arm in ARMS:
        rows = [x for x in raw if x["arm"] == arm and not x["undetermined"]]
        d = {}
        for f in ("P", "fallen", "linear_forms", "syzygy_excess"):
            vals = [x["derived"][f] for x in rows]
            if vals:
                d[f] = {"min": min(vals), "max": max(vals), "median": float(np.median(vals)),
                        "mode_counts": dict(sorted(((str(v), vals.count(v)) for v in set(vals)), key=lambda t: -t[1])[:5])}
        out[arm] = d
    return out


def iter_dist(raw):
    out = {}
    for x in raw:
        if x["undetermined"]:
            continue
        kk = f"{x['arm']}|{x['role']}"
        e = out.setdefault(kk, {})
        key = f"it={x['W_4_iterations']},first1={x['W_4_one_first_iteration']}"
        e[key] = e.get(key, 0) + 1
    return out


def git(*a):
    return subprocess.run(["git", *a], cwd=C.ROOT, capture_output=True, text=True).stdout.strip()


def write_manifest(R, status, ic, summary, dr, p0, p3, p4, na):
    import yaml
    out = R.out
    timings = []
    tp = R.ck / "timings.jsonl"
    if tp.exists():
        timings = [json.loads(x) for x in tp.read_text().splitlines() if x.strip()]
    ep = jl(out / "engine-provenance" / "engine-provenance.json")
    envj = jl(out / "environment.json") if (out / "environment.json").exists() else {}
    files = {}
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name not in ("manifest.yaml",) and "checkpoint" not in p.parts:
            files[str(p.relative_to(out))] = {"sha256": C.sha256_file(p), "bytes": p.stat().st_size}
    ck_bytes = sum(p.stat().st_size for p in (out / "checkpoint").rglob("*") if p.is_file())
    total = sum(v["bytes"] for v in files.values())
    man = {
        "manifest_version": 1, "experiment_id": C.EXPERIMENT_ID, "run_id": R.args.run_id,
        "task_id": "TASK-20260924-a50c5b", "archived_by": "TASK-20260924-d0f80c",
        "approval_decision": "DEC-20260924-f5c3f9", "hypothesis_id": "H-CERTBIN-e3ac93",
        "validity_status": status,
        "failed_instrument_checks": [k for k, v in ic.items() if v["status"] == "fail"],
        "git": {"head_at_phase7": git("rev-parse", "HEAD"), "head_at_launch": envj.get("git_head"),
                "dirty_at_launch": envj.get("git_dirty"), "status_porcelain_at_launch": envj.get("git_status")},
        "commands": (out / "command.txt").read_text() if (out / "command.txt").exists() else None,
        "environment": envj,
        "engine": {"package": "src/crypto_autoresearcher/gf2", "pinned_commit": C.PINNED_COMMIT,
                   "import_mode": "src/ on sys.path (impl/common.py inserts ROOT/src)",
                   "build_info": ep["items"]["e_build_info"]["build_info"],
                   "kernels_c_sha256": ep["items"]["b_hashes"]["kernels_c_sha256"],
                   "package_files_sha256": ep["items"]["b_hashes"]["package_files_sha256"],
                   "tree": ep["items"]["a_tree_rule"]},
        "input_hashes": jl(out / "inputs.json")["files"],
        "seeds": dict(C.SEEDS), "other_randomness": [
            "negative-control corruption choices: numpy PCG64(S_selftest + 999) (does not touch any arm stream)",
            "no other randomness; threads do not affect results (C-DET (c))"],
        "trial_plan_sha256": p0["plan_sha256"], "specification_sha256": p0["spec_sha256"],
        "predictions_sha256": p3["predictions_sha256"], "predictions_written_utc": p3["predictions_written_utc"],
        "inference": {"requested_policy": "executor-implementation", "reasoning_effort_requested": None,
                      "resolved_model": "claude-opus-5-5 (session model; Claude Code subagent inheritance)",
                      "fallback_used": True,
                      "fallback_reason": "DEC-20260923-4d7a19 R-1: same-session subagents inherit the session model; "
                                         "per-role model selection is process-level",
                      "model_verified": False, "model_verified_note": "the runtime reports the model name; no "
                                                                       "independent attestation is available in-session"},
        "timings_measured": timings,
        "certificate_kinds": ["flat-v1 (M_3, M_4, engine W_4)", "wdag-v1 (W_4)", "ann-v1 (W_4 non-refutation)"],
        "certificate": {"kind": "unsatisfiability_certificate",
                        "verified_by": "verifier/verify_n19.py, separate process"},
        "output_bound": {"package_bytes_excluding_checkpoint": total, "checkpoint_bytes": ck_bytes,
                         "under_200_MiB_excluding_checkpoint": total < 200 * 2 ** 20,
                         "ann_nonarchived": na},
        "files": files,
    }
    with open(out / "manifest.yaml", "w") as f:
        yaml.safe_dump(man, f, sort_keys=False, width=110)


def write_report(R, status, ic, summary, dr, p2, na):
    out = R.out
    L = []
    a = L.append
    m1 = summary["MR19-1"]
    a(f"# Run report: {C.EXPERIMENT_ID} / {R.args.run_id}\n")
    a(f"Validity status: **{status}**. Failed instrument checks: {[k for k, v in ic.items() if v['status'] == 'fail'] or 'none'}.\n")
    a("Observations only. No hypothesis status, evidence record or decision is implied.\n")
    a("## Claim tier and scope (verbatim from the specification)\n")
    a("Claim tier: toy. Refutation-degree measurement at one cell: n = 19, f = t^19 + t^5 + t^2 + t + 1, m = 2, "
      "l = 10, polynomial V = {deg < 10}, one curve A = 46693, B = 306147 (#E = 2 * 261823, h = 2), subgroup (= x(2E)) "
      "targets plus uniform-x_R strata, under M_3, M_4, W_4 and the substituted R'_3, R'_4, W'_4 as defined below. "
      "n = 17 enters only as quoted references and as a regression slice. sota_delta: zero on every ECDLP cost axis. "
      "Dominated by oracle A (2^10 quadratic root-findings per attempt) and, for the DLP at q = 261823, by parallel "
      "Pollard rho.\n")
    a("## Decision rules (mechanical)\n")
    d1 = dr["N19-DR-1"]
    a(f"- N19-DR-1 (primary): w = {m1['w']} / N = {m1['N']}, CP95 {m1['cp95']['cp95_str'] if m1['cp95'] else None}; "
      f"label L1 = {d1['label_L1']}, label L2 = {d1['label_L2']} (N_L2 = {m1['N_L2']}); verdict: {d1['verdict']}. "
      f"E-PERSIST falsified (L1): {d1['E-PERSIST_falsified_L1']}; E-DECAY falsified (L1): {d1['E-DECAY_falsified_L1']}. "
      f"n = 17 comparison: {d1['n17_comparison']} ({d1['n17_reading']}).")
    d2 = dr["N19-DR-2"]
    a(f"- N19-DR-2: M_4 m = {d2['inputs']['m']} / {d2['inputs']['N']}, CP95 {d2['inputs']['cp95']['cp95_str']}; "
      f"verdict {d2['verdict']} against [0.799, 0.875]. M_3 count {d2['inputs']['M_3_count']}. W_4 rate on systems "
      f"M_4 does not refute: {fmt_cp(d2['inputs']['W_4_rate_on_S3-U400_not_M4_refuted'])}.")
    d3 = dr["N19-DR-3"]["inputs"]
    a(f"- N19-DR-3 (primary): N_b = {d3['N_b']}; sigma > 0: {d3['sigma_gt_0']}, sigma = 0: {d3['sigma_eq_0']}, "
      f"sigma < 0: {d3['sigma_lt_0']}; FULL (1160): {d3['FULL_1160']} (fraction {d3['FULL_fraction']}); verdict "
      f"{dr['N19-DR-3']['verdict']}. Profiles: {d3['profile_distribution']}. Not substituted: {d3['rc_b_not_substituted_labels']}.")
    for X, v in dr["N19-DR-4"]["comparisons"].items():
        a(f"- N19-DR-4 vs {X}: W_4 {v['W_4']['verdict']} (X: {fmt_cp(v['W_4']['X'])}); "
          f"M_4 {v['M_4']['verdict']} (X: {fmt_cp(v['M_4']['X'])}).")
    d5 = dr["N19-DR-5"]
    a(f"- N19-DR-5: N-CONV19 W_4 {d5['inputs']['w_c']} / {d5['inputs']['n_c']}: {d5['verdict']}; AT S_3's RATE: "
      f"{d5['AT_S3_RATE']}; ABOVE N-ELL19: {d5['N-CONV19_ABOVE_N-ELL19']}; ABOVE N-F219: {d5['N-CONV19_ABOVE_N-F219']}; "
      f"paired 2x2: {d5['inputs']['paired_2x2_on_shared_x_R']}.")
    for clo, v in dr["N19-DR-6"]["results"].items():
        a(f"- N19-DR-6 at {clo}: table {v['table']}, one-sided Fisher p {v['fisher_one_sided_p']}, {v['verdict']}; "
          f"RANDX X2E REPLICATES PRIMARY: {v['RANDX_X2E_REPLICATES_PRIMARY']}.")
    for arm, v in dr["N19-DR-7"]["per_arm"].items():
        a(f"- N19-DR-7 {arm}: {v['with_reference_profile']}/{v['systems']} with {v['reference']} -> {v['verdict']}; "
          f"T5_applicable fraction {v['T5_applicable_fraction']:.3f}.")
    a(f"- N19-DR-8: failed checks {dr['N19-DR-8']['failed'] or 'none'}; voids {dr['N19-DR-8']['voids']}.")
    a(f"- N19-DR-9: m = 3 pricing flag {dr['N19-DR-9']['flag']} (the Coordinator decides after review).")
    a("- N19-DR-10: primary verdicts are N19-DR-1 and N19-DR-3.\n")
    a("## Pre-registered predictions PP-1..PP-6 (H-CERTBIN-e3ac93), as observed\n")
    pa = summary["MR19-3"]["per_arm"]
    pp = pp_status(summary, dr, ic)
    for k, v in pp.items():
        a(f"- {k}: {v}")
    a("\n## Coordinator prior (a)-(g): which parts the observations overturn\n")
    for k, v in prior_status(summary, dr).items():
        a(f"- {k}: {v}")
    a("\n## Instrument checks\n")
    for k, v in ic.items():
        a(f"- {k}: {v['status']}")
    a("\n## E_hex bit layout\n")
    a("A system is a 19 x 211 F_2 matrix E; row k is f_k (the coefficient of t^k). Column j is the j-th monomial of "
      "mu_order(2, 20): degree ascending, then ascending sorted index tuple (column 0 = 1, columns 1..20 = v_0..v_19, "
      "columns 21..210 = the pairs (i, j), i < j, in lexicographic order). E_hex is a list of 19 lowercase hex integers, "
      "bit j (LSB first) = column j. E_sha256 = sha256 of the compact JSON list of the 19 E_hex strings. Assignment "
      "integers u have bit i = v_i (x_1 = u mod 2^10, x_2 = u >> 10).\n")
    a("## Independence disclosure\n")
    a("The engine (src/crypto_autoresearcher/gf2, pinned 934bee5) was written by the dispatching session. impl/ and "
      "verifier/ were written by this executor. The verifier imports nothing from impl/, from crypto_autoresearcher or "
      "from any archived impl/ or review directory (asserted at start and exit); it is code-independent of both the "
      "engine and impl/, but NOT author-independent of impl/. Author-independent verification is the review round's "
      "(claim_tier_and_review joint 1).\n")
    a("## Sizes, shortfalls, output bound\n")
    a(f"- kept sizes: {p2['sizes']}; by role: {p2['sizes_by_role']}; F-RANDX19 strata: {p2['F-RANDX19_strata']}.")
    a(f"- shortfalls / exhausted: {p2['shortfalls']}.")
    a(f"- ann-v1 output bound applied: {na['output_bound_applied']} ({len(na['files'])} S3-U400 ann-v1 files not archived).")
    a("\nAll counts above are measured on this run. Runtime and memory figures are in manifest.yaml (measured).\n")
    (out / "run-report.md").write_text("\n".join(L) + "\n")


def fmt_cp(x):
    if not x:
        return "n/a"
    return f"{x['k']}/{x['n']} CP95 [{x['cp95'][0]:.4f}, {x['cp95'][1]:.4f}]"


def pp_status(summary, dr, ic):
    d1 = dr["N19-DR-1"]
    d3 = dr["N19-DR-3"]
    pa = summary["MR19-3"]["per_arm"]
    out = {}
    out["PP-1 (w; E-PERSIST vs E-DECAY)"] = (f"L1 {d1['label_L1']}, L2 {d1['label_L2']}; E-PERSIST falsified: "
                                            f"{d1['E-PERSIST_falsified_L1']}; E-DECAY falsified: {d1['E-DECAY_falsified_L1']}")
    out["PP-2 (sigma)"] = f"N19-DR-3 {d3['verdict']}"
    out["PP-3 (M_4 vs n = 17)"] = f"N19-DR-2 {dr['N19-DR-2']['verdict']}"
    nulls = {X: (pa.get(f'{X}|unsat') or {}).get('W_4') for X in ("N-F219", "N-AFF19", "N-ELL19")}
    out["PP-4 (null / N-ELL19 W_4 refutations)"] = "; ".join(f"{X}: {fmt_cp(v)}" for X, v in nulls.items()) + \
        f"; C-PRED {ic['C-PRED']['status']}"
    ps = summary["MR19-3"]["C-PS"]
    out["PP-5 (soundness)"] = (f"refuted satisfiable controls M_3 {ps['refuted_M_3']}, M_4 {ps['refuted_M_4']}, "
                               f"W_4 {ps['refuted_W_4']} of {ps['satisfiable_controls']}; codim >= s on "
                               f"{ps['codim_ge_s']}; C-PS {ic['C-PS']['status']}")
    out["PP-6 (L-TOP)"] = f"C-TOP19 {ic['C-TOP19']['status']} ({ic['C-TOP19']['slots_compared']} systems compared)"
    return out


def prior_status(summary, dr):
    d1 = dr["N19-DR-1"]["verdict"]
    return {
        "(a) N19-DR-1 prior PERSISTS 55 / PARTIAL 30 / DECAYS 15": f"observed {d1} (a probability prior is not overturned by one outcome; the most-likely label was PERSISTS)",
        "(b) N19-DR-2 prior LOWER 50 / CONSISTENT 40 / HIGHER 10": f"observed {dr['N19-DR-2']['verdict']}",
        "(c) N19-DR-3 prior NON-SEMI-REGULAR PERSISTS 80; FULL on most 40": f"observed {dr['N19-DR-3']['verdict']}; FULL fraction {dr['N19-DR-3']['inputs']['FULL_fraction']}",
        "(d) nulls and N-ELL19 at 0 W_4 refutations; N19-DR-7 HOLDS": "; ".join(
            f"{X}: W_4 {fmt_cp(v['W_4']['X'])}" for X, v in dr["N19-DR-4"]["comparisons"].items()) + "; DR-7: " +
            ", ".join(f"{a}: {v['verdict']}" for a, v in dr["N19-DR-7"]["per_arm"].items()),
        "(e) N19-DR-5 TENSOR-LEVEL 50": f"observed {dr['N19-DR-5']['verdict']}",
        "(f) N19-DR-6 at M_4 MODULATED or WEAK 60; W_4 SATURATED if (a) PERSISTS": ", ".join(
            f"{c}: {v['verdict']}" for c, v in dr["N19-DR-6"]["results"].items()),
        "(g) every W_4 refutation certified 80; C-NONREF non-vacuous 45": (
            f"uncertified W_4 refutations: {summary['MR19-3']['uncertified_W_4_refutations'] or 'none'}; "
            f"ann-v1 submitted {summary['MR19-3']['ann_v1']['submitted']}"),
    }
