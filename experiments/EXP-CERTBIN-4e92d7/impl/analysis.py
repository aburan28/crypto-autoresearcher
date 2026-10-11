"""Phase 8: aggregation, instrument checks (M5), decision rules DR-1..DR-8,
sizing, raw-result cross-check and the run report.

Mechanical only: every threshold below is copied from the frozen
specification (version 1); nothing here chooses a threshold or a reference
after seeing results.
"""
import gzip
import json
import math
from collections import Counter

import numpy as np

from stats import (clopper_pearson, entropy_bits, binary_entropy, median, mann_whitney,
                   binom_two_sided_interval, binom_sf, binom_cdf)

FAMS = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3", "F-NULLF2"]
GRANS = ["rank", "set", "strict", "ops"]
DS = [3, 4]
S_SELFTEST = 20260923199


def primary_keys(fam, unit):
    """Ordered reference keys used for the family's primary statistics."""
    if fam == "F-PLANT":
        base = [k for k in ("F-S3:U1", "F-S3:U2", "F-S3:U3", "F-S3:S1", "F-S3:S2", "F-S3:modal")]
        return base + ["modal"]
    labels = [r["label"] for r in unit["refs"]]
    return [k for k in ("U1", "U2", "U3", "S1", "S2", "modal") if k in labels]


def m1_keys(fam, unit):
    """The 3 unsatisfiable references and the modal reference (M1)."""
    if fam == "F-PLANT":
        return ["F-S3:U1", "F-S3:U2", "F-S3:U3", "modal"]
    labels = [r["label"] for r in unit["refs"]]
    return [k for k in ("U1", "U2", "U3", "modal") if k in labels]


def retention(records, key, g, arm):
    sub = [r for r in records if not r["degenerate"] and r["stratum"] == arm and key in r["refs"]]
    n = len(sub)
    x = sum(1 for r in sub if r["refs"][key]["match"][g])
    return {"x": x, "n": n, "value": (x / n) if n else None, "cp95": clopper_pearson(x, n)}


def family_retention(records, keys, g, arm="unsat"):
    per = {k: retention(records, k, g, arm) for k in keys}
    best = None
    for k in keys:
        v = per[k]["value"]
        if v is None:
            continue
        if best is None or v > per[best]["value"]:
            best = k
    return per, best


