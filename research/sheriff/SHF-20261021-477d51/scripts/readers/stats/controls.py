#!/usr/bin/env python3
"""Extra blind analyses and proves-too-much controls (reader "stats").

1. Pooled double-base/plan across the six curves at each band weight
   (stratified target bootstrap, geometric mean of per-curve ratios of sums).
2. Break-even weight w* per curve where double-base/plan = 1.
3. Seed A/A: plan against plan on the same target at a different round
   (different algorithm seed), the A/A the design could have had.
4. Proves-too-much: (a) swap plan<->double-base within every pair: the rule
   must flip confirmed->refuted; (b) random within-pair label swaps
   (null): how often does the rule say "confirmed"/"refuted"; (c) inject a
   known +3%, +10% effect into a copy of plan (A/A positive control);
   (d) perturb: drop plan's unpriced lookups/probes, show w=1 flips.

Usage: python3 -I controls.py <campaign_dir> <out_json>
"""
import json
import math
import sys
from collections import OrderedDict

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rederive as rd  # noqa: E402  (own module, same directory)

WEIGHTS = rd.WEIGHTS


def strata_for(R, a, b, val):
    byw, _, _ = rd.pairs_by_workload(R, a, b, val)
    return [v for v in byw.values() if v]


def label(R, a, b, valf):
    cls = []
    out = []
    for w in WEIGHTS:
        st = strata_for(R, a, b, valf(w))
        ratio = rd.stat_ros(st)
        ci = rd.cluster_ci(st, rd.CMP_RESAMPLES, rd.CMP_SEED, rd.stat_ros)
        cls.append(rd.classify(ci))
        out.append({"w": w, "ratio": ratio, "ci95": ci, "class": cls[-1]})
    return out, rd.protocol_label(cls)


def priced(w):
    return lambda r: rd.priced_s(r, w)


