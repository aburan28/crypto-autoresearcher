#!/usr/bin/env python3
"""Blind re-derivation of the ic_planner_validation_20261020 statistics.

Sheriff case SHF-20261021-477d51, reader B9 joint "stats" (B6).

Written from PROTOCOL.md, PROTOCOL_AMENDMENT_1.md, the raw records.jsonl and a
read-only reading of the ecbench source (src/cryptanalysis/ecbench/{compare,
stats,band,canonical,record}.rs and src/bin/ecbench.rs `table`/`band_cmd`).
No producer output (analysis/, comparisons/, README.md, REPORT.*, figures/,
scripts/) was read before this file produced its output. No crypto code runs.

Usage: python3 -I rederive.py <campaign_dir> <out_json>
"""
import json
import math
import sys
from collections import OrderedDict, defaultdict

import numpy as np

M64 = (1 << 64) - 1
SESSIONS = ["c24", "c28", "c30", "r24", "r26", "r28"]
ALTS = ["half-base", "double-base", "rootfind", "full-rank", "random-targets"]
IC_ARMS = ["plan", "half-base", "double-base", "rootfind", "full-rank", "random-targets", "plan-aa"]
WEIGHTS = [0.0, 0.1, 1.0]
# PROTOCOL.md:52-53 and PROTOCOL_AMENDMENT_1.md:33-34
PREDICTED_IC_OVER_RHO = {"c24": 11.46, "c28": 19.33, "c30": 24.55,
                         "r24": 12.23, "r26": 14.45, "r28": 20.08}
CMP_RESAMPLES, CMP_SEED = 4000, 20261002  # src/bin/ecbench.rs:238-241
TABLE_RESAMPLES, TABLE_SEED = 4000, 20261002  # src/bin/ecbench.rs:1717


# ---- ecbench stats.rs port ------------------------------------------------
def splitmix64(x):
    # canonical.rs:117-123
    x = (x + 0x9E3779B97F4A7C15) & M64
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


class Resampler:
    # stats.rs:53-63: the state is replaced by splitmix64(state)
    def __init__(self, seed):
        self.s = seed & M64

    def below(self, n):
        self.s = splitmix64(self.s)
        return self.s % n


def quantile(xs, q):
    # stats.rs:18-28
    if not xs:
        return None
    v = sorted(xs)
    pos = min(max(q, 0.0), 1.0) * (len(v) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def resample(strata, resamples, seed, clusters, stat):
    # stats.rs:102-140
    if not strata or any(len(s) == 0 for s in strata):
        return None
    rng = Resampler(seed)
    values = []
    for _ in range(resamples):
        if clusters:
            picked = [strata[rng.below(len(strata))] for _ in range(len(strata))]
        else:
            picked = list(strata)
        draw = [[s[rng.below(len(s))] for _ in range(len(s))] for s in picked]
        v = stat(draw)
        if v is not None and math.isfinite(v):
            values.append(v)
    if len(values) < resamples * 9 // 10:
        return None
    return (quantile(values, 0.025), quantile(values, 0.975))


def cluster_ci(strata, resamples, seed, stat):
    if len(strata) < 2:
        return None
    return resample(strata, resamples, seed, True, stat)


def ratio_of_sums(pairs):
    sa = sum(a for a, _ in pairs)
    sb = sum(b for _, b in pairs)
    return sb / sa if pairs and sa > 0 else None


def stat_ros(strata):
    return ratio_of_sums([p for s in strata for p in s])


def stat_mean(strata):
    xs = [x for s in strata for x in s]
    return sum(xs) / len(xs) if xs else None


# ---- records -------------------------------------------------------------
def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f]


def counts(r):  # record.rs:361-363
    return (not r["warmup"]) and r["outcome"]["status"] == "verified"


def unpriced_counts(r):  # band.rs:39-64
    out = OrderedDict()
    for name in r["cost"]["unpriced"]:
        base = name[: -len("_uncharged")] if name.endswith("_uncharged") else name
        if name in r["counters"]:
            out[name] = r["counters"][name]
            continue
        total, found = 0, False
        for p in r["phases"]:
            nat = p.get("native") or {}
            v = nat.get(name, nat.get(base))
            if v is not None:
                total += v
                found = True
        out[name] = total if found else None
    return out


def priced_s(r, w):  # band.rs:136-152; no record carries calibration pins
    pins = (r.get("detail") or {}).get("calibration_pinned_units") or []
    assert not pins, "calibration pins present: port calibrated_native"
    uc = unpriced_counts(r)
    missing = any(v is None for v in uc.values())
    if missing and w > 0:
        return None
    u = sum(v for v in uc.values() if v is not None)
    return (r["cost"]["total_gae"] + w * u) / math.sqrt(r["workload"]["curve"]["r"])


