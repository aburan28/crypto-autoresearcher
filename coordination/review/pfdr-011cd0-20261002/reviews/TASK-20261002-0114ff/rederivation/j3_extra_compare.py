#!/usr/bin/env python3
"""J3 after the seal, part 2: PC-1, Q6 dispersions, multiplicity histograms, planted per rung.

TASK-20261002-0114ff. Own inputs: rederivation/outputs/{relcount.jsonl.gz, cells.json,
census-fields-R12-jobs.jsonl.gz} (sealed by hash). Producer: calibration.json
(PC_1), heuristics.json (H1c, H5, multiplicity_histograms), cells.jsonl (planted
per-rung cells). The planted per-rung cells are computed here AFTER the seal with
the sealed CC-8 convention (CONV-6/7), and are labelled post-seal.
Standard library only.
"""
import collections
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
RUNS = WT + "/experiments/EXP-PFDR-011cd0/runs/"
SUB_R = ["random_sub_r0", "random_sub_r1", "random_sub_r2"]
DICK_R = ["random_dick_r0", "random_dick_r1", "random_dick_r2"]


def close(a, b, rel=1e-9):
    return a is not None and b is not None and abs(a - b) <= rel * max(1.0, abs(a), abs(b))


def main():
    own = {}
    with gzip.open(os.path.join(HERE, "outputs", "relcount.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            own[tuple(r["key"])] = r
    cells = json.load(open(os.path.join(HERE, "outputs", "cells.json")))
    cal = json.load(open(RUNS + "RUN-PFDR-011cd0-calibrate/calibration.json"))
    heu = json.load(open(RUNS + "RUN-PFDR-011cd0-analysis/heuristics.json"))
    prod_cells = [json.loads(l) for l in open(RUNS + "RUN-PFDR-011cd0-analysis/cells.jsonl")]
    design = json.load(open(RUNS + "RUN-PFDR-011cd0-p0-design/attempt-3/design.json"))
    out = {}
    # 1. PC-1 per instance
    pc = cal["PC_1"]
    rows = []
    for inst in pc["instances"]:
        k = (inst["bits"], inst["curve"], 3, "known_log", "table")
        o = own[k]
        rows.append({"key": [inst["bits"], inst["curve"]],
                     "TT_raw": [o["TT"]["n_raw"], inst["TT"]["raw"], o["TT"]["n_raw"] == inst["TT"]["raw"]],
                     "TB_raw": [o["TB"]["n_raw"], inst["TB"]["raw"], o["TB"]["n_raw"] == inst["TB"]["raw"]],
                     "TT_nonformal": [o["TT"]["n_nonformal"], inst["TT"]["nonformal"], o["TT"]["n_nonformal"] == inst["TT"]["nonformal"]],
                     "TB_nonformal": [o["TB"]["n_nonformal"], inst["TB"]["nonformal"], o["TB"]["n_nonformal"] == inst["TB"]["nonformal"]]})
    out["PC1_instances"] = {"compared": len(rows), "all_equal": all(all(v[2] for kk, v in r.items() if kk != "key") for r in rows),
                            "rows": rows, "producer_other_PC1_fields": {k: v for k, v in pc.items() if k != "instances"},
                            "own_Q5": {k: v["aggregate"] for k, v in cells["Q5_PC1"].items()}}
    # 2. Q6 vs H1c / H5
    q6 = {}
    for cm, v in cells["Q6_random_dispersion_band"].items():
        src = heu["H5"] if cm.startswith("SS") else heu["H1c"]
        p = src.get(cm, {}).get("relation_dispersion_pooled_within_curve")
        q6[cm] = {"own_pooled": v["pooled"]["D"], "producer": p, "equal": close(v["pooled"]["D"], p) if p is not None else None}
    out["Q6_vs_heuristics"] = q6
    # 3. multiplicity histograms: own random arms (r0..r2 of both families), band, completed instances
    mh = {}
    for cm, ph in heu["multiplicity_histograms"].items():
        cls, m = cm[:2], int(cm[2:])
        agg = collections.Counter()
        for k, o in own.items():
            if k[2] == m and k[0] in (30, 32) and k[3] in SUB_R + DICK_R and k[4] == ("search" if cls == "SS" else "table"):
                for M, n in o[cls]["hist_raw"].items():
                    agg[int(M)] += n
        p = {int(a): b for a, b in ph.items()}
        mh[cm] = {"equal": dict(agg) == p, "own_total": sum(agg.values()), "producer_total": sum(p.values())}
    out["multiplicity_histograms_random_band_vs_heuristics"] = mh
    # 4. planted per-rung cells (post-seal computation, sealed convention)
    census = {}
    js = json.load(open(RUNS + "RUN-PFDR-011cd0-table/attempt-1/jobs-spec.json"))
    jm = {j["name"]: j["m"] for j in js["jobs"]}
    with gzip.open(os.path.join(HERE, "outputs", "census-fields-R12-jobs.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            census[(r["bits"], r["curve"], jm[r["_file"].split("/")[-2]], r["arm"], r["mode"])] = r
    fam = ["subgroup", "small_x"] + SUB_R + ["known_null_sub", "planted_sub"]
    pmap = {r["id"]: r for r in prod_cells if r["kind"] == "planted"}
    pr = {}
    for cls in ("TT", "TB"):
        for b in (20, 22, 24, 26, 28, 30, 32):
            n = design["final_n"]["table"]["3"][str(b)]
            CA = sr = s2 = 0.0
            used = 0
            for c in range(10, 10 + n):
                if any(census[(b, c, 3, a, "table")]["status"] != "completed_valid" for a in fam):
                    continue
                if len({census[(b, c, 3, x, "table")]["fb_size"] for x in SUB_R + ["planted_sub"]}) != 1:
                    continue
                nA = own[(b, c, 3, "planted_sub", "table")][cls]["n_nonformal"]
                nr = [own[(b, c, 3, x, "table")][cls]["n_nonformal"] for x in SUB_R]
                CA += nA
                sr += sum(nr)
                mu = sum(nr) / 3.0
                s2 += sum((x - mu) ** 2 for x in nr) / 2.0
                used += 1
            CR = sr / 3.0
            V = max(s2, CR)
            SD = math.sqrt(4 * V / 3)
            z = (CA - CR) / SD
            pid = f"planted_sub|{cls}3|{b}"
            p = pmap.get(pid)
            pr[pid] = {"own": {"C_A": CA, "C_R": CR, "V": V, "z": z, "curves_used": used},
                       "producer": {k: p[k] for k in ("C_A", "C_R", "V", "z", "curves_used")} if p else None,
                       "equal": bool(p) and CA == p["C_A"] and round(3 * CR) == round(3 * p["C_R"]) and close(V, p["V"]) and close(z, p["z"]) and used == p["curves_used"]}
    out["planted_per_rung_post_seal"] = pr
    out["calibration_top_keys"] = sorted(cal.keys())
    out["calibration_cells_keys"] = sorted(cal["cells"].keys())
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    print("PC1", out["PC1_instances"]["compared"], out["PC1_instances"]["all_equal"])
    print("PC1 producer fields", json.dumps(out["PC1_instances"]["producer_other_PC1_fields"])[:1500])
    print("Q6", json.dumps(q6))
    print("MH", json.dumps(mh))
    print("planted per rung", {k: v["equal"] for k, v in pr.items()})
    print("cal cells keys", out["calibration_cells_keys"])


if __name__ == "__main__":
    main()
