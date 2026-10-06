#!/usr/bin/env python3
"""J3/J1(f) after the seal: own per-instance counts vs the harvester's in-process relcount.

TASK-20261002-0114ff. Own counts: rederivation/outputs/relcount.jsonl.gz (sealed by
hash). Harvester counts: the 'harvest' block of every census row of the R12 and
R13 root rows.jsonl.gz (TT, TB at_stop = whole table; SS at_X_fix), and of the
R13 rows for TT/TB (digest-only classes, counted in process).
Compared exactly, per instance and class:
  relations_nonformal  vs own n_nonformal          (the count entering z)
  relations_distinct   vs own n_raw                (formal included)
  R_star               vs own R_star (nonformal; equal to formal-included R_star
                                      except on known_log, reported separately)
  multiplicity_histogram vs own hist_raw (and hist_nonformal)
  relations_distinct_sign vs own n_signonly_nonformal (generic arms)
  star_groups_with_ge2_star_rows (TB) vs own TB vs TB_B difference indicator
Standard library only.
"""
import collections
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
RUNS = WT + "/experiments/EXP-PFDR-011cd0/runs/"


def main():
    own = {}
    with gzip.open(os.path.join(HERE, "outputs", "relcount.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            own[tuple(r["key"])] = r
    res = collections.Counter()
    mism = []
    tb_ge2 = []
    r13_ttb_vs_r12 = collections.Counter()
    r13_ttb_mism = []
    for run, rd, mode in (("R12", "RUN-PFDR-011cd0-table", "table"), ("R13", "RUN-PFDR-011cd0-search", "search")):
        with gzip.open(RUNS + rd + "/rows.jsonl.gz", "rt") as fh:
            for line in fh:
                r = json.loads(line)
                m = int(r["method"].replace("ic_m", ""))
                key = (r["bits"], r["curve"], m, r["arm"], r["mode"])
                o = own.get(key)
                if o is None:
                    res["no_own_record"] += 1
                    continue
                h = r["harvest"]
                classes = [("TT", "at_stop"), ("TB", "at_stop")] if mode == "table" else [("SS", "at_X_fix")]
                for cls, scope in classes:
                    hb = h[cls][scope]
                    oc = o[cls]
                    kl = r["arm"] == "known_log"
                    checks = {
                        "relations_nonformal": hb["relations_nonformal"] == oc["n_nonformal"],
                        "relations_distinct": hb["relations_distinct"] == oc["n_raw"],
                        "multiplicity_histogram_vs_raw": {int(k): v for k, v in hb["multiplicity_histogram"].items()} ==
                        {int(k): v for k, v in oc["hist_raw"].items()},
                    }
                    if not kl:
                        checks["R_star"] = hb["R_star"] == oc["R_star"]
                        checks["relations_distinct_sign"] = hb["relations_distinct_sign"] == oc["n_signonly_nonformal"]
                    for k, v in checks.items():
                        res[f"{run}|{cls}|{k}|{'equal' if v else 'DIFFER'}"] += 1
                    if not all(checks.values()):
                        if len(mism) < 200:
                            mism.append({"key": list(key), "class": cls, "failed": [k for k, v in checks.items() if not v],
                                         "harvester": {k: hb[k] for k in ("relations_nonformal", "relations_distinct", "R_star",
                                                                         "relations_distinct_sign", "multiplicity_histogram")},
                                         "own": {k: oc[k] for k in ("n_nonformal", "n_raw", "R_star", "n_signonly_nonformal", "hist_raw")}})
                    if cls == "TB" and hb.get("star_groups_with_ge2_star_rows"):
                        tb_ge2.append({"key": list(key), "star_groups_with_ge2_star_rows": hb["star_groups_with_ge2_star_rows"],
                                       "own_TB": oc["n_nonformal"], "own_TB_B": o["TB_B"]["n_nonformal"]})
                if mode == "search":
                    # in-process TT/TB of the search instance vs own R12 counts of the same (bits, curve, m, arm)
                    tkey = (r["bits"], r["curve"], m, r["arm"], "table")
                    ot = own.get(tkey)
                    for cls in ("TT", "TB"):
                        hb = h[cls]["at_stop"]
                        if ot is None:
                            r13_ttb_vs_r12["no_R12_key"] += 1
                            continue
                        ok = hb["relations_nonformal"] == ot[cls]["n_nonformal"] and hb["relations_distinct"] == ot[cls]["n_raw"]
                        r13_ttb_vs_r12[f"{cls}|{'equal' if ok else 'DIFFER'}"] += 1
                        if not ok and len(r13_ttb_mism) < 50:
                            r13_ttb_mism.append({"key": list(key), "class": cls, "harvester_R13": hb["relations_nonformal"],
                                                 "own_R12": ot[cls]["n_nonformal"]})
                res[f"{run}|instances"] += 1
    out = {"counts": dict(sorted(res.items())), "mismatches_first_200": mism,
           "TB_instances_with_ge2_star_rows": tb_ge2,
           "R13_in_process_TT_TB_vs_own_R12": dict(r13_ttb_vs_r12), "R13_TT_TB_mismatches": r13_ttb_mism}
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    print(json.dumps(out["counts"], indent=1))
    print("TB ge2:", len(tb_ge2), json.dumps(tb_ge2[:30]))
    print("R13 TT/TB vs R12:", out["R13_in_process_TT_TB_vs_own_R12"])
    print("mismatch examples:", json.dumps(mism[:5])[:3000])


if __name__ == "__main__":
    main()
