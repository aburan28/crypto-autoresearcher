"""R0: regenerate the ladder tables, slopes, labels, band table and iteration-count
tables of EXP-PFDR-cbdefb from runs/*/raw-result.json ONLY, and diff against
analysis.json / analysis.md / execution-report.yaml.

Red Team TASK-20260904-3a2ff5.  Reads only; writes only its own JSON output.
"""
import json, math, os, sys, collections

ROOT = "/home/user/crypto-autoresearcher"
PKG = os.path.join(ROOT, "experiments/EXP-PFDR-cbdefb")
RUNS = os.path.join(PKG, "runs")
OUT = os.path.join(ROOT, "coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5")

LADDER = [f"RUN-PFDR-cbdefb-m2-s{s}-p{p}" for s in (1,2,3,4,5) for p in (4099,16411,65537)]

def load(run):
    with open(os.path.join(RUNS, run, "raw-result.json")) as fh:
        return json.load(fh)

# ---------------------------------------------------------------- per-draw extraction
# A "system record" is closure.measure_system's dict.  The ITERATION-COUNT RULE
# (contract invalidation rule 3) invalidates a FALL ENTRY whose iteration_count == 1.
def apply_count1_rule(sysrec):
    """Return (d_ff, d_lf, n_invalidated, invalidated_saturated) after rule 3."""
    hist = sysrec.get("history", [])
    falls, inval, sat = [], 0, 0
    for h in hist:
        if not h.get("fall"):
            continue
        if h.get("iteration_count") == 1:
            inval += 1
            if h.get("W0_saturated") is True:
                sat += 1
            continue
        falls.append(h["D"])
    return (falls[0] if falls else None, falls[-1] if falls else None, inval, sat)

def arm_systems(raw, arm):
    """Yield system records for one arm of one cell."""
    if arm == "semaev":
        for d in raw["raw"]["draws"]:
            yield d["semaev"]
    elif arm == "noncurve":
        for d in raw["raw"]["noncurve"]:
            yield d["result"] if "result" in d else d
    elif arm == "null1":
        for d in raw["raw"]["draws"]:
            for o in d.get("null1", []):
                yield o["result"]
    elif arm == "null2":
        for o in raw["raw"].get("null2_objects", []):
            yield o["result"]
    elif arm == "null3":
        for o in raw["raw"].get("null3_objects", []):
            yield o["result"]

def cell_summary(raw, arm):
    recs = [r for r in arm_systems(raw, arm)]
    out = {"n": len(recs), "degenerate": 0, "d_ff": collections.Counter(),
           "d_lf": collections.Counter(), "d_lf_uncensored": collections.Counter(),
           "raw_pairs": collections.Counter(), "right_censored": 0,
           "no_fall_in_window": 0, "single_fall": 0, "it1": 0, "it1_sat": 0,
           "min_iter": [], "closure_eq_graded": [], "routes": collections.Counter(),
           "engines": set(), "cross_checked": 0, "cross_agree": True,
           "V_complete_at_fall": collections.Counter(),
           "Z_sizes": collections.Counter(), "dim_V_at_Dmax": [], "dim_I_at_Dmax": []}
    live = []
    for r in recs:
        if r.get("degenerate"):
            out["degenerate"] += 1
            continue
        live.append(r)
        dff, dlf, inval, sat = apply_count1_rule(r)
        out["d_ff"][str(dff)] += 1
        out["d_lf"][str(dlf)] += 1
        out["raw_pairs"][f"({r.get('d_ff')}, {r.get('d_lf')})"] += 1
        cens = bool(r.get("right_censored"))
        out["right_censored"] += cens
        if not cens:
            out["d_lf_uncensored"][str(dlf)] += 1
        out["no_fall_in_window"] += bool(r.get("no_fall_in_window"))
        out["single_fall"] += bool(r.get("single_fall_degree"))
        out["it1"] += inval; out["it1_sat"] += sat
        if r.get("min_iteration_count_at_falls") is not None:
            out["min_iter"].append(r["min_iteration_count_at_falls"])
        out["closure_eq_graded"].append(r.get("closure_dff_equals_graded_dff"))
        cert = r.get("certificate", {})
        out["routes"][cert.get("route", "none")] += 1
        out["Z_sizes"][cert.get("Z_size")] += 1
        out["engines"].add(r.get("engine"))
        cc = r.get("cross_check")
        if cc:
            out["cross_checked"] += 1
            out["cross_agree"] = out["cross_agree"] and bool(cc.get("agree"))
        # V_complete_at_D at the (raw) first fall degree
        for h in r.get("history", []):
            if h.get("fall"):
                out["V_complete_at_fall"][str(h.get("V_complete_at_D"))] += 1
        if r.get("history"):
            out["dim_V_at_Dmax"].append(r["history"][-1]["dim_V"])
            di = r["history"][-1].get("dim_I_at_D")
            out["dim_I_at_Dmax"].append(di)
    out["min_iter"] = min(out["min_iter"]) if out["min_iter"] else None
    out["closure_eq_graded"] = (all(x is True for x in out["closure_eq_graded"])
                               if out["closure_eq_graded"] else None)
    out["engines"] = sorted(x for x in out["engines"] if x)
    for k in ("d_ff","d_lf","d_lf_uncensored","raw_pairs","routes","V_complete_at_fall"):
        out[k] = dict(out[k])
    out["Z_sizes"] = {str(k): v for k, v in out["Z_sizes"].items()}
    return out

def main():
    table = {}
    for run in LADDER:
        raw = load(run)
        cell = raw["metrics"]["cell"]
        s, p = cell["s"], cell["primes"][0]
        for arm in ("semaev","null1","null2","null3","noncurve"):
            table[f"{s},{p},{arm}"] = cell_summary(raw, arm)
        table[f"{s},{p},__cell__"] = {"n": cell["n"], "D_max": cell["D_max"],
            "columns_at_Dmax": cell["columns_at_Dmax"], "engine": cell["engine"]}
    with open(os.path.join(OUT, "r0_regenerated_ladder.json"), "w") as fh:
        json.dump(table, fh, indent=1, sort_keys=True, default=str)
    print("cells written:", len(table))

if __name__ == "__main__":
    main()
