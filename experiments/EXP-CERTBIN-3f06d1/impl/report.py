"""Phase 9 writer for EXP-CERTBIN-3f06d1: every declared artifact of the run
package. Copied from EXP-CERTBIN-4e92d7/impl/report.py and rewritten for the
v2 contract (impl-provenance.json).

raw-result.json is recomputed from the WRITTEN targets-<cell>-<family>.jsonl.gz
and pivot-hazards-<cell>.json files by code in this module that does not call
analysis.py (its own hull, restriction, band and median code), and compared
with cell-summary.json on every primary metric.
"""
import datetime
import gzip
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from math import comb

import numpy as np
import yaml

import analysis
from analysis import FAMS, AFFINE, GRANS, DS, CELLS


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_new(path, text, mode="w"):
    if os.path.exists(path):
        raise RuntimeError(f"{path} exists; refusing to overwrite")
    tmp = path + ".tmp"
    with open(tmp, mode) as f:
        f.write(text)
    os.replace(tmp, path)


def _jd(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, Fraction):
        return str(o)
    raise TypeError(type(o))


def jdump(obj, compact=False):
    if compact:
        return json.dumps(obj, separators=(",", ":"), default=_jd)
    return json.dumps(obj, indent=1, default=_jd)


# ---------------------------------------------------------------------------
# independent recomputation (does not call analysis.py)
# ---------------------------------------------------------------------------
def _ech_add(rows, v):
    while v:
        h = v.bit_length() - 1
        if h in rows:
            v ^= rows[h]
        else:
            rows[h] = v
            return True
    return False


def _band(n):
    tot = 1 << n
    cum = 0
    lo = 0
    for i in range(n + 1):
        cum += comb(n, i)
        if 2000 * cum <= tot:
            lo = i + 1
        else:
            break
    cum = 0
    hi = n
    for i in range(n, -1, -1):
        cum += comb(n, i)
        if 2000 * cum <= tot:
            hi = i - 1
        else:
            break
    return lo, hi


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def independent_primary(out_dir):
    res = {}
    for cell in CELLS:
        res[cell] = {}
        hz = json.load(open(os.path.join(out_dir, f"pivot-hazards-{cell}.json")))["families"]
        for fam in FAMS:
            recs = []
            with gzip.open(os.path.join(out_dir, f"targets-{cell}-{fam}.jsonl.gz"), "rt") as f:
                for line in f:
                    recs.append(json.loads(line))
            res[cell][fam] = {}
            for D in DS:
                rd = [r for r in recs if r["D"] == D and r["stratum"] != "degenerate"]
                un = [r for r in rd if r["stratum"] == "unsat"]
                sa = [r for r in rd if r["stratum"] == "sat"]
                keys = sorted({k for r in rd for k in r["refs"]})
                m1 = {k: [sum(1 for r in un if k in r["refs"] and r["refs"][k]["match"]["strict"]),
                          sum(1 for r in un if k in r["refs"])] for k in keys}
                fdm = {k: {"unsat": _median([r["refs"][k]["f_div"] for r in un if k in r["refs"]]),
                           "sat": _median([r["refs"][k]["f_div"] for r in sa if k in r["refs"]])} for k in keys}
                o = {"arm_sizes": {"unsat": len(un), "sat": len(sa)},
                     "strict_unsat_counts": m1, "median_f_div": fdm,
                     "one_in_R_unsat": [sum(1 for r in un if r["one_in_R"]), len(un)]}
                if fam == "F-RANDX":
                    o["one_in_R_unsat_by_class"] = {c: [sum(1 for r in un if r["x2E_class"] == c and r["one_in_R"]),
                                                        sum(1 for r in un if r["x2E_class"] == c)]
                                                    for c in ("x2E", "xE_not_2E", "twist")}
                if fam in AFFINE:
                    # own hull from the written per-target file (idx order, non-degenerate)
                    pts = sorted((r["idx"], r["x_R"]) for r in rd)
                    h0 = pts[0][1]
                    rows = {}
                    for _, x in pts[1:]:
                        _ech_add(rows, x ^ h0)
                    Wb = [rows[k] for k in sorted(rows, reverse=True)]
                    kr = {}
                    ts_meas = {}
                    for key, t in hz[fam][f"D{D}"].items():
                        rest = []
                        for a in t["a"]:
                            v = 0
                            for i, w in enumerate(Wb):
                                if bin(a & w).count("1") & 1:
                                    v |= 1 << i
                            rest.append(v)
                        er = {}
                        inc = [_ech_add(er, v) for v in rest]
                        kr[key] = {"K_rank_hull": sum(inc), "dim_W": len(Wb)}
                        if key in (["F-S3:U1", "F-S3:U2", "F-S3:U3", "F-S3:S1", "F-S3:S2", "F-S3:modal", "modal"] if fam == "F-PLANT"
                                   else ["U1", "U2", "U3", "S1", "S2", "modal"]):
                            sc = [r for r in rd if key in r["refs"] and (key != "modal" or r["idx"] > 100)]
                            byf = {}
                            for r in sc:
                                byf.setdefault(r["refs"][key]["replay_first_zero"], []).append(r["idx"])
                            S = set(r["idx"] for r in sc)
                            for k in range(len(rest)):
                                if k > 0:
                                    S.difference_update(byf.get(k - 1, []))
                                if len(S) < 100:
                                    break
                                if inc[k]:
                                    z = len(byf.get(k, []))
                                    kk = (rest[k], tuple(sorted(S)))
                                    ts_meas.setdefault(kk, (len(S), z))
                    o["K_rank_hull"] = kr
                    m = len(ts_meas)
                    oo = 0
                    for S, z in ts_meas.values():
                        lo, hi = _band(S)
                        oo += not (lo <= z <= hi)
                    o["TS1R_m_o"] = [m, oo]
                res[cell][fam][f"D{D}"] = o
    return res


