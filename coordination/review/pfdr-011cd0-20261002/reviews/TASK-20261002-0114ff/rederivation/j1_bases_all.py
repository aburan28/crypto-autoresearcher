#!/usr/bin/env python3
"""J1 (c) extension: every written base (bases.jsonl.gz of every R12 and R13 job) rebuilt from
the specification's arm seeds (cells.arms.bases) and compared point by point.

TASK-20261002-0114ff. Reuses the validator's own g4r_verify.rebuild (factor_base.py and
curve.py for CONSTRUCTION only). Also checks (p, a, b, N, P) against design.json and |F|
against s_sub / s_dick. Standard library only (plus the construction modules).
"""
import gzip
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g4r_verify", os.path.join(HERE, "g4r_verify.py"))
g4r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g4r)


def main():
    curve_m, fbm = g4r.load_engine()
    design = json.load(open(g4r.DESIGN))
    dc = {(c["bits"], c["curve"]): c for c in design["curves"]}
    tot, bad, per_arm = 0, [], {}
    for run, jd in g4r.RUNS.items():
        for job in sorted(os.listdir(jd)):
            fp = os.path.join(jd, job, "bases.jsonl.gz")
            if not os.path.exists(fp):
                continue
            with gzip.open(fp, "rt") as fh:
                for line in fh:
                    r = json.loads(line)
                    k = (r["bits"], r["curve"], r["m"], r["arm"])
                    d = dc[(k[0], k[1])]
                    E = curve_m.Curve(r["p"], r["a"], r["b"], r["N"])
                    fb, expect = g4r.rebuild(fbm, E, tuple(r["P"]), r["arm"], r["curve"], d["sizes"][str(r["m"])])
                    ok_pts = [tuple(x) for x in fb.points] == [tuple(x) for x in r["points"]]
                    ok_curve = (d["p"], d["a"], d["b"], d["N"], tuple(d["P"])) == (r["p"], r["a"], r["b"], r["N"], tuple(r["P"]))
                    ok_size = len(r["points"]) == expect
                    tot += 1
                    per_arm.setdefault(f"{run}|{r['arm']}", [0, 0])
                    per_arm[f"{run}|{r['arm']}"][0] += 1
                    if ok_pts and ok_curve and ok_size:
                        per_arm[f"{run}|{r['arm']}"][1] += 1
                    elif len(bad) < 50:
                        bad.append({"run": run, "key": list(k), "points_equal": ok_pts, "curve_equal": ok_curve, "size_equal": ok_size})
    out = {"bases_records": tot, "all_equal": not bad, "failures": bad, "per_run_arm_records_and_equal": per_arm}
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    print(json.dumps({"bases_records": tot, "all_equal": not bad, "failures": bad[:5]}))


if __name__ == "__main__":
    main()