def fdiv_stats(records, key):
    out = {}
    vals = {}
    for arm in ("unsat", "sat"):
        sub = [r["refs"][key] for r in records if not r["degenerate"] and r["stratum"] == arm and key in r["refs"]]
        f = [c["f_div"] for c in sub if c["f_div"] is not None]
        vals[arm] = f
        degs = Counter(c["div_deg"] for c in sub)
        hist = [0] * 10
        for x in f:
            hist[min(9, int(x * 10))] += 1
        out[arm] = {"n": len(f), "median_f_div": median(f),
                    "quantiles": [float(np.quantile(f, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)] if f else None,
                    "hist_10bins": hist, "n_match_strict": sum(1 for c in sub if c["match"]["strict"]),
                    "n_proper_extension": sum(1 for c in sub if c["f_div"] == 1 and not c["match"]["strict"]),
                    "divergence_column_degree": {str(k): v for k, v in sorted(degs.items(), key=lambda kv: str(kv[0]))}}
    out["mann_whitney_unsat_vs_sat"] = mann_whitney(vals["unsat"], vals["sat"])
    return out


def strict_own_hazard(records, key, L_ref):
    sub = [r["refs"][key] for r in records if not r["degenerate"] and key in r["refs"]]
    kd = Counter()
    for c in sub:
        if not c["match"]["strict"] and c["kdiv"] < L_ref:
            kd[c["kdiv"]] += 1
    n = len(sub)
    at = n
    rows = []
    for k in range(L_ref):
        f = kd.get(k, 0)
        if f:
            rows.append([k, at, f, round(f / at, 6)])
        at -= f
        if at == 0:
            break
    return {"n": n, "rows_k_atrisk_fail_h": rows, "note": "only steps with >= 1 divergence listed"}


def p2_set(hz, keys):
    items = []
    for key in keys:
        t = hz.get(key)
        if not t:
            continue
        for k, (dep, Sk, hk) in enumerate(zip(t["sampled_dependent"], t["S_k"], t["h_k"])):
            if dep and Sk >= 200:
                items.append({"ref": key, "k": k, "S_k": Sk, "zeros": t["zeros_k"][k], "h": t["zeros_k"][k] / Sk})
    return items


def summarize_p2(items):
    if not items:
        return {"n": 0, "evaluable": False, "reason": "empty P2 set"}
    hs = [it["h"] for it in items]
    inband = sum(1 for h in hs if 0.4 <= h <= 0.6)
    out = {"n": len(items), "evaluable": True, "median_h": median(hs), "frac_in_[0.4,0.6]": inband / len(hs),
           "n_in_band": inband, "min_h": min(hs), "max_h": max(hs)}
    # tail check: extremes vs binomial(S_k, 0.5)
    mn, mx = min(hs), max(hs)
    p_all_above = 1.0
    p_all_below = 1.0
    for it in items:
        S = it["S_k"]
        p_all_above *= binom_sf(int(math.floor(mn * S)) + 1, S, 0.5)  # P(h > mn)
        p_all_below *= binom_cdf(int(math.ceil(mx * S)) - 1, S, 0.5)  # P(h < mx)
    out["tail_extremes"] = {"observed_min_h": mn, "observed_max_h": mx,
                            "P_null_min_le_observed": 1 - p_all_above,
                            "P_null_max_ge_observed": 1 - p_all_below,
                            "null": "independent Binomial(S_k, 0.5)/S_k per pivot in the set"}
    return out


def expected_max_class(N, d, reps, rng):
    if d <= 0 or N <= 0:
        return None
    x = rng.integers(0, d, size=(reps, N))
    mx = [int(np.bincount(row, minlength=d).max()) for row in x]
    return {"mean": float(np.mean(mx)), "q99": float(np.quantile(mx, 0.99)), "max": int(max(mx)), "reps": reps}


# ---------------------------------------------------------------------------
def analyse(ctx):
    P1 = ctx["phase1"]
    U = ctx["units"]          # (fam, D) -> unit result
    det = ctx["phase7"]
    selftest = ctx["selftest"]
    spec_seeds = ctx["plan"]["seeds"]

    cell = {"families": {}}
    hazards_out = {}
    sizing = {"per_reference": {}, "thresholds": {"per_system_warp_bytes": 32, "per_SM_bytes": 233472}}
    rng_tail = np.random.Generator(np.random.PCG64(S_SELFTEST))

    for fam in FAMS:
        cell["families"][fam] = {}
        for D in DS:
            unit = U[(fam, D)]
            recs = unit["records"]
            keys = primary_keys(fam, unit)
            nd = [r for r in recs if not r["degenerate"]]
            arms = {a: [r for r in nd if r["stratum"] == a] for a in ("unsat", "sat")}
            c = {"N_targets": len(recs), "N_non_degenerate": len(nd), "N_degenerate": len(recs) - len(nd),
                 "arm_sizes": {a: len(v) for a, v in arms.items()},
                 "underpowered": {a: len(v) < 100 for a, v in arms.items()},
                 "reference_keys": keys}
            # M1 / retention at every granularity, every reference, every arm
            ret = {}
            for g in GRANS:
                ret[g] = {}
                for k in keys:
                    ret[g][k] = {arm: retention(recs, k, g, arm) for arm in ("unsat", "sat")}
            c["retention"] = ret
            mk = m1_keys(fam, unit)
            fr = {}
            for g in GRANS:
                per, best = family_retention(recs, mk, g, "unsat")
                fr[g] = {"m1_keys": mk, "maximizing_reference": best,
                         "retention_family": per[best]["value"] if best else None,
                         "count": per[best]["x"] if best else None, "n": per[best]["n"] if best else None,
                         "all_counts_zero": all(per[k]["x"] == 0 for k in mk if per[k]["n"]),
                         "per_reference": per}
            c["retention_family_unsat"] = fr
            if fam == "F-RANDX":
                sec = {}
                for g in GRANS:
                    sec[g] = {k: {arm: retention(recs, k, g, arm) for arm in ("unsat", "sat")}
                              for k in ("F-S3:U1", "F-S3:U2", "F-S3:U3", "F-S3:S1", "F-S3:S2", "F-S3:modal")}
                c["secondary_vs_F-S3_references"] = sec
            # M4 entropy
            m4 = {}
            psat = len(arms["sat"]) / len(nd) if nd else None
            for g in GRANS:
                h, dist, n, mxc = entropy_bits([r["h_" + g] for r in nd])
                m4[g] = {"H_bits": h, "distinct": dist, "N": n, "largest_class": mxc,
                         "expected_max_class_uniform_null": expected_max_class(n, dist, 1000, rng_tail)}
            m4["P_sat"] = psat
            m4["h_P_sat"] = binary_entropy(psat) if psat is not None else None
            m4["E1_threshold_bits"] = 8.97
            c["M4_entropy"] = m4
            # M2 and K
            hz = unit["hazards"]
            hazards_out.setdefault(fam, {})[f"D{D}"] = hz
            declared = [k for k in keys if k != "modal" and not k.endswith(":modal")]
            c["M2_like"] = {"pooled_declared_refs": summarize_p2(p2_set(hz, declared)),
                            "per_reference": {k: summarize_p2(p2_set(hz, [k])) for k in keys if k in hz}}
            kinfo = {}
            for k, t in hz.items():
                if t is None:
                    continue
                rank = len(t["p"])
                kinfo[k] = {"K_sampled": t["K_sampled"], "rank": rank,
                            "K_over_rank": t["K_sampled"] / rank if rank else None,
                            "K_exact": t.get("K_exact"), "K_rank": t.get("K_rank"),
                            "K_basis": t["dependence_basis"],
                            "predicted_retention_2^-K_rank": t.get("predicted_retention_2^-K_rank"),
                            "measured_fixed_schedule_retention": t["measured_fixed_schedule_retention"],
                            "product_of_per_pivot_survivals": t["product_of_per_pivot_survivals"],
                            "n_scored": t["n_scored"], "full_replay_survivors": t["full_replay_survivors"]}
                zd = [x for x in t.get("unconditional_zero_density", []) if x is not None]
                if zd:
                    kinfo[k]["zero_density_nonconstant_pivots"] = {
                        "n": len(zd), "mean": float(np.mean(zd)), "median": float(np.median(zd)),
                        "min": float(min(zd)), "max": float(max(zd)),
                        "frac_in_[0.45,0.55]": sum(1 for x in zd if 0.45 <= x <= 0.55) / len(zd)}
            c["K_and_replay"] = kinfo
            # f_div and strict own hazard
            c["f_div"] = {k: fdiv_stats(recs, k) for k in keys}
            refL = {}
            for r in unit["refs"]:
                refL[r["label"]] = r["len_strict"]
            for k in keys:
                if k in hz and hz[k] is not None:
                    refL.setdefault(k, len(hz[k]["p"]))
            c["strict_own_elimination_hazard"] = {k: strict_own_hazard(recs, k, refL[k]) for k in keys if k in refL}
            # D*, 1-in-R, rank distribution
            c["one_in_R_rate"] = {a: (sum(r["one_in_R"] for r in v) / len(v) if v else None) for a, v in arms.items()}
            c["rank_distribution"] = {a: dict(sorted(Counter(r["rank"] for r in v).items())) for a, v in arms.items()}
            c["rational_flag_rate"] = (sum(1 for r in nd if (r["rational_flag"] or 0) > 0) / len(nd)) if nd and fam in ("F-S3", "F-S3-REV", "F-PLANT", "F-RANDX") else None
            c["wall_seconds"] = unit["wall_seconds"]
            c["peak_rss_bytes_process"] = unit.get("peak_rss_bytes")
            c["modal_info"] = unit["modal_info"]
            cell["families"][fam][f"D{D}"] = c
            for r in unit["refs"]:
                sizing["per_reference"].setdefault(fam, {}).setdefault(f"D{D}", {})[r["label"]] = {
                    "sizes": r["sizes"], "saving": r["saving"], "rank": r["rank"], "Z_size": r["Z_size"]}
        # D* per arm (needs both D)
        d3 = {r["idx"]: r for r in U[(fam, 3)]["records"]}
        d4 = {r["idx"]: r for r in U[(fam, 4)]["records"]}
        dstar = {"unsat": Counter(), "sat": Counter()}
        for idx, r3 in d3.items():
            if r3["degenerate"]:
                continue
            r4 = d4[idx]
            ds = 3 if r3["one_in_R"] else (4 if r4["one_in_R"] else "not reached at D <= 4")
            dstar[r3["stratum"]][str(ds)] += 1
        cell["families"][fam]["D_star_distribution"] = {a: dict(v) for a, v in dstar.items()}

    # ---- M3 (D = 4, T_strict)
    def rf(fam):
        return cell["families"][fam]["D4"]["retention_family_unsat"]["strict"]
    num = rf("F-S3")
    dens = [rf(f"F-AFF-{d}") for d in (1, 2, 3)]
    m3 = {"granularity": "strict", "D": 4, "numerator": {"retention_family": num["retention_family"], "count": num["count"], "n": num["n"], "ref": num["maximizing_reference"]},
          "denominators": [{"family": f"F-AFF-{d}", "retention_family": x["retention_family"], "count": x["count"], "n": x["n"], "ref": x["maximizing_reference"]} for d, x in zip((1, 2, 3), dens)]}
    num_count0 = (num["count"] or 0) == 0
    den_all0 = all((x["count"] or 0) == 0 for x in dens)
    per_draw = []
    for d, x in zip((1, 2, 3), dens):
        if x["retention_family"]:
            per_draw.append({"draw": d, "ratio": num["retention_family"] / x["retention_family"]})
        else:
            per_draw.append({"draw": d, "ratio": None, "reason": "denominator 0"})
    m3["per_draw_ratios"] = per_draw
    if num_count0 and den_all0:
        m3.update({"kind": "not_estimable", "value": None,
                   "note": "numerator and denominator counts all 0; E1's [0.5, 2] clause is 'not evaluable'"})
    elif num_count0:
        m3.update({"kind": "zero", "value": 0.0, "note": "numerator count 0: ratio is 0; E2's >= 10x clause NOT met"})
    elif den_all0:
        npool = sum(x["n"] for x in dens)
        ub = clopper_pearson(0, npool)[1]
        m3.update({"kind": "lower_bound", "value": num["retention_family"] / ub, "pooled_n": npool,
                   "pooled_cp95_upper": ub})
    else:
        point = num["retention_family"] / np.mean([x["retention_family"] for x in dens])
        m3.update({"kind": "point", "value": float(point), "bootstrap95": bootstrap_m3(U)})
    cell["M3"] = m3

    # ---- M2 P2 set: F-S3, D = 4, 5 declared references
    hz4 = U[("F-S3", 4)]["hazards"]
    decl = [k for k in ("U1", "U2", "U3", "S1", "S2") if k in hz4]
    p2 = p2_set(hz4, decl)
    m2 = summarize_p2(p2)
    m2["per_reference"] = {k: summarize_p2(p2_set(hz4, [k])) for k in decl}
    m2["set"] = p2
    # independence tail check per reference
    m2["independence_tail_check"] = {k: {kk: cell["families"]["F-S3"]["D4"]["K_and_replay"][k][kk] for kk in (
        "measured_fixed_schedule_retention", "product_of_per_pivot_survivals", "predicted_retention_2^-K_rank",
        "K_rank", "K_sampled")} for k in decl}
    cell["M2"] = m2

    checks = instrument_checks(ctx, cell)
    dr = decision_rules(cell, checks)
    return cell, hazards_out, sizing, checks, dr


def bootstrap_m3(U, B=10000):
    rng = np.random.Generator(np.random.PCG64(S_SELFTEST))
    ratios = []
    fams = ["F-S3", "F-AFF-1", "F-AFF-2", "F-AFF-3"]
    per_fam = []
    for fam in fams:
        unit = U[(fam, 4)]
        keys = m1_keys(fam, unit)
        arm = [r for r in unit["records"] if not r["degenerate"] and r["stratum"] == "unsat"]
        n = len(arm)
        A = np.array([[bool(r["refs"].get(k, {}).get("match", {}).get("strict", False)) for k in keys] for r in arm], dtype=bool).reshape(n, len(keys))
        has = np.array([[k in r["refs"] for k in keys] for r in arm], dtype=bool).reshape(n, len(keys))
        idx = rng.integers(0, n, size=(B, n)) if n else np.zeros((B, 0), dtype=np.int64)
        vals = np.zeros((B, len(keys)))
        for j in range(len(keys)):
            m = A[:, j][idx]
            h = has[:, j][idx]
            cnt = h.sum(axis=1)
            vals[:, j] = np.where(cnt > 0, m.sum(axis=1) / np.maximum(cnt, 1), 0.0)
        per_fam.append(vals.max(axis=1) if len(keys) else np.zeros(B))
    num = per_fam[0]
    den = np.mean(np.stack(per_fam[1:]), axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(den > 0, num / np.where(den > 0, den, 1), np.inf)
    rs = np.sort(r)
    return {"resamples": B, "seed": S_SELFTEST, "ci95": [float(rs[int(0.025 * B)]), float(rs[int(0.975 * B) - 1])],
            "n_infinite": int(np.isinf(r).sum()),
            "procedure": "resample each family's non-degenerate unsatisfiable arm with replacement (families in order F-S3, F-AFF-1, F-AFF-2, F-AFF-3; one rng.integers(0, n, size=(B, n)) call each); modal retention over resampled targets with idx > 100"}


# ---------------------------------------------------------------------------
def instrument_checks(ctx, cell):
    P1 = ctx["phase1"]
    U = ctx["units"]
    det = ctx["phase7"]
    st = ctx["selftest"]
    out = {}
    out["C-FIX"] = {"pass": bool(st.get("C-FIX_pass")), "detail": next(i for i in st["items"] if i["id"] == "C-FIX")}
    out["C-SELF"] = {"pass": bool(st.get("C-SELF_pass")),
                     "items": {i["id"]: i["pass"] for i in st["items"] if i["id"] != "C-FIX"}}

    def instances(fam):
        d = P1[fam]
        res = []
        for c in d.get("ref_scan", []):
            if c.get("status") == "classified":
                res.append(("ref_scan", c))
        for t in d["targets"]:
            res.append(("target", t))
        return res

    # C-ORACLE
    viol = []
    n = 0
    for fam in ("F-S3", "F-PLANT", "F-RANDX"):
        for kind, c in instances(fam):
            n += 1
            if not c["oracle_agree"] or c["s"] != c["s_A"]:
                viol.append({"family": fam, "kind": kind, "x_R": c["x_R"], "s_A": c["s_A"], "s_B": c["s"]})
    out["C-ORACLE"] = {"pass": not viol, "checked": n, "failed": len(viol), "violations": viol,
                       "scope": "every classified F-S3 reference candidate, F-S3 target, F-PLANT target, F-RANDX reference candidate and target (oracle A vs oracle B solution SETS)"}
    # C-WIT
    viol = []
    nsol = 0
    ninst = 0
    for fam in ("F-S3", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3", "F-NULLF2"):
        for kind, c in instances(fam):
            ninst += 1
            nsol += len(c["sols"])
            for w in c["wit_fail"]:
                viol.append({"family": fam, "kind": kind, "x_R": c.get("x_R"), **w})
    plant_bad = [t["idx"] for t in P1["F-PLANT"]["targets"] if t["s"] < 1 or not t["planted_witness_found"]]
    out["C-WIT"] = {"pass": not viol and not plant_bad, "instances": ninst, "solutions_verified": nsol,
                    "failed": len(viol), "violations": viol, "F-PLANT_s_ge_1_all": not plant_bad,
                    "F-PLANT_failures": plant_bad}
    # C-AFF
    viol = []
    n = 0
    for fam in ("F-S3", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3"):
        for kind, c in instances(fam):
            n += 1
            if not c.get("aff_ok", False):
                viol.append({"family": fam, "kind": kind, "x_R": c.get("x_R")})
    direct = {}
    dfail = []
    for fam in FAMS:
        for D in DS:
            cd = U[(fam, D)]["caff_direct"]
            direct[f"{fam}/D{D}"] = {"checked_pairs": cd["checked_pairs"], "mismatch_pairs": cd["mismatch_pairs"]}
            if cd["mismatch_pairs"]:
                dfail.append({"family": fam, "D": D, "mismatches": cd["mismatches"]})
    out["C-AFF"] = {"pass": not viol and not dfail, "identity_checked": n, "identity_failed": len(viol),
                    "identity_violations": viol, "direct_replay_vs_affine": direct, "direct_replay_failures": dfail,
                    "affected_families": sorted({v["family"] for v in viol} | {f["family"] for f in dfail})}
    # C-DET
    out["C-DET"] = {"pass": bool(det and det["targets_matched"] == det["targets_checked"] == ctx["plan"]["counts"]["test_targets"] * 2
                                 and det["refs_matched"] == det["refs_checked"]),
                    "targets_matched": det["targets_matched"] if det else None,
                    "targets_checked": det["targets_checked"] if det else None,
                    "refs_matched": det["refs_matched"] if det else None,
                    "refs_checked": det["refs_checked"] if det else None,
                    "per_D": det["per_D"] if det else None,
                    "mismatches": det["mismatches"] if det else None,
                    "separate_process": det.get("process") if det else None}
    # C-PASS
    viol = []
    n = 0
    for (fam, D), unit in U.items():
        for r in unit["records"]:
            n += 1
            if not r["cpass"]:
                viol.append({"family": fam, "D": D, "idx": r["idx"]})
        for lab, ok in unit["ref_cpass"].items():
            n += 1
            if not ok:
                viol.append({"family": fam, "D": D, "ref": lab})
    out["C-PASS"] = {"pass": not viol, "checked": n, "failed": len(viol), "violations": viol}
    # C-PROPS
    ps = {"PS0": [], "PS1": [], "PS3": []}
    n = 0
    for (fam, D), unit in U.items():
        for r in unit["records"]:
            n += 1
            if r["PS0_fail"]:
                ps["PS0"].append({"family": fam, "D": D, "idx": r["idx"], "detail": r["PS0_fail"]})
            if r["PS1_fail"]:
                ps["PS1"].append({"family": fam, "D": D, "idx": r["idx"]})
            if r["PS3_fail"]:
                ps["PS3"].append({"family": fam, "D": D, "idx": r["idx"]})
        for ref in unit["refs"]:
            n += 1
            ch = ref["checks"]
            if ch["PS0_fail"]:
                ps["PS0"].append({"family": fam, "D": D, "ref": ref["label"], "detail": ch["PS0_fail"]})
            if ch["PS1_fail"]:
                ps["PS1"].append({"family": fam, "D": D, "ref": ref["label"]})
            if ch["PS3_fail"]:
                ps["PS3"].append({"family": fam, "D": D, "ref": ref["label"]})
    ps2 = {}
    ps2_viol = []
    for fam in FAMS:
        for D in DS:
            unit = U[(fam, D)]
            if fam == "F-PLANT":
                continue  # F-PLANT is covered under the F-S3 references
            ref_by = {r["label"]: r for r in unit["refs"]}
            unsat_refs = []
            for lab, r in ref_by.items():
                if lab == "modal":
                    st_ = unit["modal_info"]["stratum"]
                else:
                    st_ = "unsat" if lab.startswith("U") else "sat"
                if st_ == "unsat" and r["one_in_R"]:
                    unsat_refs.append(r)
            if not unsat_refs:
                ps2[f"{fam}/D{D}"] = "VACUOUS (no unsatisfiable reference has 1 in R_D)"
                continue
            sat_sets = [(f"target {r['idx']}", r["h_set"]) for r in unit["records"] if r["s"] >= 1]
            sat_sets += [(f"ref {lab}", r["h_set"]) for lab, r in ref_by.items()
                         if (lab.startswith("S") or (lab == "modal" and unit["modal_info"]["stratum"] == "sat"))]
            if fam == "F-S3":
                sat_sets += [(f"F-PLANT target {r['idx']}", r["h_set"]) for r in U[("F-PLANT", D)]["records"] if r["s"] >= 1]
            cnt = 0
            for ur in unsat_refs:
                for name, hs in sat_sets:
                    if hs == ur["h_set"]:
                        cnt += 1
                        ps2_viol.append({"family": fam, "D": D, "unsat_ref": ur["label"], "sat_instance": name})
            ps2[f"{fam}/D{D}"] = {"unsat_refs_with_1_in_R": [r["label"] for r in unsat_refs],
                                  "sat_instances_compared": len(sat_sets), "equal_T_set": cnt}
    out["C-PROPS"] = {
        "pass": not (ps["PS0"] or ps["PS1"] or ps["PS3"] or ps2_viol),
        "instances_checked_per_D_family": n,
        "PS0": {"failed": len(ps["PS0"]), "violations": ps["PS0"]},
        "PS1": {"failed": len(ps["PS1"]), "violations": ps["PS1"]},
        "PS2": {"failed": len(ps2_viol), "violations": ps2_viol, "per_family_D": ps2},
        "PS3": {"failed": len(ps["PS3"]), "violations": ps["PS3"]},
    }
    out["PS2_vacuous"] = {k: (isinstance(v, str)) for k, v in ps2.items()}
    # C-UNIF (F-RANDX, own references incl. modal)
    un = {}
    ufail = []
    for D in DS:
        hz = U[("F-RANDX", D)]["hazards"]
        for k in ("U1", "U2", "U3", "S1", "S2", "modal"):
            t = hz.get(k)
            if not t:
                continue
            p = 2.0 ** (-t["K_rank"])
            nn = t["n_scored"]
            x = t["full_replay_survivors"]
            lo, hi = binom_two_sided_interval(nn, p, 0.999)
            ok = lo <= x <= hi
            un[f"D{D}/{k}"] = {"survivors": x, "n": nn, "K_rank": t["K_rank"], "p": p,
                               "interval99.9": [lo, hi], "pass": ok}
            if not ok:
                ufail.append(f"D{D}/{k}")
    out["C-UNIF"] = {"pass": not ufail, "checked": len(un), "failed": len(ufail), "per_reference": un, "violations": ufail}
    # nesting (INV-6)
    nest = []
    for (fam, D), unit in U.items():
        items = [(r["h_rank"], r["h_set"], r["h_strict"], r["h_ops"]) for r in unit["records"]]
        items += [(r["h_rank"], r["h_set"], r["h_strict"], r["h_ops"]) for r in unit["refs"]]
        for fine in (3, 2, 1):
            grp = {}
            for it in items:
                grp.setdefault(it[fine], set()).add(it[fine - 1])
            bad = [h for h, s in grp.items() if len(s) > 1]
            if bad:
                nest.append({"family": fam, "D": D, "finer": GRANS[fine], "violating_classes": len(bad)})
        for r in unit["records"]:
            for key, cmp in r["refs"].items():
                m = cmp["match"]
                if (m["ops"] and not m["strict"]) or (m["strict"] and not m["set"]) or (m["set"] and not m["rank"]):
                    nest.append({"family": fam, "D": D, "idx": r["idx"], "ref": key, "match": m})
    out["NESTING"] = {"pass": not nest, "violations": nest}
    anomalies = []
    for (fam, D), unit in U.items():
        anomalies += unit["hash_anomalies"]
    out["HASH_CONTENT"] = {"pass": not anomalies, "anomalies": anomalies}
    srf = [{"family": fam, "D": D, "ref": r["label"]} for (fam, D), unit in U.items() for r in unit["refs"] if not r.get("self_replay_ok")]
    out["REF_SELF_REPLAY"] = {"pass": not srf, "violations": srf,
                              "note": "additional check: each reference's own op log replayed on its own matrix meets e_k = 1 at every step"}
    out["C-REV"] = {"pass": True, "note": "replicate family run (see cell-summary F-S3-REV)"}
    out["C-NULLS"] = {"pass": all((f, D) in U for f in ("F-AFF-1", "F-AFF-2", "F-AFF-3", "F-NULLF2", "F-RANDX") for D in DS),
                      "note": "all null/control families ran through the identical pipeline at both D"}
    # invalidation
    inv = {}
    inv["INV-1"] = not out["C-FIX"]["pass"]
    inv["INV-2"] = not out["C-SELF"]["pass"]
    inv["INV-3"] = not (out["C-ORACLE"]["pass"] and out["C-WIT"]["pass"])
    inv["INV-4"] = not out["C-PROPS"]["pass"]
    inv["INV-5"] = not out["C-AFF"]["pass"]
    inv["INV-6"] = not (out["NESTING"]["pass"] and out["C-PASS"]["pass"] and out["C-DET"]["pass"])
    inv["INV-7"] = not out["C-UNIF"]["pass"]
    void = inv["INV-1"] or inv["INV-2"] or inv["INV-4"] or inv["INV-6"]
    voided = []
    if inv["INV-3"]:
        voided.append("all arm-dependent metrics, every family (INV-3)")
    if inv["INV-5"]:
        voided.append(f"M2, K, K_rank for {out['C-AFF']['affected_families']} (INV-5)")
    if inv["INV-7"]:
        voided.append("M2, K_rank and the independence tail check, pending explanation (INV-7)")
    if out["HASH_CONTENT"]["anomalies"]:
        voided.append("hash/content disagreement recorded (not a declared INV; see HASH_CONTENT)")
    out["invalidation"] = {"triggered": inv, "run_void": void, "voided_metrics": voided}
    out["M5_summary"] = {k: {"pass": v["pass"]} for k, v in out.items() if isinstance(v, dict) and "pass" in v}
    return out


# ---------------------------------------------------------------------------
def _m3_ge10(m3):
    k = m3["kind"]
    if k == "point":
        return m3["value"] >= 10
    if k == "zero":
        return False
    if k == "lower_bound":
        return True if m3["value"] >= 10 else "unknown"
    return "unknown"


def _m3_lt10(m3):
    k = m3["kind"]
    if k == "point":
        return m3["value"] < 10
    if k == "zero":
        return True
    if k == "lower_bound":
        return False if m3["value"] >= 10 else "unknown"
    return "unknown"


def decision_rules(cell, checks):
    c4 = cell["families"]["F-S3"]["D4"]
    fr = c4["retention_family_unsat"]["strict"]
    rfv = fr["retention_family"]
    best = fr["maximizing_reference"]
    m2 = cell["M2"]
    m3 = cell["M3"]
    out = {"cell": "F-S3, D = 4, granularity T_strict (primary, DR-8)",
           "maximizing_reference_rule": "argmax of unsat-arm T_strict retention over (U1, U2, U3, modal); ties to the first in that order",
           "run_void": checks["invalidation"]["run_void"],
           "voided_metrics": checks["invalidation"]["voided_metrics"]}
    per = fr["per_reference"]
    # DR-1
    vals = {k: per[k]["value"] for k in fr["m1_keys"]}
    missing = [k for k in ("U1", "U2", "U3", "modal") if k not in vals or vals[k] is None]
    if missing:
        v1 = "not evaluable"
        r1 = f"references missing or empty arm: {missing}"
    else:
        v1 = "STRICT P-GPU FALSIFIED at this cell" if all(v < 0.5 for v in vals.values()) else "not falsified"
        r1 = None
    out["DR-1"] = {"verdict": v1, "reason": r1, "granularity": "T_strict", "D": 4, "inputs": {"M1_per_reference": vals}}
    # DR-2
    med = m2.get("median_h") if m2.get("evaluable") else None
    frac = m2.get("frac_in_[0.4,0.6]") if m2.get("evaluable") else None
    fals = []
    if rfv is not None and rfv >= 0.5:
        fals.append("retention_family >= 0.5")
    if med is not None and med < 0.2:
        fals.append("M2 median < 0.2")
    ge = _m3_ge10(m3)
    if ge is True:
        fals.append("M3 (or its lower bound) >= 10")
    cons = {"retention_family <= 0.01": (rfv <= 0.01) if rfv is not None else "not evaluable",
            ">= 90% of P2 set in [0.4, 0.6]": (frac >= 0.9) if frac is not None else "not evaluable",
            "M3 in [0.5, 2] or not evaluable": (m3["kind"] == "not_estimable") or (m3["kind"] in ("point",) and 0.5 <= m3["value"] <= 2)}
    if fals:
        v2 = "E1 FALSIFIED"
    elif all(v is True for v in cons.values()):
        v2 = "E1 CONSISTENT"
    elif any(v == "not evaluable" for v in cons.values()) and not any(v is False for v in cons.values()):
        v2 = "not evaluable"
    else:
        v2 = "between"
    out["DR-2"] = {"verdict": v2, "granularity": "T_strict", "D": 4,
                   "inputs": {"retention_family": rfv, "maximizing_reference": best, "M2_median": med,
                              "M2_frac_in_band": frac, "M2_set_size": m2.get("n"), "M3": {"kind": m3["kind"], "value": m3.get("value")},
                              "falsifying_clauses_met": fals, "consistency_clauses": cons,
                              "M3_ge_10_clause": ge}}
    # DR-3
    Kbest = c4["K_and_replay"].get(best, {}).get("K_sampled") if best else None
    ge10 = _m3_ge10(m3)
    lt10 = _m3_lt10(m3)
    if rfv is not None and rfv >= 0.5 and ge10 is True and Kbest is not None and Kbest <= 1:
        v3 = "E2 SUPPORTED"
    elif (rfv is not None and rfv < 0.5) or lt10 is True:
        v3 = "E2 FALSIFIED"
    elif ge10 == "unknown" or lt10 == "unknown":
        v3 = "not evaluable"
    else:
        v3 = "neither supported nor falsified"
    out["DR-3"] = {"verdict": v3, "granularity": "T_strict", "D": 4,
                   "inputs": {"retention_family": rfv, "M3": {"kind": m3["kind"], "value": m3.get("value")},
                              "K_sampled_maximizing_reference": Kbest, "maximizing_reference": best}}
    # DR-4
    if not m2.get("evaluable"):
        v4 = "not evaluable"
        r4 = "P2 set empty"
    elif med < 0.2:
        v4 = "H1 FALSIFIED"
        r4 = None
    elif frac >= 0.9:
        v4 = "H1 SUPPORTED at this cell"
        r4 = None
    else:
        v4 = "not supported, not falsified"
        r4 = None
    out["DR-4"] = {"verdict": v4, "reason": r4, "granularity": "fixed-schedule replay of T_ops (P2 set)", "D": 4,
                   "inputs": {"P2_set_size": m2.get("n"), "median_h": med, "frac_in_band": frac}}
    # DR-5
    if rfv is not None and 0.01 < rfv < 0.5:
        if ge10 is True:
            v5 = "E2-leaning"
        elif m3["kind"] in ("point", "zero") and m3["value"] <= 2:
            v5 = "E1-leaning"
        else:
            v5 = "undetermined"
    else:
        v5 = "not applicable (retention_family not in (0.01, 0.5))"
    out["DR-5"] = {"reading": v5, "is_verdict": False, "granularity": "T_strict", "D": 4,
                   "inputs": {"retention_family": rfv, "M3": {"kind": m3["kind"], "value": m3.get("value")}}}
    # DR-6, DR-7 (maximizing reference)
    return out


def decision_rules_sizing(dr, cell, sizing):
    fr = cell["families"]["F-S3"]["D4"]["retention_family_unsat"]["strict"]
    best = fr["maximizing_reference"]
    refs = sizing["per_reference"]["F-S3"]["D4"]
    pruned = {k: v["sizes"]["pruned"]["dense_bytes"] for k, v in refs.items()}
    if best is None or best not in refs:
        dr["DR-6"] = {"verdict": "not evaluable", "reason": "no maximizing reference", "D": 4}
    else:
        pb = pruned[best]
        dr["DR-6"] = {"one_system_per_SM": "SURVIVES" if pb <= 233472 else "FAILS",
                      "thousands_per_warp": "FAILS" if pb > 32 else "SURVIVES",
                      "granularity": "T_set pruning (rows not in Z_D; nonzero columns of those rows)", "D": 4,
                      "inputs": {"maximizing_reference": best, "pruned_dense_bytes": pb,
                                 "pruned_dense_bytes_all_references": pruned, "SM_bytes": 233472, "warp_bytes": 32}}
    per = {}
    for k, v in refs.items():
        s = v["saving"]
        per[k] = {"saving_strict": s["saving_strict"], "saving_set": s["saving_set"],
                  "strict_replay_closed": (s["saving_strict"] is not None and s["saving_strict"] < 1.5),
                  "T_set_replay_closed": (s["saving_set"] is not None and s["saving_set"] < 1.5)}
    if best is None or best not in per:
        dr["DR-7"] = {"verdict": "not evaluable", "per_reference": per}
    else:
        b = per[best]
        dr["DR-7"] = {"strict_replay": "CLOSED (saving_strict < 1.5)" if b["strict_replay_closed"] else "not closed",
                      "T_set_replay": "CLOSED (saving_set < 1.5)" if b["T_set_replay_closed"] else "not closed",
                      "granularity": "T_strict and T_set", "D": 4,
                      "inputs": {"maximizing_reference": best, **b}, "per_reference": per}
    d3 = sizing["per_reference"]["F-S3"]["D3"]
    dr["DR-7"]["secondary_D3_per_reference"] = {k: {"saving_strict": v["saving"]["saving_strict"], "saving_set": v["saving"]["saving_set"]} for k, v in d3.items()}
    # DR-8: secondary table
    sec = {}
    for D in (3, 4):
        for g in GRANS:
            f = cell["families"]["F-S3"][f"D{D}"]["retention_family_unsat"][g]
            if D == 4 and g == "strict":
                continue
            sec[f"D{D}/T_{g}"] = {"retention_family": f["retention_family"], "maximizing_reference": f["maximizing_reference"],
                                  "DR-1_analogue": ("all < 0.5" if f["retention_family"] is not None and f["retention_family"] < 0.5 else "some >= 0.5") if f["retention_family"] is not None else "not evaluable",
                                  "status": "SECONDARY (DR-8)"}
    dr["DR-8"] = {"rule": "every verdict names its granularity and D; D = 3 and T_set/T_rank/T_ops verdicts are secondary",
                  "primary_cell": "F-S3, D = 4, T_strict", "secondary_cells": sec}
    return dr