def agreement(cells_summary, indep):
    diffs = []
    checked = 0
    for cell in CELLS:
        for fam in FAMS:
            for D in DS:
                c = cells_summary[cell]["families"][fam][f"D{D}"]
                i = indep[cell][fam][f"D{D}"]
                checked += 1
                if c["arm_sizes"] != i["arm_sizes"]:
                    diffs.append({"cell": cell, "family": fam, "D": D, "metric": "arm_sizes", "cell_summary": c["arm_sizes"], "raw": i["arm_sizes"]})
                for k, v in c["retention"]["strict"].items():
                    checked += 1
                    iv = i["strict_unsat_counts"].get(k, [0, 0])
                    if [v["unsat"]["x"], v["unsat"]["n"]] != iv:
                        diffs.append({"cell": cell, "family": fam, "D": D, "metric": "M1 strict unsat", "ref": k,
                                      "cell_summary": [v["unsat"]["x"], v["unsat"]["n"]], "raw": iv})
                for k, v in c["M1f_first_divergence"].items():
                    for arm in ("unsat", "sat"):
                        checked += 1
                        a, b = v[arm]["median_f_div"], i["median_f_div"].get(k, {}).get(arm)
                        if not ((a is None and b is None) or (a is not None and b is not None and abs(a - b) < 1e-12)):
                            diffs.append({"cell": cell, "family": fam, "D": D, "metric": "median f_div", "ref": k, "arm": arm,
                                          "cell_summary": a, "raw": b})
                checked += 1
                u = c["one_in_R"]["unsat"]
                if [u["x"], u["n"]] != i["one_in_R_unsat"]:
                    diffs.append({"cell": cell, "family": fam, "D": D, "metric": "1 in R unsat", "cell_summary": [u["x"], u["n"]], "raw": i["one_in_R_unsat"]})
                if fam == "F-RANDX":
                    for cls, (x, n) in i["one_in_R_unsat_by_class"].items():
                        checked += 1
                        s = c["one_in_R_unsat_by_x2E_class"][cls]
                        if [s["x"], s["n"]] != [x, n]:
                            diffs.append({"cell": cell, "D": D, "metric": f"F-RANDX split {cls}", "cell_summary": [s["x"], s["n"]], "raw": [x, n]})
                if fam in AFFINE:
                    for k, v in c["M1k_hull_rank"].items():
                        checked += 1
                        iv = i["K_rank_hull"].get(k)
                        if iv is None or iv["K_rank_hull"] != v["K_rank_hull"] or iv["dim_W"] != v["dim_W"]:
                            diffs.append({"cell": cell, "family": fam, "D": D, "metric": "K_rank_hull", "ref": k,
                                          "cell_summary": [v["K_rank_hull"], v["dim_W"]], "raw": iv})
                    checked += 1
                    ts = c["M2R_TS1R"]
                    if [ts["m"], ts["o"]] != i["TS1R_m_o"]:
                        diffs.append({"cell": cell, "family": fam, "D": D, "metric": "TS1R (m, o)", "cell_summary": [ts["m"], ts["o"]], "raw": i["TS1R_m_o"]})
    return {"checked_items": checked, "disagreements": diffs, "agree": not diffs}


# ---------------------------------------------------------------------------
def fmt(x, nd=4):
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:.{nd}g}"
    return str(x)


def cpfmt(ci):
    if not ci:
        return "n/a"
    return f"[{ci['lo']:.4f}, {ci['hi']:.4f}]"


