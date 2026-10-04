"""Phase 9: aggregation, hull accounting (OBJ-3), TS1R (M2R), the 1-in-R_4
rate (M-R4), instrument checks (M5), invalidation and decision rules
RR-1..RR-10 for EXP-CERTBIN-3f06d1.

Copied from EXP-CERTBIN-4e92d7/impl/analysis.py and rewritten for the v2
contract (impl-provenance.json). Mechanical only: every threshold below is
copied from the frozen specification (version 1); nothing here chooses a
threshold, a reference or a granularity after seeing results. Every interval
and tail is exact (xstats.py).
"""
import math
from collections import Counter

import numpy as np

from stats import entropy_bits, binary_entropy, median, mann_whitney
from xstats import (clopper_pearson, cp_pair, band_half, band_binom, binom_sf_exact, fisher_one_sided_greater,
                    frac_report)
from vspace import (affine_hull, restrict, Echelon, solve_affine_system, parity, int_rank)
from fractions import Fraction

FAMS = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1", "F-NULLF2"]
AFFINE = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1"]
CURVE_ALG = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX"]
GRANS = ["rank", "set", "strict", "ops"]
DS = [3, 4]
CELLS = ["R1", "R2", "R3"]
N = 17
S_SELFTEST = 2026092410099
STAGE1_RATE_INTERVAL = (0.799, 0.875)


def primary_keys(fam, unit):
    if fam == "F-PLANT":
        return ["F-S3:U1", "F-S3:U2", "F-S3:U3", "F-S3:S1", "F-S3:S2", "F-S3:modal", "modal"]
    labels = [r["label"] for r in unit["refs"]]
    return [k for k in ("U1", "U2", "U3", "S1", "S2", "modal") if k in labels]


def m1_keys(fam, unit):
    if fam == "F-PLANT":
        return ["F-S3:U1", "F-S3:U2", "F-S3:U3", "modal"]
    labels = [r["label"] for r in unit["refs"]]
    return [k for k in ("U1", "U2", "U3", "modal") if k in labels]


def ts1r_keys(fam, unit):
    """I-19: the family's references for the TS1R evaluation set."""
    if fam == "F-PLANT":
        return ["F-S3:U1", "F-S3:U2", "F-S3:U3", "F-S3:S1", "F-S3:S2", "F-S3:modal", "modal"]
    return [k for k in ("U1", "U2", "U3", "S1", "S2", "modal") if k in unit["hazards"]]


def cpd(x, n):
    r = clopper_pearson(x, n)
    return None if r is None else {"lo": r["lo"], "hi": r["hi"], "lo_str": r["lo_str"], "hi_str": r["hi_str"]}