def pairs_by_workload(R, a_arm, b_arm, value=lambda r: r["cost"]["s"]):
    """compare.rs:230-260: key (workload_id, round), both counted, sorted."""
    A = {(r["workload"]["workload_id"], r["round"]): r for r in R if r["arm"] == a_arm and counts(r)}
    B = {(r["workload"]["workload_id"], r["round"]): r for r in R if r["arm"] == b_arm and counts(r)}
    byw = OrderedDict()
    same_seeds = True
    for k in sorted(A):
        if k in B:
            same_seeds &= A[k]["algorithm_seed"] == B[k]["algorithm_seed"]
            byw.setdefault(k[0], []).append((value(A[k]), value(B[k])))
    paired = sum(len(v) for v in byw.values())
    unpaired = (len(A) - paired) + (len(B) - paired)
    return byw, unpaired, same_seeds


def ecb_compare(R, a_arm, b_arm, value=lambda r: r["cost"]["s"]):
    byw, unpaired, same_seeds = pairs_by_workload(R, a_arm, b_arm, value)
    strata = [v for v in byw.values() if v]
    ratio = stat_ros(strata)
    if len(strata) >= 2:
        ci, method = cluster_ci(strata, CMP_RESAMPLES, CMP_SEED, stat_ros), "cluster"
    else:
        ci, method = resample(strata, CMP_RESAMPLES, CMP_SEED, False, stat_ros), "within"
    return {"ratio": ratio, "ci95": ci, "ci_method": method,
            "pairs": sum(len(s) for s in strata), "workloads": len(strata),
            "unpaired": unpaired, "same_seeds": same_seeds,
            "per_workload": {k: ratio_of_sums(v) for k, v in byw.items()}}


def np_cluster_boot(R, a_arm, b_arm, value=lambda r: r["cost"]["s"], B=20000, seed=477051):
    """Independent cross-check: one-stage cluster bootstrap by target (all
    rounds of a target move together), ratio of sums, percentile 95%."""
    byw, _, _ = pairs_by_workload(R, a_arm, b_arm, value)
    keys = list(byw)
    sa = np.array([sum(a for a, _ in byw[k]) for k in keys])
    sb = np.array([sum(b for _, b in byw[k]) for k in keys])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(keys), size=(B, len(keys)))
    rat = sb[idx].sum(1) / sa[idx].sum(1)
    lo, hi = np.percentile(rat, [2.5, 97.5])
    return {"ratio": float(sb.sum() / sa.sum()), "ci95": [float(lo), float(hi)]}


def table_rows(R, arms, ref="rho-neg"):
    rows = OrderedDict()
    for arm in arms:
        mine = [r for r in R if (not r["warmup"]) and r["arm"] == arm]
        ok = [r["cost"]["s"] for r in mine if counts(r)]
        by_w = OrderedDict()
        for r in mine:
            if counts(r):
                by_w.setdefault(r["workload"]["workload_id"], []).append(r["cost"]["s"])
        strata = [by_w[k] for k in sorted(by_w)]
        ci = cluster_ci(strata, TABLE_RESAMPLES, TABLE_SEED, stat_mean) or \
            resample(strata, TABLE_RESAMPLES, TABLE_SEED, False, stat_mean)
        refs = {(r["workload"]["workload_id"], r["round"]): r["cost"]["s"]
                for r in R if counts(r) and r["arm"] == ref}
        sa = sb = 0.0
        for r in mine:
            if counts(r):
                k = (r["workload"]["workload_id"], r["round"])
                if k in refs:
                    sa += refs[k]
                    sb += r["cost"]["s"]
        lv = defaultdict(int)
        for r in mine:
            lv[r["isolation"]["level"]] += 1
        rows[arm] = {"verified": len(ok), "runs": len(mine),
                     "mean_s": sum(ok) / len(ok) if ok else None,
                     "ci95": ci, "s_over_ref": sb / sa if sa > 0 else None,
                     "levels": dict(sorted(lv.items()))}
    return rows


def band_rows(R, arms):
    out = OrderedDict()
    for arm in arms:
        rs = [r for r in R if (not r["warmup"]) and r["arm"] == arm]
        ok = [r for r in rs if counts(r)]
        ms = []
        for w in WEIGHTS:
            vals = [priced_s(r, w) for r in ok]
            ms.append(None if (not ok or any(v is None for v in vals)) else sum(vals) / len(vals))
        unc = sorted({k for r in rs for k, v in unpriced_counts(r).items() if v is None})
        mean_u = sum(sum(v for v in unpriced_counts(r).values() if v is not None) for r in ok) / len(ok)
        out[arm] = {"mean_s": ms, "uncounted": unc, "mean_unpriced_ops": mean_u,
                    "runs": len(rs), "verified": len(ok)}
    return out


def classify(ci):
    if ci is None:
        return "no interval"
    lo, hi = ci
    if lo > 1:
        return "above"
    if hi < 1:
        return "below"
    return "across"


def protocol_label(per_weight_classes):
    """PROTOCOL.md:68-71 literal: confirmed iff above at every weight;
    refuted when it lies below 1; not separated when it contains 1."""
    if all(c == "above" for c in per_weight_classes):
        return "confirmed"
    if any(c == "below" for c in per_weight_classes):
        return "refuted (at >=1 weight)"
    return "not separated"