def main(campaign, outp):
    out = OrderedDict()
    data = {s: rd.load(f"{campaign}/sessions/{s}/records.jsonl") for s in rd.SESSIONS}

    # 1. pooled double-base/plan
    pooled = OrderedDict()
    for group, sess in (("all6", rd.SESSIONS), ("r", ["r24", "r26", "r28"]), ("c", ["c24", "c28", "c30"])):
        per_w = []
        for w in WEIGHTS:
            arrs = []
            for s in sess:
                byw, _, _ = rd.pairs_by_workload(data[s], "plan", "double-base", priced(w))
                keys = list(byw)
                sa = np.array([sum(a for a, _ in byw[k]) for k in keys])
                sb = np.array([sum(b for _, b in byw[k]) for k in keys])
                arrs.append((sa, sb))
            point = math.exp(np.mean([math.log(sb.sum() / sa.sum()) for sa, sb in arrs]))
            rng = np.random.default_rng(20261021)
            B = 20000
            logs = np.zeros(B)
            for sa, sb in arrs:
                idx = rng.integers(0, len(sa), size=(B, len(sa)))
                logs += np.log(sb[idx].sum(1) / sa[idx].sum(1))
            g = np.exp(logs / len(arrs))
            lo, hi = np.percentile(g, [2.5, 97.5])
            per_w.append({"w": w, "geomean_ratio": point, "ci95": [float(lo), float(hi)],
                          "per_curve_below_1": sum(1 for sa, sb in arrs if sb.sum() < sa.sum())})
        pooled[group] = per_w
    out["pooled_double_base_over_plan"] = pooled

    # 2. break-even weight
    be = OrderedDict()
    for s in rd.SESSIONS:
        R = data[s]
        def tot(arm):
            rs = [r for r in R if rd.counts(r) and r["arm"] == arm]
            g = sum(r["cost"]["total_gae"] for r in rs)
            u = sum(sum(v for v in rd.unpriced_counts(r).values()) for r in rs)
            return g, u
        gp, up = tot("plan")
        gd, ud = tot("double-base")
        be[s] = {"w_star": (gd - gp) / (up - ud), "plan_unpriced_per_gae": up / gp,
                 "double_unpriced_per_gae": ud / gd}
    out["break_even_weight_double_base"] = be

    # 3. seed A/A: plan(t, round i) vs plan(t, round i+1 mod 3)
    saa = OrderedDict()
    for s in rd.SESSIONS:
        R = data[s]
        plan = {(r["workload"]["workload_id"], r["round"]): r for r in R if rd.counts(r) and r["arm"] == "plan"}
        rounds = sorted({k[1] for k in plan})
        shift = {rounds[i]: rounds[(i + 1) % len(rounds)] for i in range(len(rounds))}
        byw = OrderedDict()
        for k in sorted(plan):
            byw.setdefault(k[0], []).append((plan[k]["cost"]["s"], plan[(k[0], shift[k[1]])]["cost"]["s"]))
        st = [v for v in byw.values()]
        # NB: a cyclic shift makes the pooled sums identical (ratio exactly 1);
        # the interval is what carries the information: within-target seed noise.
        ratio = rd.stat_ros(st)
        ci = rd.cluster_ci(st, rd.CMP_RESAMPLES, rd.CMP_SEED, rd.stat_ros)
        # per-target coefficient of variation of plan S across seeds
        cv = []
        for k, v in byw.items():
            xs = np.array([a for a, _ in v])
            cv.append(float(xs.std(ddof=1) / xs.mean()))
        saa[s] = {"ratio": ratio, "ci95": ci, "class": rd.classify(ci),
                  "mean_within_target_cv_of_plan_S": float(np.mean(cv)),
                  "max_within_target_cv_of_plan_S": float(np.max(cv))}
    out["seed_aa_plan_round_shift"] = saa

    # 4. proves-too-much controls
    ptm = OrderedDict()
    for s in rd.SESSIONS:
        R = data[s]
        res = OrderedDict()
        # (a) swap labels plan <-> double-base everywhere
        Rsw = []
        for r in R:
            q = dict(r)
            if r["arm"] == "plan":
                q["arm"] = "double-base"
            elif r["arm"] == "double-base":
                q["arm"] = "plan"
            Rsw.append(q)
        res["true_double_base"] = label(R, "plan", "double-base", priced)[1]
        res["swapped_double_base"] = label(Rsw, "plan", "double-base", priced)
        res["true_half_base"] = label(R, "plan", "half-base", priced)[1]
        Rsh = []
        for r in R:
            q = dict(r)
            if r["arm"] == "plan":
                q["arm"] = "half-base"
            elif r["arm"] == "half-base":
                q["arm"] = "plan"
            Rsh.append(q)
        res["swapped_half_base"] = label(Rsh, "plan", "half-base", priced)
        # (b) random within-pair swaps, 100 permutations, w=0 only (cheap)
        rng = np.random.default_rng(477051)
        tally = {"confirmed": 0, "not separated": 0, "refuted (at >=1 weight)": 0}
        tally_w0 = {"above": 0, "across": 0, "below": 0}
        keyed = {}
        for r in R:
            if rd.counts(r) and r["arm"] in ("plan", "half-base"):
                keyed.setdefault((r["workload"]["workload_id"], r["round"]), {})[r["arm"]] = r
        NPERM = 100
        for _ in range(NPERM):
            Rp = []
            for k, d in keyed.items():
                flip = rng.random() < 0.5
                for arm, r in d.items():
                    q = dict(r)
                    if flip:
                        q["arm"] = "half-base" if arm == "plan" else "plan"
                    Rp.append(q)
            st = strata_for(Rp, "plan", "half-base", lambda r: r["cost"]["s"])
            ci = rd.cluster_ci(st, 1000, rd.CMP_SEED, rd.stat_ros)
            tally_w0[rd.classify(ci)] += 1
        res["random_within_pair_swap_plan_half_base_w0"] = {"permutations": NPERM, "resamples": 1000,
                                                             "classes": tally_w0}
        # (c) inject known effects into a copy of plan (as arm "plan-x")
        inj = OrderedDict()
        for eff in (1.03, 1.10):
            Rx = list(R)
            for r in R:
                if r["arm"] == "plan":
                    q = json.loads(json.dumps(r))
                    q["arm"] = "plan-x"
                    q["cost"]["total_gae"] *= eff
                    q["cost"]["s"] *= eff
                    Rx.append(q)
            st = strata_for(Rx, "plan", "plan-x", lambda r: r["cost"]["s"])
            inj[str(eff)] = {"ratio": rd.stat_ros(st),
                             "ci95": rd.cluster_ci(st, rd.CMP_RESAMPLES, rd.CMP_SEED, rd.stat_ros)}
        # same effect but injected with seed-level noise: replace plan-x with
        # plan from a shifted round times eff (what an honest A/A would see)
        for eff in (1.03, 1.10):
            plan = {(r["workload"]["workload_id"], r["round"]): r for r in R if rd.counts(r) and r["arm"] == "plan"}
            rounds = sorted({k[1] for k in plan})
            shift = {rounds[i]: rounds[(i + 1) % len(rounds)] for i in range(len(rounds))}
            byw = OrderedDict()
            for k in sorted(plan):
                byw.setdefault(k[0], []).append((plan[k]["cost"]["s"], eff * plan[(k[0], shift[k[1]])]["cost"]["s"]))
            st = list(byw.values())
            ci = rd.cluster_ci(st, rd.CMP_RESAMPLES, rd.CMP_SEED, rd.stat_ros)
            inj[f"{eff}_with_seed_noise"] = {"ratio": rd.stat_ros(st), "ci95": ci, "class": rd.classify(ci)}
        res["injected_effect"] = inj
        # (d) perturb: zero plan's unpriced lookups + target_guard_probes
        Rz = []
        for r in R:
            if r["arm"] == "plan":
                q = json.loads(json.dumps(r))
                q["cost"]["unpriced"] = [u for u in q["cost"]["unpriced"]
                                         if u not in ("lookups_uncharged", "target_guard_probes_uncharged")]
                Rz.append(q)
            else:
                Rz.append(r)
        res["plan_without_lookup_probe_pricing_double_base"] = label(Rz, "plan", "double-base", priced)
        ptm[s] = res
    out["proves_too_much"] = ptm
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", outp)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
