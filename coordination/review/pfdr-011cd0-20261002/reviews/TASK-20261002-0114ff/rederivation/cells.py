#!/usr/bin/env python3
"""J3 blind re-derivation, step 2: cells (Q1-Q6) from the per-instance counts.

TASK-20261002-0114ff. Inputs: rederivation/outputs/relcount.jsonl.gz (own
counts), rederivation/outputs/census-fields-R1{2,3}-jobs.jsonl.gz (whitelisted
status and size fields), design.json (curve lists, sizes, final n).
Conventions (sealed): CC-5..CC-8 and CC-10 as written, with
  CONV-6 CC-6: (a) unmatched_size: fb_size(A) != the common fb_size of A's three
         randoms on curve j (or the randoms disagree) -> curve j dropped from A's
         cell only, and C_A, C_R and V of that cell are computed over the cell's
         remaining curves (paired, CC-5). (b) any arm of the family (as run on
         that panel and m) with status != completed_valid or without a census
         row on curve j -> curve j dropped from every cell of the family for that
         (class, m, rung). A cell keeping < 80% of its design curves is flagged
         incomplete.
  CONV-7 band = the 30-bit and 32-bit curves pooled; s_j^2 per curve (ddof 1 over
         the three randoms); V = max(sum_j s_j^2, C_R); SD_null = sqrt(4V/3);
         z = (C_A - C_R) / SD_null; kappa_rel = C_A / C_R.
  CONV-10 PC-1 (Q5): raw = distinct monic relations including formal ones (CC-1),
         per class TT, TB and TT+TB; ratio = sum_j raw_known_log /
         ((1/3) sum_r sum_j raw_random_sub_r) over curves 10..19, per bits and
         pooled; nonformal per instance.
  CONV-11 PC-R (iii) (Q3): planted relations from FactorBase.planted (construction
         only); a TT plant is checked against its instance's TT nonformal set, the
         TB plant against the TB (CONV-1) set; union also reported.
  CONV-13 Q6: D = sum_j s_j^2 / sum_j nbar_j over the band curves kept in the
         family's cells, per (family, class, m) and pooled over both families.
Usage: cells.py OUT_JSON
"""
import collections
import gzip
import json
import math
import os
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
EXP = WT + "/experiments/EXP-PFDR-011cd0"
RUNS = {"R12": EXP + "/runs/RUN-PFDR-011cd0-table", "R13": EXP + "/runs/RUN-PFDR-011cd0-search"}
DESIGN = EXP + "/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"
HERE = os.path.dirname(os.path.abspath(__file__))
SUB_R = ["random_sub_r0", "random_sub_r1", "random_sub_r2"]
DICK_R = ["random_dick_r0", "random_dick_r1", "random_dick_r2"]
SUB = ["subgroup", "small_x"] + SUB_R + ["known_null_sub", "planted_sub"]
DICK = ["dickson"] + DICK_R + ["known_null_dick"]
FAM1 = [("TT", 3), ("TT", 4), ("TT", 5), ("SS", 3), ("SS", 4), ("SS", 5), ("TB", 3)]
BAND = [30, 32]
RUNGS = [20, 22, 24, 26, 28, 30, 32]


def var3(x):
    m = sum(x) / 3.0
    return sum((v - m) ** 2 for v in x) / 2.0


