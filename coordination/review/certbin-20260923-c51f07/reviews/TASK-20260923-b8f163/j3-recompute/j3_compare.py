#!/usr/bin/env python3
"""TASK-20260923-b8f163 J3: compare the validator's own aggregation
(j3_recompute.json) with the producer's cell-summary.json, pivot-hazards.json,
sizing.json and decision-rules.json. Run AFTER j3_recompute.py. Reads committed
bytes only; runs no producer code. Writes j3_compare.json and j3_table.txt."""
import gzip
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments", "EXP-CERTBIN-4e92d7", "runs", "RUN-CERTBIN-3b7e05")
FAMS = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3", "F-NULLF2"]
GR = ("rank", "set", "strict", "ops")
EPS = 1e-9


def close(a, b, eps=EPS):
    if a is None or b is None:
        return a is b
    return abs(a - b) <= eps * max(1.0, abs(a), abs(b))


def main():
    mine = json.load(open(os.path.join(HERE, "j3_recompute.json")))
    cs = json.load(open(os.path.join(RUN, "cell-summary.json")))
    ph = json.load(open(os.path.join(RUN, "pivot-hazards.json")))
    sz = json.load(open(os.path.join(RUN, "sizing.json")))
    dr = json.load(open(os.path.join(RUN, "decision-rules.json")))
    out = {"mismatches": []}
    mm = out["mismatches"]
    n_cmp = Counter()

    # 1. retention, every family / D / granularity / reference / arm
    for key, v in mine["retention"].items():
        f, D, g, lab, arm = key.split("/")
        c = cs["families"][f][D]["retention"][g].get(lab, {}).get(arm)
        n_cmp["retention"] += 1
        if c is None:
            mm.append({"what": "retention missing in cell-summary", "key": key})
            continue
        if (c["x"], c["n"]) != (v["x"], v["n"]):
            mm.append({"what": "retention", "key": key, "mine": [v["x"], v["n"]], "producer": [c["x"], c["n"]]})
    # 2. retention_family
    for key, v in mine["retention_family"].items():
        f, D, g = key.split("/")
        c = cs["families"][f][D]["retention_family_unsat"][g]
        n_cmp["retention_family"] += 1
        if not (close(c["retention_family"], v["value"]) and c["maximizing_reference"] == v["argmax_first"]
                and c["count"] == v["count"] and c["n"] == v["n"]):
            mm.append({"what": "retention_family", "key": key, "mine": [v["value"], v["argmax_first"], v["count"], v["n"]],
                       "producer": [c["retention_family"], c["maximizing_reference"], c["count"], c["n"]]})
        if f == "F-S3" and D == "D4" and g == "strict":
            for lab, (x, n, r, cp) in v["per_ref"].items():
                pc = c["per_reference"][lab]["cp95"]
                n_cmp["cp95"] += 1
                if not (close(pc[0], cp[0], 1e-7) and close(pc[1], cp[1], 1e-7)):
                    mm.append({"what": "cp95", "ref": lab, "mine": cp, "producer": pc})
    # 3. M4
    for key, v in mine["M4"].items():
        f, D = key.split("/")
        c = cs["families"][f][D]["M4_entropy"]
        n_cmp["M4"] += 1
        if not (close(c["P_sat"], v["P_sat"]) and close(c["h_P_sat"], v["h_P_sat"])):
            mm.append({"what": "P_sat/h", "key": key, "mine": [v["P_sat"], v["h_P_sat"]], "producer": [c["P_sat"], c["h_P_sat"]]})
        for g in GR:
            n_cmp["M4_g"] += 1
            if not (close(c[g]["H_bits"], v[g]["H_bits"]) and c[g]["distinct"] == v[g]["distinct"]
                    and c[g]["largest_class"] == v[g]["largest_class"]):
                mm.append({"what": "M4", "key": f"{key}/{g}", "mine": v[g], "producer": c[g]})
    # 4. M2 set, stats, per reference
    ps = [(p["ref"], p["k"], p["S_k"], p["zeros"]) for p in cs["M2"]["set"]]
    ms = [(p["ref"], p["k"], p["S_k"], p["zeros"]) for p in mine["M2"]["P2"]]
    out["M2_set_equal"] = sorted(ps) == sorted(ms)
    out["M2_set_size"] = [len(ms), len(ps)]
    out["M2_stats"] = {"mine": {k: mine["M2"]["pooled"][k] for k in ("median", "frac_in_[0.4,0.6]", "n_in_band", "min", "max")},
                       "producer": {"median": cs["M2"]["median_h"], "frac_in_[0.4,0.6]": cs["M2"]["frac_in_[0.4,0.6]"],
                                    "n_in_band": cs["M2"]["n_in_band"], "min": cs["M2"]["min_h"], "max": cs["M2"]["max_h"]}}
    for lab in ("U1", "U2", "U3", "S1", "S2"):
        a = mine["M2"]["per_ref"][lab]
        b = cs["M2"]["per_reference"][lab]
        n_cmp["M2_per_ref"] += 1
        if not (a["P2"]["n"] == b["n"] and close(a["P2"]["median"], b["median_h"]) and close(a["P2"]["frac_in_band"], b["frac_in_[0.4,0.6]"])):
            mm.append({"what": "M2 per ref", "ref": lab, "mine": a["P2"], "producer": b})
        n_cmp["K_sampled"] += 1
        if a["K_sampled"] != ph["families"]["F-S3"]["D4"][lab]["K_sampled"]:
            mm.append({"what": "K_sampled", "ref": lab, "mine": a["K_sampled"], "producer": ph["families"]["F-S3"]["D4"][lab]["K_sampled"]})
        if a["K_exact"] != ph["families"]["F-S3"]["D4"][lab]["K_exact"]:
            mm.append({"what": "K_exact", "ref": lab, "mine": a["K_exact"], "producer": ph["families"]["F-S3"]["D4"][lab]["K_exact"]})
    # 4b. every S_k / zeros_k of pivot-hazards (all families, both D) from archived per-target first zeros
    recs = {}
    for f in FAMS:
        with gzip.open(os.path.join(RUN, f"targets-{f}.jsonl.gz"), "rt") as fh:
            recs[f] = [json.loads(line) for line in fh]
    refs = json.load(open(os.path.join(RUN, "references.json")))
    hz_pairs = hz_bad = 0
    for f in FAMS:
        for D in (3, 4):
            for key, t in ph["families"][f][f"D{D}"].items():
                K = len(t["S_k"])
                if key == "modal" or key.endswith(":modal") and False:
                    pass
                pool = [r for r in recs[f] if r["D"] == D and not r["degenerate"] and key in r["refs"]]
                if key == "modal":
                    pool = [r for r in pool if r["idx"] > 100]
                fz = Counter(r["refs"][key]["replay_first_zero"] for r in pool)
                S, run_ = [], len(pool)
                for k in range(K):
                    S.append(run_)
                    run_ -= fz.get(k, 0)
                Z = [fz.get(k, 0) for k in range(K)]
                hz_pairs += 1
                if S != t["S_k"] or Z != t["zeros_k"]:
                    hz_bad += 1
                    mm.append({"what": "pivot-hazards S_k/zeros_k", "family": f, "D": D, "ref": key})
    out["pivot_hazards_Sk_zeros_recomputed"] = {"tables": hz_pairs, "mismatching": hz_bad}
    # 5. M3
    c = cs["M3"]
    m = mine["M3"]
    out["M3"] = {"producer_kind": c["kind"], "producer_note": c.get("note"), "mine_case": m["case"],
                 "counts_equal": (c["numerator"]["count"], [d["count"] for d in c["denominators"]]) == (m["numerator_count"], m["denominator_counts"]),
                 "n_equal": [d["n"] for d in c["denominators"]]}
    # 6. sizes and savings (F-S3 references)
    for key, v in mine["sizes_savings"].items():
        D, lab = key.split("/")
        c = sz["per_reference"]["F-S3"][D][lab]
        n_cmp["sizing"] += 1
        pairs = [
            (c["rank"], v["rank"]), (c["Z_size"], v["Z"]),
            (c["sizes"]["full"]["nnz"], v["full"]["nnz"]), (c["sizes"]["full"]["csr_bytes"], v["full"]["csr_bytes"]),
            (c["sizes"]["full"]["dense_bytes"], v["full"]["dense_bytes"]),
            (c["sizes"]["pruned"]["rows"], v["pruned"]["rows"]), (c["sizes"]["pruned"]["cols"], v["pruned"]["cols"]),
            (c["sizes"]["pruned"]["dense_bytes"], v["pruned"]["dense_bytes"]), (c["sizes"]["pruned"]["nnz"], v["pruned"]["nnz"]),
            (c["sizes"]["pruned"]["csr_bytes"], v["pruned"]["csr_bytes"]),
            (c["saving"]["ops_masked_full"], v["ops_masked_full"]), (c["saving"]["ops_strict"], v["ops_strict"]),
            (c["saving"]["ops_set"], v["ops_set"]), (c["saving"]["words_per_row"], v["words_per_row"])]
        if not all(a == b for a, b in pairs) or not close(c["saving"]["saving_strict"], v["saving_strict"]) \
                or not close(c["saving"]["saving_set"], v["saving_set"]):
            mm.append({"what": "sizing", "key": key, "pairs": pairs})
    # 7. decision rules
    V = mine["DR_validator"]["verdicts"]
    drc = {
        "DR-1": (dr["DR-1"]["verdict"], V["DR-1"]),
        "DR-2": (dr["DR-2"]["verdict"], V["DR-2"]),
        "DR-3": (dr["DR-3"]["verdict"], V["DR-3"]),
        "DR-4": (dr["DR-4"]["verdict"], V["DR-4"]),
        "DR-5": (dr["DR-5"]["reading"].split(" (")[0], V["DR-5"]),
        "DR-6": ((dr["DR-6"]["one_system_per_SM"], dr["DR-6"]["thousands_per_warp"]), (V["DR-6"]["one_system_per_SM"], V["DR-6"]["thousands_per_warp"])),
        "DR-7": ((dr["DR-7"]["strict_replay"], dr["DR-7"]["T_set_replay"]), (V["DR-7"]["strict_replay"], V["DR-7"]["T_set_replay"])),
    }
    out["decision_rules"] = {k: {"producer": a, "validator": b, "equal": a == b} for k, (a, b) in drc.items()}
    out["DR_inputs"] = {
        "DR-2": {"producer": dr["DR-2"]["inputs"], "validator": V["DR-2_clauses"]},
        "DR-3_K_sampled_maxref": [dr["DR-3"]["inputs"]["K_sampled_maximizing_reference"], mine["DR_validator"]["inputs"]["K_sampled_maxref"]],
        "DR-6_pruned_bytes": [dr["DR-6"]["inputs"]["pruned_dense_bytes"], V["DR-6"]["pruned_dense_bytes"]],
        "DR-7_savings": [[dr["DR-7"]["inputs"]["saving_strict"], dr["DR-7"]["inputs"]["saving_set"]],
                         [V["DR-7"]["saving_strict"], V["DR-7"]["saving_set"]]],
    }
    # arm sizes / underpowered (SR-3)
    ua = {}
    for f in FAMS:
        for D in ("D3", "D4"):
            c = cs["families"][f][D]
            ua[f"{f}/{D}"] = {"arm_sizes": c["arm_sizes"], "underpowered": c["underpowered"],
                              "SR3_expected": {a: c["arm_sizes"][a] < 100 for a in ("unsat", "sat")}}
            if {a: c["arm_sizes"][a] < 100 for a in ("unsat", "sat")} != c["underpowered"]:
                mm.append({"what": "underpowered flag", "key": f"{f}/{D}"})
    out["arms"] = ua
    out["comparisons"] = dict(n_cmp)
    json.dump(out, open(os.path.join(HERE, "j3_compare.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("arms",)}, indent=1)[:7000])


if __name__ == "__main__":
    main()