def run_report(spec, cells_summary, checks, dr, agree, status, run_id, inv):
    sc = spec["experiment"]["claim_tier_and_scope"]
    L = []
    L.append(f"# Run report: {run_id} (EXP-CERTBIN-3f06d1, specification version 1)\n")
    L.append("Generated mechanically by phase 9 of `experiments/EXP-CERTBIN-3f06d1/impl/driver.py`. Every line is an "
             "observation or the mechanical application of a frozen rule. It declares no hypothesis or heuristic "
             "supported, refuted, replicated in the official sense, or closed; RR verdict strings are the frozen rule "
             "labels. That judgement belongs to the Reviewer and the Coordinator.\n")
    L.append(f"**Run validity status:** `{status}`." + (f" Void reasons: {'; '.join(inv['run_void_reasons'])}." if inv["run_void"] else "") + "\n")
    L.append("## Claim tier and scope (verbatim from the specification)\n")
    for k in ("claim_tier", "statement", "sota_delta", "dominated_by", "certificate_kind", "affected_vs_safe"):
        L.append(f"- {k}: {sc[k]}")
    L.append("\nTested parameters: n = 17 (F_2[t]/(t^17 + t^3 + 1)), m = 2, l = 9, D in {3, 4}, the Stage-1 fixed-shape "
             "Macaulay elimination (declared row order, descending degrevlex columns, constant last, smallest-original-row "
             "pivot rule), cells R1, R2, R3 below. Nothing is claimed for other n, other curves or V, other orders or pivot "
             "rules, regime B, or any deployed curve.\n")
    L.append("## Cells\n")
    L.append("| cell | A | B | #E | h | q | V | dim W (F-S3 hull) | 0 in H | C-TR |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for cell in CELLS:
        cv = checks["cells_meta"][cell]
        h = cells_summary[cell]["hull_per_family"]["F-S3"]
        L.append(f"| {cell} | {cv['A']} | {cv['B']} | {cv['order']} | {cv['h']} | {cv['q']} | {cv['V']} | {h['dim_W']} | {h['zero_in_H']} | "
                 f"{'pass' if checks['per_cell'][cell]['C-TR']['pass'] else 'FAIL (data)'} |")
    L.append("")
    L.append("## Arm sizes (non-degenerate) and UNDERPOWERED flags (SR-3), D = 4\n")
    L.append("| cell | family | unsat | sat | degenerate | flags |")
    L.append("|---|---|---|---|---|---|")
    for cell in CELLS:
        for fam in FAMS:
            c = cells_summary[cell]["families"][fam]["D4"]
            up = [a for a, v in c["underpowered"].items() if v]
            L.append(f"| {cell} | {fam} | {c['arm_sizes']['unsat']} | {c['arm_sizes']['sat']} | {c['N_degenerate']} | "
                     f"{', '.join('UNDERPOWERED ' + a for a in up) or '-'} |")
    L.append("")
    L.append("## Primary readings per cell (F-S3, D = 4)\n")
    for cell in CELLS:
        cs = cells_summary[cell]
        c4 = cs["families"]["F-S3"]["D4"]
        d = dr["per_cell"][cell]
        L.append(f"### {cell}\n")
        per = c4["M1_retention_family_unsat"]["strict"]["per_reference"]
        L.append("- M1 (T_strict unsat retention): " + "; ".join(f"{k} {v['x']}/{v['n']} CP95 {cpfmt(v['cp95'])}" for k, v in per.items()))
        fd = c4["M1f_first_divergence"]
        L.append("- M1f median f_div (unsat, sat): " + "; ".join(f"{k} ({fmt(v['unsat']['median_f_div'], 3)}, {fmt(v['sat']['median_f_div'], 3)})" for k, v in fd.items()))
        mk = c4["M1k_hull_rank"]
        L.append("- M1k (K_rank / K_rank_hull / dim W / dim Sigma_H): " + "; ".join(
            f"{k} {v['K_rank']}/{v['K_rank_hull']}/{v['dim_W']}/{v['Sigma_H_dim']}" for k, v in mk.items()))
        ts = c4["M2R_TS1R"]
        L.append(f"- M2R TS1R: m = {ts['m']}, o = {ts['o']}, P[Bin(m, 0.001) >= o] = {fmt((ts['P_Bin_m_0.001_ge_o'] or {}).get('value'))}"
                 f" (log10 {fmt((ts['P_Bin_m_0.001_ge_o'] or {}).get('log10'))}); n_rep = {ts['n_rep']}, all h = 0: {ts['n_rep_all_h_zero']}")
        u = c4["one_in_R"]["unsat"]
        L.append(f"- M-R4: F-S3 unsat 1 in R_4 {u['x']}/{u['n']} = {fmt(u['rate'])} CP95 {cpfmt(u['cp95'])}; nulls: " +
                 "; ".join(f"{f} {cs['families'][f]['D4']['one_in_R']['unsat']['x']}/{cs['families'][f]['D4']['one_in_R']['unsat']['n']} CP95 {cpfmt(cs['families'][f]['D4']['one_in_R']['unsat']['cp95'])}" for f in ("F-AFF-1", "F-NULLF2")))
        sp = cs["families"]["F-RANDX"]["D4"]["one_in_R_unsat_by_x2E_class"]
        fz = cs["x2E_modulation_F-RANDX"]["D4"]
        L.append("- x(2E) split (F-RANDX unsat, D = 4): " + "; ".join(f"{k} {v['x']}/{v['n']}" for k, v in sp.items()) +
                 (f"; exact one-sided Fisher p = {fmt(fz['p_value'])}" if fz.get("evaluable") else "; not evaluable"))
        m3 = cs["M3"]
        L.append(f"- M3: rule ({m3['rule']}) {m3['kind']}, value {fmt(m3.get('value'))}")
        for k in ("RR-1", "RR-2", "RR-3", "RR-4", "RR-5", "RR-6", "RR-7"):
            v = d[k]
            extra = f"; nulls: {v['nulls']}" if k == "RR-5" else ""
            where = ", ".join(str(x) for x in (v.get("family"), v.get("granularity"), f"D = {v.get('D')}") if x)
            L.append(f"- **{k}** [{cell}; {where}]: {v['verdict']}{extra}" + (f" ({v['reason']})" if v.get("reason") else ""))
        L.append(f"- **RR-8**: {d['RR-8']['verdict']}" + (f"; failed: {d['RR-8']['failed_controls']}" if d['RR-8']['failed_controls'] else ""))
        L.append("")
    L.append("## Composite (RR-9) and primary set (RR-10)\n")
    L.append(f"- H-CERTBIN-a73f1c: {dr['RR-9']['H-CERTBIN-a73f1c']}")
    L.append(f"- H-CERTBIN-5e71c9 C2: {dr['RR-9']['H-CERTBIN-5e71c9_C2']}")
    L.append(f"- H-CERTBIN-7c3a18: KR1 {dr['RR-9']['H-CERTBIN-7c3a18']['KR1_per_RR-2']}; TS1R {dr['RR-9']['H-CERTBIN-7c3a18']['TS1R_per_RR-4']}")
    L.append(f"- RR-10: primary = {dr['RR-10']['primary']}; everything else is secondary.\n")
    L.append("## Pre-registered prediction (formula) against the data\n")
    L.append("| cell | retention_family < 0.5 (pred. <= 0.01) | K_rank_hull = dim W all refs | median f_div <= 0.1 both arms | TS1R | 1-in-R_4 CP95 overlaps [0.799, 0.875] | null CP95 upper <= 0.05 | x(2E) Fisher p < 0.01 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for cell in CELLS:
        d = dr["per_cell"][cell]
        rf = cells_summary[cell]["families"]["F-S3"]["D4"]["M1_retention_family_unsat"]["strict"]["retention_family"]
        L.append(f"| {cell} | {fmt(rf)} ({'< 0.5' if rf is not None and rf < 0.5 else 'not < 0.5'}; {'<= 0.01' if rf is not None and rf <= 0.01 else '> 0.01'}) | "
                 f"{d['RR-2']['verdict']} | {d['RR-3']['verdict']} | {d['RR-4']['verdict']} | {d['RR-5']['verdict']} | {d['RR-5']['nulls']} | {d['RR-6']['verdict']} |")
    L.append("")
    L.append("## Coordinator prior (a)-(e) against the data (mechanical readings)\n")
    for row in prior_rows(dr):
        L.append(f"- {row}")
    L.append("")
    L.append("## Instrument checks (M5)\n")
    L.append("Global: " + ", ".join(f"{k}: {'pass' if v['pass'] else 'FAIL'}" for k, v in checks["global"].items()))
    for cell in CELLS:
        ch = checks["per_cell"][cell]
        L.append(f"- {cell}: " + ", ".join(f"{k}: {'pass' if v.get('pass', v.get('pass_support_and_bands')) else 'FAIL'}"
                                            for k, v in ch.items() if isinstance(v, dict) and ("pass" in v or "pass_support_and_bands" in v)))
    L.append(f"\nCount of controls that can fail: {checks['controls_that_can_fail']} (all declared controls; C-TR failure is data).\n")
    L.append("## Raw-result and cell-summary agreement\n")
    L.append(f"raw-result.json was recomputed from the written targets-<cell>-<family>.jsonl.gz and pivot-hazards-<cell>.json files "
             f"by separate code and compared with cell-summary.json on {agree['checked_items']} primary-metric items: "
             f"{'all agree' if agree['agree'] else str(len(agree['disagreements'])) + ' DISAGREEMENTS (see raw-result.json)'}.\n")
    return "\n".join(L) + "\n"


def prior_rows(dr):
    pc = dr["per_cell"]
    rows = []
    def tri(vals, good, bad):
        if all(v == good for v in vals):
            return "held"
        if any(v in bad for v in vals):
            return "OVERTURNED"
        return "not evaluable at some cell"
    rows.append(f"(a) RR-1 replicates at all three cells: {tri([pc[c]['RR-1']['verdict'] for c in CELLS], 'DIRECTION REPLICATES', ('FAILS TO REPLICATE',))} ({ {c: pc[c]['RR-1']['verdict'] for c in CELLS} })")
    rows.append(f"(b) RR-2 holds at all three cells: {tri([pc[c]['RR-2']['verdict'] for c in CELLS], 'HULL RANK FULL', ('REVISIT TRIGGER FIRES',))} ({ {c: pc[c]['RR-2']['verdict'] for c in CELLS} })")
    cc = {c: pc[c]["RR-4"]["verdict"] for c in CELLS}
    ev = [v for v in cc.values() if v in ("SUPPORTED", "FALSIFIED")]
    rows.append(f"(c) TS1R SUPPORTED where evaluable: {'held' if ev and all(v == 'SUPPORTED' for v in ev) else ('not evaluable anywhere' if not ev else 'OVERTURNED')} ({cc}; m per cell: { {c: pc[c]['RR-4']['inputs']['m'] for c in CELLS} })")
    dd = {c: pc[c]["RR-5"]["verdict"] for c in CELLS}
    rows.append(f"(d) R2 REPLICATES / R1 least certain / R3 either way: observed {dd}")
    ee = {c: pc[c]["RR-6"]["verdict"] for c in CELLS}
    rows.append(f"(e) x(2E) modulation replicates at R2, less sure at R1: observed {ee}")
    return rows


# ---------------------------------------------------------------------------
def phase9(run, plan, spec, spec_text, ctx):
    final = run.out
    out = os.path.join(run.ck, "p9-staging")
    if os.path.exists(out):
        shutil.rmtree(out)  # transient staging from an interrupted phase 9
    os.makedirs(out)
    det = run.ck_load("p7-determinism")
    st = json.load(open(os.path.join(final, "selftest.json")))
    cprov = json.load(open(os.path.join(final, "cprov.json")))
    ver = json.load(open(os.path.join(final, "ps0prime-verification.json")))
    cells_summary, cellchecks, hazards_all, sizing_all, P1s, Us = {}, {}, {}, {}, {}, {}
    code_hashes = set()
    for cell in CELLS:
        P1 = run.ck_load(f"p1-{cell}-instances")
        U = {}
        for (ph, fam) in ((2, "F-S3"), (2, "F-PLANT"), (3, "F-RANDX"), (4, "F-AFF-1"), (5, "F-NULLF2"), (6, "F-S3-REV")):
            for D in DS:
                U[(fam, D)] = run.ck_load(f"p{ph}-{cell}-{fam}-D{D}")
                code_hashes.add(U[(fam, D)]["code_path_sha256"]["_combined"])
        run.log(f"  phase 9 [{cell}]: analysis")
        cs, hz, sz, hullchecks = analysis.analyse_cell(cell, P1, U, plan)
        cells_summary[cell] = cs
        hazards_all[cell] = hz
        sizing_all[cell] = sz
        cellchecks[cell] = analysis.instrument_checks_cell(cell, P1, U, det, ver, hullchecks, plan)
        cellchecks[cell]["C-SELF_cell"] = {"pass": P1["cell_selftest"]["pass"],
                                           "items": {i["id"]: i["pass"] for i in P1["cell_selftest"]["items"]}}
        P1s[cell] = P1
        Us[cell] = U
    global_checks = {
        "C-FIX": {"pass": bool(st.get("C-FIX_pass")), "detail": next(i for i in st["items"] if i["id"] == "C-FIX")},
        "C-SELF": {"pass": bool(st.get("C-SELF_pass")) and all(cellchecks[c]["C-SELF_cell"]["pass"] for c in CELLS),
                   "generic_items": {i["id"]: i["pass"] for i in st["items"] if i["id"] != "C-FIX"},
                   "per_cell": {c: cellchecks[c]["C-SELF_cell"] for c in CELLS}},
        "C-PROV": {"pass": bool(cprov.get("pass")), "comparisons": cprov.get("comparisons"), "mismatches": cprov.get("mismatches"),
                   "inputs_match_receipt": cprov.get("inputs_match_receipt"), "finished_at": cprov.get("finished_at")},
        "C-NULLS_code_path": {"pass": len(code_hashes) == 1, "distinct_combined_hashes": sorted(code_hashes)},
    }
    inv = analysis.invalidation(global_checks, cellchecks)
    dr = analysis.decision_rules_all(cells_summary, inv, global_checks, cellchecks)
    checks = {"global": global_checks, "per_cell": cellchecks, "invalidation": inv,
              "controls_that_can_fail": ["C-FIX", "C-SELF", "C-PROV", "C-ORACLE", "C-WIT", "C-AFF", "C-FORMS", "C-SURV",
                                         "C-HZERO", "C-TR (as data)", "C-DET", "C-PASS", "C-PROPS", "C-REV", "C-NULLS"],
              "cells_meta": {c: {"A": P1s[c]["curve"]["A"], "B": P1s[c]["curve"]["B"], "order": P1s[c]["curve"]["order"],
                                 "h": P1s[c]["curve"]["h"], "q": P1s[c]["curve"]["q"],
                                 "V": ("polynomial" if P1s[c]["V"]["is_polynomial_basis"] else "random RREF")} for c in CELLS}}
    status = "invalid_measurement" if inv["run_void"] else "completed_valid"

    # ---- orders
    for D in DS:
        S = ctx["shapes"][D]
        write_new(os.path.join(out, f"column-order-D{D}.json"),
                  json.dumps({"D": D, "C_D": S.C, "shared_across_cells": True, "order": "descending degrevlex, v_0 > ... > v_17, constant last",
                              "columns": [{"col": i, "monomial": list(m), "degree": len(m)} for i, m in enumerate(S.cols)]}))
        write_new(os.path.join(out, f"row-order-D{D}.json"),
                  json.dumps({"D": D, "R_D": S.R, "shared_across_cells": True, "rule": "row = (index of mu) * 17 + k; mu by (degree asc, sorted index tuple lex)",
                              "rows": S.row_order()}))
    # ---- references and per-target files per cell
    for cell in CELLS:
        P1, U = P1s[cell], Us[cell]
        hull_s3 = cells_summary[cell]["hull_per_family"]["F-S3"]
        ech = analysis.Echelon()
        for w in hull_s3["W_basis"]:
            ech.add(w)
        refs_out = {}
        for fam in FAMS:
            src = "F-S3" if fam in ("F-S3", "F-S3-REV") else fam
            fr = {"source_instances": src, "shortfall": P1.get(src, {}).get("ref_shortfall"), "references": {}}
            if fam == "F-PLANT":
                fr["note"] = "F-PLANT is scored against the F-S3 references and its own modal reference"
            for D in DS:
                unit = U[(fam, D)]
                for r in unit["refs"]:
                    e = fr["references"].setdefault(r["label"], {})
                    if r["label"] == "modal":
                        e.setdefault("modal_per_D", {})[f"D{D}"] = r["modal_info"]
                    e[f"D{D}"] = {kk: r.get(kk) for kk in ("rank", "one_in_R", "h_rank", "h_set", "h_strict", "h_ops", "h_pivcols",
                                                          "len_strict", "Z_size", "K_exact", "K_rank", "T_strict",
                                                          "forms_selfcheck_direct_eq_affine_at_r_ref", "self_replay_ok")}
                    mk = cells_summary[cell]["families"][fam][f"D{D}"].get("M1k_hull_rank", {})
                    if isinstance(mk, dict) and r["label"] in mk:
                        e[f"D{D}"]["K_rank_hull"] = mk[r["label"]]["K_rank_hull"]
                        e[f"D{D}"]["dim_W"] = mk[r["label"]]["dim_W"]
            for inst in P1.get(src, {}).get("refs", []) if fam != "F-PLANT" else []:
                e = fr["references"].setdefault(inst["selected_as"], {})
                e.update({"arm": "sat" if inst["s"] >= 1 else "unsat", "s": inst["s"], "stream_draw": inst["draw"],
                          "x_R": inst.get("x_R"), "a": inst.get("a"), "b": inst.get("b"), "E_hex": inst.get("E_hex"),
                          "x2E_class": inst.get("x2E_class")})
                o3 = e.get("D3", {}).get("one_in_R")
                o4 = e.get("D4", {}).get("one_in_R")
                e["D_star"] = 3 if o3 else (4 if o4 else "not reached at D <= 4")
            refs_out[fam] = fr
        write_new(os.path.join(out, f"references-{cell}.json"), jdump({"cell": cell, "families": refs_out}, compact=True))
        for fam in FAMS:
            d3 = {r["idx"]: r for r in U[(fam, 3)]["records"]}
            d4 = {r["idx"]: r for r in U[(fam, 4)]["records"]}
            hull_f = cells_summary[cell]["hull_per_family"].get(fam)
            eo = None
            if hull_f:
                eo = analysis.Echelon()
                for w in hull_f["W_basis"]:
                    eo.add(w)
            p = os.path.join(out, f"targets-{cell}-{fam}.jsonl.gz")
            tmp = p + ".tmp"
            with gzip.open(tmp, "wt") as f:
                for idx in sorted(d3):
                    ds = 3 if d3[idx]["one_in_R"] else (4 if d4[idx]["one_in_R"] else "not reached at D <= 4")
                    for r in (d3[idx], d4[idx]):
                        rr = dict(r)
                        rr["cell"] = cell
                        rr["D_star"] = ds
                        x = r.get("x_R")
                        rr["in_own_family_hull"] = (eo.reduce(x ^ hull_f["h0"]) == 0) if (eo is not None and x is not None) else None
                        rr["in_F-S3_hull"] = (ech.reduce(x ^ hull_s3["h0"]) == 0) if x is not None else None
                        f.write(json.dumps(rr, separators=(",", ":"), default=_jd) + "\n")
            os.replace(tmp, p)
        write_new(os.path.join(out, f"pivot-hazards-{cell}.json"),
                  jdump({"cell": cell, "layout": "families -> D -> reference key -> per-pivot arrays (index k = pivot step); S_k, zeros_k, band_lo, band_hi stop at the first k with S_k = 0 (truncated_at_first_S_k_0); a0, a (17-bit linear parts, bit j = r_j), hull_rank_increasing cover every pivot",
                         "families": hazards_all[cell]}, compact=True))
    # ---- summaries
    for cell in CELLS:
        cells_summary[cell]["rejections_per_stream"] = P1s[cell]["rejections"]
        cells_summary[cell]["curve"] = {k: P1s[cell]["curve"].get(k) for k in ("A", "B", "order", "h", "q", "P", "Q", "k_Q")}
        cells_summary[cell]["V"] = {k: P1s[cell]["V"].get(k) for k in ("label", "basis_b0_to_b8", "is_polynomial_basis")}
        cells_summary[cell]["tau"] = P1s[cell]["tau"]
        cells_summary[cell]["reference_shortfalls"] = {f: P1s[cell][f].get("ref_shortfall") for f in ("F-S3", "F-RANDX", "F-AFF-1", "F-NULLF2")}
        cells_summary[cell]["F-RANDX_x_R_shared_with_F-S3"] = P1s[cell]["F-RANDX"]["x_R_shared_with_F-S3_targets"]
        cells_summary[cell]["F-AFF-1_reference_x_collisions_with_F-S3_test_targets"] = P1s[cell]["F-AFF-1"]["ref_x_collides_with_F-S3_test_x"]
    summary = {"experiment_id": "EXP-CERTBIN-3f06d1", "run_id": run.args.run_id, "primary_unit": "GF(2) full-row XOR operations",
               "cells": cells_summary}
    write_new(os.path.join(out, "cell-summary.json"), jdump(summary))
    write_new(os.path.join(out, "instrument-checks.json"), jdump(checks))
    write_new(os.path.join(out, "decision-rules.json"), jdump(dr))
    ident = {}
    for cell, sz in sizing_all.items():
        for fam, dd in sz.items():
            for D, refs in dd.items():
                for lab, v in refs.items():
                    ident[f"{cell}/{fam}/{D}/{lab}"] = bool(v["saving"]["saving_set_identity_exact"] and v["saving"]["ops_set_equals_rank_sq"])
    write_new(os.path.join(out, "sizing.json"), jdump({"per_cell": sizing_all, "saving_set_identity_check": ident,
                                                        "saving_set_identity_all_pass": all(ident.values()),
                                                        "labels": "all sizes and op counts are MEASURED from the actual matrices and op logs; nothing is modeled",
                                                        "thresholds": {"per_system_warp_bytes": 32, "per_SM_bytes": 233472}}))
    indep = independent_primary(out)
    agree = agreement(cells_summary, indep)
    raw = {"run_id": run.args.run_id, "experiment_id": "EXP-CERTBIN-3f06d1", "validity_status": status,
           "derivation": "recomputed by report.independent_primary from targets-<cell>-<family>.jsonl.gz and pivot-hazards-<cell>.json (own hull, restriction, band and median code; analysis.py not called)",
           "primary": indep,
           "decision_rules_verdicts": {c: {k: {"verdict": v.get("verdict"), **({"nulls": v["nulls"]} if k == "RR-5" else {})}
                                           for k, v in dr["per_cell"][c].items() if k.startswith("RR-")} for c in CELLS},
           "RR-9": dr["RR-9"], "agreement_with_cell_summary": agree}
    write_new(os.path.join(out, "raw-result.json"), jdump(raw))
    write_new(os.path.join(out, "run-report.md"), run_report(spec, cells_summary, checks, dr, agree, status, run.args.run_id, inv))
    write_manifest_and_env(run, plan, spec, spec_text, status, checks, cells_summary, dr, agree, out, ver, cprov)
    for f in sorted(os.listdir(out)):
        if os.path.exists(os.path.join(final, f)):
            raise RuntimeError(f"{os.path.join(final, f)} exists; refusing to overwrite")
    for f in sorted(os.listdir(out)):
        os.replace(os.path.join(out, f), os.path.join(final, f))
    os.rmdir(out)


def write_manifest_and_env(run, plan, spec, spec_text, status, checks, cells_summary, dr, agree, out, ver, cprov):
    final = run.out
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    invs = [json.loads(line) for line in open(os.path.join(final, "checkpoint", "invocations.jsonl"))]
    st = json.load(open(os.path.join(final, "selftest.json")))
    plan_path = os.path.abspath(run.args.plan)
    try:
        res_json = subprocess.run([sys.executable, "-m", "orchestration.adapter", "resolve", "--role", "executor", "--json"],
                                  capture_output=True, text=True, cwd=repo).stdout
        resol = json.loads(res_json)
    except Exception as e:
        resol = {"error": repr(e)}
    session_model = os.environ.get("AUTORESEARCH_SESSION_MODEL")
    fb = bool(session_model and session_model != resol.get("resolved_model_id"))
    inference = {
        "requested_policy": "executor-implementation",
        "canonical_policy": resol.get("policy"), "backend": resol.get("backend"), "provider": resol.get("provider"),
        "adapter_resolved_model_id": resol.get("resolved_model_id"),
        "resolved_model_id": session_model,
        "model_provenance": "operator-supplied (executor session model as reported by the Claude Code runtime)",
        "model_verified": False,
        "requested_reasoning_effort": resol.get("requested_reasoning_effort"), "reasoning_effort": None,
        "fallback_allowed": True, "fallback_used": fb,
        "fallback_reason": (f"Runtime inheritance: same-session Claude Code subagents inherit the session model ({session_model}); "
                            f"the adapter binding for executor-implementation is {resol.get('resolved_model_id')} "
                            f"(DEC-20260923-4d7a19 R-1 forward rule; handoff fallback_allowed: true). Not a tier downgrade.") if fb else None,
        "degraded_requirements": [], "independent_session": False,
        "adapter_version": resol.get("adapter_version"), "config_digest": resol.get("config_digest"),
        "note": "The model wrote the implementation. Every number in this run comes from deterministic code; no model was in the computational loop.",
    }
    fd = run.ck_load("first-draw")
    phases = {}
    for name in sorted(os.listdir(run.ck)):
        if not name.endswith(".json.gz") or name.startswith("first-") or name.startswith("p9"):
            continue
        d = run.ck_load(name[:-8])
        m = d.get("_meta", d)
        phases[name[:-8]] = {k: m.get(k) for k in ("started_at", "finished_at", "wall_seconds", "peak_rss_bytes", "pid")}
    peak = max([i.get("peak_rss_bytes") or 0 for i in invs] + [p.get("peak_rss_bytes") or 0 for p in phases.values()] +
               [cprov.get("peak_rss_bytes") or 0])
    env = {
        "python_version": sys.version, "python_executable": sys.executable,
        "numpy_version": np.__version__, "numpy_location": np.__file__, "pyyaml_version": yaml.__version__,
        "numpy_required": "2.4.6 (DEC-20260923-4d7a19 R-2)", "numpy_matches_required": np.__version__ == "2.4.6",
        "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "mem_total_kB": next((line.split()[1] for line in open("/proc/meminfo") if line.startswith("MemTotal")), None),
        "sage": "not used", "scipy": "not used (not installed)",
        "env": {k: os.environ.get(k) for k in ("PYTHONDONTWRITEBYTECODE", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "AUTORESEARCH_SESSION_MODEL")},
        "rlimit_as_bytes": 4 * 1024 ** 3, "compiled_helpers": "none (pure Python + numpy)",
        "machine_sharing": "up to two other CERTBIN executors ran concurrently on this 4-core host (DEC-20260924-8e2f47 concurrency)",
    }
    write_new(os.path.join(out, "environment.json"), jdump(env))
    impl_dir = os.path.dirname(os.path.abspath(__file__))
    impl_hashes = {f: sha256_file(os.path.join(impl_dir, f)) for f in sorted(os.listdir(impl_dir))
                   if os.path.isfile(os.path.join(impl_dir, f))}
    ver_path = os.path.join(repo, "experiments", "EXP-CERTBIN-3f06d1", "verifier", "verify_cert.py")
    artifacts = {}
    for d in (final, out):
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if os.path.isfile(p) and f not in ("manifest.yaml", "stdout.log", "stderr.log", "command.txt", "implementation.md"):
                artifacts[f] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(final) for f in fs
                if not dp.startswith(os.path.join(final, "checkpoint")))
    ckbytes = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(final, "checkpoint")) for f in fs)
    inv = checks["invalidation"]
    metrics = {}
    for cell in CELLS:
        c4 = cells_summary[cell]["families"]["F-S3"]["D4"]
        metrics[cell] = {
            "F-S3_D4_T_strict_retention_family_unsat": c4["M1_retention_family_unsat"]["strict"]["retention_family"],
            "F-S3_D4_one_in_R4_unsat": {k: c4["one_in_R"]["unsat"][k] for k in ("x", "n", "rate")},
            "F-S3_D4_TS1R_m_o": [c4["M2R_TS1R"]["m"], c4["M2R_TS1R"]["o"]],
            "RR_verdicts": {k: v.get("verdict") for k, v in dr["per_cell"][cell].items() if k.startswith("RR-")}}
    manifest = {"run": {
        "id": run.args.run_id, "experiment_id": "EXP-CERTBIN-3f06d1", "task_id": "TASK-20260924-9f15a2",
        "status": status, "claim_tier": "toy",
        "code": {"commit": invs[0]["git"].get("commit"), "dirty": invs[0]["git"].get("dirty"),
                 "dirty_paths_at_first_driver_invocation": invs[0]["git"].get("status_porcelain"),
                 "impl_sha256": impl_hashes, "verifier_sha256": sha256_file(ver_path),
                 "impl_sha256_at_cprov": cprov.get("impl_sha256_at_cprov"),
                 "commands": {"cprov": cprov.get("process", {}).get("argv"), "selftest": st.get("argv"),
                              "driver_invocations": [i["argv"] for i in invs if i.get("event") == "start"],
                              "verifier": ver.get("process", {}).get("argv")},
                 "command": ("See command.txt for the exact commands as run, in order (cprov, trial plan, the frozen command "
                             "selftest.py && driver.py, the determinism command, driver --resume, the verify command, driver --resume); "
                             "per-invocation argv under run.code.commands and run.timing.invocations"),
                 "command_file": "command.txt"},
        "inference": inference,
        "environment": {"see": "environment.json", "python_version": platform.python_version(), "numpy_version": np.__version__,
                        "operating_system": platform.platform(), "architecture": platform.machine(), "sage_version": None},
        "inputs": {"specification": "experiments/EXP-CERTBIN-3f06d1/specification.yaml",
                   "specification_sha256": hashlib.sha256(spec_text).hexdigest(),
                   "specification_receipt_sha256": "78c99f8516e5e80f22d327a35d267d38bad59088329b60f5a001cc5715402564 (TASK-20260924-d3a90c)",
                   "trial_plan": "experiments/EXP-CERTBIN-3f06d1/trial-plan-v1.json",
                   "trial_plan_sha256": sha256_file(plan_path),
                   "trial_plan_mtime_utc": datetime.datetime.fromtimestamp(os.path.getmtime(plan_path), datetime.timezone.utc).isoformat(),
                   "trial_plan_written_at": plan.get("written_at"),
                   "cprov_finished_at": cprov.get("finished_at"),
                   "first_frozen_stream_draw_at": fd["at"],
                   "order_check": {"cprov_before_plan": cprov.get("finished_at", "") < plan.get("written_at", ""),
                                   "plan_before_first_draw": plan.get("written_at", "") < fd["at"]},
                   "stage1_inputs": cprov.get("inputs"),
                   "seeds": {"cells": {c: plan["cells"][c]["seeds"] for c in CELLS}, "S_selftest": plan["S_selftest"]},
                   "randomness": ["the per-cell frozen streams above (numpy PCG64, one generator per stream)",
                                  "S_selftest: selftest.py (one generator), per-cell C-SELF items PCG64(SeedSequence([S_selftest, c])), M3 bootstrap PCG64(S_selftest) per cell, M4 max-class Monte Carlo PCG64(SeedSequence([S_selftest, 100 + cell index]))",
                                  "no other source of randomness"],
                   "generator": "numpy.random.Generator(numpy.random.PCG64(seed)), one generator per stream",
                   "cells": {c: {**checks["cells_meta"][c]} for c in CELLS},
                   "parameters": {"n": 17, "m": 2, "l": 9, "D": [3, 4], "modulus": "t^17 + t^3 + 1"}},
        "timing": {"invocations": [{k: i.get(k) for k in ("event", "pid", "started_at", "at", "wall_seconds", "argv", "rc")} for i in invs],
                   "cprov": {"started_at": cprov.get("started_at"), "finished_at": cprov.get("finished_at"), "wall_seconds": cprov.get("wall_seconds")},
                   "selftest": {"started_at": st.get("started_at"), "finished_at": st.get("finished_at"), "wall_seconds": st.get("wall_seconds")},
                   "verifier": {"started_at": ver.get("started_at"), "finished_at": ver.get("finished_at"), "wall_seconds": ver.get("wall_seconds")},
                   "phases": phases},
        "resources": {"peak_rss_bytes": peak, "per_invocation_peak_rss_bytes": [i.get("peak_rss_bytes") for i in invs if i.get("event") == "end"],
                      "cpu_seconds_per_invocation": [i.get("cpu_seconds") for i in invs if i.get("event") == "end"],
                      "memory_cap": "RLIMIT_AS 4 GiB set in-process (cprov, driver)", "watchdog_seconds": 86400,
                      "workers": 1},
        "result": {
            "valid": status == "completed_valid", "invalid_reason": None if status == "completed_valid" else inv["run_void_reasons"],
            "voided_metrics": {c: inv["per_cell"][c]["voided_metrics"] for c in CELLS},
            "metrics": metrics, "RR-9": dr["RR-9"],
            "decision_rules": "decision-rules.json",
            "raw_result_agrees_with_cell_summary": agree["agree"],
            "certificate": {"kind": "none",
                            "note": ("No discrete-log, decomposition or key-recovery claim (docs/claims-and-verification.md). The "
                                     "specification's certificate_kind 'unsatisfiability_certificate (instrument only; PS0')' is "
                                     "recorded under instrument_certificates_PS0prime.")},
            "instrument_certificates_PS0prime": {
                "kind": "unsatisfiability_certificate", "role": "instrument only (C-PROPS PS0'); no solve or relation is claimed",
                "verified": bool(ver.get("all_pass")), "verifier": "experiments/EXP-CERTBIN-3f06d1/verifier/verify_cert.py",
                "verification_file": "ps0prime-verification.json",
                "verifier_separate_process": True, "verifier_imports_from_impl": ver.get("independence", {}).get("imports_from_impl"),
                "n_certificates": ver.get("n_certificates"), "n_passed": ver.get("n_passed"),
                "per_cell": ver.get("per_cell")}},
        "protocol_interpretations": plan.get("interpretations"),
        "deviations": "see implementation.md",
        "artifacts": artifacts,
        "package_bytes_excluding_checkpoint_at_phase9": total,
        "checkpoint_bytes": ckbytes,
    }}

    class NoAlias(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True
    write_new(os.path.join(out, "manifest.yaml"), yaml.dump(manifest, Dumper=NoAlias, sort_keys=False, width=120))