def main():
    design = json.load(open(DESIGN))
    final_n = design["final_n"]
    counts = {}
    planted = {}
    with gzip.open(os.path.join(HERE, "outputs", "relcount.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            k = tuple(r["key"])
            counts[k] = r
            if "planted" in r:
                planted[k] = r["planted"]
    census = {}
    dup = 0
    for run in ("R12", "R13"):
        js = json.load(open(RUNS[run] + "/attempt-1/jobs-spec.json"))
        jm = {j["name"]: j["m"] for j in js["jobs"]}
        with gzip.open(os.path.join(HERE, "outputs", f"census-fields-{run}-jobs.jsonl.gz"), "rt") as fh:
            for line in fh:
                r = json.loads(line)
                key = (r["bits"], r["curve"], jm[r["_file"].split("/")[-2]], r["arm"], r["mode"])
                dup += key in census
                census[key] = r

    def curves(panel, m, bits):
        n = final_n[panel][str(m)][str(bits)]
        return list(range(10, 10 + n))

    def n_of(key, cls, variant=None):
        r = counts[key]
        if variant == "TB_B":
            return r["TB_B"]["n_nonformal"]
        return r[cls]["n_nonformal"]

    def fam_arms(A, panel, m):
        fam = SUB if A in SUB else DICK
        arms = [x for x in fam if not (x == "planted_sub" and not (panel == "table" and m == 3))]
        return arms, (SUB_R if A in SUB else DICK_R)

    drops_log = []

    def cell(A, cls, m, bits_list, variant=None, log_drops=True):
        panel = "search" if cls == "SS" else "table"
        mode = panel
        arms, R = fam_arms(A, panel, m)
        CA, sumr, s2, used, design_curves = 0, 0.0, 0.0, [], 0
        per_curve = []
        drops = []
        for bits in bits_list:
            for c in curves(panel, m, bits):
                design_curves += 1
                bad = [a for a in arms if census.get((bits, c, m, a, mode), {}).get("status") != "completed_valid"]
                if bad:
                    drops.append({"bits": bits, "curve": c, "reason": "failed_infrastructure_or_missing", "arms": bad})
                    continue
                szR = {census[(bits, c, m, r, mode)]["fb_size"] for r in R}
                if len(szR) != 1 or census[(bits, c, m, A, mode)]["fb_size"] not in szR:
                    drops.append({"bits": bits, "curve": c, "reason": "unmatched_size",
                                  "A": census[(bits, c, m, A, mode)]["fb_size"], "randoms": sorted(szR)})
                    continue
                nA = n_of((bits, c, m, A, mode), cls, variant)
                nr = [n_of((bits, c, m, r, mode), cls, variant) for r in R]
                CA += nA
                sumr += sum(nr)
                s2 += var3(nr)
                used.append((bits, c))
                per_curve.append([bits, c, nA] + nr)
        CR = sumr / 3.0
        V = max(s2, CR)
        SD = math.sqrt(V * 4.0 / 3.0)
        z = (CA - CR) / SD if SD > 0 else None
        if log_drops and drops:
            drops_log.append({"cell": f"{A}|{cls}{m}|{'-'.join(map(str, bits_list))}", "variant": variant, "drops": drops})
        return {"A": A, "class": cls, "m": m, "bits": bits_list, "variant": variant,
                "C_A": CA, "C_R": CR, "kappa_rel": (CA / CR) if CR else None, "sum_s2": s2,
                "V": V, "SD_null": SD, "z": z, "curves_used": len(used), "design_curves": design_curves,
                "incomplete": len(used) < 0.8 * design_curves, "drops": drops,
                "per_curve_counts_A_r0_r1_r2": per_curve}

    out = {"Q2_FAM1_band": {}, "Q2_known_null_band": {}, "Q2_TB3_variant_B": {},
           "Q2_per_rung_secondary": {}, "Q3_planted": {}, "Q4_CARRY1": None, "Q5_PC1": {},
           "Q6_random_dispersion_band": {}, "Q1_multiplicity_histograms_band": {},
           "Q1_counts_file": "rederivation/outputs/q1-counts-band.jsonl.gz",
           "census_duplicate_keys": dup}
    for A in ("subgroup", "small_x", "dickson"):
        for cls, m in FAM1:
            out["Q2_FAM1_band"][f"{A}|{cls}{m}|band"] = cell(A, cls, m, BAND)
    for A in ("known_null_sub", "known_null_dick"):
        for cls, m in FAM1:
            out["Q2_known_null_band"][f"{A}|{cls}{m}|band"] = cell(A, cls, m, BAND)
    for A in ("subgroup", "small_x", "dickson", "known_null_sub", "known_null_dick"):
        out["Q2_TB3_variant_B"][f"{A}|TB3|band"] = cell(A, "TB", 3, BAND, variant="TB_B")
    for A in ("subgroup", "small_x", "dickson", "known_null_sub", "known_null_dick"):
        for cls, m in FAM1:
            for b in RUNGS:
                c_ = cell(A, cls, m, [b], log_drops=False)
                c_.pop("per_curve_counts_A_r0_r1_r2")
                out["Q2_per_rung_secondary"][f"{A}|{cls}{m}|{b}"] = c_
    # Q3 planted
    for cls in ("TT", "TB"):
        c_ = cell("planted_sub", cls, 3, BAND)
        tot_rel, rec_own, rec_union, fails = 0, 0, 0, []
        declared = 0
        for bits in BAND:
            for c in curves("table", 3, bits):
                pk = (bits, c, 3, "planted_sub", "table")
                pl = planted.get(pk)
                if pl is None:
                    fails.append({"key": list(pk), "reason": "no planted record"})
                    continue
                cens = census[pk]["fb_params"]
                if (cens.get("n_tt"), cens.get("n_tb"), cens.get("skipped_tuples")) != (pl["n_tt"], pl["n_tb"], pl["skipped_tuples"]):
                    fails.append({"key": list(pk), "reason": "planted declaration differs from census fb_params"})
                declared += pl["n_tt"] if cls == "TT" else pl["n_tb"]
                for rel in pl["relations"]:
                    if rel["class"] != cls:
                        continue
                    tot_rel += 1
                    rec_own += rel["in_own_class_set"]
                    rec_union += rel["in_union_TT_TB"]
                    if not rel["in_own_class_set"]:
                        fails.append({"key": list(pk), "relation": rel})
        c_["declared_planted_total"] = declared
        c_["excess_C_planted_minus_C_R"] = c_["C_A"] - c_["C_R"]
        c_["planted_relations"] = tot_rel
        c_["recovered_in_own_class_set"] = rec_own
        c_["recovered_in_union"] = rec_union
        c_["recovery_failures"] = fails
        out["Q3_planted"][f"planted_sub|{cls}3|band"] = c_
    # all planted instances at every rung (PC-R (iii) is stated for its instances)
    allp = {"instances": 0, "relations": 0, "recovered_own": 0, "not_recovered": []}
    for pk, pl in sorted(planted.items()):
        allp["instances"] += 1
        for rel in pl["relations"]:
            allp["relations"] += 1
            allp["recovered_own"] += rel["in_own_class_set"]
            if not rel["in_own_class_set"]:
                allp["not_recovered"].append({"key": list(pk), "relation": rel})
    out["Q3_planted_all_rungs"] = allp
    # Q4
    out["Q4_CARRY1"] = cell("subgroup", "TT", 3, [28])
    # Q5 PC-1
    for bl in ([20], [24], [20, 24]):
        agg = {cls: {"KL_raw": 0, "R_raw_mean": 0.0} for cls in ("TT", "TB", "TT+TB")}
        nf = []
        for b in bl:
            for c in range(10, 20):
                kk = (b, c, 3, "known_log", "table")
                r = counts[kk]
                nf.append({"key": list(kk), "status": census[kk]["status"], "fb_size": census[kk]["fb_size"],
                           "TT_nonformal": r["TT"]["n_nonformal"], "TB_nonformal": r["TB"]["n_nonformal"],
                           "TT_raw": r["TT"]["n_raw"], "TB_raw": r["TB"]["n_raw"]})
                for cls in ("TT", "TB"):
                    agg[cls]["KL_raw"] += r[cls]["n_raw"]
                    agg[cls]["R_raw_mean"] += sum(counts[(b, c, 3, x, "table")][cls]["n_raw"] for x in SUB_R) / 3.0
                agg["TT+TB"]["KL_raw"] += r["TT"]["n_raw"] + r["TB"]["n_raw"]
                agg["TT+TB"]["R_raw_mean"] += sum(counts[(b, c, 3, x, "table")]["TT"]["n_raw"] +
                                                  counts[(b, c, 3, x, "table")]["TB"]["n_raw"] for x in SUB_R) / 3.0
        for cls in agg:
            agg[cls]["ratio"] = agg[cls]["KL_raw"] / agg[cls]["R_raw_mean"] if agg[cls]["R_raw_mean"] else None
        out["Q5_PC1"]["-".join(map(str, bl))] = {"aggregate": agg, "per_instance": nf,
                                                 "nonformal_all_zero": all(x["TT_nonformal"] == 0 and x["TB_nonformal"] == 0 for x in nf)}
    # Q6 random dispersion (band) per (family, class, m) and pooled
    for cls, m in [("TT", 3), ("TT", 4), ("TT", 5), ("TB", 3), ("TB", 4), ("TB", 5), ("SS", 3), ("SS", 4), ("SS", 5)]:
        res = {}
        num_all = den_all = 0.0
        for fam, A in (("SUB", "subgroup"), ("DICK", "dickson")):
            c_ = cell(A, cls, m, BAND, log_drops=False)
            num = sum(var3(pc[3:]) for pc in c_["per_curve_counts_A_r0_r1_r2"])
            den = sum(sum(pc[3:]) / 3.0 for pc in c_["per_curve_counts_A_r0_r1_r2"])
            res[fam] = {"sum_s2": num, "sum_nbar": den, "D": num / den if den else None,
                        "curves": len(c_["per_curve_counts_A_r0_r1_r2"])}
            num_all += num
            den_all += den
        res["pooled"] = {"sum_s2": num_all, "sum_nbar": den_all, "D": num_all / den_all if den_all else None}
        out["Q6_random_dispersion_band"][f"{cls}{m}"] = res
    # Q1 multiplicity histograms (band, completed_valid instances) and the counts file
    hist = collections.defaultdict(collections.Counter)
    with gzip.open(os.path.join(HERE, "outputs", "q1-counts-band.jsonl.gz"), "wt") as fh:
        for k, r in sorted(counts.items(), key=lambda kv: (kv[0][4], kv[0][2], kv[0][3], kv[0][0], kv[0][1])):
            bits, c, m, arm, mode = k
            if bits not in BAND or arm == "known_log":
                continue
            st = census.get(k, {}).get("status")
            classes = ("SS",) if mode == "search" else ("TT", "TB")
            rec = {"bits": bits, "curve": c, "m": m, "arm": arm, "mode": mode, "status": st}
            for cls in classes:
                rec[cls] = r[cls]["n_nonformal"]
                rec[cls + "_R_star"] = r[cls]["R_star"]
                rec[cls + "_signonly"] = r[cls]["n_signonly_nonformal"]
                if st == "completed_valid":
                    for M, n in r[cls]["hist_nonformal"].items():
                        hist[f"{arm}|{cls}{m}"][int(M)] += n
            if mode == "table":
                rec["TB_B"] = r["TB_B"]["n_nonformal"]
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    out["Q1_multiplicity_histograms_band"] = {k: dict(sorted(v.items())) for k, v in sorted(hist.items())}
    out["CC6_drops_listed"] = drops_log
    # universe check
    uni = 0
    miss = []
    for run in ("R12", "R13"):
        js = json.load(open(RUNS[run] + "/attempt-1/jobs-spec.json"))
        for j in js["jobs"]:
            for k in j["expected_keys"]:
                uni += 1
                if tuple(k) not in counts or tuple(k) not in census:
                    miss.append(k)
    out["universe"] = {"expected_keys": uni, "missing_counts_or_census": miss[:50], "missing_n": len(miss),
                       "status_counts": dict(collections.Counter(v.get("status") for v in census.values()))}
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
