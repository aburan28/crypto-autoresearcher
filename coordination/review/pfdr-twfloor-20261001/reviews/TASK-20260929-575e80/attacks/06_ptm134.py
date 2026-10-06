"""06 -- PTM-1 (known_log), PTM-3 (harvest-off rows), PTM-4 (structured vs random, Fisher).

Conventions (choices G-1, F3-2, F4-2, F3-3): frozen = A7; rank = S/((1/2)sqrt(rank*N));
rank1 = rank + 1; Xtotal = X_total/sqrt(r_frozen*N); c1 = frozen/2. Aggregate T per
(m, arm class) with w = 1/(N*B) (point value; intervals for the census arms are in 04).
PTM-3 quantile threshold: an instance "fires" iff its frozen ratio lies below the 0.001
quantile of the PTM-5 census-mode frozen ratios of the same m (out/ptm5_results.jsonl).
No randomness.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, RUNS, P, WT, dump, iter_jsonl  # noqa: E402
from numlib import fisher_exact  # noqa: E402


def conv_ratios(S, r_frozen, rank, N, B, attempts):
    out = {"frozen": S / (0.5 * math.sqrt(r_frozen * N)) if r_frozen > 0 else None,
           "rank": S / (0.5 * math.sqrt(rank * N)) if rank > 0 else None,
           "rank1": S / (0.5 * math.sqrt((rank + 1) * N)),
           "Xtotal": (2 * S + B + attempts + 2) / math.sqrt(r_frozen * N) if r_frozen > 0 else None}
    out["c1"] = out["frozen"] / 2 if out["frozen"] is not None else None
    return out


def agg_T(items, rkey):
    num = sum(x["S"] ** 2 / (x["N"] * x["B"]) for x in items)
    den = sum(x[rkey] * x["N"] / 4 / (x["N"] * x["B"]) for x in items)
    return num / den if den > 0 else None


def ptm5_quantiles():
    path = os.path.join(OUT, "ptm5_results.jsonl")
    vals = defaultdict(list)
    if not os.path.exists(path):
        return None
    for line in open(path):
        r = json.loads(line)
        p = r["primary"]
        if r["mode"] != "census" or p is None or p["r_frozen"] <= 0:
            continue
        vals[r["m"]].append(p["S"] / (0.5 * math.sqrt(p["r_frozen"] * r["N"])))
    q = {}
    for m, v in vals.items():
        v.sort()
        q[m] = {"n": len(v), "q001": v[max(0, int(math.floor(0.001 * (len(v) - 1))))], "min": v[0]}
    return q


def main():
    xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
    ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r"]
    res = {}

    # ---------------- PTM-1: known_log ---------------------------------------------------------
    kl = [x for x in ev if x["arm"] == "known_log"]
    det = []
    for x in kl:
        c = conv_ratios(x["S"], x["r_frozen"], x["rank"], x["N"], x["B"], x["attempts"])
        det.append({"key": [x["bits"], x["curve"], x["mode"]], "premise_violation":
                    x["formal_kind"] == "known_log" and x["formal_rank"] == x["B"] - 1, **c})
    kl_census_all = [x for x in xs if x["arm"] == "known_log" and x["mode"] == "census" and x["src"] != "stage-r"]
    res["PTM1_known_log"] = {
        "evaluable_on": sum(1 for x in kl if x["mode"] == "on"),
        "census_rows": len(kl_census_all),
        "census_not_evaluable_reasons": dict(Counter(x["excl_reason"] for x in kl_census_all if not x["evaluable"])),
        "census_relations_zero": sum(1 for x in kl_census_all if x.get("relations") == 0),
        "census_terminated_by": dict(Counter(x.get("terminated_by") for x in kl_census_all)),
        "all_classified_premise_violation": all(d["premise_violation"] for d in det),
        "below_0_9_by_convention": {c: sum(1 for d in det if d[c] is not None and d[c] < 0.9)
                                     for c in ("frozen", "rank", "rank1", "Xtotal", "c1")},
        "min_max_by_convention": {c: [min(d[c] for d in det if d[c] is not None),
                                      max(d[c] for d in det if d[c] is not None)]
                                  for c in ("frozen", "rank", "rank1", "Xtotal", "c1")},
        "aggregate_T_on": {"frozen": agg_T(kl, "r_frozen"), "rank": agg_T(kl, "rank")},
        "detail": sorted(det, key=lambda d: d["key"])}

    # j0_coset alongside (premise audit object of F3)
    jc = [x for x in ev if x["arm"] == "j0_coset" and x["mode"] == "on"]
    jdet = [conv_ratios(x["S"], x["r_frozen"], x["rank"], x["N"], x["B"], x["attempts"]) for x in jc]
    res["j0_coset_on"] = {"n": len(jc),
                          "below_0_9_by_convention": {c: sum(1 for d in jdet if d[c] is not None and d[c] < 0.9)
                                                      for c in ("frozen", "rank", "rank1", "Xtotal", "c1")},
                          "min_max_by_convention": {c: [min(d[c] for d in jdet), max(d[c] for d in jdet)]
                                                    for c in ("frozen", "rank", "rank1", "Xtotal", "c1")},
                          "formal_rows_fed_share_mean": sum(
                              (x["rowsformal_TT"] + x["rowsformal_TB"] + x["rowsformal_SS"]) / max(1, sum(x["fed"].values()))
                              for x in jc) / len(jc)}

    # ---------------- PTM-3: harvest-off rows ------------------------------------------------------
    q5 = ptm5_quantiles()
    res["PTM3_ptm5_census_quantiles"] = q5
    cen_rand = [x for x in ev if x["mode"] == "census" and x["cls"] == "random"]
    def count_block(items, mkey=lambda x: x["m"]):
        out = {}
        for c in ("frozen", "rank", "rank1", "Xtotal", "c1"):
            cnt = Counter()
            for x in items:
                v = conv_ratios(x["S"], x["r_frozen"], x["rank"], x["N"], x["B"], x["attempts"])[c]
                if v is not None and v < 0.9:
                    cnt[f"m{mkey(x)}"] += 1
            out[c] = {"fire": sum(cnt.values()), "by_m": dict(cnt)}
        if q5:
            cnt = Counter()
            for x in items:
                m = mkey(x)
                v = x["S"] / (0.5 * math.sqrt(x["r_frozen"] * x["N"]))
                if m in q5 and v < q5[m]["q001"]:
                    cnt[f"m{m}"] += 1
            out["quantile_q001_ptm5"] = {"fire": sum(cnt.values()), "by_m": dict(cnt)}
        return out
    res["PTM3_census_random"] = {"n": len(cen_rand), "n_by_m": dict(Counter(f"m{x['m']}" for x in cen_rand)),
                                 "fires": count_block(cen_rand),
                                 "aggregate_T_frozen_by_m": {f"m{m}": agg_T([x for x in cen_rand if x["m"] == m], "r_frozen")
                                                             for m in (3, 4, 5)}}
    # R05 / R06 rows (harvest off) -----------------------------------------------------------------
    sweep = []
    for run in ("reg-off-sweep-minfill-20260926", "reg-off-sweep-arity-minfill-20260926"):
        for r in iter_jsonl(os.path.join(RUNS, P + run, "rows.jsonl.gz")):
            if str(r.get("method", "")).startswith("ic_m") and r.get("engine") == "mitm":
                m = int(r["method"][4:])
                sweep.append({"run": run, "m": m, "fb": r["fb"], "bits": r["bits"], "curve": r["curve"],
                              "S": r["s3_solves"], "r_frozen": r["relations"], "rank": r["rank"], "N": r["N"],
                              "B": r["fb_size"], "attempts": r["attempts"], "ok": r["ok"]})
    sweep_ok = [x for x in sweep if x["ok"] and x["r_frozen"] > 0]
    res["PTM3_R05_R06"] = {"rows": len(sweep), "evaluable": len(sweep_ok),
                           "n_by_run_m": dict(Counter(f"{x['run']}|m{x['m']}" for x in sweep_ok)),
                           "fires": count_block(sweep_ok),
                           "aggregate_T_frozen": {f"{run}|m{m}|{fb}": agg_T(
                               [x for x in sweep_ok if x["run"] == run and x["m"] == m and x["fb"] == fb], "r_frozen")
                               for run in ("reg-off-sweep-minfill-20260926", "reg-off-sweep-arity-minfill-20260926")
                               for m in (2, 3, 4, 5) for fb in ("small_x", "random", "subgroup")
                               if any(x["run"] == run and x["m"] == m and x["fb"] == fb for x in sweep_ok)},
                           "min_frozen": min(conv_ratios(x["S"], x["r_frozen"], x["rank"], x["N"], x["B"], x["attempts"])["frozen"]
                                             for x in sweep_ok)}
    # Stage 0 floor rows: archived ratios (cross-check only)
    s0 = os.path.join(WT, "experiments", "EXP-PFDR-7c8bf2", "runs", "RUN-PFDR-7c8bf2-stage0", "floor-rows.jsonl.gz")
    s0rows = list(iter_jsonl(s0))
    res["PTM3_stage0_floor_rows"] = {"rows": len(s0rows),
                                     "ratio_lt_0_9": sum(1 for r in s0rows if r.get("ratio") is not None and r["ratio"] < 0.9),
                                     "ratio_lt_1_0": sum(1 for r in s0rows if r.get("ratio") is not None and r["ratio"] < 1.0),
                                     "min_ratio": min(r["ratio"] for r in s0rows if r.get("ratio") is not None),
                                     "fields": sorted(s0rows[0].keys())}

    # ---------------- PTM-4: structured vs random (on mode) -------------------------------------
    p4 = {}
    for conv in ("frozen", "rank", "Xtotal"):
        for m in (3, 4, 5, "all"):
            def sel(x, cl):
                return x["mode"] == "on" and x["cls"] == cl and (m == "all" or x["m"] == m)
            st = [x for x in ev if sel(x, "structured")]
            ra = [x for x in ev if sel(x, "random")]
            def fires(items):
                return sum(1 for x in items if (conv_ratios(x["S"], x["r_frozen"], x["rank"], x["N"], x["B"], x["attempts"])[conv] or 9) < 0.9)
            a, c = fires(st), fires(ra)
            two, gr = fisher_exact(a, len(st) - a, c, len(ra) - c)
            p4[f"{conv}|m{m}"] = {"structured": [a, len(st)], "random": [c, len(ra)],
                                  "rate_structured": a / len(st), "rate_random": c / len(ra),
                                  "fisher_two_sided": two, "fisher_structured_greater": gr}
    res["PTM4_fisher"] = p4
    dump("06_ptm134.json", res)
    print(json.dumps({k: v for k, v in res.items() if k != "PTM1_known_log"}, indent=1, default=str)[:9000])
    print(json.dumps({k: v for k, v in res["PTM1_known_log"].items() if k != "detail"}, indent=1))


if __name__ == "__main__":
    main()
