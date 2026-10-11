"""02 -- F3/F4 row-level checks (F3-3, F3-5, F4-2, F4-3, F4-4). No randomness.

* G5 recomputed from fields on every firing row and every census twin, and on all rows;
* table_entries <= 2*table_s3_solves, and the closed forms of the table build
  (h = 2: entries == B^2, table_s3 == B(B+1)/2; h = 3: table_s3 == B(B+1)/2 + B(B+1)(2B+1)/6
  and entries <= 2*u3, u3 = B(B+1)(2B+1)/6, the last-level units);
* X_total = 2S + B + attempts + 2 and X_cmp = table_entries + B + enc_rec ratios on every
  evaluable instance; survivors among the firing set;
* c = 1 (ratio/2) on every evaluable census-mode row (random arms singled out);
* per-arm premise fields (formal kind/rank, formal rows fed).
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump  # noqa: E402


def load():
    return [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]


def g5(x):
    return x["enc_rec"] == 2 * (x["S"] - x["table_s3"]) - x["degenerate"]


def table_forms(x):
    B, h, ts, ent = x["B"], x["h"], x["table_s3"], x["table_entries"]
    out = {"entries_le_2_table_s3": ent <= 2 * ts}
    if h == 2:
        out["h2_entries_eq_B2"] = ent == B * B
        out["h2_table_s3_eq_B(B+1)/2"] = ts == B * (B + 1) // 2
    elif h == 3:
        u2 = B * (B + 1) // 2
        u3 = B * (B + 1) * (2 * B + 1) // 6
        out["h3_table_s3_eq_u2_plus_u3"] = ts == u2 + u3
        out["h3_entries_le_2_u3"] = ent <= 2 * u3
        out["h3_entries_deficit_from_2u3"] = 2 * u3 - ent
    return out


def main():
    xs = load()
    main_j0 = [x for x in xs if x["src"] != "stage-r"]
    ev = [x for x in main_j0 if x["evaluable"]]
    fire = [x for x in ev if x["ratio"] < 0.9]
    idx = {(x["panel"], x["bits"], x["curve"], x["m"], x["arm"], x["mode"]): x for x in main_j0}
    twins = []
    for x in fire:
        t = idx.get((x["panel"], x["bits"], x["curve"], x["m"], x["arm"], "census"))
        twins.append(t)
    res = {}

    # --- G5 -------------------------------------------------------------------------------
    def g5_block(rows):
        c = Counter()
        bad = []
        for x in rows:
            if x is None or "enc_rec" not in x:
                c["missing"] += 1
                continue
            ok = g5(x) and x["identity_ok"] and x["search_charged"] == x["S"] - x["table_s3"]
            c["pass" if ok else "fail"] += 1
            if not ok:
                bad.append({k: x[k] for k in ("panel", "bits", "curve", "m", "arm", "mode")})
        return {"counts": dict(c), "failures": bad}

    res["G5_firing_rows"] = g5_block(fire)
    res["G5_census_twins"] = g5_block(twins)
    res["G5_all_rows_with_harvest"] = g5_block([x for x in xs if "enc_rec" in x])
    res["degenerate_roots_total_firing"] = sum(x["degenerate"] for x in fire)

    # --- table ---------------------------------------------------------------------------
    def table_block(rows):
        c = Counter()
        bad = []
        for x in rows:
            if x is None or "table_entries" not in x:
                c["missing"] += 1
                continue
            f = table_forms(x)
            for k, v in f.items():
                if isinstance(v, bool):
                    c[f"{k}:{v}"] += 1
            if not all(v for v in f.values() if isinstance(v, bool)):
                bad.append({"key": [x[k] for k in ("panel", "bits", "curve", "m", "arm", "mode")], **f})
        return {"counts": dict(c), "failures": bad}

    res["table_firing_rows"] = table_block(fire)
    res["table_census_twins"] = table_block(twins)
    res["table_all_rows"] = table_block([x for x in xs if "table_entries" in x])
    res["h3_entry_deficit_firing_m5"] = [table_forms(x).get("h3_entries_deficit_from_2u3")
                                         for x in fire if x["h"] == 3]

    # --- X_total / X_cmp ---------------------------------------------------------------------
    per = []
    for x in ev:
        Xf = 2 * x["S"]
        Xt = Xf + x["B"] + x["attempts"] + 2
        Xc = x["table_entries"] + x["B"] + x["enc_rec"]
        rf = x["r_frozen"]
        q = {"key": [x[k] for k in ("panel", "bits", "curve", "m", "arm", "mode")], "cls": x["cls"],
             "ratio": x["ratio"], "ratio_Xtotal": Xt / math.sqrt(rf * x["N"]),
             "ratio_Xcmp": Xc / math.sqrt(rf * x["N"]),
             "free_share": (x["B"] + x["attempts"] + 2) / Xf, "Xcmp_over_2S": Xc / Xf}
        per.append(q)
    fk = {tuple(q["key"]) for q in per if q["ratio"] < 0.9}
    surv_t = [q for q in per if tuple(q["key"]) in fk and q["ratio_Xtotal"] < 0.9]
    surv_c = [q for q in per if tuple(q["key"]) in fk and q["ratio_Xcmp"] < 0.9]
    new_t = [q for q in per if q["ratio_Xtotal"] < 0.9 and tuple(q["key"]) not in fk]
    res["Xtotal"] = {
        "firing_frozen": len(fk),
        "survive_Xtotal": len(surv_t),
        "survive_Xtotal_by_cls": dict(Counter(q["cls"] for q in surv_t)),
        "survive_Xcmp": len(surv_c),
        "survive_Xcmp_by_cls": dict(Counter(q["cls"] for q in surv_c)),
        "new_firings_under_Xtotal": len(new_t),
        "dropped_by_Xtotal": sorted([q["key"] for q in per if tuple(q["key"]) in fk and q["ratio_Xtotal"] >= 0.9]),
        "max_free_share_firing": max(q["free_share"] for q in per if tuple(q["key"]) in fk),
        "max_free_share_all": max(q["free_share"] for q in per),
        "free_share_by_m_bits_max": {},
        "Xcmp_over_2S_range_firing": [min(q["Xcmp_over_2S"] for q in per if tuple(q["key"]) in fk),
                                      max(q["Xcmp_over_2S"] for q in per if tuple(q["key"]) in fk)],
        "firing_rows_detail": sorted([{k: q[k] for k in ("key", "cls", "ratio", "ratio_Xtotal", "ratio_Xcmp", "free_share")}
                                      for q in per if tuple(q["key"]) in fk], key=lambda d: d["ratio"]),
    }
    fs = defaultdict(float)
    for q in per:
        k = f"m{q['key'][3]}|b{q['key'][1]}"
        fs[k] = max(fs[k], q["free_share"])
    res["Xtotal"]["free_share_by_m_bits_max"] = dict(sorted(fs.items()))

    # --- c = 1 -------------------------------------------------------------------------------
    cen = [x for x in ev if x["mode"] == "census"]
    c1 = Counter()
    c1_rows = []
    for x in cen:
        r1 = x["ratio"] / 2
        if r1 < 0.9:
            c1[f"{x['cls']}|m{x['m']}"] += 1
            c1_rows.append({"key": [x[k] for k in ("panel", "bits", "curve", "m", "arm")], "cls": x["cls"],
                            "ratio_c1": r1})
    res["c1_census"] = {"evaluable_census": len(cen),
                        "evaluable_census_by_cls_m": dict(Counter(f"{x['cls']}|m{x['m']}" for x in cen)),
                        "firing_c1_by_cls_m": dict(c1), "firing_c1_total": sum(c1.values()),
                        "random_arm_firing_c1": sum(v for k, v in c1.items() if k.startswith("random|")),
                        "min_ratio_c1_by_cls_m": {}}
    mn = defaultdict(lambda: 9e9)
    for x in cen:
        k = f"{x['cls']}|m{x['m']}"
        mn[k] = min(mn[k], x["ratio"] / 2)
    res["c1_census"]["min_ratio_c1_by_cls_m"] = dict(sorted(mn.items()))
    res["c1_on"] = {"firing_c1_by_cls_m": dict(Counter(f"{x['cls']}|m{x['m']}" for x in ev
                                                        if x["mode"] == "on" and x["ratio"] / 2 < 0.9)),
                    "evaluable_on_by_cls_m": dict(Counter(f"{x['cls']}|m{x['m']}" for x in ev if x["mode"] == "on"))}
    res["census_min_frozen_ratio_by_cls_m"] = {}
    mf = defaultdict(lambda: 9e9)
    for x in cen:
        k = f"{x['cls']}|m{x['m']}"
        mf[k] = min(mf[k], x["ratio"])
    res["census_min_frozen_ratio_by_cls_m"] = dict(sorted(mf.items()))

    # --- premise fields per arm ----------------------------------------------------------------
    prem = defaultdict(lambda: {"n": 0, "formal_kind": Counter(), "formal_rank_minus_expect": Counter(),
                                "fr_over_B": [], "rows_formal_on": 0, "rows_fed_on": 0,
                                "formal_rank_values": Counter()})
    for x in main_j0:
        if "formal_kind" not in x:
            continue
        a = prem[x["arm"] if x["cls"] in ("known_log", "j0_coset") else x["cls"] + ("_j0" if x["panel"] == "j0" else "")]
        a["n"] += 1
        a["formal_kind"][x["formal_kind"]] += 1
        a["formal_rank_values"][x["formal_rank"]] += 1
        a["fr_over_B"].append(x["formal_rank"] / x["B"])
        if x["arm"] == "known_log":
            a["formal_rank_minus_expect"][x["formal_rank"] - (x["B"] - 1)] += 1
        elif x["arm"] == "j0_coset":
            a["formal_rank_minus_expect"][3 * x["formal_rank"] - 2 * x["B"]] += 1
        if x["mode"] == "on":
            a["rows_formal_on"] += x["rowsformal_TT"] + x["rowsformal_TB"] + x["rowsformal_SS"]
            a["rows_fed_on"] += sum(x["fed"].values())
    pout = {}
    for k, a in prem.items():
        pout[k] = {"n": a["n"], "formal_kind": dict(a["formal_kind"]),
                   "formal_rank_minus_expected": dict(a["formal_rank_minus_expect"]),
                   "formal_rank_over_B_min_max": [min(a["fr_over_B"]), max(a["fr_over_B"])],
                   "nonzero_formal_rank_instances": sum(v for kk, v in a["formal_rank_values"].items() if kk),
                   "rows_formal_emitted_on_total": a["rows_formal_on"], "rows_fed_on_total": a["rows_fed_on"]}
    res["premise_fields"] = pout
    # j0_coset omega-closed orbits = formal_rank/2
    orb = [(x["bits"], x["curve"], x["mode"], x["B"], x["formal_rank"], x["formal_rank"] // 2)
           for x in main_j0 if x["arm"] == "j0_coset" and "formal_rank" in x]
    res["j0_coset_orbits"] = {"records": len(orb),
                              "all_B_eq_3_orbits": all(B == 3 * o for _, _, _, B, fr, o in orb),
                              "orbits_by_bits": {str(b): sorted({o for bb, _, _, _, _, o in orb if bb == b})
                                                 for b in sorted({o[0] for o in orb})}}
    dump("02_f3_f4_checks.json", res)
    short = {k: v for k, v in res.items() if k not in ("Xtotal",)}
    print(json.dumps(short, indent=1, default=str)[:7000])
    print(json.dumps({k: v for k, v in res["Xtotal"].items() if k not in ("firing_rows_detail", "dropped_by_Xtotal")}, indent=1))


if __name__ == "__main__":
    main()