def analyse(campaign):
    res = OrderedDict()
    for s in SESSIONS:
        R = load(f"{campaign}/sessions/{s}/records.jsonl")
        sess = OrderedDict()
        r0 = R[0]["workload"]["curve"]
        sess["curve"] = {"slug": r0["slug"], "r": r0["r"], "log2_r": math.log2(r0["r"])}
        sess["n_records"] = len(R)
        sess["status_counts"] = dict(sorted(defaultdict(int, {}).items()))
        st = defaultdict(int)
        for r in R:
            st[r["outcome"]["status"]] += 1
        sess["status_counts"] = dict(st)
        sess["warmups"] = sum(1 for r in R if r["warmup"])
        sess["s_equals_total_over_sqrt_r"] = all(
            abs(r["cost"]["s"] - r["cost"]["total_gae"] / math.sqrt(r["workload"]["curve"]["r"])) <= 1e-12 * r["cost"]["s"]
            for r in R)
        sess["table"] = table_rows(R, ["rho-neg"] + IC_ARMS)
        cmp_ = OrderedDict()
        for b in ALTS + ["plan-aa"]:
            c = ecb_compare(R, "plan", b)
            c["np_cluster_boot"] = np_cluster_boot(R, "plan", b)
            cmp_[f"plan__{b}"] = c
        c = ecb_compare(R, "rho-neg", "plan")
        c["np_cluster_boot"] = np_cluster_boot(R, "rho-neg", "plan")
        cmp_["rho-neg__plan"] = c
        sess["compare"] = cmp_
        sess["band"] = band_rows(R, ["rho-neg"] + IC_ARMS)
        # band ratio alt/plan per weight: point (ratio of means == ratio of
        # sums here: equal N, all verified) and two intervals: ecbench's
        # cluster method applied to priced S, and the numpy cross-check.
        bands = OrderedDict()
        for b in ALTS + ["plan-aa"]:
            per = []
            for w in WEIGHTS:
                val = (lambda w: (lambda r: priced_s(r, w)))(w)
                c = ecb_compare(R, "plan", b, val)
                npb = np_cluster_boot(R, "plan", b, val)
                pm = sess["band"]["plan"]["mean_s"][WEIGHTS.index(w)]
                bm = sess["band"][b]["mean_s"][WEIGHTS.index(w)]
                per.append({"w": w, "ratio_of_band_means": bm / pm, "ratio": c["ratio"],
                            "ci95_ecbench_method": c["ci95"], "ci95_np": npb["ci95"],
                            "class": classify(c["ci95"]), "class_np": classify(npb["ci95"])})
            bands[b] = {"per_weight": per,
                        "protocol_label": protocol_label([p["class"] for p in per]),
                        "band_order_holds": (all(p["ratio_of_band_means"] > 1 for p in per) or
                                             all(p["ratio_of_band_means"] < 1 for p in per))}
        # plan/rho across the band too
        per = []
        for w in WEIGHTS:
            val = (lambda w: (lambda r: priced_s(r, w)))(w)
            c = ecb_compare(R, "rho-neg", "plan", val)
            per.append({"w": w, "ratio": c["ratio"], "ci95_ecbench_method": c["ci95"]})
        bands["plan_over_rho"] = per
        sess["band_ratios"] = bands
        # determinism probes
        det = OrderedDict()
        for arm in IC_ARMS + ["rho-neg"]:
            byt = defaultdict(set)
            for r in R:
                if r["arm"] == arm and not r["warmup"]:
                    byt[r["workload"]["workload_id"]].add(r["cost"]["total_gae"])
            det[arm] = {"targets_with_identical_S_across_rounds": sum(1 for v in byt.values() if len(v) == 1)}
        identical = sum(1 for r in R if r["arm"] == "plan" and not r["warmup"]) and all(
            any(q["arm"] == "plan-aa" and q["round"] == r["round"]
                and q["workload"]["workload_id"] == r["workload"]["workload_id"]
                and q["cost"]["total_gae"] == r["cost"]["total_gae"]
                and q["counters"] == r["counters"] for q in R)
            for r in R if r["arm"] == "plan" and not r["warmup"])
        det["plan_vs_plan_aa_identical_total_and_counters_every_pair"] = identical
        sess["determinism"] = det
        # P4
        pr = cmp_["rho-neg__plan"]["ratio"]
        sess["P4"] = {"S_plan_over_S_rho": pr, "predicted": PREDICTED_IC_OVER_RHO[s],
                      "measured_over_predicted": pr / PREDICTED_IC_OVER_RHO[s],
                      "within_factor_2": 0.5 <= pr / PREDICTED_IC_OVER_RHO[s] <= 2}
        # P1
        ic_means = {a: sess["table"][a]["mean_s"] for a in IC_ARMS if a != "plan-aa"}
        sess["P1"] = {"lowest_ic_arm_excl_aa": min(ic_means, key=ic_means.get),
                      "plan_lowest": min(ic_means, key=ic_means.get) == "plan"}
        res[s] = sess
    return res


if __name__ == "__main__":
    campaign, out = sys.argv[1], sys.argv[2]
    res = analyse(campaign)
    with open(out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=False)
    print("wrote", out)