def retention(records, key, g, arm):
    sub = [r for r in records if not r["degenerate"] and r["stratum"] == arm and key in r["refs"]]
    n = len(sub)
    x = sum(1 for r in sub if r["refs"][key]["match"][g])
    return {"x": x, "n": n, "value": (x / n) if n else None, "cp95": cpd(x, n)}


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
                    "frac_f_div_le_0.01": (sum(1 for x in f if x <= 0.01) / len(f)) if f else None,
                    "n_f_div_le_0.01": sum(1 for x in f if x <= 0.01),
                    "quantiles": [float(np.quantile(f, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)] if f else None,
                    "hist_10bins": hist, "n_match_strict": sum(1 for c in sub if c["match"]["strict"]),
                    "divergence_step_k_counts_first10": dict(sorted(Counter(min(c["kdiv"], 10) for c in sub).items())),
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


def expected_max_class(N_, d, reps, rng):
    if d <= 0 or N_ <= 0:
        return None
    x = rng.integers(0, d, size=(reps, N_))
    mx = [int(np.bincount(row, minlength=d).max()) for row in x]
    return {"mean": float(np.mean(mx)), "q99": float(np.quantile(mx, 0.99)), "max": int(max(mx)), "reps": reps}


# ---------------------------------------------------------------------------
# hull accounting
# ---------------------------------------------------------------------------
class WCoords:
    """Coordinates of vectors of W in the (ordered) basis Wb."""

    def __init__(self, Wb):
        self.rows = []  # (lead, vec, coordmask) fully reduced
        for i, w in enumerate(Wb):
            v, m = w, 1 << i
            for lb, rv, rm in self.rows:
                if (v >> lb) & 1:
                    v ^= rv
                    m ^= rm
            assert v
            lb = v.bit_length() - 1
            rows2 = []
            for (a, rv, rm) in self.rows:
                if (rv >> lb) & 1:
                    rv ^= v
                    rm ^= m
                rows2.append((a, rv, rm))
            self.rows = rows2 + [(lb, v, m)]

    def coords(self, x):
        c = 0
        for lb, rv, rm in self.rows:
            if (x >> lb) & 1:
                x ^= rv
                c ^= rm
        return c if x == 0 else None


def family_hull(P1, fam, plan):
    tg = P1["F-S3"]["targets"] if fam in ("F-S3", "F-AFF-1", "F-S3-REV") else P1[fam]["targets"]
    tg = sorted(tg, key=lambda t: t["idx"])
    if fam == "F-S3-REV":
        tg = tg[:plan["counts"]["rev_targets"]]
    nd = [t for t in tg if not t["degenerate"]]
    h0, Wb, z = affine_hull([t["x_R"] for t in nd])
    return {"n_points": len(nd), "h0": h0, "h0_idx": nd[0]["idx"] if nd else None, "dim_W": len(Wb), "W_basis": Wb,
            "zero_in_H": z}


def ref_xR_map(P1, U, fam, D):
    """reference key -> x_R of the reference instance, for this unit."""
    m = {}
    src = {"F-S3": "F-S3", "F-S3-REV": "F-S3", "F-RANDX": "F-RANDX", "F-AFF-1": "F-AFF-1", "F-PLANT": None}[fam]
    if src:
        for r in P1[src]["refs"]:
            m[r["selected_as"]] = r["x_R"]
    unit = U[(fam, D)]
    tgt = {t["idx"]: t for t in (P1["F-S3"]["targets"] if fam in ("F-S3", "F-S3-REV", "F-AFF-1") else P1[fam]["targets"])}
    if unit.get("modal_info"):
        m["modal"] = tgt[unit["modal_info"]["modal_idx"]]["x_R"]
    if fam in ("F-PLANT", "F-RANDX"):
        for r in P1["F-S3"]["refs"]:
            m["F-S3:" + r["selected_as"]] = r["x_R"]
        u3 = U[("F-S3", D)]
        s3t = {t["idx"]: t for t in P1["F-S3"]["targets"]}
        m["F-S3:modal"] = s3t[u3["modal_info"]["modal_idx"]]["x_R"]
    return m


def hull_ref_analysis(tab, recs, key, hull, x_ref, min_surv):
    """Everything exact about one reference on one family's hull."""
    a0 = [int(x) for x in tab["a0"]]
    a = [int(x) for x in tab["a"]]
    K = len(a)
    Wb = hull["W_basis"]
    h0 = hull["h0"]
    d = len(Wb)
    rest = [restrict(x, Wb) for x in a]
    ech = Echelon()
    inc = [ech.add(rv) for rv in rest]
    K_rank_hull = sum(inc)
    nz = [x for x in a if x]
    K_rank = int_rank(nz)
    # scored targets and their first-zero indices (forms path)
    if key == "modal":
        scored = [r for r in recs if not r["degenerate"] and r["idx"] > 100 and key in r["refs"]]
    else:
        scored = [r for r in recs if not r["degenerate"] and key in r["refs"]]
    fz = [r["refs"][key]["replay_first_zero"] for r in scored]
    idxs = [r["idx"] for r in scored]
    counts = Counter(fz)
    Sk = []
    zk = []
    s = len(fz)
    for k in range(K):
        Sk.append(s)
        z = counts.get(k, 0)
        zk.append(z)
        s -= z
    survivors = s
    table_ok = (Sk == [int(x) for x in tab["S_k"]] and zk == [int(x) for x in tab["zeros_k"]]
                and survivors == int(tab["full_replay_survivors"]))
    # Sigma over F_2^n and Sigma_H over H
    sol = solve_affine_system([(a[k], 1 ^ a0[k]) for k in range(K)], N)
    sol_H = solve_affine_system([(rest[k], 1 ^ a0[k] ^ parity(a[k] & h0)) for k in range(K)], d)
    wc = WCoords(Wb)
    kerE = None
    if sol is not None:
        kerE = Echelon()
        for v in sol[1]:
            kerE.add(v)
    kerH = None
    if sol_H is not None:
        kerH = Echelon()
        for v in sol_H[1]:
            kerH.add(v)
    in_sigma = 0
    in_sigmaH = 0
    for r in scored:
        x = r["x_R"]
        if sol is not None and kerE.reduce(x ^ sol[0]) == 0:
            in_sigma += 1
        c = wc.coords(x ^ h0)
        if sol_H is not None and c is not None and kerH.reduce(c ^ sol_H[0]) == 0:
            in_sigmaH += 1
    sigmaH_elems = None
    if sol_H is not None and len(sol_H[1]) <= 10:
        elems = []
        for mask in range(1 << len(sol_H[1])):
            c = sol_H[0]
            for i, v in enumerate(sol_H[1]):
                if (mask >> i) & 1:
                    c ^= v
            x = h0
            for i, w in enumerate(Wb):
                if (c >> i) & 1:
                    x ^= w
            elems.append(x)
        sigmaH_elems = sorted(elems)
    ref_in_H = (wc.coords(x_ref ^ h0) is not None) if x_ref is not None else None
    # C-HZERO and hazard rows
    hz_viol = []
    rows = []
    trunc = next((k for k in range(K) if Sk[k] == 0), K)
    ts1r_meas = []
    n_rep = 0
    rep_nonzero = []
    for k in range(K):
        if Sk[k] >= 1 and not inc[k] and zk[k] > 0:
            hz_viol.append({"k": k, "S_k": Sk[k], "zeros": zk[k]})
        if k < trunc:
            lo, hi = band_half(Sk[k])
            rows.append((Sk[k], zk[k], lo, hi))
        if Sk[k] >= min_surv:
            if inc[k]:
                members = tuple(sorted(i for i, f in zip(idxs, fz) if f >= k))
                ts1r_meas.append({"ref": key, "k": k, "S_k": Sk[k], "zeros": zk[k], "restriction": rest[k],
                                  "set_members_sha": _sha_tuple(members)})
            else:
                n_rep += 1
                if zk[k] != 0:
                    rep_nonzero.append({"k": k, "S_k": Sk[k], "zeros": zk[k]})
    info = {
        "K": K, "K_exact": len(nz), "K_rank": K_rank, "K_rank_hull": K_rank_hull, "dim_W": d,
        "zero_in_H": hull["zero_in_H"], "ref_in_H": ref_in_H,
        "K_sampled": int(tab["K_sampled"]),
        "Sigma_dim": (N - K_rank) if sol is not None else None, "Sigma_empty": sol is None,
        "Sigma_H_dim": (d - K_rank_hull) if sol_H is not None else None, "Sigma_H_empty": sol_H is None,
        "Sigma_H_elements": sigmaH_elems,
        "n_scored": len(scored), "full_replay_survivors": survivors,
        "targets_in_Sigma": in_sigma, "targets_in_Sigma_H": in_sigmaH,
        "Sigma_H_cap_T_over_T": (in_sigmaH / len(scored)) if scored else None,
        "predicted_retention_2^-K_rank": 2.0 ** (-K_rank),
        "measured_fixed_schedule_retention": (survivors / len(scored)) if scored else None,
        "C-SURV_pass": (survivors == in_sigma == in_sigmaH),
        "C-HZERO_violations": hz_viol,
        "hazard_table_recomputed_equal": table_ok,
        "n_rep_S_ge_min": n_rep, "n_rep_nonzero_h": rep_nonzero,
        "n_hull_increasing_S_ge_min": len(ts1r_meas),
        "truncated_at": trunc,
    }
    haz = {"a0": a0, "a": a, "hull_rank_increasing": [int(x) for x in inc],
           "S_k": [r[0] for r in rows], "zeros_k": [r[1] for r in rows],
           "h_k": [(r[1] / r[0]) for r in rows],
           "band_lo": [r[2] for r in rows], "band_hi": [r[3] for r in rows],
           "truncated_at_first_S_k_0": trunc}
    return info, haz, ts1r_meas


def _sha_tuple(t):
    import hashlib
    return hashlib.sha256((",".join(str(x) for x in t)).encode()).hexdigest()


def ts1r_summary(meas):
    """Deduplicate by (restriction, survivor set); o, m, exact tail."""
    dedup = {}
    complementary = 0
    for m in meas:
        k = (m["restriction"], m["set_members_sha"])
        if k in dedup:
            if dedup[k]["zeros"] != m["zeros"]:
                complementary += 1
            dedup[k]["also"].append([m["ref"], m["k"]])
            continue
        dedup[k] = dict(m, also=[])
    E = list(dedup.values())
    for e in E:
        lo, hi = band_half(e["S_k"])
        e["band"] = [lo, hi]
        e["h"] = e["zeros"] / e["S_k"]
        e["in_band"] = lo <= e["zeros"] <= hi
    m = len(E)
    o = sum(1 for e in E if not e["in_band"])
    P = binom_sf_exact(o, m, Fraction(1, 1000)) if m else None
    out = {"m": m, "o": o, "n_measurements_before_dedup": len(meas),
           "dedup_pairs_with_complementary_zero_counts": complementary,
           "P_Bin_m_0.001_ge_o": frac_report(P) if P is not None else None,
           "min_h": min((e["h"] for e in E), default=None), "max_h": max((e["h"] for e in E), default=None),
           "set": [{k: e[k] for k in ("ref", "k", "S_k", "zeros", "h", "band", "in_band", "restriction", "set_members_sha", "also")} for e in E]}
    if m < 5:
        v = "NOT EVALUABLE"
    elif P >= Fraction(1, 1000):
        v = "SUPPORTED"
    else:
        v = "FALSIFIED"
    out["RR-4_reading"] = v
    return out


# ---------------------------------------------------------------------------
def analyse_cell(cell, P1, U, plan):
    rng_tail = np.random.Generator(np.random.PCG64(np.random.SeedSequence([S_SELFTEST, 100 + CELLS.index(cell)])))
    min_surv = plan["counts"]["ts1r_min_survivors"]
    cs = {"families": {}}
    hazards_out = {}
    hull_out = {}
    sizing = {}
    hullchecks = {"C-SURV": [], "C-HZERO": [], "table_recompute": []}
    for fam in FAMS:
        cs["families"][fam] = {}
        hull = family_hull(P1, fam, plan) if fam in AFFINE else None
        hull_out[fam] = hull
        for D in DS:
            unit = U[(fam, D)]
            recs = unit["records"]
            keys = primary_keys(fam, unit)
            nd = [r for r in recs if not r["degenerate"]]
            arms = {a: [r for r in nd if r["stratum"] == a] for a in ("unsat", "sat")}
            c = {"N_targets": len(recs), "N_non_degenerate": len(nd), "N_degenerate": len(recs) - len(nd),
                 "arm_sizes": {a: len(v) for a, v in arms.items()},
                 "underpowered": {a: len(v) < 100 for a, v in arms.items()},
                 "reference_keys": keys, "modal_info": unit["modal_info"]}
            ret = {}
            for g in GRANS:
                ret[g] = {k: {arm: retention(recs, k, g, arm) for arm in ("unsat", "sat")} for k in keys}
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
            c["M1_retention_family_unsat"] = fr
            if fam == "F-RANDX":
                c["secondary_vs_F-S3_references"] = {g: {k: {arm: retention(recs, k, g, arm) for arm in ("unsat", "sat")}
                                                          for k in ("F-S3:U1", "F-S3:U2", "F-S3:U3", "F-S3:S1", "F-S3:S2", "F-S3:modal")}
                                                      for g in GRANS}
            # M1f
            c["M1f_first_divergence"] = {k: fdiv_stats(recs, k) for k in keys}
            refL = {r["label"]: r["len_strict"] for r in unit["refs"]}
            for k in keys:
                if k in unit["hazards"] and unit["hazards"][k] is not None:
                    refL.setdefault(k, len(unit["hazards"][k]["p"]))
            c["strict_own_elimination_hazard"] = {k: strict_own_hazard(recs, k, refL[k]) for k in keys if k in refL}
            # M4
            m4 = {}
            psat = len(arms["sat"]) / len(nd) if nd else None
            for g in GRANS:
                h, dist, n, mxc = entropy_bits([r["h_" + g] for r in nd])
                m4[g] = {"H_bits": h, "distinct": dist, "N": n, "largest_class": mxc,
                         "log2_N": math.log2(n) if n else None,
                         "saturated_at_log2_N": (h is not None and n and abs(h - math.log2(n)) < 1e-9),
                         "expected_max_class_uniform_null": expected_max_class(n, dist, 1000, rng_tail)}
            m4["P_sat"] = psat
            m4["h_P_sat"] = binary_entropy(psat) if psat is not None else None
            m4["note"] = "saturation at log2 N makes H uninformative when every family saturates (spec M4)"
            c["M4_entropy"] = m4
            # M-R4 (this D)
            c["one_in_R"] = {a: {"x": sum(1 for r in v if r["one_in_R"]), "n": len(v),
                                 "rate": (sum(1 for r in v if r["one_in_R"]) / len(v)) if v else None,
                                 "cp95": cpd(sum(1 for r in v if r["one_in_R"]), len(v))} for a, v in arms.items()}
            if fam in CURVE_ALG or fam == "F-AFF-1":
                split = {}
                for cls in ("x2E", "xE_not_2E", "twist"):
                    v = [r for r in arms["unsat"] if r.get("x2E_class") == cls]
                    x = sum(1 for r in v if r["one_in_R"])
                    split[cls] = {"x": x, "n": len(v), "rate": (x / len(v)) if v else None, "cp95": cpd(x, len(v))}
                c["one_in_R_unsat_by_x2E_class"] = split
                c["x2E_class_counts_non_degenerate"] = dict(Counter(r.get("x2E_class") for r in nd))
            c["rank_distribution"] = {a: dict(sorted(Counter(r["rank"] for r in v).items())) for a, v in arms.items()}
            c["rational_flag_rate"] = (sum(1 for r in nd if (r["rational_flag"] or 0) > 0) / len(nd)) if nd and fam in CURVE_ALG else None
            c["wall_seconds"] = unit["wall_seconds"]
            c["peak_rss_bytes_process"] = unit.get("peak_rss_bytes")
            # hull accounting (M1k), hazards, TS1R (M2R)
            hz = unit["hazards"]
            hazards_out.setdefault(fam, {})[f"D{D}"] = {}
            if fam in AFFINE:
                xmap = ref_xR_map(P1, U, fam, D)
                kinfo = {}
                meas_all = []
                tkeys = ts1r_keys(fam, unit)
                for k, tab in hz.items():
                    if tab is None:
                        continue
                    info, haz, meas = hull_ref_analysis(tab, recs, k, hull, xmap.get(k), min_surv)
                    haz["p"] = tab["p"]
                    haz["c"] = tab["c"]
                    kinfo[k] = info
                    hazards_out[fam][f"D{D}"][k] = {**haz, "K_rank": info["K_rank"], "K_rank_hull": info["K_rank_hull"],
                                                    "dim_W": info["dim_W"], "K_sampled": info["K_sampled"]}
                    if k in tkeys:
                        meas_all.extend(meas)
                    hullchecks["C-SURV"].append({"family": fam, "D": D, "ref": k, "pass": info["C-SURV_pass"],
                                                 "survivors": info["full_replay_survivors"],
                                                 "in_Sigma": info["targets_in_Sigma"], "in_Sigma_H": info["targets_in_Sigma_H"]})
                    if info["C-HZERO_violations"]:
                        hullchecks["C-HZERO"].append({"family": fam, "D": D, "ref": k, "violations": info["C-HZERO_violations"],
                                                      "ref_in_H": info["ref_in_H"]})
                    if not info["hazard_table_recomputed_equal"]:
                        hullchecks["table_recompute"].append({"family": fam, "D": D, "ref": k})
                c["M1k_hull_rank"] = {k: {kk: v[kk] for kk in ("K_rank", "K_rank_hull", "dim_W", "zero_in_H", "ref_in_H",
                                                               "Sigma_H_dim", "Sigma_H_empty", "Sigma_H_elements",
                                                               "targets_in_Sigma_H", "n_scored", "Sigma_H_cap_T_over_T",
                                                               "Sigma_dim", "Sigma_empty", "K", "K_exact", "K_sampled")}
                                      for k, v in kinfo.items()}
                c["K_and_replay"] = {k: {kk: v[kk] for kk in ("K", "K_sampled", "K_exact", "K_rank", "K_rank_hull",
                                                              "predicted_retention_2^-K_rank", "measured_fixed_schedule_retention",
                                                              "n_scored", "full_replay_survivors", "n_rep_S_ge_min",
                                                              "n_rep_nonzero_h", "n_hull_increasing_S_ge_min")}
                                     for k, v in kinfo.items()}
                for k, v in c["K_and_replay"].items():
                    v["K_over_rank"] = v["K_sampled"] / v["K"] if v["K"] else None
                ts = ts1r_summary(meas_all)
                ts["references"] = tkeys
                ts["n_rep"] = sum(kinfo[k]["n_rep_S_ge_min"] for k in tkeys if k in kinfo)
                ts["n_rep_all_h_zero"] = all(not kinfo[k]["n_rep_nonzero_h"] for k in tkeys if k in kinfo)
                ts["min_survivors"] = min_surv
                c["M2R_TS1R"] = ts
                c["hull"] = {kk: hull[kk] for kk in ("n_points", "h0", "h0_idx", "dim_W", "zero_in_H")}
                c["hull"]["W_basis"] = hull["W_basis"]
            else:
                c["K_and_replay"] = {k: {"K_sampled": t["K_sampled"], "K_basis": t["dependence_basis"],
                                         "K": len(t["p"]), "n_scored": t["n_scored"],
                                         "full_replay_survivors": t["full_replay_survivors"],
                                         "measured_fixed_schedule_retention": t["measured_fixed_schedule_retention"]}
                                     for k, t in hz.items() if t is not None}
                for k, t in hz.items():
                    if t is None:
                        continue
                    hazards_out[fam][f"D{D}"][k] = {"p": t["p"], "c": t["c"], "S_k": t["S_k"], "zeros_k": t["zeros_k"],
                                                    "dependence_basis": t["dependence_basis"], "K_sampled": t["K_sampled"]}
                c["M2R_TS1R"] = {"evaluable": False, "reason": "F-NULLF2 has no r-structure (no affine forms, no hull)"}
                c["M1k_hull_rank"] = {"evaluable": False, "reason": "no affine forms / hull for F-NULLF2"}
            cs["families"][fam][f"D{D}"] = c
            for r in unit["refs"]:
                sizing.setdefault(fam, {}).setdefault(f"D{D}", {})[r["label"]] = {
                    "sizes": r["sizes"], "saving": r["saving"], "rank": r["rank"], "Z_size": r["Z_size"]}
        # D* per arm
        d3 = {r["idx"]: r for r in U[(fam, 3)]["records"]}
        d4 = {r["idx"]: r for r in U[(fam, 4)]["records"]}
        dstar = {"unsat": Counter(), "sat": Counter()}
        for idx, r3 in d3.items():
            if r3["degenerate"]:
                continue
            ds = 3 if r3["one_in_R"] else (4 if d4[idx]["one_in_R"] else "not reached at D <= 4")
            dstar[r3["stratum"]][str(ds)] += 1
        cs["families"][fam]["D_star_distribution"] = {a: dict(v) for a, v in dstar.items()}

    # ---- RR-6 input: F-RANDX Fisher test (D = 4; D = 3 secondary)
    fisher = {}
    for D in DS:
        sp = cs["families"]["F-RANDX"][f"D{D}"]["one_in_R_unsat_by_x2E_class"]
        a, n1 = sp["x2E"]["x"], sp["x2E"]["n"]
        c_, n2 = sp["xE_not_2E"]["x"] + sp["twist"]["x"], sp["xE_not_2E"]["n"] + sp["twist"]["n"]
        if n1 == 0 or n2 == 0:
            fisher[f"D{D}"] = {"evaluable": False, "reason": "a group is empty", "table": [[a, n1 - a], [c_, n2 - c_]]}
        else:
            p = fisher_one_sided_greater(a, n1 - a, c_, n2 - c_)
            fisher[f"D{D}"] = {"evaluable": True, "table_rows_x2E_vs_off_cols_1inR_not": [[a, n1 - a], [c_, n2 - c_]],
                               "rate_x2E": a / n1, "rate_off_x2E_pooled": c_ / n2,
                               "p_one_sided_x2E_higher": frac_report(p), "p_value": float(p), "p_fraction": p}
    cs["x2E_modulation_F-RANDX"] = {k: {kk: vv for kk, vv in v.items() if kk != "p_fraction"} for k, v in fisher.items()}

    # ---- M3 (D = 4, T_strict), first-matching precedence
    num = cs["families"]["F-S3"]["D4"]["M1_retention_family_unsat"]["strict"]
    den = cs["families"]["F-AFF-1"]["D4"]["M1_retention_family_unsat"]["strict"]
    m3 = {"granularity": "T_strict", "D": 4,
          "numerator": {"family": "F-S3", "retention_family": num["retention_family"], "count": num["count"], "n": num["n"], "ref": num["maximizing_reference"]},
          "denominator": {"family": "F-AFF-1", "retention_family": den["retention_family"], "count": den["count"], "n": den["n"], "ref": den["maximizing_reference"]}}
    nc, dc = (num["count"] or 0), (den["count"] or 0)
    if nc == 0 and dc == 0:
        m3.update({"rule": 1, "kind": "not_estimable", "value": None,
                   "E1_[0.5,2]_clause": "not evaluable", "E2_>=10x_clause": "not met"})
    elif nc == 0:
        m3.update({"rule": 2, "kind": "zero", "value": 0.0, "E2_>=10x_clause": "not met"})
    elif dc == 0:
        ub = clopper_pearson(0, den["n"])
        m3.update({"rule": 3, "kind": "lower_bound", "value": num["retention_family"] / ub["hi"],
                   "denominator_cp95_upper": ub["hi"], "denominator_cp95_upper_str": ub["hi_str"]})
    else:
        m3.update({"rule": 4, "kind": "point", "value": num["retention_family"] / den["retention_family"],
                   "bootstrap95": bootstrap_m3(U)})
    cs["M3"] = m3

    # ---- tail check: F-RANDX fixed-schedule survival vs 2^-K_rank
    tails = {}
    for D in DS:
        for k, v in cs["families"]["F-RANDX"][f"D{D}"]["K_and_replay"].items():
            if k.startswith("F-S3:"):
                continue
            if v["K_rank"] >= N:
                tails[f"D{D}/{k}"] = {"K_rank": v["K_rank"], "status": "determined by the identity (K_rank = n): survival set = {r_ref}",
                                      "survivors": v["full_replay_survivors"], "n": v["n_scored"]}
            else:
                lo, hi = band_binom(v["n_scored"], Fraction(1, 2 ** v["K_rank"]))
                x = v["full_replay_survivors"]
                tails[f"D{D}/{k}"] = {"K_rank": v["K_rank"], "survivors": x, "n": v["n_scored"], "band99.9": [lo, hi],
                                      "inside": lo <= x <= hi}
    cs["tail_check_F-RANDX_survival_vs_2^-K_rank"] = tails
    cs["hull_per_family"] = {f: ({kk: h[kk] for kk in ("n_points", "h0", "h0_idx", "dim_W", "zero_in_H", "W_basis")} if h else None)
                             for f, h in hull_out.items()}
    return cs, hazards_out, sizing, hullchecks


def bootstrap_m3(U, B=10000):
    rng = np.random.Generator(np.random.PCG64(S_SELFTEST))
    per_fam = []
    for fam in ("F-S3", "F-AFF-1"):
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
    num, den = per_fam
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(den > 0, num / np.where(den > 0, den, 1), np.inf)
    rs = np.sort(r)
    return {"resamples": B, "seed": S_SELFTEST, "ci95": [float(rs[int(0.025 * B)]), float(rs[int(0.975 * B) - 1])],
            "n_infinite": int(np.isinf(r).sum())}


# ---------------------------------------------------------------------------
# instrument checks
# ---------------------------------------------------------------------------
def band_check_half(ones, n):
    lo, hi = band_half(n)
    return {"ones": ones, "n": n, "band99.9": [lo, hi], "inside": lo <= ones <= hi}


def cnulls_support(P1):
    from macaulay import affine_basis  # noqa: F401  (support read from phase-1 E^j below)
    from families import E_from_hex
    from gf2n import TableField
    from vspace import VBasis
    F = TableField()
    V = VBasis(P1["V"]["basis_b0_to_b8"], P1["V"]["label"])
    from macaulay import affine_basis as ab
    E0, Ej = ab(F, P1["curve"]["B"], V.basis)
    A0 = E_from_hex(P1["F-AFF-1"]["A0_hex"])
    Aj = [E_from_hex(x) for x in P1["F-AFF-1"]["Aj_hex"]]
    per = []
    ok = True
    pooled_ones = pooled_n = 0
    for lab, Em, Am in [("E'^0", E0, A0)] + [(f"E'^{j}'", Ej[j], Aj[j]) for j in range(len(Ej))]:
        supp = Em.astype(bool)
        contained = bool(not (Am.astype(bool) & ~supp).any())
        ones = int(Am[supp].sum())
        n = int(supp.sum())
        bc = band_check_half(ones, n)
        pooled_ones += ones
        pooled_n += n
        per.append({"matrix": lab, "support_contained": contained, **bc})
        ok &= contained and bc["inside"]
    aff = {"per_matrix": per, "pooled": band_check_half(pooled_ones, pooled_n), "pass": ok}
    # F-NULLF2
    U = E0.astype(bool).copy()
    for x in Ej:
        U |= x.astype(bool)
    insts = [c for c in P1["F-NULLF2"]["ref_scan"] if c.get("status") == "classified"] + P1["F-NULLF2"]["targets"]
    bad = []
    ones = 0
    n = 0
    for c in insts:
        Em = E_from_hex(c["E_hex"]).astype(bool)
        if (Em & ~U).any():
            bad.append(c.get("idx", c.get("draw")))
        ones += int(Em[U].sum())
        n += int(U.sum())
    nf = {"instances": len(insts), "support_violations": bad, "pooled": band_check_half(ones, n),
          "U_size": int(U.sum())}
    nf["pass"] = (not bad) and nf["pooled"]["inside"]
    return aff, nf


def instrument_checks_cell(cell, P1, U, det, ver, hullchecks, plan):
    out = {}

    def instances(fam):
        d = P1[fam]
        res = [("ref_scan", c) for c in d.get("ref_scan", []) if c.get("status") == "classified"]
        res += [("target", t) for t in d["targets"]]
        return res

    viol = []
    n = 0
    for fam in ("F-S3", "F-PLANT", "F-RANDX"):
        for kind, c in instances(fam):
            n += 1
            if not c["oracle_agree"] or c["s"] != c["s_A"]:
                viol.append({"family": fam, "kind": kind, "x_R": c["x_R"], "s_A": c["s_A"], "s_B": c["s"]})
    out["C-ORACLE"] = {"pass": not viol, "checked": n, "failed": len(viol), "violations": viol}
    viol = []
    nsol = ninst = 0
    for fam in ("F-S3", "F-PLANT", "F-RANDX", "F-AFF-1", "F-NULLF2"):
        for kind, c in instances(fam):
            ninst += 1
            nsol += len(c["sols"])
            for w in c["wit_fail"]:
                viol.append({"family": fam, "kind": kind, "x_R": c.get("x_R"), **w})
    plant_bad = [t["idx"] for t in P1["F-PLANT"]["targets"] if t["s"] < 1 or not t["planted_witness_found"]]
    out["C-WIT"] = {"pass": not viol and not plant_bad, "instances": ninst, "solutions_verified": nsol,
                    "failed": len(viol), "violations": viol, "F-PLANT_failures": plant_bad}
    viol = []
    n = 0
    for fam in ("F-S3", "F-PLANT", "F-RANDX", "F-AFF-1"):
        for kind, c in instances(fam):
            n += 1
            if not c.get("aff_ok", False):
                viol.append({"family": fam, "kind": kind, "x_R": c.get("x_R")})
    direct, dfail, selff = {}, [], []
    for fam in AFFINE:
        for D in DS:
            cd = U[(fam, D)]["caff_direct"]
            direct[f"{fam}/D{D}"] = {"checked_pairs": cd["checked_pairs"], "mismatch_pairs": cd["mismatch_pairs"]}
            if cd["mismatch_pairs"]:
                dfail.append({"family": fam, "D": D, "mismatches": cd["mismatches"]})
            for r in U[(fam, D)]["refs"]:
                if r.get("forms_selfcheck_direct_eq_affine_at_r_ref") is False:
                    selff.append({"family": fam, "D": D, "ref": r["label"]})
    out["C-AFF"] = {"pass": not viol and not dfail and not selff, "identity_checked": n, "identity_failed": len(viol),
                    "identity_violations": viol, "direct_replay_vs_affine": direct, "direct_replay_failures": dfail,
                    "reference_self_replay_vs_forms_failures": selff,
                    "affected_families": sorted({v["family"] for v in viol} | {f["family"] for f in dfail} | {f["family"] for f in selff})}
    cf = {}
    cff = []
    for fam in AFFINE:
        for D in DS:
            x = U[(fam, D)]["cforms"]
            cf[f"{fam}/D{D}"] = {"scalar_path_checked": x["scalar_path_checked"], "scalar_path_mismatches": len(x["scalar_path_mismatches"]),
                                 "direct_checked": x["direct_checked"], "direct_mismatches": len(x["direct_mismatches"])}
            if x["scalar_path_mismatches"] or x["direct_mismatches"]:
                cff.append({"family": fam, "D": D, "scalar": x["scalar_path_mismatches"][:20], "direct": x["direct_mismatches"][:20]})
    out["C-FORMS"] = {"pass": not cff, "per_family_D": cf, "violations": cff, "affected_families": sorted({v["family"] for v in cff})}
    sfail = [c for c in hullchecks["C-SURV"] if not c["pass"]]
    out["C-SURV"] = {"pass": not sfail, "checked": len(hullchecks["C-SURV"]), "violations": sfail,
                     "affected_families": sorted({v["family"] for v in sfail}),
                     "hazard_table_recompute_mismatches": hullchecks["table_recompute"]}
    out["C-HZERO"] = {"pass": not hullchecks["C-HZERO"], "violations": hullchecks["C-HZERO"],
                      "affected_families": sorted({v["family"] for v in hullchecks["C-HZERO"]}),
                      "note": "instrument, never evidence about TS1R"}
    out["C-TR"] = {**P1["C-TR"], "consequence_if_fail": "data: the measured hull is used anyway (no invalidation)"}
    pc = det["per_cell_D"]
    dm = [m for m in det["mismatches"] if m.get("cell") == cell]
    out["C-DET"] = {"pass": not dm and all(pc[f"{cell}/D{D}"]["targets_matched"] == pc[f"{cell}/D{D}"]["targets_checked"] and
                                           pc[f"{cell}/D{D}"]["refs_matched"] == pc[f"{cell}/D{D}"]["refs_checked"] for D in DS),
                    "per_D": {f"D{D}": pc[f"{cell}/D{D}"] for D in DS}, "mismatches": dm,
                    "separate_process": det.get("process")}
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
    ps = {"PS0": [], "PS1": []}
    implied = {"PS3": [], "PS2": {}}
    n = 0
    for (fam, D), unit in U.items():
        for r in unit["records"]:
            n += 1
            if r["PS0_fail"]:
                ps["PS0"].append({"family": fam, "D": D, "idx": r["idx"], "detail": r["PS0_fail"]})
            if r["PS1_fail"]:
                ps["PS1"].append({"family": fam, "D": D, "idx": r["idx"]})
            if r["PS3_fail"]:
                implied["PS3"].append({"family": fam, "D": D, "idx": r["idx"]})
        for ref in unit["refs"]:
            n += 1
            ch = ref["checks"]
            if ch["PS0_fail"]:
                ps["PS0"].append({"family": fam, "D": D, "ref": ref["label"], "detail": ch["PS0_fail"]})
            if ch["PS1_fail"]:
                ps["PS1"].append({"family": fam, "D": D, "ref": ref["label"]})
    for D in DS:
        unit = U[("F-S3", D)]
        ur = [r for r in unit["refs"] if r["one_in_R"] and (r["label"].startswith("U") or
                                                            (r["label"] == "modal" and unit["modal_info"]["stratum"] == "unsat"))]
        sat_sets = [r["h_set"] for r in unit["records"] if r["s"] >= 1] + [r["h_set"] for r in U[("F-PLANT", D)]["records"] if r["s"] >= 1]
        eq = sum(1 for r in ur for h in sat_sets if h == r["h_set"])
        implied["PS2"][f"F-S3/D{D}"] = ("VACUOUS" if not ur else {"unsat_refs_with_1_in_R": [r["label"] for r in ur],
                                                                   "sat_instances_compared": len(sat_sets), "equal_T_set": eq})
    vpc = ver["per_cell"].get(cell, {"certificates": 0, "passed": 0, "failed_idx": []}) if ver else None
    want = plan["counts"]["ps0prime_certificates_per_cell"]
    ps0p_fail = (ver is None or not ver.get("modulus_irreducible_brute_force") or vpc["passed"] != vpc["certificates"])
    out["C-PROPS"] = {"pass": not (ps["PS0"] or ps["PS1"] or ps0p_fail),
                      "instances_checked": n,
                      "PS0": {"failed": len(ps["PS0"]), "violations": ps["PS0"]},
                      "PS1": {"failed": len(ps["PS1"]), "violations": ps["PS1"]},
                      "PS0prime": {"certificates": vpc["certificates"] if vpc else 0, "passed": vpc["passed"] if vpc else 0,
                                   "failed_idx": vpc["failed_idx"] if vpc else None, "planned": want,
                                   "shortfall": max(0, want - (vpc["certificates"] if vpc else 0)),
                                   "verifier_process": ver.get("process") if ver else None,
                                   "verifier_imports_from_impl": ver["independence"]["imports_from_impl"] if ver else None,
                                   "fail": ps0p_fail},
                      "implied_checks_not_counted": {"PS2": implied["PS2"], "PS3_failures": implied["PS3"]}}
    # C-REV
    rv = []
    ncmp = 0
    for D in DS:
        a = {r["idx"]: r for r in U[("F-S3", D)]["records"]}
        b = {r["idx"]: r for r in U[("F-S3-REV", D)]["records"]}
        for idx, rb in b.items():
            ra = a[idx]
            ncmp += 1
            d = [f for f in ("rank", "h_pivcols", "one_in_R") if ra[f] != rb[f]]
            if d:
                rv.append({"D": D, "idx": idx, "differs": d})
        ra_ = {r["label"]: r for r in U[("F-S3", D)]["refs"]}
        rb_ = {r["label"]: r for r in U[("F-S3-REV", D)]["refs"]}
        for lab in ("U1", "U2", "U3", "S1", "S2"):
            if lab in ra_ and lab in rb_:
                ncmp += 1
                d = [f for f in ("rank", "h_pivcols", "one_in_R") if ra_[lab][f] != rb_[lab][f]]
                if d:
                    rv.append({"D": D, "ref": lab, "differs": d})
    out["C-REV"] = {"pass": not rv, "instances_compared": ncmp, "violations": rv,
                    "invariants": "rank_D, pivot-column set, 1 in R_D (per instance, F-S3 vs F-S3-REV)"}
    aff, nf = cnulls_support(P1)
    hashes = {f"{fam}/D{D}": U[(fam, D)]["code_path_sha256"]["_combined"] for (fam, D) in U}
    out["C-NULLS"] = {"pass_support_and_bands": aff["pass"] and nf["pass"], "F-AFF-1": aff, "F-NULLF2": nf,
                      "code_path_combined_sha256_per_unit": hashes}
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
    out["REF_SELF_REPLAY"] = {"pass": not srf, "violations": srf}
    return out


def invalidation(global_checks, cellchecks):
    """INV-1..INV-7 per cell, plus the run-level void."""
    inv = {}
    run_void = False
    reasons = []
    if not global_checks["C-FIX"]["pass"] or not global_checks["C-SELF"]["pass"]:
        run_void = True
        reasons.append("INV-1 (C-FIX or C-SELF)")
    if not global_checks["C-PROV"]["pass"]:
        run_void = True
        reasons.append("INV-2 (C-PROV)")
    nulls_hash_ok = global_checks["C-NULLS_code_path"]["pass"]
    for cell, ch in cellchecks.items():
        t = {}
        voided = []
        t["INV-3"] = not (ch["C-ORACLE"]["pass"] and ch["C-WIT"]["pass"])
        if t["INV-3"]:
            voided.append("every arm-dependent metric, all families of this cell (INV-3)")
        fams4 = set()
        for c in ("C-AFF", "C-FORMS", "C-SURV", "C-HZERO"):
            if not ch[c]["pass"]:
                af = ch[c].get("affected_families") or AFFINE
                fams4 |= set(af if len(af) <= 1 else AFFINE)
        t["INV-4"] = bool(fams4)
        if fams4:
            voided.append(f"M2R, K, K_rank and K_rank_hull for {sorted(fams4)} (INV-4)")
        t["INV-5"] = not (ch["C-DET"]["pass"] and ch["C-PASS"]["pass"] and ch["C-REV"]["pass"] and ch["NESTING"]["pass"])
        t["INV-6"] = not ch["C-PROPS"]["pass"]
        if t["INV-5"]:
            run_void = True
            reasons.append(f"INV-5 at {cell}")
        if t["INV-6"]:
            run_void = True
            reasons.append(f"INV-6 at {cell}")
        nulls_void = not (ch["C-NULLS"]["pass_support_and_bands"] and nulls_hash_ok)
        if nulls_void:
            voided.append("null comparisons (M3, RR-5 nulls) (C-NULLS)")
        if ch["HASH_CONTENT"]["anomalies"]:
            voided.append("hash/content disagreement recorded (not a declared INV)")
        inv[cell] = {"triggered": t, "voided_metrics": voided, "INV-4_families": sorted(fams4), "nulls_void": nulls_void,
                     "arm_metrics_void": t["INV-3"]}
    return {"per_cell": inv, "run_void": run_void, "run_void_reasons": reasons,
            "INV-7": "a void run is an implementation failure (AGENTS.md core rule 5)"}


# ---------------------------------------------------------------------------
# decision rules
# ---------------------------------------------------------------------------
def _m3_flags(m3):
    k = m3["kind"]
    if k == "point":
        return {"ge10": m3["value"] >= 10, "lt10": m3["value"] < 10}
    if k == "zero":
        return {"ge10": False, "lt10": True}
    if k == "lower_bound":
        return {"ge10": True if m3["value"] >= 10 else "unknown", "lt10": False if m3["value"] >= 10 else "unknown"}
    return {"ge10": False, "lt10": "unknown"}


def decision_rules_cell(cell, cs, inv):
    out = {}
    c4 = cs["families"]["F-S3"]["D4"]
    c3 = cs["families"]["F-S3"]["D3"]
    arm_void = inv["arm_metrics_void"]
    fr = c4["M1_retention_family_unsat"]["strict"]
    per = fr["per_reference"]
    # RR-1
    vals = {k: per[k]["value"] for k in ("U1", "U2", "U3", "modal") if k in per}
    missing = [k for k in ("U1", "U2", "U3", "modal") if vals.get(k) is None]
    if arm_void:
        v1, r1 = "not evaluable", "INV-3 voids arm-dependent metrics"
    elif missing:
        v1, r1 = "not evaluable", f"references missing or empty arm: {missing}"
    else:
        v1 = "DIRECTION REPLICATES" if all(v < 0.5 for v in vals.values()) else "FAILS TO REPLICATE"
        r1 = None
    out["RR-1"] = {"verdict": v1, "reason": r1, "family": "F-S3", "granularity": "T_strict", "D": 4,
                   "inputs": {k: {"x": per[k]["x"], "n": per[k]["n"], "value": per[k]["value"], "cp95": per[k]["cp95"]} for k in per}}
    # RR-2
    mk = c4.get("M1k_hull_rank", {})
    rows = {k: {"K_rank_hull": v["K_rank_hull"], "dim_W": v["dim_W"], "K_rank": v["K_rank"], "Sigma_H_dim": v["Sigma_H_dim"],
                "targets_in_Sigma_H": v["targets_in_Sigma_H"], "n_scored": v["n_scored"]}
            for k, v in mk.items() if k in ("U1", "U2", "U3", "S1", "S2", "modal")}
    if "F-S3" in inv["INV-4_families"]:
        v2, r2 = "not evaluable", "INV-4 voids K_rank_hull for F-S3"
    elif not rows:
        v2, r2 = "not evaluable", "no reference"
    else:
        full = all(v["K_rank_hull"] == v["dim_W"] for v in rows.values())
        v2 = "HULL RANK FULL" if full else "REVISIT TRIGGER FIRES"
        r2 = None
    d3 = {k: {"K_rank_hull": v["K_rank_hull"], "dim_W": v["dim_W"]} for k, v in c3.get("M1k_hull_rank", {}).items()
          if k in ("U1", "U2", "U3", "S1", "S2", "modal")}
    out["RR-2"] = {"verdict": v2, "reason": r2, "family": "F-S3", "D": 4, "inputs_D4": rows, "reported_D3": d3}
    # RR-3
    fd = c4["M1f_first_divergence"]
    med = {k: {"unsat": fd[k]["unsat"]["median_f_div"], "sat": fd[k]["sat"]["median_f_div"]} for k in ("U1", "U2", "U3") if k in fd}
    if arm_void:
        v3, r3 = "not evaluable", "INV-3"
    elif len(med) < 3 or any(v is None for m in med.values() for v in m.values()):
        v3, r3 = "not evaluable", "missing reference or empty arm"
    else:
        v3 = "EARLY DIVERGENCE REPLICATES" if all(v <= 0.1 for m in med.values() for v in m.values()) else "does not replicate"
        r3 = None
    out["RR-3"] = {"verdict": v3, "reason": r3, "family": "F-S3", "granularity": "T_strict (f_div)", "D": 4,
                   "inputs_median_f_div": med,
                   "modal_reported_not_in_rule": ({"unsat": fd["modal"]["unsat"]["median_f_div"], "sat": fd["modal"]["sat"]["median_f_div"]} if "modal" in fd else None)}
    # RR-4
    ts = c4["M2R_TS1R"]
    if "F-S3" in inv["INV-4_families"]:
        v4 = "not evaluable (INV-4)"
    else:
        v4 = ts["RR-4_reading"]
    out["RR-4"] = {"verdict": v4, "family": "F-S3", "D": 4, "heuristic": "HEUR-CERTBIN-TS1R",
                   "inputs": {"m": ts["m"], "o": ts["o"], "P_Bin_m_0.001_ge_o": ts["P_Bin_m_0.001_ge_o"],
                              "n_rep": ts["n_rep"], "n_rep_all_h_zero": ts["n_rep_all_h_zero"]},
                   "secondary": {f"{fam}/D{D}": cs["families"][fam][f"D{D}"]["M2R_TS1R"].get("RR-4_reading")
                                 for fam in AFFINE for D in DS if not (fam == "F-S3" and D == 4)}}
    # RR-5
    r4 = c4["one_in_R"]["unsat"]
    ci = r4["cp95"]
    if arm_void or ci is None:
        v5 = "not evaluable"
    elif ci["hi"] < STAGE1_RATE_INTERVAL[0]:
        v5 = "LOWER"
    elif ci["lo"] > STAGE1_RATE_INTERVAL[1]:
        v5 = "HIGHER"
    else:
        v5 = "REPLICATES"
    nulls = {}
    for f in ("F-AFF-1", "F-NULLF2"):
        u = cs["families"][f]["D4"]["one_in_R"]["unsat"]
        nulls[f] = {"x": u["x"], "n": u["n"], "rate": u["rate"], "cp95": u["cp95"]}
    if inv["nulls_void"]:
        vn = "not evaluable (C-NULLS)"
    elif any(v["cp95"] is None for v in nulls.values()):
        vn = "not evaluable (empty null unsat arm)"
    else:
        vn = "NULLS CLEAN" if all(v["cp95"]["hi"] <= 0.05 for v in nulls.values()) else "NULLS NOT CLEAN"
    out["RR-5"] = {"verdict": v5, "nulls": vn, "family": "F-S3", "D": 4,
                   "inputs": {"x": r4["x"], "n": r4["n"], "rate": r4["rate"], "cp95": ci,
                              "stage1_interval": list(STAGE1_RATE_INTERVAL), "nulls": nulls,
                              "underpowered_unsat_arm": r4["n"] < 100}}
    # RR-6
    fz = cs["x2E_modulation_F-RANDX"]["D4"]
    if arm_void or not fz.get("evaluable"):
        v6 = "not evaluable"
    else:
        p = fz["p_value"]
        v6 = "MODULATION REPLICATES" if p < 0.01 else ("ABSENT" if p >= 0.2 else "WEAK")
    out["RR-6"] = {"verdict": v6, "family": "F-RANDX (unsat arm)", "D": 4, "inputs": fz,
                   "split": cs["families"]["F-RANDX"]["D4"]["one_in_R_unsat_by_x2E_class"]}
    # RR-7
    m3 = cs["M3"]
    fl = _m3_flags(m3)
    rfv = fr["retention_family"]
    best = fr["maximizing_reference"]
    Kb = c4["K_and_replay"].get(best, {}).get("K_sampled") if best else None
    if arm_void or rfv is None:
        v7 = "not evaluable"
    elif rfv < 0.5 or fl["lt10"] is True or m3["rule"] in (1, 2):
        v7 = "E2 FALSIFIED"
    elif rfv >= 0.5 and fl["ge10"] is True and Kb is not None and Kb <= 1:
        v7 = "E2 SUPPORTED"
    else:
        v7 = "neither (M3 clause unknown or K > 1)"
    out["RR-7"] = {"verdict": v7, "family": "F-S3", "granularity": "T_strict", "D": 4,
                   "inputs": {"retention_family": rfv, "maximizing_reference": best, "M3": {k: m3.get(k) for k in ("rule", "kind", "value")},
                              "K_sampled_maximizing_reference": Kb}}
    return out


def decision_rules_all(cells_summary, inv, global_checks, cellchecks):
    dr = {"per_cell": {}}
    for cell in CELLS:
        d = decision_rules_cell(cell, cells_summary[cell], inv["per_cell"][cell])
        fails = [k for k, v in cellchecks[cell].items() if isinstance(v, dict) and "pass" in v and v["pass"] is False and k != "C-TR"]
        if cellchecks[cell]["C-NULLS"]["pass_support_and_bands"] is False:
            fails.append("C-NULLS")
        d["RR-8"] = {"verdict": "ALL CONTROLS PASS" if not fails and not inv["run_void"] else "CONTROL FAILURE(S): invalidation applied before any verdict",
                     "failed_controls": fails, "C-TR": {"pass": cellchecks[cell]["C-TR"]["pass"], "note": "C-TR failure is data"},
                     "invalidation": inv["per_cell"][cell]}
        dr["per_cell"][cell] = d
    g = [k for k in ("C-FIX", "C-SELF", "C-PROV", "C-NULLS_code_path") if not global_checks[k]["pass"]]
    dr["global_controls_failed"] = g
    if inv["run_void"]:
        for cell in CELLS:
            for k in ("RR-1", "RR-2", "RR-3", "RR-4", "RR-5", "RR-6", "RR-7"):
                dr["per_cell"][cell][k]["verdict_before_void"] = dr["per_cell"][cell][k]["verdict"]
                dr["per_cell"][cell][k]["verdict"] = "VOID (run invalid: " + "; ".join(inv["run_void_reasons"]) + ")"
    pc = dr["per_cell"]
    rr1 = {c: pc[c]["RR-1"]["verdict"] for c in CELLS}
    rr2 = {c: pc[c]["RR-2"]["verdict"] for c in CELLS}
    rr5 = {c: (pc[c]["RR-5"]["verdict"], pc[c]["RR-5"]["nulls"]) for c in CELLS}
    if all(v == "DIRECTION REPLICATES" for v in rr1.values()):
        if all(v == "HULL RANK FULL" for v in rr2.values()):
            a = "REPLICATED (direction and obstruction)"
        elif any(v == "REVISIT TRIGGER FIRES" for v in rr2.values()):
            a = "DIRECTION REPLICATED, OBSTRUCTION NOT"
        else:
            a = "not evaluable (RR-2 not evaluable at some cell)"
    elif any(v == "FAILS TO REPLICATE" for v in rr1.values()):
        a = "NOT REPLICATED"
    else:
        a = "not evaluable (RR-1 not evaluable at some cell)"
    side = {c: v for c, (v, _) in rr5.items() if v in ("HIGHER", "LOWER")}
    if side:
        c2 = "RATE CURVE- OR V-DEPENDENT: " + ", ".join(f"{c} {v}" for c, v in side.items())
    elif all(v == "REPLICATES" and n == "NULLS CLEAN" for v, n in rr5.values()):
        c2 = "RATE REPLICATES"
    else:
        c2 = "neither composite condition met: " + ", ".join(f"{c}: {v} / {n}" for c, (v, n) in rr5.items())
    dr["RR-9"] = {"H-CERTBIN-a73f1c": a, "H-CERTBIN-5e71c9_C2": c2,
                  "H-CERTBIN-7c3a18": {"KR1_per_RR-2": rr2, "TS1R_per_RR-4": {c: pc[c]["RR-4"]["verdict"] for c in CELLS}},
                  "inputs": {"RR-1": rr1, "RR-2": rr2, "RR-5": {c: {"rate": v, "nulls": n} for c, (v, n) in rr5.items()}},
                  "note": "mechanical composite; the Coordinator decides official status separately"}
    dr["RR-10"] = {"primary": "RR-1, RR-2, RR-3 and RR-5 at D = 4 on F-S3",
                   "secondary": "every D = 3, T_set, T_rank, T_ops, cross-family or REV reading",
                   "secondary_D3_T_strict_RR-1_analogue": {c: _rr1_analogue(cells_summary[c], 3, "strict") for c in CELLS},
                   "secondary_D4_other_granularities": {c: {g: _rr1_analogue(cells_summary[c], 4, g) for g in ("set", "rank", "ops")} for c in CELLS},
                   "secondary_REV_D4_T_strict_retention": {c: {k: v["value"] for k, v in cells_summary[c]["families"]["F-S3-REV"]["D4"]["M1_retention_family_unsat"]["strict"]["per_reference"].items()} for c in CELLS}}
    return dr


def _rr1_analogue(cs, D, g):
    fr = cs["families"]["F-S3"][f"D{D}"]["M1_retention_family_unsat"][g]
    vals = {k: v["value"] for k, v in fr["per_reference"].items()}
    if any(v is None for v in vals.values()):
        return {"values": vals, "all_lt_0.5": None}
    return {"values": vals, "all_lt_0.5": all(v < 0.5 for v in vals.values())}
